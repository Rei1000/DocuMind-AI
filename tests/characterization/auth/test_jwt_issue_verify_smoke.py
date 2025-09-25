"""
JWT Issue/Verify Smoke Test
Testet JWT-Generierung, Verifikation und Signatur-Schutz
"""

import pytest
import sqlite3
from tests.helpers.ab_runner import run_request
from tests.helpers.seeds_auth import seed_user_with_password
from tests.helpers.jwt_utils import set_test_secret, issue_test_jwt, decode_jwt
from tests.characterization.auth.conftest import before_import_env, after_import_override


class TestJwtIssueVerifySmoke:
    """Smoke-Tests für JWT Issue/Verify"""
    
    def test_jwt_sign_verify_and_tamper_protection(self, client):
        """Testet JWT-Signatur, Verifikation und Manipulationsschutz"""
        print("Teste JWT Issue/Verify Smoke...")
        
        # Test-Secret setzen
        set_test_secret("test-secret")
        
        # Seeds anwenden
        db_path = "/Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        with sqlite3.connect(db_path) as conn:
            user_id = seed_user_with_password(conn, "jwt@local", "P@ssw0rd!")
        
        # JWT generieren
        token = issue_test_jwt(user_id, "jwt@local", is_superuser=True)
        assert token is not None, "JWT token generation failed"
        
        # JWT dekodieren und Claims prüfen
        claims = decode_jwt(token)
        assert claims is not None, "JWT decode failed"
        assert "sub" in claims, "Missing 'sub' claim in JWT"
        assert claims.get("sub") == str(user_id), f"Wrong user ID in JWT: {claims.get('sub')} != {user_id}"
        
        # Superuser oder Admin-Rolle prüfen
        is_superuser = claims.get("is_superuser", False)
        has_admin_role = "admin" in str(claims.get("roles", []))
        assert is_superuser or has_admin_role, f"No admin privileges in JWT: {claims}"
        
        # Manipulation testen (1 Zeichen ändern)
        tampered_token = token[:-1] + "X"
        tampered_claims = decode_jwt(tampered_token)
        assert tampered_claims is None, "Tampered JWT should fail verification"
        
        print("✅ JWT sign/verify ok")

