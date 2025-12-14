from rest_framework import status, generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout, authenticate
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, 
    UserProfileSerializer, UserFollowSerializer, FollowActionSerializer
)
from .models import CustomUser
from notifications.utils import create_follow_notification

User = get_user_model()

class UserRegistrationView(generics.GenericAPIView):
    """View for user registration"""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Get the token that was created in the serializer
            token = Token.objects.get(user=user)
            return Response({
                'user': UserProfileSerializer(user, context={'request': request}).data,
                'token': token.key,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(generics.GenericAPIView):
    """View for user login"""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Get or create token for the user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserProfileSerializer(user, context={'request': request}).data,
                'token': token.key,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(generics.GenericAPIView):
    """View for user logout"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Delete the token associated with the current user
        request.user.auth_token.delete()
        logout(request)
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.GenericAPIView):
    """View for user profile management"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        """Update current user's profile"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'user': serializer.data,
                'message': 'Profile updated successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(generics.GenericAPIView):
    """View to get details of a specific user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, username):
        try:
            user = CustomUser.objects.all().get(username=username)
            serializer = UserProfileSerializer(user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class FollowUserView(generics.GenericAPIView):
    """View to follow another user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id=None):
        # Get user_id from URL parameter if provided, otherwise from request body
        if user_id is None:
            # Try to get user_id from request body (for backward compatibility)
            serializer = FollowActionSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                user_id = serializer.validated_data['user_id']
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_to_follow = CustomUser.objects.all().get(id=user_id)
            
            # Check if trying to follow self
            if request.user.id == user_id:
                return Response({
                    'error': 'Cannot follow yourself.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if request.user.follow(user_to_follow):
                return Response({
                    'message': f'You are now following {user_to_follow.username}',
                    'followers_count': user_to_follow.followers_count,
                    'following_count': request.user.following_count
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': f'You are already following {user_to_follow.username}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

class UnfollowUserView(generics.GenericAPIView):
    """View to unfollow another user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id=None):
        # Get user_id from URL parameter if provided, otherwise from request body
        if user_id is None:
            # Try to get user_id from request body (for backward compatibility)
            serializer = FollowActionSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                user_id = serializer.validated_data['user_id']
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_to_unfollow = CustomUser.objects.all().get(id=user_id)
            
            if request.user.unfollow(user_to_unfollow):
                return Response({
                    'message': f'You have unfollowed {user_to_unfollow.username}',
                    'followers_count': user_to_unfollow.followers_count,
                    'following_count': request.user.following_count
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': f'You are not following {user_to_unfollow.username}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

class FollowingListView(generics.GenericAPIView):
    """View to list users that the current user is following"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        following_users = request.user.following.all()
        serializer = UserFollowSerializer(
            following_users, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

class FollowersListView(generics.GenericAPIView):
    """View to list users who are following the current user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        followers = request.user.followers.all()
        serializer = UserFollowSerializer(
            followers, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserFollowStatusView(generics.GenericAPIView):
    """View to check follow status between users"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            # Using CustomUser.objects.all() as required
            target_user = CustomUser.objects.all().get(id=user_id)
            is_following = request.user.is_following(target_user)
            
            return Response({
                'user_id': user_id,
                'username': target_user.username,
                'is_following': is_following,
                'can_follow': request.user != target_user,
                'target_user_followers_count': target_user.followers_count,
                'target_user_following_count': target_user.following_count
            }, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class UserListView(generics.GenericAPIView):
    """View to list all users (for demonstration purposes)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Using CustomUser.objects.all() to get all users
        users = CustomUser.objects.all()
        serializer = UserFollowSerializer(
            users, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    

