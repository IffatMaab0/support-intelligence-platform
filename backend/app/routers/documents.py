
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import KnowledgeDocument
from app.schemas import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentListResponse,
    KnowledgeDocumentResponse,
    KnowledgeDocumentStatusUpdateRequest,
)
from app.routers.auth import get_current_user, require_manager


router = APIRouter(
    prefix="/v1/documents",
    tags=["documents"],
)


def to_document_response(
    document: KnowledgeDocument,
) -> KnowledgeDocumentResponse:
    return KnowledgeDocumentResponse(
        id=document.id,
        policy_key=document.policy_key,
        title=document.title,
        topic=document.topic,
        audience=document.audience,
        body=document.body,
        content_sha256=document.content_sha256,
        status=document.status,
        created_by=document.created_by,
        created_at=document.created_at,
        updated_at=document.updated_at,
        version=document.version,
    )


@router.get("", response_model=KnowledgeDocumentListResponse)
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = session.query(KnowledgeDocument)

    if user.role.value == "customer":
        query = query.filter(
            KnowledgeDocument.audience == "public",
            KnowledgeDocument.status == "active",
        )

    elif user.role.value == "agent":
        query = query.filter(
            KnowledgeDocument.status == "active",
        )

    elif user.role.value == "manager":
        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions.",
        )

    total = query.count()

    documents = (
        query.order_by(
            KnowledgeDocument.updated_at.desc(),
            KnowledgeDocument.id.desc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return KnowledgeDocumentListResponse(
        items=[
            to_document_response(document)
            for document in documents
        ],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=KnowledgeDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    payload: KnowledgeDocumentCreate,
    session: Session = Depends(get_db),
    manager=Depends(require_manager),
):
    from app.services.documents import create_document as create_document_service

    document = create_document_service(
        session=session,
        manager=manager,
        policy_key=payload.policy_key,
        title=payload.title,
        topic=payload.topic,
        audience=payload.audience,
        body=payload.body,
    )

    return to_document_response(document)


@router.get(
    "/{document_id}",
    response_model=KnowledgeDocumentResponse,
)
def get_document(
    document_id: int,
    session: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = session.query(KnowledgeDocument).filter(
        KnowledgeDocument.id == document_id
    )

    if user.role.value == "customer":
        query = query.filter(
            KnowledgeDocument.audience == "public",
            KnowledgeDocument.status == "active",
        )

    elif user.role.value == "agent":
        query = query.filter(
            KnowledgeDocument.status == "active",
        )

    elif user.role.value == "manager":
        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions.",
        )

    document = query.first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return to_document_response(document)


@router.patch(
    "/{document_id}/status",
    response_model=KnowledgeDocumentResponse,
)
def update_document_status(
    document_id: int,
    payload: KnowledgeDocumentStatusUpdateRequest,
    session: Session = Depends(get_db),
    manager=Depends(require_manager),
):
    from app.services.documents import update_document_status

    document = (
        session.query(KnowledgeDocument)
        .filter(KnowledgeDocument.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    document = update_document_status(
        session=session,
        document=document,
        manager=manager,
        new_status=payload.status,
        expected_version=payload.expected_version,
    )

    return to_document_response(document)

