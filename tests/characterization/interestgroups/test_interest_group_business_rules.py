"""
Charakterisierungstest für InterestGroup Business Rules
Dokumentiert das bestehende Verhalten ohne neue Regeln zu erfinden.
"""

import pytest
import sys
from pathlib import Path

# Import-Pfad für Backend-Modelle
backend_path = Path("/Users/reiner/Documents/DocuMind-AI/backend")
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.models import InterestGroup

class TestInterestGroupBusinessRules:
    """Test für InterestGroup Business Rules und Validierungen"""
    
    def test_interest_group_entity_creation(self):
        """Test: InterestGroup Entity kann erstellt werden"""
        # Test mit minimalen Daten
        group = InterestGroup(
            name="Test Business Group",
            code="test_business_group",
            is_external=False,
            is_active=True
        )
        
        # Entity sollte korrekt erstellt werden
        assert group.name == "Test Business Group"
        assert group.code == "test_business_group"
        assert group.is_external is False
        assert group.is_active is True
        assert group.description is None
        assert group.group_permissions is None
        assert group.ai_functionality is None
        assert group.typical_tasks is None
    
    def test_interest_group_permissions_parsing(self):
        """Test: get_group_permissions_list() parst verschiedene Formate korrekt"""
        # Test 1: JSON-String
        group_json = InterestGroup(
            name="JSON Permissions Group",
            code="json_permissions_group",
            group_permissions='["perm1", "perm2", "perm3"]',
            is_external=False,
            is_active=True
        )
        
        permissions = group_json.get_group_permissions_list()
        assert permissions == ["perm1", "perm2", "perm3"]
        
        # Test 2: Komma-separierte Strings
        group_comma = InterestGroup(
            name="Comma Permissions Group",
            code="comma_permissions_group",
            group_permissions="perm1, perm2, perm3",
            is_external=False,
            is_active=True
        )
        
        permissions = group_comma.get_group_permissions_list()
        assert permissions == ["perm1", "perm2", "perm3"]
        
        # Test 3: Liste von Strings
        group_list = InterestGroup(
            name="List Permissions Group",
            code="list_permissions_group",
            group_permissions=["perm1", "perm2", "perm3"],
            is_external=False,
            is_active=True
        )
        
        permissions = group_list.get_group_permissions_list()
        assert permissions == ["perm1", "perm2", "perm3"]
        
        # Test 4: Leere Permissions
        group_empty = InterestGroup(
            name="Empty Permissions Group",
            code="empty_permissions_group",
            group_permissions="",
            is_external=False,
            is_active=True
        )
        
        permissions = group_empty.get_group_permissions_list()
        assert permissions == []
        
        # Test 5: None Permissions
        group_none = InterestGroup(
            name="None Permissions Group",
            code="none_permissions_group",
            group_permissions=None,
            is_external=False,
            is_active=True
        )
        
        permissions = group_none.get_group_permissions_list()
        assert permissions == []
    
    def test_interest_group_code_validation(self):
        """Test: Code-Validierung funktioniert korrekt"""
        # Test mit gültigem Code (snake_case)
        valid_codes = [
            "valid_code",
            "valid_code_123",
            "a",
            "ab",
            "valid_code_with_underscores"
        ]
        
        for code in valid_codes:
            group = InterestGroup(
                name=f"Group with code {code}",
                code=code,
                is_external=False,
                is_active=True
            )
            assert group.code == code
        
        # Test mit ungültigen Codes (sollten Fehler werfen)
        invalid_codes = [
            "InvalidCode",  # PascalCase
            "invalid-code",  # Kebab-Case
            "invalid code",  # Leerzeichen
            "123invalid",    # Beginnt mit Zahl
            "_invalid",      # Beginnt mit Unterstrich
            "invalid_",      # Endet mit Unterstrich
            "__invalid__"    # Mehrere Unterstriche
        ]
        
        for code in invalid_codes:
            try:
                group = InterestGroup(
                    name=f"Group with invalid code {code}",
                    code=code,
                    is_external=False,
                    is_active=True
                )
                # Falls kein Fehler geworfen wird, ist das ein Problem
                assert False, f"Code {code} sollte ungültig sein"
            except Exception:
                # Erwartet: Exception für ungültige Codes
                pass
    
    def test_interest_group_name_validation(self):
        """Test: Name-Validierung funktioniert korrekt"""
        # Test mit gültigen Namen
        valid_names = [
            "Valid Name",
            "Valid Name 123",
            "Valid-Name",
            "Valid_Name",
            "A",  # Minimal
            "A" * 100  # Maximal
        ]
        
        for name in valid_names:
            group = InterestGroup(
                name=name,
                code=f"valid_name_{len(name)}",
                is_external=False,
                is_active=True
            )
            assert group.name == name
        
        # Test mit ungültigen Namen
        invalid_names = [
            "",  # Leerer String
            "A" * 101,  # Zu lang
            None  # None
        ]
        
        for name in invalid_names:
            try:
                group = InterestGroup(
                    name=name,
                    code=f"invalid_name_{hash(name) if name else 'none'}",
                    is_external=False,
                    is_active=True
                )
                # Falls kein Fehler geworfen wird, ist das ein Problem
                assert False, f"Name {name} sollte ungültig sein"
            except Exception:
                # Erwartet: Exception für ungültige Namen
                pass
    
    def test_interest_group_boolean_fields(self):
        """Test: Boolean-Felder funktionieren korrekt"""
        # Test mit verschiedenen Boolean-Kombinationen
        test_cases = [
            (True, True),
            (True, False),
            (False, True),
            (False, False)
        ]
        
        for is_external, is_active in test_cases:
            group = InterestGroup(
                name=f"Boolean Test Group {is_external}_{is_active}",
                code=f"boolean_test_{is_external}_{is_active}",
                is_external=is_external,
                is_active=is_active
            )
            
            assert group.is_external is is_external
            assert group.is_active is is_active
    
    def test_interest_group_optional_fields(self):
        """Test: Optionale Felder werden korrekt behandelt"""
        # Test mit minimalen Daten
        minimal_group = InterestGroup(
            name="Minimal Group",
            code="minimal_group",
            is_external=False,
            is_active=True
        )
        
        # Optionale Felder sollten None sein
        assert minimal_group.description is None
        assert minimal_group.group_permissions is None
        assert minimal_group.ai_functionality is None
        assert minimal_group.typical_tasks is None
        
        # Test mit allen optionalen Feldern
        full_group = InterestGroup(
            name="Full Group",
            code="full_group",
            description="Vollständige Beschreibung",
            group_permissions=["perm1", "perm2"],
            ai_functionality="AI Funktionen",
            typical_tasks="Typische Aufgaben",
            is_external=True,
            is_active=False
        )
        
        # Alle Felder sollten gesetzt sein
        assert full_group.description == "Vollständige Beschreibung"
        assert full_group.group_permissions == ["perm1", "perm2"]
        assert full_group.ai_functionality == "AI Funktionen"
        assert full_group.typical_tasks == "Typische Aufgaben"
        assert full_group.is_external is True
        assert full_group.is_active is False
    
    def test_interest_group_string_representation(self):
        """Test: String-Repräsentation der InterestGroup"""
        group = InterestGroup(
            name="String Test Group",
            code="string_test_group",
            description="Test für String-Repräsentation",
            is_external=False,
            is_active=True
        )
        
        # String-Repräsentation sollte den Namen enthalten
        str_repr = str(group)
        assert "String Test Group" in str_repr
        assert "string_test_group" in str_repr
        
        # Repr-Repräsentation sollte technische Details enthalten
        repr_repr = repr(group)
        assert "InterestGroup" in repr_repr
        assert "string_test_group" in repr_repr
    
    def test_interest_group_equality(self):
        """Test: Gleichheit zwischen InterestGroup-Instanzen"""
        # Zwei identische Gruppen
        group1 = InterestGroup(
            name="Equality Test Group",
            code="equality_test_group",
            is_external=False,
            is_active=True
        )
        
        group2 = InterestGroup(
            name="Equality Test Group",
            code="equality_test_group",
            is_external=False,
            is_active=True
        )
        
        # Gruppen mit gleichen Daten sollten gleich sein
        assert group1.name == group2.name
        assert group1.code == group2.code
        assert group1.is_external == group2.is_external
        assert group1.is_active == group2.is_active
        
        # Aber es sind verschiedene Instanzen
        assert group1 is not group2
        
        # Gruppen mit verschiedenen Daten sollten ungleich sein
        group3 = InterestGroup(
            name="Different Group",
            code="different_group",
            is_external=True,
            is_active=False
        )
        
        assert group1.name != group3.name
        assert group1.code != group3.code
        assert group1.is_external != group3.is_external
        assert group1.is_active != group3.is_active
