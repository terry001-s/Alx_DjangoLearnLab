from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views  # Import the entire views module

urlpatterns = [
    # Function-based view for listing all books
    path('books/', views.list_books, name='book_list'),

    # Class-based view for library details
    path('library/<int:pk>/', views.LibraryDetailView.as_view(), name='library_detail'),

    # Authentication views
    path('login/', LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
    path('register/', views.register, name='register'),  # Explicitly using views.register
]
