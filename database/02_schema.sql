USE resume_screening;
GO

IF OBJECT_ID('dbo.company_resume_matches', 'U') IS NOT NULL DROP TABLE dbo.company_resume_matches;
IF OBJECT_ID('dbo.matches', 'U') IS NOT NULL DROP TABLE dbo.matches;
IF OBJECT_ID('dbo.model_runs', 'U') IS NOT NULL DROP TABLE dbo.model_runs;
IF OBJECT_ID('dbo.company_resumes', 'U') IS NOT NULL DROP TABLE dbo.company_resumes;
IF OBJECT_ID('dbo.jobs', 'U') IS NOT NULL DROP TABLE dbo.jobs;
IF OBJECT_ID('dbo.resumes', 'U') IS NOT NULL DROP TABLE dbo.resumes;
IF OBJECT_ID('dbo.company_profiles', 'U') IS NOT NULL DROP TABLE dbo.company_profiles;
IF OBJECT_ID('dbo.candidate_profiles', 'U') IS NOT NULL DROP TABLE dbo.candidate_profiles;
IF OBJECT_ID('dbo.users', 'U') IS NOT NULL DROP TABLE dbo.users;
GO

CREATE TABLE dbo.users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL,
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT CK_users_role CHECK (role IN ('candidate', 'company', 'admin'))
);
GO

CREATE TABLE dbo.candidate_profiles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(30) NULL,
    location VARCHAR(150) NULL,
    experience_years DECIMAL(4,1) NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_candidate_profiles_users FOREIGN KEY (user_id) REFERENCES dbo.users(id)
);
GO

CREATE TABLE dbo.company_profiles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    company_name VARCHAR(180) NOT NULL,
    industry VARCHAR(120) NULL,
    website VARCHAR(255) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_company_profiles_users FOREIGN KEY (user_id) REFERENCES dbo.users(id)
);
GO

CREATE TABLE dbo.resumes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    candidate_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    parsed_text NVARCHAR(MAX) NULL,
    extracted_skills NVARCHAR(MAX) NULL,
    education NVARCHAR(MAX) NULL,
    experience_summary NVARCHAR(MAX) NULL,
    uploaded_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_resumes_candidate_profiles FOREIGN KEY (candidate_id) REFERENCES dbo.candidate_profiles(id)
);
GO

CREATE TABLE dbo.jobs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    company_id INT NOT NULL,
    title VARCHAR(180) NOT NULL,
    description NVARCHAR(MAX) NOT NULL,
    required_skills NVARCHAR(MAX) NULL,
    min_experience DECIMAL(4,1) NOT NULL DEFAULT 0,
    location VARCHAR(150) NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'open',
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_jobs_company_profiles FOREIGN KEY (company_id) REFERENCES dbo.company_profiles(id),
    CONSTRAINT CK_jobs_status CHECK (status IN ('open', 'closed'))
);
GO

CREATE TABLE dbo.company_resumes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    company_id INT NOT NULL,
    candidate_name VARCHAR(150) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    parsed_text NVARCHAR(MAX) NULL,
    extracted_skills NVARCHAR(MAX) NULL,
    uploaded_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_company_resumes_company_profiles FOREIGN KEY (company_id) REFERENCES dbo.company_profiles(id)
);
GO

CREATE TABLE dbo.matches (
    id INT IDENTITY(1,1) PRIMARY KEY,
    resume_id INT NOT NULL,
    job_id INT NOT NULL,
    similarity_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    skill_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    experience_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    final_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    explanation NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_matches_resumes FOREIGN KEY (resume_id) REFERENCES dbo.resumes(id),
    CONSTRAINT FK_matches_jobs FOREIGN KEY (job_id) REFERENCES dbo.jobs(id),
    CONSTRAINT UQ_matches_resume_job UNIQUE (resume_id, job_id)
);
GO

CREATE TABLE dbo.company_resume_matches (
    id INT IDENTITY(1,1) PRIMARY KEY,
    company_resume_id INT NOT NULL,
    job_id INT NOT NULL,
    similarity_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    skill_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    final_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    explanation NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_company_resume_matches_company_resumes FOREIGN KEY (company_resume_id) REFERENCES dbo.company_resumes(id),
    CONSTRAINT FK_company_resume_matches_jobs FOREIGN KEY (job_id) REFERENCES dbo.jobs(id),
    CONSTRAINT UQ_company_resume_matches_resume_job UNIQUE (company_resume_id, job_id)
);
GO

CREATE TABLE dbo.model_runs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    model_name VARCHAR(120) NOT NULL,
    dataset_name VARCHAR(180) NULL,
    accuracy DECIMAL(5,2) NULL,
    precision_score DECIMAL(5,2) NULL,
    recall_score DECIMAL(5,2) NULL,
    f1_score DECIMAL(5,2) NULL,
    notes NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

CREATE INDEX IX_candidate_profiles_user_id ON dbo.candidate_profiles(user_id);
CREATE INDEX IX_company_profiles_user_id ON dbo.company_profiles(user_id);
CREATE INDEX IX_resumes_candidate_id ON dbo.resumes(candidate_id);
CREATE INDEX IX_jobs_company_id ON dbo.jobs(company_id);
CREATE INDEX IX_jobs_status ON dbo.jobs(status);
CREATE INDEX IX_company_resumes_company_id ON dbo.company_resumes(company_id);
CREATE INDEX IX_matches_resume_id ON dbo.matches(resume_id);
CREATE INDEX IX_matches_job_id ON dbo.matches(job_id);
CREATE INDEX IX_matches_final_score ON dbo.matches(final_score DESC);
CREATE INDEX IX_company_resume_matches_company_resume_id ON dbo.company_resume_matches(company_resume_id);
CREATE INDEX IX_company_resume_matches_job_id ON dbo.company_resume_matches(job_id);
CREATE INDEX IX_company_resume_matches_final_score ON dbo.company_resume_matches(final_score DESC);
GO
