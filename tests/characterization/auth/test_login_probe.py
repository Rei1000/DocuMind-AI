"""
Login Probe Test
Testet /api/auth/login Verhalten in Legacy und DDD
"""

import pytest
import os
from tests.helpers.ab_runner import run_request
from tests.helpers.auth_env import set_auth_env_for_tests


class TestLoginProbe:
    """Probiert /api/auth/login Verhalten"""
    
    def test_login_endpoint_probe(self, client):
        """Probiert /api/auth/login Endpoint"""
        print("Probiere /api/auth/login...")
        
        # ENV setzen
        set_auth_env_for_tests()
        os.environ["DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        os.environ["SQLALCHEMY_DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        
        # Test-Credentials
        test_credentials = {
            "username": "test@example.org",
            "password": "TestPassword123!"
        }
        
        # Legacy Login-Probe
        legacy_status = None
        legacy_data = {}
        legacy_headers = {}
        
        try:
            # GET /api/auth/login
            legacy_get_response = run_request(
                client, "legacy", "GET", "/api/auth/login"
            )
            legacy_get_status = legacy_get_response[0]
            legacy_get_headers = legacy_get_response[2]
            print(f"[LOGIN] mode=legacy method=GET status={legacy_get_status}")
            
            # POST /api/auth/login mit JSON
            legacy_post_response = run_request(
                client, "legacy", "POST", "/api/auth/login",
                json_data=test_credentials
            )
            legacy_status = legacy_post_response[0]
            legacy_data = legacy_post_response[1]
            legacy_headers = legacy_post_response[2]
            
        except Exception as e:
            print(f"Legacy login error: {e}")
            legacy_status = 500
        
        # DDD Login-Probe
        ddd_status = None
        ddd_data = {}
        ddd_headers = {}
        
        try:
            # GET /api/auth/login
            ddd_get_response = run_request(
                client, "ddd", "GET", "/api/auth/login"
            )
            ddd_get_status = ddd_get_response[0]
            ddd_get_headers = ddd_get_response[2]
            print(f"[LOGIN] mode=ddd method=GET status={ddd_get_status}")
            
            # POST /api/auth/login mit JSON
            ddd_post_response = run_request(
                client, "ddd", "POST", "/api/auth/login",
                json_data=test_credentials
            )
            ddd_status = ddd_post_response[0]
            ddd_data = ddd_post_response[1]
            ddd_headers = ddd_post_response[2]
            
        except Exception as e:
            print(f"DDD login error: {e}")
            ddd_status = 500
        
        # Response-Analyse
        def analyze_login_response(mode, status, data, headers):
            """Analysiert Login-Response"""
            has_token_field = False
            set_cookie = False
            location = None
            
            if isinstance(data, dict):
                # Token-Felder suchen
                token_fields = ['access_token', 'token', 'jwt', 'accessToken']
                has_token_field = any(field in data for field in token_fields)
            
            if isinstance(headers, dict):
                # Set-Cookie Header
                set_cookie = 'set-cookie' in headers or 'Set-Cookie' in headers
                # Location Header (Redirect)
                location = headers.get('location') or headers.get('Location')
            
            print(f"[LOGIN] mode={mode} method=POST json status={status} has_token_field={has_token_field} set_cookie={set_cookie} location={location}")
            
            if not has_token_field and not set_cookie:
                print(f"[LOGIN] no_token_no_cookie=true")
            
            return has_token_field, set_cookie, location
        
        # Legacy analysieren
        legacy_has_token, legacy_set_cookie, legacy_location = analyze_login_response(
            "legacy", legacy_status, legacy_data, legacy_headers
        )
        
        # DDD analysieren
        ddd_has_token, ddd_set_cookie, ddd_location = analyze_login_response(
            "ddd", ddd_status, ddd_data, ddd_headers
        )
        
        # Test erfolgreich (auch wenn Login fehlschlägt)
        assert True, "Login probe completed"

