from sqlalchemy import Column, Integer, String, Boolean, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    todos = relationship("Todo", back_populates="owner", cascade="all")

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    owner = relationship("User")

def init_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database is ready.")