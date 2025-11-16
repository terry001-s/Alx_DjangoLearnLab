from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponse, Http404
from .models import Book

# View that requires specific permissions
@permission_required('bookshelf.can_create')
def book_list(request):
    """
    View that lists all books - requires can_create permission
    """
    books = Book.objects.all()
    return render(request, 'bookshelf/book_list.html', {'books': books})

# View that raises an exception
@login_required
def raise_exception(request):
    """
    View that intentionally raises an exception
    """
    # This will raise a 404 exception
    raise Http404("This page intentionally raises an exception")

# Alternative view using permission_required decorator
@permission_required('bookshelf.can_delete')
def books(request):
    """
    View that displays books - requires can_delete permission
    """
    books = Book.objects.all()
    return render(request, 'bookshelf/books.html', {'books': books})

# Additional view to demonstrate multiple permission usage
@permission_required(['bookshelf.can_create', 'bookshelf.can_delete'])
def manage_books(request):
    """
    View that requires both create and delete permissions
    """
    books = Book.objects.all()
    return render(request, 'bookshelf/manage_books.html', {'books': books})