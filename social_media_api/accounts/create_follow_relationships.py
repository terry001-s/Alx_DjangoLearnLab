from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample follow relationships between users'
    
    def handle(self, *args, **options):
        # Get existing users
        users = list(User.objects.all()[:5])  # Get first 5 users
        
        if len(users) < 3:
            self.stdout.write(self.style.WARNING('Need at least 3 users to create follow relationships'))
            return
        
        # Create follow relationships
        # User 0 follows User 1 and User 2
        users[0].follow(users[1])
        users[0].follow(users[2])
        
        # User 1 follows User 2 and User 3 (if exists)
        users[1].follow(users[2])
        if len(users) > 3:
            users[1].follow(users[3])
        
        # User 2 follows User 0 and User 1
        users[2].follow(users[0])
        users[2].follow(users[1])
        
        self.stdout.write(self.style.SUCCESS('Successfully created follow relationships!'))
        self.stdout.write(f'{users[0].username} is following: {[u.username for u in users[0].following.all()]}')
        self.stdout.write(f'{users[1].username} is following: {[u.username for u in users[1].following.all()]}')
        self.stdout.write(f'{users[2].username} is following: {[u.username for u in users[2].following.all()]}')