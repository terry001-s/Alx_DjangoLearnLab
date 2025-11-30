from rest_framework import permissions

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission class that allows:
    - Read-only access to any user (authenticated or not)
    - Write access only to authenticated users
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS requests to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only allow POST, PUT, PATCH, DELETE to authenticated users
        return request.user and request.user.is_authenticated


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission class that allows:
    - Read-only access to any user
    - Write access only to admin users
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS requests to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only allow write operations to admin users
        return request.user and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission class that allows:
    - Read-only access to any user
    - Write access only to the owner of the object
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        # This assumes your Book model has a 'owner' field
        return obj.owner == request.user