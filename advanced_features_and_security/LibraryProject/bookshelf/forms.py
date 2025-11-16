from django import forms
from django.core.exceptions import ValidationError
from .models import Book
import html
import re

class ExampleForm(forms.Form):
    """
    ExampleForm demonstrating secure form practices with various field types.
    This form showcases security measures like input validation, sanitization,
    and CSRF protection.
    """
    
    # Security: Text field with length validation
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your name',
            'maxlength': '100'
        }),
        help_text="Enter your full name (max 100 characters)"
    )
    
    # Security: Email field with built-in validation
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        }),
        help_text="Enter a valid email address"
    )
    
    # Security: Choice field with limited options
    CATEGORY_CHOICES = [
        ('book', 'Book'),
        ('author', 'Author'),
        ('genre', 'Genre'),
    ]
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text="Select a category"
    )
    
    # Security: Integer field with range validation
    age = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=120,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your age',
            'min': '0',
            'max': '120'
        }),
        help_text="Enter your age (optional, 0-120)"
    )
    
    # Security: Text area with sanitization
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your message',
            'rows': 4,
            'maxlength': '500'
        }),
        help_text="Enter your message (max 500 characters)"
    )
    
    # Security: Boolean field for agreements
    agree_to_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="You must agree to the terms and conditions"
    )

    def clean_name(self):
        """Security: Sanitize and validate name field."""
        name = self.cleaned_data['name'].strip()
        
        # Security: Check for minimum length
        if len(name) < 2:
            raise ValidationError("Name must be at least 2 characters long.")
        
        # Security: Check for maximum length (redundant but safe)
        if len(name) > 100:
            raise ValidationError("Name cannot exceed 100 characters.")
        
        # Security: Basic XSS prevention through escaping
        name = html.escape(name)
        
        # Security: Validate name contains only allowed characters
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', name):
            raise ValidationError("Name can only contain letters, spaces, hyphens, apostrophes, and periods.")
        
        return name

    def clean_email(self):
        """Security: Additional email validation."""
        email = self.cleaned_data['email'].strip().lower()
        
        # Security: Basic email format validation (Django does this already, but extra safety)
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Please enter a valid email address.")
        
        # Security: Prevent potential email header injection
        if any(char in email for char in ['\r', '\n', '\0']):
            raise ValidationError("Invalid characters in email address.")
        
        return email

    def clean_message(self):
        """Security: Sanitize message content."""
        message = self.cleaned_data.get('message', '').strip()
        
        if message:
            # Security: Limit message length
            if len(message) > 500:
                raise ValidationError("Message cannot exceed 500 characters.")
            
            # Security: Basic XSS prevention
            message = html.escape(message)
            
            # Security: Remove potentially dangerous patterns
            dangerous_patterns = [
                r'<script.*?>.*?</script>',
                r'javascript:',
                r'onload=',
                r'onerror=',
                r'onclick=',
            ]
            
            for pattern in dangerous_patterns:
                message = re.sub(pattern, '', message, flags=re.IGNORECASE)
        
        return message

    def clean(self):
        """Security: Cross-field validation."""
        cleaned_data = super().clean()
        
        # Security: Example of cross-field validation
        age = cleaned_data.get('age')
        category = cleaned_data.get('category')
        
        if age and age < 18 and category == 'book':
            # Security: Log this for monitoring (in real application)
            # logger.info(f"Minor user accessing book category: {cleaned_data.get('email')}")
            pass
        
        return cleaned_data

class SecureBookForm(forms.ModelForm):
    """
    Secure form with custom validation and input sanitization.
    """
    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']
        widgets = {
            'title': forms.TextInput(attrs={
                'maxlength': '200',
                'pattern': '.{1,200}',
                'title': 'Title must be between 1 and 200 characters'
            }),
            'author': forms.TextInput(attrs={
                'maxlength': '100',
                'pattern': '.{1,100}',
                'title': 'Author name must be between 1 and 100 characters'
            }),
            'publication_year': forms.NumberInput(attrs={
                'min': '1000',
                'max': '2030',  # Reasonable future year
                'title': 'Publication year must be between 1000 and 2030'
            })
        }

    def clean_title(self):
        """Security: Sanitize and validate title input."""
        title = self.cleaned_data['title'].strip()
        
        # Security: Basic XSS prevention
        title = html.escape(title)
        
        if len(title) < 1:
            raise ValidationError("Title cannot be empty.")
        if len(title) > 200:
            raise ValidationError("Title cannot exceed 200 characters.")
        
        return title

    def clean_author(self):
        """Security: Sanitize and validate author input."""
        author = self.cleaned_data['author'].strip()
        
        # Security: Basic XSS prevention
        author = html.escape(author)
        
        if len(author) < 1:
            raise ValidationError("Author cannot be empty.")
        if len(author) > 100:
            raise ValidationError("Author name cannot exceed 100 characters.")
        
        return author

    def clean_publication_year(self):
        """Security: Validate publication year."""
        year = self.cleaned_data['publication_year']
        
        if year < 1000 or year > 2030:
            raise ValidationError("Publication year must be between 1000 and 2030.")
        
        return year