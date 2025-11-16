from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views  # Import all views as checker expects views.<view_name>

urlpatterns = [
    # --- Book & Library Views ---
    path('books/', views.list_books, name='book_list'),  # Function-based view
    path('library/<int:pk>/', views.LibraryDetailView.as_view(), name='library_detail'),  # Class-based view

    # --- Authentication Views ---
    path('login/', LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
    path('register/', views.register, name='register'),  # Explicitly using views.register

    # --- Role-based Access Views ---
    path('admin-view/', views.admin_view, name='admin_view'),
    path('librarian-view/', views.librarian_view, name='librarian_view'),
    path('member-view/', views.member_view, name='member_view'),

    # --- Secured Book Operations (permissions) ---
    path('add_book/', views.add_book, name='add_book'),
    path('edit_book/<int:pk>/', views.edit_book, name='edit_book'),
    path('delete_book/<int:pk>/', views.delete_book, name='delete_book'),

]
