"""
QMS Admin Superuser Tests
Testet Superuser qms.admin Vollzugriff und Admin-Funktionen
"""

import pytest
import os
import uuid
import sqlite3
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from tests.helpers.seeds_accesscontrol import seed_superuser_qms_admin, seed_basic_users, seed_roles_and_permissions
from tests.helpers.payloads_accesscontrol import create_user_payload, update_user_payload, superuser_qms_admin_payload


class TestQmsAdminSuperuser:
    """Testet QMS Admin Superuser Verhalten"""
    
    def test_superuser_create_user_parity(self, client):
        """Test: qms.admin darf neue Benutzer anlegen (POST /users) → 200/201 parity"""
        print("Teste Superuser Create User Parität...")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_superuser_create_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_superuser_create_{uuid.uuid4().hex[:8]}_ddd.db"
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
        
        # Test-User Payload
        test_user_payload = create_user_payload(
            email="new.user@company.com",
            full_name="New User",
            employee_id="NEW001",
            organizational_unit="Test",
            individual_permissions=["users:read"],
            is_active=True
        )
        
        # Legacy: Superuser erstellt User
        try:
            legacy_create_response = run_request(
                client, "legacy", "POST", "/api/users",
                json_data=test_user_payload,
                database_url=legacy_database_url
            )
            legacy_create_status = legacy_create_response[0]
            legacy_create_success = legacy_create_status in [200, 201]
            legacy_user_data = legacy_create_response[1] if legacy_create_success else {}
            legacy_user_id = legacy_user_data.get('id')
            legacy_user_email = legacy_user_data.get('email')
        except Exception as e:
            legacy_create_status = 500
            legacy_create_success = False
            legacy_user_id = None
            legacy_user_email = None
            print(f"Legacy create error: {e}")
        
        # DDD: Superuser erstellt User
        try:
            ddd_create_response = run_request(
                client, "ddd", "POST", "/api/users",
                json_data=test_user_payload,
                database_url=ddd_database_url
            )
            ddd_create_status = ddd_create_response[0]
            ddd_create_success = ddd_create_status in [200, 201]
            ddd_user_data = ddd_create_response[1] if ddd_create_success else {}
            ddd_user_id = ddd_user_data.get('id')
            ddd_user_email = ddd_user_data.get('email')
        except Exception as e:
            ddd_create_status = 500
            ddd_create_success = False
            ddd_user_id = None
            ddd_user_email = None
            print(f"DDD create error: {e}")
        
        # Vergleich
        print(f"Legacy: create_status={legacy_create_status}, success={legacy_create_success}, user_id={legacy_user_id}, email={legacy_user_email}")
        print(f"DDD: create_status={ddd_create_status}, success={ddd_create_success}, user_id={ddd_user_id}, email={ddd_user_email}")
        
        # Asserts
        assert legacy_create_success == ddd_create_success, f"Create success parity: Legacy={legacy_create_success}, DDD={ddd_create_success}"
        assert legacy_create_status == ddd_create_status, f"Create status parity: Legacy={legacy_create_status}, DDD={ddd_create_status}"
        assert legacy_user_id == ddd_user_id, f"User ID parity: Legacy={legacy_user_id}, DDD={ddd_user_id}"
        assert legacy_user_email == ddd_user_email, f"User email parity: Legacy={legacy_user_email}, DDD={ddd_user_email}"
        
        print(f"\n✅ Superuser Create User Parität erfolgreich getestet")
    
    def test_superuser_update_user_parity(self, client):
        """Test: qms.admin darf Benutzer bearbeiten (PUT /users/{id}) → 200 parity"""
        print("Teste Superuser Update User Parität...")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_superuser_update_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_superuser_update_{uuid.uuid4().hex[:8]}_ddd.db"
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
        
        # Test-User erstellen (User 101)
        test_user_payload = create_user_payload(
            email="update.test@company.com",
            full_name="Update Test User",
            employee_id="UTU001",
            organizational_unit="Test",
            individual_permissions=["users:read"],
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
        
        # Update-Payload
        update_payload = update_user_payload(
            full_name="Updated Test User",
            organizational_unit="Updated Test",
            individual_permissions=["users:read", "users:update"]
        )
        
        # Legacy: Superuser updated User
        try:
            legacy_update_response = run_request(
                client, "legacy", "PUT", f"/api/users/{legacy_user_id}",
                json_data=update_payload,
                database_url=legacy_database_url
            )
            legacy_update_status = legacy_update_response[0]
            legacy_update_success = legacy_update_status == 200
            legacy_updated_data = legacy_update_response[1] if legacy_update_success else {}
        except Exception as e:
            legacy_update_status = 500
            legacy_update_success = False
            legacy_updated_data = {}
            print(f"Legacy update error: {e}")
        
        # DDD: Superuser updated User
        try:
            ddd_update_response = run_request(
                client, "ddd", "PUT", f"/api/users/{ddd_user_id}",
                json_data=update_payload,
                database_url=ddd_database_url
            )
            ddd_update_status = ddd_update_response[0]
            ddd_update_success = ddd_update_status == 200
            ddd_updated_data = ddd_update_response[1] if ddd_update_success else {}
        except Exception as e:
            ddd_update_status = 500
            ddd_update_success = False
            ddd_updated_data = {}
            print(f"DDD update error: {e}")
        
        # Vergleich
        print(f"Legacy: update_status={legacy_update_status}, success={legacy_update_success}, updated_name={legacy_updated_data.get('full_name')}")
        print(f"DDD: update_status={ddd_update_status}, success={ddd_update_success}, updated_name={ddd_updated_data.get('full_name')}")
        
        # Asserts
        assert legacy_create_success == ddd_create_success, f"Create parity: Legacy={legacy_create_success}, DDD={ddd_create_success}"
        assert legacy_update_success == ddd_update_success, f"Update success parity: Legacy={legacy_update_success}, DDD={ddd_update_success}"
        assert legacy_update_status == ddd_update_status, f"Update status parity: Legacy={legacy_update_status}, DDD={ddd_update_status}"
        
        print(f"\n✅ Superuser Update User Parität erfolgreich getestet")
    
    def test_superuser_assign_revoke_role_parity(self, client):
        """Test: qms.admin darf Rollen zuweisen/entziehen → 200 parity"""
        print("Teste Superuser Assign/Revoke Role Parität...")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_superuser_roles_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_superuser_roles_{uuid.uuid4().hex[:8]}_ddd.db"
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
        
        # Test-User erstellen (User 101)
        test_user_payload = create_user_payload(
            email="role.test@company.com",
            full_name="Role Test User",
            employee_id="RTU001",
            organizational_unit="Test",
            individual_permissions=[],
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
        
        # Role Assignment (über User-Update simulieren)
        role_assignment_payload = update_user_payload(
            individual_permissions=["users:read", "users:update"]
        )
        
        # Legacy: Superuser assigned Role
        try:
            legacy_assign_response = run_request(
                client, "legacy", "PUT", f"/api/users/{legacy_user_id}",
                json_data=role_assignment_payload,
                database_url=legacy_database_url
            )
            legacy_assign_status = legacy_assign_response[0]
            legacy_assign_success = legacy_assign_status == 200
        except Exception as e:
            legacy_assign_status = 500
            legacy_assign_success = False
            print(f"Legacy assign error: {e}")
        
        # DDD: Superuser assigned Role
        try:
            ddd_assign_response = run_request(
                client, "ddd", "PUT", f"/api/users/{ddd_user_id}",
                json_data=role_assignment_payload,
                database_url=ddd_database_url
            )
            ddd_assign_status = ddd_assign_response[0]
            ddd_assign_success = ddd_assign_status == 200
        except Exception as e:
            ddd_assign_status = 500
            ddd_assign_success = False
            print(f"DDD assign error: {e}")
        
        # Role Revocation (Permissions entfernen)
        role_revocation_payload = update_user_payload(
            individual_permissions=[]
        )
        
        # Legacy: Superuser revoked Role
        try:
            legacy_revoke_response = run_request(
                client, "legacy", "PUT", f"/api/users/{legacy_user_id}",
                json_data=role_revocation_payload,
                database_url=legacy_database_url
            )
            legacy_revoke_status = legacy_revoke_response[0]
            legacy_revoke_success = legacy_revoke_status == 200
        except Exception as e:
            legacy_revoke_status = 500
            legacy_revoke_success = False
            print(f"Legacy revoke error: {e}")
        
        # DDD: Superuser revoked Role
        try:
            ddd_revoke_response = run_request(
                client, "ddd", "PUT", f"/api/users/{ddd_user_id}",
                json_data=role_revocation_payload,
                database_url=ddd_database_url
            )
            ddd_revoke_status = ddd_revoke_response[0]
            ddd_revoke_success = ddd_revoke_status == 200
        except Exception as e:
            ddd_revoke_status = 500
            ddd_revoke_success = False
            print(f"DDD revoke error: {e}")
        
        # Vergleich
        print(f"Legacy: assign_status={legacy_assign_status}, revoke_status={legacy_revoke_status}")
        print(f"DDD: assign_status={ddd_assign_status}, revoke_status={ddd_revoke_status}")
        
        # Asserts
        assert legacy_create_success == ddd_create_success, f"Create parity: Legacy={legacy_create_success}, DDD={ddd_create_success}"
        assert legacy_assign_success == ddd_assign_success, f"Assign success parity: Legacy={legacy_assign_success}, DDD={ddd_assign_success}"
        assert legacy_revoke_success == ddd_revoke_success, f"Revoke success parity: Legacy={legacy_revoke_success}, DDD={ddd_revoke_success}"
        
        print(f"\n✅ Superuser Assign/Revoke Role Parität erfolgreich getestet")
    
    def test_superuser_checkaccess_always_true_parity(self, client):
        """Test: qms.admin hat CheckAccess immer true für beliebige permission codes"""
        print("Teste Superuser CheckAccess Always True Parität...")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_superuser_checkaccess_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_superuser_checkaccess_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_database_url}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            seed_superuser_qms_admin(conn)
            seed_basic_users(conn, n=2)
            seed_roles_and_permissions(conn)
        
        with sqlite3.connect(ddd_db_path) as conn:
            seed_superuser_qms_admin(conn)
            seed_basic_users(conn, n=2)
            seed_roles_and_permissions(conn)
        
        # Test verschiedene Permissions
        test_permissions = [
            "users:create",
            "users:update", 
            "users:delete",
            "roles:assign",
            "system:admin",
            "nonexistent:permission"
        ]
        
        legacy_results = {}
        ddd_results = {}
        
        for permission in test_permissions:
            # Legacy: CheckAccess für qms.admin
            try:
                legacy_check_response = run_request(
                    client, "legacy", "GET", "/api/users/999",  # qms.admin ID
                    database_url=legacy_database_url
                )
                legacy_check_success = legacy_check_response[0] == 200
                legacy_user_data = legacy_check_response[1] if legacy_check_success else {}
                legacy_permissions = legacy_user_data.get('permissions', [])
                legacy_has_permission = "*" in legacy_permissions or permission in legacy_permissions
            except Exception as e:
                legacy_has_permission = False
                print(f"Legacy check {permission} error: {e}")
            
            # DDD: CheckAccess für qms.admin
            try:
                ddd_check_response = run_request(
                    client, "ddd", "GET", "/api/users/999",  # qms.admin ID
                    database_url=ddd_database_url
                )
                ddd_check_success = ddd_check_response[0] == 200
                ddd_user_data = ddd_check_response[1] if ddd_check_success else {}
                ddd_permissions = ddd_user_data.get('permissions', [])
                ddd_has_permission = "*" in ddd_permissions or permission in ddd_permissions
            except Exception as e:
                ddd_has_permission = False
                print(f"DDD check {permission} error: {e}")
            
            legacy_results[permission] = legacy_has_permission
            ddd_results[permission] = ddd_has_permission
        
        # Vergleich
        print(f"Legacy results: {legacy_results}")
        print(f"DDD results: {ddd_results}")
        
        # Asserts
        for permission in test_permissions:
            assert legacy_results[permission] == ddd_results[permission], f"Permission {permission} parity: Legacy={legacy_results[permission]}, DDD={ddd_results[permission]}"
            assert legacy_results[permission] == True, f"Superuser should have permission {permission}: {legacy_results[permission]}"
        
        print(f"\n✅ Superuser CheckAccess Always True Parität erfolgreich getestet")
    
    def test_superuser_interest_group_actions_smoke(self, client):
        """Test: qms.admin darf Interest-Group-bezogene Aktionen (smoke)"""
        print("Teste Superuser Interest Group Actions Smoke...")
        
        # Prüfe ob Interest Group Endpoints vorhanden sind
        try:
            # Test ob Interest Group Endpoint existiert
            test_response = run_request(
                client, "legacy", "GET", "/api/interest-groups"
            )
            interest_groups_available = test_response[0] in [200, 404]  # 404 ist OK, bedeutet Endpoint existiert
        except Exception as e:
            interest_groups_available = False
            print(f"Interest Groups endpoint not available: {e}")
        
        if not interest_groups_available:
            pytest.skip("Interest Group endpoints not available - skipping smoke test")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_superuser_ig_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_superuser_ig_{uuid.uuid4().hex[:8]}_ddd.db"
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
        
        # Test Interest Group Actions
        # Legacy: Superuser kann Interest Groups abrufen
        try:
            legacy_ig_response = run_request(
                client, "legacy", "GET", "/api/interest-groups",
                database_url=legacy_database_url
            )
            legacy_ig_success = legacy_ig_response[0] == 200
        except Exception as e:
            legacy_ig_success = False
            print(f"Legacy IG error: {e}")
        
        # DDD: Superuser kann Interest Groups abrufen
        try:
            ddd_ig_response = run_request(
                client, "ddd", "GET", "/api/interest-groups",
                database_url=ddd_database_url
            )
            ddd_ig_success = ddd_ig_response[0] == 200
        except Exception as e:
            ddd_ig_success = False
            print(f"DDD IG error: {e}")
        
        # Vergleich
        print(f"Legacy IG access: {legacy_ig_success}")
        print(f"DDD IG access: {ddd_ig_success}")
        
        # Asserts
        assert legacy_ig_success == ddd_ig_success, f"Interest Group access parity: Legacy={legacy_ig_success}, DDD={ddd_ig_success}"
        
        print(f"\n✅ Superuser Interest Group Actions Smoke erfolgreich getestet")

