from rest_framework import generics, viewsets
from .models import Book
from .serializers import BookSerializer

class BookList(generics.ListAPIView):
    """
    API view to retrieve a list of all books.
    Uses ListAPIView to provide read-only endpoint for book collections.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions for CRUD operations.
    
    Using ModelViewSet automatically provides:
    - GET /books_all/ (list all books)
    - POST /books_all/ (create new book)
    - GET /books_all/{id}/ (retrieve specific book)
    - PUT /books_all/{id}/ (update entire book)
    - PATCH /books_all/{id}/ (partial update of book)
    - DELETE /books_all/{id}/ (delete book)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer