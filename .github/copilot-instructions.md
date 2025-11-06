# Copilot Instructions: AdultingOS

Quick guide for AI agents to work effectively in this repo. Focus on what exists, how components talk to each other, and current integration status.

## Big picture
- Django REST API (primary) — `backend/adultingos_web`
  - Auth: DRF Token auth with custom endpoints in `core/views.py`: `POST /api/auth/register/`, `POST /api/auth/login/`.
  - Core resources: `Task`, `Tag`, `UserProfile` in `core/models.py` with DRF serializers in `core/serializers.py`.
  - Tasks: `TaskViewSet` supports filters `completed=true|false`, `category`, `priority=1..5`, `search`; custom actions `POST /api/tasks/{id}/mark_complete/` and `POST /api/tasks/{id}/mark_incomplete/`.
  - Routing: `adultingos_web/urls.py` mounts `core/urls.py` at `/api/`; browsable API at `/api-auth/`.
  - CORS: `adultingos_web/settings.py` enables `corsheaders` for `http://127.0.0.1:3000` and `http://localhost:3000`.

- FastAPI (assistant + experimental tasks) — `backend/main.py`
  - Runs at `http://127.0.0.1:8001` in dev. Imports routers from `src.assistant.router` and `src.tasks` (top-level `src/`).
  - Assistant slash-commands are handled in the assistant router; tools operate on simple data (see `data/tasks.json`) separate from Django DB.
  - Vercel: sets `root_path="/api"` when `VERCEL` is set.
  - Important integration: `POST /chat` expects an OAuth2 token and then calls Django `/api/profile/me/` with header `Authorization: Token <token>`.

-- Web frontend (React) — `frontend`
  - API client: `frontend/src/services/apiService.js` uses `REACT_APP_API_URL` or defaults to `http://127.0.0.1:8000` and sends `Authorization: Token <token>`.
  - Screens/components map to Django endpoints for tasks/tags.
  - Assistant/chat integration via `REACT_APP_ASSISTANT_URL` (default: `http://127.0.0.1:8001`).
  - User profile endpoints and assistant endpoints now supported in API client.

-- Mobile (React Native) — `mobile`
  - Screens under `mobile/src/screens`. Chat use-cases talk to the assistant via FastAPI.
  - API client in `mobile/src/services/apiService.js` now matches web frontend: supports tasks, tags, profile, and assistant endpoints.

Note: Two task systems exist in the repo for the MVP — Django DB (primary, used by web/mobile) and assistant JSON/in-memory (used by assistant/mobile). They are intentionally not synced.

## Dev workflows (Windows PowerShell)
- Django API
  - cd `backend\adultingos_web`; run: `python manage.py runserver 127.0.0.1:8000`
  - Migrations/admin: see `docs/backend/runbook.md` for `makemigrations`, `migrate`, `createsuperuser`.
- FastAPI (assistant)
  - Ensure Python can import top-level `src` (set `PYTHONPATH` to repo root if needed).
  - From repo root: `uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload`
-- Frontend
  - cd `frontend`; `npm install`; `npm start` (uses `REACT_APP_API_URL` and `REACT_APP_ASSISTANT_URL` if set).
-- Mobile
  - cd `mobile`; follow React Native setup for your platform; ensure endpoints match backend URLs.
- Smoke test API
  - With Django running, execute `python backend/test_api.py` to exercise auth, tasks, and tags via HTTP.

## Patterns and conventions
- DRF ViewSets restrict data to the current user and require auth for writes (`permissions.IsAuthenticated`). See `core/views.py`.
- Task serialization uses tag names (SlugRelatedField) and exposes computed fields: `priority_display`, `is_overdue`. See `core/serializers.py`.
- Prefer query parameters for filtering (`completed`, `category`, `priority`, `search`) instead of new endpoints.
- JSON Schema for foundational identity is served at `GET /api/schemas/foundational-documents/` (loads from `core/schemas/foundational_documents.schema.json`).
-- CORS/CSRF origins live in `adultingos_web/settings.py`; update when adding new dev hosts/ports.
-- API clients (web and mobile) should use the provided API service modules and environment variables for base URLs.

## Integration gotchas
- Ports: Django 8000, Frontend 3000, FastAPI 8001.
- Tokens: FastAPI `/chat` forwards `Authorization: Token <token>` to Django; ensure you use DRF token values, not OAuth/JWT.
- Data split: Changes to Django tasks don’t affect `data/tasks.json` and vice versa.
-- Serverless: If deploying FastAPI to Vercel, account for `root_path=/api` in client base URLs.
-- Mobile and web clients now use matching API service modules and support all endpoints (tasks, tags, profile, assistant).

## Handy examples
- Filter tasks: `GET /api/tasks/?completed=false&priority=3&search=rent`
- Mark complete: `POST /api/tasks/{id}/mark_complete/`
-- Create tag: `POST /api/tags/` with `{ "name": "important" }`
-- Chat with assistant: `POST /chat` with `{ "message": "your message" }` and `Authorization: Token <token>`
-- Get user profile: `GET /api/profile/me/` with `Authorization: Token <token>`

## Pointers
- Django: `backend/adultingos_web/core/{models.py,serializers.py,views.py,urls.py}`
- FastAPI: `backend/main.py`, routers from `src.assistant.router` and `src.tasks`
- Data: `data/tasks.json`, embeddings at `data/embeddings.jsonl`
-- Docs: `docs/api/{overview.md,auth.md,tasks.md}`, `docs/backend/runbook.md`, `docs/architecture.md`, `docs/frontend/integration.md`

## For AI changes
- Pick the correct boundary first (Django vs assistant). Don’t cross-write between systems unless explicitly required.
-- If you change public API shapes or behavior, update `docs/api/*`, `docs/frontend/integration.md`, and confirm `frontend/src/services/apiService.js` and `mobile/src/services/apiService.js` expectations.
