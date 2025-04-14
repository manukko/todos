from datetime import timedelta
import datetime
from typing import Any
import src.env as env
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.models import User, SessionLocal

# Secret key and JWT settings: to define in env.py
SECRET_KEY = env.SECRET_KEY
ALGORITHM = env.ALGORITHM

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials: please provide a valid access token",
    headers={"WWW-Authenticate": "Bearer"},
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_token(
    data: dict,
    expires_delta: timedelta,
    is_refresh_token: bool = False
):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    to_encode.update({"refresh": is_refresh_token})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def validate_token(token: str, is_refresh_token: bool = False) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        refresh = payload.get("refresh")
        exp = payload.get("exp")
        if (
            username is None
            or exp is None
            or refresh is None
            or refresh != is_refresh_token
            or datetime.datetime.fromtimestamp(exp) < datetime.datetime.now()
        ):
            raise CREDENTIALS_EXCEPTION
    except JWTError:
        raise CREDENTIALS_EXCEPTION
    return payload


def get_current_user(
    access_token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)
):
    payload = validate_token(access_token)
    username = payload.get("sub")
    user = get_user(db, username)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user
