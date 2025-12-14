from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

User = get_user_model()

class Notification(models.Model):
    """Model for user notifications"""
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('mention', 'Mention'),
        ('post', 'Post'),
    )
    
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    actor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='actions'
    )
    verb = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # Generic foreign key to the target object (post, comment, etc.)
    target_content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')
    
    # Status fields
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)  # Add timestamp field
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.actor.username} {self.verb} at {self.timestamp}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        self.is_read = False
        self.save()
    
    @classmethod
    def create_notification(cls, recipient, actor, verb, notification_type, target=None):
        """Create a new notification"""
        notification = cls.objects.create(
            recipient=recipient,
            actor=actor,
            verb=verb,
            notification_type=notification_type,
        )
        
        if target:
            notification.target = target
            notification.save()
        
        return notification

class NotificationSettings(models.Model):
    """Model for user notification preferences"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='notification_settings'
    )
    
    # Notification preferences
    receive_like_notifications = models.BooleanField(default=True)
    receive_comment_notifications = models.BooleanField(default=True)
    receive_follow_notifications = models.BooleanField(default=True)
    receive_mention_notifications = models.BooleanField(default=True)
    
    # Email preferences
    email_like_notifications = models.BooleanField(default=False)
    email_comment_notifications = models.BooleanField(default=False)
    email_follow_notifications = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification settings for {self.user.username}"