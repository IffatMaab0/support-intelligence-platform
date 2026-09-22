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

    ticket = (
        session.query(Ticket)
        .filter(Ticket.id == ticket.id)
        .with_for_update()
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )

    # Staff cannot reply publicly while the ticket is resolved.
    # They must explicitly reopen it first.
    if ticket.status == "resolved" and author.role.value != "customer":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resolved tickets must be reopened before a staff reply.",
        )

    now = datetime.now(timezone.utc)

    # A customer message on a resolved ticket automatically reopens it.
    if ticket.status == "resolved" and author.role.value == "customer":
        ticket.status = "open"
        ticket.resolved_at = None

        # Keep the assignee only if the current assignee is still active.
        if ticket.assigned_agent_id is not None:
            assigned_agent = (
                session.query(User)
                .filter(User.id == ticket.assigned_agent_id)
                .first()
            )

            if not assigned_agent or not assigned_agent.is_active:
                ticket.assigned_agent_id = None

        ticket.updated_at = now
        ticket.version += 1

        reopen_event = TicketEvent(
            ticket_id=ticket.id,
            actor_user_id=author.id,
            event_type="status_changed",
            details=(
                "Ticket automatically reopened because the customer "
                "sent a new message."
            ),
            created_at=now,
        )

        session.add(reopen_event)

    message = TicketMessage(
        ticket_id=ticket.id,
        author_user_id=author.id,
        body=body,
        created_at=now,
    )

    session.add(message)

    ticket.version += 1
    ticket.updated_at = now
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


def update_ticket_status(
    session: Session,
    ticket: Ticket,
    actor: User,
    new_status: str,
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
            detail="Ticket not found.",
        )

    if ticket.version != expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ticket has changed. Please refresh and try again.",
        )

    valid_statuses = {"open", "in_review", "resolved"}

    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ticket status.",
        )

    if new_status == ticket.status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ticket is already in this status.",
        )

    allowed_transitions = {
        "open": {"in_review", "resolved"},
        "in_review": {"open", "resolved"},
        "resolved": {"open"},
    }

    if new_status not in allowed_transitions[ticket.status]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Cannot change ticket status from "
                f"{ticket.status} to {new_status}."
            ),
        )

    if new_status == "in_review" and ticket.assigned_agent_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A ticket must have a current assignee before review.",
        )

    if new_status == "resolved":
        newest_customer_message = (
            session.query(TicketMessage)
            .join(User, TicketMessage.author_user_id == User.id)
            .filter(
                TicketMessage.ticket_id == ticket.id,
                User.role == "customer",
            )
            .order_by(
                TicketMessage.created_at.desc(),
                TicketMessage.id.desc(),
            )
            .first()
        )

        if newest_customer_message:
            staff_reply = (
                session.query(TicketMessage)
                .join(User, TicketMessage.author_user_id == User.id)
                .filter(
                    TicketMessage.ticket_id == ticket.id,
                    User.role.in_(["agent", "manager"]),
                    TicketMessage.created_at > newest_customer_message.created_at,
                )
                .order_by(
                    TicketMessage.created_at.desc(),
                    TicketMessage.id.desc(),
                )
                .first()
            )
        else:
            staff_reply = (
                session.query(TicketMessage)
                .join(User, TicketMessage.author_user_id == User.id)
                .filter(
                    TicketMessage.ticket_id == ticket.id,
                    User.role.in_(["agent", "manager"]),
                )
                .order_by(
                    TicketMessage.created_at.desc(),
                    TicketMessage.id.desc(),
                )
                .first()
            )

        if not staff_reply:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A staff public reply is required before resolving.",
            )

    now = datetime.now(timezone.utc)
    previous_status = ticket.status

    ticket.status = new_status
    ticket.updated_at = now
    ticket.version += 1

    if new_status == "resolved":
        ticket.resolved_at = now

    elif previous_status == "resolved" and new_status == "open":
        ticket.resolved_at = None

        if ticket.assigned_agent_id is not None:
            assigned_agent = (
                session.query(User)
                .filter(User.id == ticket.assigned_agent_id)
                .first()
            )

            if not assigned_agent or not assigned_agent.is_active:
                ticket.assigned_agent_id = None

    event = TicketEvent(
        ticket_id=ticket.id,
        actor_user_id=actor.id,
        event_type="status_changed",
        details=(
            f"Ticket status changed from {previous_status} "
            f"to {new_status} by {actor.display_name}."
        ),
        created_at=now,
    )

    session.add(event)
    session.commit()
    session.refresh(ticket)

    return ticket


def update_ticket_priority(
    session: Session,
    ticket: Ticket,
    actor: User,
    new_priority: str,
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
            detail="Ticket not found.",
        )

    if ticket.version != expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ticket has changed. Please refresh and try again.",
        )

    valid_priorities = {"low", "normal", "high"}

    if new_priority not in valid_priorities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ticket priority.",
        )

    if new_priority == ticket.priority:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ticket already has this priority.",
        )

    now = datetime.now(timezone.utc)
    previous_priority = ticket.priority

    ticket.priority = new_priority
    ticket.updated_at = now
    ticket.version += 1

    event = TicketEvent(
        ticket_id=ticket.id,
        actor_user_id=actor.id,
        event_type="priority_changed",
        details=(
            f"Ticket priority changed from {previous_priority} "
            f"to {new_priority} by {actor.display_name}."
        ),
        created_at=now,
    )

    session.add(event)
    session.commit()
    session.refresh(ticket)

    return ticket