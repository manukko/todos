from sqlalchemy import Column, Integer, String, Boolean, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, deferred
from src import env
from sqlalchemy.dialects import postgresql
from datetime import datetime

DATABASE_URL = env.POSTGRES_DB_URL
engine = create_engine(
    # DATABASE_URL, connect_args={"check_same_thread": False}, echo=True # for sqlite
    DATABASE_URL, echo=True # for postgres
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False, default="default_user")
    email = Column(String, unique=True, index=True, nullable=False, default="default@default.default")
    hashed_password = deferred(Column(String, nullable=False, default="default_password"))
    created_at = Column(postgresql.TIMESTAMP, default=datetime.now, nullable=False)
    updated_at = Column(postgresql.TIMESTAMP, default=datetime.now, nullable=False)
    todos = relationship("Todo", back_populates="owner", cascade="all")


class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(postgresql.TIMESTAMP, default=datetime.now, nullable=False)
    updated_at = Column(postgresql.TIMESTAMP, default=datetime.now, nullable=False)
    owner = relationship("User")


def init_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database is ready.")
