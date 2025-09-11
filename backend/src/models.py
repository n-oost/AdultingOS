"""
Data models for the AdultingOS backend.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class Task(BaseModel):
    """Model for representing a task in the system"""
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    category: str
    due_date: Optional[datetime] = None
    priority: int = Field(1, ge=1, le=5)  # Priority from 1-5
    completed: bool = False
    tags: List[str] = []
    
    class Config:
        schema_extra = {
            "example": {
                "title": "File taxes",
                "description": "Gather documents and file annual tax return",
                "category": "finance",
                "due_date": "2025-04-15T00:00:00",
                "priority": 2,
                "tags": ["finance", "important", "annual"]
            }
        }


class User(BaseModel):
    """Model for representing a user in the system"""
    id: Optional[str] = None
    username: str
    email: str
    full_name: Optional[str] = None
    joined_date: datetime = datetime.now()
    preferences: Dict[str, any] = {}
    
    class Config:
        schema_extra = {
            "example": {
                "username": "adultuser",
                "email": "user@example.com",
                "full_name": "Adult User",
                "preferences": {
                    "theme": "dark",
                    "notifications": True
                }
            }
        }
