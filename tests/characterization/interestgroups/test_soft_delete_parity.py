"""
Soft-Delete-Parität: Legacy vs. DDD
Vergleicht Soft-Delete-Verhalten zwischen beiden Modi
"""

import pytest
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result


class TestSoftDeleteParity:
    """Testet Soft-Delete-Parität zwischen Legacy und DDD"""
    
    def test_soft_delete_behavior_parity(self, client):
        """Test: Soft-Delete-Verhalten ist identisch zwischen Legacy und DDD"""
        # 1. Gruppe erstellen
        create_data = {
            "name": "Soft Delete Parity Test",
            "code": "soft_delete_parity_test",
            "description": "Test für Soft-Delete-Parität"
        }
        
        create_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        assert create_response[0] == 200, f"Gruppe konnte nicht erstellt werden: {create_response[0]}"
        
        created_group = create_response[1]
        group_id = created_group["id"]
        
        print(f"Gruppe erstellt: ID={group_id}, Name='{created_group['name']}'")
        
        # 2. Gruppe löschen (Soft-Delete)
        print(f"\nLösche Gruppe {group_id}...")
        
        # Legacy-Delete
        legacy_delete_response = run_request(
            client, "legacy", "DELETE", f"/api/interest-groups/{group_id}"
        )
        
        # DDD-Delete
        ddd_delete_response = run_request(
            client, "ddd", "DELETE", f"/api/interest-groups/{group_id}"
        )
        
        # Delete-Responses vergleichen
        delete_comparison = compare_responses(legacy_delete_response, ddd_delete_response)
        print(f"DELETE Response: {format_comparison_result(delete_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert delete_comparison["status_equal"], f"Delete-Status unterscheidet sich: {delete_comparison['status_diff']}"
        
        # 3. Gruppe nach Delete abrufen (sollte 404 oder is_active=false)
        print(f"\nPrüfe Gruppe {group_id} nach Delete...")
        
        # Legacy-Get nach Delete
        legacy_get_after_delete = run_request(
            client, "legacy", "GET", f"/api/interest-groups/{group_id}"
        )
        
        # DDD-Get nach Delete
        ddd_get_after_delete = run_request(
            client, "ddd", "GET", f"/api/interest-groups/{group_id}"
        )
        
        # Get-Responses nach Delete vergleichen
        get_after_delete_comparison = compare_responses(legacy_get_after_delete, ddd_get_after_delete)
        print(f"GET nach DELETE: {format_comparison_result(get_after_delete_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert get_after_delete_comparison["status_equal"], f"Get-nach-Delete-Status unterscheidet sich: {get_after_delete_comparison['status_diff']}"
        
        # 4. Gruppe in Liste prüfen (sollte nicht mehr angezeigt werden)
        print(f"\nPrüfe Gruppe {group_id} in Liste...")
        
        # Legacy-Liste
        legacy_list_response = run_request(
            client, "legacy", "GET", "/api/interest-groups"
        )
        
        # DDD-Liste
        ddd_list_response = run_request(
            client, "ddd", "GET", "/api/interest-groups"
        )
        
        # Listen-Responses vergleichen
        list_comparison = compare_responses(legacy_list_response, ddd_list_response)
        print(f"Liste nach DELETE: {format_comparison_result(list_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert list_comparison["status_equal"], f"Listen-Status unterscheidet sich: {list_comparison['status_diff']}"
        
        # 5. Prüfen, ob gelöschte Gruppe in beiden Listen fehlt
        legacy_groups = legacy_list_response[1] if isinstance(legacy_list_response[1], list) else []
        ddd_groups = ddd_list_response[1] if isinstance(ddd_list_response[1], list) else []
        
        # IDs der gelöschten Gruppe in beiden Listen suchen
        legacy_contains_deleted = any(group.get("id") == group_id for group in legacy_groups)
        ddd_contains_deleted = any(group.get("id") == group_id for group in ddd_groups)
        
        print(f"Legacy-Liste enthält gelöschte Gruppe: {legacy_contains_deleted}")
        print(f"DDD-Liste enthält gelöschte Gruppe: {ddd_contains_deleted}")
        
        # Beide Listen müssen identisch sein (gleiche Gruppen enthalten/ausschließen)
        assert legacy_contains_deleted == ddd_contains_deleted, \
            f"Listen unterscheiden sich: Legacy={legacy_contains_deleted}, DDD={ddd_contains_deleted}"
        
        # 6. Soft-Delete-Flag prüfen (falls vorhanden)
        if legacy_get_after_delete[0] == 200:
            # Gruppe existiert noch, aber ist deaktiviert
            legacy_group = legacy_get_after_delete[1]
            ddd_group = ddd_get_after_delete[1]
            
            print(f"Gruppe existiert noch, prüfe is_active Flag...")
            
            # is_active sollte in beiden Modi identisch sein
            legacy_is_active = legacy_group.get("is_active", True)
            ddd_is_active = ddd_group.get("is_active", True)
            
            print(f"Legacy is_active: {legacy_is_active}")
            print(f"DDD is_active: {ddd_is_active}")
            
            assert legacy_is_active == ddd_is_active, \
                f"is_active unterscheidet sich: Legacy={legacy_is_active}, DDD={ddd_is_active}"
            
            # is_active sollte false sein (gelöscht)
            assert not legacy_is_active, f"Legacy: is_active sollte false sein, ist aber {legacy_is_active}"
            assert not ddd_is_active, f"DDD: is_active sollte false sein, ist aber {ddd_is_active}"
        
        print(f"\n✅ Soft-Delete-Parität erfolgreich getestet")
    
    def test_multiple_soft_deletes_parity(self, client):
        """Test: Mehrere Soft-Deletes sind identisch zwischen Legacy und DDD"""
        # Mehrere Gruppen erstellen
        groups_to_delete = []
        
        for i in range(3):
            create_data = {
                "name": f"Multi Delete Test {i+1}",
                "code": f"multi_delete_test_{i+1}",
                "description": f"Testgruppe {i+1} für Multi-Delete-Parität"
            }
            
            create_response = run_request(
                client, "legacy", "POST", "/api/interest-groups", json_data=create_data
            )
            assert create_response[0] == 200, f"Gruppe {i+1} konnte nicht erstellt werden"
            
            groups_to_delete.append(create_response[1]["id"])
        
        print(f"Gruppen erstellt: {groups_to_delete}")
        
        # Alle Gruppen löschen
        for group_id in groups_to_delete:
            print(f"Lösche Gruppe {group_id}...")
            
            # Legacy-Delete
            legacy_delete = run_request(
                client, "legacy", "DELETE", f"/api/interest-groups/{group_id}"
            )
            
            # DDD-Delete
            ddd_delete = run_request(
                client, "ddd", "DELETE", f"/api/interest-groups/{group_id}"
            )
            
            # Vergleich
            comparison = compare_responses(legacy_delete, ddd_delete)
            assert comparison["status_equal"], f"Delete-Status unterscheidet sich für Gruppe {group_id}"
            
            print(f"  Gruppe {group_id}: {format_comparison_result(comparison)}")
        
        # Liste nach allen Deletes prüfen
        print(f"\nPrüfe Liste nach allen Deletes...")
        
        legacy_list = run_request(client, "legacy", "GET", "/api/interest-groups")
        ddd_list = run_request(client, "ddd", "GET", "/api/interest-groups")
        
        list_comparison = compare_responses(legacy_list, ddd_list)
        print(f"Liste nach allen Deletes: {format_comparison_result(list_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert list_comparison["status_equal"], f"Listen-Status unterscheidet sich: {list_comparison['status_diff']}"
        
        # Keine der gelöschten Gruppen sollte in der Liste sein
        legacy_groups = legacy_list[1] if isinstance(legacy_list[1], list) else []
        ddd_groups = ddd_list[1] if isinstance(ddd_list[1], list) else []
        
        for group_id in groups_to_delete:
            legacy_contains = any(group.get("id") == group_id for group in legacy_groups)
            ddd_contains = any(group.get("id") == group_id for group in ddd_groups)
            
            # Beide Listen müssen identisch sein
            assert legacy_contains == ddd_contains, \
                f"Gruppe {group_id}: Legacy={legacy_contains}, DDD={ddd_contains}"
            
            print(f"  Gruppe {group_id}: Legacy={legacy_contains}, DDD={ddd_contains}")
        
        print(f"\n✅ Multi-Delete-Parität erfolgreich getestet")
    
    def test_soft_delete_nonexistent_parity(self, client):
        """Test: Soft-Delete nicht-existenter Gruppen ist identisch zwischen Legacy und DDD"""
        non_existent_id = 99999
        
        print(f"Teste Soft-Delete nicht-existenter Gruppe {non_existent_id}...")
        
        # Legacy-Delete
        legacy_delete = run_request(
            client, "legacy", "DELETE", f"/api/interest-groups/{non_existent_id}"
        )
        
        # DDD-Delete
        ddd_delete = run_request(
            client, "ddd", "DELETE", f"/api/interest-groups/{non_existent_id}"
        )
        
        # Vergleich
        comparison = compare_responses(legacy_delete, ddd_delete)
        print(f"Delete nicht-existente Gruppe: {format_comparison_result(comparison)}")
        
        # Statuscodes müssen identisch sein
        assert comparison["status_equal"], f"Delete-Status unterscheidet sich: {comparison['status_diff']}"
        
        # Body sollte auch identisch sein
        assert comparison["body_equal"], f"Delete-Body unterscheidet sich: {comparison['body_diff']}"
        
        print(f"\n✅ Soft-Delete nicht-existenter Gruppen erfolgreich getestet")
