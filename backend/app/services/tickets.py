from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import Ticket, TicketEvent, User


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