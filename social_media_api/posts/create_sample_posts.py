from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from posts.models import Post, Comment

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample posts and comments for testing'
    
    def handle(self, *args, **options):
        # Get or create users
        alice, _ = User.objects.get_or_create(
            username='alice',
            defaults={'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Smith'}
        )
        bob, _ = User.objects.get_or_create(
            username='bob',
            defaults={'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Johnson'}
        )
        charlie, _ = User.objects.get_or_create(
            username='charlie',
            defaults={'email': 'charlie@example.com', 'first_name': 'Charlie', 'last_name': 'Brown'}
        )
        
        # Create sample posts
        posts_data = [
            {
                'author': alice,
                'title': 'My First Post',
                'content': 'Hello everyone! This is my first post on this awesome social media platform.'
            },
            {
                'author': bob,
                'title': 'Travel Tips',
                'content': 'Here are some of my favorite travel destinations and tips for budget travelers.'
            },
            {
                'author': charlie,
                'title': 'Music Recommendations',
                'content': 'Sharing my favorite albums of this year. What are you listening to?'
            },
            {
                'author': alice,
                'title': 'Learning Django',
                'content': 'Just finished building my first Django API. It was challenging but fun!'
            },
            {
                'author': bob,
                'title': 'Food Adventures',
                'content': 'Tried a new restaurant today. The pasta was amazing!'
            },
        ]
        
        for post_data in posts_data:
            post, created = Post.objects.get_or_create(
                author=post_data['author'],
                title=post_data['title'],
                defaults={'content': post_data['content']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created post: {post.title}'))
        
        # Create sample comments
        posts = Post.objects.all()
        comments_data = [
            {
                'post': posts[0],
                'author': bob,
                'content': 'Welcome Alice! Great to have you here.'
            },
            {
                'post': posts[0],
                'author': charlie,
                'content': 'Looking forward to your posts!'
            },
            {
                'post': posts[1],
                'author': alice,
                'content': 'Love these travel tips! I\'ve been to Thailand and it was amazing.'
            },
            {
                'post': posts[2],
                'author': bob,
                'content': 'Great music taste! Have you heard the new album from that indie band?'
            },
            {
                'post': posts[3],
                'author': charlie,
                'content': 'Django is awesome! I\'m also learning it for my backend projects.'
            },
        ]
        
        for comment_data in comments_data:
            comment, created = Comment.objects.get_or_create(
                post=comment_data['post'],
                author=comment_data['author'],
                defaults={'content': comment_data['content']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created comment by {comment.author.username}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample posts and comments!'))