from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.routers.auth import require_manager


router = APIRouter(
    prefix="/v1/meta",
    tags=["meta"],
)


@router.get("")
def get_meta():
    return {
        "ticket_statuses": ["open", "resolved"],
        "ticket_priorities": ["normal", "high", "urgent"],
        "ticket_channels": ["web_form"],
    }


@router.get("/agents")
def get_active_agents(
    manager: User = Depends(require_manager),
    session: Session = Depends(get_db),
):
    agents = (
        session.query(User)
        .filter(
            User.role == "agent",
            User.is_active.is_(True),
        )
        .order_by(User.display_name.asc())
        .all()
    )

    return [
        {
            "id": agent.id,
            "display_name": agent.display_name,
        }
        for agent in agents
    ]