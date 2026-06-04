"""Admin user-management schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class AdminUserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminCreateUserRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    role: str = Field(..., pattern="^(candidate|company|admin)$")
    full_name: str | None = Field(default=None, max_length=150)
    company_name: str | None = Field(default=None, max_length=180)


class AdminUserStatusUpdate(BaseModel):
    is_active: bool
