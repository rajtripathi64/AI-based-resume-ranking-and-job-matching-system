# ML

Machine learning assets for resume-job matching.

## Contents

```text
ml/
  datasets/job_resume_fit/       local public training dataset copy
  models/                        final trained model and SBERT model
```

## Training Dataset

The model training data comes from:

```text
batuhanmtl/job_resume_fit
```

Local file after setup:

```text
ml/datasets/job_resume_fit/train.csv
```

## Demo Resume Dataset

The presentation demo resumes come from:

```text
https://huggingface.co/datasets/opensporks/resumes
```

Local subset:

```text
test_data/source_resume_dataset/resumes
```

## Model Training

Training is run from the backend folder:

```powershell
cd "C:\Users\RAJ TRIPATHI\Desktop\final_year_project\backend"
.\.venv\Scripts\python.exe train_model.py
```

The script compares:

- Logistic Regression
- SVM
- KNN
- Random Forest
- XGBoost

XGBoost is selected as the final project model because it handles non-linear feature relationships and is suitable for future larger datasets.

## Live Matching Signals

- Required skill match
- SBERT semantic similarity
- XGBoost probability
- Resume quality
- Fuzzy text match and count features used for model input

## Final Score

```text
42% Section-Weighted Required Skill Match
30% Section-Weighted SBERT Semantic Similarity
20% XGBoost Model Score
8% Resume Quality
```

## GitHub Note

The full training CSV and local SBERT model folder are ignored in Git because they are large generated/downloaded assets.

Recreate the SBERT folder:

```powershell
cd "project_path\backend"
.\.venv\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('../ml/models/all-MiniLM-L6-v2')"
```

Recreate the training CSV:

```powershell
cd "project_path\backend"
.\.venv\Scripts\python.exe -c "from datasets import load_dataset; from pathlib import Path; p=Path('../ml/datasets/job_resume_fit'); p.mkdir(parents=True, exist_ok=True); load_dataset('batuhanmtl/job_resume_fit', split='train').to_csv(str(p / 'train.csv'))"
```
