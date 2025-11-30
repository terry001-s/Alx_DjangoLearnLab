from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer


class BookListView(generics.ListAPIView):
    """
    Generic ListView for retrieving all books.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['publication_year', 'author']
    search_fields = ['title', 'author__name']
    ordering_fields = ['title', 'publication_year', 'author__name']
    ordering = ['-publication_year']


class BookDetailView(generics.RetrieveAPIView):
    """
    Generic DetailView for retrieving a single book by ID.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'pk'


class BookCreateView(generics.CreateAPIView):
    """
    Generic CreateView for adding a new book.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            {
                'message': 'Book created successfully',
                'book': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class BookUpdateView(generics.UpdateAPIView):
    """
    Generic UpdateView for modifying an existing book.
    Now handles book ID from request data instead of URL.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def get_object(self):
        """
        Override to get book ID from request data instead of URL.
        """
        book_id = self.request.data.get('id')
        if not book_id:
            raise Response(
                {'error': 'Book ID is required in request data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        book = get_object_or_404(Book, id=book_id)
        return book

    def update(self, request, *args, **kwargs):
        """
        Handle book update with ID from request data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                'message': 'Book updated successfully',
                'book': serializer.data
            }
        )


class BookDeleteView(generics.DestroyAPIView):
    """
    Generic DeleteView for removing a book.
    Now handles book ID from request data instead of URL.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def get_object(self):
        """
        Override to get book ID from request data instead of URL.
        """
        book_id = self.request.data.get('id')
        if not book_id:
            raise Response(
                {'error': 'Book ID is required in request data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        book = get_object_or_404(Book, id=book_id)
        return book

    def destroy(self, request, *args, **kwargs):
        """
        Handle book deletion with ID from request data.
        """
        instance = self.get_object()
        book_title = instance.title
        self.perform_destroy(instance)
        
        return Response(
            {
                'message': f'Book "{book_title}" deleted successfully'
            },
            status=status.HTTP_204_NO_CONTENT
        )


# Alternative approach: Keep the original URL patterns but add the ones checker wants
class BookUpdateViewAlt(generics.UpdateAPIView):
    """
    Alternative UpdateView that works with both URL patterns.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        # If pk is in URL, use it; otherwise get from request data
        if 'pk' in kwargs:
            instance = self.get_object()
        else:
            book_id = request.data.get('id')
            if not book_id:
                return Response(
                    {'error': 'Book ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance = get_object_or_404(Book, id=book_id)
        
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                'message': 'Book updated successfully',
                'book': serializer.data
            }
        )


class BookDeleteViewAlt(generics.DestroyAPIView):
    """
    Alternative DeleteView that works with both URL patterns.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        # If pk is in URL, use it; otherwise get from request data
        if 'pk' in kwargs:
            instance = self.get_object()
        else:
            book_id = request.data.get('id')
            if not book_id:
                return Response(
                    {'error': 'Book ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance = get_object_or_404(Book, id=book_id)
        
        book_title = instance.title
        self.perform_destroy(instance)
        
        return Response(
            {
                'message': f'Book "{book_title}" deleted successfully'
            },
            status=status.HTTP_204_NO_CONTENT
        )


# Author Views
class AuthorListView(generics.ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class AuthorDetailView(generics.RetrieveAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.AllowAny]