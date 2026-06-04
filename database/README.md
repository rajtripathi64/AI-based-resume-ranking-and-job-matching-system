# Database

SQL Server scripts for creating and preparing the project database.

## Database Tool

Use Microsoft SQL Server with SSMS.

Recommended local server:

```text
LAPTOP-CJ0JLQGR\SQLEXPRESS
```

## Script Order

Run these files in SSMS in this order:

```text
01_create_database.sql
02_schema.sql
03_join_examples.sql
04_phase8_company_resume_matching.sql
```

## What The Schema Supports

- Users and roles: candidate, company/recruiter, admin
- Candidate profiles
- Company/recruiter profiles
- Jobs and job descriptions
- Candidate resumes
- Company uploaded resume pool
- Resume-to-job matching results
- Company resume shortlist matching results

## Backend Connection

The backend connection is configured in:

```text
backend/.env
```

Example trusted connection style:

```text
DATABASE_URL=mssql+pyodbc://@LAPTOP-CJ0JLQGR\SQLEXPRESS/ResumeScreeningDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

If using SQL username/password, update the URL manually.

## Notes

- Keep database scripts in the project for examiner review.
- Do not store private SQL passwords in README files.
- Use SSMS to inspect tables during demo.
