# blog/urls.py - FINAL CORRECT VERSION
from django.urls import path
from . import views
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    CommentCreateView,
    CommentUpdateView,
    CommentDeleteView
)

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Blog Post URLs - Changed from 'blog/' to 'posts/'
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/new/', PostCreateView.as_view(), name='post_new'),
    path('posts/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    
    # Comment URLs - EXACTLY as specified in requirements
    # 1. Create comment: /posts/<int:post_id>/comments/new/
    path('posts/<int:post_pk>/comments/new/', 
         CommentCreateView.as_view(), 
         name='comment_create'),
    
    # 2. Update comment: /comment/<int:pk>/update/ (as per requirement check)
    path('comment/<int:pk>/update/', 
         CommentUpdateView.as_view(), 
         name='comment_update'),
    
    # 3. Delete comment (implied, though not explicitly mentioned)
    path('comment/<int:pk>/delete/', 
         CommentDeleteView.as_view(), 
         name='comment_delete'),
]