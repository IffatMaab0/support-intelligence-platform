import hashlib
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import KnowledgeDocument, User


def create_document(
    session: Session,
    manager: User,
    policy_key: str,
    title: str,
    topic: str,
    audience: str,
    body: str,
) -> KnowledgeDocument:
    if audience not in {"public", "internal"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document audience.",
        )

    now = datetime.now(timezone.utc)

    content_sha256 = hashlib.sha256(
        body.encode("utf-8")
    ).hexdigest()

    document = KnowledgeDocument(
        policy_key=policy_key,
        title=title,
        topic=topic,
        audience=audience,
        body=body,
        content_sha256=content_sha256,
        status="draft",
        created_by=manager.id,
        created_at=now,
        updated_at=now,
        version=1,
    )

    session.add(document)

    try:
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise

    session.refresh(document)

    return document


def update_document_status(
    session: Session,
    document: KnowledgeDocument,
    manager: User,
    new_status: str,
    expected_version: int,
) -> KnowledgeDocument:
    document = (
        session.query(KnowledgeDocument)
        .filter(KnowledgeDocument.id == document.id)
        .with_for_update()
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    if document.version != expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document has changed. Please refresh and try again.",
        )

    valid_statuses = {"active", "archived"}

    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document status.",
        )

    if new_status == document.status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document is already in this status.",
        )

    if document.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft documents can be activated or archived.",
        )

    now = datetime.now(timezone.utc)

    if new_status == "active":
        active_document = (
            session.query(KnowledgeDocument)
            .filter(
                KnowledgeDocument.policy_key == document.policy_key,
                KnowledgeDocument.status == "active",
                KnowledgeDocument.id != document.id,
            )
            .with_for_update()
            .first()
        )

        if active_document:
            active_document.status = "archived"
            active_document.updated_at = now
            active_document.version += 1

        document.status = "active"

    elif new_status == "archived":
        document.status = "archived"

    document.updated_at = now
    document.version += 1

    try:
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise

    session.refresh(document)

    return document