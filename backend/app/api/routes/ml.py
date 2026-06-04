"""ML routes for model training and comparison."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import ModelRun, User
from app.schemas.ml import ModelRunResponse, TrainingResponse
from app.services.model_training import decimal_metric, train_and_compare

router = APIRouter()


def require_admin(user: User) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can train ML models")


@router.post("/train", response_model=TrainingResponse)
def train_models(
    max_samples: int = Query(default=2385, ge=100, le=10000),
    threshold: float = Query(default=75.0, ge=1, le=99),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrainingResponse:
    require_admin(current_user)
    try:
        training_results, dataset_name = train_and_compare(max_samples=max_samples, threshold=threshold)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    saved_runs = []
    for result in training_results:
        run = ModelRun(
            model_name=result.model_name,
            dataset_name=dataset_name,
            accuracy=decimal_metric(result.accuracy),
            precision_score=decimal_metric(result.precision),
            recall_score=decimal_metric(result.recall),
            f1_score=decimal_metric(result.f1),
            notes=result.notes,
        )
        db.add(run)
        saved_runs.append(run)

    db.commit()
    for run in saved_runs:
        db.refresh(run)

    return TrainingResponse(
        dataset_name=dataset_name,
        max_samples=max_samples,
        threshold=threshold,
        results=[ModelRunResponse.model_validate(run) for run in saved_runs],
    )


@router.get("/runs", response_model=list[ModelRunResponse])
def list_model_runs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ModelRunResponse]:
    require_admin(current_user)
    runs = db.scalars(select(ModelRun).order_by(ModelRun.created_at.desc())).all()
    return [ModelRunResponse.model_validate(run) for run in runs]


@router.get("/comparison", response_model=list[ModelRunResponse])
def latest_model_comparison(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ModelRunResponse]:
    require_admin(current_user)
    runs = db.scalars(select(ModelRun).order_by(ModelRun.created_at.desc())).all()
    latest_by_model = {}
    for run in runs:
        if run.model_name not in latest_by_model:
            latest_by_model[run.model_name] = run
    ordered = sorted(latest_by_model.values(), key=lambda item: item.f1_score or 0, reverse=True)
    return [ModelRunResponse.model_validate(run) for run in ordered]
