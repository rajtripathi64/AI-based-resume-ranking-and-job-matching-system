# Recruiter Resume Test Dataset

Generated from the public Hugging Face dataset already stored in this project:

```text
ml/datasets/job_resume_fit/train.csv
```

Files generated:

```text
resumes/*.txt = 120 resume files
job_description.txt = one recruiter JD used for ranking test
candidate_names.txt = comma-separated names for upload API
```

Purpose:

- Test recruiter flow with 100+ resumes.
- Verify bulk ranking returns candidates sorted by final model score.
- Keep test resumes separate from real uploaded resumes.
