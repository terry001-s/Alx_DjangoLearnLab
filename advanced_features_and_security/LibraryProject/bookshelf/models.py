from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Keep the username field but add our custom fields
    date_of_birth = models.DateField(null=True, blank=True)
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        null=True, 
        blank=True
    )
    
    def __str__(self):
        return self.username
    
    class Meta:
        permissions = [
            ("can_create", "Can create items"),
            ("can_delete", "Can delete items"),
        ]

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_year = models.IntegerField()

    def __str__(self):
        return f"{self.title} by {self.author} ({self.publication_year})"
    
    class Meta:
        permissions = [
            ("can_create", "Can create books"),
            ("can_delete", "Can delete books"),
        ]