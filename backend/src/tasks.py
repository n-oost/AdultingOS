"""
API endpoints for the task management system.
"""
from fastapi import APIRouter, HTTPException, Path, Body
from typing import List
import uuid

from backend.src.models import Task
from backend.src.utils import format_response

# Create a router for task management
router = APIRouter(prefix="/tasks", tags=["tasks"])

# In-memory storage for tasks (replace with database in production)
tasks_db = {}


@router.post("/", response_model=dict)
async def create_task(task: Task):
    """
    Create a new task in the system.
    """
    task_id = str(uuid.uuid4())
    task.id = task_id
    tasks_db[task_id] = task
    
    return format_response(
        task.dict(),
        message="Task created successfully"
    )


@router.get("/", response_model=dict)
async def get_all_tasks():
    """
    Retrieve all tasks in the system.
    """
    return format_response(
        [task.dict() for task in tasks_db.values()],
        message=f"Retrieved {len(tasks_db)} tasks"
    )


@router.get("/{task_id}", response_model=dict)
async def get_task(task_id: str = Path(..., description="The ID of the task to retrieve")):
    """
    Retrieve a specific task by ID.
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return format_response(
        tasks_db[task_id].dict(),
        message="Task retrieved successfully"
    )


@router.put("/{task_id}", response_model=dict)
async def update_task(
    task_update: dict = Body(...),
    task_id: str = Path(..., description="The ID of the task to update")
):
    """
    Update a specific task by ID.
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    # Update task attributes from the request
    for key, value in task_update.items():
        if hasattr(task, key):
            setattr(task, key, value)
    
    tasks_db[task_id] = task
    
    return format_response(
        task.dict(),
        message="Task updated successfully"
    )


@router.delete("/{task_id}", response_model=dict)
async def delete_task(task_id: str = Path(..., description="The ID of the task to delete")):
    """
    Delete a specific task by ID.
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    deleted_task = tasks_db.pop(task_id)
    
    return format_response(
        deleted_task.dict(),
        message="Task deleted successfully"
    )
