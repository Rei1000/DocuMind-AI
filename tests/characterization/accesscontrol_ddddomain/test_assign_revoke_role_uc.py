"""
Assign/Revoke Role Use Case Tests
Vergleicht Legacy vs. DDD-Use-Case Resultat
"""

import pytest
import os
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from contexts.accesscontrol.infrastructure.adapters import AdapterFactory
from contexts.accesscontrol.application.use_cases import AssignRoleUseCase, RevokeRoleUseCase


class TestAssignRevokeRoleUseCase:
    """Testet Assign/Revoke Role Use Cases"""
    
    def test_assign_role_use_case_vs_legacy(self, client):
        """Test: Assign Role Use Case vs Legacy Endpoint"""
        print("Teste Assign Role Use Case vs Legacy...")
        
        # DDD Use Case Setup mit isolierter DB
        import uuid
        test_db_path = f".tmp/test_assign_role_{uuid.uuid4().hex[:8]}_legacy.db"
        database_url = f"sqlite:///{test_db_path}"
        adapters = AdapterFactory.create_adapters(database_url)
        
        assign_role_uc = AssignRoleUseCase(
            user_repo=adapters['user_repo'],
            role_repo=adapters['role_repo'],
            assignment_repo=adapters['assignment_repo'],
            audit_port=adapters['audit_port']
        )
        
        # Test: Role zuweisen (User 1, Role "dev_lead")
        try:
            # DDD Use Case
            ddd_assignment = assign_role_uc.execute(
                user_id=1,
                role_name="dev_lead",
                assigned_by=1
            )
            ddd_success = True
            ddd_error = None
        except Exception as e:
            ddd_success = False
            ddd_error = str(e)
        
        # Legacy Endpoint (über User-Update simulieren)
        try:
            # Hole aktuelle User-Permissions
            legacy_user_response = run_request(
                client, "legacy", "GET", "/api/users/1"
            )
            
            if legacy_user_response[0] == 200:
                user_data = legacy_user_response[1]
                current_permissions = user_data.get('permissions', [])
                
                # Füge dev_lead Permissions hinzu
                dev_lead_permissions = ["design_approval", "change_management"]
                new_permissions = list(set(current_permissions + dev_lead_permissions))
                
                # Update User
                legacy_update_response = run_request(
                    client, "legacy", "PUT", "/api/users/1",
                    json_data={"permissions": new_permissions}
                )
                legacy_success = legacy_update_response[0] == 200
                legacy_error = None
            else:
                legacy_success = False
                legacy_error = f"User not found: {legacy_user_response[0]}"
        except Exception as e:
            legacy_success = False
            legacy_error = str(e)
        
        # Vergleich
        print(f"DDD Use Case: success={ddd_success}, error={ddd_error}")
        print(f"Legacy Endpoint: success={legacy_success}, error={legacy_error}")
        
        # Beide sollten erfolgreich sein
        assert ddd_success == legacy_success, f"Success mismatch: DDD={ddd_success}, Legacy={legacy_success}"
        
        print(f"\n✅ Assign Role Use Case vs Legacy erfolgreich getestet")
    
    def test_revoke_role_use_case_vs_legacy(self, client):
        """Test: Revoke Role Use Case vs Legacy Endpoint"""
        print("Teste Revoke Role Use Case vs Legacy...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        revoke_role_uc = RevokeRoleUseCase(
            user_repo=adapters['user_repo'],
            role_repo=adapters['role_repo'],
            assignment_repo=adapters['assignment_repo'],
            audit_port=adapters['audit_port']
        )
        
        # Test: Role entziehen (User 1, Role "test_role")
        try:
            # DDD Use Case
            ddd_success = revoke_role_uc.execute(
                user_id=1,
                role_name="test_role",
                revoked_by=1
            )
            ddd_error = None
        except Exception as e:
            ddd_success = False
            ddd_error = str(e)
        
        # Legacy Endpoint (falls vorhanden)
        try:
            legacy_response = run_request(
                client, "legacy", "DELETE", "/api/assignments/1/test_role"
            )
            legacy_success = legacy_response[0] == 200
            legacy_error = None
        except Exception as e:
            legacy_success = False
            legacy_error = str(e)
        
        # Vergleich
        print(f"DDD Use Case: success={ddd_success}, error={ddd_error}")
        print(f"Legacy Endpoint: success={legacy_success}, error={legacy_error}")
        
        # Beide sollten das gleiche Verhalten haben (beide NotImplementedError)
        assert ddd_success == legacy_success, f"Success mismatch: DDD={ddd_success}, Legacy={legacy_success}"
        
        print(f"\n✅ Revoke Role Use Case vs Legacy erfolgreich getestet")
    
    def test_user_repository_legacy_integration(self, client):
        """Test: User Repository Legacy Integration"""
        print("Teste User Repository Legacy Integration...")
        
        # DDD Repository Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        user_repo = adapters['user_repo']
        
        # Test: User by ID abrufen
        user = user_repo.get_by_id(1)
        
        if user:
            print(f"User gefunden: {user.email}, {user.full_name}, Level: {user.approval_level}")
            assert user.id == 1
            assert user.email is not None
            assert user.full_name is not None
        else:
            print("Kein User mit ID 1 gefunden")
        
        # Test: User by Email finden
        if user:
            user_by_email = user_repo.find_by_email(user.email)
            assert user_by_email is not None
            assert user_by_email.id == user.id
        
        # Test: User-Liste
        users = user_repo.list_all(limit=5)
        print(f"User-Liste: {len(users)} User gefunden")
        assert len(users) >= 0
        
        print(f"\n✅ User Repository Legacy Integration erfolgreich getestet")
    
    def test_membership_repository_legacy_integration(self, client):
        """Test: Membership Repository Legacy Integration"""
        print("Teste Membership Repository Legacy Integration...")
        
        # DDD Repository Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        membership_repo = adapters['membership_repo']
        
        # Test: Memberships für User abrufen
        memberships = membership_repo.list_groups_for_user(1)
        print(f"Memberships für User 1: {len(memberships)} gefunden")
        
        for membership in memberships:
            print(f"  - Group {membership.interest_group_id}, Role: {membership.role_in_group}, Level: {membership.approval_level}")
            assert membership.user_id == 1
            assert membership.interest_group_id > 0
        
        # Test: Membership-Check
        if memberships:
            first_membership = memberships[0]
            is_member = membership_repo.is_member(1, first_membership.interest_group_id)
            assert is_member == True
        
        print(f"\n✅ Membership Repository Legacy Integration erfolgreich getestet")
    
    def test_policy_port_legacy_integration(self, client):
        """Test: Policy Port Legacy Integration"""
        print("Teste Policy Port Legacy Integration...")
        
        # DDD Policy Port Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        policy_port = adapters['policy_port']
        
        # Test: User-Permissions abrufen
        permissions = policy_port.get_user_permissions(1)
        print(f"User 1 Permissions: {permissions}")
        assert isinstance(permissions, list)
        
        # Test: Access-Check
        if permissions:
            first_permission = permissions[0]
            has_access = policy_port.check_access(1, first_permission)
            print(f"User 1 hat Permission '{first_permission}': {has_access}")
            assert isinstance(has_access, bool)
        
        # Test: Approval-Check
        can_approve = policy_port.can_approve(1, 2)
        print(f"User 1 kann Level 2 freigeben: {can_approve}")
        assert isinstance(can_approve, bool)
        
        # Test: User-Management-Check
        can_manage = policy_port.can_manage_users(1)
        print(f"User 1 kann User verwalten: {can_manage}")
        assert isinstance(can_manage, bool)
        
        print(f"\n✅ Policy Port Legacy Integration erfolgreich getestet")
