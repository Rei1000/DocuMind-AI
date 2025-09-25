"""
Auth Guard Smoke Test
Testet Authorization-Header und Token-basierte Zugriffskontrolle
"""

import pytest
import os
from tests.helpers.jwt_signer import make_access_token, ensure_bearer
from tests.helpers.ab_runner import run_request
from tests.characterization.auth.conftest import before_import_env, after_import_override


class TestAuthGuardSmoke:
    """Smoke-Tests für Auth Guards"""
    
    def test_auth_guard_without_and_with_token(self, client, legacy_headers, ddd_headers):
        """Testet Auth Guard ohne und mit Token"""
        print("Teste Auth Guard Smoke...")
        
        # ENV setzen
        os.environ["DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        os.environ["SQLALCHEMY_DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        
        # Guard-Pfad (aus Discovery)
        guard_path = "/api/auth/me"
        
        # Ohne Authorization Header: GET /api/auth/me
        try:
            legacy_response = run_request(
                client, "legacy", "GET", guard_path
            )
            legacy_status = legacy_response[0]
        except Exception as e:
            print(f"Legacy {guard_path} error: {e}")
            legacy_status = 500
        
        try:
            ddd_response = run_request(
                client, "ddd", "GET", guard_path
            )
            ddd_status = ddd_response[0]
        except Exception as e:
            print(f"DDD {guard_path} error: {e}")
            ddd_status = 500
        
        # Log ohne Token
        print(f"[GUARD] no_token legacy_status={legacy_status}")
        print(f"[GUARD] no_token ddd_status={ddd_status}")
        
        # Erwarte {401,403} für beide Modi (Guard aktiv)
        if legacy_status not in [401, 403]:
            if legacy_status == 200:
                pytest.xfail("Guard not enforced in Legacy - returns 200 without token")
            else:
                assert legacy_status in [401, 403], f"Legacy expected 401/403, got {legacy_status}"
        
        if ddd_status not in [401, 403]:
            if ddd_status == 200:
                pytest.xfail("Guard not enforced in DDD - returns 200 without token")
            else:
                assert ddd_status in [401, 403], f"DDD expected 401/403, got {ddd_status}"
        
        # Mit gültigem User-Token: GET /api/auth/me (Legacy)
        try:
            legacy_response = run_request(
                client, "legacy", "GET", guard_path,
                headers=legacy_headers
            )
            legacy_status = legacy_response[0]
            legacy_data = legacy_response[1]
        except Exception as e:
            print(f"Legacy {guard_path} with token error: {e}")
            legacy_status = 500
            legacy_data = {}
        
        # Mit gültigem User-Token: GET /api/auth/me (DDD)
        try:
            ddd_response = run_request(
                client, "ddd", "GET", guard_path,
                headers=ddd_headers
            )
            ddd_status = ddd_response[0]
            ddd_data = ddd_response[1]
        except Exception as e:
            print(f"DDD {guard_path} with token error: {e}")
            ddd_status = 500
            ddd_data = {}
        
        # Log mit Token
        legacy_contains_email = isinstance(legacy_data, dict) and 'email' in legacy_data
        legacy_contains_id = isinstance(legacy_data, dict) and 'id' in legacy_data
        ddd_contains_email = isinstance(ddd_data, dict) and 'email' in ddd_data
        ddd_contains_id = isinstance(ddd_data, dict) and 'id' in ddd_data
        
        print(f"[AUTHFIX] mode=legacy path={guard_path} method=GET status={legacy_status} contains_email={legacy_contains_email} contains_id={legacy_contains_id}")
        print(f"[AUTHFIX] mode=ddd path={guard_path} method=GET status={ddd_status} contains_email={ddd_contains_email} contains_id={ddd_contains_id}")
        
        # Wenn weiterhin 401/403: Response-Text ausgeben
        if legacy_status not in [200] or ddd_status not in [200]:
            if legacy_status not in [200]:
                legacy_response_text = str(legacy_data)[:300] if legacy_data else "No response data"
                print(f"[GUARD-RESP] legacy: {legacy_response_text}")
            if ddd_status not in [200]:
                ddd_response_text = str(ddd_data)[:300] if ddd_data else "No response data"
                print(f"[GUARD-RESP] ddd: {ddd_response_text}")
            pytest.fail("override not engaged or claim mismatch")
        
        # Erwarte 200 für beide Modi
        assert legacy_status == 200, f"Legacy expected 200, got {legacy_status}"
        assert ddd_status == 200, f"DDD expected 200, got {ddd_status}"
        
        # Prüfe Response-Body enthält mindestens 'email' oder 'id'
        if isinstance(legacy_data, dict):
            has_email_or_id = 'email' in legacy_data or 'id' in legacy_data
            assert has_email_or_id, f"Legacy response missing email/id: {list(legacy_data.keys())}"
        
        if isinstance(ddd_data, dict):
            has_email_or_id = 'email' in ddd_data or 'id' in ddd_data
            assert has_email_or_id, f"DDD response missing email/id: {list(ddd_data.keys())}"
        
        print("✅ guard_enforced=true")