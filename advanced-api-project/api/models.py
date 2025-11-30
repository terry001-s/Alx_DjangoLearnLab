from django.db import models

class Author(models.Model):
    """
    Author model representing a book author.
    
    Fields:
    - name: CharField to store the author's full name (max 100 characters)
    
    Relationships:
    - One-to-many relationship with Book model (one author can have multiple books)
    """
    name = models.CharField(max_length=100, help_text="Full name of the author")
    
    def __str__(self):
        """
        String representation of the Author model.
        Returns the author's name for easy identification.
        """
        return self.name
    
    class Meta:
        ordering = ['name']  # Order authors alphabetically by name


class Book(models.Model):
    """
    Book model representing a published book.
    
    Fields:
    - title: CharField for the book's title (max 200 characters)
    - publication_year: IntegerField for the year the book was published
    - author: ForeignKey linking to the Author model, establishing a one-to-many relationship
    
    Relationships:
    - Many-to-one relationship with Author model (many books can belong to one author)
    - When an author is deleted, their books are protected from deletion
    """
    title = models.CharField(max_length=200, help_text="Title of the book")
    publication_year = models.IntegerField(help_text="Year the book was published")
    author = models.ForeignKey(
        Author, 
        on_delete=models.PROTECT,  # Protect books from deletion if author is deleted
        related_name='books',  # Reverse relation name: author.books.all()
        help_text="Author who wrote this book"
    )
    
    def __str__(self):
        """
        String representation of the Book model.
        Returns a formatted string with title, author, and publication year.
        """
        return f'"{self.title}" by {self.author.name} ({self.publication_year})'
    
    class Meta:
        ordering = ['-publication_year', 'title']  # Order by most recent first, then title
        unique_together = ['title', 'author']  # Prevent duplicate books by same author