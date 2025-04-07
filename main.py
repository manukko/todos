from fastapi import FastAPI
from models import init_db
from routes import router

init_db()

version = "v1"
app = FastAPI(
    title="todos api",
    version=version
    )
app.include_router(router=router, prefix=f"/api/{version}")