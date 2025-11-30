from rest_framework import serializers
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    """
    Custom serializer for the Book model.
    
    Handles serialization of Book instances to JSON and deserialization from JSON.
    Includes custom validation for publication_year to ensure it's not in the future.
    
    Fields:
    - All fields from the Book model are included: id, title, publication_year, author
    
    Validation:
    - Custom validate_publication_year method ensures publication year is not in the future
    - Built-in ModelSerializer validation for other fields
    """
    
    class Meta:
        model = Book
        fields = '__all__'  # Include all fields from the Book model
    
    def validate_publication_year(self, value):
        """
        Custom validation for publication_year field.
        
        Args:
            value (int): The publication year to validate
            
        Returns:
            int: The validated publication year if it passes validation
            
        Raises:
            ValidationError: If the publication year is in the future
        """
        current_year = datetime.now().year
        
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. Current year is {current_year}."
            )
        
        if value < 1000:
            raise serializers.ValidationError(
                "Publication year must be a valid year (1000 or later)."
            )
        
        return value
    
    def validate(self, data):
        """
        Object-level validation for the entire Book instance.
        
        Args:
            data (dict): The data being validated
            
        Returns:
            dict: The validated data
            
        Raises:
            ValidationError: If the validation fails
        """
        # Example of object-level validation: Check if author already has a book with same title
        title = data.get('title')
        author = data.get('author')
        
        if title and author:
            # Check for existing books with same title and author (excluding current instance if updating)
            existing_books = Book.objects.filter(title=title, author=author)
            if self.instance:  # If updating an existing instance
                existing_books = existing_books.exclude(pk=self.instance.pk)
            
            if existing_books.exists():
                raise serializers.ValidationError(
                    f"Author {author.name} already has a book titled '{title}'."
                )
        
        return data


class AuthorSerializer(serializers.ModelSerializer):
    """
    Custom serializer for the Author model with nested Book serialization.
    
    Handles serialization of Author instances including their related books.
    Uses BookSerializer to nest book information within author data.
    
    Fields:
    - id: The author's unique identifier
    - name: The author's name
    - books: Nested serialization of related books using BookSerializer
    
    Relationships:
    - One-to-many relationship with Book model is represented through nested serialization
    - The 'books' field dynamically includes all books written by the author
    """
    
    # Nested serializer for related books
    # read_only=True prevents books from being created/updated through author serializer
    books = BookSerializer(many=True, read_only=True)
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books']  # Include id, name, and nested books
    
    def validate_name(self, value):
        """
        Custom validation for author name field.
        
        Args:
            value (str): The author name to validate
            
        Returns:
            str: The validated author name
            
        Raises:
            ValidationError: If the name contains invalid characters or is too short
        """
        value = value.strip()
        
        if len(value) < 2:
            raise serializers.ValidationError("Author name must be at least 2 characters long.")
        
        if len(value) > 100:
            raise serializers.ValidationError("Author name cannot exceed 100 characters.")
        
        # Basic validation for name format (letters, spaces, hyphens, apostrophes)
        if not all(c.isalpha() or c in ' -.\'' for c in value):
            raise serializers.ValidationError(
                "Author name can only contain letters, spaces, hyphens, apostrophes, and periods."
            )
        
        return value