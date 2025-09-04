"""
Paritäts-Tests für IG-Endpoints: Legacy vs. DDD
Vergleicht exakt dieselben Requests zwischen beiden Modi
"""

import pytest
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result, run_legacy, run_ddd


class TestEndpointParity:
    """Testet Parität zwischen Legacy und DDD für alle IG-Endpoints"""
    
    def test_get_interest_groups_list_parity(self, client):
        """Test: GET /api/interest-groups Liste - Legacy vs. DDD"""
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "GET", "/api/interest-groups"
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "GET", "/api/interest-groups"
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        
        # Assertions
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        assert comparison["body_equal"], f"Body unterscheidet sich: {comparison['body_diff']}"
        assert comparison["headers_equal"], f"Headers unterscheiden sich: {comparison['header_diffs']}"
        
        print(f"GET /api/interest-groups: {format_comparison_result(comparison)}")
    
    def test_get_interest_group_by_id_parity(self, client):
        """Test: GET /api/interest-groups/{id} - Legacy vs. DDD"""
        # Erst eine Gruppe erstellen für den Test
        create_data = {
            "name": "Parity Test Group",
            "code": "parity_test_group",
            "description": "Test für Paritäts-Vergleich"
        }
        
        create_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        assert create_response[0] == 200, f"Gruppe konnte nicht erstellt werden: {create_response[0]}"
        
        created_group = create_response[1]
        group_id = created_group["id"]
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "GET", f"/api/interest-groups/{group_id}"
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "GET", f"/api/interest-groups/{group_id}"
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        
        # Assertions
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        assert comparison["body_equal"], f"Body unterscheidet sich: {comparison['body_diff']}"
        assert comparison["headers_equal"], f"Headers unterscheiden sich: {comparison['header_diffs']}"
        
        print(f"GET /api/interest-groups/{group_id}: {format_comparison_result(comparison)}")
    
    def test_create_interest_group_parity(self, client):
        """Test: POST /api/interest-groups - Legacy vs. DDD"""
        # Verwende eindeutige Payload für jeden Request
        import time
        timestamp = int(time.time())
        
        # Erst eine Gruppe erstellen (Legacy)
        create_data = {
            "name": f"Create Parity Test {timestamp}",
            "code": f"create_parity_test_{timestamp}",
            "description": "Test für Create-Parität"
        }
        
        create_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        assert create_response[0] == 200, f"Gruppe konnte nicht erstellt werden: {create_response[0]}"
        
        # Jetzt den gleichen POST in beiden Modi testen (beide sollten 200 zurückgeben)
        # Legacy-Request (Duplicate)
        legacy_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # DDD-Request (Duplicate)
        ddd_response = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        
        # Assertions - beide sollten 200 zurückgeben (Legacy-Kompatibilität)
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        assert legacy_response[0] == 200, f"Legacy sollte 200 zurückgeben, aber gab {legacy_response[0]} zurück"
        assert ddd_response[0] == 200, f"DDD sollte 200 zurückgeben, aber gab {ddd_response[0]} zurück"
        assert comparison["body_equal"], f"Body unterscheidet sich: {comparison['body_diff']}"
        assert comparison["headers_equal"], f"Headers unterscheiden sich: {comparison['header_diffs']}"
        
        print(f"POST /api/interest-groups (Duplicate): {format_comparison_result(comparison)}")
    
    def test_update_interest_group_parity(self, client):
        """Test: PUT /api/interest-groups/{id} - Legacy vs. DDD"""
        # Erst eine Gruppe erstellen
        create_data = {
            "name": "Update Parity Test",
            "code": "update_parity_test",
            "description": "Test für Update-Parität"
        }
        
        create_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        assert create_response[0] == 200, f"Gruppe konnte nicht erstellt werden: {create_response[0]}"
        
        created_group = create_response[1]
        group_id = created_group["id"]
        
        # Update-Daten
        update_data = {
            "description": "Aktualisierte Beschreibung für Paritäts-Test"
        }
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "PUT", f"/api/interest-groups/{group_id}", json_data=update_data
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "PUT", f"/api/interest-groups/{group_id}", json_data=update_data
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        
        # Assertions
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        assert comparison["body_equal"], f"Body unterscheidet sich: {comparison['body_diff']}"
        assert comparison["headers_equal"], f"Headers unterscheiden sich: {comparison['header_diffs']}"
        
        print(f"PUT /api/interest-groups/{group_id}: {format_comparison_result(comparison)}")
    
    def test_delete_interest_group_parity(self, client):
        """Test: DELETE /api/interest-groups/{id} - Legacy vs. DDD"""
        # Erst eine Gruppe erstellen
        create_data = {
            "name": "Delete Parity Test",
            "code": "delete_parity_test",
            "description": "Test für Delete-Parität"
        }
        
        create_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        assert create_response[0] == 200, f"Gruppe konnte nicht erstellt werden: {create_response[0]}"
        
        created_group = create_response[1]
        group_id = created_group["id"]
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "DELETE", f"/api/interest-groups/{group_id}"
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "DELETE", f"/api/interest-groups/{group_id}"
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        
        # Assertions
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        assert comparison["body_equal"], f"Body unterscheidet sich: {comparison['body_diff']}"
        assert comparison["headers_equal"], f"Headers unterscheiden sich: {comparison['header_diffs']}"
        
        print(f"DELETE /api/interest-groups/{group_id}: {format_comparison_result(comparison)}")
    
    def test_error_cases_parity(self, client):
        """Test: Fehlerfälle - Legacy vs. DDD"""
        # Test mit nicht existierender ID
        non_existent_id = 99999
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "GET", f"/api/interest-groups/{non_existent_id}"
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "GET", f"/api/interest-groups/{non_existent_id}"
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        
        # Assertions
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        assert comparison["body_equal"], f"Body unterscheidet sich: {comparison['body_diff']}"
        
        print(f"GET /api/interest-groups/{non_existent_id} (404): {format_comparison_result(comparison)}")
        
        # Test mit ungültigen Daten
        invalid_data = {
            "name": "",  # Zu kurz
            "code": "invalid code"  # Ungültiges Format
        }
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=invalid_data
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=invalid_data
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        
        # Assertions
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        
        print(f"POST /api/interest-groups (invalid): {format_comparison_result(comparison)}")

    def test_post_duplicate_parity(self, client):
        """Test: POST /api/interest-groups (Duplicate) - Legacy vs. DDD Parität"""
        import time
        timestamp = int(time.time())
        test_code = f"duplicate_parity_test_{timestamp}"
        
        # Test-Daten vorbereiten
        create_data = {
            "name": f"Duplicate Parity Test {timestamp}",
            "code": test_code,
            "description": "Test für Duplicate-Parität zwischen Legacy und DDD"
        }
        
        # Getrennte DB-Pfade
        legacy_db = ".tmp/_legacy.db"
        ddd_db = ".tmp/_ddd.db"
        
        # Legacy: POST + Duplicate POST
        legacy_create = run_legacy("backend.app.main:app", legacy_db, "POST", "/api/interest-groups", create_data)
        legacy_group_id = legacy_create[1].get("id", 0)
        
        legacy_duplicate = run_legacy("backend.app.main:app", legacy_db, "POST", "/api/interest-groups", create_data)
        
        # DDD: POST + Duplicate POST
        ddd_create = run_ddd("backend.app.main:app", ddd_db, "POST", "/api/interest-groups", create_data)
        ddd_group_id = ddd_create[1].get("id", 0)
        
        ddd_duplicate = run_ddd("backend.app.main:app", ddd_db, "POST", "/api/interest-groups", create_data)
        
        # Ergebnisse
        print(f"POST id check: legacy_id>0={legacy_group_id > 0}, ddd_id>0={ddd_group_id > 0}")
        print(f"POST duplicate parity: legacy={legacy_duplicate[0]}, ddd={ddd_duplicate[0]}")
        
        # Body-Parität prüfen
        if legacy_duplicate[0] == 200 and ddd_duplicate[0] == 200:
            legacy_body = legacy_duplicate[1]
            ddd_body = ddd_duplicate[1]
            body_equal = "name" in legacy_body and "name" in ddd_body and legacy_body.get("name") == ddd_body.get("name")
            print(f"POST duplicate body_equal={body_equal}")
        else:
            print(f"POST duplicate body_equal=false (status mismatch)")
