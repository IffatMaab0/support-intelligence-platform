import hashlib
import json
from typing import Any

from sqlalchemy.orm import Session
from app.models import IdempotencyRecord
from sqlalchemy.exc import IntegrityError


def canonical_request_hash(payload: Any) -> str:
    canonical_json = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()

def find_idempotency_record(
    session: Session,
    actor_user_id,
    operation: str,
    idempotency_key: str,
):
    return (
        session.query(IdempotencyRecord)
        .filter(
            IdempotencyRecord.actor_user_id == actor_user_id,
            IdempotencyRecord.operation == operation,
            IdempotencyRecord.idempotency_key == idempotency_key,
        )
        .first()
    )

def create_idempotency_record(
    session: Session,
    actor_user_id,
    operation: str,
    idempotency_key: str,
    request_hash: str,
):
    record = IdempotencyRecord(
        actor_user_id=actor_user_id,
        operation=operation,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        response_body={},
        response_status=0,
    )

    session.add(record)
    session.flush()

    return record

def validate_idempotency_request(
    record,
    request_hash: str,
):
    if record.request_hash != request_hash:
        raise ValueError(
            "Idempotency key was already used with a different request."
        )

    return record
    
def reserve_idempotency_record(
    session: Session,
    actor_user_id,
    operation: str,
    idempotency_key: str,
    request_hash: str,
):
    record = IdempotencyRecord(
        actor_user_id=actor_user_id,
        operation=operation,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        response_body={},
        response_status=0,
    )

    session.add(record)

    try:
        session.flush()
        return record, True
    except IntegrityError as exc:
        # PostgreSQL identifies which constraint caused the failure.
        constraint_name = getattr(
            getattr(exc.orig, "diag", None),
            "constraint_name",
            None,
        )

        session.rollback()

        if constraint_name != "uq_idempotency_actor_operation_key":
            raise

        existing_record = find_idempotency_record(
            session=session,
            actor_user_id=actor_user_id,
            operation=operation,
            idempotency_key=idempotency_key,
        )

        if existing_record is None:
            raise

        return existing_record, False

