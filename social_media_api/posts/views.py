from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, PostCreateSerializer
from .permissions import IsOwnerOrReadOnly
import django_filters

# Custom pagination class
class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CommentPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

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
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
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

class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing comments.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = CommentPagination
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
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