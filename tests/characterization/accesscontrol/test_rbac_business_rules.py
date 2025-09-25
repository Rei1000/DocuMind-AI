"""
RBAC Business Rules Charakterisierungstests
Testet CheckAccess, Rollenzuweisungskaskaden, Konfliktfälle
"""

import pytest
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from tests.helpers.payloads_accesscontrol import (
    unique_user_payload, membership_payload, document_status_change_payload
)


class TestRBACBusinessRules:
    """Testet RBAC-Business-Regeln und -Logik"""
    
    def test_approval_level_hierarchy(self, client):
        """Test: Approval Level Hierarchie - Legacy vs DDD"""
        print("Teste Approval Level Hierarchie...")
        
        # Teste verschiedene Approval Levels
        test_levels = [1, 2, 3, 4, 5]
        
        for level in test_levels:
            # User mit spezifischem Approval Level erstellen
            user_data = unique_user_payload(
                f"level_{level}_user", f"Level {level} User", f"LVL{level:03d}",
                approval_level=level
            )
            
            # Legacy-Create
            legacy_create = run_request(
                client, "legacy", "POST", "/api/users", json_data=user_data
            )
            
            # DDD-Create
            ddd_create = run_request(
                client, "ddd", "POST", "/api/users", json_data=user_data
            )
            
            # Vergleich
            create_comparison = compare_responses(legacy_create, ddd_create)
            print(f"Level {level} User Create: {format_comparison_result(create_comparison)}")
            
            # Statuscodes müssen identisch sein
            assert create_comparison["status_equal"], f"Level {level} Create-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        print(f"\n✅ Approval Level Hierarchie erfolgreich getestet")
    
    def test_department_head_privileges(self, client):
        """Test: Department Head Privileges - Legacy vs DDD"""
        print("Teste Department Head Privileges...")
        
        # 1. Department Head User erstellen
        dept_head_data = unique_user_payload(
            "dept_head", "Department Head", "DEPT001",
            is_department_head=True,
            approval_level=3
        )
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/users", json_data=dept_head_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/users", json_data=dept_head_data
        )
        
        # Vergleich
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"Department Head Create: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Dept-Head-Create-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        # 2. Department Head in Group zuweisen
        if legacy_create[0] == 200 and ddd_create[0] == 200:
            user_id = legacy_create[1]["id"]
            
            membership_data = membership_payload(
                user_id=user_id,
                interest_group_id=1,  # Quality Management
                role_in_group="Department Head",
                approval_level=3,
                is_department_head=True
            )
            
            # Legacy-Membership
            legacy_membership = run_request(
                client, "legacy", "POST", "/api/memberships", json_data=membership_data
            )
            
            # DDD-Membership
            ddd_membership = run_request(
                client, "ddd", "POST", "/api/memberships", json_data=membership_data
            )
            
            # Vergleich
            membership_comparison = compare_responses(legacy_membership, ddd_membership)
            print(f"Department Head Membership: {format_comparison_result(membership_comparison)}")
            
            # Statuscodes müssen identisch sein
            assert membership_comparison["status_equal"], f"Dept-Head-Membership-Status unterscheidet sich: {membership_comparison['status_diff']}"
        
        print(f"\n✅ Department Head Privileges erfolgreich getestet")
    
    def test_multi_group_membership(self, client):
        """Test: Multi-Group Membership - Legacy vs DDD"""
        print("Teste Multi-Group Membership...")
        
        # 1. User erstellen
        user_data = unique_user_payload(
            "multi_group_user", "Multi Group User", "MULTI001",
            approval_level=2
        )
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/users", json_data=user_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/users", json_data=user_data
        )
        
        # Vergleich
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"Multi-Group User Create: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Multi-Group-Create-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        # 2. User in mehrere Gruppen zuweisen
        if legacy_create[0] == 200 and ddd_create[0] == 200:
            user_id = legacy_create[1]["id"]
            
            # Membership 1: Quality Management
            membership1_data = membership_payload(
                user_id=user_id,
                interest_group_id=1,  # Quality Management
                role_in_group="QM Representative",
                approval_level=2
            )
            
            # Legacy-Membership 1
            legacy_membership1 = run_request(
                client, "legacy", "POST", "/api/memberships", json_data=membership1_data
            )
            
            # DDD-Membership 1
            ddd_membership1 = run_request(
                client, "ddd", "POST", "/api/memberships", json_data=membership1_data
            )
            
            # Vergleich
            membership1_comparison = compare_responses(legacy_membership1, ddd_membership1)
            print(f"Multi-Group Membership 1: {format_comparison_result(membership1_comparison)}")
            
            # Statuscodes müssen identisch sein
            assert membership1_comparison["status_equal"], f"Multi-Group-Membership-1-Status unterscheidet sich: {membership1_comparison['status_diff']}"
            
            # Membership 2: Product Development
            membership2_data = membership_payload(
                user_id=user_id,
                interest_group_id=2,  # Product Development
                role_in_group="Developer",
                approval_level=1
            )
            
            # Legacy-Membership 2
            legacy_membership2 = run_request(
                client, "legacy", "POST", "/api/memberships", json_data=membership2_data
            )
            
            # DDD-Membership 2
            ddd_membership2 = run_request(
                client, "ddd", "POST", "/api/memberships", json_data=membership2_data
            )
            
            # Vergleich
            membership2_comparison = compare_responses(legacy_membership2, ddd_membership2)
            print(f"Multi-Group Membership 2: {format_comparison_result(membership2_comparison)}")
            
            # Statuscodes müssen identisch sein
            assert membership2_comparison["status_equal"], f"Multi-Group-Membership-2-Status unterscheidet sich: {membership2_comparison['status_diff']}"
        
        print(f"\n✅ Multi-Group Membership erfolgreich getestet")
    
    def test_permission_aggregation(self, client):
        """Test: Permission Aggregation - Legacy vs DDD"""
        print("Teste Permission Aggregation...")
        
        # 1. User mit individuellen Permissions erstellen
        user_data = unique_user_payload(
            "perm_user", "Permission User", "PERM001",
            individual_permissions=["custom_permission_1", "custom_permission_2"],
            approval_level=2
        )
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/users", json_data=user_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/users", json_data=user_data
        )
        
        # Vergleich
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"Permission User Create: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Permission-Create-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        # 2. User in Group mit Group-Permissions zuweisen
        if legacy_create[0] == 200 and ddd_create[0] == 200:
            user_id = legacy_create[1]["id"]
            
            membership_data = membership_payload(
                user_id=user_id,
                interest_group_id=1,  # Quality Management (hat group_permissions)
                role_in_group="Permission Tester",
                approval_level=2
            )
            
            # Legacy-Membership
            legacy_membership = run_request(
                client, "legacy", "POST", "/api/memberships", json_data=membership_data
            )
            
            # DDD-Membership
            ddd_membership = run_request(
                client, "ddd", "POST", "/api/memberships", json_data=membership_data
            )
            
            # Vergleich
            membership_comparison = compare_responses(legacy_membership, ddd_membership)
            print(f"Permission Membership: {format_comparison_result(membership_comparison)}")
            
            # Statuscodes müssen identisch sein
            assert membership_comparison["status_equal"], f"Permission-Membership-Status unterscheidet sich: {membership_comparison['status_diff']}"
        
        print(f"\n✅ Permission Aggregation erfolgreich getestet")
    
    def test_duplicate_membership_conflict(self, client):
        """Test: Duplicate Membership Conflict - Legacy vs DDD"""
        print("Teste Duplicate Membership Conflict...")
        
        # 1. Duplikat-Membership (User 1 → Group 1, bereits vorhanden)
        duplicate_data = membership_payload(
            user_id=1,  # Admin User
            interest_group_id=1,  # Quality Management (bereits vorhanden)
            role_in_group="Duplicate Member",
            approval_level=1
        )
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/memberships", json_data=duplicate_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/memberships", json_data=duplicate_data
        )
        
        # Vergleich
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"Duplicate Membership: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Duplicate-Membership-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        print(f"\n✅ Duplicate Membership Conflict erfolgreich getestet")
    
    def test_invalid_approval_level(self, client):
        """Test: Invalid Approval Level - Legacy vs DDD"""
        print("Teste Invalid Approval Level...")
        
        # 1. User mit ungültigem Approval Level erstellen
        invalid_data = unique_user_payload(
            "invalid_level_user", "Invalid Level User", "INV001",
            approval_level=6  # Ungültiger Level (> 5)
        )
        
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
        print(f"Invalid Approval Level: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Invalid-Level-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        print(f"\n✅ Invalid Approval Level erfolgreich getestet")
    
    def test_empty_permissions_handling(self, client):
        """Test: Empty Permissions Handling - Legacy vs DDD"""
        print("Teste Empty Permissions Handling...")
        
        # 1. User mit leeren Permissions erstellen
        empty_data = unique_user_payload(
            "empty_perms_user", "Empty Permissions User", "EMP001",
            individual_permissions=[],
            approval_level=1
        )
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/users", json_data=empty_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/users", json_data=empty_data
        )
        
        # Vergleich
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"Empty Permissions: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Empty-Permissions-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        print(f"\n✅ Empty Permissions Handling erfolgreich getestet")
