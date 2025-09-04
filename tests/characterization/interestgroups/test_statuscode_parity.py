"""
Statuscode-Parität: Legacy vs. DDD
Vergleicht Statuscodes zwischen beiden Modi für Edge-Cases
"""

import pytest
import time
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from tests.helpers.payloads import unique_ig_payload


class TestStatuscodeParity:
    """Testet Statuscode-Parität zwischen Legacy und DDD für Edge-Cases"""
    
    def test_missing_required_fields_parity(self, client):
        """Test: Fehlende Pflichtfelder - Legacy vs. DDD"""
        print("Teste fehlende Pflichtfelder...")
        
        # Test ohne name (Pflichtfeld)
        invalid_data_no_name = {
            "code": "test_no_name",
            "description": "Test ohne Name"
        }
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=invalid_data_no_name
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=invalid_data_no_name
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        print(f"Fehlendes name-Feld: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        
        # Test ohne code (Pflichtfeld)
        invalid_data_no_code = {
            "name": "Test ohne Code",
            "description": "Test ohne Code"
        }
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=invalid_data_no_code
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=invalid_data_no_code
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        print(f"Fehlendes code-Feld: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        
        print(f"\n✅ Fehlende Pflichtfelder erfolgreich getestet")
    
    def test_duplicate_constraints_parity(self, client):
        """Test: Duplicate-Constraints - Legacy vs. DDD"""
        print("Teste Duplicate-Constraints...")
        
        # Erst eine Gruppe erstellen (mit eindeutigen Daten)
        create_data = unique_ig_payload("duplicate_test", "Duplicate Test Group", None)
        create_data["description"] = "Test für Duplicate-Constraints"
        
        create_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        assert create_response[0] == 200, f"Gruppe konnte nicht erstellt werden: {create_response[0]}"
        
        # Versuche, eine Gruppe mit gleichem Namen zu erstellen (aber anderem Code)
        duplicate_name_data = {
            "name": create_data["name"],  # Gleicher Name wie erstellt
            "code": f"different_code_{int(time.time() * 1000)}",  # Anderer Code
            "description": "Andere Beschreibung"
        }
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=duplicate_name_data
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=duplicate_name_data
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        print(f"Duplicate name: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein - beide sollten 200 zurückgeben (Legacy-Kompatibilität)
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        assert legacy_response[0] == 200, f"Legacy sollte 200 zurückgeben, aber gab {legacy_response[0]} zurück"
        assert ddd_response[0] == 200, f"DDD sollte 200 zurückgeben, aber gab {ddd_response[0]} zurück"
        
        # Versuche, eine Gruppe mit gleichem Code zu erstellen
        duplicate_code_data = {
            "name": "Different Name",
            "code": "duplicate_test_code",  # Gleicher Code
            "description": "Andere Beschreibung"
        }
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=duplicate_code_data
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=duplicate_code_data
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        print(f"Duplicate code: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein - beide sollten 200 zurückgeben (Legacy-Kompatibilität)
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        assert legacy_response[0] == 200, f"Legacy sollte 200 zurückgeben, aber gab {legacy_response[0]} zurück"
        assert ddd_response[0] == 200, f"DDD sollte 200 zurückgeben, aber gab {ddd_response[0]} zurück"
        
        print(f"\n✅ Duplicate-Constraints erfolgreich getestet")
    
    def test_invalid_id_parity(self, client):
        """Test: Ungültige IDs - Legacy vs. DDD"""
        print("Teste ungültige IDs...")
        
        # Test mit nicht existierender ID
        non_existent_id = 99999
        
        # GET nicht existierende Gruppe
        legacy_get = run_request(
            client, "legacy", "GET", f"/api/interest-groups/{non_existent_id}"
        )
        
        ddd_get = run_request(
            client, "ddd", "GET", f"/api/interest-groups/{non_existent_id}"
        )
        
        # Vergleich
        comparison = compare_responses(legacy_get, ddd_get)
        print(f"GET nicht existierende ID: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        
        # PUT nicht existierende Gruppe
        update_data = {
            "name": "Updated Name",
            "description": "Updated Description"
        }
        
        legacy_put = run_request(
            client, "legacy", "PUT", f"/api/interest-groups/{non_existent_id}", json_data=update_data
        )
        
        ddd_put = run_request(
            client, "ddd", "PUT", f"/api/interest-groups/{non_existent_id}", json_data=update_data
        )
        
        # Vergleich
        comparison = compare_responses(legacy_put, ddd_put)
        print(f"PUT nicht existierende ID: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        
        # DELETE nicht existierende Gruppe
        legacy_delete = run_request(
            client, "legacy", "DELETE", f"/api/interest-groups/{non_existent_id}"
        )
        
        ddd_delete = run_request(
            client, "ddd", "DELETE", f"/api/interest-groups/{non_existent_id}"
        )
        
        # Vergleich
        comparison = compare_responses(legacy_delete, ddd_delete)
        print(f"DELETE nicht existierende ID: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        
        print(f"\n✅ Ungültige IDs erfolgreich getestet")
    
    def test_invalid_content_type_parity(self, client):
        """Test: Ungültiger Content-Type - Legacy vs. DDD"""
        print("Teste ungültigen Content-Type...")
        
        # Test mit form-data statt JSON
        form_data = {
            "name": "Form Data Test",
            "code": "form_data_test",
            "description": "Test mit form-data"
        }
        
        # Legacy-Request mit form-data
        legacy_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", 
            json_data=None,  # Kein JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # DDD-Request mit form-data
        ddd_response = run_request(
            client, "ddd", "POST", "/api/interest-groups", 
            json_data=None,  # Kein JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        print(f"Form-data Content-Type: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        
        # Test ohne Content-Type Header (mit eindeutigen Daten)
        no_content_type_data = unique_ig_payload("no_content_type", "No Content Type", None)
        legacy_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", 
            json_data=no_content_type_data
        )
        
        ddd_response = run_request(
            client, "ddd", "POST", "/api/interest-groups", 
            json_data=no_content_type_data
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        print(f"Kein Content-Type Header: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        
        print(f"\n✅ Ungültiger Content-Type erfolgreich getestet")
    
    def test_validation_rules_parity(self, client):
        """Test: Validierungsregeln - Legacy vs. DDD"""
        print("Teste Validierungsregeln...")
        
        # Test mit zu kurzem Namen (min 2 Zeichen)
        short_name_data = {
            "name": "A",  # Zu kurz
            "code": "short_name_test"
        }
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=short_name_data
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=short_name_data
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        print(f"Zu kurzer Name: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        
        # Test mit zu langem Namen (max 100 Zeichen)
        long_name_data = {
            "name": "A" * 101,  # Zu lang
            "code": "long_name_test"
        }
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=long_name_data
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=long_name_data
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        print(f"Zu langer Name: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        
        # Test mit ungültigem Code-Format (sollte snake_case sein)
        invalid_code_data = {
            "name": "Invalid Code Test",
            "code": "InvalidCode"  # Ungültiges Format
        }
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=invalid_code_data
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=invalid_code_data
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        print(f"Ungültiger Code: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        
        print(f"\n✅ Validierungsregeln erfolgreich getestet")
    
    def test_edge_cases_parity(self, client):
        """Test: Edge-Cases - Legacy vs. DDD"""
        print("Teste Edge-Cases...")
        
        # Test mit leeren Strings
        empty_strings_data = {
            "name": "",  # Leerer String
            "code": "",  # Leerer String
            "description": ""  # Leerer String
        }
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=empty_strings_data
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=empty_strings_data
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        print(f"Leere Strings: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        
        # Test mit None-Werten (mit eindeutigen Daten)
        none_values_data = unique_ig_payload("none_values_test", "None Values Test", None)
        none_values_data.update({
            "description": None,  # None-Wert
            "group_permissions": None,  # None-Wert
            "ai_functionality": None,  # None-Wert
            "typical_tasks": None  # None-Wert
        })
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=none_values_data
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=none_values_data
        )
        
        # Vergleich
        comparison = compare_responses(legacy_response, ddd_response)
        print(f"None-Werte: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein
        assert comparison["status_equal"], f"Status unterscheidet sich: {comparison['status_diff']}"
        
        print(f"\n✅ Edge-Cases erfolgreich getestet")
