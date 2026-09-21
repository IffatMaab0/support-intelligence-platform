from uuid import UUID

from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    expires_at: str


class CurrentUserResponse(BaseModel):
    id: UUID
    email: EmailStr
    display_name: str
    role: str



class TicketCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str = Field(min_length=5, max_length=160)
    original_message: str = Field(min_length=10, max_length=5000)


class TicketResponse(BaseModel):
    id: int
    reference: str
    subject: str
    original_message: str
    status: str
    priority: str
    channel: str
    assigned_agent_id: UUID | None
    version: int
    created_at: datetime
    updated_at: datetime
    last_public_activity_at: datetime    


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    total: int
    skip: int
    limit: int    


class TicketAssignmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assigned_agent_id: UUID | None = None
    expected_version: int = Field(ge=1)    