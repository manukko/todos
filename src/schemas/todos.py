from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str
    description: str
    completed: bool = False

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TodoModel(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime