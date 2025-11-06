# Frontend API Integration Summary

## Overview
This document summarizes the frontend API client implementation and integration with the backend services.

## Architecture

### Two Backend Services
1. **Django REST API** (Port 8000)
   - Handles authentication, tasks, tags, and user profiles
   - Token-based authentication
   
2. **FastAPI Assistant** (Port 8001)
   - Handles AI chat/assistant interactions
   - Forwards authentication to Django for user context

## API Service (`frontend/src/services/apiService.js`)

### Configuration
- `API_BASE`: Django REST API base URL (default: `http://127.0.0.1:8000`)
- `ASSISTANT_BASE`: FastAPI assistant base URL (default: `http://127.0.0.1:8001`)
- Both can be overridden via environment variables in `.env.local`

### Available Methods

#### Authentication (`auth`)
- `register(username, email, password)` - Register new user
- `login(username, password)` - Login existing user
- `logout()` - Clear auth token

#### Tasks (`tasks`)
- `list()` - Get all tasks for authenticated user
- `create(taskData)` - Create a new task
- `update(taskId, taskData)` - Update an existing task
- `markComplete(taskId)` - Mark task as complete
- `markIncomplete(taskId)` - Mark task as incomplete
- `delete(taskId)` - Delete a task

#### Tags (`tags`)
- `list()` - Get all tags
- `create(name)` - Create a new tag

#### User Profile (`profile`)
- `get()` - Get current user's profile
- `update(profileData)` - Update current user's profile

#### Assistant/Chat (`assistant`)
- `chat(message)` - Send a message to the AI assistant

### Authentication Flow
1. User logs in via `auth.login(username, password)`
2. Token is automatically stored in `authToken` variable
3. All subsequent API requests include `Authorization: Token <token>` header
4. Token persists in memory (resets on page refresh)

### Token Persistence Note
Currently, the auth token is stored in memory and resets on page refresh. For production, consider persisting to `localStorage` or `sessionStorage`.

## Component Integration

### LoginForm.jsx
- Uses `auth.login()` to authenticate users
- Passes user and token to parent component on success
- Shows validation and error messages

### TasksList.jsx
- Uses `tasks.list()` to fetch tasks
- Uses `tasks.create()` to add new tasks
- Uses `tasks.delete()` to remove tasks
- Automatically reloads task list after mutations

### Chatbot.js
- Uses `assistant.chat()` to send messages to FastAPI assistant
- Displays conversation history
- Shows loading state while waiting for responses
- Handles errors gracefully with user-friendly messages
- Requires user to be authenticated

## Environment Variables

Create a `.env.local` file in the `frontend/` directory to customize API URLs:

```bash
# Django API Base URL
REACT_APP_API_URL=http://127.0.0.1:8000

# FastAPI Assistant Base URL
REACT_APP_ASSISTANT_URL=http://127.0.0.1:8001
```

## Testing the Integration

### Prerequisites
1. Django server running on port 8000
2. FastAPI server running on port 8001
3. User account created (use `backend/test_api.py` or register via frontend)

### Test Flow
1. Start Django: `cd backend/adultingos_web && python manage.py runserver`
2. Start FastAPI: `cd backend && uvicorn main:app --host 127.0.0.1 --port 8001`
3. Start React: `cd frontend && npm start`
4. Navigate to `http://localhost:3000`
5. Login with test credentials
6. Try creating/viewing tasks
7. Try chatting with the assistant

## Key Changes Made

### apiService.js
- ✅ Added `profile` methods for user profile management
- ✅ Added `assistant` methods for AI chat integration
- ✅ Separated Django and FastAPI base URLs
- ✅ Added proper error handling for both services

### Chatbot.js
- ✅ Updated to use `assistant.chat()` from API service
- ✅ Fixed endpoint from `http://localhost:8000/chat` to FastAPI at port 8001
- ✅ Added authentication token to chat requests
- ✅ Added loading state and error handling
- ✅ Improved UX with placeholder messages and disabled state

### Documentation
- ✅ Created `.env.example` for frontend environment variables
- ✅ Updated `docs/api/overview.md` with complete endpoint listing
- ✅ Created this integration summary document

## Next Steps

### Recommended Improvements
1. **Token Persistence**: Store auth token in `localStorage` for persistence across page refreshes
2. **Profile Component**: Create a component to view/edit user profile using `profile.get()` and `profile.update()`
3. **Assistant Response Format**: Update FastAPI to return a proper message field (currently returns user profile)
4. **Error Boundaries**: Add React error boundaries for better error handling
5. **Loading States**: Add global loading indicator for API requests
6. **Offline Support**: Add service worker for offline functionality

### Testing Improvements
1. Add unit tests for API service methods
2. Add integration tests for components
3. Add E2E tests with Cypress or Playwright

## Troubleshooting

### "Connection refused" errors
- Ensure both Django (port 8000) and FastAPI (port 8001) servers are running
- Check that ports are not blocked by firewall
- Verify URLs in `.env.local` match your server configuration

### "Unauthorized" errors
- Ensure user is logged in before making authenticated requests
- Check that token is being set correctly after login
- Verify token is being sent in `Authorization` header

### Chat not working
- Ensure FastAPI server is running on port 8001
- Check browser console for detailed error messages
- Verify user is authenticated (chat requires auth token)

## Related Files
- `frontend/src/services/apiService.js` - API client implementation
- `frontend/src/components/LoginForm.jsx` - Login component
- `frontend/src/components/TasksList.jsx` - Tasks component
- `frontend/src/components/Chatbot.js` - Chat component
- `frontend/.env.example` - Environment variables template
- `docs/api/overview.md` - API documentation
