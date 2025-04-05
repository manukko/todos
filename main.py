from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from models import Todo, User, init_db
from auth import get_db, get_current_user, create_access_token, authenticate_user, get_password_hash, TOKEN_DEFAULT_LIFESPAN_MINUTES
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
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

# User authentication: return a bearer token that allows the user to access the service
@app.post("/get_auth_token/")
def get_auth_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.delete("/delete_user")
def delete_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted"}

# Create a new Todo
@app.post("/create_todo/")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_todo = Todo(title=todo.title, description=todo.description, completed=todo.completed, owner_id=current_user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

# Get all Todos for current user
@app.get("/todos/")
def get_todos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Todo).filter(Todo.owner_id == current_user.id).all()

# Get a Todo by id
@app.get("/todo/{todo_id}")
def get_todo_by_id(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

# Get Todos by title
@app.get("/todos_by_title/")
def get_todos_by_title(title: str = Query(..., "title of the todo"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Todo).filter(Todo.title == title, Todo.owner_id == current_user.id).all()

# Update a Todo
@app.put("/update_todo/{todo_id}")
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
@app.delete("/delete_todo/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return {"message": "Todo deleted"}
    return {"error": "Todo not found"}
