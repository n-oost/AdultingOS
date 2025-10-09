from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.
class Tag(models.Model):
    """Model representing a tag for categorizing tasks."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    """Model representing a task to be completed."""
    class Priority(models.IntegerChoices):
        LOW = 1
        MEDIUM = 2
        HIGH = 3
        URGENT = 4
        CRITICAL = 5
        
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.LOW)
    completed = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def mark_completed(self):
        self.completed = True
        self.save()
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-priority', 'due_date']

#class UserProfile(models.Model):