"""
Deterministic tools the assistant can call via slash-commands.
Backed by a simple JSON file so it's easy to understand and extend.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import ValidationError

from backend.src.models import Task


DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")

os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)


def _load_tasks() -> List[Task]:
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    tasks: List[Task] = []
    for item in raw:
        try:
            if isinstance(item.get("due_date"), str):
                try:
                    item["due_date"] = datetime.fromisoformat(item["due_date"]).replace(tzinfo=None)
                except Exception:
                    item["due_date"] = None
            tasks.append(Task(**item))
        except ValidationError:
            # Skip invalid entries rather than crashing
            continue
    return tasks


def _save_tasks(tasks: List[Task]) -> None:
    serializable = []
    for t in tasks:
        item = t.model_dump() if hasattr(t, "model_dump") else t.dict()  # pydantic v2|v1
        if isinstance(item.get("due_date"), datetime):
            item["due_date"] = item["due_date"].isoformat()
        serializable.append(item)
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)


def list_tasks(show_completed: bool = True) -> List[Task]:
    tasks = _load_tasks()
    if show_completed:
        return tasks
    return [t for t in tasks if not t.completed]


def create_task(
    title: str,
    description: Optional[str] = None,
    category: str = "general",
    due_date: Optional[str] = None,
    priority: int = 1,
    tags: Optional[list[str]] = None,
) -> Task:
    tasks = _load_tasks()
    new_task = Task(
        id=str(uuid.uuid4()),
        title=title.strip(),
        description=(description or "").strip() or None,
        category=category.strip() or "general",
        due_date=datetime.fromisoformat(due_date) if due_date else None,
        priority=priority,
        completed=False,
        tags=tags or [],
    )
    tasks.append(new_task)
    _save_tasks(tasks)
    return new_task


def complete_task(task_id: str) -> Optional[Task]:
    tasks = _load_tasks()
    for t in tasks:
        if t.id == task_id:
            t.completed = True
            _save_tasks(tasks)
            return t
    return None
