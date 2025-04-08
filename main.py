from fastapi import FastAPI
from models import init_db
from routes import router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting...")
    init_db()
    yield
    print("Server is stopping...")


version = "v1"
app = FastAPI(title="todos api", version=version, lifespan=lifespan)
app.include_router(router=router, prefix=f"/api/{version}")
