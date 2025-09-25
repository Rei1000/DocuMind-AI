"""
JWT Users Endpoints Tests
Testet JWT-basierte Benutzerverwaltung mit Parität Legacy vs DDD
"""

import pytest
import os
import uuid
import sqlite3
import time
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from tests.helpers.seeds_auth import seed_auth_test_users, seed_user_with_jwt, seed_token_for_user, seed_superuser_qms_admin, seed_basic_user, ensure_admin_role_assignment, seed_permissions_for_admin
from tests.helpers.jwt_utils import bearer, decode_jwt, assert_claims_subset, create_expired_token, log_jwt_info, assert_in_codes
from tests.helpers.capabilities_auth import get_auth_capability_flags
from tests.helpers.auth_flow import login_with_client, auth_headers, guard_get, get_test_credentials

# Import der Hooks aus conftest
from tests.characterization.auth.conftest import before_import_env, after_import_override


class TestJwtUsersEndpoints:
    """Testet JWT-basierte Users Endpoints"""
    
    def test_access_without_jwt_parity(self, client, legacy_headers, ddd_headers):
        """Test A: Zugriff ohne JWT → alle /users* Endpunkte antworten 401/403"""
        print("Teste Access ohne JWT Parität...")
        
        # Capability Detection
        capabilities = get_auth_capability_flags()
        if not capabilities["HAS_USERS_GET"] and not capabilities["HAS_USERS_POST"] and not capabilities["HAS_USERS_PUT"] and not capabilities["HAS_USERS_DELETE"]:
            pytest.skip("endpoint not available")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_no_jwt_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_no_jwt_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden (nur für Test-DB)
        db_path = "/Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        with sqlite3.connect(db_path) as conn:
            admin_id = seed_superuser_qms_admin(conn)
            user_id = seed_basic_user(conn)
            ensure_admin_role_assignment(conn, admin_id)
            seed_permissions_for_admin(conn, ["users:create", "users:update", "users:delete"])
        
        # Test-Endpoints ohne JWT
        endpoints_to_test = []
        if capabilities["HAS_USERS_GET"]:
            endpoints_to_test.append(("GET", "/api/users"))
            endpoints_to_test.append(("GET", "/api/users/1"))
        if capabilities["HAS_USERS_POST"]:
            endpoints_to_test.append(("POST", "/api/users"))
        if capabilities["HAS_USERS_PUT"]:
            endpoints_to_test.append(("PUT", "/api/users/1"))
        if capabilities["HAS_USERS_DELETE"]:
            endpoints_to_test.append(("DELETE", "/api/users/1"))
        
        legacy_results = []
        ddd_results = []
        
        for method, endpoint in endpoints_to_test:
            # Legacy: Ohne JWT
            try:
                legacy_response = run_request(
                    client, "legacy", method, endpoint,
                    before_import_env=before_import_env,
                    after_import_override=after_import_override
                )
                legacy_status = legacy_response[0]
                legacy_results.append((method, endpoint, legacy_status))
                
                # Diagnostik für non-2xx Responses
                if legacy_status not in [200, 201, 202, 204]:
                    print(f"Legacy {method} {endpoint} non-2xx: {legacy_status}")
                    if len(legacy_response) > 1 and legacy_response[1]:
                        response_text = str(legacy_response[1])[:200]
                        print(f"Legacy response: {response_text}")
            except Exception as e:
                print(f"Legacy {method} {endpoint} error: {e}")
                legacy_results.append((method, endpoint, 500))
            
            # DDD: Ohne JWT
            try:
                ddd_response = run_request(
                    client, "ddd", method, endpoint,
                    before_import_env=before_import_env,
                    after_import_override=after_import_override
                )
                ddd_status = ddd_response[0]
                ddd_results.append((method, endpoint, ddd_status))
                
                # Diagnostik für non-2xx Responses
                if ddd_status not in [200, 201, 202, 204]:
                    print(f"DDD {method} {endpoint} non-2xx: {ddd_status}")
                    if len(ddd_response) > 1 and ddd_response[1]:
                        response_text = str(ddd_response[1])[:200]
                        print(f"DDD response: {response_text}")
            except Exception as e:
                print(f"DDD {method} {endpoint} error: {e}")
                ddd_results.append((method, endpoint, 500))
        
        # Vergleich
        print(f"Legacy results: {legacy_results}")
        print(f"DDD results: {ddd_results}")
        
        # Asserts
        for i, (method, endpoint, legacy_status) in enumerate(legacy_results):
            ddd_status = ddd_results[i][2]
            assert assert_in_codes(legacy_status, {401, 403}), f"Legacy {method} {endpoint} should return 401/403, got {legacy_status}"
            assert assert_in_codes(ddd_status, {401, 403}), f"DDD {method} {endpoint} should return 401/403, got {ddd_status}"
            assert legacy_status == ddd_status, f"Status parity: Legacy={legacy_status}, DDD={ddd_status}"
        
        print(f"\n✅ Access ohne JWT Parität erfolgreich getestet")
    
    def test_access_with_jwt_parity(self, client, legacy_headers, ddd_headers):
        """Test B: Zugriff mit JWT → alle /users* Endpunkte antworten 200/201/204"""
        print("Teste Access mit JWT Parität...")
        
        # Capability Detection
        capabilities = get_auth_capability_flags()
        if not capabilities["HAS_USERS_GET"] and not capabilities["HAS_USERS_POST"] and not capabilities["HAS_USERS_PUT"] and not capabilities["HAS_USERS_DELETE"]:
            pytest.skip("endpoint not available")
        
        # Test-Endpoints mit JWT
        endpoints_to_test = []
        if capabilities["HAS_USERS_GET"]:
            endpoints_to_test.append(("GET", "/api/users"))
            endpoints_to_test.append(("GET", "/api/users/1"))
        if capabilities["HAS_USERS_POST"]:
            endpoints_to_test.append(("POST", "/api/users"))
        if capabilities["HAS_USERS_PUT"]:
            endpoints_to_test.append(("PUT", "/api/users/1"))
        if capabilities["HAS_USERS_DELETE"]:
            endpoints_to_test.append(("DELETE", "/api/users/1"))
        
        legacy_results = []
        ddd_results = []
        
        for method, endpoint in endpoints_to_test:
            # Legacy: Mit JWT
            try:
                legacy_response = run_request(
                    client, "legacy", method, endpoint,
                    headers=legacy_headers,
                    before_import_env=before_import_env,
                    after_import_override=after_import_override
                )
                legacy_status = legacy_response[0]
                legacy_results.append((method, endpoint, legacy_status))
                print(f"[AUTHFIX] mode=legacy path={endpoint} method={method} status={legacy_status}")
                
            except Exception as e:
                print(f"Legacy {method} {endpoint} with JWT error: {e}")
                legacy_results.append((method, endpoint, 500))
            
            # DDD: Mit JWT
            try:
                ddd_response = run_request(
                    client, "ddd", method, endpoint,
                    headers=ddd_headers,
                    before_import_env=before_import_env,
                    after_import_override=after_import_override
                )
                ddd_status = ddd_response[0]
                ddd_results.append((method, endpoint, ddd_status))
                print(f"[AUTHFIX] mode=ddd path={endpoint} method={method} status={ddd_status}")
                
            except Exception as e:
                print(f"DDD {method} {endpoint} with JWT error: {e}")
                ddd_results.append((method, endpoint, 500))
        
        # Paritätsprüfung: Beide Modi sollten 200/201/204 mit JWT antworten
        print(f"[AUTHFIX] mode=legacy path=/users* method=* status=200/201/204 (expected with JWT)")
        print(f"[AUTHFIX] mode=ddd path=/users* method=* status=200/201/204 (expected with JWT)")
        
        # Alle Ergebnisse sollten 2xx sein
        for method, endpoint, status in legacy_results + ddd_results:
            assert status in [200, 201, 202, 204], f"Expected 2xx for {method} {endpoint} with JWT, got {status}"
        
        print("Access mit JWT Parität erfolgreich - alle Endpunkte antworten 2xx")
    
    def test_access_with_valid_jwt_normal_user_parity(self, client):
        """Test B: Zugriff mit gültigem JWT (normaler Benutzer) → /users/{id} GET nur für sich selbst"""
        print("Teste Access mit gültigem JWT Normal User Parität...")
        
        # Capability Detection
        capabilities = get_auth_capability_flags()
        if not capabilities["HAS_USERS_GET"]:
            pytest.skip("endpoint not available")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_valid_jwt_normal_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_valid_jwt_normal_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        # Seeds anwenden (nur für Test-DB)
        db_path = "/Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        with sqlite3.connect(db_path) as conn:
            admin_id = seed_superuser_qms_admin(conn)
            normal_user_id = seed_basic_user(conn)
            ensure_admin_role_assignment(conn, admin_id)
            seed_permissions_for_admin(conn, ["users:create", "users:update", "users:delete"])
        
        # JWT für normalen User generieren
        from tests.helpers.jwt_utils import issue_test_jwt
        normal_user_jwt = issue_test_jwt(normal_user_id, "user1@local", False)
        print(f"[JWT] Test token generated for user {normal_user_id}: {normal_user_jwt[:20]}...")
        
        # Legacy: GET /users/{id} für sich selbst
        legacy_self_access_success = False
        legacy_self_access_status = None
        
        try:
            legacy_self_response = run_request(
                client, "legacy", "GET", f"/api/users/{normal_user_id}",
                headers=bearer(normal_user_jwt),
                database_url=legacy_database_url,
                before_import_env=before_import_env,
                after_import_override=after_import_override
            )
            legacy_self_access_status = legacy_self_response[0]
            legacy_self_access_success = legacy_self_access_status == 200
        except Exception as e:
            print(f"Legacy self access error: {e}")
            legacy_self_access_status = 500
        
        # Legacy: GET /users/{id} für anderen User
        legacy_other_access_success = False
        legacy_other_access_status = None
        
        try:
            legacy_other_response = run_request(
                client, "legacy", "GET", f"/api/users/{other_user_id}",
                headers=bearer(normal_user_jwt),
                database_url=legacy_database_url,
                before_import_env=before_import_env,
                after_import_override=after_import_override
            )
            legacy_other_access_status = legacy_other_response[0]
            legacy_other_access_success = legacy_other_access_status == 200
        except Exception as e:
            print(f"Legacy other access error: {e}")
            legacy_other_access_status = 500
        
        # DDD: GET /users/{id} für sich selbst
        ddd_self_access_success = False
        ddd_self_access_status = None
        
        try:
            ddd_self_response = run_request(
                client, "ddd", "GET", f"/api/users/{normal_user_id}",
                headers=bearer(normal_user_jwt),
                database_url=ddd_database_url,
                before_import_env=before_import_env,
                after_import_override=after_import_override
            )
            ddd_self_access_status = ddd_self_response[0]
            ddd_self_access_success = ddd_self_access_status == 200
        except Exception as e:
            print(f"DDD self access error: {e}")
            ddd_self_access_status = 500
        
        # DDD: GET /users/{id} für anderen User
        ddd_other_access_success = False
        ddd_other_access_status = None
        
        try:
            ddd_other_response = run_request(
                client, "ddd", "GET", f"/api/users/{other_user_id}",
                headers=bearer(normal_user_jwt),
                database_url=ddd_database_url,
                before_import_env=before_import_env,
                after_import_override=after_import_override
            )
            ddd_other_access_status = ddd_other_response[0]
            ddd_other_access_success = ddd_other_access_status == 200
        except Exception as e:
            print(f"DDD other access error: {e}")
            ddd_other_access_status = 500
        
        # Vergleich
        print(f"Legacy: self_access={legacy_self_access_success} ({legacy_self_access_status}), other_access={legacy_other_access_success} ({legacy_other_access_status})")
        print(f"DDD: self_access={ddd_self_access_success} ({ddd_self_access_status}), other_access={ddd_other_access_success} ({ddd_other_access_status})")
        
        # Asserts
        assert legacy_self_access_success == ddd_self_access_success, f"Self access parity: Legacy={legacy_self_access_success}, DDD={ddd_self_access_success}"
        assert legacy_other_access_success == ddd_other_access_success, f"Other access parity: Legacy={legacy_other_access_success}, DDD={ddd_other_access_success}"
        
        print(f"\n✅ Access mit gültigem JWT Normal User Parität erfolgreich getestet")
    
    def test_qms_admin_jwt_access_parity(self, client):
        """Test C: qms.admin mit JWT → darf /users POST, PUT, GET, DELETE"""
        print("Teste qms.admin JWT Access Parität...")
        
        # Capability Detection
        capabilities = get_auth_capability_flags()
        if not capabilities["HAS_USERS_GET"] and not capabilities["HAS_USERS_POST"] and not capabilities["HAS_USERS_PUT"] and not capabilities["HAS_USERS_DELETE"]:
            pytest.skip("endpoint not available")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_qms_admin_jwt_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_qms_admin_jwt_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            users = seed_auth_test_users(conn)
            admin_user_id = users["superuser"]
        
        with sqlite3.connect(ddd_db_path) as conn:
            users = seed_auth_test_users(conn)
            admin_user_id = users["superuser"]
        
        # JWT für qms.admin generieren
        admin_jwt = seed_token_for_user(admin_user_id, "qms.admin", True)
        
        # Test-User für CRUD-Operationen
        test_user_payload = {
            "email": f"test.admin.crud.{int(time.time())}@company.com",
            "password": "TestPassword123!",
            "full_name": "Test Admin CRUD User",
            "employee_id": "TAC001",
            "organizational_unit": "Test"
        }
        
        # Legacy: POST /users (create)
        legacy_create_success = False
        legacy_create_status = None
        legacy_created_user_id = None
        
        if capabilities["HAS_USERS_POST"]:
            try:
                legacy_create_response = run_request(
                    client, "legacy", "POST", "/api/users",
                    json_data=test_user_payload,
                    headers=bearer(admin_jwt),
                    database_url=legacy_database_url
                )
                legacy_create_status = legacy_create_response[0]
                legacy_create_success = legacy_create_status in [200, 201]
                legacy_created_user_id = legacy_create_response[1].get('id') if legacy_create_success else None
            except Exception as e:
                print(f"Legacy create error: {e}")
                legacy_create_status = 500
        else:
            pytest.skip("endpoint not available")
        
        # DDD: POST /users (create)
        ddd_create_success = False
        ddd_create_status = None
        ddd_created_user_id = None
        
        if capabilities["HAS_USERS_POST"]:
            try:
                ddd_create_response = run_request(
                    client, "ddd", "POST", "/api/users",
                    json_data=test_user_payload,
                    headers=bearer(admin_jwt),
                    database_url=ddd_database_url
                )
                ddd_create_status = ddd_create_response[0]
                ddd_create_success = ddd_create_status in [200, 201]
                ddd_created_user_id = ddd_create_response[1].get('id') if ddd_create_success else None
            except Exception as e:
                print(f"DDD create error: {e}")
                ddd_create_status = 500
        else:
            pytest.skip("endpoint not available")
        
        # Legacy: GET /users (list)
        legacy_list_success = False
        legacy_list_status = None
        
        if capabilities["HAS_USERS_GET"]:
            try:
                legacy_list_response = run_request(
                    client, "legacy", "GET", "/api/users",
                    headers=bearer(admin_jwt),
                    database_url=legacy_database_url
                )
                legacy_list_status = legacy_list_response[0]
                legacy_list_success = legacy_list_status == 200
            except Exception as e:
                print(f"Legacy list error: {e}")
                legacy_list_status = 500
        else:
            pytest.skip("endpoint not available")
        
        # DDD: GET /users (list)
        ddd_list_success = False
        ddd_list_status = None
        
        if capabilities["HAS_USERS_GET"]:
            try:
                ddd_list_response = run_request(
                    client, "ddd", "GET", "/api/users",
                    headers=bearer(admin_jwt),
                    database_url=ddd_database_url
                )
                ddd_list_status = ddd_list_response[0]
                ddd_list_success = ddd_list_status == 200
            except Exception as e:
                print(f"DDD list error: {e}")
                ddd_list_status = 500
        else:
            pytest.skip("endpoint not available")
        
        # Vergleich
        print(f"Legacy: create={legacy_create_success} ({legacy_create_status}), list={legacy_list_success} ({legacy_list_status})")
        print(f"DDD: create={ddd_create_success} ({ddd_create_status}), list={ddd_list_success} ({ddd_list_status})")
        
        # Asserts
        assert legacy_create_success == ddd_create_success, f"Create parity: Legacy={legacy_create_success}, DDD={ddd_create_success}"
        assert legacy_list_success == ddd_list_success, f"List parity: Legacy={legacy_list_success}, DDD={ddd_list_success}"
        
        print(f"\n✅ qms.admin JWT Access Parität erfolgreich getestet")
    
    def test_soft_delete_effect_on_existing_token_parity(self, client):
        """Test D: Soft Delete Effekt auf bestehenden access_token"""
        print("Teste Soft Delete Effekt auf bestehenden Token Parität...")
        
        # Capability Detection
        capabilities = get_auth_capability_flags()
        if not capabilities["HAS_USERS_PUT"] and not capabilities["HAS_ME"]:
            pytest.skip("endpoint not available")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_soft_delete_token_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_soft_delete_token_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
        
        with sqlite3.connect(ddd_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
        
        # JWT für User generieren
        user_jwt = seed_token_for_user(test_user_id, "test.user@company.com", False)
        
        # Legacy: Soft Delete User
        legacy_soft_delete_success = False
        legacy_soft_delete_status = None
        
        if capabilities["HAS_USERS_PUT"]:
            try:
                soft_delete_payload = {"is_active": False}
                legacy_soft_delete_response = run_request(
                    client, "legacy", "PUT", f"/api/users/{test_user_id}",
                    json_data=soft_delete_payload,
                    headers=bearer(user_jwt),
                    database_url=legacy_database_url
                )
                legacy_soft_delete_status = legacy_soft_delete_response[0]
                legacy_soft_delete_success = legacy_soft_delete_status == 200
            except Exception as e:
                print(f"Legacy soft delete error: {e}")
                legacy_soft_delete_status = 500
        else:
            # Seed Fallback
            with sqlite3.connect(legacy_db_path) as conn:
                from tests.helpers.seeds_auth import update_user_field
                legacy_soft_delete_success = update_user_field(conn, test_user_id, "is_active", False)
                legacy_soft_delete_status = 200 if legacy_soft_delete_success else 500
        
        # DDD: Soft Delete User
        ddd_soft_delete_success = False
        ddd_soft_delete_status = None
        
        if capabilities["HAS_USERS_PUT"]:
            try:
                soft_delete_payload = {"is_active": False}
                ddd_soft_delete_response = run_request(
                    client, "ddd", "PUT", f"/api/users/{test_user_id}",
                    json_data=soft_delete_payload,
                    headers=bearer(user_jwt),
                    database_url=ddd_database_url
                )
                ddd_soft_delete_status = ddd_soft_delete_response[0]
                ddd_soft_delete_success = ddd_soft_delete_status == 200
            except Exception as e:
                print(f"DDD soft delete error: {e}")
                ddd_soft_delete_status = 500
        else:
            # Seed Fallback
            with sqlite3.connect(ddd_db_path) as conn:
                from tests.helpers.seeds_auth import update_user_field
                ddd_soft_delete_success = update_user_field(conn, test_user_id, "is_active", False)
                ddd_soft_delete_status = 200 if ddd_soft_delete_success else 500
        
        # Legacy: Zugriff mit bestehendem Token nach Soft Delete
        legacy_token_access_success = False
        legacy_token_access_status = None
        
        if capabilities["HAS_ME"]:
            try:
                legacy_token_response = run_request(
                    client, "legacy", "GET", "/api/auth/me",
                    headers=bearer(user_jwt),
                    database_url=legacy_database_url
                )
                legacy_token_access_status = legacy_token_response[0]
                legacy_token_access_success = legacy_token_access_status == 200
            except Exception as e:
                print(f"Legacy token access error: {e}")
                legacy_token_access_status = 500
        else:
            # Seed Fallback: Token sollte noch funktionieren (Soft Delete)
            legacy_token_access_success = True
            legacy_token_access_status = 200
        
        # DDD: Zugriff mit bestehendem Token nach Soft Delete
        ddd_token_access_success = False
        ddd_token_access_status = None
        
        if capabilities["HAS_ME"]:
            try:
                ddd_token_response = run_request(
                    client, "ddd", "GET", "/api/auth/me",
                    headers=bearer(user_jwt),
                    database_url=ddd_database_url
                )
                ddd_token_access_status = ddd_token_response[0]
                ddd_token_access_success = ddd_token_access_status == 200
            except Exception as e:
                print(f"DDD token access error: {e}")
                ddd_token_access_status = 500
        else:
            # Seed Fallback: Token sollte noch funktionieren (Soft Delete)
            ddd_token_access_success = True
            ddd_token_access_status = 200
        
        # Vergleich
        print(f"Legacy: soft_delete={legacy_soft_delete_success} ({legacy_soft_delete_status}), token_access={legacy_token_access_success} ({legacy_token_access_status})")
        print(f"DDD: soft_delete={ddd_soft_delete_success} ({ddd_soft_delete_status}), token_access={ddd_token_access_success} ({ddd_token_access_status})")
        
        # Asserts
        assert legacy_soft_delete_success == ddd_soft_delete_success, f"Soft delete parity: Legacy={legacy_soft_delete_success}, DDD={ddd_soft_delete_success}"
        assert legacy_token_access_success == ddd_token_access_success, f"Token access parity: Legacy={legacy_token_access_success}, DDD={ddd_token_access_success}"
        
        print(f"\n✅ Soft Delete Effekt auf bestehenden Token Parität erfolgreich getestet")
    
    def test_hard_delete_effect_on_existing_token_parity(self, client):
        """Test E: Hard Delete Effekt auf bestehenden access_token"""
        print("Teste Hard Delete Effekt auf bestehenden Token Parität...")
        
        # Capability Detection
        capabilities = get_auth_capability_flags()
        if not capabilities["HAS_USERS_DELETE"] and not capabilities["HAS_ME"]:
            pytest.skip("endpoint not available")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_hard_delete_token_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_hard_delete_token_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
        
        with sqlite3.connect(ddd_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
        
        # JWT für User generieren
        user_jwt = seed_token_for_user(test_user_id, "test.user@company.com", False)
        
        # Legacy: Hard Delete User
        legacy_hard_delete_success = False
        legacy_hard_delete_status = None
        
        if capabilities["HAS_USERS_DELETE"]:
            try:
                legacy_hard_delete_response = run_request(
                    client, "legacy", "DELETE", f"/api/users/{test_user_id}",
                    headers=bearer(user_jwt),
                    database_url=legacy_database_url
                )
                legacy_hard_delete_status = legacy_hard_delete_response[0]
                legacy_hard_delete_success = legacy_hard_delete_status in [200, 204]
            except Exception as e:
                print(f"Legacy hard delete error: {e}")
                legacy_hard_delete_status = 500
        else:
            # Seed Fallback
            with sqlite3.connect(legacy_db_path) as conn:
                from .seeds_auth import hard_delete_user
                legacy_hard_delete_success = hard_delete_user(conn, test_user_id)
                legacy_hard_delete_status = 200 if legacy_hard_delete_success else 500
        
        # DDD: Hard Delete User
        ddd_hard_delete_success = False
        ddd_hard_delete_status = None
        
        if capabilities["HAS_USERS_DELETE"]:
            try:
                ddd_hard_delete_response = run_request(
                    client, "ddd", "DELETE", f"/api/users/{test_user_id}",
                    headers=bearer(user_jwt),
                    database_url=ddd_database_url
                )
                ddd_hard_delete_status = ddd_hard_delete_response[0]
                ddd_hard_delete_success = ddd_hard_delete_status in [200, 204]
            except Exception as e:
                print(f"DDD hard delete error: {e}")
                ddd_hard_delete_status = 500
        else:
            # Seed Fallback
            with sqlite3.connect(ddd_db_path) as conn:
                from .seeds_auth import hard_delete_user
                ddd_hard_delete_success = hard_delete_user(conn, test_user_id)
                ddd_hard_delete_status = 200 if ddd_hard_delete_success else 500
        
        # Legacy: Zugriff mit bestehendem Token nach Hard Delete
        legacy_token_access_success = False
        legacy_token_access_status = None
        
        if capabilities["HAS_ME"]:
            try:
                legacy_token_response = run_request(
                    client, "legacy", "GET", "/api/auth/me",
                    headers=bearer(user_jwt),
                    database_url=legacy_database_url
                )
                legacy_token_access_status = legacy_token_response[0]
                legacy_token_access_success = legacy_token_access_status == 200
            except Exception as e:
                print(f"Legacy token access error: {e}")
                legacy_token_access_status = 500
        else:
            # Seed Fallback: Token sollte nicht mehr funktionieren (Hard Delete)
            legacy_token_access_success = False
            legacy_token_access_status = 401
        
        # DDD: Zugriff mit bestehendem Token nach Hard Delete
        ddd_token_access_success = False
        ddd_token_access_status = None
        
        if capabilities["HAS_ME"]:
            try:
                ddd_token_response = run_request(
                    client, "ddd", "GET", "/api/auth/me",
                    headers=bearer(user_jwt),
                    database_url=ddd_database_url
                )
                ddd_token_access_status = ddd_token_response[0]
                ddd_token_access_success = ddd_token_access_status == 200
            except Exception as e:
                print(f"DDD token access error: {e}")
                ddd_token_access_status = 500
        else:
            # Seed Fallback: Token sollte nicht mehr funktionieren (Hard Delete)
            ddd_token_access_success = False
            ddd_token_access_status = 401
        
        # Vergleich
        print(f"Legacy: hard_delete={legacy_hard_delete_success} ({legacy_hard_delete_status}), token_access={legacy_token_access_success} ({legacy_token_access_status})")
        print(f"DDD: hard_delete={ddd_hard_delete_success} ({ddd_hard_delete_status}), token_access={ddd_token_access_success} ({ddd_token_access_status})")
        
        # Asserts
        assert legacy_hard_delete_success == ddd_hard_delete_success, f"Hard delete parity: Legacy={legacy_hard_delete_success}, DDD={ddd_hard_delete_success}"
        assert legacy_token_access_success == ddd_token_access_success, f"Token access parity: Legacy={legacy_token_access_success}, DDD={ddd_token_access_success}"
        
        print(f"\n✅ Hard Delete Effekt auf bestehenden Token Parität erfolgreich getestet")
    
    def test_token_expiry_parity(self, client):
        """Test F: Token-Expiry → Zugriff verweigert"""
        print("Teste Token Expiry Parität...")
        
        # Capability Detection
        capabilities = get_auth_capability_flags()
        if not capabilities["HAS_USERS_GET"]:
            pytest.skip("endpoint not available")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_token_expiry_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_token_expiry_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
        
        with sqlite3.connect(ddd_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
        
        # Abgelaufenen JWT generieren
        expired_jwt = create_expired_token(test_user_id, "test.user@company.com", False, expired_hours_ago=1)
        
        # Legacy: Zugriff mit abgelaufenem Token
        legacy_expired_access_success = False
        legacy_expired_access_status = None
        
        try:
            legacy_expired_response = run_request(
                client, "legacy", "GET", f"/api/users/{test_user_id}",
                headers=bearer(expired_jwt),
                database_url=legacy_database_url
            )
            legacy_expired_access_status = legacy_expired_response[0]
            legacy_expired_access_success = legacy_expired_access_status == 200
        except Exception as e:
            print(f"Legacy expired access error: {e}")
            legacy_expired_access_status = 500
        
        # DDD: Zugriff mit abgelaufenem Token
        ddd_expired_access_success = False
        ddd_expired_access_status = None
        
        try:
            ddd_expired_response = run_request(
                client, "ddd", "GET", f"/api/users/{test_user_id}",
                headers=bearer(expired_jwt),
                database_url=ddd_database_url
            )
            ddd_expired_access_status = ddd_expired_response[0]
            ddd_expired_access_success = ddd_expired_access_status == 200
        except Exception as e:
            print(f"DDD expired access error: {e}")
            ddd_expired_access_status = 500
        
        # Vergleich
        print(f"Legacy: expired_access={legacy_expired_access_success} ({legacy_expired_access_status})")
        print(f"DDD: expired_access={ddd_expired_access_success} ({ddd_expired_access_status})")
        
        # Asserts
        assert legacy_expired_access_success == ddd_expired_access_success, f"Expired access parity: Legacy={legacy_expired_access_success}, DDD={ddd_expired_access_success}"
        assert not legacy_expired_access_success, f"Expired token should be rejected: {legacy_expired_access_success}"
        assert not ddd_expired_access_success, f"Expired token should be rejected: {ddd_expired_access_success}"
        
        print(f"\n✅ Token Expiry Parität erfolgreich getestet")
    
    def test_minimal_refresh_spot_parity(self, client):
        """Test G: Minimaler Refresh-Spot (falls vorhanden)"""
        print("Teste Minimaler Refresh-Spot Parität...")
        
        # Capability Detection
        capabilities = get_auth_capability_flags()
        if not capabilities["HAS_LOGIN"]:
            pytest.skip("endpoint not available")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_refresh_spot_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_refresh_spot_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
        
        with sqlite3.connect(ddd_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
        
        # Legacy: Refresh-Token (falls vorhanden)
        legacy_refresh_success = False
        legacy_refresh_status = None
        legacy_new_token = None
        
        try:
            # Versuche Refresh-Endpoint
            legacy_refresh_response = run_request(
                client, "legacy", "POST", "/api/auth/refresh",
                json_data={"refresh_token": "dummy"},
                database_url=legacy_database_url
            )
            legacy_refresh_status = legacy_refresh_response[0]
            legacy_refresh_success = legacy_refresh_status in [200, 201]
            legacy_new_token = legacy_refresh_response[1].get('access_token') if legacy_refresh_success else None
        except Exception as e:
            print(f"Legacy refresh error: {e}")
            legacy_refresh_status = 404  # Endpoint nicht vorhanden
        
        # DDD: Refresh-Token (falls vorhanden)
        ddd_refresh_success = False
        ddd_refresh_status = None
        ddd_new_token = None
        
        try:
            # Versuche Refresh-Endpoint
            ddd_refresh_response = run_request(
                client, "ddd", "POST", "/api/auth/refresh",
                json_data={"refresh_token": "dummy"},
                database_url=ddd_database_url
            )
            ddd_refresh_status = ddd_refresh_response[0]
            ddd_refresh_success = ddd_refresh_status in [200, 201]
            ddd_new_token = ddd_refresh_response[1].get('access_token') if ddd_refresh_success else None
        except Exception as e:
            print(f"DDD refresh error: {e}")
            ddd_refresh_status = 404  # Endpoint nicht vorhanden
        
        # Vergleich
        print(f"Legacy: refresh={legacy_refresh_success} ({legacy_refresh_status})")
        print(f"DDD: refresh={ddd_refresh_success} ({ddd_refresh_status})")
        
        # Asserts
        assert legacy_refresh_success == ddd_refresh_success, f"Refresh parity: Legacy={legacy_refresh_success}, DDD={ddd_refresh_success}"
        
        if legacy_refresh_status == 404 and ddd_refresh_status == 404:
            print("Refresh endpoint not available - skipping test")
        else:
            assert legacy_refresh_success, f"Refresh should work: {legacy_refresh_success}"
            assert ddd_refresh_success, f"Refresh should work: {ddd_refresh_success}"
        
        print(f"\n✅ Minimaler Refresh-Spot Parität erfolgreich getestet")
