# Architecture (High Level)

- Backend: Django REST Framework + PostgreSQL
  - App(s): core (tasks/tags)
  - Auth: DRF Token Auth (authtoken)
- Frontend: React (web)
  - API client in `frontend/src/services/apiService.js`
  - Components: Login, Register, Tasks, Chatbot
- Environments
  - Dev: Django API (127.0.0.1:8000), React (localhost:3000)
  - Secrets via `.env` at `backend/adultingos_web/.env`
