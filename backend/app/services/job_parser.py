"""Job description parsing helpers."""

import re

from app.services.skill_normalization import extract_skills_from_text, skill_family_coverage_score

SECTION_WEIGHTS = {
    "required": 0.60,
    "preferred": 0.30,
    "soft": 0.10,
}


def clean_job_description(description: str) -> str:
    lines = [line.strip() for line in description.replace("\r", "\n").split("\n")]
    return "\n".join(line for line in lines if line)


def normalize_heading(line: str) -> str:
    return re.sub(r"[^a-z0-9 &/+-]", "", line.lower()).strip()


def detect_section(line: str) -> str | None:
    heading = normalize_heading(line)
    if not heading or len(heading.split()) > 8:
        return None
    if any(keyword in heading for keyword in ("preferred", "nice to have", "bonus")):
        return "preferred"
    if any(keyword in heading for keyword in ("soft skill", "competenc", "communication", "teamwork")):
        return "soft"
    if any(keyword in heading for keyword in ("required", "requirement", "qualification", "skill")):
        return "required"
    if any(keyword in heading for keyword in ("responsibil", "duty", "role", "description")):
        return "responsibilities"
    return None


def split_job_description_sections(description: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {
        "overview": [],
        "responsibilities": [],
        "required": [],
        "preferred": [],
        "soft": [],
    }
    current = "overview"
    for line in clean_job_description(description).split("\n"):
        section = detect_section(line)
        if section:
            current = section
            continue
        sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def extract_required_skills(description: str) -> list[str]:
    return extract_skills_from_text(description)


def extract_sectioned_job_skills(description: str) -> dict[str, list[str]]:
    sections = split_job_description_sections(description)
    return {
        section_name: extract_skills_from_text(section_text)
        for section_name, section_text in sections.items()
    }


def section_skill_overlap_score(resume_skills: str | None, section_skills: list[str]) -> float:
    return skill_family_coverage_score(resume_skills, ", ".join(section_skills))


def weighted_job_skill_score(resume_skills: str | None, description: str) -> float:
    sectioned_skills = extract_sectioned_job_skills(description)
    weighted_scores: list[tuple[float, float]] = []

    for section_name, weight in SECTION_WEIGHTS.items():
        skills = sectioned_skills.get(section_name, [])
        if skills:
            weighted_scores.append((section_skill_overlap_score(resume_skills, skills), weight))

    if not weighted_scores:
        all_skills = extract_required_skills(description)
        return section_skill_overlap_score(resume_skills, all_skills)

    available_weight = sum(weight for _, weight in weighted_scores)
    if available_weight == 0:
        return 0.0
    score = sum(score * weight for score, weight in weighted_scores) / available_weight
    return round(score, 2)


