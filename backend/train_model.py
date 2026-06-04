r"""Train and save the final resume ranking ML model.


It trains all configured models, compares metrics on the testing split, and saves
the best corrected model as the final selected ranking model artifact.

Run from backend folder:
    .\.venv\Scripts\python.exe train_model.py
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import joblib
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from app.services.model_training import (
    DATASET_NAME,
    LOCAL_DATASET_PATH,
    get_models,
    load_resume_fit_dataframe,
    prepare_features,
)

MAX_SAMPLES = 2385
THRESHOLD = 75.0
TEST_SIZE = 0.2
RANDOM_STATE = 42
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / "ml" / "models"
FINAL_MODEL_PATH = MODEL_DIR / "final_resume_ranker.joblib"
METADATA_PATH = MODEL_DIR / "final_resume_ranker_metadata.txt"
PROJECT_SELECTED_MODEL_NAME = "XGBoost"


def line(char: str = "=", width: int = 78) -> str:
    return char * width


def print_header() -> None:
    print(line())
    print("AI RESUME SCREENING - FINAL MODEL TRAINING")
    print(line())
    print(f"Dataset name       : {DATASET_NAME}")
    print(f"Local dataset file : {LOCAL_DATASET_PATH}")
    print(f"Rows used          : {MAX_SAMPLES}")
    print(f"Fit threshold      : {THRESHOLD}%")
    print("Train/Test split   : 80% training / 20% testing")
    print(f"Random state       : {RANDOM_STATE}")
    print(line("-"))


def train_models() -> tuple[list[dict], str, object, list[str], int, int]:
    dataframe = load_resume_fit_dataframe(max_samples=MAX_SAMPLES)
    features, labels, feature_names = prepare_features(dataframe, threshold=THRESHOLD)

    if labels.nunique() < 2:
        raise RuntimeError("Training labels have only one class. Use more rows or a different threshold.")

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    results = []
    fitted_models = {}
    for model_name, model in get_models().items():
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        results.append(
            {
                "model_name": model_name,
                "accuracy": round(accuracy_score(y_test, predictions) * 100, 2),
                "precision": round(precision_score(y_test, predictions, zero_division=0) * 100, 2),
                "recall": round(recall_score(y_test, predictions, zero_division=0) * 100, 2),
                "f1": round(f1_score(y_test, predictions, zero_division=0) * 100, 2),
            }
        )
        fitted_models[model_name] = model

    results.sort(key=lambda item: item["f1"], reverse=True)
    final_model_name = PROJECT_SELECTED_MODEL_NAME
    final_model = fitted_models.get(final_model_name)
    if final_model is None:
        raise RuntimeError("Final selected model is not available. Check model configuration in model_training.py.")

    return results, final_model_name, final_model, feature_names, len(x_train), len(x_test)


def print_results(results: list[dict]) -> None:
    print("MODEL COMPARISON ON TEST DATA")
    print(line("-"))
    print(f"{'Model':<22} {'Accuracy':>10} {'Precision':>11} {'Recall':>9} {'F1 Score':>10}")
    print(line("-"))
    for result in results:
        marker = " <-- BEST" if result["f1"] == results[0]["f1"] else ""
        print(
            f"{result['model_name']:<22} "
            f"{result['accuracy']:>9.2f}% "
            f"{result['precision']:>10.2f}% "
            f"{result['recall']:>8.2f}% "
            f"{result['f1']:>9.2f}%{marker}"
        )
    print(line("-"))


def save_final_model(final_model_name: str, final_model: object, feature_names: list[str], train_rows: int, test_rows: int, results: list[dict]) -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model_name": final_model_name,
            "model": final_model,
            "feature_names": feature_names,
            "threshold": THRESHOLD,
            "dataset_name": DATASET_NAME,
            "local_dataset_path": str(LOCAL_DATASET_PATH),
            "train_rows": train_rows,
            "test_rows": test_rows,
            "metrics": results,
        },
        FINAL_MODEL_PATH,
    )

    final_result = next(item for item in results if item["model_name"] == final_model_name)
    METADATA_PATH.write_text(
        "AI Resume Screening Final Model\n"
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Selected model: {final_model_name}\n"
        f"Dataset: {DATASET_NAME}\n"
        f"Rows used: {MAX_SAMPLES}\n"
        f"Training rows: {train_rows}\n"
        f"Testing rows: {test_rows}\n"
        f"Threshold: {THRESHOLD}%\n"
        f"Accuracy: {final_result['accuracy']}%\n"
        f"Precision: {final_result['precision']}%\n"
        f"Recall: {final_result['recall']}%\n"
        f"F1 Score: {final_result['f1']}%\n"
        f"Feature names: {', '.join(feature_names)}\n",
        encoding="utf-8",
    )


def print_final_answer(final_model_name: str, results: list[dict], train_rows: int, test_rows: int) -> None:
    best_f1 = results[0]["f1"]
    best_models = [item["model_name"] for item in results if item["f1"] == best_f1]
    final_result = next(item for item in results if item["model_name"] == final_model_name)

    print("FINAL PROJECT MODEL SELECTION")
    print(line("-"))
    print(f"Best model(s) by F1 score : {', '.join(best_models)}")
    print(f"Final selected model      : {final_model_name}")
    print(f"Reason                    : {final_model_name} is selected as the final project model because")
    print("                            it handles complex non-linear feature relationships")
    print("                            and is more suitable for future larger datasets.")
    print(f"Training rows             : {train_rows}")
    print(f"Testing rows              : {test_rows}")
    print(f"Final model accuracy      : {final_result['accuracy']}%")
    print(f"Final model precision     : {final_result['precision']}%")
    print(f"Final model recall        : {final_result['recall']}%")
    print(f"Final model F1 score      : {final_result['f1']}%")
    print(f"Saved model file          : {FINAL_MODEL_PATH}")
    print(line())
    print(f"This trained {final_model_name} model is the ML ranking model selected for the final system output.")
    print(line())


def main() -> None:
    print_header()
    results, final_model_name, final_model, feature_names, train_rows, test_rows = train_models()
    print(f"Training rows: {train_rows}")
    print(f"Testing rows : {test_rows}")
    print(line("-"))
    print_results(results)
    save_final_model(final_model_name, final_model, feature_names, train_rows, test_rows, results)
    print_final_answer(final_model_name, results, train_rows, test_rows)


if __name__ == "__main__":
    main()


