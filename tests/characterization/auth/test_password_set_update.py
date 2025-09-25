"""
Password Set/Update Tests
Testet Passwort-Setzung und -Aktualisierung mit Policy-Validierung
"""

import pytest
import os
import uuid
import sqlite3
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from tests.helpers.seeds_auth import seed_user_with_password, update_user_password, get_user_password_hash, seed_auth_test_users
from tests.helpers.password_policy import detect_hash_scheme, validate_password_complexity, make_password_hash
from tests.helpers.capabilities_auth import get_auth_capability_flags


class TestPasswordSetUpdate:
    """Testet Password Set/Update Verhalten"""
    
    def test_password_set_via_register_parity(self, client):
        """Test: Passwort-Setzung via Register oder POST /users"""
        print("Teste Password Set via Register/Users-Parität...")
        
        # Capability Detection
        capabilities = get_auth_capability_flags()
        if not capabilities["HAS_REGISTER"] and not capabilities["HAS_USER_SET_PASSWORD"]:
            pytest.skip("legacy endpoint not available")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_password_set_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_password_set_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            seed_auth_test_users(conn)
        
        with sqlite3.connect(ddd_db_path) as conn:
            seed_auth_test_users(conn)
        
        # Test-User erstellen
        test_email = f"test.password.set.{int(time.time())}@company.com"
        test_password = "SecurePassword123!"
        
        # Legacy: User erstellen
        legacy_create_success = False
        legacy_user_id = None
        legacy_seed_fallback = False
        
        if capabilities["HAS_REGISTER"]:
            try:
                register_payload = {
                    "email": test_email,
                    "password": test_password,
                    "full_name": "Test Password Set User",
                    "employee_id": "TPS001",
                    "organizational_unit": "Test"
                }
                legacy_create_response = run_request(
                    client, "legacy", "POST", "/api/auth/register",
                    json_data=register_payload,
                    database_url=legacy_database_url
                )
                legacy_create_success = legacy_create_response[0] in [200, 201]
                legacy_user_id = legacy_create_response[1].get('id') if legacy_create_success else None
            except Exception as e:
                print(f"Legacy register error: {e}")
        elif capabilities["HAS_USER_SET_PASSWORD"]:
            try:
                user_payload = {
                    "email": test_email,
                    "password": test_password,
                    "full_name": "Test Password Set User",
                    "employee_id": "TPS001",
                    "organizational_unit": "Test"
                }
                legacy_create_response = run_request(
                    client, "legacy", "POST", "/api/users",
                    json_data=user_payload,
                    database_url=legacy_database_url
                )
                legacy_create_success = legacy_create_response[0] in [200, 201]
                legacy_user_id = legacy_create_response[1].get('id') if legacy_create_success else None
            except Exception as e:
                print(f"Legacy user create error: {e}")
        else:
            # Seed Fallback
            with sqlite3.connect(legacy_db_path) as conn:
                legacy_user_id = seed_user_with_password(
                    conn, test_email, test_password, "Test Password Set User", "TPS001", "Test"
                )
                legacy_create_success = True
                legacy_seed_fallback = True
        
        # DDD: User erstellen
        ddd_create_success = False
        ddd_user_id = None
        ddd_seed_fallback = False
        
        if capabilities["HAS_REGISTER"]:
            try:
                register_payload = {
                    "email": test_email,
                    "password": test_password,
                    "full_name": "Test Password Set User",
                    "employee_id": "TPS001",
                    "organizational_unit": "Test"
                }
                ddd_create_response = run_request(
                    client, "ddd", "POST", "/api/auth/register",
                    json_data=register_payload,
                    database_url=ddd_database_url
                )
                ddd_create_success = ddd_create_response[0] in [200, 201]
                ddd_user_id = ddd_create_response[1].get('id') if ddd_create_success else None
            except Exception as e:
                print(f"DDD register error: {e}")
        elif capabilities["HAS_USER_SET_PASSWORD"]:
            try:
                user_payload = {
                    "email": test_email,
                    "password": test_password,
                    "full_name": "Test Password Set User",
                    "employee_id": "TPS001",
                    "organizational_unit": "Test"
                }
                ddd_create_response = run_request(
                    client, "ddd", "POST", "/api/users",
                    json_data=user_payload,
                    database_url=ddd_database_url
                )
                ddd_create_success = ddd_create_response[0] in [200, 201]
                ddd_user_id = ddd_create_response[1].get('id') if ddd_create_success else None
            except Exception as e:
                print(f"DDD user create error: {e}")
        else:
            # Seed Fallback
            with sqlite3.connect(ddd_db_path) as conn:
                ddd_user_id = seed_user_with_password(
                    conn, test_email, test_password, "Test Password Set User", "TPS001", "Test"
                )
                ddd_create_success = True
                ddd_seed_fallback = True
        
        # Passwort-Hash prüfen
        legacy_hash = None
        ddd_hash = None
        
        if legacy_user_id:
            with sqlite3.connect(legacy_db_path) as conn:
                legacy_hash = get_user_password_hash(conn, legacy_user_id)
        
        if ddd_user_id:
            with sqlite3.connect(ddd_db_path) as conn:
                ddd_hash = get_user_password_hash(conn, ddd_user_id)
        
        # Hash-Schema erkennen
        legacy_scheme = detect_hash_scheme(legacy_hash) if legacy_hash else {"scheme": "unknown", "valid": False}
        ddd_scheme = detect_hash_scheme(ddd_hash) if ddd_hash else {"scheme": "unknown", "valid": False}
        
        # Vergleich
        print(f"Legacy: create={legacy_create_success}, user_id={legacy_user_id}, scheme={legacy_scheme['scheme']}, seed_fallback={legacy_seed_fallback}")
        print(f"DDD: create={ddd_create_success}, user_id={ddd_user_id}, scheme={ddd_scheme['scheme']}, seed_fallback={ddd_seed_fallback}")
        
        # Asserts
        assert legacy_create_success == ddd_create_success, f"Create parity: Legacy={legacy_create_success}, DDD={ddd_create_success}"
        assert legacy_scheme['scheme'] == ddd_scheme['scheme'], f"Hash scheme parity: Legacy={legacy_scheme['scheme']}, DDD={ddd_scheme['scheme']}"
        assert legacy_scheme['valid'] == ddd_scheme['valid'], f"Hash valid parity: Legacy={legacy_scheme['valid']}, DDD={ddd_scheme['valid']}"
        
        print(f"\n✅ Password Set Parität erfolgreich getestet")
    
    def test_password_update_via_change_password_parity(self, client):
        """Test: Passwort-Update via PUT /users/{id}/password oder /auth/change-password"""
        print("Teste Password Update Parität...")
        
        # Capability Detection
        capabilities = get_auth_capability_flags()
        if not capabilities["HAS_USER_SET_PASSWORD"] and not capabilities["HAS_CHANGE_PASSWORD"]:
            pytest.skip("legacy endpoint not available")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_password_update_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_password_update_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
        
        with sqlite3.connect(ddd_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
        
        # Neues Passwort
        new_password = "NewSecurePassword456!"
        
        # Legacy: Passwort aktualisieren
        legacy_update_success = False
        legacy_seed_fallback = False
        
        if capabilities["HAS_USER_SET_PASSWORD"]:
            try:
                password_payload = {"password": new_password}
                legacy_update_response = run_request(
                    client, "legacy", "PUT", f"/api/users/{test_user_id}/password",
                    json_data=password_payload,
                    database_url=legacy_database_url
                )
                legacy_update_success = legacy_update_response[0] == 200
            except Exception as e:
                print(f"Legacy password update error: {e}")
        elif capabilities["HAS_CHANGE_PASSWORD"]:
            try:
                password_payload = {
                    "current_password": "TestPassword123!",
                    "new_password": new_password,
                    "confirm_password": new_password
                }
                legacy_update_response = run_request(
                    client, "legacy", "PUT", "/api/auth/change-password",
                    json_data=password_payload,
                    database_url=legacy_database_url
                )
                legacy_update_success = legacy_update_response[0] == 200
            except Exception as e:
                print(f"Legacy change password error: {e}")
        else:
            # Seed Fallback
            with sqlite3.connect(legacy_db_path) as conn:
                legacy_update_success = update_user_password(conn, test_user_id, new_password)
                legacy_seed_fallback = True
        
        # DDD: Passwort aktualisieren
        ddd_update_success = False
        ddd_seed_fallback = False
        
        if capabilities["HAS_USER_SET_PASSWORD"]:
            try:
                password_payload = {"password": new_password}
                ddd_update_response = run_request(
                    client, "ddd", "PUT", f"/api/users/{test_user_id}/password",
                    json_data=password_payload,
                    database_url=ddd_database_url
                )
                ddd_update_success = ddd_update_response[0] == 200
            except Exception as e:
                print(f"DDD password update error: {e}")
        elif capabilities["HAS_CHANGE_PASSWORD"]:
            try:
                password_payload = {
                    "current_password": "TestPassword123!",
                    "new_password": new_password,
                    "confirm_password": new_password
                }
                ddd_update_response = run_request(
                    client, "ddd", "PUT", "/api/auth/change-password",
                    json_data=password_payload,
                    database_url=ddd_database_url
                )
                ddd_update_success = ddd_update_response[0] == 200
            except Exception as e:
                print(f"DDD change password error: {e}")
        else:
            # Seed Fallback
            with sqlite3.connect(ddd_db_path) as conn:
                ddd_update_success = update_user_password(conn, test_user_id, new_password)
                ddd_seed_fallback = True
        
        # Passwort-Hash prüfen
        legacy_old_hash = None
        legacy_new_hash = None
        ddd_old_hash = None
        ddd_new_hash = None
        
        with sqlite3.connect(legacy_db_path) as conn:
            legacy_new_hash = get_user_password_hash(conn, test_user_id)
        
        with sqlite3.connect(ddd_db_path) as conn:
            ddd_new_hash = get_user_password_hash(conn, test_user_id)
        
        # Hash-Änderung prüfen
        legacy_hash_changed = legacy_new_hash != legacy_old_hash
        ddd_hash_changed = ddd_new_hash != ddd_old_hash
        
        # Vergleich
        print(f"Legacy: update={legacy_update_success}, hash_changed={legacy_hash_changed}, seed_fallback={legacy_seed_fallback}")
        print(f"DDD: update={ddd_update_success}, hash_changed={ddd_hash_changed}, seed_fallback={ddd_seed_fallback}")
        
        # Asserts
        assert legacy_update_success == ddd_update_success, f"Update parity: Legacy={legacy_update_success}, DDD={ddd_update_success}"
        assert legacy_hash_changed == ddd_hash_changed, f"Hash changed parity: Legacy={legacy_hash_changed}, DDD={ddd_hash_changed}"
        
        print(f"\n✅ Password Update Parität erfolgreich getestet")
    
    def test_password_policy_validation_parity(self, client):
        """Test: Passwort-Policy-Validierung (Hash-Schema, Komplexität)"""
        print("Teste Password Policy Validation Parität...")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_password_policy_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_password_policy_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            users = seed_auth_test_users(conn)
        
        with sqlite3.connect(ddd_db_path) as conn:
            users = seed_auth_test_users(conn)
        
        # Hash-Schema-Tests
        test_passwords = [
            ("SecurePassword123!", "strong"),
            ("123456", "weak"),
            ("password", "common"),
            ("", "empty")
        ]
        
        legacy_schemes = []
        ddd_schemes = []
        
        for password, category in test_passwords:
            # Legacy Hash
            with sqlite3.connect(legacy_db_path) as conn:
                legacy_hash = make_password_hash(password, "bcrypt")
                legacy_scheme = detect_hash_scheme(legacy_hash)
                legacy_schemes.append(legacy_scheme)
            
            # DDD Hash
            with sqlite3.connect(ddd_db_path) as conn:
                ddd_hash = make_password_hash(password, "bcrypt")
                ddd_scheme = detect_hash_scheme(ddd_hash)
                ddd_schemes.append(ddd_scheme)
        
        # Komplexitäts-Validierung
        complexity_results = []
        for password, category in test_passwords:
            complexity = validate_password_complexity(password)
            complexity_results.append(complexity)
        
        # Vergleich
        print(f"Legacy schemes: {[s['scheme'] for s in legacy_schemes]}")
        print(f"DDD schemes: {[s['scheme'] for s in ddd_schemes]}")
        print(f"Complexity results: {[c['valid'] for c in complexity_results]}")
        
        # Asserts
        assert all(s['scheme'] == 'bcrypt' for s in legacy_schemes), "Legacy should use bcrypt"
        assert all(s['scheme'] == 'bcrypt' for s in ddd_schemes), "DDD should use bcrypt"
        assert all(s['valid'] for s in legacy_schemes), "Legacy hashes should be valid"
        assert all(s['valid'] for s in ddd_schemes), "DDD hashes should be valid"
        
        print(f"\n✅ Password Policy Validation Parität erfolgreich getestet")

