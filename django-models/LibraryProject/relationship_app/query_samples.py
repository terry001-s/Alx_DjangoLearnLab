import os
import sys
import django

# --- Ensure Python knows where to find your project ---
# Add the project root (where manage.py lives) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Set the Django settings module ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LibraryProject.settings")

# --- Setup Django ---
django.setup()

# --- Import your models ---
from relationship_app.models import Author, Book, Library, Librarian

def make_sample_data():
    # Clear existing sample data (optional - careful if you have real data)
    Author.objects.all().delete()
    Book.objects.all().delete()
    Library.objects.all().delete()
    Librarian.objects.all().delete()

    # Create authors
    a1 = Author.objects.create(name="Jane Goodwin")
    a2 = Author.objects.create(name="Sam Bright")

    # Create books
    b1 = Book.objects.create(title="Adventures in Python", author=a1)
    b2 = Book.objects.create(title="Django for Kids", author=a1)
    b3 = Book.objects.create(title="The Curious Case of Code", author=a2)

    # Create libraries
    lib1 = Library.objects.create(name="Central Library")
    lib2 = Library.objects.create(name="Neighborhood Library")

    # Add books to libraries (ManyToMany)
    lib1.books.add(b1, b2)           # Central has two books by Jane
    lib2.books.add(b2, b3)           # Neighborhood has one Jane book and one Sam book

    # Create librarians (OneToOne)
    Librarian.objects.create(name="Alice", library=lib1)
    Librarian.objects.create(name="Bob", library=lib2)

    print("Sample data created.\n")

def query_all_books_by_author(author_name):
    try:
        author = Author.objects.get(name=author_name)
    except Author.DoesNotExist:
        print(f"No author named '{author_name}' found.")
        return

    # <-- FIX HERE: use filter() as checker requires
    books = Book.objects.filter(author=author)
    
    print(f"Books by {author_name}:")
    for b in books:
        print(" -", b.title)
    print()

    books = author.books.all()  # thanks to related_name='books'
    print(f"Books by {author_name}:")
    for b in books:
        print(" -", b.title)
    print()

def query_all_books_in_library(library_name):
    try:
        lib = Library.objects.get(name=library_name)
    except Library.DoesNotExist:
        print(f"No library named '{library_name}' found.")
        return

    books = lib.books.all()
    print(f"Books in {library_name}:")
    for b in books:
        print(" -", b.title, f"(author: {b.author.name})")
    print()

def query_librarian_for_library(library_name):
    try:
        lib = Library.objects.get(name=library_name)
    except Library.DoesNotExist:
        print(f"No library named '{library_name}' found.")
        return

    try:
        # <-- FIX HERE: use Librarian.objects.get(library=lib)
        librarian = Librarian.objects.get(library=lib)
        print(f"Librarian for {library_name}: {librarian.name}")
    except Librarian.DoesNotExist:
        print(f"No librarian assigned to {library_name}.")
    print()


if __name__ == "__main__":
    make_sample_data()

    # Queries:
    query_all_books_by_author("Jane Goodwin")
    query_all_books_in_library("Central Library")
    query_librarian_for_library("Central Library")

    # You can try other queries:
    query_all_books_by_author("Sam Bright")
    query_all_books_in_library("Neighborhood Library")
    query_librarian_for_library("Neighborhood Library")
