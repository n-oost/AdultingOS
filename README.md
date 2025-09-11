# AdultingOS

AdultingOS is a monorepo with a Python/FastAPI backend and a React frontend to help users navigate the challenges of adult life.

## Project Structure

- `backend/` FastAPI backend
   - `src/` app modules (settings, assistant, tasks, models, utils)
   - `data/` local data (JSON, etc.)
   - `tests/` unit tests (pytest)
- `frontend/` React app (Create React App)

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- (Optional) Ollama for local LLM: https://ollama.com

## Quick Start

Backend (first time):

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r backend\requirements.txt
```

Run backend:

```powershell
.\r
.\n+# from repo root
python -m venv venv; .\venv\Scripts\Activate.ps1; setx PYTHONPATH "${PWD}"; uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
```

Frontend:

```powershell
cd frontend; npm install; npm start
```

Backend API: http://127.0.0.1:8001
Frontend dev: http://localhost:3000

## VS Code Tasks

Tasks are available to run services and tests:
- Run Backend
- Run Frontend
- Run All Tests

## Configuration

Backend reads environment variables from `backend/.env` if present. Example:

```
MODEL_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:1b
```

## Tests

```powershell
cd backend; python -m pytest -q
```

## License

Private.
