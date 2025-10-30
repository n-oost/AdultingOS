"""
Views for the AdultingOS core app.

Why these views exist
---------------------
This module exposes REST API endpoints used by the web frontend, mobile app, and
assistant. ViewSets are implemented to provide consistent CRUD operations for
user-scoped resources (tasks, identity snapshots, and applications). Restricting
querysets to the authenticated user and centralizing actions (e.g., marking
tasks complete) keeps authorization logic simple and reduces duplication.

Purpose
-------
Offer stable, discoverable API endpoints powered by Django REST Framework. The
views translate HTTP requests to serializer and model operations, apply
permission checks, and surface helpful status messages. They are intentionally
thin—complex domain rules are enforced on models/serializers.

"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.db.models import Q
from .models import (
    Task, Tag, UserProfile,
    FoundationalDocumentsSnapshot, SINApplication, PassportApplication,
    OntarioProvincialIdApplication, OSAPApplication
)
from .serializers import (
    TaskSerializer,
    TagSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    FoundationalDocumentsSnapshotSerializer,
    SINApplicationSerializer,
    PassportApplicationSerializer,
    OntarioProvincialIdApplicationSerializer,
    OSAPApplicationSerializer,
)


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user tasks.
    
    Provides CRUD operations (Create, Read, Update, Delete) for tasks.
    Each user can only access their own tasks. Supports filtering and
    bulk operations for better user experience.
    
    Available endpoints:
    - GET /api/tasks/ - List all user's tasks
    - POST /api/tasks/ - Create a new task
    - GET /api/tasks/{id}/ - Get specific task details
    - PUT /api/tasks/{id}/ - Update a task
    - DELETE /api/tasks/{id}/ - Delete a task
    - POST /api/tasks/{id}/mark_complete/ - Mark task as complete
    """
    
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return only tasks belonging to the current user.
        
        This ensures users can only see and modify their own tasks,
        providing data isolation and security.
        """
        queryset = self.request.user.tasks.all()
        
        # Add filtering options via query parameters
        completed = self.request.query_params.get('completed')
        category = self.request.query_params.get('category')
        priority = self.request.query_params.get('priority')
        search = self.request.query_params.get('search')
        
        # Filter by completion status
        if completed is not None:
            queryset = queryset.filter(completed=completed.lower() == 'true')
        
        # Filter by category
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        # Filter by priority level
        if priority:
            try:
                priority_int = int(priority)
                if priority_int in [choice.value for choice in Task.Priority]:
                    queryset = queryset.filter(priority=priority_int)
            except (ValueError, TypeError):
                pass  # Invalid priority value, skip filtering
        
        # Search in title and description
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset

    def perform_create(self, serializer):
        """
        Set the task owner to the current user when creating a new task.
        
        This ensures that tasks are automatically associated with the user
        who created them, without requiring the user to specify themselves.
        """
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """
        Custom action to mark a task as complete.
        
        POST /api/tasks/{id}/mark_complete/
        """
        task = self.get_object()
        task.mark_completed()
        return Response({'status': 'task marked as complete'})

    @action(detail=True, methods=['post'])
    def mark_incomplete(self, request, pk=None):
        """
        Custom action to mark a task as incomplete.
        
        POST /api/tasks/{id}/mark_incomplete/
        """
        task = self.get_object()
        task.mark_incomplete()
        return Response({'status': 'task marked as incomplete'})


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing task tags.
    
    Provides CRUD operations for tags that can be applied to tasks.
    Tags help users organize and categorize their tasks.
    
    Available endpoints:
    - GET /api/tags/ - List all tags
    - POST /api/tags/ - Create a new tag
    - GET /api/tags/{id}/ - Get specific tag details
    - PUT /api/tags/{id}/ - Update a tag
    - DELETE /api/tags/{id}/ - Delete a tag
    """
    
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return all tags, optionally filtered by search query."""
        queryset = Tag.objects.all()
        
        # Add search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Allow unauthenticated access for registration
def register(request):
    """
    Register a new user account.
    
    POST /api/auth/register/
    
    Expected data:
    {
        "username": "string",
        "email": "email@example.com", 
        "password": "string (min 8 chars)",
        "password_confirm": "string (must match password)"
    }
    
    Returns:
    {
        "user": {
            "id": int,
            "username": "string",
            "email": "email"
        },
        "token": "authentication_token"
    }
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Create the new user account
        user = serializer.save()
        
        # Create an authentication token for immediate login
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user info and token for immediate authentication
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
    # Return validation errors if registration failed
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Allow unauthenticated access for login
def login_view(request):
    """
    Authenticate user and return access token.
    
    POST /api/auth/login/
    
    Expected data:
    {
        "username": "string",
        "password": "string"
    }
    
    Returns:
    {
        "user": {
            "id": int,
            "username": "string", 
            "email": "email"
        },
        "token": "authentication_token"
    }
    """
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        # Get the authenticated user from the serializer
        user = serializer.validated_data['user']
        
        # Get or create an authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user info and token for authentication
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'token': token.key
        })
    
    # Return validation errors if login failed
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user profile management.
    
    Provides CRUD operations for the current user's profile.
    Used for onboarding and personalized task generation.
    
    Available endpoints:
    - GET /api/profile/me/ - Get current user's profile
    - PATCH /api/profile/update_me/ - Update current user's profile
    """
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's profile."""
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Always return the current user's profile (or create if missing)."""
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's profile.
        
        GET /api/profile/me/
        """
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_me(self, request):
        """
        Update current user's profile.
        
        PATCH /api/profile/update_me/
        """
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class FoundationalDocumentsSnapshotViewSet(viewsets.ModelViewSet):
    """API endpoint for a user's identity snapshot.

    - GET /api/identity/ - list (admin)
    - GET /api/identity/me/ - current user's snapshot
    - POST /api/identity/ - create snapshot
    """

    serializer_class = FoundationalDocumentsSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = FoundationalDocumentsSnapshot.objects.all()

    def get_queryset(self):
        # Allow admins to list all; otherwise restrict to the user's snapshot
        if self.request.user.is_staff:
            return super().get_queryset()
        return FoundationalDocumentsSnapshot.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        snapshot, _ = FoundationalDocumentsSnapshot.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(snapshot)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BaseApplicationViewSet(viewsets.ModelViewSet):
    """Common behavior for application viewsets."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only applications belonging to the current user
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SINApplicationViewSet(BaseApplicationViewSet):
    queryset = SINApplication.objects.all()
    serializer_class = SINApplicationSerializer


class PassportApplicationViewSet(BaseApplicationViewSet):
    queryset = PassportApplication.objects.all()
    serializer_class = PassportApplicationSerializer


class OntarioProvincialIdApplicationViewSet(BaseApplicationViewSet):
    queryset = OntarioProvincialIdApplication.objects.all()
    serializer_class = OntarioProvincialIdApplicationSerializer


class OSAPApplicationViewSet(BaseApplicationViewSet):
    queryset = OSAPApplication.objects.all()
    serializer_class = OSAPApplicationSerializer