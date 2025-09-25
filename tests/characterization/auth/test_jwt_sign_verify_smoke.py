"""
JWT Sign/Verify Smoke Test
Testet JWT-Generierung und Verifikation
"""

import pytest
import os
from tests.helpers.jwt_signer import make_access_token, decode_token


class TestJwtSignVerifySmoke:
    """Smoke-Tests für JWT Sign/Verify"""
    
    def test_jwt_user_token_sign_verify(self, client):
        """Testet JWT-Sign/Verify für normalen User"""
        print("Teste JWT User Token Sign/Verify...")
        
        # ENV setzen
        os.environ["DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        os.environ["SQLALCHEMY_DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        
        # User-Token erstellen
        payload = {
            "sub": "normal.user@example.org",
            "role": "user",
            "user_id": 123
        }
        
        token = make_access_token(payload, secret="test-secret", algorithm="HS256", minutes=5)
        assert token is not None, "Token generation failed"
        
        # Token verifizieren
        claims = decode_token(token, secret="test-secret", algorithms=["HS256"])
        assert claims is not None, "Token decode failed"
        
        # Claims prüfen (sub enthält user_id, email ist separater Claim)
        assert claims.get("sub") == "123", f"Wrong sub: {claims.get('sub')}"
        assert claims.get("email") == "normal.user@example.org", f"Wrong email: {claims.get('email')}"
        assert claims.get("user_id") == 123, f"Wrong user_id: {claims.get('user_id')}"
        assert "exp" in claims, "Missing exp claim"
        assert "iat" in claims, "Missing iat claim"
        
        print("[JWT-SMOKE] kind=user ok=true")
    
    def test_jwt_admin_token_sign_verify(self, client):
        """Testet JWT-Sign/Verify für Admin"""
        print("Teste JWT Admin Token Sign/Verify...")
        
        # ENV setzen
        os.environ["DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        os.environ["SQLALCHEMY_DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        
        # Admin-Token erstellen
        payload = {
            "sub": "qms.admin@example.org",
            "role": "qms.admin",
            "user_id": 1,
            "is_superuser": True
        }
        
        token = make_access_token(payload, secret="test-secret", algorithm="HS256", minutes=5)
        assert token is not None, "Token generation failed"
        
        # Token verifizieren
        claims = decode_token(token, secret="test-secret", algorithms=["HS256"])
        assert claims is not None, "Token decode failed"
        
        # Claims prüfen (sub enthält user_id, email ist separater Claim)
        assert claims.get("sub") == "1", f"Wrong sub: {claims.get('sub')}"
        assert claims.get("email") == "qms.admin@example.org", f"Wrong email: {claims.get('email')}"
        assert claims.get("user_id") == 1, f"Wrong user_id: {claims.get('user_id')}"
        assert claims.get("is_superuser") == True, f"Wrong is_superuser: {claims.get('is_superuser')}"
        assert "exp" in claims, "Missing exp claim"
        assert "iat" in claims, "Missing iat claim"
        
        print("[JWT-SMOKE] kind=admin ok=true")
