"""Tests for resume parsing and skill/name extraction."""

import tempfile
import unittest
from pathlib import Path

from fastapi import HTTPException

from app.api.routes.resumes import validate_extension
from app.services.resume_parser import extract_basic_skills, extract_candidate_name, parse_resume_file


class ResumeParserTests(unittest.TestCase):
    def test_txt_resume_is_cleaned_and_parsed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            resume_path = Path(temp_dir) / "resume.txt"
            resume_path.write_text("\ufeff Raj Tripathi \r\n\r\n Python  SQL  React ", encoding="utf-8")

            parsed = parse_resume_file(resume_path)

        self.assertEqual(parsed, "Raj Tripathi\nPython  SQL  React")

    def test_skill_extraction_finds_core_web_skills(self):
        skills = extract_basic_skills("Built React, Node.js, Express REST APIs with MongoDB, SQL, Git and AWS.")

        self.assertIn("react", skills)
        self.assertIn("node.js", skills)
        self.assertIn("express", skills)
        self.assertIn("mongodb", skills)
        self.assertIn("sql", skills)
        self.assertIn("git", skills)
        self.assertIn("aws", skills)

    def test_single_word_name_beats_education_line(self):
        text = "Rishabh\nPhone: +91-9999999999\nEmail: r@example.com\nEducation\nB.Tech in Computer Science"

        self.assertEqual(extract_candidate_name(text), "Rishabh")

    def test_noisy_education_line_is_not_returned_as_name(self):
        text = "Phone: +91-9999999999\nEmail: test@example.com\nB.Tech In Computer Science\nSkills\nPython"

        self.assertIsNone(extract_candidate_name(text))

    def test_bad_upload_extension_is_rejected(self):
        with self.assertRaises(HTTPException):
            validate_extension("malware.exe")

    def test_unsupported_parse_file_type_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            resume_path = Path(temp_dir) / "resume.exe"
            resume_path.write_text("not a resume", encoding="utf-8")

            with self.assertRaises(ValueError):
                parse_resume_file(resume_path)


if __name__ == "__main__":
    unittest.main()
