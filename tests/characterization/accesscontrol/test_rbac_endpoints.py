"""
RBAC Endpoints Charakterisierungstests
Testet CRUD für Users, Memberships, Permissions mit Legacy vs DDD Parität
"""

import pytest
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from tests.helpers.payloads_accesscontrol import (
    unique_user_payload, membership_payload, login_payload,
    admin_user_payload, qm_manager_payload, team_member_payload
)


class TestRBACEndpoints:
    """Testet RBAC-Endpunkte für Users, Memberships, Permissions"""
    
    def test_user_crud_parity(self, client):
        """Test: User CRUD - Legacy vs DDD Parität"""
        print("Teste User CRUD Parität...")
        
        # 1. User erstellen
        create_data = unique_user_payload("test_user", "Test User", "TEST001")
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/users", json_data=create_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/users", json_data=create_data
        )
        
        # Vergleich
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"User Create: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Create-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        # 2. User abrufen (falls erstellt)
        if legacy_create[0] == 200 and ddd_create[0] == 200:
            user_id = legacy_create[1]["id"]
            
            # Legacy-Get
            legacy_get = run_request(
                client, "legacy", "GET", f"/api/users/{user_id}"
            )
            
            # DDD-Get
            ddd_get = run_request(
                client, "ddd", "GET", f"/api/users/{user_id}"
            )
            
            # Vergleich
            get_comparison = compare_responses(legacy_get, ddd_get)
            print(f"User Get: {format_comparison_result(get_comparison)}")
            
            # Statuscodes müssen identisch sein
            assert get_comparison["status_equal"], f"Get-Status unterscheidet sich: {get_comparison['status_diff']}"
        
        print(f"\n✅ User CRUD Parität erfolgreich getestet")
    
    def test_membership_crud_parity(self, client):
        """Test: Membership CRUD - Legacy vs DDD Parität"""
        print("Teste Membership CRUD Parität...")
        
        # 1. Membership erstellen (User 1 → Group 1)
        create_data = membership_payload(
            user_id=1,
            interest_group_id=1,
            role_in_group="Test Member",
            approval_level=2
        )
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/memberships", json_data=create_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/memberships", json_data=create_data
        )
        
        # Vergleich
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"Membership Create: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Create-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        # 2. Memberships abrufen
        # Legacy-Get
        legacy_get = run_request(
            client, "legacy", "GET", "/api/memberships"
        )
        
        # DDD-Get
        ddd_get = run_request(
            client, "ddd", "GET", "/api/memberships"
        )
        
        # Vergleich
        get_comparison = compare_responses(legacy_get, ddd_get)
        print(f"Membership Get: {format_comparison_result(get_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert get_comparison["status_equal"], f"Get-Status unterscheidet sich: {get_comparison['status_diff']}"
        
        print(f"\n✅ Membership CRUD Parität erfolgreich getestet")
    
    def test_authentication_parity(self, client):
        """Test: Authentication - Legacy vs DDD Parität"""
        print("Teste Authentication Parität...")
        
        # 1. Login
        login_data = login_payload("admin@company.com", "admin123")
        
        # Legacy-Login
        legacy_login = run_request(
            client, "legacy", "POST", "/api/auth/login", json_data=login_data
        )
        
        # DDD-Login
        ddd_login = run_request(
            client, "ddd", "POST", "/api/auth/login", json_data=login_data
        )
        
        # Vergleich
        login_comparison = compare_responses(legacy_login, ddd_login)
        print(f"Login: {format_comparison_result(login_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert login_comparison["status_equal"], f"Login-Status unterscheidet sich: {login_comparison['status_diff']}"
        
        # 2. User Info abrufen (falls Login erfolgreich)
        if legacy_login[0] == 200 and ddd_login[0] == 200:
            # Legacy-User-Info
            legacy_user_info = run_request(
                client, "legacy", "GET", "/api/auth/me"
            )
            
            # DDD-User-Info
            ddd_user_info = run_request(
                client, "ddd", "GET", "/api/auth/me"
            )
            
            # Vergleich
            user_info_comparison = compare_responses(legacy_user_info, ddd_user_info)
            print(f"User Info: {format_comparison_result(user_info_comparison)}")
            
            # Statuscodes müssen identisch sein
            assert user_info_comparison["status_equal"], f"User-Info-Status unterscheidet sich: {user_info_comparison['status_diff']}"
        
        print(f"\n✅ Authentication Parität erfolgreich getestet")
    
    def test_user_list_parity(self, client):
        """Test: User List - Legacy vs DDD Parität"""
        print("Teste User List Parität...")
        
        # Legacy-User-List
        legacy_list = run_request(
            client, "legacy", "GET", "/api/users"
        )
        
        # DDD-User-List
        ddd_list = run_request(
            client, "ddd", "GET", "/api/users"
        )
        
        # Vergleich
        list_comparison = compare_responses(legacy_list, ddd_list)
        print(f"User List: {format_comparison_result(list_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert list_comparison["status_equal"], f"List-Status unterscheidet sich: {list_comparison['status_diff']}"
        
        print(f"\n✅ User List Parität erfolgreich getestet")
    
    def test_user_update_parity(self, client):
        """Test: User Update - Legacy vs DDD Parität"""
        print("Teste User Update Parität...")
        
        # 1. User aktualisieren (User ID 2)
        update_data = {
            "organizational_unit": "Updated Department",
            "approval_level": 3
        }
        
        # Legacy-Update
        legacy_update = run_request(
            client, "legacy", "PUT", "/api/users/2", json_data=update_data
        )
        
        # DDD-Update
        ddd_update = run_request(
            client, "ddd", "PUT", "/api/users/2", json_data=update_data
        )
        
        # Vergleich
        update_comparison = compare_responses(legacy_update, ddd_update)
        print(f"User Update: {format_comparison_result(update_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert update_comparison["status_equal"], f"Update-Status unterscheidet sich: {update_comparison['status_diff']}"
        
        print(f"\n✅ User Update Parität erfolgreich getestet")
    
    def test_invalid_user_creation_parity(self, client):
        """Test: Invalid User Creation - Legacy vs DDD Parität"""
        print("Teste Invalid User Creation Parität...")
        
        # Ungültige User-Daten
        invalid_data = {
            "email": "invalid-email",  # Ungültige Email
            "full_name": "",  # Leerer Name
            "employee_id": "INV001",
            "approval_level": 6  # Ungültiger Level
        }
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/users", json_data=invalid_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/users", json_data=invalid_data
        )
        
        # Vergleich
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"Invalid User Create: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Invalid-Create-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        print(f"\n✅ Invalid User Creation Parität erfolgreich getestet")
    
    def test_duplicate_user_creation_parity(self, client):
        """Test: Duplicate User Creation - Legacy vs DDD Parität"""
        print("Teste Duplicate User Creation Parität...")
        
        # Duplikat-User (gleiche Email wie Admin)
        duplicate_data = {
            "email": "admin@company.com",  # Gleiche Email
            "full_name": "Duplicate Admin",
            "employee_id": "DUP001",
            "organizational_unit": "Test"
        }
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/users", json_data=duplicate_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/users", json_data=duplicate_data
        )
        
        # Vergleich
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"Duplicate User Create: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Duplicate-Create-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        print(f"\n✅ Duplicate User Creation Parität erfolgreich getestet")

