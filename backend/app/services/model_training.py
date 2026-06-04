"""Training pipeline for resume-job fit model comparison."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from datasets import load_dataset
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from app.services.embedding_service import cosine_similarity, fallback_embedding, has_local_sbert_model, LOCAL_MODEL_PATH
from app.services.ranking_model import alias_skill_overlap_score, fuzzy_text_match_score
from app.services.skill_normalization import (
    normalized_skill_count,
    normalized_skill_overlap_count,
    normalized_skill_overlap_score,
    resume_quality_score,
)

try:
    from xgboost import XGBClassifier
except Exception:  # pragma: no cover - only used when xgboost install is unavailable
    XGBClassifier = None

DATASET_NAME = "batuhanmtl/job_resume_fit"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOCAL_DATASET_PATH = PROJECT_ROOT / "ml" / "datasets" / "job_resume_fit" / "train.csv"


@dataclass
class TrainingResult:
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    notes: str


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def count_overlap(first: str, second: str) -> int:
    first_tokens = {token.strip().lower() for token in first.replace(",", " ").split() if token.strip()}
    second_tokens = {token.strip().lower() for token in second.replace(",", " ").split() if token.strip()}
    return len(first_tokens & second_tokens)




def cosine_similarity_value(first: Any, second: Any) -> float:
    first_array = np.asarray(first, dtype=float)
    second_array = np.asarray(second, dtype=float)
    denominator = np.linalg.norm(first_array) * np.linalg.norm(second_array)
    if denominator == 0:
        return 0.0
    return float(np.dot(first_array, second_array) / denominator)


def calculate_sbert_similarity_scores(resume_texts: list[str], job_texts: list[str]) -> list[float]:
    if not has_local_sbert_model():
        scores = []
        for resume_text, job_text in zip(resume_texts, job_texts):
            score = cosine_similarity(fallback_embedding(resume_text), fallback_embedding(job_text))
            scores.append(round(max(0.0, min(score, 1.0)) * 100, 2))
        return scores

    try:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(str(LOCAL_MODEL_PATH))
        resume_embeddings = model.encode(resume_texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False)
        job_embeddings = model.encode(job_texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False)
        return [round(max(0.0, min(cosine_similarity_value(resume, job), 1.0)) * 100, 2) for resume, job in zip(resume_embeddings, job_embeddings)]
    except Exception:
        return [0.0 for _ in resume_texts]

def first_existing(row: dict[str, Any], names: list[str], default: Any = 0) -> Any:
    for name in names:
        if name in row and row[name] is not None:
            return row[name]
    return default


def load_resume_fit_dataframe(max_samples: int = 2385) -> pd.DataFrame:
    if LOCAL_DATASET_PATH.exists():
        dataframe = pd.read_csv(LOCAL_DATASET_PATH, nrows=max_samples)
        if dataframe.empty:
            raise RuntimeError(f"Local dataset is empty: {LOCAL_DATASET_PATH}")
        return dataframe

    dataset = load_dataset(DATASET_NAME, split="train", streaming=True)
    rows = []
    for index, row in enumerate(dataset):
        if index >= max_samples:
            break
        rows.append(dict(row))
    if not rows:
        raise RuntimeError("No rows loaded from Hugging Face dataset")
    return pd.DataFrame(rows)


def prepare_features(dataframe: pd.DataFrame, threshold: float = 75.0) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Build independent features and labels.

    ai_match_score is used only to create the label, not as an input feature,
    because using it as a feature would leak the answer into training.
    """
    records = []
    labels = []
    rows = dataframe.to_dict(orient="records")
    resume_texts = [safe_text(first_existing(row, ["resume_text", "resume", "Resume"], "")) for row in rows]
    job_texts = [safe_text(first_existing(row, ["job_text", "job_description", "Job Description"], "")) for row in rows]
    sbert_scores = calculate_sbert_similarity_scores(resume_texts, job_texts)

    for index, row in enumerate(rows):
        resume_text = resume_texts[index]
        job_text = job_texts[index]
        resume_skills = safe_text(first_existing(row, ["resume_skill_list", "resume_skills", "skills"], ""))
        job_skills = safe_text(first_existing(row, ["job_required_skills", "required_skills", "job_skills"], ""))
        ai_score = float(first_existing(row, ["ai_match_score", "match_score", "score"], 0) or 0)
        string_score = float(first_existing(row, ["skill_string_match_score", "string_match_score"], 0) or 0)
        fuzzy_score = fuzzy_text_match_score(resume_text, job_text)

        records.append(
            {
                "sbert_similarity_score": sbert_scores[index],
                "skill_string_match_score": string_score,
                "fuzzy_match_score": fuzzy_score,
                "alias_skill_overlap_score": alias_skill_overlap_score(resume_skills, job_skills),
                "required_skill_score": normalized_skill_overlap_score(resume_skills, job_skills),
                "normalized_skill_overlap_score": normalized_skill_overlap_score(resume_skills, job_skills),
                "resume_quality_score": resume_quality_score(resume_text, resume_skills),
                "resume_text_length": len(resume_text),
                "job_text_length": len(job_text),
                "resume_skill_count": normalized_skill_count(resume_skills),
                "job_skill_count": normalized_skill_count(job_skills),
                "skill_overlap_count": normalized_skill_overlap_count(resume_skills, job_skills),
            }
        )
        labels.append(1 if ai_score >= threshold else 0)

    features = pd.DataFrame(records).fillna(0)
    return features, pd.Series(labels), list(features.columns)


def get_models() -> dict[str, Any]:
    models: dict[str, Any] = {
        "Logistic Regression": Pipeline(
            [("scaler", StandardScaler()), ("model", LogisticRegression(max_iter=1000))]
        ),
        "SVM": Pipeline([("scaler", StandardScaler()), ("model", SVC(kernel="rbf"))]),
        "KNN": Pipeline([("scaler", StandardScaler()), ("model", KNeighborsClassifier(n_neighbors=5))]),
        "Random Forest": RandomForestClassifier(n_estimators=120, random_state=42),
    }
    if XGBClassifier is not None:
        models["XGBoost"] = XGBClassifier(
            n_estimators=120,
            max_depth=4,
            learning_rate=0.08,
            eval_metric="logloss",
            random_state=42,
        )
    return models


def train_and_compare(max_samples: int = 2385, threshold: float = 75.0) -> tuple[list[TrainingResult], str]:
    dataframe = load_resume_fit_dataframe(max_samples=max_samples)
    features, labels, feature_names = prepare_features(dataframe, threshold=threshold)

    if labels.nunique() < 2:
        raise RuntimeError("Training labels have only one class. Try a different threshold or more samples.")

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    results: list[TrainingResult] = []
    for model_name, model in get_models().items():
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        results.append(
            TrainingResult(
                model_name=model_name,
                accuracy=round(accuracy_score(y_test, predictions) * 100, 2),
                precision=round(precision_score(y_test, predictions, zero_division=0) * 100, 2),
                recall=round(recall_score(y_test, predictions, zero_division=0) * 100, 2),
                f1=round(f1_score(y_test, predictions, zero_division=0) * 100, 2),
                notes=f"Dataset={DATASET_NAME}; local_path={LOCAL_DATASET_PATH}; samples={len(features)}; threshold={threshold}; features={', '.join(feature_names)}",
            )
        )

    results.sort(key=lambda item: item.f1, reverse=True)
    return results, DATASET_NAME


def decimal_metric(value: float) -> Decimal:
    return Decimal(str(round(value, 2)))






