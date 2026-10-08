import os

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db
from app.routers.auth import require_manager


router = APIRouter(
    prefix="/v1/system",
    tags=["system"],
)


@router.get("/status")
def system_status(
    session: Session = Depends(get_db),
    _manager=Depends(require_manager),
):
    database_status = "Healthy"

    try:
        session.execute(text("SELECT 1"))
    except Exception:
        database_status = "Unavailable"

    return {
        "api": {
            "status": "Healthy",
        },
        "database": {
            "status": database_status,
        },
        "application": {
            "version": os.getenv("APP_VERSION", "development"),
            "environment": "Local Development",
        },
        "ai": {
            "assistant": "Not implemented",
            "ticket_classification": "Not implemented",
            "escalation_risk": "Not implemented",
        },
    }