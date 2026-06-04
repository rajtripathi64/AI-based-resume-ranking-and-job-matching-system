"""Final ML ranking model helpers.

The live score is a role-neutral hybrid of section-weighted required skills,
section-aware SBERT semantics, XGBoost probability, and resume quality.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from app.services.embedding_service import final_match_score
from app.services.job_parser import weighted_job_skill_score
from app.services.skill_normalization import (
    normalized_skill_count,
    normalized_skill_overlap_count,
    normalized_skill_overlap_score,
    resume_quality_score,
    skill_set,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "final_resume_ranker.joblib"
REQUIRED_SKILL_WEIGHT = 0.42
SBERT_WEIGHT = 0.30
XGBOOST_WEIGHT = 0.20
RESUME_QUALITY_WEIGHT = 0.08


@lru_cache(maxsize=1)
def load_ranking_artifact() -> dict[str, Any] | None:
    if not MODEL_PATH.exists():
        return None
    try:
        import joblib
        return joblib.load(MODEL_PATH)
    except Exception:
        return None


def clamp_score(value: float) -> float:
    return max(0.0, min(value, 100.0))


def format_weight(weight: float) -> str:
    return f"{weight * 100:g}%"


def fuzzy_text_match_score(first_text: str, second_text: str) -> float:
    first_tokens = {token for token in (first_text or "").lower().replace(",", " ").split() if len(token) > 2}
    second_tokens = {token for token in (second_text or "").lower().replace(",", " ").split() if len(token) > 2}
    if not first_tokens or not second_tokens:
        return 0.0
    overlap = len(first_tokens & second_tokens)
    return round((2 * overlap / (len(first_tokens) + len(second_tokens))) * 100, 2)


def alias_skill_overlap_score(resume_skills: str | None, job_skills: str | None) -> float:
    resume = skill_set(resume_skills)
    job = skill_set(job_skills)
    if not job:
        return 0.0
    return round((len(resume & job) / len(job)) * 100, 2)


def preprocessing_explainability_score(
    resume_text: str,
    resume_skills: str | None,
    job_skills: str | None,
) -> float:
    required_skill_score = normalized_skill_overlap_score(resume_skills, job_skills)
    alias_score = alias_skill_overlap_score(resume_skills, job_skills)
    quality_score = resume_quality_score(resume_text, resume_skills)
    return round(
        (required_skill_score * 0.65)
        + (alias_score * 0.20)
        + (quality_score * 0.15),
        2,
    )


def build_live_features(
    resume_text: str,
    job_text: str,
    resume_skills: str | None,
    job_skills: str | None,
    similarity_score: float,
    skill_match_score: float,
) -> pd.DataFrame:
    overlap_score = normalized_skill_overlap_score(resume_skills, job_skills)
    section_weighted_score = weighted_job_skill_score(resume_skills, job_text)
    alias_score = alias_skill_overlap_score(resume_skills, job_skills)
    return pd.DataFrame([
        {
            "sbert_similarity_score": similarity_score,
            "skill_string_match_score": skill_match_score,
            "fuzzy_match_score": fuzzy_text_match_score(resume_text, job_text),
            "alias_skill_overlap_score": alias_score,
            "required_skill_score": section_weighted_score,
            "normalized_skill_overlap_score": overlap_score,
            "resume_quality_score": resume_quality_score(resume_text, resume_skills),
            "resume_text_length": len(resume_text or ""),
            "job_text_length": len(job_text or ""),
            "resume_skill_count": normalized_skill_count(resume_skills),
            "job_skill_count": normalized_skill_count(job_skills),
            "skill_overlap_count": normalized_skill_overlap_count(resume_skills, job_skills),
        }
    ])


def ranking_model_score(
    resume_text: str,
    job_text: str,
    resume_skills: str | None,
    job_skills: str | None,
    similarity_score: float,
    skill_match_score: float,
) -> tuple[float, str]:
    artifact = load_ranking_artifact()
    fallback_score = final_match_score(similarity_score, skill_match_score)
    if artifact is None:
        return fallback_score, "SBERT + skill fallback score"

    model = artifact.get("model")
    model_name = artifact.get("model_name", "Saved ML model")
    feature_names = artifact.get("feature_names")
    features = build_live_features(
        resume_text=resume_text,
        job_text=job_text,
        resume_skills=resume_skills,
        job_skills=job_skills,
        similarity_score=similarity_score,
        skill_match_score=skill_match_score,
    )
    if feature_names:
        features = features.reindex(columns=feature_names, fill_value=0)

    try:
        if hasattr(model, "predict_proba"):
            model_score = float(model.predict_proba(features)[0][1]) * 100
        else:
            model_score = float(model.predict(features)[0]) * 100
    except Exception:
        return fallback_score, "SBERT + skill fallback score"

    required_skill_score = weighted_job_skill_score(resume_skills, job_text)
    quality_score = resume_quality_score(resume_text, resume_skills)
    final_score = (
        clamp_score(required_skill_score) * REQUIRED_SKILL_WEIGHT
        + clamp_score(similarity_score) * SBERT_WEIGHT
        + clamp_score(model_score) * XGBOOST_WEIGHT
        + clamp_score(quality_score) * RESUME_QUALITY_WEIGHT
    )
    score = round(clamp_score(final_score), 2)
    return score, (
        f"Hybrid ranking: required skills {format_weight(REQUIRED_SKILL_WEIGHT)}, "
        f"section-SBERT {format_weight(SBERT_WEIGHT)}, "
        f"{model_name} {format_weight(XGBOOST_WEIGHT)}, "
        f"resume quality {format_weight(RESUME_QUALITY_WEIGHT)}."
    )
