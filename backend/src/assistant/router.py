"""
FastAPI router for the AdultingOS AI assistant.

This module defines the primary API endpoint for interacting with the assistant:
- `POST /assistant/chat`: Handles user messages, processes slash-commands (e.g., `/task list`, `/task add`)
  by integrating with the Django backend's API, and routes natural language queries to an LLM.

"""
from __future__ import annotations

from typing import List, Optional, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import requests

from src.assistant.client import LLMClient
from src.knowledge_base.kb import FormKnowledgeBase, format_results_plain
from src.settings import get_settings
router = APIRouter()
settings = get_settings()
llm = LLMClient()


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    user_id: Optional[str] = None # In a real app, this would be used to get the user's auth token
    message: str
    history: Optional[List[ChatMessage]] = None
    mode: Literal["auto", "chat_only", "tools_only"] = "auto"


class ChatResponse(BaseModel):
    reply: str


# --- Configuration for Django API Integration ---
DJANGO_API_BASE_URL = "http://127.0.0.1:8000/api"
# In a real application, you would fetch this token securely based on the user_id
# For this MVP integration, we'll use a hardcoded token.
# To get a token:
# 1. Run "python backend/adultingos_web/manage.py createsuperuser"
# 2. Login to the Django admin at http://127.0.0.1:8000/admin/
# 3. Go to "Authtokens" -> "Tokens" and add a token for your user.
# 4. Paste the generated key here.
DJANGO_AUTH_TOKEN = "YOUR_DJANGO_AUTH_TOKEN_HERE" # Replace with your actual token


@router.post("/assistant/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    text = req.message.strip()

    if text.startswith("/"):
        reply = _handle_command(text, req.user_id)
        return ChatResponse(reply=reply)

    if req.mode == "tools_only":
        raise HTTPException(status_code=400, detail="Tools-only mode requires a slash-command.")

    messages: List[dict] = [{"role": "system", "content": settings.system_prompt}]
    if req.history:
        messages.extend([m.dict() for m in req.history[-8:]])
    messages.append({"role": "user", "content": text})

    reply = llm.chat(messages)
    return ChatResponse(reply=reply)


def _handle_command(text: str, user_id: Optional[str] = None) -> str:
    parts = text.split()
    if not parts:
        return "Empty command."

    # Knowledge base search: /kb search <query>
    if parts[0] == "/kb":
        if len(parts) >= 2 and parts[1].lower() == "search":
            query = text.split("search", 1)[1].strip() if "search" in text else ""
            if not query:
                return "Usage: /kb search <query>"
            kb = FormKnowledgeBase()
            results = kb.search(query, top_k=5)
            return format_results_plain(results)
        return (
            "Unknown /kb command. Try:\n"
            "/kb search how to apply cpp\n"
            "/kb search TD1 Ontario 2025"
        )

    # Task commands
    if parts[0] != "/task" or len(parts) < 2:
        return (
            "Unknown command. Try:\n"
            "/task list\n"
            "/task add \"Title\" --desc \"...\" --cat \"...\" --due 2025-12-31 --priority 2 --tags home,finance\n"
            "/task done <task_id>\n"
            "/kb search <query>"
        )

    sub = parts[1].lower()
    if sub == "list":
        try:
            headers = {"Authorization": f"Token {DJANGO_AUTH_TOKEN}"}
            response = requests.get(f"{DJANGO_API_BASE_URL}/tasks/", headers=headers)
            response.raise_for_status()
            tasks = response.json()
            if not tasks:
                return "No tasks found."
            lines = []
            for t in tasks:
                status = "✔" if t.get('completed') else "•"
                due_str = t.get('due_date')
                due = f" (due {due_str.split('T')[0]})" if due_str else ""
                lines.append(f"{status} {t.get('title')} [{t.get('id')}] {due} [prio {t.get('priority')}]")
            return "\n".join(lines)
        except requests.RequestException as e:
            return f"Error fetching tasks from Django API: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    if sub == "done":
        if len(parts) < 3:
            return "Usage: /task done <task_id>"
        task_id = parts[2]
        try:
            headers = {"Authorization": f"Token {DJANGO_AUTH_TOKEN}"}
            # Use the custom action on the Django TaskViewSet
            response = requests.post(f"{DJANGO_API_BASE_URL}/tasks/{task_id}/mark_complete/", headers=headers)
            response.raise_for_status()
            # Fetch the task to show its title
            get_response = requests.get(f"{DJANGO_API_BASE_URL}/tasks/{task_id}/", headers=headers)
            get_response.raise_for_status()
            task_title = get_response.json().get('title', f"Task {task_id}")
            return f"Marked complete: {task_title}"
        except requests.RequestException as e:
            if e.response and e.response.status_code == 404:
                return f"Task with ID {task_id} not found."
            return f"Error completing task: {e}"

    if sub == "add":
        try:
            remainder = text[text.index("add") + 3 :].strip()
            title = None
            if remainder.startswith('"'):
                end = remainder.find('"', 1)
                if end == -1:
                    return 'Missing closing quote for title. Example: /task add "Pay rent"'
                title = remainder[1:end]
                remainder = remainder[end + 1 :].strip()
            else:
                sp = remainder.find(" --")
                title = remainder[:sp].strip() if sp != -1 else remainder.strip()
                remainder = remainder[sp:] if sp != -1 else ""

            desc = _extract_flag(remainder, "--desc")
            cat = _extract_flag(remainder, "--cat") or "general"
            due = _extract_flag(remainder, "--due")
            prio = _extract_flag(remainder, "--priority")
            tags = _extract_flag(remainder, "--tags")

            priority = int(prio) if prio and prio.isdigit() else 2 # Default to Medium
            tag_list = [t.strip() for t in tags.split(",")] if tags else []

            payload = {
                "title": title,
                "description": desc,
                "category": cat,
                "due_date": due,
                "priority": priority,
                "tags": tag_list,
            }
            # Filter out None values
            payload = {k: v for k, v in payload.items() if v is not None}

            headers = {"Authorization": f"Token {DJANGO_AUTH_TOKEN}"}
            response = requests.post(f"{DJANGO_API_BASE_URL}/tasks/", json=payload, headers=headers)
            response.raise_for_status()
            new_task = response.json()
            return f'Created task "{new_task.get("title")}" with id {new_task.get("id")}.'
        except Exception as e:  # noqa: BLE001 - keep simple for MVP
            return f"Could not add task: {e}"

    return "Unknown /task subcommand."


def _extract_flag(text: str, flag: str) -> Optional[str]:
    if flag not in text:
        return None
    after = text.split(flag, 1)[1].strip()
    if not after:
        return None
    if after.startswith('"'):
        end = after.find('"', 1)
        if end == -1:
            return None
        return after[1:end]
    next_idx = after.find(" --")
    return after[:next_idx].strip() if next_idx != -1 else after.strip()
