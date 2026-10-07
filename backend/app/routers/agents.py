from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
from app.routers.auth import require_manager
from app.services.agents import create_agent, list_agents, update_agent
from app.schemas import AgentCreate, AgentResponse, AgentUpdate


router = APIRouter(
    prefix="/v1/admin/agents",
    tags=["agents"],
)


@router.get("")
def get_agents(
    session: Session = Depends(get_db),
    _manager=Depends(require_manager),
):
    return list_agents(session)

@router.post("", response_model=AgentResponse, status_code=201)
def create_agent_account(
    data: AgentCreate,
    session: Session = Depends(get_db),
    _manager=Depends(require_manager),
):
    agent = create_agent(session, data)

    return AgentResponse(
        id=agent.id,
        display_name=agent.display_name,
        email=agent.email,
        is_active=agent.is_active,
        version=agent.version,
    )

@router.patch("/{agent_id}", response_model=AgentResponse)
def edit_agent(
    agent_id: UUID,
    data: AgentUpdate,
    session: Session = Depends(get_db),
    _manager=Depends(require_manager),
):
    agent = update_agent(session, agent_id, data)

    return AgentResponse(
        id=agent.id,
        display_name=agent.display_name,
        email=agent.email,
        is_active=agent.is_active,
        version=agent.version,
    )