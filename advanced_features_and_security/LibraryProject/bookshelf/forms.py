from django import forms
from django.core.exceptions import ValidationError
from .models import Book
import html

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