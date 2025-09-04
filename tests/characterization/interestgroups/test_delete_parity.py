"""
DELETE-Paritätstests für Interest Groups
Vergleicht Legacy vs. DDD DELETE-Verhalten
"""

import pytest
from tests.helpers.ab_runner import run_request, compare_responses


class TestDeleteParity:
    """Test für DELETE-Parität zwischen Legacy und DDD"""
    
    def test_delete_interest_group_parity(self, client):
        """Test: DELETE-Verhalten ist identisch zwischen Legacy und DDD"""
        # Test-Daten
        create_data = {
            "name": "Delete Parity Test Group",
            "code": "delete_parity_test",
            "description": "Test für DELETE-Parität"
        }
        
        print("Teste DELETE-Parität...")
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # Vergleich der Create-Responses
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"Create-Parität: {create_comparison['equal']}")
        
        # Extrahiere IDs für DELETE
        legacy_group_id = legacy_create[1]["id"] if legacy_create[0] == 200 else None
        ddd_group_id = ddd_create[1]["id"] if ddd_create[0] == 200 else None
        
        if legacy_group_id and ddd_group_id:
            # Legacy-Delete
            legacy_delete = run_request(
                client, "legacy", "DELETE", f"/api/interest-groups/{legacy_group_id}"
            )
            
            # DDD-Delete
            ddd_delete = run_request(
                client, "ddd", "DELETE", f"/api/interest-groups/{ddd_group_id}"
            )
            
            # Vergleich der Delete-Responses
            delete_comparison = compare_responses(legacy_delete, ddd_delete)
            print(f"Delete-Parität: {delete_comparison['equal']}")
            
            # Statuscodes müssen identisch sein
            assert delete_comparison["status_equal"], f"Delete-Status unterscheidet sich: {delete_comparison['status_diff']}"
            
            # Response-Bodies sollten ähnlich sein (message und success)
            if delete_comparison["body_equal"]:
                print("✅ DELETE-Response-Bodies sind identisch")
            else:
                print(f"⚠️ DELETE-Response-Bodies unterscheiden sich: {delete_comparison['body_diff']}")
            
            # Test: Gelöschte Gruppen sollten nicht mehr abrufbar sein
            legacy_get = run_request(
                client, "legacy", "GET", f"/api/interest-groups/{legacy_group_id}"
            )
            
            ddd_get = run_request(
                client, "ddd", "GET", f"/api/interest-groups/{ddd_group_id}"
            )
            
            # GET nach DELETE sollte 404 zurückgeben
            assert legacy_get[0] == 404, f"Legacy GET nach DELETE sollte 404 sein, ist {legacy_get[0]}"
            assert ddd_get[0] == 404, f"DDD GET nach DELETE sollte 404 sein, ist {ddd_get[0]}"
            
            print(f"GET nach DELETE - Legacy: {legacy_get[0]}, DDD: {ddd_get[0]}")
            
        else:
            pytest.skip("Gruppen konnten nicht erstellt werden")
    
    def test_delete_nonexistent_group_parity(self, client):
        """Test: DELETE nicht existierender Gruppe - Legacy vs. DDD"""
        non_existent_id = 99999
        
        print("Teste DELETE nicht existierender Gruppe...")
        
        # Legacy-Delete
        legacy_delete = run_request(
            client, "legacy", "DELETE", f"/api/interest-groups/{non_existent_id}"
        )
        
        # DDD-Delete
        ddd_delete = run_request(
            client, "ddd", "DELETE", f"/api/interest-groups/{non_existent_id}"
        )
        
        # Vergleich
        delete_comparison = compare_responses(legacy_delete, ddd_delete)
        print(f"Delete nicht existierender Gruppe: {delete_comparison['equal']}")
        
        # Beide sollten 404 zurückgeben
        assert delete_comparison["status_equal"], f"Status unterscheidet sich: {delete_comparison['status_diff']}"
        assert legacy_delete[0] == 404, f"Legacy sollte 404 sein, ist {legacy_delete[0]}"
        assert ddd_delete[0] == 404, f"DDD sollte 404 sein, ist {ddd_delete[0]}"
        
        print(f"Delete nicht existierender Gruppe - Legacy: {legacy_delete[0]}, DDD: {ddd_delete[0]}")
    
    def test_delete_response_structure_parity(self, client):
        """Test: DELETE-Response-Struktur ist identisch zwischen Legacy und DDD"""
        # Test-Daten
        create_data = {
            "name": "Response Structure Parity Test",
            "code": "response_structure_parity",
            "description": "Test für Response-Struktur-Parität"
        }
        
        print("Teste DELETE-Response-Struktur-Parität...")
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # Extrahiere IDs
        legacy_group_id = legacy_create[1]["id"] if legacy_create[0] == 200 else None
        ddd_group_id = ddd_create[1]["id"] if ddd_create[0] == 200 else None
        
        if legacy_group_id and ddd_group_id:
            # Legacy-Delete
            legacy_delete = run_request(
                client, "legacy", "DELETE", f"/api/interest-groups/{legacy_group_id}"
            )
            
            # DDD-Delete
            ddd_delete = run_request(
                client, "ddd", "DELETE", f"/api/interest-groups/{ddd_group_id}"
            )
            
            # Prüfe Response-Struktur
            if legacy_delete[0] == 200 and ddd_delete[0] == 200:
                legacy_body = legacy_delete[1]
                ddd_body = ddd_delete[1]
                
                # Beide sollten message und success haben
                assert "message" in legacy_body, "Legacy Response sollte 'message' haben"
                assert "message" in ddd_body, "DDD Response sollte 'message' haben"
                
                # Message sollte den Gruppennamen enthalten
                assert "Response Structure Parity Test" in legacy_body["message"], "Legacy message sollte Gruppennamen enthalten"
                assert "Response Structure Parity Test" in ddd_body["message"], "DDD message sollte Gruppennamen enthalten"
                
                print(f"✅ Response-Struktur-Parität: Legacy='{legacy_body['message']}', DDD='{ddd_body['message']}'")
            else:
                print(f"⚠️ DELETE fehlgeschlagen - Legacy: {legacy_delete[0]}, DDD: {ddd_delete[0]}")
        else:
            pytest.skip("Gruppen konnten nicht erstellt werden")
