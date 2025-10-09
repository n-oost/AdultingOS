from rest_framework import serializers
from .models import Task, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class TaskSerializer(serializers.ModelSerializer):
    # Display tag names instead of just IDs for readability
    tags = serializers.StringRelatedField(many=True, read_only=True)
    # Show username for the user field
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Task
        fields = [
            'id', 'user', 'title', 'description', 'category', 'due_date',
            'priority', 'completed', 'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']