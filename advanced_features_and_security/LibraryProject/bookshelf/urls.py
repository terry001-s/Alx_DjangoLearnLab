from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.book_list, name='book_list'),
    path('books/create/', views.create_book, name='create_book'),
    path('books/delete/', views.delete_book, name='delete_book'),
    path('raise-exception/', views.raise_exception, name='raise_exception'),
    path('books-view/', views.books, name='books'),
    path('api/search/', views.safe_search_api, name='safe_search_api'),
    path('example-form/', views.example_form_view, name='example_form_view'),
    path('example-form/success/', views.example_form_success, name='example_form_success'),
]