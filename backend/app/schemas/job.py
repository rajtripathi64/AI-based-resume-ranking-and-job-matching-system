"""Job request and response schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class JobCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=180)
    description: str = Field(..., min_length=20)
    min_experience: Decimal = Field(default=0, ge=0, le=50)
    location: str | None = Field(default=None, max_length=150)
    status: str = Field(default="open", pattern="^(open|closed)$")


class JobUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=180)
    description: str | None = Field(default=None, min_length=20)
    min_experience: Decimal | None = Field(default=None, ge=0, le=50)
    location: str | None = Field(default=None, max_length=150)
    status: str | None = Field(default=None, pattern="^(open|closed)$")


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    required_skills: str | None
    min_experience: Decimal
    location: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
