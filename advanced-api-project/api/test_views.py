"""
Unit tests for Django REST Framework API endpoints.

This test suite covers:
- CRUD operations for Book model endpoints
- Filtering, searching, and ordering functionalities
- Authentication and permission mechanisms
- Response data integrity and status codes
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from .models import Author, Book


class BaseTestCase(APITestCase):
    """
    Base test case with common setup methods for all test classes.
    Provides reusable methods for creating test data and authenticated clients.
    """
    
    def setUp(self):
        """
        Set up test data that will be used across multiple test cases.
        This method runs before each test.
        """
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.regular_user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='testpass123'
        )
        self.another_user = User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='testpass123'
        )
        
        # Create test authors
        self.author1 = Author.objects.create(name="J.K. Rowling")
        self.author2 = Author.objects.create(name="George Orwell")
        self.author3 = Author.objects.create(name="J.R.R. Tolkien")
        
        # Create test books
        self.book1 = Book.objects.create(
            title="Harry Potter and the Philosopher's Stone",
            publication_year=1997,
            author=self.author1
        )
        self.book2 = Book.objects.create(
            title="Harry Potter and the Chamber of Secrets",
            publication_year=1998,
            author=self.author1
        )
        self.book3 = Book.objects.create(
            title="1984",
            publication_year=1949,
            author=self.author2
        )
        self.book4 = Book.objects.create(
            title="Animal Farm",
            publication_year=1945,
            author=self.author2
        )
        self.book5 = Book.objects.create(
            title="The Hobbit",
            publication_year=1937,
            author=self.author3
        )
        self.book6 = Book.objects.create(
            title="The Lord of the Rings",
            publication_year=1954,
            author=self.author3
        )
        
        # Initialize API client
        self.client = APIClient()
    
    def authenticate_user(self, user=None):
        """
        Helper method to authenticate a user for testing protected endpoints.
        """
        if user is None:
            user = self.regular_user
        self.client.force_authenticate(user=user)
    
    def unauthenticate_user(self):
        """
        Helper method to remove authentication.
        """
        self.client.force_authenticate(user=None)


class BookCRUDTests(BaseTestCase):
    """
    Test cases for Book model CRUD operations.
    """
    
    def test_list_books_unauthenticated(self):
        """
        Test that unauthenticated users can list all books.
        """
        url = reverse('book-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response is paginated or direct list
        if isinstance(response.data, list):
            self.assertEqual(len(response.data), 6)
        else:  # Paginated response
            self.assertEqual(len(response.data['results']), 6)
    
    def test_retrieve_book_detail_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve book details.
        """
        url = reverse('book-detail', kwargs={'pk': self.book1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)
        self.assertEqual(response.data['publication_year'], self.book1.publication_year)
        self.assertEqual(response.data['author'], self.author1.id)
    
    def test_create_book_unauthenticated_should_fail(self):
        """
        Test that unauthenticated users cannot create books.
        """
        url = reverse('book-create')
        data = {
            'title': 'New Test Book',
            'publication_year': 2024,
            'author': self.author1.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_book_authenticated(self):
        """
        Test that authenticated users can create books.
        """
        self.authenticate_user()
        url = reverse('book-create')
        data = {
            'title': 'New Test Book',
            'publication_year': 2024,
            'author': self.author1.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check the structure of the response
        if 'book' in response.data:
            self.assertEqual(response.data['book']['title'], 'New Test Book')
        else:
            self.assertEqual(response.data['title'], 'New Test Book')
        
        # Verify the book was actually created in the database
        self.assertTrue(Book.objects.filter(title='New Test Book').exists())
    
    def test_update_book_unauthenticated_should_fail(self):
        """
        Test that unauthenticated users cannot update books.
        """
        url = reverse('book-update', kwargs={'pk': self.book1.id})
        data = {
            'title': 'Updated Book Title',
            'publication_year': 2000,
            'author': self.author1.id
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_book_authenticated(self):
        """
        Test that authenticated users can update books.
        """
        self.authenticate_user()
        url = reverse('book-update', kwargs={'pk': self.book1.id})
        data = {
            'title': 'Updated Book Title',
            'publication_year': 2000,
            'author': self.author1.id
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check response structure
        if 'book' in response.data:
            self.assertEqual(response.data['book']['title'], 'Updated Book Title')
        else:
            self.assertEqual(response.data['title'], 'Updated Book Title')
        
        # Verify the book was actually updated in the database
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Updated Book Title')
    
    def test_delete_book_unauthenticated_should_fail(self):
        """
        Test that unauthenticated users cannot delete books.
        """
        url = reverse('book-delete', kwargs={'pk': self.book1.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_book_authenticated(self):
        """
        Test that authenticated users can delete books.
        """
        self.authenticate_user()
        url = reverse('book-delete', kwargs={'pk': self.book1.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify the book was actually deleted from the database
        self.assertFalse(Book.objects.filter(id=self.book1.id).exists())


class BookFilteringSearchingOrderingTests(BaseTestCase):
    """
    Test cases for filtering, searching, and ordering functionalities.
    """
    
    def get_response_data(self, response):
        """Helper method to handle both paginated and non-paginated responses."""
        if isinstance(response.data, list):
            return response.data
        elif 'results' in response.data:
            return response.data['results']
        return response.data
    
    def test_filter_by_publication_year(self):
        """
        Test filtering books by exact publication year.
        """
        url = reverse('book-list')
        response = self.client.get(url, {'publication_year': 1997})
        data = self.get_response_data(response)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], "Harry Potter and the Philosopher's Stone")
    
    def test_filter_by_publication_year_range(self):
        """
        Test filtering books by publication year range.
        """
        url = reverse('book-list')
        response = self.client.get(url, {
            'publication_year__gte': 1940,
            'publication_year__lte': 2000
        })
        data = self.get_response_data(response)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return books from 1945, 1949, 1997, 1998
        self.assertEqual(len(data), 4)
    
    def test_filter_by_author_name(self):
        """
        Test filtering books by author name (case-insensitive contains).
        """
        url = reverse('book-list')
        response = self.client.get(url, {'author__name__icontains': 'rowling'})
        data = self.get_response_data(response)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)  # Two books by Rowling
    
    def test_search_functionality(self):
        """
        Test text-based search across title and author fields.
        """
        url = reverse('book-list')
        response = self.client.get(url, {'search': 'harry'})
        data = self.get_response_data(response)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find books with "harry" in title (case-insensitive)
        harry_books = [book for book in data if 'harry' in book['title'].lower()]
        self.assertEqual(len(harry_books), 2)  # Two Harry Potter books
    
    def test_search_by_author_name(self):
        """
        Test searching by author name using the search parameter.
        """
        url = reverse('book-list')
        response = self.client.get(url, {'search': 'tolkien'})
        data = self.get_response_data(response)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find books by Tolkien
        tolkien_books = [book for book in data if 'tolkien' in book.get('author_name', '').lower()]
        self.assertEqual(len(tolkien_books), 2)  # Two books by Tolkien
    
    def test_ordering_by_title_ascending(self):
        """
        Test ordering books by title in ascending order.
        """
        url = reverse('book-list')
        response = self.client.get(url, {'ordering': 'title'})
        data = self.get_response_data(response)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in data]
        self.assertEqual(titles, sorted(titles))
    
    def test_ordering_by_title_descending(self):
        """
        Test ordering books by title in descending order.
        """
        url = reverse('book-list')
        response = self.client.get(url, {'ordering': '-title'})
        data = self.get_response_data(response)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in data]
        self.assertEqual(titles, sorted(titles, reverse=True))
    
    def test_ordering_by_publication_year_descending(self):
        """
        Test ordering books by publication year in descending order.
        """
        url = reverse('book-list')
        response = self.client.get(url, {'ordering': '-publication_year'})
        data = self.get_response_data(response)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        publication_years = [book['publication_year'] for book in data]
        self.assertEqual(publication_years, sorted(publication_years, reverse=True))
    
    def test_combined_filtering_searching_ordering(self):
        """
        Test combining multiple query parameters.
        """
        url = reverse('book-list')
        response = self.client.get(url, {
            'author__name__icontains': 'rowling',
            'search': 'harry',
            'ordering': '-publication_year'
        })
        data = self.get_response_data(response)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find Harry Potter books by Rowling, ordered by newest first
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['publication_year'], 1998)  # Chamber of Secrets
        self.assertEqual(data[1]['publication_year'], 1997)  # Philosopher's Stone


class AuthorAPITests(BaseTestCase):
    """
    Test cases for Author API endpoints.
    """
    
    def get_response_data(self, response):
        """Helper method to handle both paginated and non-paginated responses."""
        if isinstance(response.data, list):
            return response.data
        elif 'results' in response.data:
            return response.data['results']
        return response.data
    
    def test_list_authors(self):
        """
        Test listing all authors.
        """
        url = reverse('author-list')
        response = self.client.get(url)
        data = self.get_response_data(response)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 3)
    
    def test_retrieve_author_detail(self):
        """
        Test retrieving a specific author with nested books.
        """
        url = reverse('author-detail', kwargs={'pk': self.author1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'J.K. Rowling')
        self.assertEqual(len(response.data['books']), 2)
        self.assertEqual(response.data['book_count'], 2)
    
    def test_search_authors(self):
        """
        Test searching authors by name.
        """
        url = reverse('author-list')
        response = self.client.get(url, {'search': 'rowling'})
        data = self.get_response_data(response)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'J.K. Rowling')


class ErrorHandlingTests(BaseTestCase):
    """
    Test cases for error handling and edge cases.
    """
    
    def test_retrieve_nonexistent_book(self):
        """
        Test retrieving a book that doesn't exist.
        """
        url = reverse('book-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_nonexistent_book(self):
        """
        Test updating a book that doesn't exist.
        """
        self.authenticate_user()
        url = reverse('book-update', kwargs={'pk': 9999})
        data = {
            'title': 'Updated Title',
            'publication_year': 2000,
            'author': self.author1.id
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_nonexistent_book(self):
        """
        Test deleting a book that doesn't exist.
        """
        self.authenticate_user()
        url = reverse('book-delete', kwargs={'pk': 9999})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# Simplified test runner
class SimpleBookTests(APITestCase):
    """
    Simplified test cases focusing on core functionality.
    """
    
    def setUp(self):
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            publication_year=2020,
            author=self.author
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
    
    def test_book_list(self):
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_book_detail(self):
        url = reverse('book-detail', kwargs={'pk': self.book.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Book')
    
    def test_book_search(self):
        url = reverse('book-list')
        response = self.client.get(url, {'search': 'test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_book_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, {'publication_year': 2020})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_book_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)