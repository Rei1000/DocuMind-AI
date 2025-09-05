"""
Audit Smoke Use Case Tests
Testet AuditPort-Fake und verifiziert Audit-Einträge
"""

import pytest
import os
from io import StringIO
import sys
from contextlib import redirect_stdout
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from contexts.accesscontrol.infrastructure.adapters import AdapterFactory
from contexts.accesscontrol.application.use_cases import AssignRoleUseCase, RevokeRoleUseCase, CheckAccessUseCase


class TestAuditSmokeUseCase:
    """Testet Audit Use Cases"""
    
    def test_assign_role_audit_logging(self, client):
        """Test: Assign Role Audit Logging"""
        print("Teste Assign Role Audit Logging...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        assign_role_uc = AssignRoleUseCase(
            user_repo=adapters['user_repo'],
            role_repo=adapters['role_repo'],
            assignment_repo=adapters['assignment_repo'],
            audit_port=adapters['audit_port']
        )
        
        # Capture stdout für Audit-Logs
        captured_output = StringIO()
        
        try:
            with redirect_stdout(captured_output):
                # DDD Use Case ausführen
                ddd_assignment = assign_role_uc.execute(
                    user_id=1,
                    role_name="dev_lead",
                    assigned_by=1
                )
            
            # Prüfe Audit-Log
            output = captured_output.getvalue()
            print(f"Audit Output: {output}")
            
            # Audit-Log sollte enthalten:
            # - role_assignment event
            assert "role_assignment" in output, "Audit log should contain role_assignment event"
            assert "user=1" in output, "Audit log should contain user ID"
            assert "role=dev_lead" in output, "Audit log should contain role name"
            assert "assigned_by=1" in output, "Audit log should contain assigned_by"
            
            ddd_success = True
            ddd_error = None
        except Exception as e:
            ddd_success = False
            ddd_error = str(e)
        
        # Legacy: Kein direkter Audit-Check möglich, aber Operation sollte funktionieren
        try:
            # Simuliere Legacy-Operation
            legacy_response = run_request(
                client, "legacy", "GET", "/api/users/1"
            )
            legacy_success = legacy_response[0] == 200
            legacy_error = None
        except Exception as e:
            legacy_success = False
            legacy_error = str(e)
        
        # Vergleich
        print(f"DDD Audit: success={ddd_success}, error={ddd_error}")
        print(f"Legacy: success={legacy_success}, error={legacy_error}")
        
        # DDD sollte erfolgreich sein und Audit-Log haben
        assert ddd_success, f"DDD should succeed: {ddd_error}"
        assert legacy_success, f"Legacy should succeed: {legacy_error}"
        
        print(f"\n✅ Assign Role Audit Logging erfolgreich getestet")
    
    def test_revoke_role_audit_logging(self, client):
        """Test: Revoke Role Audit Logging"""
        print("Teste Revoke Role Audit Logging...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        revoke_role_uc = RevokeRoleUseCase(
            user_repo=adapters['user_repo'],
            role_repo=adapters['role_repo'],
            assignment_repo=adapters['assignment_repo'],
            audit_port=adapters['audit_port']
        )
        
        # Capture stdout für Audit-Logs
        captured_output = StringIO()
        
        try:
            with redirect_stdout(captured_output):
                # DDD Use Case ausführen
                ddd_success = revoke_role_uc.execute(
                    user_id=1,
                    role_name="dev_lead",
                    revoked_by=1
                )
            
            # Prüfe Audit-Log
            output = captured_output.getvalue()
            print(f"Audit Output: {output}")
            
            # Audit-Log sollte enthalten:
            # - role_revoked event
            assert "role_revoked" in output, "Audit log should contain role_revoked event"
            assert "user=1" in output, "Audit log should contain user ID"
            assert "role_name=dev_lead" in output, "Audit log should contain role name"
            assert "revoked_by=1" in output, "Audit log should contain revoked_by"
            
            ddd_error = None
        except Exception as e:
            ddd_success = False
            ddd_error = str(e)
        
        # Legacy: Kein direkter Audit-Check möglich
        try:
            legacy_response = run_request(
                client, "legacy", "GET", "/api/users/1"
            )
            legacy_success = legacy_response[0] == 200
            legacy_error = None
        except Exception as e:
            legacy_success = False
            legacy_error = str(e)
        
        # Vergleich
        print(f"DDD Audit: success={ddd_success}, error={ddd_error}")
        print(f"Legacy: success={legacy_success}, error={legacy_error}")
        
        # DDD sollte erfolgreich sein und Audit-Log haben
        assert ddd_success, f"DDD should succeed: {ddd_error}"
        assert legacy_success, f"Legacy should succeed: {legacy_error}"
        
        print(f"\n✅ Revoke Role Audit Logging erfolgreich getestet")
    
    def test_check_access_audit_logging(self, client):
        """Test: Check Access Audit Logging"""
        print("Teste Check Access Audit Logging...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        check_access_uc = CheckAccessUseCase(
            user_repo=adapters['user_repo'],
            permission_repo=adapters['permission_repo'],
            policy_port=adapters['policy_port'],
            audit_port=adapters['audit_port']
        )
        
        # Capture stdout für Audit-Logs
        captured_output = StringIO()
        
        try:
            with redirect_stdout(captured_output):
                # DDD Use Case ausführen
                ddd_has_access = check_access_uc.execute(1, "system_administration")
            
            # Prüfe Audit-Log
            output = captured_output.getvalue()
            print(f"Audit Output: {output}")
            
            # Audit-Log sollte enthalten:
            # - access_check event
            assert "access_check" in output, "Audit log should contain access_check event"
            assert "user=1" in output, "Audit log should contain user ID"
            assert "permission=system_administration" in output, "Audit log should contain permission"
            assert "granted=" in output, "Audit log should contain granted status"
            
            ddd_success = True
            ddd_error = None
        except Exception as e:
            ddd_success = False
            ddd_error = str(e)
        
        # Legacy: Kein direkter Audit-Check möglich
        try:
            legacy_response = run_request(
                client, "legacy", "GET", "/api/users/1"
            )
            legacy_success = legacy_response[0] == 200
            legacy_error = None
        except Exception as e:
            legacy_success = False
            legacy_error = str(e)
        
        # Vergleich
        print(f"DDD Audit: success={ddd_success}, error={ddd_error}")
        print(f"Legacy: success={legacy_success}, error={legacy_error}")
        
        # DDD sollte erfolgreich sein und Audit-Log haben
        assert ddd_success, f"DDD should succeed: {ddd_error}"
        assert legacy_success, f"Legacy should succeed: {legacy_error}"
        
        print(f"\n✅ Check Access Audit Logging erfolgreich getestet")
    
    def test_multiple_audit_events(self, client):
        """Test: Multiple Audit Events"""
        print("Teste Multiple Audit Events...")
        
        # DDD Use Case Setup
        database_url = os.environ.get("DATABASE_URL", "sqlite:///.tmp/test_qms_mvp.db")
        adapters = AdapterFactory.create_adapters(database_url)
        
        assign_role_uc = AssignRoleUseCase(
            user_repo=adapters['user_repo'],
            role_repo=adapters['role_repo'],
            assignment_repo=adapters['assignment_repo'],
            audit_port=adapters['audit_port']
        )
        
        check_access_uc = CheckAccessUseCase(
            user_repo=adapters['user_repo'],
            permission_repo=adapters['permission_repo'],
            policy_port=adapters['policy_port'],
            audit_port=adapters['audit_port']
        )
        
        # Capture stdout für Audit-Logs
        captured_output = StringIO()
        
        try:
            with redirect_stdout(captured_output):
                # Multiple Use Cases ausführen
                assign_role_uc.execute(user_id=1, role_name="dev_lead", assigned_by=1)
                check_access_uc.execute(1, "design_approval")
                check_access_uc.execute(1, "system_administration")
            
            # Prüfe Audit-Log
            output = captured_output.getvalue()
            print(f"Audit Output: {output}")
            
            # Audit-Log sollte mehrere Events enthalten:
            assert output.count("role_assignment") >= 1, "Should have at least one role_assignment event"
            assert output.count("access_check") >= 2, "Should have at least two access_check events"
            
            ddd_success = True
            ddd_error = None
        except Exception as e:
            ddd_success = False
            ddd_error = str(e)
        
        # Legacy: Kein direkter Audit-Check möglich
        try:
            legacy_response = run_request(
                client, "legacy", "GET", "/api/users/1"
            )
            legacy_success = legacy_response[0] == 200
            legacy_error = None
        except Exception as e:
            legacy_success = False
            legacy_error = str(e)
        
        # Vergleich
        print(f"DDD Multiple Audit: success={ddd_success}, error={ddd_error}")
        print(f"Legacy: success={legacy_success}, error={legacy_error}")
        
        # DDD sollte erfolgreich sein und mehrere Audit-Logs haben
        assert ddd_success, f"DDD should succeed: {ddd_error}"
        assert legacy_success, f"Legacy should succeed: {legacy_error}"
        
        print(f"\n✅ Multiple Audit Events erfolgreich getestet")
