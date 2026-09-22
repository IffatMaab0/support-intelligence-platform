from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Ticket, TicketMessage, User
from app.routers.auth import (
    get_current_user,
    require_agent,
    require_customer,
    require_manager,
)
from app.schemas import (
    TicketAssignmentRequest,
    TicketCreate,
    TicketListResponse,
    TicketMessageCreate,
    TicketMessageResponse,
    TicketResponse,
)
from app.services.tickets import add_ticket_message, assign_ticket, create_ticket

router = APIRouter(
    prefix="/v1/tickets",
    tags=["tickets"],
)


def to_ticket_response(ticket: Ticket) -> TicketResponse:
    return TicketResponse(
        id=ticket.id,
        reference=f"SUP-{ticket.id:06d}",
        subject=ticket.subject,
        original_message=ticket.original_message,
        status=ticket.status,
        priority=ticket.priority,
        channel=ticket.channel,
        assigned_agent_id=ticket.assigned_agent_id,
        version=ticket.version,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        last_public_activity_at=ticket.last_public_activity_at,
    )


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_ticket(
    data: TicketCreate,
    customer: User = Depends(require_customer),
    session: Session = Depends(get_db),
):
    ticket = create_ticket(
        session=session,
        customer=customer,
        subject=data.subject,
        original_message=data.original_message,
    )

    return to_ticket_response(ticket)


@router.patch(
    "/{ticket_id}/assignment",
    response_model=TicketResponse,
)
def assign_ticket_to_agent(
    ticket_id: int,
    data: TicketAssignmentRequest,
    manager: User = Depends(require_manager),
    session: Session = Depends(get_db),
):
    ticket = (
        session.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    ticket = assign_ticket(
        session=session,
        ticket=ticket,
        manager=manager,
        assigned_agent_id=data.assigned_agent_id,
        expected_version=data.expected_version,
    )

    return to_ticket_response(ticket)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    query = session.query(Ticket).filter(Ticket.id == ticket_id)

    if user.role.value == "customer":
        query = query.filter(Ticket.customer_id == user.id)

    elif user.role.value == "agent":
        query = query.filter(Ticket.assigned_agent_id == user.id)

    elif user.role.value == "manager":
        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    ticket = query.first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return to_ticket_response(ticket)


@router.get("", response_model=TicketListResponse)
def list_tickets(
    search: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    query = session.query(Ticket)

    # 1. Apply ownership scope first
    if user.role.value == "customer":
        query = query.filter(Ticket.customer_id == user.id)

    elif user.role.value == "agent":
        query = query.filter(Ticket.assigned_agent_id == user.id)

    elif user.role.value == "manager":
        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    # 2. Search only inside the allowed scope
    if search:
        search_text = f"%{search}%"
        query = query.filter(
            Ticket.subject.ilike(search_text)
            | Ticket.original_message.ilike(search_text)
        )

    # 3. Count after scope + search
    total = query.count()

    # 4. Stable newest-first ordering + pagination
    tickets = (
        query
        .order_by(Ticket.created_at.desc(), Ticket.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return TicketListResponse(
        items=[to_ticket_response(ticket) for ticket in tickets],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{ticket_id}/messages",
    response_model=list[TicketMessageResponse],
)
def list_ticket_messages(
    ticket_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    query = (
        session.query(Ticket)
        .filter(Ticket.id == ticket_id)
    )

    if user.role.value == "customer":
        query = query.filter(Ticket.customer_id == user.id)

    elif user.role.value == "agent":
        query = query.filter(Ticket.assigned_agent_id == user.id)

    elif user.role.value == "manager":
        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    ticket = query.first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    messages = (
        session.query(TicketMessage, User)
        .join(User, TicketMessage.author_user_id == User.id)
        .filter(TicketMessage.ticket_id == ticket.id)
        .order_by(
            TicketMessage.created_at.asc(),
            TicketMessage.id.asc(),
        )
        .all()
    )

    result = []

    for message, author in messages:
        if user.role.value == "customer":
            author_label = (
                "Customer"
                if author.role.value == "customer"
                else "Support"
            )
        else:
            author_label = author.display_name

        result.append(
            TicketMessageResponse(
                id=message.id,
                ticket_id=message.ticket_id,
                body=message.body,
                created_at=message.created_at,
                author=author_label,
            )
        )

    return result


@router.post(
    "/{ticket_id}/messages",
    response_model=TicketMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket_message(
    ticket_id: int,
    data: TicketMessageCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    query = (
        session.query(Ticket)
        .filter(Ticket.id == ticket_id)
    )

    if user.role.value == "customer":
        query = query.filter(Ticket.customer_id == user.id)

    elif user.role.value == "agent":
        query = query.filter(Ticket.assigned_agent_id == user.id)

    elif user.role.value == "manager":
        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    ticket = query.first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    message = add_ticket_message(
        session=session,
        ticket=ticket,
        author=user,
        body=data.body,
    )

    if user.role.value == "customer":
        author_label = "Customer"
    else:
        author_label = user.display_name

    return TicketMessageResponse(
        id=message.id,
        ticket_id=message.ticket_id,
        body=message.body,
        created_at=message.created_at,
        author=author_label,
    )

