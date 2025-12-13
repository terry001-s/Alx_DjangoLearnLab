from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'comments_count']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Basic Information', {
            'fields': ['author', 'title', 'content']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Basic Information', {
            'fields': ['post', 'author', 'content']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]