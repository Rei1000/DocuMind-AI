"""
Permission-Parsing-Parität: Legacy vs. DDD
Vergleicht Permission-Parsing zwischen beiden Modi
"""

import pytest
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result


class TestPermissionParity:
    """Testet Permission-Parsing-Parität zwischen Legacy und DDD"""
    
    def test_empty_permissions_parity(self, client):
        """Test: Leere Permissions werden identisch behandelt"""
        create_data = {
            "name": "Empty Permissions Test",
            "code": "empty_permissions_test",
            "description": "Test für leere Permissions",
            "group_permissions": []  # Leere Liste
        }
        
        print("Teste leere Permissions...")
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # Vergleich
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"Create mit leeren Permissions: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Create-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        # Body sollte auch identisch sein
        assert create_comparison["body_equal"], f"Create-Body unterscheidet sich: {create_comparison['body_diff']}"
        
        # Gruppe abrufen und Permissions prüfen
        if legacy_create[0] == 200:
            group_id = legacy_create[1]["id"]
            
            # Legacy-Get
            legacy_get = run_request(
                client, "legacy", "GET", f"/api/interest-groups/{group_id}"
            )
            
            # DDD-Get
            ddd_get = run_request(
                client, "ddd", "GET", f"/api/interest-groups/{group_id}"
            )
            
            # Get-Responses vergleichen
            get_comparison = compare_responses(legacy_get, ddd_get)
            print(f"GET mit leeren Permissions: {format_comparison_result(get_comparison)}")
            
            # Statuscodes müssen identisch sein
            assert get_comparison["status_equal"], f"Get-Status unterscheidet sich: {get_comparison['status_diff']}"
            
            # Body sollte auch identisch sein
            assert get_comparison["body_equal"], f"Get-Body unterscheidet sich: {get_comparison['body_diff']}"
            
            # Permissions in beiden Responses prüfen
            legacy_permissions = legacy_get[1].get("group_permissions", [])
            ddd_permissions = ddd_get[1].get("group_permissions", [])
            
            print(f"Legacy Permissions: {legacy_permissions} (Typ: {type(legacy_permissions)})")
            print(f"DDD Permissions: {ddd_permissions} (Typ: {type(ddd_permissions)})")
            
            # Permissions müssen identisch sein
            assert legacy_permissions == ddd_permissions, \
                f"Permissions unterscheiden sich: Legacy={legacy_permissions}, DDD={ddd_permissions}"
        
        print(f"\n✅ Leere Permissions erfolgreich getestet")
    
    def test_simple_permissions_parity(self, client):
        """Test: Einfache Permissions werden identisch behandelt"""
        create_data = {
            "name": "Simple Permissions Test",
            "code": "simple_permissions_test",
            "description": "Test für einfache Permissions",
            "group_permissions": ["VIEW", "EDIT"]  # Einfache Liste
        }
        
        print("Teste einfache Permissions...")
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # Vergleich
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"Create mit einfachen Permissions: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Create-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        # Body sollte auch identisch sein
        assert create_comparison["body_equal"], f"Create-Body unterscheidet sich: {create_comparison['body_diff']}"
        
        # Gruppe abrufen und Permissions prüfen
        if legacy_create[0] == 200:
            group_id = legacy_create[1]["id"]
            
            # Legacy-Get
            legacy_get = run_request(
                client, "legacy", "GET", f"/api/interest-groups/{group_id}"
            )
            
            # DDD-Get
            ddd_get = run_request(
                client, "ddd", "GET", f"/api/interest-groups/{group_id}"
            )
            
            # Get-Responses vergleichen
            get_comparison = compare_responses(legacy_get, ddd_get)
            print(f"GET mit einfachen Permissions: {format_comparison_result(get_comparison)}")
            
            # Statuscodes müssen identisch sein
            assert get_comparison["status_equal"], f"Get-Status unterscheidet sich: {get_comparison['status_diff']}"
            
            # Body sollte auch identisch sein
            assert get_comparison["body_equal"], f"Get-Body unterscheidet sich: {get_comparison['body_diff']}"
            
            # Permissions in beiden Responses prüfen
            legacy_permissions = legacy_get[1].get("group_permissions", [])
            ddd_permissions = ddd_get[1].get("group_permissions", [])
            
            print(f"Legacy Permissions: {legacy_permissions} (Typ: {type(legacy_permissions)})")
            print(f"DDD Permissions: {ddd_permissions} (Typ: {type(ddd_permissions)})")
            
            # Permissions müssen identisch sein
            assert legacy_permissions == ddd_permissions, \
                f"Permissions unterscheiden sich: Legacy={legacy_permissions}, DDD={ddd_permissions}"
        
        print(f"\n✅ Einfache Permissions erfolgreich getestet")
    
    def test_complex_permissions_parity(self, client):
        """Test: Komplexe Permissions werden identisch behandelt"""
        create_data = {
            "name": "Complex Permissions Test",
            "code": "complex_permissions_test",
            "description": "Test für komplexe Permissions",
            "group_permissions": ["VIEW", "EDIT", "DELETE", "APPROVE", "ADMIN"]  # Komplexe Liste
        }
        
        print("Teste komplexe Permissions...")
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # Vergleich
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"Create mit komplexen Permissions: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Create-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        # Body sollte auch identisch sein
        assert create_comparison["body_equal"], f"Create-Body unterscheidet sich: {create_comparison['body_diff']}"
        
        # Gruppe abrufen und Permissions prüfen
        if legacy_create[0] == 200:
            group_id = legacy_create[1]["id"]
            
            # Legacy-Get
            legacy_get = run_request(
                client, "legacy", "GET", f"/api/interest-groups/{group_id}"
            )
            
            # DDD-Get
            ddd_get = run_request(
                client, "ddd", "GET", f"/api/interest-groups/{group_id}"
            )
            
            # Get-Responses vergleichen
            get_comparison = compare_responses(legacy_get, ddd_get)
            print(f"GET mit komplexen Permissions: {format_comparison_result(get_comparison)}")
            
            # Statuscodes müssen identisch sein
            assert get_comparison["status_equal"], f"Get-Status unterscheidet sich: {get_comparison['status_diff']}"
            
            # Body sollte auch identisch sein
            assert get_comparison["body_equal"], f"Get-Body unterscheidet sich: {get_comparison['body_diff']}"
            
            # Permissions in beiden Responses prüfen
            legacy_permissions = legacy_get[1].get("group_permissions", [])
            ddd_permissions = ddd_get[1].get("group_permissions", [])
            
            print(f"Legacy Permissions: {legacy_permissions} (Typ: {type(legacy_permissions)})")
            print(f"DDD Permissions: {ddd_permissions} (Typ: {type(ddd_permissions)})")
            
            # Permissions müssen identisch sein
            assert legacy_permissions == ddd_permissions, \
                f"Permissions unterscheiden sich: Legacy={legacy_permissions}, DDD={ddd_permissions}"
        
        print(f"\n✅ Komplexe Permissions erfolgreich getestet")
    
    def test_json_string_permissions_parity(self, client):
        """Test: JSON-String Permissions werden identisch behandelt"""
        # JSON-String als group_permissions
        json_permissions = '["VIEW", "EDIT", "DELETE"]'
        
        create_data = {
            "name": "JSON String Permissions Test",
            "code": "json_string_permissions_test",
            "description": "Test für JSON-String Permissions",
            "group_permissions": json_permissions
        }
        
        print(f"Teste JSON-String Permissions: {json_permissions}")
        
        # Legacy-Create
        legacy_create = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # DDD-Create
        ddd_create = run_request(
            client, "ddd", "POST", "/api/interest-groups", json_data=create_data
        )
        
        # Vergleich
        create_comparison = compare_responses(legacy_create, ddd_create)
        print(f"Create mit JSON-String Permissions: {format_comparison_result(create_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert create_comparison["status_equal"], f"Create-Status unterscheidet sich: {create_comparison['status_diff']}"
        
        # Body sollte auch identisch sein
        assert create_comparison["body_equal"], f"Create-Body unterscheidet sich: {create_comparison['body_diff']}"
        
        # Gruppe abrufen und Permissions prüfen
        if legacy_create[0] == 200:
            group_id = legacy_create[1]["id"]
            
            # Legacy-Get
            legacy_get = run_request(
                client, "legacy", "GET", f"/api/interest-groups/{group_id}"
            )
            
            # DDD-Get
            ddd_get = run_request(
                client, "ddd", "GET", f"/api/interest-groups/{group_id}"
            )
            
            # Get-Responses vergleichen
            get_comparison = compare_responses(legacy_get, ddd_get)
            print(f"GET mit JSON-String Permissions: {format_comparison_result(get_comparison)}")
            
            # Statuscodes müssen identisch sein
            assert get_comparison["status_equal"], f"Get-Status unterscheidet sich: {get_comparison['status_diff']}"
            
            # Body sollte auch identisch sein
            assert get_comparison["body_equal"], f"Get-Body unterscheidet sich: {get_comparison['body_diff']}"
            
            # Permissions in beiden Responses prüfen
            legacy_permissions = legacy_get[1].get("group_permissions", [])
            ddd_permissions = ddd_get[1].get("group_permissions", [])
            
            print(f"Legacy Permissions: {legacy_permissions} (Typ: {type(legacy_permissions)})")
            print(f"DDD Permissions: {ddd_permissions} (Typ: {type(ddd_permissions)})")
            
            # Permissions müssen identisch sein
            assert legacy_permissions == ddd_permissions, \
                f"Permissions unterscheiden sich: Legacy={legacy_permissions}, DDD={ddd_permissions}"
        
        print(f"\n✅ JSON-String Permissions erfolgreich getestet")
    
    def test_permission_update_parity(self, client):
        """Test: Permission-Updates werden identisch behandelt"""
        # Erst Gruppe mit einfachen Permissions erstellen
        create_data = {
            "name": "Permission Update Test",
            "code": "permission_update_test",
            "description": "Test für Permission-Updates",
            "group_permissions": ["VIEW"]
        }
        
        create_response = run_request(
            client, "legacy", "POST", "/api/interest-groups", json_data=create_data
        )
        assert create_response[0] == 200, f"Gruppe konnte nicht erstellt werden: {create_response[0]}"
        
        created_group = create_response[1]
        group_id = created_group["id"]
        
        print(f"Gruppe erstellt: ID={group_id}")
        
        # Permissions aktualisieren
        update_data = {
            "group_permissions": ["VIEW", "EDIT", "DELETE"]
        }
        
        print(f"Update Permissions: {update_data['group_permissions']}")
        
        # Legacy-Update
        legacy_update = run_request(
            client, "legacy", "PUT", f"/api/interest-groups/{group_id}", json_data=update_data
        )
        
        # DDD-Update
        ddd_update = run_request(
            client, "ddd", "PUT", f"/api/interest-groups/{group_id}", json_data=update_data
        )
        
        # Update-Responses vergleichen
        update_comparison = compare_responses(legacy_update, ddd_update)
        print(f"Update Permissions: {format_comparison_result(update_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert update_comparison["status_equal"], f"Update-Status unterscheidet sich: {update_comparison['status_diff']}"
        
        # Body sollte auch identisch sein
        assert update_comparison["body_equal"], f"Update-Body unterscheidet sich: {update_comparison['body_diff']}"
        
        # Aktualisierte Gruppe abrufen
        legacy_get = run_request(
            client, "legacy", "GET", f"/api/interest-groups/{group_id}"
        )
        
        ddd_get = run_request(
            client, "ddd", "GET", f"/api/interest-groups/{group_id}"
        )
        
        # Get-Responses nach Update vergleichen
        get_comparison = compare_responses(legacy_get, ddd_get)
        print(f"GET nach Update: {format_comparison_result(get_comparison)}")
        
        # Statuscodes müssen identisch sein
        assert get_comparison["status_equal"], f"Get-Status unterscheidet sich: {get_comparison['status_diff']}"
        
        # Body sollte auch identisch sein
        assert get_comparison["body_equal"], f"Get-Body unterscheidet sich: {get_comparison['body_diff']}"
        
        # Aktualisierte Permissions prüfen
        legacy_permissions = legacy_get[1].get("group_permissions", [])
        ddd_permissions = ddd_get[1].get("group_permissions", [])
        
        print(f"Legacy aktualisierte Permissions: {legacy_permissions}")
        print(f"DDD aktualisierte Permissions: {ddd_permissions}")
        
        # Permissions müssen identisch sein
        assert legacy_permissions == ddd_permissions, \
            f"Aktualisierte Permissions unterscheiden sich: Legacy={legacy_permissions}, DDD={ddd_permissions}"
        
        print(f"\n✅ Permission-Updates erfolgreich getestet")
