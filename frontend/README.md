# Frontend

React frontend for candidate, recruiter, and admin portals.

## Responsibilities

- Login and registration UI
- Candidate dashboard and resume/JD match flow
- Recruiter dashboard, JD upload, bulk resume matching flow
- Recruiter ranked results with matched-skill chips
- Admin dashboard and ML analysis view
- API integration with FastAPI backend

## Folder Structure

```text
frontend/
  src/
    components/  shared layout and messages
    pages/       login, register, dashboards, matching, jobs, ML analysis
    services/    API client and session helpers
    App.jsx      route definitions
    main.jsx     React entry point
    styles.css   global UI styles
```

## Setup

```powershell
cd "project_path\frontend"
npm.cmd install
```

## Run Frontend

```powershell
cd "project_path\frontend"
npm.cmd run dev
```

Open:

```text
http://127.0.0.1:5173
```

## Build Check

```powershell
cd "project_path\frontend"
npm.cmd run build
```

## Portal Flow

- Candidate: upload resume and compare with JD
- Recruiter: upload JD and multiple resumes, then view ranked candidates and matched skills
- Admin: view ML training comparison and final model result

## Demo Dataset Use

For recruiter demo, select multiple `.txt` resumes from:

```text
test_data/source_resume_dataset/resumes
```

The frontend accepts multiple files on the recruiter matching page.

## API URL

The frontend reads API settings from `frontend/.env` or defaults used in the API service. Keep `.env.example` for setup and do not submit private `.env` values.
