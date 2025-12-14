from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, FeedView, LikeView, PostLikesView

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('feed/', FeedView.as_view(), name='feed'),
    
    # Like endpoints
    path('posts/<int:pk>/like/', LikeView.as_view(), name='post-like'),
    path('posts/<int:pk>/unlike/', LikeView.as_view(), name='post-unlike'),
    path('posts/<int:pk>/likes/', PostLikesView.as_view(), name='post-likes'),
]