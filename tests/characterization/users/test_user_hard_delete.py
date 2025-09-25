"""
User Hard Delete Tests
Testet Hard Delete Verhalten (Row entfernt, 404 bei GET)
"""

import pytest
import os
import uuid
import sqlite3
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from tests.helpers.seeds_accesscontrol import seed_superuser_qms_admin, seed_basic_users, seed_roles_and_permissions
from tests.helpers.payloads_accesscontrol import create_user_payload, hard_delete_user_payload


class TestUserHardDelete:
    """Testet User Hard Delete Verhalten"""
    
    def test_hard_delete_404_parity(self, client):
        """Test: Create User → Hard Delete → GET /users/{id} liefert 404"""
        print("Teste Hard Delete 404-Parität...")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_hard_delete_404_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_hard_delete_404_{uuid.uuid4().hex[:8]}_ddd.db"
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
            email="test.harddelete@company.com",
            full_name="Test Hard Delete User",
            employee_id="THD001",
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
        
        # GET User vor Hard Delete (sollte 200 sein)
        # Legacy: GET User vor Delete
        try:
            legacy_get_before_response = run_request(
                client, "legacy", "GET", f"/api/users/{legacy_user_id}",
                database_url=legacy_database_url
            )
            legacy_get_before_success = legacy_get_before_response[0] == 200
        except Exception as e:
            legacy_get_before_success = False
            print(f"Legacy get before error: {e}")
        
        # DDD: GET User vor Delete
        try:
            ddd_get_before_response = run_request(
                client, "ddd", "GET", f"/api/users/{ddd_user_id}",
                database_url=ddd_database_url
            )
            ddd_get_before_success = ddd_get_before_response[0] == 200
        except Exception as e:
            ddd_get_before_success = False
            print(f"DDD get before error: {e}")
        
        # Hard Delete durchführen
        # Legacy: Hard Delete
        try:
            legacy_hard_delete_response = run_request(
                client, "legacy", "DELETE", f"/api/users/{legacy_user_id}",
                database_url=legacy_database_url
            )
            legacy_hard_delete_success = legacy_hard_delete_response[0] in [200, 204]
        except Exception as e:
            legacy_hard_delete_success = False
            print(f"Legacy hard delete error: {e}")
        
        # DDD: Hard Delete
        try:
            ddd_hard_delete_response = run_request(
                client, "ddd", "DELETE", f"/api/users/{ddd_user_id}",
                database_url=ddd_database_url
            )
            ddd_hard_delete_success = ddd_hard_delete_response[0] in [200, 204]
        except Exception as e:
            ddd_hard_delete_success = False
            print(f"DDD hard delete error: {e}")
        
        # GET User nach Hard Delete (sollte 404 sein)
        # Legacy: GET User nach Delete
        try:
            legacy_get_after_response = run_request(
                client, "legacy", "GET", f"/api/users/{legacy_user_id}",
                database_url=legacy_database_url
            )
            legacy_get_after_status = legacy_get_after_response[0]
            legacy_get_after_404 = legacy_get_after_status == 404
        except Exception as e:
            legacy_get_after_status = 500
            legacy_get_after_404 = False
            print(f"Legacy get after error: {e}")
        
        # DDD: GET User nach Delete
        try:
            ddd_get_after_response = run_request(
                client, "ddd", "GET", f"/api/users/{ddd_user_id}",
                database_url=ddd_database_url
            )
            ddd_get_after_status = ddd_get_after_response[0]
            ddd_get_after_404 = ddd_get_after_status == 404
        except Exception as e:
            ddd_get_after_status = 500
            ddd_get_after_404 = False
            print(f"DDD get after error: {e}")
        
        # Vergleich
        print(f"Legacy: create={legacy_create_success}, get_before={legacy_get_before_success}, hard_delete={legacy_hard_delete_success}, get_after={legacy_get_after_status} (404={legacy_get_after_404})")
        print(f"DDD: create={ddd_create_success}, get_before={ddd_get_before_success}, hard_delete={ddd_hard_delete_success}, get_after={ddd_get_after_status} (404={ddd_get_after_404})")
        
        # Asserts
        assert legacy_create_success == ddd_create_success, f"Create parity: Legacy={legacy_create_success}, DDD={ddd_create_success}"
        assert legacy_get_before_success == ddd_get_before_success, f"Get before parity: Legacy={legacy_get_before_success}, DDD={ddd_get_before_success}"
        assert legacy_hard_delete_success == ddd_hard_delete_success, f"Hard delete parity: Legacy={legacy_hard_delete_success}, DDD={ddd_hard_delete_success}"
        assert legacy_get_after_404 == ddd_get_after_404, f"404 parity: Legacy={legacy_get_after_404}, DDD={ddd_get_after_404}"
        assert legacy_get_after_404 == True, f"Hard delete should result in 404: {legacy_get_after_404}"
        
        print(f"\n✅ Hard Delete 404-Parität erfolgreich getestet")
    
    def test_hard_delete_reference_integrity_parity(self, client):
        """Test: Referenzintegrität - gelöschter Benutzer darf keine aktiven role assignments mehr haben"""
        print("Teste Hard Delete Referenzintegrität...")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_hard_delete_refint_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_hard_delete_refint_{uuid.uuid4().hex[:8]}_ddd.db"
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
            email="test.refint@company.com",
            full_name="Test Reference Integrity User",
            employee_id="TRI001",
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
        
        # Prüfe Permissions vor Hard Delete (sollte vorhanden sein)
        # Legacy: Permissions vor Delete
        try:
            legacy_perms_before_response = run_request(
                client, "legacy", "GET", f"/api/users/{legacy_user_id}",
                database_url=legacy_database_url
            )
            legacy_perms_before_success = legacy_perms_before_response[0] == 200
            legacy_perms_before = legacy_perms_before_response[1].get('permissions', []) if legacy_perms_before_success else []
        except Exception as e:
            legacy_perms_before_success = False
            legacy_perms_before = []
            print(f"Legacy perms before error: {e}")
        
        # DDD: Permissions vor Delete
        try:
            ddd_perms_before_response = run_request(
                client, "ddd", "GET", f"/api/users/{ddd_user_id}",
                database_url=ddd_database_url
            )
            ddd_perms_before_success = ddd_perms_before_response[0] == 200
            ddd_perms_before = ddd_perms_before_response[1].get('permissions', []) if ddd_perms_before_success else []
        except Exception as e:
            ddd_perms_before_success = False
            ddd_perms_before = []
            print(f"DDD perms before error: {e}")
        
        # Hard Delete durchführen
        # Legacy: Hard Delete
        try:
            legacy_hard_delete_response = run_request(
                client, "legacy", "DELETE", f"/api/users/{legacy_user_id}",
                database_url=legacy_database_url
            )
            legacy_hard_delete_success = legacy_hard_delete_response[0] in [200, 204]
        except Exception as e:
            legacy_hard_delete_success = False
            print(f"Legacy hard delete error: {e}")
        
        # DDD: Hard Delete
        try:
            ddd_hard_delete_response = run_request(
                client, "ddd", "DELETE", f"/api/users/{ddd_user_id}",
                database_url=ddd_database_url
            )
            ddd_hard_delete_success = ddd_hard_delete_response[0] in [200, 204]
        except Exception as e:
            ddd_hard_delete_success = False
            print(f"DDD hard delete error: {e}")
        
        # Prüfe Permissions nach Hard Delete (sollte 404 oder leer sein)
        # Legacy: Permissions nach Delete
        try:
            legacy_perms_after_response = run_request(
                client, "legacy", "GET", f"/api/users/{legacy_user_id}",
                database_url=legacy_database_url
            )
            legacy_perms_after_status = legacy_perms_after_response[0]
            legacy_perms_after_404 = legacy_perms_after_status == 404
            legacy_perms_after = legacy_perms_after_response[1].get('permissions', []) if legacy_perms_after_status == 200 else []
        except Exception as e:
            legacy_perms_after_status = 500
            legacy_perms_after_404 = False
            legacy_perms_after = []
            print(f"Legacy perms after error: {e}")
        
        # DDD: Permissions nach Delete
        try:
            ddd_perms_after_response = run_request(
                client, "ddd", "GET", f"/api/users/{ddd_user_id}",
                database_url=ddd_database_url
            )
            ddd_perms_after_status = ddd_perms_after_response[0]
            ddd_perms_after_404 = ddd_perms_after_status == 404
            ddd_perms_after = ddd_perms_after_response[1].get('permissions', []) if ddd_perms_after_status == 200 else []
        except Exception as e:
            ddd_perms_after_status = 500
            ddd_perms_after_404 = False
            ddd_perms_after = []
            print(f"DDD perms after error: {e}")
        
        # Vergleich
        print(f"Legacy: perms_before={len(legacy_perms_before)}, hard_delete={legacy_hard_delete_success}, perms_after={legacy_perms_after_status} (404={legacy_perms_after_404}, perms={len(legacy_perms_after)})")
        print(f"DDD: perms_before={len(ddd_perms_before)}, hard_delete={ddd_hard_delete_success}, perms_after={ddd_perms_after_status} (404={ddd_perms_after_404}, perms={len(ddd_perms_after)})")
        
        # Asserts
        assert legacy_create_success == ddd_create_success, f"Create parity: Legacy={legacy_create_success}, DDD={ddd_create_success}"
        assert legacy_perms_before_success == ddd_perms_before_success, f"Perms before parity: Legacy={legacy_perms_before_success}, DDD={ddd_perms_before_success}"
        assert len(legacy_perms_before) > 0, f"User should have permissions before delete: {legacy_perms_before}"
        assert legacy_hard_delete_success == ddd_hard_delete_success, f"Hard delete parity: Legacy={legacy_hard_delete_success}, DDD={ddd_hard_delete_success}"
        assert legacy_perms_after_404 == ddd_perms_after_404, f"404 parity: Legacy={legacy_perms_after_404}, DDD={ddd_perms_after_404}"
        assert legacy_perms_after_404 == True or len(legacy_perms_after) == 0, f"After hard delete should be 404 or no permissions: 404={legacy_perms_after_404}, perms={len(legacy_perms_after)}"
        
        print(f"\n✅ Hard Delete Referenzintegrität erfolgreich getestet")

