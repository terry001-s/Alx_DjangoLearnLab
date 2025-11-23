from django.db import models

class Book(models.Model):
    """
    Simple Book model for API demonstration.
    """
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_year = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ['-created_at']