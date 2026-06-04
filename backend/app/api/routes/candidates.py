"""Candidate routes."""

from fastapi import APIRouter

from app.schemas.common import MessageResponse

router = APIRouter()


@router.get("/status", response_model=MessageResponse)
def candidate_status() -> MessageResponse:
    return MessageResponse(message="Candidate module ready")
