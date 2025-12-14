from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification, NotificationSettings
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class UserNotificationSerializer(serializers.ModelSerializer):
    """Serializer for user in notifications"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    actor = UserNotificationSerializer(read_only=True)
    recipient = UserNotificationSerializer(read_only=True)
    target_object = serializers.SerializerMethodField()
    time_since = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'actor', 'recipient', 'verb', 'notification_type',
            'target_object', 'is_read', 'created_at', 'time_since'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_target_object(self, obj):
        """Get serialized target object if it exists"""
        if obj.target:
            # You can customize this based on your model serializers
            from posts.serializers import PostSerializer, CommentSerializer
            
            if hasattr(obj.target, 'title'):  # It's a Post
                return {
                    'type': 'post',
                    'id': obj.target.id,
                    'title': obj.target.title,
                    'content_preview': obj.target.content[:100] + '...' if len(obj.target.content) > 100 else obj.target.content
                }
            elif hasattr(obj.target, 'post'):  # It's a Comment
                return {
                    'type': 'comment',
                    'id': obj.target.id,
                    'post_id': obj.target.post.id,
                    'post_title': obj.target.post.title,
                    'content': obj.target.content[:100] + '...' if len(obj.target.content) > 100 else obj.target.content
                }
        return None
    
    def get_time_since(self, obj):
        """Get human-readable time since notification was created"""
        from django.utils import timezone
        from datetime import datetime
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for notification settings"""
    class Meta:
        model = NotificationSettings
        fields = [
            'receive_like_notifications',
            'receive_comment_notifications',
            'receive_follow_notifications',
            'receive_mention_notifications',
            'email_like_notifications',
            'email_comment_notifications',
            'email_follow_notifications',
        ]