from fastapi import APIRouter

router = APIRouter()


@router.get("/health/live")
def health_check():
    return {"status": "ok"}