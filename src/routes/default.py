from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/")
def get_landing_page():
    message = "<h1>Welcome to Manukko Todos App!</h1>"
    return HTMLResponse (
        status_code=status.HTTP_200_OK,
        content=message
    )
