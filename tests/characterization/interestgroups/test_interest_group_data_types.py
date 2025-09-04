"""
Test für Interest Group Datentypen
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

class TestInterestGroupDataTypes:
    """Test für InterestGroup Datentypen"""
    
    def test_interest_group_data_types(self):
        """Test: Datentypen sind korrekt implementiert"""
        with engine.connect() as connection:
            # Erstelle eine Test-Gruppe (mit eindeutigem Code)
            import time
            unique_code = f"test_schema_group_{int(time.time())}"
            test_data = {
                'name': f'Test Group for Schema {int(time.time())}',  # Eindeutiger Name
                'code': unique_code,
                'description': 'Test-Beschreibung',
                'group_permissions': '["test_perm1", "test_perm2"]',
                'ai_functionality': 'Test AI Funktionen',
                'typical_tasks': 'Test-Aufgaben',
                'is_external': False,
                'is_active': True
            }
            
            # Insert über SQL um Datentypen zu testen
            insert_sql = """
                INSERT INTO interest_groups 
                (name, code, description, group_permissions, ai_functionality, typical_tasks, is_external, is_active)
                VALUES (:name, :code, :description, :group_permissions, :ai_functionality, :typical_tasks, :is_external, :is_active)
            """
            
            connection.execute(text(insert_sql), test_data)
            connection.commit()
            
            # Hole die eingefügten Daten zurück
            result = connection.execute(text("""
                SELECT * FROM interest_groups WHERE code = :code
            """), {"code": unique_code})
            row = result.fetchone()
            
            assert row is not None, "Test-Daten wurden nicht eingefügt"
            
            # Prüfe Datentypen
            assert isinstance(row[1], str), f"name sollte String sein, ist {type(row[1])}"
            assert isinstance(row[2], str), f"code sollte String sein, ist {type(row[2])}"
            assert isinstance(row[3], str) or row[3] is None, f"description sollte String oder None sein, ist {type(row[3])}"
            assert isinstance(row[4], str) or row[4] is None, f"group_permissions sollte String oder None sein, ist {type(row[4])}"
            assert isinstance(row[5], str) or row[5] is None, f"ai_functionality sollte String oder None sein, ist {type(row[5])}"
            assert isinstance(row[6], str) or row[6] is None, f"typical_tasks sollte String oder None sein, ist {type(row[6])}"
            
            # SQLite speichert BOOLEAN als INTEGER (0/1), daher prüfen wir auf int
            assert isinstance(row[7], int), f"is_external sollte Integer sein (SQLite BOOLEAN), ist {type(row[7])}"
            assert isinstance(row[8], int), f"is_active sollte Integer sein (SQLite BOOLEAN), ist {type(row[8])}"
            assert isinstance(row[9], str), f"created_at sollte String sein, ist {type(row[9])}"
            
            # Prüfe Boolean-Werte (0/1)
            assert row[7] in [0, 1], f"is_external sollte 0 oder 1 sein, ist {row[7]}"
            assert row[8] in [0, 1], f"is_active sollte 0 oder 1 sein, ist {row[8]}"
            
            # Cleanup
            connection.execute(text("DELETE FROM interest_groups WHERE code = :code"), {"code": unique_code})
            connection.commit()
