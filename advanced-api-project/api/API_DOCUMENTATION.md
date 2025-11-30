# API View Documentation

## Book Views

### 1. BookListView
- **URL**: `/api/books/`
- **Method**: GET
- **Permissions**: AllowAny
- **Features**: 
  - List all books
  - Search by title and author name
  - Filter by publication year and author
  - Ordering by various fields
  - Pagination (10 items per page)

### 2. BookDetailView
- **URL**: `/api/books/<int:pk>/`
- **Method**: GET
- **Permissions**: AllowAny
- **Features**: Retrieve specific book by ID

### 3. BookCreateView
- **URL**: `/api/books/create/`
- **Method**: POST
- **Permissions**: IsAuthenticated
- **Features**: Create new book with validation

### 4. BookUpdateView
- **URL**: `/api/books/<int:pk>/update/`
- **Method**: PUT, PATCH
- **Permissions**: IsAuthenticated
- **Features**: Update existing book

### 5. BookDeleteView
- **URL**: `/api/books/<int:pk>/delete/`
- **Method**: DELETE
- **Permissions**: IsAuthenticated
- **Features**: Delete book

## Custom Features

- **Validation**: Publication year cannot be in the future
- **Filtering**: By publication year and author
- **Search**: By title and author name
- **Ordering**: By title, publication year, author name
- **Pagination**: 10 items per page