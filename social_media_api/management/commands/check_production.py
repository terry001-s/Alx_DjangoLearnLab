from django.core.management.base import BaseCommand
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Check production environment settings'
    
    def handle(self, *args, **options):
        self.stdout.write('Checking production environment...\n')
        
        checks = [
            ('DEBUG mode', not settings.DEBUG, 'DEBUG should be False in production'),
            ('Secret key', len(settings.SECRET_KEY) >= 50, 'SECRET_KEY should be at least 50 characters'),
            ('Allowed hosts', len(settings.ALLOWED_HOSTS) > 0, 'ALLOWED_HOSTS should be configured'),
            ('Database', settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3' or settings.DEBUG, 
             'Consider using PostgreSQL in production'),
            ('Static root', os.path.exists(settings.STATIC_ROOT), 'STATIC_ROOT directory should exist'),
        ]
        
        all_pass = True
        for check_name, condition, message in checks:
            if condition:
                self.stdout.write(self.style.SUCCESS(f'✓ {check_name}: OK'))
            else:
                self.stdout.write(self.style.WARNING(f'✗ {check_name}: {message}'))
                all_pass = False
        
        if all_pass:
            self.stdout.write(self.style.SUCCESS('\n✅ All production checks passed!'))
        else:
            self.stdout.write(self.style.WARNING('\n⚠️  Some production checks failed'))