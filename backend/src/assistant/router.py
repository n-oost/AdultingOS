"""
FastAPI router exposing:
- POST /assistant/chat  => chat with LLM and handle slash-commands
"""
from __future__ import annotations

from typing import List, Optional, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.src.assistant.client import LLMClient
from backend.src.assistant.tools import list_tasks, create_task, complete_task
from backend.src.settings import get_settings

router = APIRouter()
settings = get_settings()
llm = LLMClient()


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    message: str
    history: Optional[List[ChatMessage]] = None
    mode: Literal["auto", "chat_only", "tools_only"] = "auto"


class ChatResponse(BaseModel):
    reply: str


@router.post("/assistant/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    text = req.message.strip()

    if text.startswith("/"):
        reply = _handle_command(text)
        return ChatResponse(reply=reply)

    if req.mode == "tools_only":
        raise HTTPException(status_code=400, detail="Tools-only mode requires a slash-command.")

    messages: List[dict] = [{"role": "system", "content": settings.system_prompt}]
    if req.history:
        messages.extend([m.dict() for m in req.history[-8:]])
    messages.append({"role": "user", "content": text})

    reply = llm.chat(messages)
    return ChatResponse(reply=reply)


def _handle_command(text: str) -> str:
    parts = text.split()
    if len(parts) < 2 or parts[0] != "/task":
        return (
            "Unknown command. Try:\n"
            "/task list\n"
            "/task add \"Title\" --desc \"...\" --cat \"...\" --due 2025-12-31 --priority 2 --tags home,finance\n"
            "/task done <task_id>"
        )

    sub = parts[1].lower()
    if sub == "list":
        tasks = list_tasks(show_completed=True)
        if not tasks:
            return "No tasks yet."
        lines = []
        for t in tasks:
            status = "✔" if t.completed else "•"
            due = f" (due {t.due_date.date()})" if t.due_date else ""
            lines.append(f"{status} {t.title} [{t.id}] {due} [prio {t.priority}]")
        return "\n".join(lines)

    if sub == "done":
        if len(parts) < 3:
            return "Usage: /task done <task_id>"
        done = complete_task(parts[2])
        return f"Marked complete: {done.title}" if done else "Task not found."

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

            priority = int(prio) if prio else 1
            tag_list = [t.strip() for t in tags.split(",")] if tags else []

            task = create_task(
                title=title,
                description=desc,
                category=cat,
                due_date=due,
                priority=priority,
                tags=tag_list,
            )
            return f'Created task "{task.title}" with id {task.id}.'
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
