"""Job description routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import CompanyProfile, Job, User
from app.schemas.job import JobCreateRequest, JobResponse, JobUpdateRequest
from app.services.job_parser import clean_job_description, extract_required_skills

router = APIRouter()


def get_company_profile(db: Session, user: User) -> CompanyProfile:
    if user.role != "company":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company users can manage jobs",
        )

    profile = db.scalar(select(CompanyProfile).where(CompanyProfile.user_id == user.id))
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )
    return profile


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobResponse:
    company = get_company_profile(db, current_user)
    description = clean_job_description(payload.description)
    required_skills = ", ".join(extract_required_skills(description))

    job = Job(
        company_id=company.id,
        title=payload.title,
        description=description,
        required_skills=required_skills,
        min_experience=payload.min_experience,
        location=payload.location,
        status=payload.status,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return JobResponse.model_validate(job)


@router.get("/mine", response_model=list[JobResponse])
def list_my_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[JobResponse]:
    company = get_company_profile(db, current_user)
    jobs = db.scalars(
        select(Job).where(Job.company_id == company.id).order_by(Job.created_at.desc())
    ).all()
    return [JobResponse.model_validate(job) for job in jobs]


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobResponse:
    company = get_company_profile(db, current_user)
    job = db.get(Job, job_id)
    if job is None or job.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobResponse.model_validate(job)


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    payload: JobUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobResponse:
    company = get_company_profile(db, current_user)
    job = db.get(Job, job_id)
    if job is None or job.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "description" in update_data:
        update_data["description"] = clean_job_description(update_data["description"])
        update_data["required_skills"] = ", ".join(extract_required_skills(update_data["description"]))

    for key, value in update_data.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return JobResponse.model_validate(job)


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    company = get_company_profile(db, current_user)
    job = db.get(Job, job_id)
    if job is None or job.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}
