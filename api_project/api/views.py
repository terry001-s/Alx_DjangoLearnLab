from rest_framework import generics, viewsets, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from .models import Book
from .serializers import BookSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission class that allows:
    - Read-only access to any user (authenticated or not)
    - Write access only to admin users
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS requests to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only allow POST, PUT, PATCH, DELETE to admin users
        return request.user and request.user.is_staff

class BookList(generics.ListAPIView):
    """
    API view to retrieve a list of all books.
    Uses ListAPIView to provide read-only endpoint for book collections.
    
    Permission: AllowAny - Anyone can view the book list
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]  # No authentication required for listing


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
    
    Permissions:
    - IsAuthenticatedOrReadOnly: Anyone can view, but only authenticated users can modify
    - Custom permissions can be added for more granular control
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Authenticated users can modify, anyone can view
    
    def perform_create(self, serializer):
        """
        Override to set the user who created the book.
        This is called when a new book instance is created.
        """
        serializer.save()  # You could add: created_by=self.request.user if your model has this field
    
    def get_permissions(self):
        """
        Override to provide different permissions for different actions.
        Example: Allow anyone to list and retrieve, but only admins to create/update/delete.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # More restrictive permissions for write operations
            permission_classes = [IsAuthenticated]
        else:
            # More permissive permissions for read operations
            permission_classes = [permissions.AllowAny]
        
        return [permission() for permission in permission_classes]