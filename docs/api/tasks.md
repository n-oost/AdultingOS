# Tasks API

List (requires Token)
- GET /api/tasks/
Headers
```
Authorization: Token <token>
```

Create
- POST /api/tasks/
Body
```
{ "title": "Pay rent", "priority": 2, "due_date": "2025-11-01T12:00:00Z", "category": "finance" }
```

Update
- PUT /api/tasks/{id}/
Body
```
{ "title": "Pay rent (updated)", "completed": true }
```

Delete
- DELETE /api/tasks/{id}/
