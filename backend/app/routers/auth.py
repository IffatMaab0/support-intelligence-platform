from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import AuthSession, User
from app.schemas import CurrentUserResponse, LoginRequest, LoginResponse
from app.security import hash_session_token
from app.services.auth import authenticate_user


router = APIRouter(prefix="/v1/auth", tags=["auth"])


def get_current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_db),
) -> User:

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = authorization.removeprefix("Bearer ").strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token_hash = hash_session_token(token)

    auth_session = session.query(AuthSession).filter(
        AuthSession.session_token_hash == token_hash
    ).first()

    if not auth_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    now = datetime.now(timezone.utc)

    if auth_session.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    if auth_session.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user = session.query(User).filter(
        User.id == auth_session.user_id
    ).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return user


@router.post("/login", response_model=LoginResponse)
def login(
    data: LoginRequest,
    session: Session = Depends(get_db),
):
    _, token, expires_at = authenticate_user(
        session,
        data.email,
        data.password,
    )

    return LoginResponse(
        access_token=token,
        expires_at=expires_at.isoformat(),
    )


@router.get("/me", response_model=CurrentUserResponse)
def me(
    user: User = Depends(get_current_user),
):
    return CurrentUserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role.value,
    )


@router.post("/logout")
def logout(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = authorization.removeprefix("Bearer ").strip()
    token_hash = hash_session_token(token)

    auth_session = session.query(AuthSession).filter(
        AuthSession.session_token_hash == token_hash
    ).first()

    if not auth_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    if auth_session.revoked_at is None:
        auth_session.revoked_at = datetime.now(timezone.utc)
        session.commit()

    return {"status": "logged_out"}

def require_customer(
    user: User = Depends(get_current_user),
) -> User:
    if user.role.value != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )
    return user


def require_agent(
    user: User = Depends(get_current_user),
) -> User:
    if user.role.value != "agent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )
    return user


def require_manager(
    user: User = Depends(get_current_user),
) -> User:
    if user.role.value != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )
    return user