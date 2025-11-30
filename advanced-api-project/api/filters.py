import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    """
    Custom filter class for Book model with advanced filtering options.
    
    Provides comprehensive filtering capabilities for the Book model
    including range filters, exact matches, and case-insensitive searches.
    """
    
    # Range filters for publication year
    publication_year_min = django_filters.NumberFilter(
        field_name='publication_year', 
        lookup_expr='gte',
        help_text="Filter books published in or after this year"
    )
    publication_year_max = django_filters.NumberFilter(
        field_name='publication_year', 
        lookup_expr='lte',
        help_text="Filter books published in or before this year"
    )
    
    # Case-insensitive title search
    title_icontains = django_filters.CharFilter(
        field_name='title', 
        lookup_expr='icontains',
        help_text="Case-insensitive search in book titles"
    )
    
    # Exact author name filter
    author_name = django_filters.CharFilter(
        field_name='author__name', 
        lookup_expr='iexact',
        help_text="Exact match for author name (case-insensitive)"
    )
    
    # Author name contains filter
    author_name_icontains = django_filters.CharFilter(
        field_name='author__name', 
        lookup_expr='icontains',
        help_text="Case-insensitive search in author names"
    )

    class Meta:
        model = Book
        fields = {
            'title': ['exact', 'icontains'],
            'author__name': ['exact', 'icontains'],
            'publication_year': ['exact', 'gte', 'lte'],
        }