from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.utils.html import escape
from .models import Book, CustomUser
from .forms import ExampleForm, SecureBookForm 
import logging

# Security: Set up logging for security events
logger = logging.getLogger(__name__)

def example_form_view(request):
    """
    View demonstrating secure form handling with ExampleForm.
    Shows proper CSRF protection, input validation, and sanitization.
    """
    if request.method == 'POST':
        # Security: CSRF protection is automatically handled by Django middleware
        form = ExampleForm(request.POST)
        
        if form.is_valid():
            # Security: Form data is now cleaned and validated
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            category = form.cleaned_data['category']
            age = form.cleaned_data['age']
            message = form.cleaned_data['message']
            
            # Security: Log form submission (without sensitive data)
            logger.info(f"ExampleForm submitted by: {email} for category: {category}")
            
            # Security: Success message with escaped user input
            messages.success(
                request, 
                f"Thank you, {escape(name)}! Your {category} submission was received."
            )
            
            # In a real application, you would process the form data here
            # For example: save to database, send email, etc.
            
            return redirect('example_form_success')
        else:
            # Security: Form errors are automatically escaped by Django
            messages.error(request, "Please correct the errors below.")
    else:
        form = ExampleForm()
    
    context = {
        'form': form,
        'title': 'Example Form with Security Features'
    }
    return render(request, 'bookshelf/example_form.html', context)

def example_form_success(request):
    """Success page after form submission."""
    return render(request, 'bookshelf/example_form_success.html')

# ... rest of your existing views (book_list, create_book, etc.) ...

@permission_required('bookshelf.can_create')
def book_list(request):
    """
    Secure view that lists books with safe search functionality.
    Uses Django ORM to prevent SQL injection.
    """
    # Security: Safely get search query parameter
    search_query = request.GET.get('q', '').strip()
    
    # Security: Use Django ORM with parameterized queries to prevent SQL injection
    if search_query:
        # Safe search using Django's Q objects and ORM
        books = Book.objects.filter(
            Q(title__icontains=search_query) | 
            Q(author__icontains=search_query)
        )
        
        # Security: Log search queries for monitoring
        logger.info(f"User {request.user} searched for: {search_query}")
    else:
        books = Book.objects.all()
    
    # Security: Pass escaped query back to template for safe display
    context = {
        'books': books,
        'query': escape(search_query)  # Escape user input for safe display
    }
    return render(request, 'bookshelf/book_list.html', context)

@permission_required('bookshelf.can_create')
def create_book(request):
    """
    Secure view for creating books with input validation.
    """
    if request.method == 'POST':
        # Security: CSRF protection is automatically handled by Django middleware
        # Security: Manual input validation
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        publication_year = request.POST.get('publication_year', '').strip()
        
        # Security: Validate and sanitize inputs
        errors = []
        
        if not title or len(title) > 200:
            errors.append('Title is required and must be less than 200 characters.')
        
        if not author or len(author) > 100:
            errors.append('Author is required and must be less than 100 characters.')
        
        try:
            publication_year = int(publication_year)
            current_year = 2024  # This should be dynamic in real applications
            if publication_year < 1000 or publication_year > current_year:
                errors.append('Publication year must be between 1000 and current year.')
        except (ValueError, TypeError):
            errors.append('Publication year must be a valid number.')
        
        if errors:
            # Security: Safe error message display
            for error in errors:
                messages.error(request, escape(error))
        else:
            # Security: Use Django ORM to safely create object
            try:
                Book.objects.create(
                    title=escape(title),  # Additional escaping for safety
                    author=escape(author),
                    publication_year=publication_year
                )
                messages.success(request, 'Book created successfully!')
                logger.info(f"User {request.user} created book: {title}")
                return redirect('book_list')
            except Exception as e:
                # Security: Don't expose internal error details to users
                messages.error(request, 'Error creating book. Please try again.')
                logger.error(f"Error creating book: {e}")
    
    return render(request, 'bookshelf/form_example.html')

@permission_required('bookshelf.can_delete')
def delete_book(request):
    """
    Secure view for deleting books with proper authorization.
    """
    if request.method == 'POST':
        # Security: CSRF protection handled by middleware
        try:
            book_id = int(request.POST.get('book_id', 0))
            # Security: Use get_object_or_404 to safely get object
            book = get_object_or_404(Book, id=book_id)
            book_title = book.title
            book.delete()
            
            # Security: Log deletion for audit trail
            logger.warning(f"User {request.user} deleted book: {book_title}")
            messages.success(request, f'Book "{escape(book_title)}" deleted successfully!')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid book ID.')
        except Exception as e:
            messages.error(request, 'Error deleting book.')
            logger.error(f"Error deleting book: {e}")
    
    return redirect('book_list')

@login_required
def raise_exception(request):
    """
    View that intentionally raises an exception for testing.
    Security: Properly handles exceptions without exposing sensitive info.
    """
    try:
        # This will raise a 404 exception
        raise Http404("This page intentionally raises an exception for testing purposes")
    except Http404:
        # Security: Log the exception for monitoring
        logger.warning(f"User {request.user} accessed raise_exception view")
        raise  # Re-raise the exception for Django to handle

@permission_required('bookshelf.can_delete')
def books(request):
    """
    View that displays books with secure data handling.
    """
    books = Book.objects.all()
    return render(request, 'bookshelf/books.html', {'books': books})

def safe_search_api(request):
    """
    Secure API endpoint for book search.
    Demonstrates safe JSON response handling.
    """
    if request.method == 'GET':
        search_term = request.GET.get('term', '').strip()
        
        # Security: Limit search term length to prevent abuse
        if len(search_term) > 100:
            return JsonResponse({'error': 'Search term too long'}, status=400)
        
        # Security: Use Django ORM for safe database queries
        books = Book.objects.filter(
            title__icontains=search_term
        )[:10]  # Limit results to prevent resource exhaustion
        
        # Security: Safe data serialization
        book_data = [
            {
                'id': book.id,
                'title': escape(book.title),  # Escape for JSON safety
                'author': escape(book.author),
                'year': book.publication_year
            }
            for book in books
        ]
        
        return JsonResponse({'books': book_data})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)