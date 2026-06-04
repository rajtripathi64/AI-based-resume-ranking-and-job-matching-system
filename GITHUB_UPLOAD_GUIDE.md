# GitHub Upload Guide

This guide shows how to upload this project to GitHub safely.

## 1. Important Safety Notes

Do not upload these folders/files:

```text
backend/.venv/
frontend/node_modules/
frontend/dist/
backend/.env
frontend/.env
backend/uploads/
ml/models/all-MiniLM-L6-v2/
ml/datasets/job_resume_fit/train.csv
```

They are ignored by `.gitignore`.

The repository keeps the small final trained model:

```text
ml/models/final_resume_ranker.joblib
ml/models/final_resume_ranker_metadata.txt
```

## 2. Open Terminal In The Project Folder

Use PowerShell:

```powershell
cd "C:\Users\RAJ TRIPATHI\Desktop\final_year_project"
```

## 3. Check If This Folder Already Has Git

```powershell
git rev-parse --show-toplevel
```

Expected good result:

```text
C:/Users/RAJ TRIPATHI/Desktop/final_year_project
```

If it shows a parent folder like `C:/Users/RAJ TRIPATHI`, do not commit yet. Create a fresh project Git repository with the commands in the next step.

## 4. Initialize Git In This Project Only

If `final_year_project` is not already its own Git repository, run:

```powershell
git init
```

Then check status:

```powershell
git status --short
```

You should see only files from this project, such as:

```text
README.md
backend/...
frontend/...
database/...
ml/...
deployment/...
test_data/...
```

You should not see paths like:

```text
../../AppData
../../Documents
../../Downloads
```

If you see those parent paths, stop and tell me before committing.

## 5. Add Files

```powershell
git add .
```

Check what will be committed:

```powershell
git status --short
```

Optional large-file check:

```powershell
git ls-files | ForEach-Object { Get-Item $_ } | Sort-Object Length -Descending | Select-Object -First 20 FullName,Length
```

Make sure `ml/models/all-MiniLM-L6-v2/model.safetensors` and `ml/datasets/job_resume_fit/train.csv` are not listed.

## 6. Commit

```powershell
git commit -m "Initial commit: AI resume screening system"
```

## 7. Create GitHub Repository

On GitHub:

1. Open https://github.com/new
2. Repository name example:

```text
ai-resume-screening-system
```

3. Keep repository Public or Private as you prefer.
4. Do not add README, .gitignore, or license on GitHub because this project already has local files.
5. Click Create repository.

## 8. Connect Local Project To GitHub

Replace `YOUR_USERNAME` with your GitHub username:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-resume-screening-system.git
git push -u origin main
```

If the remote already exists:

```powershell
git remote set-url origin https://github.com/YOUR_USERNAME/ai-resume-screening-system.git
git push -u origin main
```

## 9. After Someone Clones The Repository

Clone:

```powershell
git clone https://github.com/YOUR_USERNAME/ai-resume-screening-system.git
cd ai-resume-screening-system
```

Backend setup:

```powershell
cd backend
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Frontend setup:

```powershell
cd ..\frontend
npm.cmd install
Copy-Item .env.example .env
```

Download SBERT model after backend dependencies install:

```powershell
cd ..\backend
.\.venv\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('../ml/models/all-MiniLM-L6-v2')"
```

Download training dataset if model training demo is needed:

```powershell
.\.venv\Scripts\python.exe -c "from datasets import load_dataset; from pathlib import Path; p=Path('../ml/datasets/job_resume_fit'); p.mkdir(parents=True, exist_ok=True); load_dataset('batuhanmtl/job_resume_fit', split='train').to_csv(str(p / 'train.csv'))"
```

## 10. Run After Clone

Backend:

```powershell
cd "project_path\backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

Frontend:

```powershell
cd "project_path\frontend"
npm.cmd run dev
```

Open:

```text
http://localhost:5173/login
http://localhost:8001/docs
```

## 11. SQL Server Setup

Open SSMS and run:

```text
database/01_create_database.sql
database/02_schema.sql
database/04_phase8_company_resume_matching.sql
```

Update `backend/.env` if your SQL Server name is different.

## 12. Final Push Checklist

Before every push:

```powershell
git status --short
```

Check that these are not staged:

```text
.env
.venv
node_modules
dist
uploads
all-MiniLM-L6-v2
train.csv
```

Then push:

```powershell
git add .
git commit -m "Update project"
git push
```
