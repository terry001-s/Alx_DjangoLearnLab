from .models import Notification, NotificationSettings
from django.contrib.auth import get_user_model

User = get_user_model()

def create_notification(recipient, actor, verb, notification_type, target=None):
    """Create a notification if user has enabled it"""
    # Check user's notification settings
    settings, created = NotificationSettings.objects.get_or_create(user=recipient)
    
    # Check if this type of notification is enabled
    if notification_type == 'like' and not settings.receive_like_notifications:
        return None
    elif notification_type == 'comment' and not settings.receive_comment_notifications:
        return None
    elif notification_type == 'follow' and not settings.receive_follow_notifications:
        return None
    elif notification_type == 'mention' and not settings.receive_mention_notifications:
        return None
    
    # Create the notification
    return Notification.create_notification(
        recipient=recipient,
        actor=actor,
        verb=verb,
        notification_type=notification_type,
        target=target
    )

def create_like_notification(post, user):
    """Create notification for post like"""
    if post.author != user:  # Don't notify if user likes their own post
        return create_notification(
            recipient=post.author,
            actor=user,
            verb=f"liked your post: {post.title}",
            notification_type='like',
            target=post
        )
    return None

def create_comment_notification(comment):
    """Create notification for comment"""
    if comment.post.author != comment.author:  # Don't notify if commenting on own post
        return create_notification(
            recipient=comment.post.author,
            actor=comment.author,
            verb=f"commented on your post: {comment.post.title}",
            notification_type='comment',
            target=comment
        )
    return None

def create_follow_notification(follower, followed):
    """Create notification for new follower"""
    return create_notification(
        recipient=followed,
        actor=follower,
        verb="started following you",
        notification_type='follow'
    )