from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Post(models.Model):
    """Model for user posts"""
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"
    
    @property
    def comments_count(self):
        return self.comments.count()
    
    @property
    def likes_count(self):
        return self.likes.count()

class Comment(models.Model):
    """Model for comments on posts"""
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"