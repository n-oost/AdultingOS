"""
Main file for the AdultingOS backend.
Configured for Vercel serverless deployment.
"""
import sys
from pathlib import Path

# Add the 'backend' directory to the Python path
# This allows uvicorn to find the 'src' module correctly when run from the project root
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
import httpx

# --- Auth ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Data Models ---
class ChatMessage(BaseModel):
    """Represents a message from the user."""
    text: str

# --- Application Setup ---
app = FastAPI(
    title="AdultingOS API",
    description="API for the AdultingOS application.",
    version="0.1.0",
    root_path="/api" if os.environ.get("VERCEL") else "",
)

# CORS (allow frontend during dev)
try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Replace with frontend URL in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
except Exception:
    pass

# Routers
try:
    from src.assistant.router import router as assistant_router
    app.include_router(assistant_router)
    print("✓ Assistant router loaded")
except Exception as e:
    print(f"✗ Assistant router failed: {e}")
    # Keep API usable even if assistant optional deps missing
    pass

# Note: src.tasks router is currently not implemented
# The task system is handled through Django REST API at /api/tasks/
# If you need FastAPI task endpoints, create a router in src/tasks.py

# --- API Endpoints ---

@app.get("/")
def read_root():
    """
    Root endpoint for the API.
    Returns a welcome message.
    """
    return {"message": "Welcome to the AdultingOS API!"}


@app.post("/chat")
async def chat(message: ChatMessage, token: str = Depends(oauth2_scheme)):
    """
    Handles the chatbot conversation.
    Receives a message from the user and returns a response.
    """
    headers = {"Authorization": f"Token {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/profile/me/", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Error fetching user profile")