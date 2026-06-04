USE resume_screening;
GO

IF OBJECT_ID('dbo.company_resumes', 'U') IS NULL
BEGIN
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

    CREATE INDEX IX_company_resumes_company_id ON dbo.company_resumes(company_id);
END;
GO

IF OBJECT_ID('dbo.company_resume_matches', 'U') IS NULL
BEGIN
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

    CREATE INDEX IX_company_resume_matches_job_id ON dbo.company_resume_matches(job_id);
    CREATE INDEX IX_company_resume_matches_final_score ON dbo.company_resume_matches(final_score DESC);
END;
GO
