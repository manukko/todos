from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from typing import Optional
from src.db.models import Todo, User
from src.auth.auth import (
    get_db_session,
    get_current_user
)
from pydantic import BaseModel

router = APIRouter()

class TodoCreate(BaseModel):
    title: str
    description: str
    completed: bool = False

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# Create a new Todo
@router.post("/")
def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    new_todo = Todo(
        title=todo.title,
        description=todo.description,
        completed=todo.completed,
        owner_id=current_user.id,
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


# Get all Todos for current user
@router.get("/")
def get_todos(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return db.query(Todo).filter(Todo.owner_id == current_user.id).all()


# Get a Todo by id
@router.get("/todo/{todo_id}")
def get_todo_by_id(
    todo_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return (
            db.query(Todo)
            .filter(Todo.id == todo_id, Todo.owner_id == current_user.id)
            .one()
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )


# Get Todos by title
@router.get("/todo")
def get_todos_by_title(
    title: str = Query(..., title="title of the todo"),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Todo)
        .filter(Todo.title == title, Todo.owner_id == current_user.id)
        .all()
    )


# Update a Todo
@router.put("/todo/{todo_id}")
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    todo_from_db = (
        db.query(Todo)
        .filter(Todo.id == todo_id, Todo.owner_id == current_user.id)
        .first()
    )
    if todo_from_db:
        if todo_update.title is not None:
            todo_from_db.title = todo_update.title
        if todo_update.description is not None:
            todo_from_db.description = todo_update.description
        if todo_update.completed is not None:
            todo_from_db.completed = todo_update.completed
        todo_from_db.updated_at = datetime.now()
        db.commit()
        db.refresh(todo_from_db)
        return todo_from_db
    return {"error": "Todo not found"}


# Delete a Todo
@router.delete("/todo/{todo_id}")
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    db_todo = (
        db.query(Todo)
        .filter(Todo.id == todo_id, Todo.owner_id == current_user.id)
        .first()
    )
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return {"message": "Todo deleted"}
    return {"error": "Todo not found"}
