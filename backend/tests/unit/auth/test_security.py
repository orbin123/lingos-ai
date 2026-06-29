"""Unit tests for the auth security primitives (`app/core/security.py`).

These helpers (bcrypt hashing + JWT encode/decode) are exercised indirectly by
the auth integration tests, but their own contract — round-trips, wrong-input
rejection, tamper/expiry handling — was never asserted directly. Pure logic,
no DB, no network.
"""

from __future__ import annotations

from datetime import timedelta

from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("s3cret-pw")
        assert hashed != "s3cret-pw"
        assert hashed.startswith("$2")  # bcrypt marker

    def test_verify_accepts_correct_password(self):
        hashed = hash_password("correct horse battery")
        assert verify_password("correct horse battery", hashed) is True

    def test_verify_rejects_wrong_password(self):
        hashed = hash_password("correct horse battery")
        assert verify_password("wrong password", hashed) is False

    def test_same_password_hashes_differ_due_to_salt(self):
        a = hash_password("same-password")
        b = hash_password("same-password")
        assert a != b
        # …but both still verify.
        assert verify_password("same-password", a)
        assert verify_password("same-password", b)

    def test_blank_hash_returns_false_not_raises(self):
        # Google OAuth accounts carry no bcrypt hash; verifying against a blank
        # string must return False, never raise UnknownHashError.
        assert verify_password("anything", "") is False

    def test_unidentifiable_hash_returns_false_not_raises(self):
        assert verify_password("anything", "not-a-real-bcrypt-hash") is False


class TestJwt:
    def test_round_trips_subject(self):
        token = create_access_token({"sub": "42"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "42"
        assert "exp" in payload

    def test_extra_claims_round_trip(self):
        token = create_access_token({"sub": "7", "role": "learner"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["role"] == "learner"

    def test_tampered_token_is_rejected(self):
        token = create_access_token({"sub": "1"})
        # Corrupt the signature so it no longer matches the signed payload.
        assert decode_token(token + "tampered") is None

    def test_garbage_token_is_rejected(self):
        assert decode_token("not-a-real-jwt") is None

    def test_expired_token_is_rejected(self):
        token = create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-1))
        assert decode_token(token) is None

    def test_custom_expiry_is_honored(self):
        token = create_access_token({"sub": "1"}, expires_delta=timedelta(hours=2))
        assert decode_token(token) is not None
