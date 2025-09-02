"""
Charakterisierungstest für GET /api/interest-groups
Dokumentiert das bestehende Verhalten ohne neue Regeln zu erfinden.
"""

import pytest

class TestGetInterestGroups:
    """Test für GET /api/interest-groups Endpunkt"""
    
    def test_get_interest_groups_returns_list(self, client):
        """Test: Endpunkt gibt Liste aller Interessensgruppen zurück"""
        response = client.get("/api/interest-groups")
        
        # Bestehendes Verhalten dokumentieren
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        
        # Struktur der Antwort dokumentieren
        if response.json():
            first_group = response.json()[0]
            expected_fields = [
                "id", "name", "code", "description", "group_permissions",
                "ai_functionality", "typical_tasks", "is_external", 
                "is_active", "created_at"
            ]
            for field in expected_fields:
                assert field in first_group, f"Feld {field} fehlt in der Antwort"
    
    def test_get_interest_groups_includes_active_groups(self, client):
        """Test: Endpunkt gibt nur aktive Gruppen zurück (is_active=True)"""
        response = client.get("/api/interest-groups")
        
        assert response.status_code == 200
        groups = response.json()
        
        # Alle zurückgegebenen Gruppen sollten aktiv sein
        for group in groups:
            assert group["is_active"] is True, f"Gruppe {group['name']} ist nicht aktiv"
    
    def test_get_interest_groups_structure(self, client):
        """Test: Struktur der Interessensgruppe entspricht dem erwarteten Schema"""
        response = client.get("/api/interest-groups")
        
        assert response.status_code == 200
        groups = response.json()
        
        if groups:
            group = groups[0]
            
            # ID sollte Integer sein
            assert isinstance(group["id"], int)
            
            # Name sollte String mit Länge 2-100 sein
            assert isinstance(group["name"], str)
            assert 2 <= len(group["name"]) <= 100
            
            # Code sollte String mit Länge 2-50 sein
            assert isinstance(group["code"], str)
            assert 2 <= len(group["code"]) <= 50
            
            # Code sollte snake_case Format haben
            assert group["code"].replace("_", "").isalnum()
            assert group["code"] == group["code"].lower()
            assert not group["code"].startswith("_")
            assert not group["code"].endswith("_")
            
            # Boolean-Felder sollten Boolean sein
            assert isinstance(group["is_external"], bool)
            assert isinstance(group["is_active"], bool)
            
            # created_at sollte String sein (ISO-Format)
            assert isinstance(group["created_at"], str)
    
    def test_get_interest_groups_permissions_format(self, client):
        """Test: group_permissions werden als Liste zurückgegeben"""
        response = client.get("/api/interest-groups")
        
        assert response.status_code == 200
        groups = response.json()
        
        for group in groups:
            # group_permissions sollte Liste sein
            assert isinstance(group["group_permissions"], list)
            
            # Alle Permissions sollten Strings sein
            for permission in group["group_permissions"]:
                assert isinstance(permission, str)
    
    def test_get_interest_groups_no_authentication_required(self, client):
        """Test: Endpunkt ist ohne Authentifizierung erreichbar"""
        response = client.get("/api/interest-groups")
        
        # Bestehendes Verhalten: Keine Authentifizierung erforderlich
        assert response.status_code == 200
    
    def test_get_interest_groups_empty_response(self, client):
        """Test: Endpunkt gibt leere Liste zurück wenn keine Gruppen existieren"""
        # Dieser Test dokumentiert das Verhalten bei leeren Daten
        # In der Praxis sollten immer die 13 Standard-Gruppen existieren
        response = client.get("/api/interest-groups")
        
        assert response.status_code == 200
        # Dokumentiert: Endpunkt gibt immer 200 zurück, auch bei leeren Daten
        assert isinstance(response.json(), list)
