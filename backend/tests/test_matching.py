"""Tests for matching score behavior."""

import unittest
from unittest.mock import patch

from app.services.embedding_service import final_match_score
from app.services.ranking_model import (
    REQUIRED_SKILL_WEIGHT,
    RESUME_QUALITY_WEIGHT,
    SBERT_WEIGHT,
    XGBOOST_WEIGHT,
    build_live_features,
    ranking_model_score,
)


class MatchingScoreTests(unittest.TestCase):
    def test_sbert_weight_stays_in_required_range(self):
        self.assertEqual(REQUIRED_SKILL_WEIGHT, 0.42)
        self.assertEqual(SBERT_WEIGHT, 0.30)
        self.assertEqual(XGBOOST_WEIGHT, 0.20)
        self.assertEqual(RESUME_QUALITY_WEIGHT, 0.08)
        self.assertAlmostEqual(
            REQUIRED_SKILL_WEIGHT + SBERT_WEIGHT + XGBOOST_WEIGHT + RESUME_QUALITY_WEIGHT,
            1.0,
        )

    def test_live_features_include_hybrid_signals(self):
        features = build_live_features(
            resume_text="React Node Express MongoDB Git",
            job_text="Full stack React Node APIs",
            resume_skills="react, node.js, express, mongodb, git",
            job_skills="react, node.js, express, mongodb, git",
            similarity_score=72,
            skill_match_score=100,
        )

        for column in [
            "sbert_similarity_score",
            "skill_string_match_score",
            "fuzzy_match_score",
            "alias_skill_overlap_score",
            "resume_skill_count",
            "job_skill_count",
            "skill_overlap_count",
        ]:
            self.assertIn(column, features.columns)

    def test_fallback_score_uses_sbert_and_skills_when_model_missing(self):
        score = final_match_score(similarity_score=80, skills_score=40)

        self.assertEqual(score, 58.0)

    def test_xgboost_led_score_blends_model_and_sbert(self):
        class MediumModel:
            def predict_proba(self, _features):
                return [[0.40, 0.60]]

        artifact = {"model": MediumModel(), "model_name": "TestXGBoost", "feature_names": None}
        with patch("app.services.ranking_model.load_ranking_artifact", return_value=artifact):
            score, method = ranking_model_score(
                resume_text="React Node Express MongoDB Git projects",
                job_text="Need React Node Express MongoDB Git",
                resume_skills="react, node.js, express, mongodb, git",
                job_skills="react, node.js, express, mongodb, git",
                similarity_score=50,
                skill_match_score=100,
            )

        self.assertGreater(score, 60)
        self.assertLess(score, 75)
        self.assertIn("required skills 42%", method)
        self.assertIn("section-SBERT 30%", method)
        self.assertIn("TestXGBoost", method)


if __name__ == "__main__":
    unittest.main()
