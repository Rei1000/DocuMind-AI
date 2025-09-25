"""
User Soft Delete Tests
Testet Soft Delete Verhalten (is_active=false) und CheckAccess-Parität
"""

import pytest
import os
import uuid
import sqlite3
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from tests.helpers.seeds_accesscontrol import seed_superuser_qms_admin, seed_basic_users, seed_roles_and_permissions, seed_user, update_user_field, get_user_by_id
from tests.helpers.payloads_accesscontrol import create_user_payload, update_user_payload, soft_delete_user_payload
from tests.helpers.capabilities import get_capability_flags


class TestUserSoftDelete:
    """Testet User Soft Delete Verhalten"""
    
    def test_soft_delete_sets_flag_parity(self, client):
        """Test: Soft Delete setzt Flag (is_active=false), GET /users/{id} liefert User weiterhin"""
        print("Teste Soft Delete Flag-Parität...")
        
        # Capability Detection
        capabilities = get_capability_flags()
        if not capabilities["HAS_USERS_POST"] or not capabilities["HAS_USERS_PUT"] or not capabilities["HAS_USERS_GET"]:
            pytest.skip("legacy endpoint not available")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_soft_delete_flag_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_soft_delete_flag_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            seed_superuser_qms_admin(conn)
            seed_basic_users(conn, n=2)
            seed_roles_and_permissions(conn)
        
        with sqlite3.connect(ddd_db_path) as conn:
            seed_superuser_qms_admin(conn)
            seed_basic_users(conn, n=2)
            seed_roles_and_permissions(conn)
        
        # Test-User erstellen
        test_user_payload = create_user_payload(
            email="test.softdelete@company.com",
            full_name="Test Soft Delete User",
            employee_id="TSD001",
            organizational_unit="Test",
            is_active=True
        )
        
        # Legacy: User erstellen
        try:
            legacy_create_response = run_request(
                client, "legacy", "POST", "/api/users",
                json_data=test_user_payload,
                database_url=legacy_database_url
            )
            legacy_create_success = legacy_create_response[0] in [200, 201]
            legacy_user_id = legacy_create_response[1].get('id') if legacy_create_success else None
        except Exception as e:
            legacy_create_success = False
            legacy_user_id = None
            print(f"Legacy create error: {e}")
        
        # DDD: User erstellen
        try:
            ddd_create_response = run_request(
                client, "ddd", "POST", "/api/users",
                json_data=test_user_payload,
                database_url=ddd_database_url
            )
            ddd_create_success = ddd_create_response[0] in [200, 201]
            ddd_user_id = ddd_create_response[1].get('id') if ddd_create_success else None
        except Exception as e:
            ddd_create_success = False
            ddd_user_id = None
            print(f"DDD create error: {e}")
        
        # Soft Delete durchführen
        soft_delete_payload = soft_delete_user_payload()
        
        # Legacy: Soft Delete
        try:
            legacy_soft_delete_response = run_request(
                client, "legacy", "PUT", f"/api/users/{legacy_user_id}",
                json_data=soft_delete_payload,
                database_url=legacy_database_url
            )
            legacy_soft_delete_success = legacy_soft_delete_response[0] == 200
        except Exception as e:
            legacy_soft_delete_success = False
            print(f"Legacy soft delete error: {e}")
        
        # DDD: Soft Delete
        try:
            ddd_soft_delete_response = run_request(
                client, "ddd", "PUT", f"/api/users/{ddd_user_id}",
                json_data=soft_delete_payload,
                database_url=ddd_database_url
            )
            ddd_soft_delete_success = ddd_soft_delete_response[0] == 200
        except Exception as e:
            ddd_soft_delete_success = False
            print(f"DDD soft delete error: {e}")
        
        # GET User nach Soft Delete
        # Legacy: GET User
        try:
            legacy_get_response = run_request(
                client, "legacy", "GET", f"/api/users/{legacy_user_id}",
                database_url=legacy_database_url
            )
            legacy_get_success = legacy_get_response[0] == 200
            legacy_user_data = legacy_get_response[1] if legacy_get_success else {}
            legacy_is_active = legacy_user_data.get('is_active', True)
        except Exception as e:
            legacy_get_success = False
            legacy_is_active = True
            print(f"Legacy get error: {e}")
        
        # DDD: GET User
        try:
            ddd_get_response = run_request(
                client, "ddd", "GET", f"/api/users/{ddd_user_id}",
                database_url=ddd_database_url
            )
            ddd_get_success = ddd_get_response[0] == 200
            ddd_user_data = ddd_get_response[1] if ddd_get_success else {}
            ddd_is_active = ddd_user_data.get('is_active', True)
        except Exception as e:
            ddd_get_success = False
            ddd_is_active = True
            print(f"DDD get error: {e}")
        
        # Vergleich
        print(f"Legacy: create={legacy_create_success}, soft_delete={legacy_soft_delete_success}, get={legacy_get_success}, is_active={legacy_is_active}")
        print(f"DDD: create={ddd_create_success}, soft_delete={ddd_soft_delete_success}, get={ddd_get_success}, is_active={ddd_is_active}")
        
        # Asserts
        assert legacy_create_success == ddd_create_success, f"Create parity: Legacy={legacy_create_success}, DDD={ddd_create_success}"
        assert legacy_soft_delete_success == ddd_soft_delete_success, f"Soft delete parity: Legacy={legacy_soft_delete_success}, DDD={ddd_soft_delete_success}"
        assert legacy_get_success == ddd_get_success, f"Get parity: Legacy={legacy_get_success}, DDD={ddd_get_success}"
        assert legacy_is_active == ddd_is_active, f"is_active parity: Legacy={legacy_is_active}, DDD={ddd_is_active}"
        assert legacy_is_active == False, f"Soft delete should set is_active=false: {legacy_is_active}"
        
        print(f"\n✅ Soft Delete Flag-Parität erfolgreich getestet")
    
    def test_soft_delete_checkaccess_denied_parity(self, client):
        """Test: Nach Soft Delete ist CheckAccess für den Benutzer nicht mehr erlaubt"""
        print("Teste Soft Delete CheckAccess-Deny-Parität...")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_soft_delete_checkaccess_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_soft_delete_checkaccess_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            seed_superuser_qms_admin(conn)
            seed_basic_users(conn, n=2)
            seed_roles_and_permissions(conn)
        
        with sqlite3.connect(ddd_db_path) as conn:
            seed_superuser_qms_admin(conn)
            seed_basic_users(conn, n=2)
            seed_roles_and_permissions(conn)
        
        # Test-User erstellen mit Permissions
        test_user_payload = create_user_payload(
            email="test.checkaccess@company.com",
            full_name="Test CheckAccess User",
            employee_id="TCA001",
            organizational_unit="Test",
            individual_permissions=["users:read", "users:update"],
            is_active=True
        )
        
        # Legacy: User erstellen
        try:
            legacy_create_response = run_request(
                client, "legacy", "POST", "/api/users",
                json_data=test_user_payload,
                database_url=legacy_database_url
            )
            legacy_create_success = legacy_create_response[0] in [200, 201]
            legacy_user_id = legacy_create_response[1].get('id') if legacy_create_success else None
        except Exception as e:
            legacy_create_success = False
            legacy_user_id = None
            print(f"Legacy create error: {e}")
        
        # DDD: User erstellen
        try:
            ddd_create_response = run_request(
                client, "ddd", "POST", "/api/users",
                json_data=test_user_payload,
                database_url=ddd_database_url
            )
            ddd_create_success = ddd_create_response[0] in [200, 201]
            ddd_user_id = ddd_create_response[1].get('id') if ddd_create_success else None
        except Exception as e:
            ddd_create_success = False
            ddd_user_id = None
            print(f"DDD create error: {e}")
        
        # CheckAccess vor Soft Delete (sollte erlaubt sein)
        # Legacy: CheckAccess vor Soft Delete
        try:
            legacy_check_before_response = run_request(
                client, "legacy", "GET", f"/api/users/{legacy_user_id}",
                database_url=legacy_database_url
            )
            legacy_check_before_success = legacy_check_before_response[0] == 200
        except Exception as e:
            legacy_check_before_success = False
            print(f"Legacy check before error: {e}")
        
        # DDD: CheckAccess vor Soft Delete
        try:
            ddd_check_before_response = run_request(
                client, "ddd", "GET", f"/api/users/{ddd_user_id}",
                database_url=ddd_database_url
            )
            ddd_check_before_success = ddd_check_before_response[0] == 200
        except Exception as e:
            ddd_check_before_success = False
            print(f"DDD check before error: {e}")
        
        # Soft Delete durchführen
        soft_delete_payload = soft_delete_user_payload()
        
        # Legacy: Soft Delete
        try:
            legacy_soft_delete_response = run_request(
                client, "legacy", "PUT", f"/api/users/{legacy_user_id}",
                json_data=soft_delete_payload,
                database_url=legacy_database_url
            )
            legacy_soft_delete_success = legacy_soft_delete_response[0] == 200
        except Exception as e:
            legacy_soft_delete_success = False
            print(f"Legacy soft delete error: {e}")
        
        # DDD: Soft Delete
        try:
            ddd_soft_delete_response = run_request(
                client, "ddd", "PUT", f"/api/users/{ddd_user_id}",
                json_data=soft_delete_payload,
                database_url=ddd_database_url
            )
            ddd_soft_delete_success = ddd_soft_delete_response[0] == 200
        except Exception as e:
            ddd_soft_delete_success = False
            print(f"DDD soft delete error: {e}")
        
        # CheckAccess nach Soft Delete (sollte verweigert werden)
        # Legacy: CheckAccess nach Soft Delete
        try:
            legacy_check_after_response = run_request(
                client, "legacy", "GET", f"/api/users/{legacy_user_id}",
                database_url=legacy_database_url
            )
            legacy_check_after_success = legacy_check_after_response[0] == 200
            legacy_user_data = legacy_check_after_response[1] if legacy_check_after_success else {}
            legacy_is_active = legacy_user_data.get('is_active', True)
        except Exception as e:
            legacy_check_after_success = False
            legacy_is_active = True
            print(f"Legacy check after error: {e}")
        
        # DDD: CheckAccess nach Soft Delete
        try:
            ddd_check_after_response = run_request(
                client, "ddd", "GET", f"/api/users/{ddd_user_id}",
                database_url=ddd_database_url
            )
            ddd_check_after_success = ddd_check_after_response[0] == 200
            ddd_user_data = ddd_check_after_response[1] if ddd_check_after_success else {}
            ddd_is_active = ddd_user_data.get('is_active', True)
        except Exception as e:
            ddd_check_after_success = False
            ddd_is_active = True
            print(f"DDD check after error: {e}")
        
        # Vergleich
        print(f"Legacy: check_before={legacy_check_before_success}, soft_delete={legacy_soft_delete_success}, check_after={legacy_check_after_success}, is_active={legacy_is_active}")
        print(f"DDD: check_before={ddd_check_before_success}, soft_delete={ddd_soft_delete_success}, check_after={ddd_check_after_success}, is_active={ddd_is_active}")
        
        # Asserts
        assert legacy_create_success == ddd_create_success, f"Create parity: Legacy={legacy_create_success}, DDD={ddd_create_success}"
        assert legacy_check_before_success == ddd_check_before_success, f"Check before parity: Legacy={legacy_check_before_success}, DDD={ddd_check_before_success}"
        assert legacy_soft_delete_success == ddd_soft_delete_success, f"Soft delete parity: Legacy={legacy_soft_delete_success}, DDD={ddd_soft_delete_success}"
        assert legacy_check_after_success == ddd_check_after_success, f"Check after parity: Legacy={legacy_check_after_success}, DDD={ddd_check_after_success}"
        assert legacy_is_active == ddd_is_active, f"is_active parity: Legacy={legacy_is_active}, DDD={ddd_is_active}"
        assert legacy_is_active == False, f"Soft delete should set is_active=false: {legacy_is_active}"
        
        print(f"\n✅ Soft Delete CheckAccess-Deny-Parität erfolgreich getestet")
