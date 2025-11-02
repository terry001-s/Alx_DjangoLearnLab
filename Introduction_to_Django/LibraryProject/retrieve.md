Command:
from bookshelf.models import Book
Book.object.all()
b = Book.objects.get(title="1984")
b.title, b.author, b.publication_year
