from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"


class Comment(models.Model):
    """
    Adjacency list model for nested comments.
    parent=None means it's a top-level comment on a post.
    parent=some_comment means it's a reply to that comment.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name='replies'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:30]}"


class PostLike(models.Model):
    """
    Like on a post. Unique constraint prevents double-liking.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Database-level constraint to prevent double likes
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_post_like')
        ]

    def __str__(self):
        return f"{self.user.username} likes post {self.post.id}"


class CommentLike(models.Model):
    """
    Like on a comment. Unique constraint prevents double-liking.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'comment'], name='unique_comment_like')
        ]

    def __str__(self):
        return f"{self.user.username} likes comment {self.comment.id}"


class KarmaTransaction(models.Model):
    """
    Records each karma-earning event. Used to calculate 24h leaderboard dynamically.
    This avoids storing a running total on the User model.
    """
    KARMA_POST_LIKE = 5
    KARMA_COMMENT_LIKE = 1

    KARMA_TYPES = [
        ('post_like', 'Post Like'),
        ('comment_like', 'Comment Like'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='karma_transactions')
    karma_type = models.CharField(max_length=20, choices=KARMA_TYPES)
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional references to track what earned the karma
    post_like = models.ForeignKey(PostLike, null=True, blank=True, on_delete=models.CASCADE)
    comment_like = models.ForeignKey(CommentLike, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}: +{self.points} ({self.karma_type})"
