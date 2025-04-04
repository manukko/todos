from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Todo, User, init_db
from auth import get_db, get_current_user, create_access_token, authenticate_user, get_password_hash
from pydantic import BaseModel
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()

init_db()

class UserCreate(BaseModel):
    username: str
    password: str

class TodoCreate(BaseModel):
    title: str
    description: str
    completed: bool = False

# User registration
@app.post("/register/")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=409, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

# User authentication: return a bearer token that allows the user to access the service
@app.post("/token/")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.delete("/delete_user")
def delete_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted"}

# Create a new Todo
@app.post("/todos/")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_todo = Todo(title=todo.title, description=todo.description, completed=todo.completed, owner_id=current_user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

# Get all Todos for current user
@app.get("/todos/")
def read_todos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Todo).filter(Todo.owner_id == current_user.id).all()

# Update a Todo
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if db_todo:
        db_todo.title = todo.title
        db_todo.description = todo.description
        db_todo.completed = todo.completed
        db.commit()
        db.refresh(db_todo)
        return db_todo
    return {"error": "Todo not found"}

# Delete a Todo
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return {"message": "Todo deleted"}
    return {"error": "Todo not found"}
