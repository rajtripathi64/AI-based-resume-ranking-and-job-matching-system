# Database Schema Draft

This is the first schema draft. We will refine it during Phase 3 when SQL Server integration begins.

## users

- id: int primary key
- email: varchar unique
- password_hash: varchar
- role: candidate/company/admin
- is_active: bit
- created_at: datetime

## candidate_profiles

- id: int primary key
- user_id: foreign key users.id
- full_name: varchar
- phone: varchar
- location: varchar
- experience_years: decimal
- created_at: datetime

## company_profiles

- id: int primary key
- user_id: foreign key users.id
- company_name: varchar
- industry: varchar
- website: varchar
- created_at: datetime

## resumes

- id: int primary key
- candidate_id: foreign key candidate_profiles.id
- file_name: varchar
- file_path: varchar
- parsed_text: nvarchar(max)
- extracted_skills: nvarchar(max)
- education: nvarchar(max)
- experience_summary: nvarchar(max)
- uploaded_at: datetime

## jobs

- id: int primary key
- company_id: foreign key company_profiles.id
- title: varchar
- description: nvarchar(max)
- required_skills: nvarchar(max)
- min_experience: decimal
- location: varchar
- status: open/closed
- created_at: datetime

## matches

- id: int primary key
- resume_id: foreign key resumes.id
- job_id: foreign key jobs.id
- similarity_score: decimal
- skill_score: decimal
- experience_score: decimal
- final_score: decimal
- explanation: nvarchar(max)
- created_at: datetime

## model_runs

- id: int primary key
- model_name: varchar
- dataset_name: varchar
- accuracy: decimal
- precision_score: decimal
- recall_score: decimal
- f1_score: decimal
- notes: nvarchar(max)
- created_at: datetime
