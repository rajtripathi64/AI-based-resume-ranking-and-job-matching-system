"""Company routes."""

from fastapi import APIRouter

from app.schemas.common import MessageResponse

router = APIRouter()


@router.get("/status", response_model=MessageResponse)
def company_status() -> MessageResponse:
    return MessageResponse(message="Company module ready")
