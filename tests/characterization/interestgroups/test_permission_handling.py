"""
Charakterisierungstest für Permission Handling in Interest Groups
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

class TestPermissionHandling:
    """Test für Permission Handling und Validierung"""
    
    def test_permission_parsing_json_string(self):
        """Test: JSON-String Permissions werden korrekt geparst"""
        # Test mit gültigem JSON
        group = InterestGroup(
            name="JSON Permissions Test",
            code="json_permissions_test",
            group_permissions='["read", "write", "delete"]',
            is_external=False,
            is_active=True
        )
        
        permissions = group.get_group_permissions_list()
        assert permissions == ["read", "write", "delete"]
        
        # Test mit leeren JSON-Array
        group.group_permissions = "[]"
        permissions = group.get_group_permissions_list()
        assert permissions == []
        
        # Test mit JSON-Array mit einem Element
        group.group_permissions = '["single_permission"]'
        permissions = group.get_group_permissions_list()
        assert permissions == ["single_permission"]
    
    def test_permission_parsing_comma_separated(self):
        """Test: Komma-separierte Permissions werden korrekt geparst"""
        # Test mit einfachen Komma-separierten Strings
        group = InterestGroup(
            name="Comma Permissions Test",
            code="comma_permissions_test",
            group_permissions="read, write, delete",
            is_external=False,
            is_active=True
        )
        
        permissions = group.get_group_permissions_list()
        assert permissions == ["read", "write", "delete"]
        
        # Test mit Leerzeichen um Kommas
        group.group_permissions = "read,write,delete"
        permissions = group.get_group_permissions_list()
        assert permissions == ["read", "write", "delete"]
        
        # Test mit gemischten Leerzeichen
        group.group_permissions = "read , write , delete"
        permissions = group.get_group_permissions_list()
        assert permissions == ["read", "write", "delete"]
    
    def test_permission_parsing_list_input(self):
        """Test: Listen-Input wird korrekt behandelt"""
        # Test mit Liste von Strings
        group = InterestGroup(
            name="List Permissions Test",
            code="list_permissions_test",
            group_permissions=["create", "read", "update", "delete"],
            is_external=False,
            is_active=True
        )
        
        permissions = group.get_group_permissions_list()
        assert permissions == ["create", "read", "update", "delete"]
        
        # Test mit leere Liste
        group.group_permissions = []
        permissions = group.get_group_permissions_list()
        assert permissions == []
        
        # Test mit Liste mit einem Element
        group.group_permissions = ["single"]
        permissions = group.get_group_permissions_list()
        assert permissions == ["single"]
    
    def test_permission_parsing_edge_cases(self):
        """Test: Edge Cases werden korrekt behandelt"""
        group = InterestGroup(
            name="Edge Cases Test",
            code="edge_cases_test",
            is_external=False,
            is_active=True
        )
        
        # Test mit None
        group.group_permissions = None
        permissions = group.get_group_permissions_list()
        assert permissions == []
        
        # Test mit leerem String
        group.group_permissions = ""
        permissions = group.get_group_permissions_list()
        assert permissions == []
        
        # Test mit String nur aus Leerzeichen
        group.group_permissions = "   "
        permissions = group.get_group_permissions_list()
        assert permissions == []
        
        # Test mit String nur aus Kommas
        group.group_permissions = ",,"
        permissions = group.get_group_permissions_list()
        assert permissions == ["", ""]
    
    def test_permission_parsing_malformed_input(self):
        """Test: Fehlerhafte Eingaben werden graceful behandelt"""
        group = InterestGroup(
            name="Malformed Input Test",
            code="malformed_input_test",
            is_external=False,
            is_active=True
        )
        
        # Test mit ungültigem JSON
        group.group_permissions = '{"invalid": json}'
        permissions = group.get_group_permissions_list()
        # Bestehendes Verhalten: Graceful Fallback zu leerer Liste
        assert permissions == []
        
        # Test mit gemischtem Format
        group.group_permissions = '["valid", invalid, "valid"]'
        permissions = group.get_group_permissions_list()
        # Bestehendes Verhalten: Graceful Fallback zu leerer Liste
        assert permissions == []
        
        # Test mit unerwarteten Datentypen
        group.group_permissions = 123
        permissions = group.get_group_permissions_list()
        # Bestehendes Verhalten: Graceful Fallback zu leerer Liste
        assert permissions == []
        
        group.group_permissions = True
        permissions = group.get_group_permissions_list()
        # Bestehendes Verhalten: Graceful Fallback zu leerer Liste
        assert permissions == []
    
    def test_permission_parsing_complex_scenarios(self):
        """Test: Komplexe Szenarien werden korrekt behandelt"""
        group = InterestGroup(
            name="Complex Scenarios Test",
            code="complex_scenarios_test",
            is_external=False,
            is_active=True
        )
        
        # Test mit gemischten Formaten (sollte JSON bevorzugen)
        group.group_permissions = '["json_permission"]'
        permissions = group.get_group_permissions_list()
        assert permissions == ["json_permission"]
        
        # Test mit Permissions die Leerzeichen enthalten
        group.group_permissions = "user management, role management, data access"
        permissions = group.get_group_permissions_list()
        assert permissions == ["user management", "role management", "data access"]
        
        # Test mit Permissions die Sonderzeichen enthalten
        group.group_permissions = "read:users, write:users, delete:users"
        permissions = group.get_group_permissions_list()
        assert permissions == ["read:users", "write:users", "delete:users"]
    
    def test_permission_consistency(self):
        """Test: Permission-Parsing ist konsistent"""
        group = InterestGroup(
            name="Consistency Test",
            code="consistency_test",
            is_external=False,
            is_active=True
        )
        
        # Gleiche Permissions in verschiedenen Formaten sollten gleiche Ergebnisse liefern
        test_permissions = ["read", "write", "delete"]
        
        # Als Liste
        group.group_permissions = test_permissions
        list_result = group.get_group_permissions_list()
        
        # Als JSON-String
        group.group_permissions = str(test_permissions).replace("'", '"')
        json_result = group.get_group_permissions_list()
        
        # Als Komma-separierte Strings
        group.group_permissions = ", ".join(test_permissions)
        comma_result = group.get_group_permissions_list()
        
        # Alle Ergebnisse sollten identisch sein
        assert list_result == test_permissions
        assert json_result == test_permissions
        assert comma_result == test_permissions
    
    def test_permission_immutability(self):
        """Test: Permissions sind nicht veränderbar nach dem Parsen"""
        group = InterestGroup(
            name="Immutability Test",
            code="immutability_test",
            group_permissions='["original_perm1", "original_perm2"]',
            is_external=False,
            is_active=True
        )
        
        # Erste Abfrage
        permissions1 = group.get_group_permissions_list()
        assert permissions1 == ["original_perm1", "original_perm2"]
        
        # Permissions ändern
        group.group_permissions = '["new_perm1", "new_perm2"]'
        
        # Zweite Abfrage sollte neue Permissions zurückgeben
        permissions2 = group.get_group_permissions_list()
        assert permissions2 == ["new_perm1", "new_perm2"]
        
        # Erste Abfrage sollte unverändert bleiben
        assert permissions1 == ["original_perm1", "original_perm2"]
    
    def test_permission_performance(self):
        """Test: Permission-Parsing ist performant"""
        group = InterestGroup(
            name="Performance Test",
            code="performance_test",
            is_external=False,
            is_active=True
        )
        
        # Test mit vielen Permissions
        many_permissions = [f"permission_{i}" for i in range(100)]
        
        # Als Liste
        group.group_permissions = many_permissions
        start_time = pytest.importorskip("time").time()
        permissions = group.get_group_permissions_list()
        end_time = pytest.importorskip("time").time()
        
        assert permissions == many_permissions
        # Parsing sollte unter 1ms dauern
        assert (end_time - start_time) < 0.001
        
        # Als JSON-String
        group.group_permissions = str(many_permissions).replace("'", '"')
        start_time = pytest.importorskip("time").time()
        permissions = group.get_group_permissions_list()
        end_time = pytest.importorskip("time").time()
        
        assert permissions == many_permissions
        # JSON-Parsing sollte unter 1ms dauern
        assert (end_time - start_time) < 0.001
