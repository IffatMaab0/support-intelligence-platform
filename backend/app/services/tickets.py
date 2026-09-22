from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Ticket, TicketEvent, TicketMessage, User
from sqlalchemy.exc import SQLAlchemyError

def create_ticket(
    session: Session,
    customer: User,
    subject: str,
    original_message: str,
) -> Ticket:

    now = datetime.now(timezone.utc)

    ticket = Ticket(
        customer_id=customer.id,
        assigned_agent_id=None,
        subject=subject,
        original_message=original_message,
        channel="web_form",
        status="open",
        priority="normal",
        created_at=now,
        updated_at=now,
        last_public_activity_at=now,
        resolved_at=None,
        version=1,
    )

    session.add(ticket)
    session.flush()

    event = TicketEvent(
        ticket_id=ticket.id,
        actor_user_id=customer.id,
        event_type="created",
        details="Ticket created through web form.",
        created_at=now,
    )

    session.add(event)

    session.commit()
    session.refresh(ticket)

    return ticket


def assign_ticket(
    session: Session,
    ticket: Ticket,
    manager: User,
    assigned_agent_id,
    expected_version: int,
) -> Ticket:
    ticket = (
        session.query(Ticket)
        .filter(Ticket.id == ticket.id)
        .with_for_update()
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    if ticket.version != expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ticket has changed. Please refresh and try again.",
        )

    if ticket.status == "resolved":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resolved tickets cannot be reassigned.",
        )

    agent = None

    if assigned_agent_id is not None:
        agent = (
            session.query(User)
            .filter(User.id == assigned_agent_id)
            .first()
        )

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned agent not found.",
            )

        if agent.role.value != "agent":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned user must be an agent.",
            )

        if not agent.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned agent is inactive.",
            )

    previous_agent_id = ticket.assigned_agent_id
    ticket.assigned_agent_id = assigned_agent_id
    ticket.updated_at = datetime.now(timezone.utc)
    ticket.version += 1

    if previous_agent_id is None and assigned_agent_id is not None:
        details = f"Ticket assigned to agent {agent.display_name} by manager."

    elif previous_agent_id is not None and assigned_agent_id is not None:
        details = (
            f"Ticket reassigned from agent ID {previous_agent_id} "
            f"to agent {agent.display_name} by manager."
        )

    else:
        details = "Ticket unassigned by manager."

    event = TicketEvent(
        ticket_id=ticket.id,
        actor_user_id=manager.id,
        event_type="assignment_changed",
        details=details,
        created_at=ticket.updated_at,
    )

    session.add(event)
    session.commit()
    session.refresh(ticket)

    return ticket


def add_ticket_message(
    session: Session,
    ticket: Ticket,
    author: User,
    body: str,
) -> TicketMessage:
    if not body.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message body cannot be empty.",
        )
    now = datetime.now(timezone.utc)

    message = TicketMessage(
        ticket_id=ticket.id,
        author_user_id=author.id,
        body=body,
        created_at=now,
    )

    session.add(message)

    ticket.version += 1
    ticket.last_public_activity_at = now

    event = TicketEvent(
        ticket_id=ticket.id,
        actor_user_id=author.id,
        event_type="message_added",
        details="Public ticket message added.",
        created_at=now,
    )

    session.add(event)

    try:
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise

    session.refresh(message)

    return message