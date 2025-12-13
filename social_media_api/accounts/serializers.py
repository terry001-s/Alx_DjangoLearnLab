from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

# Get the custom user model
User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    # Using serializers.CharField() for both password fields
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'password2', 'bio')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, data):
        # Validate that passwords match
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})
        
        # Check if username already exists
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
        
        return data
    
    def create(self, validated_data):
        # Remove password2 from validated data
        password = validated_data.pop('password')
        validated_data.pop('password2')
        
        # Use get_user_model().objects.create_user() to create the user
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            bio=validated_data.get('bio', '')
        )
        
        # Create token for the user
        Token.objects.create(user=user)
        
        return user

class UserLoginSerializer(serializers.Serializer):
    # Using serializers.CharField() for both fields
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, 
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError("User account is disabled.")
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'bio', 
                  'profile_picture', 'followers_count', 'following_count', 
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        """Add follow relationship info if requested by current user"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        if request and hasattr(request, 'user'):
            current_user = request.user
            data['is_following'] = current_user.is_following(instance)
            data['can_follow'] = current_user != instance
        
        return data

class UserFollowSerializer(serializers.ModelSerializer):
    """Serializer for user follow operations"""
    is_following = serializers.SerializerMethodField()
    can_follow = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 
                  'profile_picture', 'followers_count', 'following_count',
                  'is_following', 'can_follow']
        read_only_fields = ['id', 'username', 'first_name', 'last_name', 
                           'profile_picture', 'followers_count', 'following_count']
    
    def get_is_following(self, obj):
        """Check if current user is following this user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return request.user.is_following(obj)
        return False
    
    def get_can_follow(self, obj):
        """Check if current user can follow this user (not themselves)"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return request.user != obj
        return False

class FollowActionSerializer(serializers.Serializer):
    """Serializer for follow/unfollow actions"""
    user_id = serializers.IntegerField(required=True)
    
    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        
        # Check if trying to follow self
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if request.user.id == value:
                raise serializers.ValidationError("Cannot follow yourself.")
        
        return value    