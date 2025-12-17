# Social Media API

A RESTful Social Media API built with Django and Django REST Framework.

## Features

- User registration and authentication with token-based auth
- Custom user model with profile fields (bio, profile picture)
- Follow/unfollow functionality
- Profile management

## Setup Instructions

1. **Clone the repository and navigate to the project directory**

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt


 ## Posts and Comments API

### Posts Endpoints

- **GET /api/posts/**: List all posts (with pagination, filtering, and search)
- **POST /api/posts/**: Create a new post (requires authentication)
- **GET /api/posts/{id}/**: Retrieve a specific post
- **PUT /api/posts/{id}/**: Update a post (must be the author)
- **PATCH /api/posts/{id}/**: Partially update a post (must be the author)
- **DELETE /api/posts/{id}/**: Delete a post (must be the author)
- **GET /api/posts/{id}/comments/**: Get all comments for a specific post

### Comments Endpoints

- **GET /api/comments/**: List all comments (with pagination)
- **POST /api/comments/**: Create a new comment (requires authentication)
- **GET /api/comments/{id}/**: Retrieve a specific comment
- **PUT /api/comments/{id}/**: Update a comment (must be the author)
- **PATCH /api/comments/{id}/**: Partially update a comment (must be the author)
- **DELETE /api/comments/{id}/**: Delete a comment (must be the author)

### Filtering and Search

**Posts filtering parameters:**
- `title` (contains, case-insensitive): `?title=django`
- `content` (contains, case-insensitive): `?content=travel`
- `author` (exact username): `?author=alice`
- `author_id` (exact ID): `?author_id=1`
- `search` (searches title, content, and author username): `?search=django`
- `ordering` (created_at, updated_at, title): `?ordering=-created_at` (descending)

**Comments filtering parameters:**
- `post_id`: `?post_id=1`
- `author_id`: `?author_id=2`

### Pagination

Default pagination:
- Posts: 10 per page
- Comments: 20 per page

Adjust with `page_size` parameter: `?page_size=50`

### Request Examples

**Create a Post:**
```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token {your_token}" \
  -d '{
    "title": "My Awesome Post",
    "content": "This is the content of my post."
  }'  



  # Deployment Guide

## Prerequisites
- Python 3.11+
- PostgreSQL (for production)
- Git
- Virtual environment

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd social_media_api