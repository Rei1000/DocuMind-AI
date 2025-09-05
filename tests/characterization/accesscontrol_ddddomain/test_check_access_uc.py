"""
Check Access Use Case Tests
Vergleicht CheckAccess (Legacy Endpoint vs. DDD UC)
"""

import pytest
import os
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from contexts.accesscontrol.infrastructure.adapters import AdapterFactory
from contexts.accesscontrol.application.use_cases import CheckAccessUseCase, GetUserPermissionsUseCase


class TestCheckAccessUseCase:
    """Testet Check Access Use Cases"""
    
    def test_check_access_use_case_vs_legacy(self, client):
        """Test: Check Access Use Case vs Legacy Endpoint"""
        print("Teste Check Access Use Case vs Legacy...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        check_access_uc = CheckAccessUseCase(
            user_repo=adapters['user_repo'],
            permission_repo=adapters['permission_repo'],
            policy_port=adapters['policy_port'],
            audit_port=adapters['audit_port']
        )
        
        # Test: Access-Check für verschiedene Permissions
        test_permissions = [
            "system_administration",
            "user_management", 
            "audit_management",
            "final_approval",
            "design_approval"
        ]
        
        for permission in test_permissions:
            print(f"\nTeste Permission: {permission}")
            
            # DDD Use Case
            try:
                ddd_has_access = check_access_uc.execute(1, permission)
                ddd_error = None
            except Exception as e:
                ddd_has_access = False
                ddd_error = str(e)
            
            # Legacy Endpoint (über User-Info-Endpoint ableiten)
            try:
                # User-Info abrufen und Permissions prüfen
                legacy_response = run_request(
                    client, "legacy", "GET", "/api/auth/me"
                )
                
                if legacy_response[0] == 200:
                    user_info = legacy_response[1]
                    legacy_permissions = user_info.get('permissions', [])
                    legacy_has_access = permission in legacy_permissions
                    legacy_error = None
                else:
                    legacy_has_access = False
                    legacy_error = f"HTTP {legacy_response[0]}"
            except Exception as e:
                legacy_has_access = False
                legacy_error = str(e)
            
            # Vergleich
            print(f"  DDD Use Case: {ddd_has_access} (error: {ddd_error})")
            print(f"  Legacy Endpoint: {legacy_has_access} (error: {legacy_error})")
            
            # Beide sollten das gleiche Ergebnis haben
            assert ddd_has_access == legacy_has_access, \
                f"Access mismatch for '{permission}': DDD={ddd_has_access}, Legacy={legacy_has_access}"
        
        print(f"\n✅ Check Access Use Case vs Legacy erfolgreich getestet")
    
    def test_get_user_permissions_use_case_vs_legacy(self, client):
        """Test: Get User Permissions Use Case vs Legacy Endpoint"""
        print("Teste Get User Permissions Use Case vs Legacy...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        get_permissions_uc = GetUserPermissionsUseCase(
            user_repo=adapters['user_repo'],
            permission_repo=adapters['permission_repo'],
            policy_port=adapters['policy_port']
        )
        
        # Test: User-Permissions abrufen
        try:
            # DDD Use Case
            ddd_permissions = get_permissions_uc.execute(1)
            ddd_error = None
        except Exception as e:
            ddd_permissions = []
            ddd_error = str(e)
        
        # Legacy Endpoint
        try:
            legacy_response = run_request(
                client, "legacy", "GET", "/api/auth/me"
            )
            
            if legacy_response[0] == 200:
                user_info = legacy_response[1]
                legacy_permissions = user_info.get('permissions', [])
                legacy_error = None
            else:
                legacy_permissions = []
                legacy_error = f"HTTP {legacy_response[0]}"
        except Exception as e:
            legacy_permissions = []
            legacy_error = str(e)
        
        # Vergleich
        print(f"DDD Use Case: {len(ddd_permissions)} permissions (error: {ddd_error})")
        print(f"Legacy Endpoint: {len(legacy_permissions)} permissions (error: {legacy_error})")
        
        # Permissions sollten identisch sein
        ddd_permissions_set = set(ddd_permissions)
        legacy_permissions_set = set(legacy_permissions)
        
        assert ddd_permissions_set == legacy_permissions_set, \
            f"Permissions mismatch: DDD={ddd_permissions_set}, Legacy={legacy_permissions_set}"
        
        print(f"\n✅ Get User Permissions Use Case vs Legacy erfolgreich getestet")
    
    def test_access_check_with_different_users(self, client):
        """Test: Access Check mit verschiedenen Usern"""
        print("Teste Access Check mit verschiedenen Usern...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        check_access_uc = CheckAccessUseCase(
            user_repo=adapters['user_repo'],
            permission_repo=adapters['permission_repo'],
            policy_port=adapters['policy_port'],
            audit_port=adapters['audit_port']
        )
        
        # Test verschiedene User-IDs
        test_users = [1, 2, 3, 4, 5]
        test_permission = "system_administration"
        
        for user_id in test_users:
            print(f"\nTeste User {user_id}:")
            
            # DDD Use Case
            try:
                ddd_has_access = check_access_uc.execute(user_id, test_permission)
                ddd_error = None
            except Exception as e:
                ddd_has_access = False
                ddd_error = str(e)
            
            # Legacy: User-Info abrufen
            try:
                # Simuliere Login für User (falls möglich)
                legacy_response = run_request(
                    client, "legacy", "GET", f"/api/users/{user_id}"
                )
                
                if legacy_response[0] == 200:
                    user_data = legacy_response[1]
                    user_permissions = user_data.get('permissions', [])
                    legacy_has_access = test_permission in user_permissions
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
        
        print(f"\n✅ Access Check mit verschiedenen Usern erfolgreich getestet")
    
    def test_access_check_with_invalid_user(self, client):
        """Test: Access Check mit ungültigem User"""
        print("Teste Access Check mit ungültigem User...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        check_access_uc = CheckAccessUseCase(
            user_repo=adapters['user_repo'],
            permission_repo=adapters['permission_repo'],
            policy_port=adapters['policy_port'],
            audit_port=adapters['audit_port']
        )
        
        # Test: Ungültiger User (ID 99999)
        invalid_user_id = 99999
        test_permission = "system_administration"
        
        # DDD Use Case
        try:
            ddd_has_access = check_access_uc.execute(invalid_user_id, test_permission)
            ddd_error = None
        except Exception as e:
            ddd_has_access = False
            ddd_error = str(e)
        
        # Legacy: User-Info abrufen
        try:
            legacy_response = run_request(
                client, "legacy", "GET", f"/api/users/{invalid_user_id}"
            )
            
            if legacy_response[0] == 200:
                user_data = legacy_response[1]
                user_permissions = user_data.get('permissions', [])
                legacy_has_access = test_permission in user_permissions
                legacy_error = None
            else:
                legacy_has_access = False
                legacy_error = f"HTTP {legacy_response[0]}"
        except Exception as e:
            legacy_has_access = False
            legacy_error = str(e)
        
        # Vergleich
        print(f"DDD: {ddd_has_access} (error: {ddd_error})")
        print(f"Legacy: {legacy_has_access} (error: {legacy_error})")
        
        # Beide sollten False zurückgeben (User nicht gefunden)
        assert ddd_has_access == False, "DDD should return False for invalid user"
        assert legacy_has_access == False, "Legacy should return False for invalid user"
        
        print(f"\n✅ Access Check mit ungültigem User erfolgreich getestet")
    
    def test_access_check_with_invalid_permission(self, client):
        """Test: Access Check mit ungültiger Permission"""
        print("Teste Access Check mit ungültiger Permission...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        check_access_uc = CheckAccessUseCase(
            user_repo=adapters['user_repo'],
            permission_repo=adapters['permission_repo'],
            policy_port=adapters['policy_port'],
            audit_port=adapters['audit_port']
        )
        
        # Test: Ungültige Permission
        valid_user_id = 1
        invalid_permission = "invalid_permission_xyz"
        
        # DDD Use Case
        try:
            ddd_has_access = check_access_uc.execute(valid_user_id, invalid_permission)
            ddd_error = None
        except Exception as e:
            ddd_has_access = False
            ddd_error = str(e)
        
        # Legacy: User-Info abrufen
        try:
            legacy_response = run_request(
                client, "legacy", "GET", "/api/auth/me"
            )
            
            if legacy_response[0] == 200:
                user_info = legacy_response[1]
                user_permissions = user_info.get('permissions', [])
                legacy_has_access = invalid_permission in user_permissions
                legacy_error = None
            else:
                legacy_has_access = False
                legacy_error = f"HTTP {legacy_response[0]}"
        except Exception as e:
            legacy_has_access = False
            legacy_error = str(e)
        
        # Vergleich
        print(f"DDD: {ddd_has_access} (error: {ddd_error})")
        print(f"Legacy: {legacy_has_access} (error: {legacy_error})")
        
        # Beide sollten False zurückgeben (Permission nicht vorhanden)
        assert ddd_has_access == False, "DDD should return False for invalid permission"
        assert legacy_has_access == False, "Legacy should return False for invalid permission"
        
        print(f"\n✅ Access Check mit ungültiger Permission erfolgreich getestet")
