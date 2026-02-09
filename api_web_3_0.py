import engine.searchEngine as searchEngine
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/v3/{request}")
def read_request(request: str):
    return {
        "request": request,
    }