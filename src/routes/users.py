import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.models import User
from src.auth.auth import (
    get_db_session,
    get_current_user,
    create_token,
    authenticate_user,
    get_password_hash,
)
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

USERNAME_FORBIDDEN_CHARACTERS = list("$%\\/<>:^?!")
ACCESS_TOKEN_DEFAULT_LIFESPAN_MINUTES = 60
REFRESH_TOKEN_DEFAULT_LIFESPAN_HOURS = 36


def check_username(username: str) -> bool:
    return (
        len(username) >= 5
        and len(username) <= 30
        and not any(c in USERNAME_FORBIDDEN_CHARACTERS for c in username)
    )


def check_password(password: str) -> bool:
    return (
        len(password) >= 9
        and len(password) <= 30
        and any(c.isdigit() for c in password)
        and any(c.isalpha() for c in password)
    )


# User registration
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db_session)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already registered"
        )
    if not check_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Username must contain 5 to 30 characters, not in the list {USERNAME_FORBIDDEN_CHARACTERS}",
        )
    if not check_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password must contain 9 to 30 characters, including at least one letter and one digit",
        )
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}


# User authentication: return a bearer token that allows the user to access the service
@router.post("/get_access_token")
def get_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_token(
        data={"sub": user.username},
        expires_delta=datetime.timedelta(minutes=ACCESS_TOKEN_DEFAULT_LIFESPAN_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User authentication: return a bearer token that allows the user to access the service
@router.post("/get_refresh_token")
def get_refresh_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    refresh_token = create_token(
        data={"sub": user.username},
        expires_delta=datetime.timedelta(hours=REFRESH_TOKEN_DEFAULT_LIFESPAN_HOURS),
        is_refresh_token=True
    )
    return {"refresh_token": refresh_token, "token_type": "bearer"}


@router.delete("/delete")
def delete_user(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted"}