from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='following'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    @property
    def followers_count(self):
        return self.followers.count()
    
    @property
    def following_count(self):
        return self.following.count()
    
    def is_following(self, user):
        """Check if the current user is following another user"""
        return self.following.filter(id=user.id).exists()
    
    def follow(self, user):
        """Follow another user"""
        if not self.is_following(user) and self != user:
            self.following.add(user)
            return True
        return False
    
    def unfollow(self, user):
        """Unfollow another user"""
        if self.is_following(user):
            self.following.remove(user)
            return True
        return False