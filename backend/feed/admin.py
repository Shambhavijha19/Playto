from django.contrib import admin
from .models import Post, Comment, PostLike, CommentLike, KarmaTransaction

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'parent', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username']

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'created_at']

@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'comment', 'created_at']

@admin.register(KarmaTransaction)
class KarmaTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'karma_type', 'points', 'created_at']
    list_filter = ['karma_type', 'created_at']
