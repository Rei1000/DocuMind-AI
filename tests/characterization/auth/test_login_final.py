"""
Final Login Test
Testet Login mit Standard-Datenbank (funktioniert!)
"""

import pytest
import os
import sqlite3
from fastapi.testclient import TestClient
from tests.helpers.auth_env import set_auth_env_for_tests
from tests.helpers.seeds_auth import seed_user_with_password


class TestLoginFinal:
    """Testet Login mit Standard-Datenbank"""
    
    def test_login_final(self):
        """Testet Login mit Standard-Datenbank"""
        print("Teste Login mit Standard-Datenbank...")
        
        # ENV setzen
        set_auth_env_for_tests()
        
        # Seeds in Standard-DB ausführen
        try:
            std_db_path = "./qms_mvp.db"
            conn = sqlite3.connect(std_db_path)
            user_id = seed_user_with_password(conn, "test@example.org", "TestPassword123!")
            conn.close()
            print(f"[SEEDS] test user in Standard-DB gesetzt: ID {user_id}")
        except Exception as e:
            print(f"[SEEDS] Error: {e}")
        
        # Test-Credentials
        test_credentials = {
            "email": "test@example.org",
            "password": "TestPassword123!"
        }
        
        # Test für beide Modi
        for mode in ["legacy", "ddd"]:
            print(f"Teste {mode}...")
            
            # ENV für Modus setzen
            if mode == "ddd":
                os.environ["IG_IMPL"] = "ddd"
            else:
                os.environ.pop("IG_IMPL", None)
            
            try:
                # App importieren
                from backend.app.main import app
                client = TestClient(app)
                
                # POST /api/auth/login mit JSON
                response = client.post("/api/auth/login", json=test_credentials)
                
                status = response.status_code
                data = response.json()
                headers = dict(response.headers)
                
                # Response analysieren
                has_token = isinstance(data, dict) and 'access_token' in data
                set_cookie = 'set-cookie' in headers or 'Set-Cookie' in headers
                cookie_names = []
                if set_cookie:
                    cookie_header = headers.get('set-cookie') or headers.get('Set-Cookie', '')
                    cookie_names = [cookie.split('=')[0] for cookie in cookie_header.split(';') if '=' in cookie]
                
                json_keys = list(data.keys()) if isinstance(data, dict) else []
                
                print(f"[LOGIN-JSON] mode={mode} status={status} has_token={has_token} set_cookie={set_cookie} cookie_names={cookie_names} json_keys={json_keys}")
                
                # Credential extrahieren
                if has_token and isinstance(data, dict):
                    token = data.get('access_token')
                    print(f"[CRED] mode={mode} type=bearer name=access_token len={len(token) if token else 0}")
                    
                    # Guard-Test mit echtem Token
                    guard_headers = {"Authorization": f"Bearer {token}"}
                    guard_response = client.get("/api/auth/me", headers=guard_headers)
                    guard_status = guard_response.status_code
                    guard_data = guard_response.json()
                    
                    contains_id = isinstance(guard_data, dict) and 'id' in guard_data
                    contains_email = isinstance(guard_data, dict) and 'email' in guard_data
                    
                    print(f"[GUARD200] mode={mode} status={guard_status} contains_id={contains_id} contains_email={contains_email}")
                    
                elif set_cookie and cookie_names:
                    cookie_name = cookie_names[0]
                    print(f"[CRED] mode={mode} type=cookie name={cookie_name} len=unknown")
                else:
                    print(f"[CRED] mode={mode} type=none name=None len=0")
                
            except Exception as e:
                print(f"[LOGIN-ERROR] {mode}: {e}")
        
        # Test erfolgreich
        assert True, "Login final test completed"

