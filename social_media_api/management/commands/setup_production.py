from django.core.management.base import BaseCommand
import os
import secrets

class Command(BaseCommand):
    help = 'Setup production environment'
    
    def handle(self, *args, **options):
        # Create .env file if it doesn't exist
        env_file = '.env'
        if not os.path.exists(env_file):
            self.stdout.write('Creating .env file...')
            
            # Generate secure secret key
            secret_key = secrets.token_urlsafe(50)
            
            env_content = f"""# Production settings
DEBUG=False
SECRET_KEY={secret_key}
ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com,.herokuapp.com

# Database
# DATABASE_URL=postgresql://username:password@localhost:5432/social_media_db

# Email settings
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
"""
            
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            self.stdout.write(self.style.SUCCESS('Created .env file'))
        
        # Create logs directory
        logs_dir = 'logs'
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            self.stdout.write(self.style.SUCCESS(f'Created {logs_dir} directory'))
        
        # Create media directory
        media_dir = 'media'
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)
            os.makedirs(os.path.join(media_dir, 'profile_pics'))
            self.stdout.write(self.style.SUCCESS(f'Created {media_dir} directory'))
        
        self.stdout.write(self.style.SUCCESS('Production setup complete!'))