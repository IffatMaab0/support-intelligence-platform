from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import AuthSession, Ticket, User, UserRole
from app.schemas import AgentCreate, AgentUpdate
from app.security import hash_password
from datetime import datetime, timezone


def list_agents(session: Session) -> list[dict]:
    agents = (
        session.query(User)
        .filter(User.role == "agent")
        .order_by(User.display_name)
        .all()
    )

    return [
        {
            "id": str(agent.id),
            "display_name": agent.display_name,
            "email": agent.email,
            "is_active": agent.is_active,
            "version": agent.version,
        }
        for agent in agents
    ]


def create_agent(
    session: Session,
    data: AgentCreate,
) -> User:
    normalized_email = str(data.email).strip().lower()

    existing_user = (
        session.query(User)
        .filter(User.email == normalized_email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    agent = User(
        email=normalized_email,
        password_hash=hash_password(data.initial_password),
        display_name=data.display_name.strip(),
        role=UserRole.agent,
        is_active=True,
    )

    session.add(agent)
    session.commit()
    session.refresh(agent)

    return agent

def update_agent(
    session: Session,
    agent_id,
    data: AgentUpdate,
) -> User:
    agent = (
        session.query(User)
        .filter(
            User.id == agent_id,
            User.role == UserRole.agent,
        )
        .first()
    )

    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found.",
        )

    if agent.version != data.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This agent was updated by someone else. Please refresh and try again.",
        )

    if not data.is_active and agent.is_active:
        active_ticket_count = (
            session.query(Ticket)
            .filter(
                Ticket.assigned_agent_id == agent.id,
                Ticket.status.in_(["open", "in_review"]),
            )
            .count()
        )

        if active_ticket_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Agent cannot be deactivated while "
                    f"{active_ticket_count} active ticket(s) remain assigned. "
                    f"Reassign the tickets first."
                ),
            )

    agent.display_name = data.display_name.strip()

    if agent.is_active and not data.is_active:
        session.query(AuthSession).filter(
            AuthSession.user_id == agent.id,
            AuthSession.revoked_at.is_(None),
        ).update(
            {
                AuthSession.revoked_at: datetime.now(timezone.utc),
            },
            synchronize_session=False,
        )

    agent.is_active = data.is_active
    agent.version += 1

    session.commit()
    session.refresh(agent)

    return agent