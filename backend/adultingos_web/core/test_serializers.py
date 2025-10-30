"""
Unit tests for the Django REST Framework serializers in the `core` app.

These tests ensure that serializers for `Tag`, `Task`, `UserRegistration`,
`UserLogin`, and `UserProfile` correctly handle data validation, creation,
and updating, including complex nested fields and custom logic.
"""
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User
from .serializers import TaskSerializer, TagSerializer, UserRegistrationSerializer, UserLoginSerializer
from .models import Task, Tag
from rest_framework.exceptions import ValidationError

class TagSerializerTest(TestCase):
    def test_tag_serializer_valid(self):
        data = {'name': 'work'}
        serializer = TagSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        tag = serializer.save()
        self.assertEqual(tag.name, 'work')

    def test_tag_serializer_invalid_empty_name(self):
        data = {'name': ' '}
        serializer = TagSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_tag_serializer_strips_whitespace(self):
        data = {'name': '  personal  '}
        serializer = TagSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        tag = serializer.save()
        self.assertEqual(tag.name, 'personal')

    def test_tag_serializer_lowercase(self):
        data = {'name': 'Urgent'}
        serializer = TagSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        tag = serializer.save()
        self.assertEqual(tag.name, 'urgent')

    def test_tag_update(self):
        tag = Tag.objects.create(name='old_name')
        data = {'name': 'new_name'}
        serializer = TagSerializer(instance=tag, data=data)
        self.assertTrue(serializer.is_valid())
        updated_tag = serializer.save()
        self.assertEqual(updated_tag.name, 'new_name')

class TaskSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.tag1 = Tag.objects.create(name='work')
        self.tag2 = Tag.objects.create(name='personal')

    def test_task_serializer_valid(self):
        data = {
            'title': 'Test Task',
            'description': 'A description',
            'category': 'general',
            'priority': 2,
            'completed': False,
        }
        serializer = TaskSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        task = serializer.save(user=self.user)
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.user, self.user)

    def test_task_serializer_invalid_no_title(self):
        data = {
            'description': 'A description',
            'priority': 2,
        }
        serializer = TaskSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_task_serializer_read(self):
        task = Task.objects.create(
            user=self.user,
            title='Read Task',
            priority=3
        )
        task.tags.add(self.tag1)
        serializer = TaskSerializer(instance=task)
        data = serializer.data
        self.assertEqual(data['title'], 'Read Task')
        self.assertEqual(data['priority_display'], 'High')
        self.assertIn('work', data['tags'])
        self.assertEqual(data['user'], 'testuser')

    def test_task_update(self):
        task = Task.objects.create(user=self.user, title='Old Title', priority=1)
        data = {'title': 'New Title', 'priority': 4}
        serializer = TaskSerializer(instance=task, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_task = serializer.save()
        self.assertEqual(updated_task.title, 'New Title')
        self.assertEqual(updated_task.priority, 4)

    def test_task_create_with_tags(self):
        data = {
            'title': 'Task with Tags',
            'priority': 2,
            'tags': ['work', 'urgent']
        }
        serializer = TaskSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        task = serializer.save(user=self.user)
        self.assertEqual(task.tags.count(), 2)
        self.assertTrue(task.tags.filter(name='work').exists())

    def test_is_overdue(self):
        overdue_task = Task.objects.create(
            user=self.user, 
            title='Overdue Task', 
            due_date=timezone.now() - timezone.timedelta(days=1)
        )
        serializer = TaskSerializer(instance=overdue_task)
        self.assertTrue(serializer.data['is_overdue'])

        not_overdue_task = Task.objects.create(
            user=self.user, 
            title='Not Overdue Task', 
            due_date=timezone.now() + timezone.timedelta(days=1)
        )
        serializer = TaskSerializer(instance=not_overdue_task)
        self.assertFalse(serializer.data['is_overdue'])

    def test_task_serializer_invalid_empty_title(self):
        data = {
            'title': '  ',
            'description': 'A description',
            'priority': 2,
        }
        serializer = TaskSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_task_update_with_tags(self):
        task = Task.objects.create(user=self.user, title='Task with tags')
        task.tags.add(self.tag1)
        data = {
            'tags': ['personal', 'urgent']
        }
        serializer = TaskSerializer(instance=task, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_task = serializer.save()
        self.assertEqual(updated_task.tags.count(), 2)
        self.assertTrue(updated_task.tags.filter(name='personal').exists())
        self.assertTrue(updated_task.tags.filter(name='urgent').exists())
        self.assertFalse(updated_task.tags.filter(name='work').exists())

class UserRegistrationSerializerTest(TestCase):
    def test_registration_valid(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepassword123',
            'password_confirm': 'securepassword123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('securepassword123'))

    def test_registration_password_mismatch(self):
        data = {
            'username': 'user2',
            'email': 'user2@example.com',
            'password': 'password1',
            'password_confirm': 'password2'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertIn('Passwords don\'t match.', str(serializer.errors))

    def test_registration_existing_username(self):
        User.objects.create_user(username='existinguser', password='password')
        data = {
            'username': 'existinguser',
            'email': 'test@example.com',
            'password': 'securepassword123',
            'password_confirm': 'securepassword123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_registration_missing_email(self):
        data = {
            'username': 'user_no_email',
            'password': 'securepassword123',
            'password_confirm': 'securepassword123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

class UserLoginSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testlogin', password='loginpass')

    def test_login_valid(self):
        data = {
            'username': 'testlogin',
            'password': 'loginpass'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['user'], self.user)

    def test_login_invalid_password(self):
        data = {
            'username': 'testlogin',
            'password': 'wrongpassword'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertIn('Invalid username or password.', str(serializer.errors))

    def test_login_invalid_username(self):
        data = {
            'username': 'nonexistentuser',
            'password': 'loginpass'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertIn('Invalid username or password.', str(serializer.errors))

    def test_login_missing_credentials(self):
        data = {'username': 'testlogin'}
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertIn('Must include both username and password.', str(serializer.errors))


class UserProfileSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='profileuser', password='password')

    def test_profile_serializer_create_and_update(self):
        # Test creating a profile through the serializer
        profile_data = {
            'age': 30,
            'occupation': 'Engineer',
            'is_student': False,
            'filing_status': 'single',
            'has_dependents': False,
        }
        serializer = UserProfileSerializer(data=profile_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        # Note: UserProfile is created via a signal or get_or_create, so we update it
        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        updated_profile = serializer.update(profile, serializer.validated_data)

        self.assertEqual(updated_profile.age, 30)
        self.assertEqual(updated_profile.occupation, 'Engineer')
        self.assertGreater(updated_profile.profile_completeness, 0)

        # Test updating the profile
        update_data = {
            'occupation': 'Senior Engineer',
            'has_401k': True,
        }
        update_serializer = UserProfileSerializer(instance=updated_profile, data=update_data, partial=True)
        self.assertTrue(update_serializer.is_valid(), update_serializer.errors)
        final_profile = update_serializer.save()

        self.assertEqual(final_profile.occupation, 'Senior Engineer')
        self.assertTrue(final_profile.has_401k)
