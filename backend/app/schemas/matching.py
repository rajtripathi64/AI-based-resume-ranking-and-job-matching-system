"""Matching response schemas."""

from pydantic import BaseModel


class CandidateMatchResponse(BaseModel):
    resume_id: int
    candidate_name: str
    file_name: str
    similarity_score: float
    skill_score: float
    final_score: float
    extracted_skills: str | None
    explanation: str


class JobMatchResponse(BaseModel):
    job_id: int
    title: str
    company_name: str
    similarity_score: float
    skill_score: float
    final_score: float
    required_skills: str | None
    explanation: str


class MatchingRunResponse(BaseModel):
    method: str
    results: list[CandidateMatchResponse] | list[JobMatchResponse]
