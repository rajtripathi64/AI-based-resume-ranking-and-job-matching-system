"""Database models for the resume screening system.

The models match the SQL Server schema in database/02_schema.sql. The schema is
kept simple so joins between users, profiles, resumes, jobs, and matches are easy
to explain and debug.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, UnicodeText, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    candidate_profile: Mapped["CandidateProfile"] = relationship(back_populates="user", uselist=False)
    company_profile: Mapped["CompanyProfile"] = relationship(back_populates="user", uselist=False)


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    location: Mapped[str | None] = mapped_column(String(150))
    experience_years: Mapped[Decimal] = mapped_column(Numeric(4, 1), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    user: Mapped[User] = relationship(back_populates="candidate_profile")
    resumes: Mapped[list["Resume"]] = relationship(back_populates="candidate")


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    company_name: Mapped[str] = mapped_column(String(180), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(120))
    website: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    user: Mapped[User] = relationship(back_populates="company_profile")
    jobs: Mapped[list["Job"]] = relationship(back_populates="company")
    company_resumes: Mapped[list["CompanyResume"]] = relationship(back_populates="company")


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidate_profiles.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    parsed_text: Mapped[str | None] = mapped_column(UnicodeText)
    extracted_skills: Mapped[str | None] = mapped_column(UnicodeText)
    education: Mapped[str | None] = mapped_column(UnicodeText)
    experience_summary: Mapped[str | None] = mapped_column(UnicodeText)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    candidate: Mapped[CandidateProfile] = relationship(back_populates="resumes")
    matches: Mapped[list["Match"]] = relationship(back_populates="resume")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company_profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(UnicodeText, nullable=False)
    required_skills: Mapped[str | None] = mapped_column(UnicodeText)
    min_experience: Mapped[Decimal] = mapped_column(Numeric(4, 1), default=0)
    location: Mapped[str | None] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    company: Mapped[CompanyProfile] = relationship(back_populates="jobs")
    matches: Mapped[list["Match"]] = relationship(back_populates="job")
    company_resume_matches: Mapped[list["CompanyResumeMatch"]] = relationship(back_populates="job")


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    similarity_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    skill_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    experience_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    final_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    explanation: Mapped[str | None] = mapped_column(UnicodeText)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    resume: Mapped[Resume] = relationship(back_populates="matches")
    job: Mapped[Job] = relationship(back_populates="matches")

class CompanyResume(Base):
    __tablename__ = "company_resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company_profiles.id"), nullable=False)
    candidate_name: Mapped[str] = mapped_column(String(150), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    parsed_text: Mapped[str | None] = mapped_column(UnicodeText)
    extracted_skills: Mapped[str | None] = mapped_column(UnicodeText)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    company: Mapped[CompanyProfile] = relationship(back_populates="company_resumes")
    matches: Mapped[list["CompanyResumeMatch"]] = relationship(back_populates="company_resume")


class CompanyResumeMatch(Base):
    __tablename__ = "company_resume_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_resume_id: Mapped[int] = mapped_column(ForeignKey("company_resumes.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    similarity_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    skill_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    final_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    explanation: Mapped[str | None] = mapped_column(UnicodeText)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    company_resume: Mapped[CompanyResume] = relationship(back_populates="matches")
    job: Mapped[Job] = relationship(back_populates="company_resume_matches")

class ModelRun(Base):
    __tablename__ = "model_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    dataset_name: Mapped[str | None] = mapped_column(String(180))
    accuracy: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    precision_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    recall_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    f1_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    notes: Mapped[str | None] = mapped_column(UnicodeText)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())


