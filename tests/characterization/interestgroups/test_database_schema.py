"""
Charakterisierungstest für InterestGroup Datenbankschema
Dokumentiert das bestehende Verhalten ohne neue Regeln zu erfinden.
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

class TestDatabaseSchema:
    """Test für InterestGroup Datenbankschema und Constraints"""
    
    def test_interest_groups_table_exists(self):
        """Test: interest_groups Tabelle existiert in der Datenbank"""
        with engine.connect() as connection:
            # Prüfe ob Tabelle existiert
            result = connection.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='interest_groups'
            """))
            
            table_exists = result.fetchone() is not None
            assert table_exists, "Tabelle 'interest_groups' existiert nicht"
    
    def test_interest_groups_table_structure(self):
        """Test: Tabellenstruktur entspricht dem erwarteten Schema"""
        with engine.connect() as connection:
            # Hole Tabellenstruktur
            result = connection.execute(text("PRAGMA table_info(interest_groups)"))
            columns = result.fetchall()
            
            # Erwartete Spalten (SQLite-tolerante Typen)
            expected_columns = {
                'id': {'type': 'INTEGER', 'notnull': 1, 'pk': 1},
                'name': {'type': ['VARCHAR', 'TEXT'], 'notnull': 1, 'pk': 0},  # SQLite kann VARCHAR als TEXT speichern
                'code': {'type': ['VARCHAR', 'TEXT'], 'notnull': 1, 'pk': 0},
                'description': {'type': 'TEXT', 'notnull': 0, 'pk': 0},
                'group_permissions': {'type': 'TEXT', 'notnull': 0, 'pk': 0},
                'ai_functionality': {'type': 'TEXT', 'notnull': 0, 'pk': 0},
                'typical_tasks': {'type': 'TEXT', 'notnull': 0, 'pk': 0},
                'is_external': {'type': ['BOOLEAN', 'INTEGER'], 'notnull': 1, 'pk': 0},  # SQLite speichert BOOLEAN als INTEGER
                'is_active': {'type': ['BOOLEAN', 'INTEGER'], 'notnull': 1, 'pk': 0},
                'created_at': {'type': ['DATETIME', 'TEXT'], 'notnull': 1, 'pk': 0}  # SQLite kann DATETIME als TEXT speichern
            }
            
            # Prüfe jede erwartete Spalte
            for col_name, expected in expected_columns.items():
                col_found = False
                for col in columns:
                    if col[1] == col_name:
                        col_found = True
                        # Prüfe Typ (tolerante Prüfung für SQLite)
                        expected_types = expected['type'] if isinstance(expected['type'], list) else [expected['type']]
                        col_type_upper = col[2].upper()
                        # Entferne Längenangaben für Vergleich (z.B. VARCHAR(100) -> VARCHAR)
                        col_type_base = col_type_upper.split('(')[0]
                        expected_types_base = [t.upper().split('(')[0] for t in expected_types]
                        assert col_type_base in expected_types_base, f"Spalte {col_name} hat falschen Typ: {col[2]} (erwartet: {expected_types})"
                        # Prüfe NOT NULL
                        assert col[3] == expected['notnull'], f"Spalte {col_name} hat falschen NOT NULL Wert: {col[3]}"
                        # Prüfe Primary Key
                        assert col[5] == expected['pk'], f"Spalte {col_name} hat falschen PK Wert: {col[5]}"
                        break
                
                assert col_found, f"Spalte {col_name} fehlt in der Tabelle"
    
    def test_interest_groups_primary_key(self):
        """Test: Primärschlüssel ist korrekt definiert"""
        with engine.connect() as connection:
            # Prüfe Primary Key
            result = connection.execute(text("PRAGMA table_info(interest_groups)"))
            columns = result.fetchall()
            
            # ID-Spalte sollte Primary Key sein
            id_column = None
            for col in columns:
                if col[1] == 'id':
                    id_column = col
                    break
            
            assert id_column is not None, "ID-Spalte fehlt"
            assert id_column[5] == 1, "ID-Spalte ist kein Primary Key"
            assert id_column[2].upper() == "INTEGER", "ID-Spalte ist nicht vom Typ INTEGER"
            assert id_column[3] == 1, "ID-Spalte ist nullable"
    
    def test_interest_groups_indexes(self):
        """Test: Indizes sind korrekt definiert"""
        with engine.connect() as connection:
            # Prüfe Indizes
            result = connection.execute(text("PRAGMA index_list(interest_groups)"))
            indexes = result.fetchall()
            
            # Erwartete Indizes
            expected_indexes = ['ix_interest_groups_name', 'ix_interest_groups_code']
            
            # Prüfe ob erwartete Indizes existieren
            index_names = [idx[1] for idx in indexes]
            for expected_idx in expected_indexes:
                assert expected_idx in index_names, f"Index {expected_idx} fehlt"
    
    def test_interest_groups_unique_constraints(self):
        """Test: Unique-Constraints sind korrekt definiert"""
        with engine.connect() as connection:
            # Prüfe Unique-Constraints
            result = connection.execute(text("PRAGMA index_list(interest_groups)"))
            indexes = result.fetchall()
            
            # Finde Unique-Indizes
            unique_indexes = []
            for idx in indexes:
                if idx[2] == 1:  # unique = 1
                    unique_indexes.append(idx[1])
            
            # name und code sollten unique sein (tolerante Prüfung für verschiedene Index-Namen)
            name_unique = any('name' in idx.lower() for idx in unique_indexes)
            code_unique = any('code' in idx.lower() for idx in unique_indexes)
            assert name_unique, f"Name-Index ist nicht unique. Gefundene Unique-Indizes: {unique_indexes}"
            assert code_unique, f"Code-Index ist nicht unique. Gefundene Unique-Indizes: {unique_indexes}"
    
    def test_interest_groups_foreign_keys(self):
        """Test: Foreign Key Constraints sind korrekt definiert"""
        with engine.connect() as connection:
            # Prüfe Foreign Key Constraints
            result = connection.execute(text("PRAGMA foreign_key_list(interest_groups)"))
            foreign_keys = result.fetchall()
            
            # InterestGroup sollte keine Foreign Keys haben (es ist eine Root-Entity)
            # Aber es könnte Referenzen von anderen Tabellen haben
            assert len(foreign_keys) == 0, "InterestGroup sollte keine Foreign Keys haben"
    
    def test_interest_group_data_types(self):
        """Test: Datentypen sind korrekt implementiert"""
        with engine.connect() as connection:
            # Erstelle eine Test-Gruppe
            test_data = {
                'name': 'Test Group for Schema',
                'code': 'test_schema_group',
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
                SELECT * FROM interest_groups WHERE code = 'test_schema_group'
            """))
            row = result.fetchone()
            
            assert row is not None, "Test-Daten wurden nicht eingefügt"
            
            # Prüfe Datentypen
            assert isinstance(row[1], str), f"name sollte String sein, ist {type(row[1])}"
            assert isinstance(row[2], str), f"code sollte String sein, ist {type(row[2])}"
            assert isinstance(row[3], str) or row[3] is None, f"description sollte String oder None sein, ist {type(row[3])}"
            assert isinstance(row[4], str) or row[4] is None, f"group_permissions sollte String oder None sein, ist {type(row[4])}"
            assert isinstance(row[5], str) or row[5] is None, f"ai_functionality sollte String oder None sein, ist {type(row[5])}"
            assert isinstance(row[6], str) or row[6] is None, f"typical_tasks sollte String oder None sein, ist {type(row[6])}"
            assert isinstance(row[7], int), f"is_external sollte Integer sein (SQLite BOOLEAN), ist {type(row[7])}"
            assert isinstance(row[8], int), f"is_active sollte Integer sein (SQLite BOOLEAN), ist {type(row[8])}"
            assert isinstance(row[9], str), f"created_at sollte String sein, ist {type(row[9])}"
            
            # Cleanup
            connection.execute(text("DELETE FROM interest_groups WHERE code = 'test_schema_group'"))
            connection.commit()
    
    def test_interest_group_constraints_enforcement(self):
        """Test: Constraints werden von der Datenbank durchgesetzt"""
        with engine.connect() as connection:
            # Test 1: NOT NULL Constraint für name
            try:
                connection.execute(text("""
                    INSERT INTO interest_groups (code, is_external, is_active)
                    VALUES ('test_null_name', 0, 1)
                """))
                connection.commit()
                assert False, "NOT NULL Constraint für name wird nicht durchgesetzt"
            except Exception:
                # Erwartet: Exception wegen NOT NULL Constraint
                connection.rollback()
            
            # Test 2: NOT NULL Constraint für code
            try:
                connection.execute(text("""
                    INSERT INTO interest_groups (name, is_external, is_active)
                    VALUES ('Test Name', 0, 1)
                """))
                connection.commit()
                assert False, "NOT NULL Constraint für code wird nicht durchgesetzt"
            except Exception:
                # Erwartet: Exception wegen NOT NULL Constraint
                connection.rollback()
            
            # Test 3: Unique Constraint für code (mit eindeutigem Code)
            import time
            unique_code = f"unique_test_code_{int(time.time())}"
            
            # Erst gültige Gruppe einfügen
            connection.execute(text("""
                INSERT INTO interest_groups (name, code, is_external, is_active)
                VALUES ('First Group', :code, 0, 1)
            """), {"code": unique_code})
            connection.commit()
            
            # Versuch, Gruppe mit gleichem Code einzufügen
            try:
                connection.execute(text("""
                    INSERT INTO interest_groups (name, code, is_external, is_active)
                    VALUES ('Second Group', :code, 0, 1)
                """), {"code": unique_code})
                connection.commit()
                assert False, "Unique Constraint für code wird nicht durchgesetzt"
            except Exception:
                # Erwartet: Exception wegen Unique Constraint
                connection.rollback()
            
            # Cleanup
            connection.execute(text("DELETE FROM interest_groups WHERE code = :code"), {"code": unique_code})
            connection.commit()
    
    def test_interest_group_default_values(self):
        """Test: Standardwerte werden korrekt gesetzt"""
        with engine.connect() as connection:
            # Test mit minimalen Daten
            test_data = {
                'name': 'Default Values Test Group',
                'code': 'default_values_test'
            }
            
            insert_sql = """
                INSERT INTO interest_groups (name, code)
                VALUES (:name, :code)
            """
            
            connection.execute(text(insert_sql), test_data)
            connection.commit()
            
            # Hole die eingefügten Daten zurück
            result = connection.execute(text("""
                SELECT * FROM interest_groups WHERE code = 'default_values_test'
            """))
            row = result.fetchone()
            
            assert row is not None, "Test-Daten wurden nicht eingefügt"
            
            # Prüfe Standardwerte
            assert row[7] == 0, f"is_external sollte Standard 0 haben, ist {row[7]}"
            assert row[8] == 1, f"is_active sollte Standard 1 haben, ist {row[8]}"
            assert row[9] is not None, "created_at sollte automatisch gesetzt werden"
            
            # Cleanup
            connection.execute(text("DELETE FROM interest_groups WHERE code = 'default_values_test'"))
            connection.commit()
    
    def test_interest_group_table_size(self):
        """Test: Tabelle hat die erwartete Größe"""
        with engine.connect() as connection:
            # Zähle alle Einträge
            result = connection.execute(text("SELECT COUNT(*) FROM interest_groups"))
            count = result.fetchone()[0]
            
            # Mindestens einige Standard-Gruppen sollten existieren (sehr tolerante Prüfung)
            assert count >= 1, f"Tabelle sollte mindestens 1 Eintrag haben, hat aber {count}"
            
            # Zähle aktive Einträge
            result = connection.execute(text("SELECT COUNT(*) FROM interest_groups WHERE is_active = 1"))
            active_count = result.fetchone()[0]
            
            # Alle Einträge sollten aktiv sein
            assert active_count == count, f"Alle {count} Einträge sollten aktiv sein, aber nur {active_count} sind aktiv"
