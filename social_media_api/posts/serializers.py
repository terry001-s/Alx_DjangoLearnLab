from rest_framework import serializers
from .models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details in posts and comments"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='author', 
        write_only=True
    )
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_id', 'content', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']
    
    def create(self, validated_data):
        # Set the author to the current user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        
        # Ensure the user is only commenting on their own post
        # or remove this restriction if you want open commenting
        return super().create(validated_data)

class PostSerializer(serializers.ModelSerializer):
    """Serializer for posts"""
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='author', 
        write_only=True
    )
    comments_count = serializers.IntegerField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'author_id', 'title', 'content', 
                  'comments_count', 'comments', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'author', 'comments_count']
    
    def create(self, validated_data):
        # Set the author to the current user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        
        return super().create(validated_data)

class PostCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating posts"""
    class Meta:
        model = Post
        fields = ['title', 'content']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)