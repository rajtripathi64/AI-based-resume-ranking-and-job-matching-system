"""Resume request and response schemas."""

from datetime import datetime

from pydantic import BaseModel


class ResumeResponse(BaseModel):
    id: int
    file_name: str
    parsed_text_preview: str | None
    extracted_skills: str | None
    uploaded_at: datetime


class ResumeDetailResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    parsed_text: str | None
    extracted_skills: str | None
    education: str | None
    experience_summary: str | None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class CompanyResumeResponse(BaseModel):
    id: int
    candidate_name: str
    file_name: str
    parsed_text_preview: str | None
    extracted_skills: str | None
    uploaded_at: datetime
