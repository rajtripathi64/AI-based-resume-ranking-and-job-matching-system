"""Matching routes for SBERT resume-job ranking."""

from decimal import Decimal
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import (
    CandidateProfile,
    CompanyProfile,
    CompanyResume,
    CompanyResumeMatch,
    Job,
    Match,
    Resume,
    User,
)
from app.schemas.matching import CandidateMatchResponse, JobMatchResponse, MatchingRunResponse
from app.services.embedding_service import section_weighted_similarity_percentage, skill_score
from app.services.job_parser import clean_job_description, extract_required_skills
from app.services.ranking_model import ranking_model_score
from app.services.resume_parser import extract_basic_skills, extract_candidate_name, extract_email, parse_resume_file
from app.services.skill_normalization import skill_set

router = APIRouter()


def decimal_score(value: float) -> Decimal:
    return Decimal(str(round(value, 2)))



def matched_skill_list(resume_skills: str | None, job_skills: str | None) -> list[str]:
    return sorted(skill_set(resume_skills) & skill_set(job_skills))

def get_candidate_profile(db: Session, user: User) -> CandidateProfile:
    if user.role != "candidate":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can run this matching flow")
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate profile not found")
    return profile


def get_company_profile(db: Session, user: User) -> CompanyProfile:
    if user.role != "company":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only companies can run this matching flow")
    profile = db.scalar(select(CompanyProfile).where(CompanyProfile.user_id == user.id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found")
    return profile


@router.post("/job-to-company-resumes/{job_id}", response_model=MatchingRunResponse)
def rank_company_resumes_for_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MatchingRunResponse:
    company = get_company_profile(db, current_user)
    job = db.get(Job, job_id)
    if job is None or job.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    resumes = db.scalars(select(CompanyResume).where(CompanyResume.company_id == company.id)).all()
    results: list[CandidateMatchResponse] = []
    method = "SBERT all-MiniLM-L6-v2"

    for resume in resumes:
        similarity, method = section_weighted_similarity_percentage(resume.parsed_text or "", job.description or "")
        skills = skill_score(resume.extracted_skills, job.required_skills)
        final_score, ranking_method = ranking_model_score(resume.parsed_text or "", job.description or "", resume.extracted_skills, job.required_skills, similarity, skills)
        explanation = f"Semantic similarity {similarity}%, skill overlap {skills}%, {ranking_method} score {final_score}%."

        existing = db.scalar(
            select(CompanyResumeMatch).where(
                CompanyResumeMatch.company_resume_id == resume.id,
                CompanyResumeMatch.job_id == job.id,
            )
        )
        if existing is None:
            existing = CompanyResumeMatch(company_resume_id=resume.id, job_id=job.id)
            db.add(existing)

        existing.similarity_score = decimal_score(similarity)
        existing.skill_score = decimal_score(skills)
        existing.final_score = decimal_score(final_score)
        existing.explanation = explanation

        results.append(
            CandidateMatchResponse(
                resume_id=resume.id,
                candidate_name=resume.candidate_name,
                file_name=resume.file_name,
                similarity_score=similarity,
                skill_score=skills,
                final_score=final_score,
                extracted_skills=resume.extracted_skills,
                explanation=explanation,
            )
        )

    db.commit()
    results.sort(key=lambda item: item.final_score, reverse=True)
    return MatchingRunResponse(method=f"{method} + {ranking_method}", results=results)


@router.post("/resume-to-jobs/{resume_id}", response_model=MatchingRunResponse)
def rank_jobs_for_candidate_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MatchingRunResponse:
    candidate = get_candidate_profile(db, current_user)
    resume = db.get(Resume, resume_id)
    if resume is None or resume.candidate_id != candidate.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    jobs = db.scalars(select(Job).where(Job.status == "open")).all()
    results: list[JobMatchResponse] = []
    method = "SBERT all-MiniLM-L6-v2"

    for job in jobs:
        similarity, method = section_weighted_similarity_percentage(resume.parsed_text or "", job.description or "")
        skills = skill_score(resume.extracted_skills, job.required_skills)
        final_score, ranking_method = ranking_model_score(resume.parsed_text or "", job.description or "", resume.extracted_skills, job.required_skills, similarity, skills)
        explanation = f"Semantic similarity {similarity}%, skill overlap {skills}%, {ranking_method} score {final_score}%."

        existing = db.scalar(select(Match).where(Match.resume_id == resume.id, Match.job_id == job.id))
        if existing is None:
            existing = Match(resume_id=resume.id, job_id=job.id)
            db.add(existing)

        existing.similarity_score = decimal_score(similarity)
        existing.skill_score = decimal_score(skills)
        existing.experience_score = decimal_score(0)
        existing.final_score = decimal_score(final_score)
        existing.explanation = explanation

        company_name = job.company.company_name if job.company else "Company"
        results.append(
            JobMatchResponse(
                job_id=job.id,
                title=job.title,
                company_name=company_name,
                similarity_score=similarity,
                skill_score=skills,
                final_score=final_score,
                required_skills=job.required_skills,
                explanation=explanation,
            )
        )

    db.commit()
    results.sort(key=lambda item: item.final_score, reverse=True)
    return MatchingRunResponse(method=f"{method} + {ranking_method}", results=results)


def parse_upload_to_text(upload: UploadFile) -> str:
    suffix = Path(upload.filename or "upload.txt").suffix or ".txt"
    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_path = Path(temp_file.name)
        temp_file.write(upload.file.read())
    try:
        return parse_resume_file(temp_path)
    finally:
        temp_path.unlink(missing_ok=True)


def get_job_description_text(jd_text: str | None, jd_file: UploadFile | None) -> str:
    if jd_text and jd_text.strip():
        return clean_job_description(jd_text)
    if jd_file is not None:
        return clean_job_description(parse_upload_to_text(jd_file))
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide job description text or upload a JD file")


@router.post("/instant-candidate")
def instant_candidate_match(
    resume_file: UploadFile = File(...),
    jd_text: str | None = Form(default=None),
    jd_file: UploadFile | None = File(default=None),
    current_user: User = Depends(get_current_user),
) -> dict:
    if current_user.role != "candidate":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can run this matching flow")
    resume_text = parse_upload_to_text(resume_file)
    resume_skills = ", ".join(extract_basic_skills(resume_text))
    job_text = get_job_description_text(jd_text, jd_file)
    job_skills = ", ".join(extract_required_skills(job_text))

    similarity, method = section_weighted_similarity_percentage(resume_text, job_text)
    skills = skill_score(resume_skills, job_skills)
    final_score, ranking_method = ranking_model_score(resume_text, job_text, resume_skills, job_skills, similarity, skills)

    return {
        "method": f"{method} + {ranking_method}",
        "match": {
            "file_name": resume_file.filename,
            "final_score": final_score,
            "similarity_score": similarity,
            "skill_score": skills,
            "matched_skills": matched_skill_list(resume_skills, job_skills),
            "matched_skills_text": ", ".join(matched_skill_list(resume_skills, job_skills)),
            "resume_skills": resume_skills,
            "job_skills": job_skills,
            "explanation": f"Uploaded resume matches the provided JD by {final_score}% using {ranking_method}.",
        },
    }


@router.post("/instant-company")
def instant_company_match(
    candidate_names: str = Form(...),
    jd_text: str | None = Form(default=None),
    jd_file: UploadFile | None = File(default=None),
    resume_files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    get_company_profile(db, current_user)
    job_text = get_job_description_text(jd_text, jd_file)
    job_skills = ", ".join(extract_required_skills(job_text))
    names = [name.strip() for name in candidate_names.split(",") if name.strip()]

    results = []
    method = "SBERT all-MiniLM-L6-v2"
    for index, upload in enumerate(resume_files):
        resume_text = parse_upload_to_text(upload)
        extracted_name = extract_candidate_name(resume_text)
        extracted_email = extract_email(resume_text)
        typed_name = names[index] if index < len(names) else ""
        candidate_name = extracted_name or typed_name or f"Candidate {index + 1}"
        resume_skills = ", ".join(extract_basic_skills(resume_text))
        similarity, method = section_weighted_similarity_percentage(resume_text, job_text)
        skills = skill_score(resume_skills, job_skills)
        final_score, ranking_method = ranking_model_score(resume_text, job_text, resume_skills, job_skills, similarity, skills)
        matched_skills = matched_skill_list(resume_skills, job_skills)
        results.append({
            "candidate_name": candidate_name,
            "file_name": upload.filename,
            "email": extracted_email,
            "final_score": final_score,
            "similarity_score": similarity,
            "skill_score": skills,
            "matched_skills": matched_skills,
            "matched_skills_text": ", ".join(matched_skills),
            "extracted_skills": resume_skills,
            "explanation": f"{candidate_name} matches the uploaded JD by {final_score}% using {ranking_method}.",
        })

    results.sort(key=lambda item: item["final_score"], reverse=True)
    return {"method": f"{method} + {ranking_method}", "job_skills": job_skills, "results": results}



