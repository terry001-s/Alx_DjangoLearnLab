from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import BookList, BookViewSet

# Create a router and register our ViewSet with it
router = DefaultRouter()
router.register(r'books_all', BookViewSet, basename='book_all')

urlpatterns = [
    # Route for the BookList view (ListAPIView) - keeping the original endpoint
    path('books/', BookList.as_view(), name='book-list'),

    # Token authentication endpoint - allows users to obtain tokens
    path('auth-token/', obtain_auth_token, name='api_token_auth'),
    
    # Include the router URLs for BookViewSet (all CRUD operations)
    path('', include(router.urls)),  # This includes all routes registered with the router
]