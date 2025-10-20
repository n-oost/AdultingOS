# Auth API

Register
- POST /api/auth/register/
Request
```
{
  "username": "demo",
  "email": "demo@example.com",
  "password": "Password123!",
  "password_confirm": "Password123!"
}
```
Response
```
{ "user": { "id": 1, "username": "demo", "email": "demo@example.com" }, "token": "..." }
```

Login
- POST /api/auth/login/
Request
```
{ "username": "demo", "password": "Password123!" }
```
Response
```
{ "user": { "id": 1, "username": "demo", "email": "demo@example.com" }, "token": "..." }
```
