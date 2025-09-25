"""
Guard Diagnostics Test
Systematische Diagnose der verbleibenden Auth-Guard-Fails
"""

import pytest
import os
import sqlite3
from tests.helpers.ab_runner import run_request
from tests.helpers.auth_flow import login_with_client, auth_headers, get_test_credentials
from tests.helpers.seeds_auth import seed_superuser_qms_admin, seed_basic_user, ensure_admin_role_assignment


class TestGuardDiagnostics:
    """Systematische Diagnose der Auth-Guard-Fails"""
    
    def test_openapi_guard_discovery(self, client):
        """Analysiert OpenAPI für Guard-Pfade und Security-Schemes"""
        print("Analysiere OpenAPI für Guard-Pfade...")
        
        # Legacy OpenAPI
        try:
            legacy_response = run_request(client, "legacy", "GET", "/openapi.json")
            if legacy_response[0] == 200:
                legacy_openapi = legacy_response[1]
                self._analyze_openapi_security(legacy_openapi, "legacy")
        except Exception as e:
            print(f"Legacy OpenAPI error: {e}")
        
        # DDD OpenAPI
        try:
            ddd_response = run_request(client, "ddd", "GET", "/openapi.json")
            if ddd_response[0] == 200:
                ddd_openapi = ddd_response[1]
                self._analyze_openapi_security(ddd_openapi, "ddd")
        except Exception as e:
            print(f"DDD OpenAPI error: {e}")
    
    def _analyze_openapi_security(self, openapi, mode):
        """Analysiert Security-Schemes und Guard-Pfade"""
        paths = openapi.get('paths', {})
        security_schemes = openapi.get('components', {}).get('securitySchemes', {})
        
        # Suche nach Guard-Pfaden
        guard_candidates = []
        for path in paths.keys():
            if '/me' in path.lower() or 'auth' in path.lower() or 'user' in path.lower():
                guard_candidates.append(path)
        
        print(f"[OPENAPI-GUARD] mode={mode} candidates={guard_candidates}")
        
        # Analysiere Security-Schemes detailliert
        for scheme_name, scheme in security_schemes.items():
            scheme_type = scheme.get('type', 'unknown')
            scheme_in = scheme.get('in', 'unknown')
            scheme_name_param = scheme.get('name', 'unknown')
            print(f"[OPENAPI-GUARD] mode={mode} scheme={scheme_name} type={scheme_type} in={scheme_in} name={scheme_name_param}")
        
        # Analysiere Security für Guard-Pfade mit Details
        for path in guard_candidates:
            path_info = paths[path]
            for method, operation in path_info.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE']:
                    security = operation.get('security', [])
                    if security:
                        print(f"[OPENAPI-GUARD] mode={mode} path={path} method={method} security={security}")
                        
                        # Analysiere spezifische Security-Anforderungen
                        for sec_req in security:
                            for sec_name, scopes in sec_req.items():
                                if scopes:
                                    print(f"[OPENAPI-GUARD] mode={mode} path={path} method={method} scheme={sec_name} scopes={scopes}")
                                else:
                                    print(f"[OPENAPI-GUARD] mode={mode} path={path} method={method} scheme={sec_name} scopes=[]")
    
    def test_guard_with_different_auth_methods(self, client):
        """Testet Guard mit verschiedenen Auth-Methoden"""
        print("Teste Guard mit verschiedenen Auth-Methoden...")
        
        # Seeds prüfen
        self._check_seeds()
        
        # Guard-Pfade testen
        guard_paths = ["/api/auth/me", "/api/users/me", "/auth/me", "/users/me"]
        
        for path in guard_paths:
            self._test_guard_path(client, path)
    
    def _check_seeds(self):
        """Prüft Seeds vor Guard-Tests"""
        db_path = "/Users/reiner/Documents/DocuMind-AI/.tmp/regression.db"
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Prüfe Users-Tabelle detailliert
                try:
                    cursor.execute("SELECT email, is_active, hashed_password FROM users LIMIT 5")
                    users = cursor.fetchall()
                    for user in users:
                        email, is_active, hashed_password = user
                        hash_prefix = hashed_password[:20] + "..." if hashed_password else "None"
                        print(f"[SEED] email={email} is_active={is_active} hash_prefix={hash_prefix}")
                except sqlite3.OperationalError:
                    print("[SEED] users table not found")
                
                # Prüfe Roles-Tabelle
                try:
                    cursor.execute("SELECT name FROM roles LIMIT 5")
                    roles = cursor.fetchall()
                    role_names = [role[0] for role in roles]
                    print(f"[SEED] roles={role_names}")
                except sqlite3.OperationalError:
                    print("[SEED] roles table not found")
                
                # Prüfe User-Roles-Zuordnung
                try:
                    cursor.execute("SELECT u.email, r.name FROM users u LEFT JOIN user_roles ur ON u.id = ur.user_id LEFT JOIN roles r ON ur.role_id = r.id LIMIT 5")
                    user_roles = cursor.fetchall()
                    for user_role in user_roles:
                        email, role = user_role
                        print(f"[SEED] user_role email={email} role={role}")
                except sqlite3.OperationalError:
                    print("[SEED] user_roles table not found")
                    
        except Exception as e:
            print(f"[SEED] error: {e}")
    
    def _test_guard_path(self, client, path):
        """Testet einen spezifischen Guard-Pfad"""
        print(f"Teste Guard-Pfad: {path}")
        
        # Test 1: Ohne Auth
        try:
            legacy_response = run_request(client, "legacy", "GET", path)
            legacy_status = legacy_response[0]
            legacy_data = legacy_response[1] if len(legacy_response) > 1 else {}
            print(f"[GUARD-TRY] mode=legacy path={path} kind=none status={legacy_status}")
        except Exception as e:
            print(f"[GUARD-TRY] mode=legacy path={path} kind=none error={e}")
        
        try:
            ddd_response = run_request(client, "ddd", "GET", path)
            ddd_status = ddd_response[0]
            ddd_data = ddd_response[1] if len(ddd_response) > 1 else {}
            print(f"[GUARD-TRY] mode=ddd path={path} kind=none status={ddd_status}")
        except Exception as e:
            print(f"[GUARD-TRY] mode=ddd path={path} kind=none error={e}")
        
        # Test 2: Mit Bearer Token
        credentials = get_test_credentials()
        user_creds = credentials["user"]
        
        # Stelle sicher, dass User aktiv ist
        from tests.helpers.auth_flow import ensure_user_active_in_db
        ensure_user_active_in_db(user_creds["email"])
        
        # Legacy Token
        try:
            legacy_status, legacy_token = login_with_client(client, user_creds["email"], user_creds["password"], "legacy")
            if legacy_token:
                legacy_headers = auth_headers(legacy_token)
                legacy_response = run_request(client, "legacy", "GET", path, headers=legacy_headers)
                legacy_status = legacy_response[0]
                legacy_data = legacy_response[1] if len(legacy_response) > 1 else {}
                has_id = isinstance(legacy_data, dict) and 'id' in legacy_data
                has_email = isinstance(legacy_data, dict) and 'email' in legacy_data
                print(f"[GUARD-TRY] mode=legacy path={path} kind=bearer status={legacy_status} has_id={has_id} has_email={has_email}")
                
                if legacy_status == 200:
                    print(f"[GUARD200] mode=legacy path={path} status=200 contains_id={has_id} contains_email={has_email}")
                else:
                    # Log Body für Debugging
                    body_str = str(legacy_data)[:200] if legacy_data else "No body"
                    print(f"[GUARD-DEBUG] mode=legacy path={path} status={legacy_status} body={body_str}")
        except Exception as e:
            print(f"[GUARD-TRY] mode=legacy path={path} kind=bearer error={e}")
        
        # DDD Token
        try:
            ddd_status, ddd_token = login_with_client(client, user_creds["email"], user_creds["password"], "ddd")
            if ddd_token:
                ddd_headers = auth_headers(ddd_token)
                ddd_response = run_request(client, "ddd", "GET", path, headers=ddd_headers)
                ddd_status = ddd_response[0]
                ddd_data = ddd_response[1] if len(ddd_response) > 1 else {}
                has_id = isinstance(ddd_data, dict) and 'id' in ddd_data
                has_email = isinstance(ddd_data, dict) and 'email' in ddd_data
                print(f"[GUARD-TRY] mode=ddd path={path} kind=bearer status={ddd_status} has_id={has_id} has_email={has_email}")
                
                if ddd_status == 200:
                    print(f"[GUARD200] mode=ddd path={path} status=200 contains_id={has_id} contains_email={has_email}")
                else:
                    # Log Body für Debugging
                    body_str = str(ddd_data)[:200] if ddd_data else "No body"
                    print(f"[GUARD-DEBUG] mode=ddd path={path} status={ddd_status} body={body_str}")
        except Exception as e:
            print(f"[GUARD-TRY] mode=ddd path={path} kind=bearer error={e}")
        
        # Test 3: Mit Admin Token
        admin_creds = credentials["admin"]
        
        # Legacy Admin Token
        try:
            legacy_status, legacy_admin_token = login_with_client(client, admin_creds["email"], admin_creds["password"], "legacy")
            if legacy_admin_token:
                legacy_admin_headers = auth_headers(legacy_admin_token)
                legacy_response = run_request(client, "legacy", "GET", path, headers=legacy_admin_headers)
                legacy_status = legacy_response[0]
                legacy_data = legacy_response[1] if len(legacy_response) > 1 else {}
                has_id = isinstance(legacy_data, dict) and 'id' in legacy_data
                has_email = isinstance(legacy_data, dict) and 'email' in legacy_data
                print(f"[GUARD-TRY] mode=legacy path={path} kind=admin_bearer status={legacy_status} has_id={has_id} has_email={has_email}")
                
                if legacy_status == 200:
                    print(f"[GUARD200] mode=legacy path={path} status=200 contains_id={has_id} contains_email={has_email}")
        except Exception as e:
            print(f"[GUARD-TRY] mode=legacy path={path} kind=admin_bearer error={e}")
        
        # DDD Admin Token
        try:
            ddd_status, ddd_admin_token = login_with_client(client, admin_creds["email"], admin_creds["password"], "ddd")
            if ddd_admin_token:
                ddd_admin_headers = auth_headers(ddd_admin_token)
                ddd_response = run_request(client, "ddd", "GET", path, headers=ddd_admin_headers)
                ddd_status = ddd_response[0]
                ddd_data = ddd_response[1] if len(ddd_response) > 1 else {}
                has_id = isinstance(ddd_data, dict) and 'id' in ddd_data
                has_email = isinstance(ddd_data, dict) and 'email' in ddd_data
                print(f"[GUARD-TRY] mode=ddd path={path} kind=admin_bearer status={ddd_status} has_id={has_id} has_email={has_email}")
                
                if ddd_status == 200:
                    print(f"[GUARD200] mode=ddd path={path} status=200 contains_id={has_id} contains_email={has_email}")
        except Exception as e:
            print(f"[GUARD-TRY] mode=ddd path={path} kind=admin_bearer error={e}")
    
    def test_cookie_auth_if_available(self, client):
        """Testet Cookie-Auth falls verfügbar"""
        print("Teste Cookie-Auth falls verfügbar...")
        
        # Prüfe ob Cookie-Auth in OpenAPI definiert ist
        try:
            legacy_response = run_request(client, "legacy", "GET", "/openapi.json")
            if legacy_response[0] == 200:
                openapi = legacy_response[1]
                security_schemes = openapi.get('components', {}).get('securitySchemes', {})
                
                cookie_schemes = {name: scheme for name, scheme in security_schemes.items() 
                                if scheme.get('type') == 'apiKey' and scheme.get('in') == 'cookie'}
                
                if cookie_schemes:
                    print(f"[OPENAPI-GUARD] cookie_schemes={list(cookie_schemes.keys())}")
                    # Teste Cookie-Auth
                    for scheme_name, scheme in cookie_schemes.items():
                        cookie_name = scheme.get('name', 'auth_token')
                        # Simuliere Cookie (normalerweise würde man es vom Login erhalten)
                        client.cookies.set(cookie_name, "test_cookie_value")
                        
                        try:
                            response = run_request(client, "legacy", "GET", "/api/auth/me")
                            status = response[0]
                            print(f"[GUARD-TRY] mode=legacy path=/api/auth/me kind=cookie status={status}")
                        except Exception as e:
                            print(f"[GUARD-TRY] mode=legacy path=/api/auth/me kind=cookie error={e}")
                else:
                    print("[OPENAPI-GUARD] no cookie auth schemes found")
        except Exception as e:
            print(f"Cookie auth test error: {e}")
    
    def test_combined_bearer_cookie_auth(self, client):
        """Testet kombinierte Bearer + Cookie Auth"""
        print("Teste kombinierte Bearer + Cookie Auth...")
        
        credentials = get_test_credentials()
        user_creds = credentials["user"]
        
        # Stelle sicher, dass User aktiv ist
        from tests.helpers.auth_flow import ensure_user_active_in_db
        ensure_user_active_in_db(user_creds["email"])
        
        # Legacy: Bearer + Cookie
        try:
            legacy_status, legacy_token = login_with_client(client, user_creds["email"], user_creds["password"], "legacy")
            if legacy_token:
                legacy_headers = auth_headers(legacy_token)
                # Setze zusätzlich Cookie
                client.cookies.set("auth_token", "test_cookie_value")
                
                legacy_response = run_request(client, "legacy", "GET", "/api/auth/me", headers=legacy_headers)
                legacy_status = legacy_response[0]
                legacy_data = legacy_response[1] if len(legacy_response) > 1 else {}
                has_id = isinstance(legacy_data, dict) and 'id' in legacy_data
                has_email = isinstance(legacy_data, dict) and 'email' in legacy_data
                print(f"[GUARD-TRY] mode=legacy path=/api/auth/me kind=both status={legacy_status} has_id={has_id} has_email={has_email}")
                
                if legacy_status == 200:
                    print(f"[GUARD200] mode=legacy path=/api/auth/me status=200 contains_id={has_id} contains_email={has_email}")
        except Exception as e:
            print(f"[GUARD-TRY] mode=legacy path=/api/auth/me kind=both error={e}")
        
        # DDD: Bearer + Cookie
        try:
            ddd_status, ddd_token = login_with_client(client, user_creds["email"], user_creds["password"], "ddd")
            if ddd_token:
                ddd_headers = auth_headers(ddd_token)
                # Setze zusätzlich Cookie
                client.cookies.set("auth_token", "test_cookie_value")
                
                ddd_response = run_request(client, "ddd", "GET", "/api/auth/me", headers=ddd_headers)
                ddd_status = ddd_response[0]
                ddd_data = ddd_response[1] if len(ddd_response) > 1 else {}
                has_id = isinstance(ddd_data, dict) and 'id' in ddd_data
                has_email = isinstance(ddd_data, dict) and 'email' in ddd_data
                print(f"[GUARD-TRY] mode=ddd path=/api/auth/me kind=both status={ddd_status} has_id={has_id} has_email={has_email}")
                
                if ddd_status == 200:
                    print(f"[GUARD200] mode=ddd path=/api/auth/me status=200 contains_id={has_id} contains_email={has_email}")
        except Exception as e:
            print(f"[GUARD-TRY] mode=ddd path=/api/auth/me kind=both error={e}")
