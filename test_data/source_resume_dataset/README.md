# Source Resume Dataset for Demo

Source:

```text
https://huggingface.co/datasets/opensporks/resumes
```

This folder contains a 60-resume subset downloaded from the public Hugging Face dataset above. The files are saved as `.txt` because the project resume parser supports TXT files and plain text avoids PDF parsing issues during live presentation.

## Location

```text
test_data/source_resume_dataset/resumes
```

## How To Use In Demo

1. Open the recruiter matching page.
2. Paste or upload a job description.
3. Select multiple `.txt` resumes from `resumes/`.
4. Run ranking.
5. Show final percentage and matched required skills.

Suggested live demo size:

```text
10-20 resumes for fast demo
60 resumes for full bulk upload demo if laptop performance is good
```
