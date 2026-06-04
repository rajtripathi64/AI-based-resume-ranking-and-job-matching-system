# job_resume_fit Dataset

Local copy of the public Hugging Face dataset used in Phase 9 model training.

Source:

```text
https://huggingface.co/datasets/batuhanmtl/job_resume_fit
```

Local file:

```text
train.csv
```

Rows:

```text
2385
```

Columns:

```text
ID
resume_text
job_text
category
job_required_skills
resume_skill_list
ai_matched_skills
ai_match_score
skill_string_match_score
fuzzy_match_score
```

Project use:

- Train Logistic Regression, SVM, KNN, Random Forest, and XGBoost.
- Compare accuracy, precision, recall, and F1 score.
- Keep public training data separate from private uploaded resumes.

Privacy note:

This is a public dataset for training/demo only. User-uploaded resumes in the app should still be handled with temporary upload or controlled database storage rules.
