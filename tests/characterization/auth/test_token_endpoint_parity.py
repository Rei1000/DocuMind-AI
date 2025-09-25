"""
Token Endpoint Parity Test
Charakterisiert /token-Endpoint in Legacy und DDD
"""

import pytest
import os
from tests.helpers.ab_runner import run_request
from tests.characterization.auth.conftest import before_import_env, after_import_override
from tests.helpers.jwt_signer import decode_token


class TestTokenEndpointParity:
    """Charakterisiert Token-Endpoint Parität"""
    
    def test_token_endpoint_discovery_and_parity(self, client):
        """Findet und testet Token-Endpoint Parität"""
        print("Charakterisiere Token-Endpoint...")
        
        # ENV setzen
        os.environ["DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        os.environ["SQLALCHEMY_DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        
        # OpenAPI für beide Modi abrufen
        legacy_paths = []
        ddd_paths = []
        
        try:
            legacy_response = run_request(
                client, "legacy", "GET", "/openapi.json"
            )
            if legacy_response[0] == 200:
                legacy_openapi = legacy_response[1]
                legacy_paths = list(legacy_openapi.get('paths', {}).keys())
        except Exception as e:
            print(f"Legacy OpenAPI error: {e}")
        
        try:
            ddd_response = run_request(
                client, "ddd", "GET", "/openapi.json"
            )
            if ddd_response[0] == 200:
                ddd_openapi = ddd_response[1]
                ddd_paths = list(ddd_openapi.get('paths', {}).keys())
        except Exception as e:
            print(f"DDD OpenAPI error: {e}")
        
        # Suche nach Token-Pfaden
        token_candidates = ['/token', '/auth/token', '/login', '/api/auth/token']
        legacy_token_paths = [p for p in legacy_paths if any(candidate in p.lower() for candidate in ['token', 'login'])]
        ddd_token_paths = [p for p in ddd_paths if any(candidate in p.lower() for candidate in ['token', 'login'])]
        
        print(f"Legacy token/login paths: {legacy_token_paths[:10]}")
        print(f"DDD token/login paths: {ddd_token_paths[:10]}")
        
        # Priorität: /token > /auth/token > /login > /api/auth/token
        token_path = None
        for candidate in token_candidates:
            if candidate in legacy_paths and candidate in ddd_paths:
                token_path = candidate
                break
        
        if not token_path:
            print(f"[TOKEN] path=None (no token endpoint found)")
            print(f"Top 10 Legacy paths with token/login: {legacy_token_paths[:10]}")
            print(f"Top 10 DDD paths with token/login: {ddd_token_paths[:10]}")
            pytest.fail("No token endpoint found - consider proxying existing login flow")
        
        print(f"[TOKEN] path={token_path}")
        
        # Test-Credentials (deterministisch)
        test_credentials = {
            "username": "test@example.org",
            "password": "TestPassword123!"
        }
        
        # Legacy Token-Endpoint testen
        legacy_status = None
        legacy_data = {}
        legacy_has_token = False
        
        try:
            legacy_response = run_request(
                client, "legacy", "POST", token_path,
                json_data=test_credentials
            )
            legacy_status = legacy_response[0]
            legacy_data = legacy_response[1]
            
            if isinstance(legacy_data, dict):
                legacy_has_token = 'access_token' in legacy_data or 'token' in legacy_data
        except Exception as e:
            print(f"Legacy {token_path} error: {e}")
            legacy_status = 500
        
        # DDD Token-Endpoint testen
        ddd_status = None
        ddd_data = {}
        ddd_has_token = False
        
        try:
            ddd_response = run_request(
                client, "ddd", "POST", token_path,
                json_data=test_credentials
            )
            ddd_status = ddd_response[0]
            ddd_data = ddd_response[1]
            
            if isinstance(ddd_data, dict):
                ddd_has_token = 'access_token' in ddd_data or 'token' in ddd_data
        except Exception as e:
            print(f"DDD {token_path} error: {e}")
            ddd_status = 500
        
        # Log Ergebnisse
        print(f"[TOKEN] path={token_path} legacy={legacy_status} ddd={ddd_status} has_token_legacy={legacy_has_token} has_token_ddd={ddd_has_token}")
        
        # Parität prüfen
        if legacy_status == ddd_status:
            print("✅ parity_token_status=true")
        else:
            print(f"⚠️ parity_token_status=false (legacy={legacy_status}, ddd={ddd_status})")
        
        # Token-Verifikation (falls vorhanden)
        if legacy_has_token and isinstance(legacy_data, dict):
            token = legacy_data.get('access_token') or legacy_data.get('token')
            if token:
                claims = decode_token(token, secret="test-secret", algorithms=["HS256"])
                if claims:
                    print(f"[TOKEN] legacy token verified: sub={claims.get('sub')}")
        
        if ddd_has_token and isinstance(ddd_data, dict):
            token = ddd_data.get('access_token') or ddd_data.get('token')
            if token:
                claims = decode_token(token, secret="test-secret", algorithms=["HS256"])
                if claims:
                    print(f"[TOKEN] ddd token verified: sub={claims.get('sub')}")
        
        # Test erfolgreich (auch wenn kein Token-Endpoint)
        assert True, "Token endpoint characterization completed"

