"""
Integration tests for the Django REST Framework `TaskViewSet`.

These tests verify the CRUD operations and custom actions (mark_complete, mark_incomplete)
for tasks, ensuring proper authentication (using token authentication), authorization,
and filtering capabilities.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Task, Tag

class TaskViewSetTests(APITestCase):
    def setUp(self):
        """Set up test users and initial data."""
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.other_user = User.objects.create_user(username='otheruser', password='testpassword')
        
        # Use token authentication for API tests
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create some tasks for the primary user
        self.task1 = Task.objects.create(user=self.user, title='Task 1', description='Description 1', priority=1)
        self.task2 = Task.objects.create(user=self.user, title='Task 2', completed=True, category='Work')
        
        # Create a task for another user to test permissions
        self.other_task = Task.objects.create(user=self.other_user, title='Other user task')

    def test_list_tasks_authenticated(self):
        """Ensure authenticated users can list their own tasks."""
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], self.task1.title)

    def test_list_tasks_unauthenticated(self):
        """Ensure unauthenticated users cannot list tasks."""
        self.client.credentials()  # Clear authentication
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_own_task(self):
        """Ensure users can retrieve their own tasks."""
        url = reverse('task-detail', kwargs={'pk': self.task1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.task1.title)

    def test_cannot_retrieve_other_users_task(self):
        """Ensure users cannot retrieve tasks belonging to others."""
        url = reverse('task-detail', kwargs={'pk': self.other_task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_task(self):
        """Ensure users can create a new task."""
        url = reverse('task-list')
        data = {'title': 'New Task', 'description': 'A new description'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 4)
        self.assertEqual(Task.objects.last().user, self.user)
        self.assertEqual(Task.objects.last().title, 'New Task')

    def test_update_task(self):
        """Ensure users can update their own tasks."""
        url = reverse('task-detail', kwargs={'pk': self.task1.pk})
        data = {'title': 'Updated Title', 'completed': True}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Updated Title')
        self.assertTrue(self.task1.completed)

    def test_delete_task(self):
        """Ensure users can delete their own tasks."""
        url = reverse('task-detail', kwargs={'pk': self.task1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 2)

    def test_mark_complete_action(self):
        """Test the custom action to mark a task as complete."""
        self.assertFalse(self.task1.completed)
        url = reverse('task-mark-complete', kwargs={'pk': self.task1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertTrue(self.task1.completed)

    def test_mark_incomplete_action(self):
        """Test the custom action to mark a task as incomplete."""
        self.assertTrue(self.task2.completed)
        url = reverse('task-mark-incomplete', kwargs={'pk': self.task2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task2.refresh_from_db()
        self.assertFalse(self.task2.completed)

    def test_filter_tasks_by_completed_status(self):
        """Test filtering tasks by their completion status."""
        url = reverse('task-list')
        # Filter for completed tasks
        response = self.client.get(url, {'completed': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.task2.title)
        
        # Filter for incomplete tasks
        response = self.client.get(url, {'completed': 'false'})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.task1.title)

    def test_filter_tasks_by_category(self):
        """Test filtering tasks by category."""
        url = reverse('task-list')
        response = self.client.get(url, {'category': 'Work'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.task2.title)

    def test_filter_tasks_by_priority(self):
        """Test filtering tasks by priority."""
        url = reverse('task-list')
        response = self.client.get(url, {'priority': '1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.task1.title)

    def test_search_tasks(self):
        """Test searching for tasks by title or description."""
        url = reverse('task-list')
        response = self.client.get(url, {'search': 'Description 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.task1.title)


class TagViewSetTests(APITestCase):
    def setUp(self):
        """Set up test user, token, and initial tags."""
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.tag1 = Tag.objects.create(name='work')
        self.tag2 = Tag.objects.create(name='personal')

    def test_list_tags_authenticated(self):
        """Ensure authenticated users can list tags."""
        url = reverse('tag-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertContains(response, self.tag1.name)

    def test_list_tags_unauthenticated(self):
        """Ensure unauthenticated users cannot list tags."""
        self.client.credentials()  # Clear authentication
        url = reverse('tag-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_tag(self):
        """Ensure authenticated users can create a new tag."""
        url = reverse('tag-list')
        data = {'name': 'urgent'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 3)
        self.assertEqual(Tag.objects.last().name, 'urgent')

    def test_create_duplicate_tag_fails(self):
        """Ensure creating a tag with a duplicate name fails."""
        url = reverse('tag-list')
        data = {'name': 'work'}  # 'work' already exists
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_tag(self):
        """Ensure authenticated users can delete a tag."""
        url = reverse('tag-detail', kwargs={'pk': self.tag1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tag.objects.count(), 1)
