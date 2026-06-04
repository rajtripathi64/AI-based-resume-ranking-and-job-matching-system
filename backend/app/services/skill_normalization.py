"""Skill extraction and normalization helpers.

This is a lightweight local skill taxonomy inspired by ESCO/O*NET-style skill
families. It avoids depending on an external taxonomy.
"""

from __future__ import annotations

from functools import lru_cache
import re

SKILL_ALIASES = {
    "js": "javascript", "java script": "javascript", "node js": "node.js", "nodejs": "node.js",
    "react js": "react", "reactjs": "react", "nextjs": "next.js", "next js": "next.js",
    "express js": "express", "spring framework": "spring", "springboot": "spring boot",
    "py": "python", "ml": "machine learning", "machine-learning": "machine learning",
    "deep-learning": "deep learning", "ai": "artificial intelligence", "gen ai": "generative ai",
    "genai": "generative ai", "chat gpt": "chatgpt", "ms sql": "sql", "mssql": "sql",
    "my sql": "mysql", "postgre sql": "postgresql", "mongo db": "mongodb", "no sql": "nosql",
    "nlp": "natural language processing", "natural-language-processing": "natural language processing",
    "cv": "computer vision", "ci cd": "ci/cd", "cicd": "ci/cd", "rest": "rest api",
    "restful api": "rest api", "tailwind css": "tailwind", "scikit learn": "scikit learn",
    "scikit-learn": "scikit learn", "sklearn": "scikit learn", "tf": "tensorflow",
    "google colaboratory": "google colab", "colab": "google colab", "jupyter": "jupyter notebook",
    "jupyter notebooks": "jupyter notebook", "visual studio code": "vs code", "vscode": "vs code",
    "git hub": "github", "ms excel": "excel", "msexcel": "excel", "powerbi": "power bi",
    "hr": "human resources", "human resource": "human resources", "recruitment": "recruiting",
    "recruiter": "recruiting", "sdlc": "software development lifecycle", "unit test": "unit testing",
    "unit tests": "unit testing",
}

SKILL_TAXONOMY = {
    "programming": ["python", "java", "javascript", "typescript", "c", "c++", "c#", "php", "go", "ruby", "kotlin", "swift", "r", "scala", "dart", "matlab", "shell scripting", "bash", "powershell"],
    "frontend": ["html", "css", "sass", "react", "redux", "next.js", "angular", "vue", "vite", "tailwind", "bootstrap", "material ui", "responsive design", "ui design", "figma", "web accessibility"],
    "backend": ["node.js", "express", "fastapi", "django", "flask", "spring", "spring boot", "laravel", "asp.net", "rest api", "graphql", "api", "microservices", "web services", "authentication", "jwt", "oauth", "software development lifecycle", "debugging", "code review", "testing", "unit testing"],
    "database": ["sql", "mysql", "postgresql", "mongodb", "nosql", "firebase", "redis", "oracle", "sqlite", "sql server", "database design", "data modeling", "etl", "query optimization", "stored procedure"],
    "cloud": ["aws", "azure", "gcp", "google cloud", "cloud computing", "ec2", "s3", "lambda", "azure functions", "cloud deployment", "serverless", "heroku", "vercel", "netlify"],
    "devops": ["git", "github", "gitlab", "bitbucket", "docker", "kubernetes", "jenkins", "ci/cd", "linux", "nginx", "terraform", "ansible", "devops", "deployment", "monitoring", "logging", "agile", "scrum"],
    "ai_ml": ["artificial intelligence", "machine learning", "deep learning", "natural language processing", "bert", "sbert", "llm", "generative ai", "openai", "chatgpt", "langchain", "rag", "computer vision", "tensorflow", "keras", "pytorch", "scikit learn", "xgboost", "opencv", "model evaluation", "feature engineering", "data cleaning", "preprocessing", "supervised learning", "unsupervised learning", "predictive analytics", "recommendation system", "classification", "regression", "clustering", "neural network"],
    "data_analytics": ["pandas", "numpy", "excel", "power bi", "tableau", "data visualization", "statistics", "analytics", "data analysis", "matplotlib", "seaborn", "dashboard", "reporting", "business intelligence", "data mining", "kaggle", "jupyter notebook", "google colab"],
    "cybersecurity": ["cybersecurity", "network security", "information security", "penetration testing", "vulnerability assessment", "firewall", "encryption", "security audit", "incident response", "risk assessment"],
    "project_management": ["project management", "product management", "stakeholder management", "planning", "scheduling", "jira", "trello", "documentation", "risk management", "time management", "budgeting"],
    "business_hr": ["human resources", "recruiting", "talent acquisition", "employee relations", "onboarding", "training", "performance management", "payroll", "hris", "compliance", "interviewing", "screening", "shortlisting", "sourcing", "negotiation", "customer service", "sales", "marketing", "crm"],
    "professional": ["communication", "leadership", "problem solving", "teamwork", "collaboration", "critical thinking", "adaptability", "attention to detail", "analytical skills", "presentation", "decision making"],
    "tools_platforms": ["vs code", "visual studio", "eclipse", "intellij", "postman", "swagger", "npm", "maven", "gradle", "android studio", "xcode", "wordpress", "shopify"],
}

ALL_SKILLS = sorted({skill for skills in SKILL_TAXONOMY.values() for skill in skills})
FAMILY_MATCH_CREDIT = 0.35
NON_TRANSFERABLE_FAMILIES = {"programming", "professional", "project_management", "business_hr", "tools_platforms"}
SUBSTITUTE_SKILLS_BY_FAMILY = {
    "frontend": {"react", "angular", "vue", "next.js", "redux"},
    "backend": {"node.js", "express", "fastapi", "django", "flask", "spring", "spring boot", "laravel", "asp.net"},
    "database": {"sql", "mysql", "postgresql", "mongodb", "nosql", "firebase", "redis", "oracle", "sqlite", "sql server"},
    "cloud": {"aws", "azure", "gcp", "google cloud", "ec2", "s3", "lambda", "serverless", "heroku", "vercel", "netlify"},
    "devops": {"docker", "kubernetes", "jenkins", "ci/cd", "terraform", "ansible", "devops", "deployment"},
    "ai_ml": {"machine learning", "deep learning", "natural language processing", "computer vision", "tensorflow", "keras", "pytorch", "scikit learn", "xgboost", "opencv"},
    "data_analytics": {"pandas", "numpy", "power bi", "tableau", "data visualization", "statistics", "analytics", "data analysis"},
    "cybersecurity": {"cybersecurity", "network security", "information security", "penetration testing", "vulnerability assessment"},
}


def normalize_skill(skill: str) -> str:
    value = skill.strip().lower()
    value = value.replace("_", " ").replace("-", " ").replace("/", " ")
    value = re.sub(r"[^a-z0-9#+. ]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return SKILL_ALIASES.get(value, value)


def skill_set(skills: str | None) -> set[str]:
    if not skills:
        return set()
    raw_items = []
    for chunk in skills.split(","):
        raw_items.extend(part.strip() for part in chunk.split(";"))
    return {normalize_skill(item) for item in raw_items if normalize_skill(item)}


def taxonomy_skills() -> set[str]:
    return {normalize_skill(skill) for skill in ALL_SKILLS}


def skill_families() -> dict[str, set[str]]:
    return {family: {normalize_skill(skill) for skill in skills} for family, skills in SKILL_TAXONOMY.items()}


def skill_pattern(skill: str) -> str:
    escaped = re.escape(skill).replace(r"\ ", r"[\s\-_/]+")
    return rf"(?<![a-z0-9+#.]){escaped}(?![a-z0-9+#.])"


@lru_cache(maxsize=1)
def get_spacy_model():
    try:
        import spacy
    except Exception:
        return None
    for model_name in ("en_core_web_sm", "en_core_web_md"):
        try:
            return spacy.load(model_name)
        except Exception:
            continue
    return None


def extract_spacy_candidates(text: str) -> set[str]:
    nlp = get_spacy_model()
    if nlp is None:
        return set()
    doc = nlp(text[:20000])
    candidates = set()
    for ent in doc.ents:
        if ent.label_ in {"ORG", "PRODUCT", "WORK_OF_ART", "LANGUAGE"}:
            candidates.add(normalize_skill(ent.text))
    for chunk in doc.noun_chunks:
        normalized = normalize_skill(chunk.text)
        if normalized in taxonomy_skills() or normalized in SKILL_ALIASES.values():
            candidates.add(normalized)
    return candidates


def extract_skills_from_text(text: str) -> list[str]:
    lower_text = (text or "").lower()
    found = set()
    for skill in taxonomy_skills():
        if re.search(skill_pattern(skill), lower_text):
            found.add(skill)
    for alias, canonical in SKILL_ALIASES.items():
        if re.search(skill_pattern(alias), lower_text):
            found.add(canonical)
    found.update(skill for skill in extract_spacy_candidates(text or "") if skill in taxonomy_skills())
    return sorted(found)


def family_credit_for_missing_skill(resume: set[str], missing_job_skill: str) -> float:
    for family_name, family_skills in skill_families().items():
        if missing_job_skill not in family_skills or family_name in NON_TRANSFERABLE_FAMILIES:
            continue
        substitute_skills = SUBSTITUTE_SKILLS_BY_FAMILY.get(family_name, family_skills)
        if missing_job_skill in substitute_skills and resume & substitute_skills:
            return FAMILY_MATCH_CREDIT
    return 0.0


def skill_family_coverage_score(resume_skills: str | None, job_skills: str | None) -> float:
    resume = skill_set(resume_skills)
    job = skill_set(job_skills)
    if not job:
        return 0.0
    score = 0.0
    for job_skill in job:
        if job_skill in resume:
            score += 1.0
        else:
            score += family_credit_for_missing_skill(resume, job_skill)
    return round((score / len(job)) * 100, 2)


def normalized_skill_overlap_count(first: str | None, second: str | None) -> int:
    return len(skill_set(first) & skill_set(second))


def normalized_skill_overlap_score(resume_skills: str | None, job_skills: str | None) -> float:
    resume = skill_set(resume_skills)
    job = skill_set(job_skills)
    if not job:
        return 0.0
    return round((len(resume & job) / len(job)) * 100, 2)


def normalized_skill_count(skills: str | None) -> int:
    return len(skill_set(skills))


def resume_quality_score(resume_text: str | None, resume_skills: str | None) -> float:
    text = (resume_text or "").lower()
    score = 0.0
    if len(text) >= 800:
        score += 25
    elif len(text) >= 400:
        score += 15
    skill_count = normalized_skill_count(resume_skills)
    score += min(skill_count * 3, 30)
    for section in ["project", "experience", "education", "skills"]:
        if section in text:
            score += 10
    return round(min(score, 100.0), 2)
