from fastapi import APIRouter

router = APIRouter()

@router.get("/api/v3/{request}")
def read_request(request: str):
    return {
        "request": request,
    }