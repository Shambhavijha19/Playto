# Design Decisions

This document explains the technical choices made for the key challenges in this project.

## The Tree: Nested Comments

I used an adjacency list model for the comment tree. Each comment has a `parent` field that points to its parent comment (or null for top-level comments).

```python
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField()
```

The challenge was fetching the entire comment tree without triggering N+1 queries. Here is how I solved it:

1. Fetch all comments for a post in a single query
2. Build the tree structure in Python memory

```python
def build_comment_tree(comments):
    comment_map = {c.id: c for c in comments}
    roots = []
    
    for comment in comments:
        comment.children = []
    
    for comment in comments:
        if comment.parent_id is None:
            roots.append(comment)
        else:
            parent = comment_map.get(comment.parent_id)
            if parent:
                parent.children.append(comment)
    
    return roots
```

In the view, I fetch everything with proper annotations in one go:

```python
comments = Comment.objects.filter(post=post).select_related('author')
comments = comments.annotate(prefetched_likes_count=Count('likes', distinct=True))
comments = list(comments)  # Execute query once
post.comment_tree = build_comment_tree(comments)
```

This approach means loading a post with 50 comments runs exactly 2 SQL queries (one for the post, one for all comments) regardless of nesting depth. The tree building runs in O(n) time in Python, which is much faster than additional database round trips.

## The Math: 24-Hour Leaderboard

The leaderboard is calculated dynamically from the `KarmaTransaction` table. Every time someone likes a post or comment, a transaction record is created with the timestamp.

Here is the QuerySet:

```python
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

cutoff = timezone.now() - timedelta(hours=24)

top_users = (
    KarmaTransaction.objects
    .filter(created_at__gte=cutoff)
    .values('user_id', 'user__username')
    .annotate(karma_24h=Sum('points'))
    .order_by('-karma_24h')[:5]
)
```

The generated SQL looks roughly like this:

```sql
SELECT user_id, auth_user.username, SUM(points) as karma_24h
FROM feed_karmatransaction
JOIN auth_user ON feed_karmatransaction.user_id = auth_user.id
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY user_id, auth_user.username
ORDER BY karma_24h DESC
LIMIT 5
```

This meets the requirement of not storing daily karma as a simple integer on the User model. The karma is always computed fresh from the transaction history, filtered by timestamp.

## Concurrency: Preventing Double Likes

Double-liking is prevented at the database level using a unique constraint:

```python
class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_post_like')
        ]
```

When a like request comes in, the code attempts to create the like record. If the constraint is violated (user already liked), it catches the IntegrityError:

```python
with transaction.atomic():
    try:
        post_like = PostLike.objects.create(user=user, post=post)
        KarmaTransaction.objects.create(...)
        return Response({'liked': True})
    except IntegrityError:
        return Response({'error': 'Already liked'}, status=400)
```

The atomic transaction ensures that if creating the karma transaction fails for some reason, the like is also rolled back. This keeps the data consistent even under concurrent requests.

## The AI Audit

The AI initially generated the comment tree serialization like this:

```python
class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    def get_replies(self, obj):
        children = Comment.objects.filter(parent=obj)
        return CommentSerializer(children, many=True).data
```

This is the classic N+1 problem in disguise. For a post with 50 comments, this would trigger 50 queries (one per comment to check for children), even though most comments might have no replies.

I fixed it by pre-fetching all comments in the view and building the tree in Python before serialization. The serializer now just reads from the pre-computed `children` attribute:

```python
def get_replies(self, obj):
    if hasattr(obj, 'children'):
        return CommentSerializer(obj.children, many=True, context=self.context).data
    return []
```

This brought it down to a single query for all comments, regardless of tree depth or structure.
