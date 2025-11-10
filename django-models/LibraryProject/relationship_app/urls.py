from django.urls import path
from .views import list_books, LibraryDetailView  # import the views

urlpatterns = [
    path('books/', list_books, name='book_list'),  # function-based view
    path('library/<int:pk>/', LibraryDetailView.as_view(), name='library_detail'),  # class-based view
]
