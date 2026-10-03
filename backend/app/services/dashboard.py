from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from app.models import Ticket, TicketEvent, User


def get_dashboard_summary(session: Session) -> dict:
    now = datetime.now(timezone.utc)

    total = session.query(func.count(Ticket.id)).scalar() or 0

    open_count = (
        session.query(func.count(Ticket.id))
        .filter(Ticket.status == "open")
        .scalar()
        or 0
    )

    in_review_count = (
        session.query(func.count(Ticket.id))
        .filter(Ticket.status == "in_review")
        .scalar()
        or 0
    )

    resolved_count = (
        session.query(func.count(Ticket.id))
        .filter(Ticket.status == "resolved")
        .scalar()
        or 0
    )

    unassigned_active = (
        session.query(func.count(Ticket.id))
        .filter(
            Ticket.status.in_(["open", "in_review"]),
            Ticket.assigned_agent_id.is_(None),
        )
        .scalar()
        or 0
    )

    priority_rows = (
        session.query(Ticket.priority, func.count(Ticket.id))
        .group_by(Ticket.priority)
        .all()
    )

    priority_counts = {
        "low": 0,
        "normal": 0,
        "high": 0,
    }

    for priority, count in priority_rows:
        if priority in priority_counts:
            priority_counts[priority] = count

    agents = (
        session.query(User)
        .filter(User.role == "agent", User.is_active.is_(True))
        .order_by(User.display_name)
        .all()
    )

    workload = []

    for agent in agents:
        open_assigned = (
            session.query(func.count(Ticket.id))
            .filter(
                Ticket.assigned_agent_id == agent.id,
                Ticket.status == "open",
            )
            .scalar()
            or 0
        )

        in_review_assigned = (
            session.query(func.count(Ticket.id))
            .filter(
                Ticket.assigned_agent_id == agent.id,
                Ticket.status == "in_review",
            )
            .scalar()
            or 0
        )

        resolved_assigned = (
            session.query(func.count(Ticket.id))
            .filter(
                Ticket.assigned_agent_id == agent.id,
                Ticket.status == "resolved",
            )
            .scalar()
            or 0
        )

        workload.append(
            {
                "agent_id": str(agent.id),
                "agent": agent.display_name,
                "open": open_assigned,
                "in_review": in_review_assigned,
                "resolved": resolved_assigned,
            }
        )

    unassigned_resolved = (
        session.query(func.count(Ticket.id))
        .filter(
            Ticket.assigned_agent_id.is_(None),
            Ticket.status == "resolved",
        )
        .scalar()
        or 0
    )

    workload.append(
        {
            "agent_id": None,
            "agent": "Unassigned",
            "open": unassigned_active,
            "in_review": 0,
            "resolved": unassigned_resolved,
        }
    )

    events = (
        session.query(TicketEvent, Ticket, User)
        .join(Ticket, Ticket.id == TicketEvent.ticket_id)
        .join(User, User.id == TicketEvent.actor_user_id)
        .order_by(TicketEvent.created_at.desc(), TicketEvent.id.desc())
        .limit(5)
        .all()
    )

    recent_activity = []

    for event, ticket, actor in events:
        if event.event_type == "note_added":
            description = "Private note added."
        elif event.event_type == "message_added":
            description = "Ticket message added."
        elif event.event_type == "assignment_changed":
            description = event.details
        elif event.event_type == "status_changed":
            description = event.details
        elif event.event_type == "priority_changed":
            description = event.details
        elif event.event_type == "created":
            description = "Ticket created."
        else:
            description = "Ticket activity recorded."

        recent_activity.append(
            {
                "event_type": event.event_type,
                "ticket_id": ticket.id,
                "ticket_reference": f"SUP-{ticket.id:06d}",
                "actor": actor.display_name,
                "timestamp": event.created_at,
                "description": description,
            }
        )

    return {
        "data_as_of": now,
        "metrics": {
            "total": total,
            "open": open_count,
            "in_review": in_review_count,
            "resolved": resolved_count,
            "unassigned_active": unassigned_active,
        },
        "priority": priority_counts,
        "workload": workload,
        "recent_activity": recent_activity,
    }