"""
Charakterisierungstest für GET /api/interest-groups/{group_id}
Dokumentiert das bestehende Verhalten ohne neue Regeln zu erfinden.
"""

import pytest

class TestGetInterestGroupById:
    """Test für GET /api/interest-groups/{group_id} Endpunkt"""
    
    def test_get_interest_group_by_id_returns_single_group(self, client):
        """Test: Endpunkt gibt einzelne Interessensgruppe zurück"""
        # Erst alle Gruppen abrufen um eine gültige ID zu bekommen
        response = client.get("/api/interest-groups")
        assert response.status_code == 200
        groups = response.json()
        
        if groups:
            group_id = groups[0]["id"]
            
            # Einzelne Gruppe abrufen
            response = client.get(f"/api/interest-groups/{group_id}")
            
            assert response.status_code == 200
            group = response.json()
            
            # Sollte einzelnes Objekt sein, nicht Liste
            assert isinstance(group, dict)
            assert group["id"] == group_id
    
    def test_get_interest_group_by_id_structure(self, client):
        """Test: Struktur der einzelnen Gruppe entspricht dem Schema"""
        # Erst alle Gruppen abrufen
        response = client.get("/api/interest-groups")
        assert response.status_code == 200
        groups = response.json()
        
        if groups:
            group_id = groups[0]["id"]
            
            # Einzelne Gruppe abrufen
            response = client.get(f"/api/interest-groups/{group_id}")
            assert response.status_code == 200
            group = response.json()
            
            # Alle erwarteten Felder sollten vorhanden sein
            expected_fields = [
                "id", "name", "code", "description", "group_permissions",
                "ai_functionality", "typical_tasks", "is_external", 
                "is_active", "created_at"
            ]
            for field in expected_fields:
                assert field in group, f"Feld {field} fehlt in der Antwort"
            
            # ID sollte mit der angeforderten ID übereinstimmen
            assert group["id"] == group_id
    
    def test_get_interest_group_by_id_not_found(self, client):
        """Test: Endpunkt gibt 404 zurück für nicht existierende ID"""
        # Verwende eine sehr hohe ID die sicher nicht existiert
        non_existent_id = 99999
        
        response = client.get(f"/api/interest-groups/{non_existent_id}")
        
        # Bestehendes Verhalten: 404 für nicht gefundene Gruppen
        assert response.status_code == 404
    
    def test_get_interest_group_by_id_invalid_id_format(self, client):
        """Test: Endpunkt behandelt ungültige ID-Formate korrekt"""
        # Test mit String-ID (sollte 422 Validation Error geben)
        response = client.get("/api/interest-groups/invalid")
        
        # Bestehendes Verhalten: 422 für ungültige ID-Formate
        assert response.status_code == 422
    
    def test_get_interest_group_by_id_negative_id(self, client):
        """Test: Endpunkt behandelt negative IDs korrekt"""
        response = client.get("/api/interest-groups/-1")
        
        # Bestehendes Verhalten: 404 für negative IDs (da sie nicht existieren)
        assert response.status_code == 404
    
    def test_get_interest_group_by_id_zero_id(self, client):
        """Test: Endpunkt behandelt ID 0 korrekt"""
        response = client.get("/api/interest-groups/0")
        
        # Bestehendes Verhalten: 404 für ID 0 (da sie normalerweise nicht existiert)
        assert response.status_code == 404
    
    def test_get_interest_group_by_id_no_authentication_required(self, client):
        """Test: Endpunkt ist ohne Authentifizierung erreichbar"""
        # Erst alle Gruppen abrufen
        response = client.get("/api/interest-groups")
        assert response.status_code == 200
        groups = response.json()
        
        if groups:
            group_id = groups[0]["id"]
            
            # Einzelne Gruppe ohne Authentifizierung abrufen
            response = client.get(f"/api/interest-groups/{group_id}")
            
            # Bestehendes Verhalten: Keine Authentifizierung erforderlich
            assert response.status_code == 200
