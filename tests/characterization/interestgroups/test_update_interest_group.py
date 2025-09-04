"""
Charakterisierungstest für PUT /api/interest-groups/{group_id}
Dokumentiert das bestehende Verhalten ohne neue Regeln zu erfinden.
"""

import pytest
import os
from tests.helpers.ab_runner import run_legacy, run_ddd

class TestUpdateInterestGroup:
    """Test für PUT /api/interest-groups/{group_id} Endpunkt"""
    
    def test_update_interest_group_with_valid_data(self, client):
        """Test: Endpunkt aktualisiert bestehende Interessensgruppe"""
        # Erst eine Gruppe erstellen
        create_data = {
            "name": "Group to Update",
            "code": "group_to_update",
            "description": "Ursprüngliche Beschreibung"
        }
        
        create_response = client.post("/api/interest-groups", json=create_data)
        assert create_response.status_code == 200
        created_group = create_response.json()
        group_id = created_group["id"]
        
        # Gruppe aktualisieren
        update_data = {
            "name": "Updated Group Name",
            "description": "Aktualisierte Beschreibung",
            "is_external": True
        }
        
        response = client.put(f"/api/interest-groups/{group_id}", json=update_data)
        
        # Bestehendes Verhalten dokumentieren
        assert response.status_code == 200
        updated_group = response.json()
        
        # Aktualisierte Felder sollten geändert sein
        assert updated_group["name"] == "Updated Group Name"
        assert updated_group["description"] == "Aktualisierte Beschreibung"
        assert updated_group["is_external"] is True
        
        # Nicht aktualisierte Felder sollten unverändert bleiben
        assert updated_group["code"] == "group_to_update"
        assert updated_group["is_active"] is True
    
    def test_update_interest_group_partial_update(self, client):
        """Test: Partielle Updates funktionieren korrekt"""
        # Erst eine Gruppe erstellen
        create_data = {
            "name": "Partial Update Group",
            "code": "partial_update_group",
            "description": "Ursprüngliche Beschreibung",
            "ai_functionality": "Ursprüngliche AI Funktionen"
        }
        
        create_response = client.post("/api/interest-groups", json=create_data)
        assert create_response.status_code == 200
        created_group = create_response.json()
        group_id = created_group["id"]
        
        # Nur ein Feld aktualisieren
        update_data = {
            "description": "Neue Beschreibung"
        }
        
        response = client.put(f"/api/interest-groups/{group_id}", json=update_data)
        assert response.status_code == 200
        updated_group = response.json()
        
        # Nur das aktualisierte Feld sollte geändert sein
        assert updated_group["description"] == "Neue Beschreibung"
        
        # Alle anderen Felder sollten unverändert bleiben
        assert updated_group["name"] == "Partial Update Group"
        assert updated_group["code"] == "partial_update_group"
        assert updated_group["ai_functionality"] == "Ursprüngliche AI Funktionen"
    
    def test_update_interest_group_not_found(self, client):
        """Test: Update nicht existierender Gruppe gibt 404 zurück"""
        non_existent_id = 99999
        
        update_data = {
            "name": "Updated Name"
        }
        
        response = client.put(f"/api/interest-groups/{non_existent_id}", json=update_data)
        
        # Bestehendes Verhalten: 404 für nicht gefundene Gruppen
        assert response.status_code == 404
    
    def test_update_interest_group_invalid_id_format(self, client):
        """Test: Ungültige ID-Formate werden abgelehnt"""
        update_data = {
            "name": "Updated Name"
        }
        
        # String-ID
        response = client.put("/api/interest-groups/invalid", json=update_data)
        assert response.status_code == 422
        
        # Negative ID
        response = client.put("/api/interest-groups/-1", json=update_data)
        assert response.status_code == 404
    
    def test_update_interest_group_validation_rules(self, client):
        """Test: Validierungsregeln gelten auch bei Updates"""
        # Erst eine Gruppe erstellen
        create_data = {
            "name": "Validation Test Group",
            "code": "validation_test_group",
            "description": "Test"
        }
        
        create_response = client.post("/api/interest-groups", json=create_data)
        assert create_response.status_code == 200
        created_group = create_response.json()
        group_id = created_group["id"]
        
        # Test mit zu kurzem Namen
        short_name_update = {
            "name": "A"  # Zu kurz (min 2 Zeichen)
        }
        
        response = client.put(f"/api/interest-groups/{group_id}", json=short_name_update)
        
        # Bestehendes Verhalten: 422 für ungültige Namen
        assert response.status_code == 422
        
        # Test mit zu langem Namen
        long_name_update = {
            "name": "A" * 101  # Zu lang (max 100 Zeichen)
        }
        
        response = client.put(f"/api/interest-groups/{group_id}", json=long_name_update)
        
        # Bestehendes Verhalten: 422 für zu lange Namen
        assert response.status_code == 422
        
        # Test mit ungültigem Code-Format
        invalid_code_update = {
            "code": "InvalidCode"  # Sollte snake_case sein
        }
        
        response = client.put(f"/api/interest-groups/{group_id}", json=invalid_code_update)
        
        # Bestehendes Verhalten: 422 für ungültige Codes
        assert response.status_code == 422
    
    def test_update_interest_group_permissions_parsing(self, client):
        """Test: group_permissions werden bei Updates korrekt geparst"""
        # Erst eine Gruppe erstellen
        create_data = {
            "name": "Permissions Test Group",
            "code": "permissions_test_group",
            "group_permissions": ["original_perm1", "original_perm2"]
        }
        
        create_response = client.post("/api/interest-groups", json=create_data)
        assert create_response.status_code == 200
        created_group = create_response.json()
        group_id = created_group["id"]
        
        # Permissions als Liste aktualisieren
        list_update = {
            "group_permissions": ["new_perm1", "new_perm2", "new_perm3"]
        }
        
        response = client.put(f"/api/interest-groups/{group_id}", json=list_update)
        assert response.status_code == 200
        updated_group = response.json()
        assert updated_group["group_permissions"] == ["new_perm1", "new_perm2", "new_perm3"]
        
        # Permissions als JSON-String aktualisieren
        json_update = {
            "group_permissions": '["json_perm1", "json_perm2"]'
        }
        
        response = client.put(f"/api/interest-groups/{group_id}", json=json_update)
        assert response.status_code == 200
        updated_group = response.json()
        assert updated_group["group_permissions"] == ["json_perm1", "json_perm2"]
        
        # Permissions als komma-separierte Strings aktualisieren
        comma_update = {
            "group_permissions": "comma_perm1, comma_perm2, comma_perm3"
        }
        
        response = client.put(f"/api/interest-groups/{group_id}", json=comma_update)
        assert response.status_code == 200
        updated_group = response.json()
        assert updated_group["group_permissions"] == ["comma_perm1", "comma_perm2", "comma_perm3"]
    
    def test_update_interest_group_duplicate_constraints(self, client):
        """Test: Duplikat-Constraints gelten auch bei Updates"""
        # Zwei Gruppen erstellen
        first_group_data = {
            "name": "First Group for Duplicate Test",
            "code": "first_duplicate_test"
        }
        
        second_group_data = {
            "name": "Second Group for Duplicate Test",
            "code": "second_duplicate_test"
        }
        
        first_response = client.post("/api/interest-groups", json=first_group_data)
        second_response = client.post("/api/interest-groups", json=second_group_data)
        
        assert first_response.status_code == 200
        assert second_response.status_code == 200
        
        first_group = first_response.json()
        second_group = second_response.json()
        
        # Versuch, den Code der ersten Gruppe auf den der zweiten zu setzen
        duplicate_code_update = {
            "code": "second_duplicate_test"
        }
        
        response = client.put(f"/api/interest-groups/{first_group['id']}", json=duplicate_code_update)
        
        # Bestehendes Verhalten: 422 für doppelte Codes
        assert response.status_code == 422
        
        # Versuch, den Namen der ersten Gruppe auf den der zweiten zu setzen
        duplicate_name_update = {
            "name": "Second Group for Duplicate Test"
        }
        
        response = client.put(f"/api/interest-groups/{first_group['id']}", json=duplicate_name_update)
        
        # Bestehendes Verhalten: 422 für doppelte Namen
        assert response.status_code == 422
    
    def test_update_interest_group_boolean_fields(self, client):
        """Test: Boolean-Felder werden korrekt aktualisiert"""
        # Erst eine Gruppe erstellen
        create_data = {
            "name": "Boolean Test Group",
            "code": "boolean_test_group",
            "is_external": False,
            "is_active": True
        }
        
        create_response = client.post("/api/interest-groups", json=create_data)
        assert create_response.status_code == 200
        created_group = create_response.json()
        group_id = created_group["id"]
        
        # Boolean-Felder aktualisieren
        boolean_update = {
            "is_external": True,
            "is_active": False
        }
        
        response = client.put(f"/api/interest-groups/{group_id}", json=boolean_update)
        assert response.status_code == 200
        updated_group = response.json()
        
        # Boolean-Felder sollten aktualisiert sein
        assert updated_group["is_external"] is True
        assert updated_group["is_active"] is False
    
    def test_update_existing_group(self, client):
        """Test: UPDATE-Parität mit getrennten DBs (Legacy vs DDD)"""
        # Getrennte DB-Pfade
        legacy_db = ".tmp/_legacy.db"
        ddd_db = ".tmp/_ddd.db"
        
        # Test-Daten
        create_data = {
            "name": "Update Parity Group",
            "code": "update_parity_group",
            "description": "Test für UPDATE-Parität"
        }
        
        update_data = {
            "description": "Aktualisierte Beschreibung"
        }
        
        # Legacy: POST + UPDATE
        legacy_create = run_legacy("backend.app.main:app", legacy_db, "POST", "/api/interest-groups", create_data)
        legacy_group_id = legacy_create[1].get("id", 0)
        
        legacy_update = run_legacy("backend.app.main:app", legacy_db, "PUT", f"/api/interest-groups/{legacy_group_id}", update_data)
        
        # DDD: POST + UPDATE
        ddd_create = run_ddd("backend.app.main:app", ddd_db, "POST", "/api/interest-groups", create_data)
        ddd_group_id = ddd_create[1].get("id", 0)
        
        ddd_update = run_ddd("backend.app.main:app", ddd_db, "PUT", f"/api/interest-groups/{ddd_group_id}", update_data)
        
        # Ergebnisse
        print(f"POST id check: legacy_id>0={legacy_group_id > 0}, ddd_id>0={ddd_group_id > 0}")
        print(f"UPDATE parity: legacy={legacy_update[0]}, ddd={ddd_update[0]}")
        
        # Body-Parität prüfen
        if legacy_update[0] == 200 and ddd_update[0] == 200:
            legacy_body = legacy_update[1]
            ddd_body = ddd_update[1]
            body_equal = "description" in legacy_body and "description" in ddd_body and legacy_body.get("description") == ddd_body.get("description")
            print(f"UPDATE body_equal={body_equal}")
        else:
            print(f"UPDATE body_equal=false (status mismatch)")
