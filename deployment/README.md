# Deployment and Final Run Guide

This project is prepared for local deployment and final-year demonstration on a Windows system with SQL Server, FastAPI, and React.

## Local Deployment Stack

- Frontend: React + Vite
- Backend: FastAPI + Uvicorn
- Database: Microsoft SQL Server Express / Developer Edition through SSMS
- Authentication: JWT role-based login
- ML/NLP: SBERT embeddings, spaCy skill extraction, fuzzy matching features, XGBoost ranking model

## Required Software

Install these before running the project:

- Python 3.10 or later
- Node.js 18 or later
- Microsoft SQL Server
- SQL Server Management Studio
- VS Code

## SQL Server Setup

Connect in SSMS:

```text
Server name: LAPTOP-CJ0JLQGR\SQLEXPRESS
Authentication: Windows Authentication
```

Run database scripts in this order:

```text
database/01_create_database.sql
database/02_schema.sql
database/04_phase8_company_resume_matching.sql
```

The expected database is:

```text
resume_screening
```

## Backend Environment

Environment file:

```text
backend/.env
```

Important values:

```text
DATABASE_URL=SQL Server trusted connection string
SECRET_KEY=JWT signing secret
ACCESS_TOKEN_EXPIRE_MINUTES=token validity time
```

Do not commit real production secrets. For final demo, local `.env` is enough.

## Backend Run

```powershell
cd "project_path\backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

Backend check URLs:

```text
http://localhost:8001/docs
http://localhost:8001/api/health
http://localhost:8001/api/database/status
```

## Frontend Run

```powershell
cd "project_path\frontend"
npm.cmd run dev
```

Frontend URL:

```text
http://localhost:5173/login
```

## Production Build

Create frontend production build:

```powershell
cd "project_path\frontend"
npm.cmd run build
```

The generated frontend output is:

```text
frontend/dist/
```

For a real server deployment, this folder can be hosted using Nginx, IIS, Apache, or a static hosting service. The backend should be deployed separately using a production ASGI server setup.

## Production Deployment Notes

For industry deployment, the following changes are recommended:

- Use HTTPS with a valid SSL certificate.
- Move secrets into secure environment variables.
- Use a managed SQL Server or secured database server.
- Configure CORS only for the production frontend domain.
- Add file upload size limits and virus scanning.
- Store only necessary metadata, not unnecessary resume files.
- Add logging, monitoring, backups, and error tracking.
- Run backend using a production process manager.
- Add CI/CD for automated testing and deployment.

## Final Demo Portals

Candidate:

```text
Upload resume + JD, view match percentage and matched skills.
```

Recruiter:

```text
Upload one JD + multiple resumes, view ranked candidates with extracted name/email/file name, score, and matched skills.
```

Admin:

```text
View users and run ML model training/comparison with accuracy, precision, recall, and F1 score.
```

## Final AI Scoring

```text
42% Required skill match
30% SBERT semantic similarity
20% XGBoost ML prediction
8% Resume quality
```

This hybrid design keeps the output explainable while still using trained ML support for ranking.


