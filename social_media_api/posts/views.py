from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, PostCreateSerializer
from .permissions import IsOwnerOrReadOnly
import django_filters
from .models import Like
from notifications.utils import create_like_notification, create_comment_notification
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType

# Custom pagination class
class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CommentPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class FeedPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 50

# Custom filter for posts
class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.CharFilter(field_name='author__username', lookup_expr='exact')
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'author']

class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing posts.
    """
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = PostPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['title', 'content', 'author__username']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by author if author_id parameter is provided
        author_id = self.request.query_params.get('author_id')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        return queryset.select_related('author').prefetch_related('comments')
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get all comments for a specific post"""
        post = self.get_object()
        comments = post.comments.all()
        
        # Paginate comments
        paginator = CommentPagination()
        page = paginator.paginate_queryset(comments, request)
        
        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Get posts from users that the current user follows"""
        # Get users that the current user is following
        following_users = request.user.following.all()
        
        # Get posts from followed users, ordered by creation date (most recent first)
        posts = Post.objects.filter(author__in=following_users).order_by('-created_at')
        
        # Apply pagination
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing comments.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = CommentPagination
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

         # Create notification for comment
        create_comment_notification(comment)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by post if post_id parameter is provided
        post_id = self.request.query_params.get('post_id')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        # Filter by author if author_id parameter is provided
        author_id = self.request.query_params.get('author_id')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        return queryset.select_related('author', 'post')
    
    def create(self, request, *args, **kwargs):
        # Ensure post_id is provided in the request data
        post_id = request.data.get('post')
        if not post_id:
            return Response(
                {'error': 'post field is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the post exists
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return super().create(request, *args, **kwargs)

class FeedView(generics.GenericAPIView):
    """
    View to get posts from users that the current user follows
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = FeedPagination
    
    def get(self, request):
        # Get users that the current user is following
        following_users = request.user.following.all()
        
        # Get posts from followed users, ordered by creation date (most recent first)
        posts = Post.objects.filter(author__in=following_users).order_by('-created_at')
        
        # Apply pagination
        paginator = FeedPagination()
        page = paginator.paginate_queryset(posts, request)
        
        if page is not None:
            serializer = PostSerializer(
                page, 
                many=True,
                context={'request': request}
            )
            return paginator.get_paginated_response(serializer.data)
        
        serializer = PostSerializer(
            posts, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    

class LikeView(generics.GenericAPIView):
    """View to like or unlike a post"""
    permission_classes = [permissions.IsAuthenticated]
    
def post(self, request, pk):
    """Like or unlike a post"""
    # Use get_object_or_404 exactly as specified
    post = get_object_or_404(Post, pk=pk)
    
    # Use Like.objects.get_or_create exactly as specified
    like, created = Like.objects.get_or_create(
        user=request.user, 
        post=post
    )
    
    if created:
        # ... rest of your code for creating notification ...
        return Response({
            'message': 'Post liked successfully',
            'liked': True,
            'likes_count': post.likes.count()
        }, status=status.HTTP_200_OK)
    else:
        # Unlike if already exists
        like.delete()
        return Response({
            'message': 'Post unliked successfully',
            'liked': False,
            'likes_count': post.likes.count()
        }, status=status.HTTP_200_OK)

class PostLikesView(generics.GenericAPIView):
    """View to get users who liked a post"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        """Get list of users who liked the post"""
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
        likes = post.likes.select_related('user').all()
        
        # Paginate results
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(likes, request)
        
        if page is not None:
            from .serializers import LikeSerializer
            serializer = LikeSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        from .serializers import LikeSerializer
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)    