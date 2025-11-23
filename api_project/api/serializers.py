from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the Book model that converts model instances to JSON.
    Includes all fields from the Book model.
    """
    class Meta:
        model = Book
        fields = '__all__'  # This includes all fields from the Book model