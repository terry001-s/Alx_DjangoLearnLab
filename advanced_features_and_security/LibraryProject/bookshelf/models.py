from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
     username = None
     email = models.EmailField(_('email address'), unique=True)

    # Keep the username field but add our custom fields
     date_of_birth = models.DateField(null=True, blank=True)
     profile_photo = models.ImageField(
        upload_to='profile_photos/',
        null=True, 
        blank=True
    )
    
      # Set the custom manager
     objects = CustomUserManager()

    # Set email as the USERNAME_FIELD
     USERNAME_FIELD = 'email'
     REQUIRED_FIELDS = []

     def __str__(self):
        return self.email
    
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