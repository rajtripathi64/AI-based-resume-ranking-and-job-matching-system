"""Embedding and similarity helpers for resume-job matching."""

import hashlib
import math
import os
from functools import lru_cache
from pathlib import Path

from app.services.job_parser import split_job_description_sections

MODEL_NAME = "all-MiniLM-L6-v2"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOCAL_MODEL_PATH = PROJECT_ROOT / "ml" / "models" / MODEL_NAME
SECTION_SBERT_WEIGHTS = {
    "required": 0.60,
    "responsibilities": 0.30,
    "preferred": 0.20,
}


def has_local_sbert_model() -> bool:
    return (LOCAL_MODEL_PATH / "config.json").exists() and (LOCAL_MODEL_PATH / "modules.json").exists()


@lru_cache(maxsize=1)
def get_sentence_transformer():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None

    offline_mode = os.getenv("SBERT_OFFLINE_MODE", "true").lower() == "true"
    try:
        if has_local_sbert_model():
            return SentenceTransformer(str(LOCAL_MODEL_PATH))
        if offline_mode:
            return None
        return SentenceTransformer(MODEL_NAME)
    except Exception:
        return None


def fallback_embedding(text: str, dimensions: int = 384) -> list[float]:
    vector = [0.0] * dimensions
    words = [word.strip(".,:;()[]{}!?\"'").lower() for word in text.split()]
    for word in words:
        if not word:
            continue
        digest = hashlib.sha256(word.encode("utf-8")).hexdigest()
        index = int(digest[:8], 16) % dimensions
        vector[index] += 1.0
    return normalize(vector)


def normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def encode_text(text: str) -> tuple[list[float], str]:
    model = get_sentence_transformer()
    if model is not None:
        embedding = model.encode(text or "", normalize_embeddings=True)
        return embedding.tolist(), f"SBERT {MODEL_NAME}"
    return fallback_embedding(text or ""), "fallback hashing embedding"


def cosine_similarity(first: list[float], second: list[float]) -> float:
    if not first or not second:
        return 0.0
    return sum(a * b for a, b in zip(first, second))


def similarity_percentage(first_text: str, second_text: str) -> tuple[float, str]:
    first_vector, method = encode_text(first_text)
    second_vector, _ = encode_text(second_text)
    score = cosine_similarity(first_vector, second_vector)
    return round(max(0.0, min(score, 1.0)) * 100, 2), method


def section_weighted_similarity_percentage(resume_text: str, job_text: str) -> tuple[float, str]:
    sections = split_job_description_sections(job_text)
    weighted_scores: list[tuple[float, float]] = []
    method = f"SBERT {MODEL_NAME}"

    for section_name, weight in SECTION_SBERT_WEIGHTS.items():
        section_text = sections.get(section_name, "")
        if not section_text:
            continue
        section_score, method = similarity_percentage(resume_text, section_text)
        weighted_scores.append((section_score, weight))

    if not weighted_scores:
        return similarity_percentage(resume_text, job_text)

    available_weight = sum(weight for _, weight in weighted_scores)
    score = sum(score * weight for score, weight in weighted_scores) / available_weight
    return round(max(0.0, min(score, 100.0)), 2), f"Section-weighted {method}"


def skill_score(resume_skills: str | None, job_skills: str | None) -> float:
    resume_set = {skill.strip().lower() for skill in (resume_skills or "").split(",") if skill.strip()}
    job_set = {skill.strip().lower() for skill in (job_skills or "").split(",") if skill.strip()}
    if not job_set:
        return 0.0
    return round((len(resume_set & job_set) / len(job_set)) * 100, 2)


def final_match_score(similarity_score: float, skills_score: float) -> float:
    return round((similarity_score * 0.45) + (skills_score * 0.55), 2)
