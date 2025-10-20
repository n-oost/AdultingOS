"""
URL configuration for the AdultingOS core app.

This module defines the API endpoint routing for tasks, tags, and authentication.
Uses Django REST Framework's DefaultRouter for automatic URL pattern generation.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TagViewSet, UserProfileViewSet, register, login_view

# Create a DRF router for automatic URL generation
# This creates standard CRUD endpoints for ViewSets
router = DefaultRouter()

# Register ViewSets with the router
# This automatically creates the following endpoints:
# - /api/tasks/ (GET: list, POST: create)  
# - /api/tasks/{id}/ (GET: retrieve, PUT: update, DELETE: delete)
# - /api/tasks/{id}/mark_complete/ (POST: custom action)
# - /api/tasks/{id}/mark_incomplete/ (POST: custom action)
router.register(r'tasks', TaskViewSet, basename='task')

# Tag endpoints:
# - /api/tags/ (GET: list, POST: create)
# - /api/tags/{id}/ (GET: retrieve, PUT: update, DELETE: delete) 
router.register(r'tags', TagViewSet, basename='tag')

# UserProfile endpoints:
# - /api/profile/me/ (GET: get current user's profile)
# - /api/profile/update_me/ (PATCH: update current user's profile)
router.register(r'profile', UserProfileViewSet, basename='profile')

# Define URL patterns
# Combines auto-generated router URLs with custom authentication endpoints
urlpatterns = [
    # Include all router-generated URLs (tasks and tags endpoints)
    path('', include(router.urls)),
    
    # Authentication endpoints (not handled by ViewSets)
    path('auth/register/', register, name='register'),
    path('auth/login/', login_view, name='login'),
]