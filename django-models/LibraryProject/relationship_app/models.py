from django.db import models

# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=200)

    def __str__ (self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=300)
    author = models.ForeignKey(Author,on_delete=models.CASCADE, related_name='books')

    def __str__(self):
        return f"{self.title} (by {self.author.name})"

class Library(models.Model):
    name = models.CharField(max_length=200)
    books = models.ManyToManyField(Book, related_name='libraries', blank=True)

    def __str__(self):
        return f"{self.name} (Librarian of {self.library.name})" 