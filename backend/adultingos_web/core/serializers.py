"""
Serializers for the AdultingOS core app.

Serializers handle converting between Django model instances and JSON data
for the API. They define what data is included in API responses and how
incoming data should be validated and processed.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Task, Tag, UserProfile


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag model.
    
    Handles converting Tag instances to/from JSON for API responses.
    Tags are simple objects with just an ID and name.
    """
    
    class Meta:
        model = Tag
        fields = ['id', 'name']
        
    def validate_name(self, value):
        """Ensure tag names are not empty and are reasonably formatted."""
        if not value.strip():
            raise serializers.ValidationError("Tag name cannot be empty.")
        return value.strip().lower()  # Normalize to lowercase


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model.
    
    Handles converting Task instances to/from JSON for API responses.
    Includes custom fields for better user experience:
    - Shows tag names instead of just IDs
    - Shows username instead of user ID
    - Includes computed fields like priority display name
    """
    
    # Display tag names (e.g., ["work", "urgent"]) instead of IDs for readability
    tags = serializers.StringRelatedField(many=True, read_only=True)
    
    # Show the username instead of user ID for better readability
    user = serializers.ReadOnlyField(source='user.username')
    
    # Show human-readable priority (e.g., "High" instead of 3)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    # Add a computed field to show if task is overdue
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'user', 'title', 'description', 'category', 'due_date',
            'priority', 'priority_display', 'completed', 'tags', 'is_overdue',
            'created_at', 'updated_at'
        ]
        # These fields are automatically set by the system and shouldn't be modified by users
        read_only_fields = ['user', 'created_at', 'updated_at', 'priority_display', 'is_overdue']
    
    def get_is_overdue(self, obj):
        """Calculate if this task is overdue."""
        return obj.is_overdue()
    
    def validate_title(self, value):
        """Ensure task title is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Task title cannot be empty.")
        return value.strip()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles creating new user accounts with validation for:
    - Password confirmation matching
    - Minimum password length
    - Unique username/email
    """
    
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Must match the password field"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True},  # Make email required
        }

    def validate(self, attrs):
        """Validate that password and password_confirm match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        """Create a new user account."""
        # Remove password_confirm since it's not needed for user creation
        validated_data.pop('password_confirm')
        # Create user with encrypted password
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Validates username/password credentials and returns the authenticated user.
    """
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate user credentials and return authenticated user."""
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Attempt to authenticate with provided credentials
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid username or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            # Add the authenticated user to validated data
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include both username and password.')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    
    Handles converting UserProfile instances to/from JSON for API responses.
    Used for onboarding flow and personalized task generation.
    """
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'age', 'occupation', 'is_student',
            'filing_status', 'has_dependents', 'dependent_count',
            'typical_tax_filing_month', 'has_hsa', 'has_401k',
            'is_homeowner', 'has_student_loans', 'has_health_insurance',
            'insurance_renewal_month', 'recent_life_events',
            'preferred_reminder_frequency', 'onboarding_completed',
            'profile_completeness', 'last_profile_update',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'profile_completeness', 'created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        """Update profile and recalculate completeness."""
        instance = super().update(instance, validated_data)
        instance.calculate_completeness()
        instance.save()
        return instance