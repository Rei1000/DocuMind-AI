"""
Approval Integration Smoke Tests
Testet Happy-Path für mehrstufige Freigabe (nur Smoke/Parität)
"""

import pytest
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from tests.helpers.payloads_accesscontrol import document_status_change_payload


class TestApprovalIntegrationSmoke:
    """Testet Approval-Integration und Workflow-Smoke-Tests"""
    
    def test_document_status_workflow_parity(self, client):
        """Test: Document Status Workflow - Legacy vs DDD Parität"""
        print("Teste Document Status Workflow Parität...")
        
        # 1. Dokument-Status ändern (DRAFT → REVIEWED)
        status_data = document_status_change_payload("REVIEWED", "Test Review")
        
        # Legacy-Status-Change
        legacy_status = run_request(
            client, "legacy", "PUT", "/api/documents/1/status", json_data=status_data
        )
        
        # DDD-Status-Change
        ddd_status = run_request(
            client, "ddd", "PUT", "/api/documents/1/status", json_data=status_data
        )
        
        # Vergleich
        status_comparison = compare_responses(legacy_status, ddd_status)
        print(f"Document Status Change: {format_comparison_result(status_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert status_comparison["status_equal"], f"Status-Change-Status unterscheidet sich: {status_comparison['status_diff']}"
        
        print(f"\n✅ Document Status Workflow Parität erfolgreich getestet")
    
    def test_document_workflow_info_parity(self, client):
        """Test: Document Workflow Info - Legacy vs DDD Parität"""
        print("Teste Document Workflow Info Parität...")
        
        # 1. Workflow-Info abrufen
        # Legacy-Workflow-Info
        legacy_workflow = run_request(
            client, "legacy", "GET", "/api/documents/1/workflow"
        )
        
        # DDD-Workflow-Info
        ddd_workflow = run_request(
            client, "ddd", "GET", "/api/documents/1/workflow"
        )
        
        # Vergleich
        workflow_comparison = compare_responses(legacy_workflow, ddd_workflow)
        print(f"Document Workflow Info: {format_comparison_result(workflow_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert workflow_comparison["status_equal"], f"Workflow-Info-Status unterscheidet sich: {workflow_comparison['status_diff']}"
        
        print(f"\n✅ Document Workflow Info Parität erfolgreich getestet")
    
    def test_qm_approval_workflow_parity(self, client):
        """Test: QM Approval Workflow - Legacy vs DDD Parität"""
        print("Teste QM Approval Workflow Parität...")
        
        # 1. QM-Approval (REVIEWED → APPROVED)
        approval_data = document_status_change_payload("APPROVED", "QM Approval")
        
        # Legacy-QM-Approval
        legacy_approval = run_request(
            client, "legacy", "PUT", "/api/documents/1/status", json_data=approval_data
        )
        
        # DDD-QM-Approval
        ddd_approval = run_request(
            client, "ddd", "PUT", "/api/documents/1/status", json_data=approval_data
        )
        
        # Vergleich
        approval_comparison = compare_responses(legacy_approval, ddd_approval)
        print(f"QM Approval: {format_comparison_result(approval_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert approval_comparison["status_equal"], f"QM-Approval-Status unterscheidet sich: {approval_comparison['status_diff']}"
        
        print(f"\n✅ QM Approval Workflow Parität erfolgreich getestet")
    
    def test_obsolete_workflow_parity(self, client):
        """Test: Obsolete Workflow - Legacy vs DDD Parität"""
        print("Teste Obsolete Workflow Parität...")
        
        # 1. Dokument obsolet setzen (APPROVED → OBSOLETE)
        obsolete_data = document_status_change_payload("OBSOLETE", "Document obsolete")
        
        # Legacy-Obsolete
        legacy_obsolete = run_request(
            client, "legacy", "PUT", "/api/documents/1/status", json_data=obsolete_data
        )
        
        # DDD-Obsolete
        ddd_obsolete = run_request(
            client, "ddd", "PUT", "/api/documents/1/status", json_data=obsolete_data
        )
        
        # Vergleich
        obsolete_comparison = compare_responses(legacy_obsolete, ddd_obsolete)
        print(f"Obsolete Workflow: {format_comparison_result(obsolete_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert obsolete_comparison["status_equal"], f"Obsolete-Status unterscheidet sich: {obsolete_comparison['status_diff']}"
        
        print(f"\n✅ Obsolete Workflow Parität erfolgreich getestet")
    
    def test_reactivation_workflow_parity(self, client):
        """Test: Reactivation Workflow - Legacy vs DDD Parität"""
        print("Teste Reactivation Workflow Parität...")
        
        # 1. Dokument reaktivieren (OBSOLETE → DRAFT)
        reactivation_data = document_status_change_payload("DRAFT", "Document reactivated")
        
        # Legacy-Reactivation
        legacy_reactivation = run_request(
            client, "legacy", "PUT", "/api/documents/1/status", json_data=reactivation_data
        )
        
        # DDD-Reactivation
        ddd_reactivation = run_request(
            client, "ddd", "PUT", "/api/documents/1/status", json_data=reactivation_data
        )
        
        # Vergleich
        reactivation_comparison = compare_responses(legacy_reactivation, ddd_reactivation)
        print(f"Reactivation Workflow: {format_comparison_result(reactivation_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert reactivation_comparison["status_equal"], f"Reactivation-Status unterscheidet sich: {reactivation_comparison['status_diff']}"
        
        print(f"\n✅ Reactivation Workflow Parität erfolgreich getestet")
    
    def test_invalid_status_transition_parity(self, client):
        """Test: Invalid Status Transition - Legacy vs DDD Parität"""
        print("Teste Invalid Status Transition Parität...")
        
        # 1. Ungültige Status-Änderung (DRAFT → APPROVED, ohne REVIEWED)
        invalid_data = document_status_change_payload("APPROVED", "Invalid transition")
        
        # Legacy-Invalid-Transition
        legacy_invalid = run_request(
            client, "legacy", "PUT", "/api/documents/1/status", json_data=invalid_data
        )
        
        # DDD-Invalid-Transition
        ddd_invalid = run_request(
            client, "ddd", "PUT", "/api/documents/1/status", json_data=invalid_data
        )
        
        # Vergleich
        invalid_comparison = compare_responses(legacy_invalid, ddd_invalid)
        print(f"Invalid Status Transition: {format_comparison_result(invalid_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert invalid_comparison["status_equal"], f"Invalid-Transition-Status unterscheidet sich: {invalid_comparison['status_diff']}"
        
        print(f"\n✅ Invalid Status Transition Parität erfolgreich getestet")
    
    def test_workflow_approval_chain_parity(self, client):
        """Test: Workflow Approval Chain - Legacy vs DDD Parität"""
        print("Teste Workflow Approval Chain Parität...")
        
        # 1. Approval Chain abrufen
        # Legacy-Approval-Chain
        legacy_chain = run_request(
            client, "legacy", "GET", "/api/documents/1/workflow"
        )
        
        # DDD-Approval-Chain
        ddd_chain = run_request(
            client, "ddd", "GET", "/api/documents/1/workflow"
        )
        
        # Vergleich
        chain_comparison = compare_responses(legacy_chain, ddd_chain)
        print(f"Approval Chain: {format_comparison_result(chain_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert chain_comparison["status_equal"], f"Approval-Chain-Status unterscheidet sich: {chain_comparison['status_diff']}"
        
        print(f"\n✅ Workflow Approval Chain Parität erfolgreich getestet")
    
    def test_workflow_requirements_check_parity(self, client):
        """Test: Workflow Requirements Check - Legacy vs DDD Parität"""
        print("Teste Workflow Requirements Check Parität...")
        
        # 1. Workflow Requirements abrufen
        # Legacy-Requirements
        legacy_requirements = run_request(
            client, "legacy", "GET", "/api/documents/1/workflow"
        )
        
        # DDD-Requirements
        ddd_requirements = run_request(
            client, "ddd", "GET", "/api/documents/1/workflow"
        )
        
        # Vergleich
        requirements_comparison = compare_responses(legacy_requirements, ddd_requirements)
        print(f"Workflow Requirements: {format_comparison_result(requirements_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert requirements_comparison["status_equal"], f"Requirements-Status unterscheidet sich: {requirements_comparison['status_diff']}"
        
        print(f"\n✅ Workflow Requirements Check Parität erfolgreich getestet")

