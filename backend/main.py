"""
Main file for the AdultingOS backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Data Models ---
class ChatMessage(BaseModel):
    """Represents a message from the user."""
    text: str

# --- Application Setup ---
app = FastAPI(
    title="AdultingOS API",
    description="API for the AdultingOS application.",
    version="0.1.0",
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
    from backend.src.assistant.router import router as assistant_router
    app.include_router(assistant_router)
except Exception:
    # Keep API usable even if assistant optional deps missing
    pass

try:
    from backend.src.tasks import router as tasks_router
    app.include_router(tasks_router)
except Exception:
    pass

# --- In-memory storage for conversation state and user profile ---
# NOTE: This is a temporary solution for the MVP. In a real application, this would be a database.
conversation_state = {
    "question_index": 0,
    "questions": [
        {"id": "is_student", "text": "Are you currently a student?"},
        {"id": "income", "text": "What is your approximate annual income?"},
        {"id": "rent_or_own", "text": "Do you rent or own your home?"},
        {"id": "is_married", "text": "Are you married or single?"},
    ],
}

user_profile = {}

# --- API Endpoints ---

@app.get("/")
def read_root():
    """
    Root endpoint for the API.
    Returns a welcome message.
    """
    return {"message": "Welcome to the AdultingOS API!"}


@app.post("/chat")
def chat(message: ChatMessage):
    """
    Handles the chatbot conversation.
    Receives a message from the user and returns a response.
    """
    global conversation_state, user_profile

    # Get the current question
    question_index = conversation_state["question_index"]
    questions = conversation_state["questions"]

    # Store the user's answer
    if question_index > 0:
        previous_question = questions[question_index - 1]
        user_profile[previous_question["id"]] = message.text

    # If there are more questions, ask the next one
    if question_index < len(questions):
        next_question = questions[question_index]
        conversation_state["question_index"] += 1
        return {"text": next_question["text"], "sender": "bot"}
    else:
        # End of the conversation
        return {"text": "Thank you for completing your profile!", "sender": "bot"}