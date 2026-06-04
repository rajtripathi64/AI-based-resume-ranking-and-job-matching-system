# AI Resume Screening and JD Matching System

A final-year project for AI-based resume screening, job description matching, and recruiter shortlisting. The system provides separate candidate, recruiter, and admin portals with a React frontend, FastAPI backend, SQL Server database, resume parsing, SBERT semantic matching, and an XGBoost-based ML ranking model.

## Main Features

- Candidate login, resume upload, and JD match percentage
- Recruiter dashboard for uploading one JD and multiple resumes
- Ranked candidate shortlist with final matching percentage
- Recruiter result cards show matched required skills
- Admin dashboard for ML model comparison and training results
- JWT authentication with role-based access
- SQL Server database integration
- Resume and JD parsing for PDF, DOCX, and TXT
- Skill extraction with aliases, spaCy NLP, and a local ESCO-inspired taxonomy
- SBERT semantic similarity using `all-MiniLM-L6-v2`
- XGBoost final ML model with comparative model analysis
- Sourced 60-resume demo dataset from Hugging Face

## Final Scoring Formula

```text
Final Match Score =
42% Section-Weighted Required Skill Match
+ 30% Section-Weighted SBERT Semantic Similarity
+ 20% XGBoost Model Score
+ 8% Resume Quality
```

Required Skill Match checks JD sections with Required 60%, Preferred 30%, and Soft Skills 10%. Section-weighted SBERT compares the resume mainly with the strongest JD sections instead of treating the whole JD equally. XGBoost provides trained ML decision support using engineered features. Resume Quality rewards readable, complete resumes with useful sections and extracted skills.

## Matching Architecture

```text
Resume + JD
  -> Text Parsing and Cleaning
  -> Skill Extraction and Alias Mapping
  -> Required Skill Matching
  -> Section-Weighted SBERT Similarity
  -> Fuzzy Matching and Feature Engineering
  -> XGBoost Model Score
  -> Final Hybrid AI Match Score
```

## Tech Stack

- Frontend: React, Vite, CSS, lucide-react
- Backend: FastAPI, SQLAlchemy, JWT, Pydantic
- Database: Microsoft SQL Server / SSMS
- ML/NLP: SBERT, spaCy, scikit-learn, XGBoost, KNN, SVM, Random Forest, Logistic Regression
- Resume Parsing: PyMuPDF, python-docx
- Training Dataset: `batuhanmtl/job_resume_fit`
- Demo Resume Source: `opensporks/resumes`

## Project Structure

```text
final_year_project/
  backend/      FastAPI backend, APIs, auth, parsing, matching, model training
  frontend/     React frontend portals and dashboard UI
  database/     SQL Server setup and schema scripts
  ml/           Dataset notes, final trained model, SBERT download location
  docs/         Phase reports and architecture notes
  deployment/   Deployment notes
  test_data/    Sourced demo resume dataset and testing data
```

## Run Backend

```powershell
cd "project_path\backend"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

Open API docs:

```text
http://127.0.0.1:8001/docs
```

## Run Frontend

```powershell
cd "project_path\frontend"
npm.cmd install
npm.cmd run dev
```

Open frontend:

```text
http://127.0.0.1:5173
```

## SQL Server Setup

1. Open SSMS.
2. Connect to server: `LAPTOP-CJ0JLQGR\SQLEXPRESS`.
3. Run scripts from `database/` in order:

```text
01_create_database.sql
02_schema.sql
03_join_examples.sql
04_phase8_company_resume_matching.sql
```

4. Check backend `.env` database URL.

## Model Training Demo

```powershell
cd "project_path\backend"
.\.venv\Scripts\python.exe train_model.py
```

The training command compares Logistic Regression, SVM, KNN, Random Forest, and XGBoost, then saves the final selected XGBoost artifact in `ml/models/final_resume_ranker.joblib`.

## Demo Resume Dataset

A public sourced 60-resume subset is stored here:

```text
test_data/source_resume_dataset/resumes
```

Source:

```text
https://huggingface.co/datasets/opensporks/resumes
```

Files are saved as `.txt`, which the project parser supports. For a smooth presentation, upload 10-20 resumes at a time on the recruiter matching page.

## Final Demo Flow

1. Start SQL Server.
2. Start backend.
3. Start frontend.
4. Login/register as recruiter.
5. Upload one JD and multiple resumes from `test_data/source_resume_dataset/resumes`.
6. Show ranked candidates, match percentage, and matched skills.
7. Login/register as candidate.
8. Upload resume and JD.
9. Show match percentage.
10. Login as admin.
11. Show ML model comparison.


## GitHub Clone Setup For ML Assets

The GitHub repository does not include the large local SBERT model folder or the full training CSV. After cloning and installing backend requirements, recreate them with these commands.

Download SBERT locally:

```powershell
cd "project_path\backend"
.\.venv\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('../ml/models/all-MiniLM-L6-v2')"
```

Download the training dataset locally:

```powershell
cd "project_path\backend"
.\.venv\Scripts\python.exe -c "from datasets import load_dataset; from pathlib import Path; p=Path('../ml/datasets/job_resume_fit'); p.mkdir(parents=True, exist_ok=True); load_dataset('batuhanmtl/job_resume_fit', split='train').to_csv(str(p / 'train.csv'))"
```

The small final model file stays in GitHub:

```text
ml/models/final_resume_ranker.joblib
```
## Important Notes

- Do not commit `.env` files.
- Uploaded resumes are runtime data and should not be stored in final submission.
- `final_resume_ranker.joblib` is the active ML model file.
- `all-MiniLM-L6-v2` is the pretrained SBERT embedding model. It is ignored on GitHub because it is large; download it again using the setup command below.
- The project uses an ESCO-inspired local skill taxonomy, not the full official ESCO database.

