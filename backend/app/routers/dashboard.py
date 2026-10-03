from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.routers.auth import require_manager
from app.services.dashboard import get_dashboard_summary

router = APIRouter(
    prefix="/v1/dashboard",
    tags=["dashboard"],
)


@router.get("/summary")
def dashboard_summary(
    session: Session = Depends(get_db),
    _manager=Depends(require_manager),
):
    return get_dashboard_summary(session)