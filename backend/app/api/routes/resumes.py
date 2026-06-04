"""Resume upload and parsing routes."""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import CandidateProfile, CompanyProfile, CompanyResume, Resume, User
from app.schemas.resume import CompanyResumeResponse, ResumeDetailResponse, ResumeResponse
from app.services.resume_parser import SUPPORTED_EXTENSIONS, extract_basic_skills, parse_resume_file

router = APIRouter()
UPLOAD_DIR = Path("uploads/resumes")


def get_candidate_profile(db: Session, user: User) -> CandidateProfile:
    if user.role != "candidate":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can upload resumes")
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate profile not found")
    return profile


def get_company_profile(db: Session, user: User) -> CompanyProfile:
    if user.role != "company":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only company users can upload company resume pool files")
    profile = db.scalar(select(CompanyProfile).where(CompanyProfile.user_id == user.id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found")
    return profile


def validate_extension(original_name: str) -> str:
    extension = Path(original_name).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF, DOCX, and TXT resumes are supported")
    return extension


async def save_uploaded_file(file: UploadFile, prefix: str) -> tuple[str, Path]:
    original_name = file.filename or "resume"
    extension = validate_extension(original_name)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = UPLOAD_DIR / f"{prefix}_{uuid4().hex}{extension}"
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
    saved_path.write_bytes(content)
    return original_name, saved_path


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeResponse:
    candidate = get_candidate_profile(db, current_user)
    original_name, saved_path = await save_uploaded_file(file, str(candidate.id))

    try:
        parsed_text = parse_resume_file(saved_path)
    except Exception as exc:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume parsing failed. Please upload a readable PDF, DOCX, or TXT file.") from exc

    resume = Resume(
        candidate_id=candidate.id,
        file_name=original_name,
        file_path=str(saved_path),
        parsed_text=parsed_text,
        extracted_skills=", ".join(extract_basic_skills(parsed_text)),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return ResumeResponse(
        id=resume.id,
        file_name=resume.file_name,
        parsed_text_preview=(resume.parsed_text or "")[:350],
        extracted_skills=resume.extracted_skills,
        uploaded_at=resume.uploaded_at,
    )


@router.get("/mine", response_model=list[ResumeResponse])
def list_my_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ResumeResponse]:
    candidate = get_candidate_profile(db, current_user)
    resumes = db.scalars(select(Resume).where(Resume.candidate_id == candidate.id).order_by(Resume.uploaded_at.desc())).all()
    return [
        ResumeResponse(
            id=resume.id,
            file_name=resume.file_name,
            parsed_text_preview=(resume.parsed_text or "")[:350],
            extracted_skills=resume.extracted_skills,
            uploaded_at=resume.uploaded_at,
        )
        for resume in resumes
    ]


@router.post("/company-pool/upload", response_model=CompanyResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_company_resume(
    candidate_name: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompanyResumeResponse:
    company = get_company_profile(db, current_user)
    original_name, saved_path = await save_uploaded_file(file, f"company_{company.id}")

    try:
        parsed_text = parse_resume_file(saved_path)
    except Exception as exc:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume parsing failed. Please upload a readable PDF, DOCX, or TXT file.") from exc

    resume = CompanyResume(
        company_id=company.id,
        candidate_name=candidate_name,
        file_name=original_name,
        file_path=str(saved_path),
        parsed_text=parsed_text,
        extracted_skills=", ".join(extract_basic_skills(parsed_text)),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return CompanyResumeResponse(
        id=resume.id,
        candidate_name=resume.candidate_name,
        file_name=resume.file_name,
        parsed_text_preview=(resume.parsed_text or "")[:350],
        extracted_skills=resume.extracted_skills,
        uploaded_at=resume.uploaded_at,
    )


@router.get("/company-pool", response_model=list[CompanyResumeResponse])
def list_company_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[CompanyResumeResponse]:
    company = get_company_profile(db, current_user)
    resumes = db.scalars(select(CompanyResume).where(CompanyResume.company_id == company.id).order_by(CompanyResume.uploaded_at.desc())).all()
    return [
        CompanyResumeResponse(
            id=resume.id,
            candidate_name=resume.candidate_name,
            file_name=resume.file_name,
            parsed_text_preview=(resume.parsed_text or "")[:350],
            extracted_skills=resume.extracted_skills,
            uploaded_at=resume.uploaded_at,
        )
        for resume in resumes
    ]


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeDetailResponse:
    candidate = get_candidate_profile(db, current_user)
    resume = db.get(Resume, resume_id)
    if resume is None or resume.candidate_id != candidate.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return ResumeDetailResponse.model_validate(resume)
