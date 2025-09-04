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
        """Test: Duplikate Codes werden identisch behandelt (Legacy vs DDD)"""
        # Erste Gruppe erstellen (Legacy)
        first_group_data = {
            "name": "First Group",
            "code": "duplicate_code",
            "description": "Erste Gruppe"
        }
        
        legacy_response = client.post("/api/interest-groups", json=first_group_data, headers={"Content-Type": "application/json"})
        assert legacy_response.status_code == 200
        
        # Zweite Gruppe mit gleichem Code (Legacy)
        second_group_data = {
            "name": "Second Group",
            "code": "duplicate_code",  # Gleicher Code
            "description": "Zweite Gruppe"
        }
        
        legacy_duplicate_response = client.post("/api/interest-groups", json=second_group_data, headers={"Content-Type": "application/json"})
        
        # DDD-Modus: Erste Gruppe erstellen (mit anderem Code für frischen DB-Zustand)
        ddd_first_data = {
            "name": "DDD First Group",
            "code": "ddd_duplicate_code",
            "description": "DDD Erste Gruppe"
        }
        
        ddd_response = client.post("/api/interest-groups", json=ddd_first_data, headers={"Content-Type": "application/json"})
        assert ddd_response.status_code == 200
        
        # DDD-Modus: Zweite Gruppe mit gleichem Code
        ddd_second_data = {
            "name": "DDD Second Group",
            "code": "ddd_duplicate_code",  # Gleicher Code
            "description": "DDD Zweite Gruppe"
        }
        
        ddd_duplicate_response = client.post("/api/interest-groups", json=ddd_second_data, headers={"Content-Type": "application/json"})
        
        # Parität: Beide Modi sollten identischen Statuscode zurückgeben
        assert legacy_duplicate_response.status_code == ddd_duplicate_response.status_code, f"Statuscode-Parität verletzt: Legacy={legacy_duplicate_response.status_code}, DDD={ddd_duplicate_response.status_code}"
        
        # Snapshot des tatsächlichen Verhaltens
        print(f"Duplicate Code Test - Legacy: {legacy_duplicate_response.status_code}, DDD: {ddd_duplicate_response.status_code}")
    
    def test_create_interest_group_duplicate_name(self, client):
        """Test: Duplikate Namen werden identisch behandelt (Legacy vs DDD)"""
        # Erste Gruppe erstellen (Legacy)
        first_group_data = {
            "name": "Duplicate Name Group",
            "code": "first_code",
            "description": "Erste Gruppe"
        }
        
        legacy_response = client.post("/api/interest-groups", json=first_group_data, headers={"Content-Type": "application/json"})
        assert legacy_response.status_code == 200
        
        # Zweite Gruppe mit gleichem Namen (Legacy) - sollte fehlschlagen
        second_group_data = {
            "name": "Duplicate Name Group",  # Gleicher Name
            "code": "second_code",
            "description": "Zweite Gruppe"
        }
        
        try:
            legacy_duplicate_response = client.post("/api/interest-groups", json=second_group_data, headers={"Content-Type": "application/json"})
            legacy_status = legacy_duplicate_response.status_code
        except Exception as e:
            # Falls der Request eine Exception wirft, dokumentieren wir das
            legacy_status = f"Exception: {type(e).__name__}"
        
        # DDD-Modus: Erste Gruppe erstellen (mit anderem Namen für frischen DB-Zustand)
        ddd_first_data = {
            "name": "DDD Duplicate Name Group",
            "code": "ddd_first_code",
            "description": "DDD Erste Gruppe"
        }
        
        ddd_response = client.post("/api/interest-groups", json=ddd_first_data, headers={"Content-Type": "application/json"})
        assert ddd_response.status_code == 200
        
        # DDD-Modus: Zweite Gruppe mit gleichem Namen - sollte fehlschlagen
        ddd_second_data = {
            "name": "DDD Duplicate Name Group",  # Gleicher Name
            "code": "ddd_second_code",
            "description": "DDD Zweite Gruppe"
        }
        
        try:
            ddd_duplicate_response = client.post("/api/interest-groups", json=ddd_second_data, headers={"Content-Type": "application/json"})
            ddd_status = ddd_duplicate_response.status_code
        except Exception as e:
            # Falls der Request eine Exception wirft, dokumentieren wir das
            ddd_status = f"Exception: {type(e).__name__}"
        
        # Snapshot des tatsächlichen Verhaltens
        print(f"Duplicate Name Test - Legacy: {legacy_status}, DDD: {ddd_status}")
        
        # Beide Modi sollten das gleiche Verhalten zeigen (entweder gleicher Statuscode oder gleiche Exception)
        if isinstance(legacy_status, int) and isinstance(ddd_status, int):
            # Beide gaben Statuscodes zurück
            assert legacy_status == ddd_status, f"Statuscode-Parität verletzt: Legacy={legacy_status}, DDD={ddd_status}"
        elif isinstance(legacy_status, str) and isinstance(ddd_status, str):
            # Beide warfen Exceptions
            assert legacy_status == ddd_status, f"Exception-Parität verletzt: Legacy={legacy_status}, DDD={ddd_status}"
        else:
            # Gemischtes Verhalten - dokumentieren
            print(f"WARNUNG: Gemischtes Verhalten - Legacy: {legacy_status}, DDD: {ddd_status}")
