from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, PostLike, CommentLike


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments. The 'replies' field is populated in the view
    after we fetch all comments in a single query and build the tree in Python.
    """
    author = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at', 'parent', 'like_count', 'is_liked', 'replies']
        read_only_fields = ['author', 'created_at']

    def get_like_count(self, obj):
        # Uses prefetched likes if available
        if hasattr(obj, 'prefetched_likes_count'):
            return obj.prefetched_likes_count
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if hasattr(obj, 'user_has_liked'):
                return obj.user_has_liked
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_replies(self, obj):
        # This is populated by the view's tree-building logic
        if hasattr(obj, 'children'):
            return CommentSerializer(obj.children, many=True, context=self.context).data
        return []


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'like_count', 'comment_count', 'is_liked']
        read_only_fields = ['author', 'created_at']

    def get_like_count(self, obj):
        if hasattr(obj, 'prefetched_likes_count'):
            return obj.prefetched_likes_count
        return obj.likes.count()

    def get_comment_count(self, obj):
        if hasattr(obj, 'prefetched_comments_count'):
            return obj.prefetched_comments_count
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if hasattr(obj, 'user_has_liked'):
                return obj.user_has_liked
            return obj.likes.filter(user=request.user).exists()
        return False


class PostDetailSerializer(PostSerializer):
    """
    Includes the full comment tree. Comments are built as a tree in the view.
    """
    comments = serializers.SerializerMethodField()

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments']

    def get_comments(self, obj):
        # The view populates 'comment_tree' on the post object
        if hasattr(obj, 'comment_tree'):
            return CommentSerializer(obj.comment_tree, many=True, context=self.context).data
        return []


class LeaderboardUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    karma_24h = serializers.IntegerField()
    rank = serializers.IntegerField()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
