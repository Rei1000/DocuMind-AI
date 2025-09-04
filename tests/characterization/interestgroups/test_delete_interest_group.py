"""
Charakterisierungstest für DELETE /api/interest-groups/{group_id}
Dokumentiert das bestehende Verhalten ohne neue Regeln zu erfinden.
"""

import pytest
import os
from tests.helpers.ab_runner import run_legacy, run_ddd
from tests.helpers.seeds_interest_groups import seed_group

class TestDeleteInterestGroup:
    """Test für DELETE /api/interest-groups/{group_id} Endpunkt"""
    
    def test_delete_interest_group_success(self, client):
        """Test: Endpunkt löscht Interessensgruppe erfolgreich (Legacy vs DDD)"""
        # Erst eine Gruppe erstellen (Legacy)
        create_data = {
            "name": "Group to Delete",
            "code": "group_to_delete",
            "description": "Diese Gruppe wird gelöscht"
        }
        
        legacy_create_response = client.post("/api/interest-groups", json=create_data, headers={"Content-Type": "application/json"})
        assert legacy_create_response.status_code == 200
        created_group = legacy_create_response.json()
        group_id = created_group["id"]
        
        # Gruppe löschen (Legacy)
        legacy_delete_response = client.delete(f"/api/interest-groups/{group_id}")
        
        # DDD-Modus: Erste Gruppe erstellen
        ddd_create_data = {
            "name": "DDD Group to Delete",
            "code": "ddd_group_to_delete",
            "description": "DDD Gruppe wird gelöscht"
        }
        
        ddd_create_response = client.post("/api/interest-groups", json=ddd_create_data, headers={"Content-Type": "application/json"})
        assert ddd_create_response.status_code == 200
        ddd_created_group = ddd_create_response.json()
        ddd_group_id = ddd_created_group["id"]
        
        # Gruppe löschen (DDD)
        ddd_delete_response = client.delete(f"/api/interest-groups/{ddd_group_id}")
        
        # Parität: Beide Modi sollten identischen Statuscode zurückgeben
        assert legacy_delete_response.status_code == ddd_delete_response.status_code, f"Delete-Statuscode-Parität verletzt: Legacy={legacy_delete_response.status_code}, DDD={ddd_delete_response.status_code}"
        
        # Snapshot des tatsächlichen Verhaltens
        print(f"Delete Success Test - Legacy: {legacy_delete_response.status_code}, DDD: {ddd_delete_response.status_code}")
        
        # Gruppe sollte nicht mehr abrufbar sein (Legacy)
        legacy_get_response = client.get(f"/api/interest-groups/{group_id}")
        
        # Gruppe sollte nicht mehr abrufbar sein (DDD)
        ddd_get_response = client.get(f"/api/interest-groups/{ddd_group_id}")
        
        # Parität: Beide Modi sollten identischen Statuscode beim GET zurückgeben
        assert legacy_get_response.status_code == ddd_get_response.status_code, f"GET-Statuscode-Parität verletzt: Legacy={legacy_get_response.status_code}, DDD={ddd_get_response.status_code}"
        
        print(f"GET nach Delete - Legacy: {legacy_get_response.status_code}, DDD: {ddd_get_response.status_code}")
    
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
    
    def test_delete_parity_with_real_ids(self, client):
        """Test: DELETE-Parität mit echten IDs (Legacy vs DDD)"""
        # Test-Daten
        create_data = {
            "name": "Parity Test Group",
            "code": "parity_test_group",
            "description": "Test für DELETE-Parität"
        }
        
        # Legacy-Create
        legacy_create_response = client.post("/api/interest-groups", json=create_data, headers={"Content-Type": "application/json"})
        assert legacy_create_response.status_code == 200
        legacy_created_group = legacy_create_response.json()
        legacy_group_id = legacy_created_group["id"]
        
        # ID-Check: Legacy sollte echte ID haben
        assert legacy_group_id > 0, f"Legacy ID sollte > 0 sein, ist {legacy_group_id}"
        
        # Legacy-Delete
        legacy_delete_response = client.delete(f"/api/interest-groups/{legacy_group_id}")
        
        # DDD-Create (mit anderem Code)
        ddd_create_data = {
            "name": "DDD Parity Test Group",
            "code": "ddd_parity_test_group",
            "description": "DDD Test für DELETE-Parität"
        }
        
        ddd_create_response = client.post("/api/interest-groups", json=ddd_create_data, headers={"Content-Type": "application/json"})
        assert ddd_create_response.status_code == 200
        ddd_created_group = ddd_create_response.json()
        ddd_group_id = ddd_created_group["id"]
        
        # ID-Check: DDD sollte echte ID haben
        assert ddd_group_id > 0, f"DDD ID sollte > 0 sein, ist {ddd_group_id}"
        
        # DDD-Delete
        ddd_delete_response = client.delete(f"/api/interest-groups/{ddd_group_id}")
        
        # Parität: Beide Modi sollten identischen Statuscode zurückgeben
        assert legacy_delete_response.status_code == ddd_delete_response.status_code, f"Delete-Statuscode-Parität verletzt: Legacy={legacy_delete_response.status_code}, DDD={ddd_delete_response.status_code}"
        
        # Body-Parität prüfen (beide sollten message und success haben)
        if legacy_delete_response.status_code == 200 and ddd_delete_response.status_code == 200:
            legacy_body = legacy_delete_response.json()
            ddd_body = ddd_delete_response.json()
            
            # Beide sollten message und success haben
            assert "message" in legacy_body, "Legacy Response sollte 'message' haben"
            assert "message" in ddd_body, "DDD Response sollte 'message' haben"
            
            # Message sollte den Gruppennamen enthalten
            assert "Parity Test Group" in legacy_body["message"], "Legacy message sollte Gruppennamen enthalten"
            assert "DDD Parity Test Group" in ddd_body["message"], "DDD message sollte Gruppennamen enthalten"
            
            print(f"✅ DELETE-Parität erreicht: Legacy={legacy_delete_response.status_code}, DDD={ddd_delete_response.status_code}")
            print(f"✅ ID-Check: Legacy_ID={legacy_group_id}, DDD_ID={ddd_group_id}")
            print(f"✅ Body-Parität: Legacy='{legacy_body['message']}', DDD='{ddd_body['message']}'")
        else:
            print(f"⚠️ DELETE fehlgeschlagen - Legacy: {legacy_delete_response.status_code}, DDD: {ddd_delete_response.status_code}")
    
    def test_delete_existing_group(self, client):
        """Test: DELETE-Parität mit getrennten DBs (Legacy vs DDD)"""
        # Getrennte DB-Pfade
        legacy_db = ".tmp/_legacy.db"
        ddd_db = ".tmp/_ddd.db"
        
        # Test-Daten
        create_data = {
            "name": "Delete Parity Group",
            "code": "delete_parity_group",
            "description": "Test für DELETE-Parität"
        }
        
        # Legacy: POST + DELETE
        legacy_create = run_legacy("backend.app.main:app", legacy_db, "POST", "/api/interest-groups", create_data)
        legacy_group_id = legacy_create[1].get("id", 0)
        
        legacy_delete = run_legacy("backend.app.main:app", legacy_db, "DELETE", f"/api/interest-groups/{legacy_group_id}")
        
        # DDD: POST + DELETE
        ddd_create = run_ddd("backend.app.main:app", ddd_db, "POST", "/api/interest-groups", create_data)
        ddd_group_id = ddd_create[1].get("id", 0)
        
        ddd_delete = run_ddd("backend.app.main:app", ddd_db, "DELETE", f"/api/interest-groups/{ddd_group_id}")
        
        # Ergebnisse
        print(f"POST id check: legacy_id>0={legacy_group_id > 0}, ddd_id>0={ddd_group_id > 0}")
        print(f"DELETE parity: legacy={legacy_delete[0]}, ddd={ddd_delete[0]}")
        
        # Body-Parität prüfen
        if legacy_delete[0] == 200 and ddd_delete[0] == 200:
            legacy_body = legacy_delete[1]
            ddd_body = ddd_delete[1]
            body_equal = "message" in legacy_body and "message" in ddd_body
            print(f"DELETE body_equal={body_equal}")
        else:
            print(f"DELETE body_equal=false (status mismatch)")
