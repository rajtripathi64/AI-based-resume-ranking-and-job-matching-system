"""Tests for authentication security helpers."""

import unittest

from jose import jwt

from app.core.config import settings
from app.core.security import ALGORITHM, create_access_token, hash_password, verify_password


class AuthSecurityTests(unittest.TestCase):
    def test_password_hash_verification(self):
        password_hash = hash_password("Test1234")

        self.assertNotEqual(password_hash, "Test1234")
        self.assertTrue(verify_password("Test1234", password_hash))
        self.assertFalse(verify_password("Wrong1234", password_hash))

    def test_access_token_contains_subject_and_claims(self):
        token = create_access_token(subject="42", claims={"role": "candidate"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        self.assertEqual(payload["sub"], "42")
        self.assertEqual(payload["role"], "candidate")
        self.assertIn("exp", payload)


if __name__ == "__main__":
    unittest.main()
