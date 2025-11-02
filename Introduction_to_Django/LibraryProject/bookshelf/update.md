Command:
b = Book.objects.get(title="1984")
b.title = "Nineteen Eighty-Four"
b.save()
Books.objects.get(id=b.id).title
