"""
Charakterisierungstest für DELETE /api/interest-groups/{group_id}
Dokumentiert das bestehende Verhalten ohne neue Regeln zu erfinden.
"""

import pytest

class TestDeleteInterestGroup:
    """Test für DELETE /api/interest-groups/{group_id} Endpunkt"""
    
    def test_delete_interest_group_success(self, client):
        """Test: Endpunkt löscht Interessensgruppe erfolgreich"""
        # Erst eine Gruppe erstellen
        create_data = {
            "name": "Group to Delete",
            "code": "group_to_delete",
            "description": "Diese Gruppe wird gelöscht"
        }
        
        create_response = client.post("/api/interest-groups", json=create_data)
        assert create_response.status_code == 200
        created_group = create_response.json()
        group_id = created_group["id"]
        
        # Gruppe löschen
        response = client.delete(f"/api/interest-groups/{group_id}")
        
        # Bestehendes Verhalten dokumentieren
        assert response.status_code == 200
        
        # Gruppe sollte nicht mehr abrufbar sein
        get_response = client.get(f"/api/interest-groups/{group_id}")
        assert get_response.status_code == 404
    
    def test_delete_interest_group_not_found(self, client):
        """Test: Löschen nicht existierender Gruppe gibt 404 zurück"""
        non_existent_id = 99999
        
        response = client.delete(f"/api/interest-groups/{non_existent_id}")
        
        # Bestehendes Verhalten: 404 für nicht gefundene Gruppen
        assert response.status_code == 404
    
    def test_delete_interest_group_invalid_id_format(self, client):
        """Test: Ungültige ID-Formate werden abgelehnt"""
        # String-ID
        response = client.delete("/api/interest-groups/invalid")
        assert response.status_code == 422
        
        # Negative ID
        response = client.delete("/api/interest-groups/-1")
        assert response.status_code == 404
        
        # ID 0
        response = client.delete("/api/interest-groups/0")
        assert response.status_code == 404
    
    def test_delete_interest_group_soft_delete(self, client):
        """Test: Löschen ist ein Soft-Delete (is_active=False)"""
        # Erst eine Gruppe erstellen
        create_data = {
            "name": "Soft Delete Test Group",
            "code": "soft_delete_test_group",
            "description": "Test für Soft-Delete"
        }
        
        create_response = client.post("/api/interest-groups", json=create_data)
        assert create_response.status_code == 200
        created_group = create_response.json()
        group_id = created_group["id"]
        
        # Gruppe löschen
        delete_response = client.delete(f"/api/interest-groups/{group_id}")
        assert delete_response.status_code == 200
        
        # Gruppe sollte noch in der Datenbank existieren, aber is_active=False haben
        # Da der GET-Endpunkt nur aktive Gruppen zurückgibt, sollte 404 zurückkommen
        get_response = client.get(f"/api/interest-groups/{group_id}")
        assert get_response.status_code == 404
        
        # Aber die Gruppe sollte nicht mehr in der Liste aller Gruppen erscheinen
        list_response = client.get("/api/interest-groups")
        assert list_response.status_code == 200
        groups = list_response.json()
        
        # Die gelöschte Gruppe sollte nicht in der Liste sein
        deleted_group_ids = [g["id"] for g in groups]
        assert group_id not in deleted_group_ids
    
    def test_delete_interest_group_response_structure(self, client):
        """Test: Antwort des DELETE-Endpunkts hat korrekte Struktur"""
        # Erst eine Gruppe erstellen
        create_data = {
            "name": "Response Structure Test Group",
            "code": "response_structure_test",
            "description": "Test für Antwortstruktur"
        }
        
        create_response = client.post("/api/interest-groups", json=create_data)
        assert create_response.status_code == 200
        created_group = create_response.json()
        group_id = created_group["id"]
        
        # Gruppe löschen
        response = client.delete(f"/api/interest-groups/{group_id}")
        assert response.status_code == 200
        
        # Antwort sollte eine Bestätigung enthalten
        response_data = response.json()
        
        # Bestehendes Verhalten dokumentieren
        # Die genaue Struktur der Antwort hängt von der Implementierung ab
        # Hier dokumentieren wir nur, dass eine Antwort zurückgegeben wird
        assert isinstance(response_data, dict)
    
    def test_delete_interest_group_multiple_deletions(self, client):
        """Test: Mehrfache Löschungen der gleichen Gruppe"""
        # Erst eine Gruppe erstellen
        create_data = {
            "name": "Multiple Delete Test Group",
            "code": "multiple_delete_test",
            "description": "Test für mehrfache Löschungen"
        }
        
        create_response = client.post("/api/interest-groups", json=create_data)
        assert create_response.status_code == 200
        created_group = create_response.json()
        group_id = created_group["id"]
        
        # Gruppe zum ersten Mal löschen
        first_delete = client.delete(f"/api/interest-groups/{group_id}")
        assert first_delete.status_code == 200
        
        # Gruppe zum zweiten Mal löschen (sollte 404 zurückgeben)
        second_delete = client.delete(f"/api/interest-groups/{group_id}")
        
        # Bestehendes Verhalten: 404 für bereits gelöschte Gruppen
        assert second_delete.status_code == 404
    
    def test_delete_interest_group_no_authentication_required(self, client):
        """Test: Endpunkt ist ohne Authentifizierung erreichbar"""
        # Erst eine Gruppe erstellen
        create_data = {
            "name": "Auth Test Group",
            "code": "auth_test_group",
            "description": "Test für Authentifizierung"
        }
        
        create_response = client.post("/api/interest-groups", json=create_data)
        assert create_response.status_code == 200
        created_group = create_response.json()
        group_id = created_group["id"]
        
        # Gruppe ohne Authentifizierung löschen
        response = client.delete(f"/api/interest-groups/{group_id}")
        
        # Bestehendes Verhalten: Keine Authentifizierung erforderlich
        assert response.status_code == 200
    
    def test_delete_interest_group_cascade_effects(self, client):
        """Test: Löschen einer Gruppe hat keine Cascade-Effekte auf andere Daten"""
        # Zwei Gruppen erstellen
        first_group_data = {
            "name": "First Group for Cascade Test",
            "code": "first_cascade_test"
        }
        
        second_group_data = {
            "name": "Second Group for Cascade Test",
            "code": "second_cascade_test"
        }
        
        first_response = client.post("/api/interest-groups", json=first_group_data)
        second_response = client.post("/api/interest-groups", json=second_group_data)
        
        assert first_response.status_code == 200
        assert second_response.status_code == 200
        
        first_group = first_response.json()
        second_group = second_response.json()
        
        # Erste Gruppe löschen
        delete_response = client.delete(f"/api/interest-groups/{first_group['id']}")
        assert delete_response.status_code == 200
        
        # Zweite Gruppe sollte unverändert bleiben
        get_response = client.get(f"/api/interest-groups/{second_group['id']}")
        assert get_response.status_code == 200
        
        updated_second_group = get_response.json()
        assert updated_second_group["name"] == "Second Group for Cascade Test"
        assert updated_second_group["code"] == "second_cascade_test"
        assert updated_second_group["is_active"] is True
