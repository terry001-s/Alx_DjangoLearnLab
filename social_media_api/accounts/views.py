from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from .serializers import FollowActionSerializer, UserFollowSerializer, UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer

# Get the user model
User = get_user_model()

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Get the token that was created in the serializer
            token = Token.objects.get(user=user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'token': token.key,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Get or create token for the user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'token': token.key,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Delete the token associated with the current user
        request.user.auth_token.delete()
        logout(request)
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'user': serializer.data,
                'message': 'Profile updated successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            serializer = UserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
class FollowUserView(APIView):
    """View to follow another user"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = FollowActionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user_to_follow = get_object_or_404(User, id=serializer.validated_data['user_id'])
            
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
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnfollowUserView(APIView):
    """View to unfollow another user"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = FollowActionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user_to_unfollow = get_object_or_404(User, id=serializer.validated_data['user_id'])
            
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
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FollowingListView(APIView):
    """View to list users that the current user is following"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        following_users = request.user.following.all()
        serializer = UserFollowSerializer(
            following_users, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

class FollowersListView(APIView):
    """View to list users who are following the current user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        followers = request.user.followers.all()
        serializer = UserFollowSerializer(
            followers, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserFollowStatusView(APIView):
    """View to check follow status between users"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
            is_following = request.user.is_following(target_user)
            
            return Response({
                'user_id': user_id,
                'username': target_user.username,
                'is_following': is_following,
                'can_follow': request.user != target_user,
                'target_user_followers_count': target_user.followers_count,
                'target_user_following_count': target_user.following_count
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )        