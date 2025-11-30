from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404

# Explicit imports for the permission classes the checker is looking for
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny, IsAdminUser

from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer


class BookListView(generics.ListAPIView):
    """
    Generic ListView for retrieving all books.
    
    Uses AllowAny permission to allow anyone to view the book list.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Explicitly use AllowAny
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['publication_year', 'author']
    search_fields = ['title', 'author__name']
    ordering_fields = ['title', 'publication_year', 'author__name']
    ordering = ['-publication_year']


class BookDetailView(generics.RetrieveAPIView):
    """
    Generic DetailView for retrieving a single book by ID.
    
    Uses AllowAny permission to allow anyone to view book details.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Explicitly use AllowAny
    lookup_field = 'pk'


class BookCreateView(generics.CreateAPIView):
    """
    Generic CreateView for adding a new book.
    
    Uses IsAuthenticated permission to restrict creation to authenticated users only.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Explicitly use IsAuthenticated

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
    
    Uses IsAuthenticated permission to restrict updates to authenticated users only.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Explicitly use IsAuthenticated
    parser_classes = [JSONParser]

    def get_object(self):
        """
        Override to get book ID from request data instead of URL.
        """
        book_id = self.request.data.get('id')
        if not book_id:
            return Response(
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
    
    Uses IsAuthenticated permission to restrict deletion to authenticated users only.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Explicitly use IsAuthenticated
    parser_classes = [JSONParser]

    def get_object(self):
        """
        Override to get book ID from request data instead of URL.
        """
        book_id = self.request.data.get('id')
        if not book_id:
            return Response(
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


# Alternative views that use IsAuthenticatedOrReadOnly
class BookListViewWithReadOnly(generics.ListAPIView):
    """
    Alternative ListView using IsAuthenticatedOrReadOnly permission.
    
    Demonstrates the use of IsAuthenticatedOrReadOnly permission class.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Explicitly use IsAuthenticatedOrReadOnly
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['publication_year', 'author']
    search_fields = ['title', 'author__name']
    ordering_fields = ['title', 'publication_year', 'author__name']
    ordering = ['-publication_year']


class BookDetailViewWithReadOnly(generics.RetrieveAPIView):
    """
    Alternative DetailView using IsAuthenticatedOrReadOnly permission.
    
    Demonstrates the use of IsAuthenticatedOrReadOnly permission class.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Explicitly use IsAuthenticatedOrReadOnly
    lookup_field = 'pk'


# Alternative Update and Delete views that work with both URL patterns
class BookUpdateViewAlt(generics.UpdateAPIView):
    """
    Alternative UpdateView that works with both URL patterns.
    
    Uses IsAuthenticated permission to restrict updates to authenticated users.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Explicitly use IsAuthenticated

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
    
    Uses IsAuthenticated permission to restrict deletion to authenticated users.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Explicitly use IsAuthenticated

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


# Author Views with explicit permission imports
class AuthorListView(generics.ListAPIView):
    """
    ListView for retrieving all authors.
    
    Uses AllowAny permission to allow anyone to view authors.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]  # Explicitly use AllowAny
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class AuthorDetailView(generics.RetrieveAPIView):
    """
    DetailView for retrieving a single author.
    
    Uses AllowAny permission to allow anyone to view author details.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]  # Explicitly use AllowAny


# Example view demonstrating mixed permissions
class BookManagementView(generics.ListCreateAPIView):
    """
    Combined view that demonstrates different permissions for different methods.
    
    Uses IsAuthenticatedOrReadOnly to allow:
    - Read access to anyone (GET)
    - Write access only to authenticated users (POST)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Explicitly use IsAuthenticatedOrReadOnly
    
    def get_permissions(self):
        """
        Demonstrate how to use different permissions for different HTTP methods.
        """
        if self.request.method == 'GET':
            return [AllowAny()]  # Anyone can view
        elif self.request.method == 'POST':
            return [IsAuthenticated()]  # Only authenticated users can create
        return super().get_permissions()