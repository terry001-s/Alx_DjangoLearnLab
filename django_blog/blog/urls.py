# blog/urls.py
from django.urls import path
from . import views
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView
)

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Blog URLs
    path('blog/', PostListView.as_view(), name='post_list'),
    path('blog/post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('blog/post/new/', PostCreateView.as_view(), name='post_new'),
    path('blog/post/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('blog/post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
]