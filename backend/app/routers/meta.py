from fastapi import APIRouter

router = APIRouter(
    prefix="/v1/meta",
    tags=["meta"],
)


@router.get("")
def get_meta():
    return {
        "ticket_statuses": ["open", "resolved"],
        "ticket_priorities": ["normal", "high", "urgent"],
        "ticket_channels": ["web_form"],
    }