# Update
Command:
>>> b = Book.objects.get(title="1984")
>>> b.title = "Nineteen Eighty-Four"
>>> b.save()
# Expected output:
# (No output; changes are saved)
>>> Book.objects.get(id=b.id).title
# Expected output:
# 'Nineteen Eighty-Four'
