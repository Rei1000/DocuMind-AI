"""
Test für Interest Groups Tabellenstruktur
"""

import pytest
import sys
from pathlib import Path

# Import-Pfad für Backend-Database
backend_path = Path("/Users/reiner/Documents/DocuMind-AI/backend")
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from backend.app.database import engine
from sqlalchemy import text

class TestInterestGroupsTableStructure:
    """Test für InterestGroup Tabellenstruktur"""
    
    def test_interest_groups_table_structure(self):
        """Test: Tabellenstruktur entspricht dem erwarteten Schema"""
        with engine.connect() as connection:
            # Hole Tabellenstruktur
            result = connection.execute(text("PRAGMA table_info(interest_groups)"))
            columns = result.fetchall()
            
            # Erwartete Spalten
            expected_columns = {
                'id': {'type': 'INTEGER', 'notnull': 1, 'pk': 1},
                'name': {'type': 'VARCHAR', 'notnull': 1, 'pk': 0},
                'code': {'type': 'VARCHAR', 'notnull': 1, 'pk': 0},
                'description': {'type': 'TEXT', 'notnull': 0, 'pk': 0},
                'group_permissions': {'type': 'TEXT', 'notnull': 0, 'pk': 0},
                'ai_functionality': {'type': 'TEXT', 'notnull': 0, 'pk': 0},
                'typical_tasks': {'type': 'TEXT', 'notnull': 0, 'pk': 0},
                'is_external': {'type': 'BOOLEAN', 'notnull': 1, 'pk': 0},
                'is_active': {'type': 'BOOLEAN', 'notnull': 1, 'pk': 0},
                'created_at': {'type': 'DATETIME', 'notnull': 1, 'pk': 0}
            }
            
            # Prüfe jede erwartete Spalte
            for col_name, expected in expected_columns.items():
                col_found = False
                for col in columns:
                    if col[1] == col_name:
                        col_found = True
                        # Prüfe Typ (flexibler für VARCHAR mit Länge)
                        col_type = col[2].upper()
                        expected_type = expected['type'].upper()
                        if expected_type == 'VARCHAR':
                            assert 'VARCHAR' in col_type, f"Spalte {col_name} hat falschen Typ: {col[2]}"
                        else:
                            assert col_type == expected_type, f"Spalte {col_name} hat falschen Typ: {col[2]}"
                        # Prüfe NOT NULL
                        assert col[3] == expected['notnull'], f"Spalte {col_name} hat falschen NOT NULL Wert: {col[3]}"
                        # Prüfe Primary Key
                        assert col[5] == expected['pk'], f"Spalte {col_name} hat falschen PK Wert: {col[5]}"
                        break
                
                assert col_found, f"Spalte {col_name} fehlt in der Tabelle"
