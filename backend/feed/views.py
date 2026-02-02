from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import Count, Sum, Prefetch, Exists, OuterRef
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict

from .models import Post, Comment, PostLike, CommentLike, KarmaTransaction
from .serializers import (
    PostSerializer, PostDetailSerializer, CommentSerializer,
    LeaderboardUserSerializer, RegisterSerializer, UserSerializer
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                login(request, user)
                return Response({
                    'user': UserSerializer(user).data,
                    'message': 'Registration successful'
                }, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {'error': 'Username already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Login successful'
            })
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})


class CurrentUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'user': UserSerializer(request.user).data,
                'authenticated': True
            })
        return Response({'authenticated': False})


def build_comment_tree(comments):
    """
    Build a tree structure from a flat list of comments.
    This runs in O(n) time after fetching all comments in one query.
    """
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


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.select_related('author')
        
        # Annotate with counts
        queryset = queryset.annotate(
            prefetched_likes_count=Count('likes', distinct=True),
            prefetched_comments_count=Count('comments', distinct=True)
        )
        
        # Check if current user has liked each post
        if user.is_authenticated:
            queryset = queryset.annotate(
                user_has_liked=Exists(
                    PostLike.objects.filter(post=OuterRef('pk'), user=user)
                )
            )
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostSerializer

    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()
        user = request.user
        
        # Fetch ALL comments for this post in ONE query
        comments = Comment.objects.filter(post=post).select_related('author')
        
        # Annotate like counts
        comments = comments.annotate(
            prefetched_likes_count=Count('likes', distinct=True)
        )
        
        # Check if user liked each comment
        if user.is_authenticated:
            comments = comments.annotate(
                user_has_liked=Exists(
                    CommentLike.objects.filter(comment=OuterRef('pk'), user=user)
                )
            )
        
        comments = list(comments)
        
        # Build tree in Python (no extra queries)
        post.comment_tree = build_comment_tree(comments)
        
        serializer = self.get_serializer(post, context={'request': request})
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        # Use atomic transaction to handle race conditions
        with transaction.atomic():
            try:
                # select_for_update would be overkill here since we have unique constraint
                post_like = PostLike.objects.create(user=user, post=post)
                
                # Create karma transaction for post author
                KarmaTransaction.objects.create(
                    user=post.author,
                    karma_type='post_like',
                    points=KarmaTransaction.KARMA_POST_LIKE,
                    post_like=post_like
                )
                
                return Response({'liked': True, 'message': 'Post liked'})
            except IntegrityError:
                # Already liked - the unique constraint caught it
                return Response(
                    {'error': 'Already liked this post'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        with transaction.atomic():
            try:
                post_like = PostLike.objects.get(user=user, post=post)
                # Delete related karma transaction
                KarmaTransaction.objects.filter(post_like=post_like).delete()
                post_like.delete()
                return Response({'liked': False, 'message': 'Post unliked'})
            except PostLike.DoesNotExist:
                return Response(
                    {'error': 'You have not liked this post'},
                    status=status.HTTP_400_BAD_REQUEST
                )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.request.query_params.get('post')
        queryset = Comment.objects.select_related('author')
        
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        queryset = queryset.annotate(
            prefetched_likes_count=Count('likes', distinct=True)
        )
        
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                user_has_liked=Exists(
                    CommentLike.objects.filter(comment=OuterRef('pk'), user=self.request.user)
                )
            )
        
        return queryset

    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        parent_id = self.request.data.get('parent')
        
        post = Post.objects.get(id=post_id)
        parent = None
        if parent_id:
            parent = Comment.objects.get(id=parent_id)
        
        serializer.save(author=self.request.user, post=post, parent=parent)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        user = request.user
        
        with transaction.atomic():
            try:
                comment_like = CommentLike.objects.create(user=user, comment=comment)
                
                # Create karma transaction for comment author
                KarmaTransaction.objects.create(
                    user=comment.author,
                    karma_type='comment_like',
                    points=KarmaTransaction.KARMA_COMMENT_LIKE,
                    comment_like=comment_like
                )
                
                return Response({'liked': True, 'message': 'Comment liked'})
            except IntegrityError:
                return Response(
                    {'error': 'Already liked this comment'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        comment = self.get_object()
        user = request.user
        
        with transaction.atomic():
            try:
                comment_like = CommentLike.objects.get(user=user, comment=comment)
                KarmaTransaction.objects.filter(comment_like=comment_like).delete()
                comment_like.delete()
                return Response({'liked': False, 'message': 'Comment unliked'})
            except CommentLike.DoesNotExist:
                return Response(
                    {'error': 'You have not liked this comment'},
                    status=status.HTTP_400_BAD_REQUEST
                )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def leaderboard(request):
    """
    Get top 5 users by karma earned in the last 24 hours.
    
    This query:
    1. Filters KarmaTransaction to last 24 hours
    2. Groups by user
    3. Sums the points
    4. Orders by total descending
    5. Takes top 5
    
    The SQL generated is roughly:
    SELECT user_id, SUM(points) as karma_24h
    FROM feed_karmatransaction
    WHERE created_at >= NOW() - INTERVAL '24 hours'
    GROUP BY user_id
    ORDER BY karma_24h DESC
    LIMIT 5
    """
    cutoff = timezone.now() - timedelta(hours=24)
    
    top_users = (
        KarmaTransaction.objects
        .filter(created_at__gte=cutoff)
        .values('user_id', 'user__username')
        .annotate(karma_24h=Sum('points'))
        .order_by('-karma_24h')[:5]
    )
    
    result = [
        {
            'id': entry['user_id'],
            'username': entry['user__username'],
            'karma_24h': entry['karma_24h'],
            'rank': idx + 1
        }
        for idx, entry in enumerate(top_users)
    ]
    
    return Response(result)
