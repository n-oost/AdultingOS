from django.db import models
from django.conf import settings
from django.utils import timezone

class Tag(models.Model):
    """
    Model representing a tag for categorizing and organizing tasks.
    
    Tags allow users to group related tasks together (e.g., "work", "personal", "urgent").
    Each tag has a unique name and can be applied to multiple tasks.
    """
    # Tag name - must be unique across all tags
    name = models.CharField(max_length=50, unique=True, help_text="Unique name for this tag")

    def __str__(self):
        """Return the tag name when the object is displayed."""
        return self.name

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']  # Sort tags alphabetically


class Task(models.Model):
    """
    Model representing a task/to-do item in the AdultingOS system.
    
    Tasks are the core data model for the application. Each task belongs to a user
    and can have priorities, due dates, categories, and tags for organization.
    """
    
    class Priority(models.IntegerChoices):
        """Priority levels for tasks, from lowest to highest importance."""
        LOW = 1, "Low"
        MEDIUM = 2, "Medium" 
        HIGH = 3, "High"
        URGENT = 4, "Urgent"
        CRITICAL = 5, "Critical"
    
    # Core task fields
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        help_text="The user who owns this task"
    )
    title = models.CharField(
        max_length=200, 
        help_text="Short description of what needs to be done"
    )
    description = models.TextField(
        blank=True, 
        help_text="Optional detailed description of the task"
    )
    
    # Organization fields
    category = models.CharField(
        max_length=100, 
        default="general",
        help_text="Category to group related tasks (e.g., 'finance', 'health')"
    )
    tags = models.ManyToManyField(
        Tag, 
        blank=True, 
        related_name='tasks',
        help_text="Tags for flexible task organization"
    )
    
    # Status and priority
    priority = models.IntegerField(
        choices=Priority.choices, 
        default=Priority.MEDIUM,
        help_text="Task priority level"
    )
    completed = models.BooleanField(
        default=False, 
        help_text="Whether this task has been completed"
    )
    
    # Timing fields
    due_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When this task is due (optional)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this task was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this task was last modified"
    )
    
    def mark_completed(self):
        """Mark this task as completed and save to database."""
        self.completed = True
        self.save()
    
    def mark_incomplete(self):
        """Mark this task as incomplete and save to database."""
        self.completed = False
        self.save()
    
    def is_overdue(self):
        """Check if this task is past its due date."""
        if not self.due_date:
            return False
        return timezone.now() > self.due_date and not self.completed
    
    def __str__(self):
        """Return the task title when the object is displayed."""
        return f"{self.title} ({self.get_priority_display()})"

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        # Order by priority (highest first), then due date (earliest first)
        ordering = ['-priority', 'due_date']

#class UserProfile(models.Model):