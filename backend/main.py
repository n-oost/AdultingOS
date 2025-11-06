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
    message: str

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
async def chat(chat_message: ChatMessage, token: str = Depends(oauth2_scheme)):
    """
    Handles the chatbot conversation.
    Receives a message from the user and returns a response with user context.
    
    Returns:
        - message: The assistant's response message
        - user_profile: The user's profile data for context
    """
    headers = {"Authorization": f"Token {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/profile/me/", headers=headers)
        if response.status_code == 200:
            user_profile = response.json()
            
            # Generate a contextual response based on the user's message
            user_message = chat_message.message.strip()
            assistant_message = generate_assistant_response(user_message, user_profile)
            
            return {
                "message": assistant_message,
                "user_profile": user_profile,
                "timestamp": None  # Could add timestamp if needed
            }
        else:
            raise HTTPException(status_code=response.status_code, detail="Error fetching user profile")


def generate_assistant_response(user_message: str, user_profile: dict) -> str:
    """
    Generate a contextual response based on user message and profile.
    This is a simple implementation - in production, this would use OpenAI or another LLM.
    """
    username = user_profile.get("username", "there")
    
    # Simple greeting responses
    if any(greeting in user_message.lower() for greeting in ["hello", "hi", "hey"]):
        return f"Hi {username}! How can I help you with your adulting tasks today?"
    
    # Profile-related queries
    if "profile" in user_message.lower():
        completeness = user_profile.get("profile_completeness", 0)
        if completeness < 50:
            return f"Your profile is {completeness}% complete. Consider adding more information to get personalized recommendations!"
        return f"Your profile looks good at {completeness}% complete. How can I assist you?"
    
    # Task-related queries
    if any(word in user_message.lower() for word in ["task", "todo", "remind"]):
        return "I can help you manage your tasks! You can create, view, and complete tasks through the Tasks page. What would you like to do?"
    
    # Default response
    return f"I'm here to help you with adulting tasks, {username}! You can ask me about your profile, tasks, or get help with life admin. What would you like to know?"