USE resume_screening;
GO

SELECT
    u.id AS user_id,
    u.email,
    u.role,
    cp.full_name AS candidate_name,
    co.company_name
FROM dbo.users u
LEFT JOIN dbo.candidate_profiles cp ON cp.user_id = u.id
LEFT JOIN dbo.company_profiles co ON co.user_id = u.id;
GO

SELECT
    j.id AS job_id,
    j.title,
    co.company_name,
    j.status
FROM dbo.jobs j
INNER JOIN dbo.company_profiles co ON co.id = j.company_id;
GO

SELECT
    m.id AS match_id,
    cp.full_name AS candidate_name,
    j.title AS job_title,
    co.company_name,
    m.final_score
FROM dbo.matches m
INNER JOIN dbo.resumes r ON r.id = m.resume_id
INNER JOIN dbo.candidate_profiles cp ON cp.id = r.candidate_id
INNER JOIN dbo.jobs j ON j.id = m.job_id
INNER JOIN dbo.company_profiles co ON co.id = j.company_id
ORDER BY m.final_score DESC;
GO
