
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TagViewSet
from django.contrib import admin
from django.urls import path, include

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'tags', TagViewSet, basename='tag')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
  
    urlpatterns = [
        path('admin/', admin.site.urls),
        # Add the core app's API URLs
        path('api/', include('core.urls')),
        # Add DRF's built-in login/logout views for the browsable API
        path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    ]
]