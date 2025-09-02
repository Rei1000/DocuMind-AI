"""
Charakterisierungstest für POST /api/interest-groups
Dokumentiert das bestehende Verhalten ohne neue Regeln zu erfinden.
"""

import pytest

class TestCreateInterestGroup:
    """Test für POST /api/interest-groups Endpunkt"""
    
    def test_create_interest_group_with_valid_data(self, client):
        """Test: Endpunkt erstellt neue Interessensgruppe mit gültigen Daten"""
        # Test-Daten für neue Gruppe
        new_group_data = {
            "name": "Test Interest Group",
            "code": "test_interest_group",
            "description": "Eine Test-Interessensgruppe für Charakterisierungstests",
            "group_permissions": ["test_permission", "another_permission"],
            "ai_functionality": "Test AI Funktionen",
            "typical_tasks": "Test-Aufgaben",
            "is_external": False,
            "is_active": True
        }
        
        response = client.post("/api/interest-groups", json=new_group_data)
        
        # Bestehendes Verhalten dokumentieren
        assert response.status_code == 200
        created_group = response.json()
        
        # Alle gesendeten Felder sollten in der Antwort enthalten sein
        for key, value in new_group_data.items():
            if key == "group_permissions":
                # group_permissions werden als Liste zurückgegeben
                assert isinstance(created_group[key], list)
                assert set(created_group[key]) == set(value)
            else:
                assert created_group[key] == value
        
        # ID und created_at sollten automatisch gesetzt werden
        assert "id" in created_group
        assert isinstance(created_group["id"], int)
        assert "created_at" in created_group
        assert isinstance(created_group["created_at"], str)
    
    def test_create_interest_group_code_validation(self, client):
        """Test: Code-Validierung funktioniert korrekt"""
        # Test mit ungültigem Code-Format
        invalid_group_data = {
            "name": "Test Group",
            "code": "InvalidCode",  # Sollte snake_case sein
            "description": "Test"
        }
        
        response = client.post("/api/interest-groups", json=invalid_group_data)
        
        # Bestehendes Verhalten: 422 für ungültige Codes
        assert response.status_code == 422
        
        # Test mit gültigem Code-Format
        valid_group_data = {
            "name": "Test Group",
            "code": "valid_code",  # Korrektes snake_case
            "description": "Test"
        }
        
        response = client.post("/api/interest-groups", json=valid_group_data)
        assert response.status_code == 200
    
    def test_create_interest_group_name_validation(self, client):
        """Test: Name-Validierung funktioniert korrekt"""
        # Test mit zu kurzem Namen
        short_name_data = {
            "name": "A",  # Zu kurz (min 2 Zeichen)
            "code": "test_group",
            "description": "Test"
        }
        
        response = client.post("/api/interest-groups", json=short_name_data)
        
        # Bestehendes Verhalten: 422 für zu kurze Namen
        assert response.status_code == 422
        
        # Test mit zu langem Namen
        long_name_data = {
            "name": "A" * 101,  # Zu lang (max 100 Zeichen)
            "code": "test_group",
            "description": "Test"
        }
        
        response = client.post("/api/interest-groups", json=long_name_data)
        
        # Bestehendes Verhalten: 422 für zu lange Namen
        assert response.status_code == 422
    
    def test_create_interest_group_code_validation(self, client):
        """Test: Code-Validierung funktioniert korrekt"""
        # Test mit zu kurzem Code
        short_code_data = {
            "name": "Test Group",
            "code": "A",  # Zu kurz (min 2 Zeichen)
            "description": "Test"
        }
        
        response = client.post("/api/interest-groups", json=short_code_data)
        
        # Bestehendes Verhalten: 422 für zu kurze Codes
        assert response.status_code == 422
        
        # Test mit zu langem Code
        long_code_data = {
            "name": "Test Group",
            "code": "A" * 51,  # Zu lang (max 50 Zeichen)
            "description": "Test"
        }
        
        response = client.post("/api/interest-groups", json=long_code_data)
        
        # Bestehendes Verhalten: 422 für zu lange Codes
        assert response.status_code == 422
    
    def test_create_interest_group_permissions_parsing(self, client):
        """Test: group_permissions werden korrekt geparst"""
        # Test mit verschiedenen Permission-Formaten
        
        # 1. Liste von Strings
        list_permissions_data = {
            "name": "Test Group",
            "code": "test_group",
            "group_permissions": ["perm1", "perm2", "perm3"]
        }
        
        response = client.post("/api/interest-groups", json=list_permissions_data)
        assert response.status_code == 200
        created_group = response.json()
        assert created_group["group_permissions"] == ["perm1", "perm2", "perm3"]
        
        # 2. JSON-String
        json_permissions_data = {
            "name": "Test Group 2",
            "code": "test_group_2",
            "group_permissions": '["json_perm1", "json_perm2"]'
        }
        
        response = client.post("/api/interest-groups", json=json_permissions_data)
        assert response.status_code == 200
        created_group = response.json()
        assert created_group["group_permissions"] == ["json_perm1", "json_perm2"]
        
        # 3. Komma-separierte Strings
        comma_permissions_data = {
            "name": "Test Group 3",
            "code": "test_group_3",
            "group_permissions": "comma_perm1, comma_perm2, comma_perm3"
        }
        
        response = client.post("/api/interest-groups", json=comma_permissions_data)
        assert response.status_code == 200
        created_group = response.json()
        assert created_group["group_permissions"] == ["comma_perm1", "comma_perm2", "comma_perm3"]
    
    def test_create_interest_group_optional_fields(self, client):
        """Test: Optionale Felder werden korrekt behandelt"""
        # Minimaler Datensatz nur mit erforderlichen Feldern
        minimal_data = {
            "name": "Minimal Group",
            "code": "minimal_group"
        }
        
        response = client.post("/api/interest-groups", json=minimal_data)
        assert response.status_code == 200
        
        created_group = response.json()
        
        # Standardwerte sollten gesetzt werden
        assert created_group["description"] is None
        assert created_group["group_permissions"] == []
        assert created_group["ai_functionality"] is None
        assert created_group["typical_tasks"] is None
        assert created_group["is_external"] is False
        assert created_group["is_active"] is True
    
    def test_create_interest_group_duplicate_code(self, client):
        """Test: Duplikate Codes werden abgelehnt"""
        # Erste Gruppe erstellen
        first_group_data = {
            "name": "First Group",
            "code": "duplicate_code",
            "description": "Erste Gruppe"
        }
        
        response = client.post("/api/interest-groups", json=first_group_data)
        assert response.status_code == 200
        
        # Zweite Gruppe mit gleichem Code (sollte fehlschlagen)
        second_group_data = {
            "name": "Second Group",
            "code": "duplicate_code",  # Gleicher Code
            "description": "Zweite Gruppe"
        }
        
        response = client.post("/api/interest-groups", json=second_group_data)
        
        # Bestehendes Verhalten: 422 für doppelte Codes
        assert response.status_code == 422
    
    def test_create_interest_group_duplicate_name(self, client):
        """Test: Duplikate Namen werden abgelehnt"""
        # Erste Gruppe erstellen
        first_group_data = {
            "name": "Duplicate Name Group",
            "code": "first_code",
            "description": "Erste Gruppe"
        }
        
        response = client.post("/api/interest-groups", json=first_group_data)
        assert response.status_code == 200
        
        # Zweite Gruppe mit gleichem Namen (sollte fehlschlagen)
        second_group_data = {
            "name": "Duplicate Name Group",  # Gleicher Name
            "code": "second_code",
            "description": "Zweite Gruppe"
        }
        
        response = client.post("/api/interest-groups", json=second_group_data)
        
        # Bestehendes Verhalten: 422 für doppelte Namen
        assert response.status_code == 422
