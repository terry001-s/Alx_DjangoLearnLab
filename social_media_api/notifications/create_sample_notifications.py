from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from posts.models import Post, Comment, Like
from notifications.models import Notification
from notifications.utils import create_notification

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample notifications for testing'
    
    def handle(self, *args, **options):
        # Get existing users
        users = list(User.objects.all()[:3])
        
        if len(users) < 2:
            self.stdout.write(self.style.WARNING('Need at least 2 users to create notifications'))
            return
        
        # Get some posts
        posts = list(Post.objects.all()[:2])
        
        if not posts:
            self.stdout.write(self.style.WARNING('Need at least 1 post to create notifications'))
            return
        
        # Create sample notifications
        # Follow notification
        create_notification(
            recipient=users[1],
            actor=users[0],
            verb="started following you",
            notification_type='follow'
        )
        
        # Like notification
        if posts:
            create_notification(
                recipient=posts[0].author,
                actor=users[0],
                verb=f"liked your post: {posts[0].title}",
                notification_type='like',
                target=posts[0]
            )
        
        # Comment notification
        comments = list(Comment.objects.all()[:1])
        if comments:
            create_notification(
                recipient=comments[0].post.author,
                actor=comments[0].author,
                verb=f"commented on your post: {comments[0].post.title}",
                notification_type='comment',
                target=comments[0]
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample notifications!'))