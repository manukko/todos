from datetime import datetime
from typing import List
from pydantic import BaseModel

from src.schemas.todos import TodoModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserModel(BaseModel):
    username: str
    email: str
    created_at: datetime
    updated_at: datetime
    role: str

class UserTodosModel(UserModel):
    todos: List[TodoModel]
