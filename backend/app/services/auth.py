from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import AuthSession, User
from app.security import (
    generate_session_token,
    hash_session_token,
    verify_password,
)


SESSION_DURATION = timedelta(minutes=60)


def authenticate_user(
    session: Session,
    email: str,
    password: str,
) -> tuple[User, str, datetime]:

    user = session.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = generate_session_token()
    token_hash = hash_session_token(token)

    expires_at = datetime.now(timezone.utc) + SESSION_DURATION

    auth_session = AuthSession(
        user_id=user.id,
        session_token_hash=token_hash,
        expires_at=expires_at,
    )

    session.add(auth_session)
    session.commit()

    return user, token, expires_at