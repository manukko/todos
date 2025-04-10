from fastapi import FastAPI
from src.db.models import init_db
from src.routes.todos import router as todo_router
from src.routes.users import router as user_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting...")
    init_db()
    yield
    print("Server is stopping...")


version = "v1"
app = FastAPI(title="todos api", version=version, lifespan=lifespan)
app.include_router(router=todo_router, prefix=f"/api/{version}/todos")
app.include_router(router=user_router, prefix=f"/api/{version}/users")
