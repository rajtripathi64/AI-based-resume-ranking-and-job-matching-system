"""ML model training schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ModelRunResponse(BaseModel):
    id: int
    model_name: str
    dataset_name: str | None
    accuracy: Decimal | None
    precision_score: Decimal | None
    recall_score: Decimal | None
    f1_score: Decimal | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TrainingResponse(BaseModel):
    dataset_name: str
    max_samples: int
    threshold: float
    results: list[ModelRunResponse]
