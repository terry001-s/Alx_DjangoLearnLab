from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer
from .permissions import IsAuthenticatedOrReadOnly, IsAdminOrReadOnly



class BookListView(generics.ListAPIView):
    """
    Generic ListView for retrieving all books.
    
    Provides read-only endpoint to list all Book instances.
    Uses BookSerializer for data serialization.
    
    Features:
    - Search by title and author name
    - Filter by publication year and author
    - Ordering by various fields
    - Pagination (configured in settings)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to view books
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['publication_year', 'author']
    search_fields = ['title', 'author__name']
    ordering_fields = ['title', 'publication_year', 'author__name']
    ordering = ['-publication_year']  # Default ordering: newest first


class BookDetailView(generics.RetrieveAPIView):
    """
    Generic DetailView for retrieving a single book by ID.
    
    Provides read-only endpoint to retrieve specific Book instance.
    Uses primary key (ID) to identify the book.
    
    Features:
    - Automatic 404 handling for non-existent books
    - Detailed book information with author details
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to view book details
    lookup_field = 'pk'  # Default lookup field (primary key)


class BookCreateView(generics.CreateAPIView):
    """
    Generic CreateView for adding a new book.
    
    Handles POST requests to create new Book instances.
    Includes data validation through BookSerializer.
    
    Features:
    - Automatic validation of publication_year (not in future)
    - Permission restriction to authenticated users only
    - Custom success response
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Only authenticated users can create books

    def perform_create(self, serializer):
        """
        Custom method called when creating a new book instance.
        Can be used to add additional logic before saving.
        """
        # Additional validation or processing can be added here
        serializer.save()

    def create(self, request, *args, **kwargs):
        """
        Override create method to customize response.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Custom success response
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
    
    Handles PUT (full update) and PATCH (partial update) requests.
    Uses primary key to identify which book to update.
    
    Features:
    - Full and partial update support
    - Permission restriction to authenticated users only
    - Data validation through BookSerializer
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can update books
    lookup_field = 'pk'

    def perform_update(self, serializer):
        """
        Custom method called when updating a book instance.
        """
        serializer.save()

    def update(self, request, *args, **kwargs):
        """
        Override update method to customize response.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Custom success response
        return Response(
            {
                'message': 'Book updated successfully',
                'book': serializer.data
            }
        )


class BookDeleteView(generics.DestroyAPIView):
    """
    Generic DeleteView for removing a book.
    
    Handles DELETE requests to remove Book instances.
    Uses primary key to identify which book to delete.
    
    Features:
    - Permission restriction to authenticated users only
    - Custom success response
    - Automatic 404 handling for non-existent books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can delete books
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy method to customize response.
        """
        instance = self.get_object()
        book_title = instance.title
        self.perform_destroy(instance)
        
        # Custom success response
        return Response(
            {
                'message': f'Book "{book_title}" deleted successfully'
            },
            status=status.HTTP_204_NO_CONTENT
        )


# Additional Author Views for completeness
class AuthorListView(generics.ListAPIView):
    """
    ListView for retrieving all authors with their books.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class AuthorDetailView(generics.RetrieveAPIView):
    """
    DetailView for retrieving a single author with nested books.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.AllowAny]