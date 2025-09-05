"""
Membership Integration Use Case Tests
Testet AddMembershipUseCase und CheckAccess abhängig von Gruppen
"""

import pytest
import os
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from contexts.accesscontrol.infrastructure.adapters import AdapterFactory
from contexts.accesscontrol.application.use_cases import AddMembershipUseCase, CheckAccessUseCase


class TestMembershipIntegrationUseCase:
    """Testet Membership Integration Use Cases"""
    
    def test_add_membership_use_case_vs_legacy(self, client):
        """Test: Add Membership Use Case vs Legacy Endpoint"""
        print("Teste Add Membership Use Case vs Legacy...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        add_membership_uc = AddMembershipUseCase(
            user_repo=adapters['user_repo'],
            membership_repo=adapters['membership_repo'],
            audit_port=adapters['audit_port']
        )
        
        # Test: Membership hinzufügen (User 1 → Group 2)
        try:
            # DDD Use Case
            ddd_membership = add_membership_uc.execute(
                user_id=1,
                group_id=2,
                role_in_group="Test Member",
                approval_level=2,
                assigned_by=1
            )
            ddd_success = True
            ddd_error = None
        except Exception as e:
            ddd_success = False
            ddd_error = str(e)
        
        # Legacy Endpoint
        try:
            legacy_response = run_request(
                client, "legacy", "POST", "/api/memberships",
                json_data={
                    "user_id": 1,
                    "interest_group_id": 2,
                    "role_in_group": "Test Member",
                    "approval_level": 2,
                    "assigned_by_id": 1
                }
            )
            legacy_success = legacy_response[0] == 200
            legacy_error = None
        except Exception as e:
            legacy_success = False
            legacy_error = str(e)
        
        # Vergleich
        print(f"DDD Use Case: success={ddd_success}, error={ddd_error}")
        print(f"Legacy Endpoint: success={legacy_success}, error={legacy_error}")
        
        # Beide sollten erfolgreich sein
        assert ddd_success == legacy_success, f"Success mismatch: DDD={ddd_success}, Legacy={legacy_success}"
        
        print(f"\n✅ Add Membership Use Case vs Legacy erfolgreich getestet")
    
    def test_membership_access_check_integration(self, client):
        """Test: Membership-basierter Access Check"""
        print("Teste Membership-basierter Access Check...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        check_access_uc = CheckAccessUseCase(
            user_repo=adapters['user_repo'],
            permission_repo=adapters['permission_repo'],
            policy_port=adapters['policy_port'],
            audit_port=adapters['audit_port']
        )
        
        # Test: Access-Check für verschiedene User mit verschiedenen Memberships
        test_cases = [
            (1, "system_administration"),  # Admin User
            (2, "final_approval"),         # QM Manager
            (3, "design_approval"),        # Dev Lead
            (4, "audit_read"),            # External Auditor
        ]
        
        for user_id, permission in test_cases:
            print(f"\nTeste User {user_id} mit Permission '{permission}':")
            
            # DDD Use Case
            try:
                ddd_has_access = check_access_uc.execute(user_id, permission)
                ddd_error = None
            except Exception as e:
                ddd_has_access = False
                ddd_error = str(e)
            
            # Legacy: User-Info abrufen
            try:
                legacy_response = run_request(
                    client, "legacy", "GET", f"/api/users/{user_id}"
                )
                
                if legacy_response[0] == 200:
                    user_data = legacy_response[1]
                    user_permissions = user_data.get('permissions', [])
                    legacy_has_access = permission in user_permissions
                    legacy_error = None
                else:
                    legacy_has_access = False
                    legacy_error = f"HTTP {legacy_response[0]}"
            except Exception as e:
                legacy_has_access = False
                legacy_error = str(e)
            
            # Vergleich
            print(f"  DDD: {ddd_has_access} (error: {ddd_error})")
            print(f"  Legacy: {legacy_has_access} (error: {legacy_error})")
            
            # Beide sollten das gleiche Ergebnis haben
            assert ddd_has_access == legacy_has_access, \
                f"Access mismatch for User {user_id}: DDD={ddd_has_access}, Legacy={legacy_has_access}"
        
        print(f"\n✅ Membership-basierter Access Check erfolgreich getestet")
    
    def test_group_permission_inheritance(self, client):
        """Test: Group Permission Inheritance"""
        print("Teste Group Permission Inheritance...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        check_access_uc = CheckAccessUseCase(
            user_repo=adapters['user_repo'],
            permission_repo=adapters['permission_repo'],
            policy_port=adapters['policy_port'],
            audit_port=adapters['audit_port']
        )
        
        # Test: User mit Group-Membership sollte Group-Permissions haben
        # User 1 ist in Quality Management Group (Group 1)
        try:
            # DDD: Prüfe Group-Permissions
            ddd_has_group_access = check_access_uc.execute(1, "final_approval")
            ddd_error = None
        except Exception as e:
            ddd_has_group_access = False
            ddd_error = str(e)
        
        # Legacy: Prüfe über User-Info
        try:
            legacy_response = run_request(
                client, "legacy", "GET", "/api/users/1"
            )
            
            if legacy_response[0] == 200:
                user_data = legacy_response[1]
                user_permissions = user_data.get('permissions', [])
                legacy_has_group_access = "final_approval" in user_permissions
                legacy_error = None
            else:
                legacy_has_group_access = False
                legacy_error = f"HTTP {legacy_response[0]}"
        except Exception as e:
            legacy_has_group_access = False
            legacy_error = str(e)
        
        # Vergleich
        print(f"DDD Group Access: {ddd_has_group_access} (error: {ddd_error})")
        print(f"Legacy Group Access: {legacy_has_group_access} (error: {legacy_error})")
        
        # Beide sollten das gleiche Ergebnis haben
        assert ddd_has_group_access == legacy_has_group_access, \
            f"Group access mismatch: DDD={ddd_has_group_access}, Legacy={legacy_has_group_access}"
        
        print(f"\n✅ Group Permission Inheritance erfolgreich getestet")
    
    def test_membership_duplicate_handling(self, client):
        """Test: Duplicate Membership Handling"""
        print("Teste Duplicate Membership Handling...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        add_membership_uc = AddMembershipUseCase(
            user_repo=adapters['user_repo'],
            membership_repo=adapters['membership_repo'],
            audit_port=adapters['audit_port']
        )
        
        # Test: Duplicate Membership (User 1 → Group 1, bereits vorhanden)
        try:
            # DDD Use Case
            ddd_membership = add_membership_uc.execute(
                user_id=1,
                group_id=1,  # Bereits vorhanden
                role_in_group="Duplicate Member",
                approval_level=1
            )
            ddd_success = True
            ddd_error = None
        except Exception as e:
            ddd_success = False
            ddd_error = str(e)
        
        # Legacy Endpoint
        try:
            legacy_response = run_request(
                client, "legacy", "POST", "/api/memberships",
                json_data={
                    "user_id": 1,
                    "interest_group_id": 1,  # Bereits vorhanden
                    "role_in_group": "Duplicate Member",
                    "approval_level": 1
                }
            )
            legacy_success = legacy_response[0] == 200
            legacy_error = None
        except Exception as e:
            legacy_success = False
            legacy_error = str(e)
        
        # Vergleich
        print(f"DDD Duplicate: success={ddd_success}, error={ddd_error}")
        print(f"Legacy Duplicate: success={legacy_success}, error={legacy_error}")
        
        # Beide sollten das gleiche Verhalten haben
        assert ddd_success == legacy_success, f"Duplicate handling mismatch: DDD={ddd_success}, Legacy={legacy_success}"
        
        print(f"\n✅ Duplicate Membership Handling erfolgreich getestet")
