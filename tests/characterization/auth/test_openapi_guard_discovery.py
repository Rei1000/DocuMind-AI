"""
OpenAPI Guard Discovery Test
Findet Auth-Guard-Endpoints in Legacy und DDD
"""

import pytest
import json
from tests.helpers.ab_runner import run_request
from tests.characterization.auth.conftest import before_import_env, after_import_override


class TestOpenApiGuardDiscovery:
    """Findet Auth-Guard-Endpoints"""
    
    def test_legacy_openapi_guard_discovery(self, client):
        """Findet Legacy Auth-Guard-Endpoint"""
        print("Sondiere Legacy OpenAPI...")
        
        try:
            response = run_request(
                client, "legacy", "GET", "/openapi.json",
                before_import_env=before_import_env,
                after_import_override=after_import_override
            )
            
            if response[0] == 200:
                openapi = response[1]
                paths = list(openapi.get('paths', {}).keys())
                
                # Suche nach Guard-Pfaden
                user_paths = [p for p in paths if 'user' in p.lower()]
                me_paths = [p for p in paths if '/me' in p.lower()]
                
                print(f"Legacy paths with user: {user_paths[:10]}")
                print(f"Legacy paths with /me: {me_paths[:5]}")
                
                # Priorität: /me > /users/me > andere user-Pfade
                guard_path = None
                if me_paths:
                    guard_path = me_paths[0]
                elif '/api/users/me' in paths:
                    guard_path = '/api/users/me'
                elif '/users/me' in paths:
                    guard_path = '/users/me'
                elif user_paths:
                    guard_path = user_paths[0]
                
                if guard_path:
                    print(f"[GUARD] mode=legacy path={guard_path}")
                    assert True, f"Found guard path: {guard_path}"
                else:
                    print(f"[GUARD] mode=legacy path=None (no guard found)")
                    print(f"Top 10 user paths: {user_paths[:10]}")
                    pytest.fail("No guard path found in Legacy")
            else:
                print(f"Legacy OpenAPI status: {response[0]}")
                pytest.fail(f"Legacy OpenAPI not accessible: {response[0]}")
                
        except Exception as e:
            print(f"Legacy OpenAPI error: {e}")
            pytest.fail(f"Legacy OpenAPI error: {e}")
    
    def test_ddd_openapi_guard_discovery(self, client):
        """Findet DDD Auth-Guard-Endpoint"""
        print("Sondiere DDD OpenAPI...")
        
        try:
            response = run_request(
                client, "ddd", "GET", "/openapi.json",
                before_import_env=before_import_env,
                after_import_override=after_import_override
            )
            
            if response[0] == 200:
                openapi = response[1]
                paths = list(openapi.get('paths', {}).keys())
                
                # Suche nach Guard-Pfaden
                user_paths = [p for p in paths if 'user' in p.lower()]
                me_paths = [p for p in paths if '/me' in p.lower()]
                
                print(f"DDD paths with user: {user_paths[:10]}")
                print(f"DDD paths with /me: {me_paths[:5]}")
                
                # Priorität: /me > /users/me > andere user-Pfade
                guard_path = None
                if me_paths:
                    guard_path = me_paths[0]
                elif '/api/users/me' in paths:
                    guard_path = '/api/users/me'
                elif '/users/me' in paths:
                    guard_path = '/users/me'
                elif user_paths:
                    guard_path = user_paths[0]
                
                if guard_path:
                    print(f"[GUARD] mode=ddd path={guard_path}")
                    assert True, f"Found guard path: {guard_path}"
                else:
                    print(f"[GUARD] mode=ddd path=None (no guard found)")
                    print(f"Top 10 user paths: {user_paths[:10]}")
                    pytest.fail("No guard path found in DDD")
            else:
                print(f"DDD OpenAPI status: {response[0]}")
                pytest.fail(f"DDD OpenAPI not accessible: {response[0]}")
                
        except Exception as e:
            print(f"DDD OpenAPI error: {e}")
            pytest.fail(f"DDD OpenAPI error: {e}")

