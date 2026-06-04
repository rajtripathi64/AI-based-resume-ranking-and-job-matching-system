# Backend

FastAPI backend for authentication, resume parsing, JD parsing, candidate/recruiter matching, admin APIs, SQL Server integration, and ML model training.

## Responsibilities

- JWT authentication and role-based access
- Candidate, recruiter, and admin API routes
- SQL Server connection through SQLAlchemy
- Resume parsing for PDF, DOCX, TXT
- JD skill extraction
- Matched-skill calculation for recruiter shortlists
- SBERT semantic similarity
- XGBoost final ranking model integration
- Model training and comparison command

## Folder Structure

```text
backend/
  app/
    api/        API router, dependencies, route modules
    core/       config and security helpers
    db/         database session and base setup
    models/     SQLAlchemy table models
    schemas/    Pydantic request/response schemas
    services/   parsing, embeddings, ranking, training helpers
  tests/        backend unit tests
  uploads/      runtime upload folder; final submission keeps only .gitkeep
  train_model.py
  requirements.txt
```

## Setup

```powershell
cd "project_path \backend"
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Environment

Create `backend/.env` from `backend/.env.example`.

For Windows trusted SQL Server connection, use your SQL Server instance:

```text
LAPTOP-CJ0JLQGR\SQLEXPRESS
```

## Run Backend

```powershell
cd "project_path\backend"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

Open:

```text
http://127.0.0.1:8001/docs
```

## Test Backend

```powershell
cd "project_path\backend"
.\.venv\Scripts\python.exe -m unittest tests.test_matching tests.test_resume_parser tests.test_auth
.\.venv\Scripts\python.exe -m py_compile app\services\skill_normalization.py app\services\ranking_model.py app\services\model_training.py app\api\routes\matching.py
```

## Train Model

```powershell
cd "project_path\backend"
.\.venv\Scripts\python.exe train_model.py
```

Current final model selection is XGBoost. The training program compares Logistic Regression, SVM, KNN, Random Forest, and XGBoost for examiner demonstration.

## Recruiter Matching Response

The recruiter instant matching endpoint returns ranked candidates with:

```text
candidate_name
file_name
email
final_score
similarity_score
skill_score
matched_skills
matched_skills_text
```

`matched_skills` shows which required JD skills were found in each resume.

## Matching Formula

```text
42% Section-Weighted Required Skill Match
30% Section-Weighted SBERT Semantic Similarity
20% XGBoost Model Score
8% Resume Quality
```
