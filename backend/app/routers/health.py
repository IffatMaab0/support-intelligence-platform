from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db import engine


router = APIRouter()


@router.get("/health/live")
def health_check():
    return {"status": "ok"}


@router.get("/health/ready")
def readiness_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {"status": "ready"}

    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable"},
        )


    