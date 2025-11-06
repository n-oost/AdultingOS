"""
URL configuration for the AdultingOS core app.

Why these routes exist
----------------------
This module wires the API viewsets to URL endpoints used by the frontend, mobile app,
and assistant. Using DRF's router creates consistent RESTful endpoints for common
resource operations (list, retrieve, create, update, delete) and allows attaching
custom actions (e.g., mark_complete).

Purpose
-------
Provide a single, discoverable entrypoint under `/api/` for core resources like
tasks, tags, user profiles, identity snapshots, and government application records.
Keeping routing centralized makes it easier to document and maintain client
integrations.

"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet, TagViewSet, UserProfileViewSet,
    FoundationalDocumentsSnapshotViewSet, SINApplicationViewSet,
    PassportApplicationViewSet, OntarioProvincialIdApplicationViewSet,
    OSAPApplicationViewSet,
    register, login_view, foundational_documents_schema_view
)

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

# Identity and application endpoints
router.register(r'identity', FoundationalDocumentsSnapshotViewSet, basename='identity')
router.register(r'sin-apps', SINApplicationViewSet, basename='sinapplication')
router.register(r'passport-apps', PassportApplicationViewSet, basename='passportapplication')
router.register(r'ontario-id-apps', OntarioProvincialIdApplicationViewSet, basename='ontarioidapplication')
router.register(r'osap-apps', OSAPApplicationViewSet, basename='osapapplication')

# Define URL patterns
# Combines auto-generated router URLs with custom authentication endpoints
urlpatterns = [
    # Include all router-generated URLs (tasks and tags endpoints)
    path('', include(router.urls)),
    
    # Authentication endpoints (not handled by ViewSets)
    path('auth/register/', register, name='register'),
    path('auth/login/', login_view, name='login'),
    
    # JSON Schema endpoint (public, read-only)
    path('schemas/foundational-documents/', foundational_documents_schema_view, name='foundational-documents-schema'),
]