from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from models import Todo, User
from auth import get_db, get_current_user, create_access_token, authenticate_user, get_password_hash
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str

class TodoCreate(BaseModel):
    title: str
    description: str
    completed: bool = False

USERNAME_FORBIDDEN_CHARACTERS = list("$%\\/<>:^?!")
def check_username(username: str) -> bool:
    return len(username) >= 5 and len(username) <= 30 and \
        not any(c in USERNAME_FORBIDDEN_CHARACTERS for c in username)
def check_password(password: str) -> bool:
    return len(password) >= 9  and len(password) <= 30 \
        and any(c.isdigit() for c in password) \
        and any(c.isalpha() for c in password)

# User registration
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Username already registered"
        )
    if not check_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"Username must contain 5 to 30 characters, not in the list {USERNAME_FORBIDDEN_CHARACTERS}"
        )
    if not check_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Password must contain 9 to 30 characters, including at least one letter and one digit"
        )
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

# User authentication: return a bearer token that allows the user to access the service
@router.post("/get_auth_token")
def get_auth_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.delete("/delete_user")
def delete_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted"}

# Create a new Todo
@router.post("/create_todo")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_todo = Todo(title=todo.title, description=todo.description, completed=todo.completed, owner_id=current_user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

# Get all Todos for current user
@router.get("/todos")
def get_todos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Todo).filter(Todo.owner_id == current_user.id).all()

# Get a Todo by id
@router.get("/todo/{todo_id}")
def get_todo_by_id(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

# Get Todos by title
@router.get("/todos_by_title")
def get_todos_by_title(title: str = Query(..., title="title of the todo"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Todo).filter(Todo.title == title, Todo.owner_id == current_user.id).all()

# Update a Todo
@router.put("/update_todo/{todo_id}")
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
@router.delete("/delete_todo/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return {"message": "Todo deleted"}
    return {"error": "Todo not found"}
