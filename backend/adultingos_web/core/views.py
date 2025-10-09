from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import Task, Tag
from .serializers import TaskSerializer, TagSerializer

class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view or edit their tasks.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the tasks
        for the currently authenticated user.
        """
        return self.request.user.tasks.all()

    def perform_create(self, serializer):
        """
        Assign the current user to the task when it's created.
        """
        serializer.save(user=self.request.user)

class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tags to be viewed or edited.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]