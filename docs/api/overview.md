# API Overview

## Django REST API (Port 8000)

### Authentication
- POST /api/auth/register/
- POST /api/auth/login/
- Token: `Authorization: Token <token>`

### Tasks
- GET/POST /api/tasks/
- GET/PUT/PATCH/DELETE /api/tasks/{id}/
- POST /api/tasks/{id}/mark_complete/
- POST /api/tasks/{id}/mark_incomplete/

### Tags
- GET/POST /api/tags/
- GET/PUT/PATCH/DELETE /api/tags/{id}/

### User Profile
- GET/PATCH /api/profile/me/

## FastAPI Assistant API (Port 8001)

### Chat/Assistant
- POST /chat
  - Request: `{ "message": "your message" }`
  - Headers: `Authorization: Token <token>` (optional, but required for user context)
  - Response: User profile data and assistant response

See: `auth.md` and `tasks.md` for detailed request/response examples.
