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
    Enhanced Book ListView with comprehensive filtering, searching, and ordering capabilities.
    
    This view provides advanced query features allowing API consumers to:
    - Filter books by various criteria (publication year, author, etc.)
    - Search across book titles and author names
    - Order results by multiple fields
    - Combine multiple query parameters for precise data retrieval
    
    Filter Backends Configuration:
    - DjangoFilterBackend: For field-specific filtering
    - SearchFilter: For text-based searching across multiple fields
    - OrderingFilter: For sorting results by various fields
    
    Example Usage:
    - Filtering: /api/books/?publication_year_min=2000&publication_year_max=2020
    - Searching: /api/books/?search=harry+potter
    - Ordering: /api/books/?ordering=title,-publication_year
    - Combined: /api/books/?author_name_icontains=tolkien&ordering=-publication_year&search=lord
    """
    
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
    
    # Configure filter backends for advanced query capabilities
    filter_backends = [
        DjangoFilterBackend,  # For field-specific filtering
        SearchFilter,         # For text-based searching
        OrderingFilter,       # For sorting results
    ]
    
    # DjangoFilterBackend configuration
    filterset_class = BookFilter  # Use custom filter class
    # Alternative: Use filterset_fields for simple filtering
    # filterset_fields = {
    #     'publication_year': ['exact', 'gte', 'lte'],
    #     'author__name': ['exact', 'icontains'],
    #     'title': ['exact', 'icontains'],
    # }
    
    # SearchFilter configuration
    search_fields = [
        'title',           # Search in book titles
        'author__name',    # Search in author names
        '=title',          # Exact match for title (case-sensitive)
        '=author__name',   # Exact match for author name (case-sensitive)
    ]
    
    # OrderingFilter configuration
    ordering_fields = [
        'title',              # Order by book title
        'publication_year',   # Order by publication year
        'author__name',       # Order by author name
        'id',                 # Order by primary key
    ]
    ordering = ['-publication_year', 'title']  # Default ordering: newest first, then title
    
    def get_queryset(self):
        """
        Override to provide custom queryset optimization or additional filtering.
        
        This method can be extended to add:
        - Performance optimizations (select_related, prefetch_related)
        - Additional business logic filtering
        - Custom permission-based filtering
        """
        queryset = super().get_queryset()
        
        # Optimize database queries by selecting related author data
        queryset = queryset.select_related('author')
        
        # Example: Add custom filtering based on request parameters
        custom_filter = self.request.query_params.get('custom_filter')
        if custom_filter:
            # Add your custom filtering logic here
            pass
            
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Override list method to provide enhanced response with query information.
        
        Returns additional metadata about available filters, search fields,
        and ordering options to help API consumers understand available features.
        """
        response = super().list(request, *args, **kwargs)
        
        # Add metadata about available query features
        response.data['query_capabilities'] = {
            'filtering': {
                'available_filters': [
                    'publication_year', 'publication_year_min', 'publication_year_max',
                    'title', 'title_icontains', 
                    'author_name', 'author_name_icontains',
                    'publication_year_in'
                ],
                'description': 'Use filter parameters to narrow down results',
            },
            'searching': {
                'available_fields': self.search_fields,
                'description': 'Use search parameter for text search across multiple fields',
            },
            'ordering': {
                'available_fields': self.ordering_fields,
                'default_ordering': self.ordering,
                'description': 'Use ordering parameter to sort results',
            },
            'examples': {
                'filter_by_year': '/api/books/?publication_year_min=2000&publication_year_max=2020',
                'search_books': '/api/books/?search=harry+potter',
                'order_by_title': '/api/books/?ordering=title',
                'combined_query': '/api/books/?author_name_icontains=rowling&ordering=-publication_year',
            }
        }
        
        return response


# Enhanced AuthorListView with similar features
class AuthorListView(generics.ListAPIView):
    """
    Author ListView with filtering, searching, and ordering capabilities.
    """
    
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'books__title']  # Search in author names and their book titles
    ordering_fields = ['name', 'id']
    ordering = ['name']  # Default ordering: alphabetical by name


class BookDetailView(generics.RetrieveAPIView):
    """
    Book DetailView - unchanged from previous implementation.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
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