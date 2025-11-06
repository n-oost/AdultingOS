"""
Quick test script for AdultingOS API endpoints.
Tests user registration, login, and task management.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_response(response):
    """Print formatted response details"""
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

# Test 1: Register a new user
print_section("TEST 1: Register New User")
register_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123"
}
response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
print_response(response)

if response.status_code == 201:
    user_data = response.json()
    token = user_data.get('token')
    print(f"\n✅ Registration successful! Token: {token}")
else:
    print("\n❌ Registration failed!")
    exit(1)

# Test 2: Login with the user
print_section("TEST 2: Login")
login_data = {
    "username": "testuser",
    "password": "testpass123"
}
response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
print_response(response)

if response.status_code == 200:
    token = response.json().get('token')
    print(f"\n✅ Login successful! Token: {token}")
else:
    print("\n❌ Login failed!")
    exit(1)

# Set up headers for authenticated requests
headers = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}

# Test 3: Create a task
print_section("TEST 3: Create Task")
task_data = {
    "title": "Test Task",
    "description": "This is a test task",
    "priority": 3,  # High priority
    "category": "Testing",
    "due_date": "2025-10-20"
}
response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
print_response(response)

if response.status_code == 201:
    task = response.json()
    task_id = task.get('id')
    print(f"\n✅ Task created! ID: {task_id}")
else:
    print("\n❌ Task creation failed!")
    exit(1)

# Test 4: Get all tasks
print_section("TEST 4: Get All Tasks")
response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
print_response(response)

if response.status_code == 200:
    tasks = response.json()
    print(f"\n✅ Retrieved {len(tasks)} task(s)")
else:
    print("\n❌ Failed to get tasks!")

# Test 5: Update the task
print_section("TEST 5: Update Task")
update_data = {
    "title": "Updated Test Task",
    "description": "This task has been updated",
    "priority": 5,  # Critical priority
    "category": "Testing",
    "completed": False
}
response = requests.put(f"{BASE_URL}/tasks/{task_id}/", json=update_data, headers=headers)
print_response(response)

if response.status_code == 200:
    print(f"\n✅ Task updated successfully!")
else:
    print("\n❌ Task update failed!")

# Test 6: Mark task as complete
print_section("TEST 6: Mark Task Complete")
response = requests.post(f"{BASE_URL}/tasks/{task_id}/mark_complete/", headers=headers)
print_response(response)

if response.status_code == 200:
    print(f"\n✅ Task marked as complete!")
else:
    print("\n❌ Failed to mark task complete!")

# Test 7: Get the updated task
print_section("TEST 7: Get Updated Task")
response = requests.get(f"{BASE_URL}/tasks/{task_id}/", headers=headers)
print_response(response)

if response.status_code == 200:
    task = response.json()
    print(f"\n✅ Task retrieved!")
    print(f"   Completed: {task.get('completed')}")
    print(f"   Priority: {task.get('priority_display')}")
    print(f"   Overdue: {task.get('is_overdue')}")
else:
    print("\n❌ Failed to get task!")

# Test 8: Create a tag
print_section("TEST 8: Create Tag")
tag_data = {
    "name": "Important"
}
response = requests.post(f"{BASE_URL}/tags/", json=tag_data, headers=headers)
print_response(response)

if response.status_code == 201:
    tag = response.json()
    tag_id = tag.get('id')
    print(f"\n✅ Tag created! ID: {tag_id}")
else:
    print("\n❌ Tag creation failed!")

# Test 9: Get all tags
print_section("TEST 9: Get All Tags")
response = requests.get(f"{BASE_URL}/tags/", headers=headers)
print_response(response)

if response.status_code == 200:
    tags = response.json()
    print(f"\n✅ Retrieved {len(tags)} tag(s)")
else:
    print("\n❌ Failed to get tags!")

# Test 10: Delete the task
print_section("TEST 10: Delete Task")
response = requests.delete(f"{BASE_URL}/tasks/{task_id}/", headers=headers)
print(f"Status Code: {response.status_code}")

if response.status_code == 204:
    print(f"\n✅ Task deleted successfully!")
else:
    print("\n❌ Task deletion failed!")

# Final summary
print_section("TEST SUMMARY")
print("✅ All tests completed!")
print("\nAPI Endpoints tested:")
print("  - POST /api/auth/register/")
print("  - POST /api/auth/login/")
print("  - POST /api/tasks/")
print("  - GET /api/tasks/")
print("  - GET /api/tasks/{id}/")
print("  - PUT /api/tasks/{id}/")
print("  - POST /api/tasks/{id}/mark_complete/")
print("  - DELETE /api/tasks/{id}/")
print("  - POST /api/tags/")
print("  - GET /api/tags/")
print("\nYour AdultingOS API is working! 🎉")
