# Copilot Instructions: AdultingOS

This repo has two backends (Django + FastAPI), a web frontend (React), and a mobile app (React Native). Use these notes to quickly understand architecture, workflows, and conventions when implementing changes.

## Architecture overview
- Django REST API (primary app)
	- Location: `backend/adultingos_web`
	- Auth: DRF Token Authentication, returned by custom endpoints in `core/views.py` (`/api/auth/register/`, `/api/auth/login/`).
	- Models: `core/models.py` (`Task`, `Tag`); serializers in `core/serializers.py` add computed fields like `priority_display`, `is_overdue` and expose tag names.
	- Routes: `adultingos_web/urls.py` includes `core/urls.py` under `/api/`.
	- Task endpoints: `TaskViewSet` with query params `completed=true|false`, `category`, `priority=1..5`, `search`; custom actions: `POST /api/tasks/{id}/mark_complete/`, `POST /api/tasks/{id}/mark_incomplete/`.
	- CORS: `corsheaders` enabled in `adultingos_web/settings.py` with dev origins `http://127.0.0.1:3000` and `http://localhost:3000`.

- FastAPI (assistant + experimental tasks)
	- Entry: `backend/main.py` (local dev default: `http://127.0.0.1:8001`). Uses `backend/src/assistant/router.py` for `POST /assistant/chat` and `backend/src/tasks.py` for `/tasks/*` (in-memory).
	- Assistant commands: `backend/src/assistant/tools.py` implements `/task` actions backed by `backend/data/tasks.json` (separate from Django DB). Example: `/task add "Pay rent" --desc "..." --cat "finance" --due 2025-12-31 --priority 2 --tags home,bills`.
	- LLM config: `backend/src/settings.py` selects provider (`MODEL_PROVIDER=openai|ollama`). For OpenAI set `OPENAI_API_KEY`, `OPENAI_MODEL`; for Ollama set `OLLAMA_BASE_URL`, `OLLAMA_MODEL`.

- Frontend (React)
	- Location: `frontend` with API wrapper in `frontend/src/services/apiService.js`. Default base URL `REACT_APP_API_URL || http://127.0.0.1:8000`.
	- Auth flow: `auth.login/register` set token via `setAuthToken`; all requests add `Authorization: Token <token>`.
	- Task operations mapped to Django endpoints (`/api/tasks/`, `/api/tags/`).

- Mobile (React Native)
	- Screens under `mobile/src/screens`. The tasks screen interacts with the assistant by posting chat messages like `/task list` and expects plain-text list output with `•/✔` and `[id]` (see `assistant/router.py`).

Note: There are two task systems for the MVP (Django DB vs assistant JSON/in-memory). Frontend web uses Django; assistant/mobile uses slash-commands via FastAPI.

## Run and test (Windows)
- VS Code tasks (recommended):
	- "Run Django Server": starts `python manage.py runserver 127.0.0.1:8000` in `backend/adultingos_web`.
	- "Run Frontend": CRA dev server in `frontend` on `http://127.0.0.1:3000`.
	- "Run Backend (FastAPI)": `uvicorn main:app --host 127.0.0.1 --port 8001 --reload` in `backend`.
	- "Run API Tests": waits for Django then runs `python backend/test_api.py`.
	- "Run All Tests": `pytest` under `backend/tests/`.
- Django ops (see `docs/backend/runbook.md`): `makemigrations`, `migrate`, `createsuperuser` in `backend/adultingos_web`.
- Env: Django loads `.env` from `backend/adultingos_web` (e.g., `DJANGO_SECRET_KEY`, `DEBUG=True`, `POSTGRES_*`).

## Conventions and patterns
- DRF ViewSets: restrict queryset to `request.user.tasks`; enforce `IsAuthenticated` for write; expose browsable API via `/api-auth/`.
- Serialization: `TaskSerializer` exposes `user` as username, `tags` as names, and computed `priority_display`/`is_overdue`.
- Filtering: prefer query params (`completed`, `category`, `priority`, `search`) over custom endpoints.
- CORS/CSRF: update `CORS_ALLOWED_ORIGINS`/`CSRF_TRUSTED_ORIGINS` when adding new dev hosts/ports.
- Assistant I/O: `/assistant/chat` accepts `{ message, history?, mode? }`. Messages starting with `/` route to tools (no LLM call). Replies may be plain text lists; clients should not assume JSON.

## Integration tips and pitfalls
- Ports: Django 8000, React 3000, FastAPI 8001. Update `REACT_APP_API_URL` for the web app; mobile should point to the FastAPI base when using the assistant.
- Vercel: FastAPI sets `root_path=/api` when `VERCEL` is set; clients may need to prefix routes accordingly.
- Keep systems separate unless explicitly syncing: edits to Django tasks do not affect `backend/data/tasks.json` and vice versa.

## Useful references
- Django: `backend/adultingos_web/core/{models.py,serializers.py,views.py,urls.py}`
- Assistant: `backend/src/assistant/{router.py,tools.py,client.py}`, data at `backend/data/tasks.json`
- API docs: `docs/api/{overview.md,auth.md,tasks.md}`
- Runbook: `docs/backend/runbook.md`

## Development guidelines (for agents)
- Communicate concise intent and changes; prefer small, targeted PRs.
- Before adding task features, choose the correct backend (Django vs assistant) and keep boundaries clear.
- When changing public API behavior, update `docs/api/*` and the web/mobile clients accordingly.
