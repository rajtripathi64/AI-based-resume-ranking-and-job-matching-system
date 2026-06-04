"""Resume parsing helpers for PDF, DOCX, and plain text files."""

from pathlib import Path
import re

import fitz
from docx import Document

from app.services.skill_normalization import extract_skills_from_text

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def clean_resume_text(text: str) -> str:
    text = text.lstrip("\ufeff")
    lines = [line.strip() for line in text.replace("\r", "\n").split("\n")]
    useful_lines = [line for line in lines if line]
    return "\n".join(useful_lines)


def parse_pdf(file_path: Path) -> str:
    document = fitz.open(file_path)
    try:
        text_parts = [page.get_text() for page in document]
    finally:
        document.close()
    return clean_resume_text("\n".join(text_parts))


def parse_docx(file_path: Path) -> str:
    document = Document(file_path)
    paragraphs = [paragraph.text for paragraph in document.paragraphs]
    return clean_resume_text("\n".join(paragraphs))


def parse_txt(file_path: Path) -> str:
    return clean_resume_text(file_path.read_text(encoding="utf-8", errors="ignore"))


def parse_resume_file(file_path: Path) -> str:
    extension = file_path.suffix.lower()
    if extension == ".pdf":
        return parse_pdf(file_path)
    if extension == ".docx":
        return parse_docx(file_path)
    if extension == ".txt":
        return parse_txt(file_path)
    raise ValueError("Unsupported resume file type")


def extract_basic_skills(text: str) -> list[str]:
    return extract_skills_from_text(text)


def extract_email(text: str) -> str | None:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text or "")
    return match.group(0) if match else None


def extract_candidate_name(text: str) -> str | None:
    blocked_tokens = [
        "email", "phone", "mobile", "resume", "cv", "linkedin", "github",
        "http", "www", "skills", "education", "b.tech", "btech", "bachelor",
        "computer", "science", "engineering", "university", "college",
        "current cpi", "projects", "experience", "profile summary", "summary",
    ]

    section_headers = {"education", "skills", "projects", "experience", "certifications", "achievements"}

    for raw_line in (text or "").split("\n")[:10]:
        line = raw_line.strip().strip("-|•")
        if not line or len(line) > 60:
            continue
        lower = line.lower()
        if lower in section_headers:
            break
        if any(token in lower for token in blocked_tokens):
            continue
        if re.search(r"\d|@|[:|]", line):
            continue
        words = [word for word in re.split(r"\s+", line) if word]
        if 1 <= len(words) <= 4 and all(re.match(r"^[A-Za-z.]+$", word) for word in words):
            return " ".join(word.capitalize() for word in words)
    return None


