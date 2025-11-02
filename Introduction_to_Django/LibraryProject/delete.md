# Delete
Command:
>>> b = Book.objects.get(title="Nineteen Eighty-Four")
>>> b.delete()
# Expected output:
# (returns a tuple like (1, {'bookshelf.Book': 1}))
>>> Book.objects.all()
# Expected output:
# <QuerySet []>
