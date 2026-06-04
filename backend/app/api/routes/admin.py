"""Admin routes for protected user management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.security import hash_password
from app.db.session import get_db
from app.models import CandidateProfile, CompanyProfile, CompanyResume, CompanyResumeMatch, Job, Match, Resume, User
from app.schemas.admin import AdminCreateUserRequest, AdminUserResponse, AdminUserStatusUpdate
from app.schemas.common import MessageResponse

router = APIRouter()


def require_admin(current_user: User) -> None:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can access this route")


def create_profile_for_user(user: User, payload: AdminCreateUserRequest, db: Session) -> None:
    if payload.role == "candidate":
        if not payload.full_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="full_name is required for candidate")
        db.add(CandidateProfile(user_id=user.id, full_name=payload.full_name))
    elif payload.role == "company":
        if not payload.company_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="company_name is required for company")
        db.add(CompanyProfile(user_id=user.id, company_name=payload.company_name))


def delete_candidate_data(candidate_profile_id: int, db: Session) -> None:
    resume_ids = select(Resume.id).where(Resume.candidate_id == candidate_profile_id)
    db.execute(delete(Match).where(Match.resume_id.in_(resume_ids)))
    db.execute(delete(Resume).where(Resume.candidate_id == candidate_profile_id))
    db.execute(delete(CandidateProfile).where(CandidateProfile.id == candidate_profile_id))


def delete_company_data(company_profile_id: int, db: Session) -> None:
    company_resume_ids = select(CompanyResume.id).where(CompanyResume.company_id == company_profile_id)
    job_ids = select(Job.id).where(Job.company_id == company_profile_id)

    db.execute(delete(CompanyResumeMatch).where(CompanyResumeMatch.company_resume_id.in_(company_resume_ids)))
    db.execute(delete(CompanyResumeMatch).where(CompanyResumeMatch.job_id.in_(job_ids)))
    db.execute(delete(Match).where(Match.job_id.in_(job_ids)))
    db.execute(delete(CompanyResume).where(CompanyResume.company_id == company_profile_id))
    db.execute(delete(Job).where(Job.company_id == company_profile_id))
    db.execute(delete(CompanyProfile).where(CompanyProfile.id == company_profile_id))


@router.get("/status", response_model=MessageResponse)
def admin_status(current_user: User = Depends(get_current_user)) -> MessageResponse:
    require_admin(current_user)
    return MessageResponse(message="Admin module ready")


@router.get("/users", response_model=list[AdminUserResponse])
def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AdminUserResponse]:
    require_admin(current_user)
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [AdminUserResponse.model_validate(user) for user in users]


@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminCreateUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    require_admin(current_user)

    existing_user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.flush()
    create_profile_for_user(user, payload, db)
    db.commit()
    db.refresh(user)
    return AdminUserResponse.model_validate(user)


@router.patch("/users/{user_id}/status", response_model=AdminUserResponse)
def update_user_status(
    user_id: int,
    payload: AdminUserStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    require_admin(current_user)
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return AdminUserResponse.model_validate(user)


@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    require_admin(current_user)
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.role == "candidate" and user.candidate_profile:
        delete_candidate_data(user.candidate_profile.id, db)
    elif user.role == "company" and user.company_profile:
        delete_company_data(user.company_profile.id, db)

    db.delete(user)
    db.commit()
    return MessageResponse(message="User deleted successfully")
