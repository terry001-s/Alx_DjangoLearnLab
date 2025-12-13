from django.urls import path
from .views import (
    UserRegistrationView, 
    UserLoginView, 
    UserLogoutView, 
    UserProfileView,
    UserDetailView,
    FollowUserView,
    UnfollowUserView,
    FollowingListView,
    FollowersListView,
    UserFollowStatusView,
    UserListView  # Add this import
)

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # Profile endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('users/<str:username>/', UserDetailView.as_view(), name='user-detail'),
    path('users/', UserListView.as_view(), name='user-list'),  # Add this line
    
    # Follow management endpoints
    path('follow/', FollowUserView.as_view(), name='follow-user'),
    path('unfollow/', UnfollowUserView.as_view(), name='unfollow-user'),
    path('following/', FollowingListView.as_view(), name='following-list'),
    path('followers/', FollowersListView.as_view(), name='followers-list'),
    path('follow-status/<int:user_id>/', UserFollowStatusView.as_view(), name='follow-status'),
]