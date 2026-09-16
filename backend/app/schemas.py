from uuid import UUID

from pydantic import BaseModel, EmailStr


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