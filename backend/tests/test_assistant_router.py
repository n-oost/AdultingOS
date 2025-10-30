"""
Unit tests for the FastAPI assistant's chat router.

These tests specifically verify the functionality of slash-commands (e.g., `/task list`,
`/task add`, `/task done`) by mocking HTTP requests to the Django API. This ensures
the assistant correctly parses commands, forms API requests, and handles responses
without needing a live Django server.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from main import app  # Assuming your FastAPI app instance is in main.py

client = TestClient(app)


@pytest.fixture
def mock_requests(mocker):
    """Fixture to mock the requests library."""
    return mocker.patch("src.assistant.router.requests")


def test_task_list_success(mock_requests):
    """Test /task list successfully retrieves and formats tasks."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "id": 1,
            "title": "Pay rent",
            "completed": False,
            "due_date": "2024-11-01T00:00:00Z",
            "priority": 3,
        },
        {
            "id": 2,
            "title": "Buy groceries",
            "completed": True,
            "due_date": None,
            "priority": 2,
        },
    ]
    mock_requests.get.return_value = mock_response

    response = client.post("/assistant/chat", json={"message": "/task list"})
    assert response.status_code == 200
    reply = response.json()["reply"]
    assert "• Pay rent [1] (due 2024-11-01) [prio 3]" in reply
    assert "✔ Buy groceries [2]  [prio 2]" in reply


def test_task_list_no_tasks(mock_requests):
    """Test /task list when no tasks are returned."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_requests.get.return_value = mock_response

    response = client.post("/assistant/chat", json={"message": "/task list"})
    assert response.status_code == 200
    assert response.json()["reply"] == "No tasks found."


def test_task_add_success(mock_requests):
    """Test /task add successfully creates a task via the API."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 101, "title": "New test task"}
    mock_requests.post.return_value = mock_response

    response = client.post(
        "/assistant/chat",
        json={"message": '/task add "New test task" --priority 4 --tags urgent'},
    )
    assert response.status_code == 200
    assert response.json()["reply"] == 'Created task "New test task" with id 101.'

    # Verify the payload sent to the Django API
    mock_requests.post.assert_called_once()
    call_args = mock_requests.post.call_args
    assert call_args.kwargs["json"]["title"] == "New test task"
    assert call_args.kwargs["json"]["priority"] == 4
    assert call_args.kwargs["json"]["tags"] == ["urgent"]


def test_task_done_success(mock_requests):
    """Test /task done successfully marks a task as complete."""
    # Mock for the POST to mark_complete
    mock_post_response = MagicMock()
    mock_post_response.raise_for_status.return_value = None

    # Mock for the GET to fetch the task title
    mock_get_response = MagicMock()
    mock_get_response.raise_for_status.return_value = None
    mock_get_response.json.return_value = {"id": 42, "title": "Finish tests"}

    # The first call is POST, the second is GET
    mock_requests.post.return_value = mock_post_response
    mock_requests.get.return_value = mock_get_response

    response = client.post("/assistant/chat", json={"message": "/task done 42"})
    assert response.status_code == 200
    assert response.json()["reply"] == "Marked complete: Finish tests"

    # Verify the POST call to the mark_complete action
    mock_requests.post.assert_called_once_with(
        "http://127.0.0.1:8000/api/tasks/42/mark_complete/",
        headers={"Authorization": "Token YOUR_DJANGO_AUTH_TOKEN_HERE"},
    )
    # Verify the GET call to fetch the task details
    mock_requests.get.assert_called_once_with(
        "http://127.0.0.1:8000/api/tasks/42/",
        headers={"Authorization": "Token YOUR_DJANGO_AUTH_TOKEN_HERE"},
    )


def test_task_done_not_found(mock_requests):
    """Test /task done handles a 404 Not Found error."""
    from requests.exceptions import HTTPError

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
    mock_requests.post.return_value = mock_response

    response = client.post("/assistant/chat", json={"message": "/task done 999"})
    assert response.status_code == 200
    assert response.json()["reply"] == "Task with ID 999 not found."


def test_unknown_command():
    """Test that an unknown command returns a helpful message."""
    response = client.post("/assistant/chat", json={"message": "/foo bar"})
    assert response.status_code == 200
    assert "Unknown command. Try:" in response.json()["reply"]