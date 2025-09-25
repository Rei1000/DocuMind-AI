"""
AccessControl Database Schema Charakterisierungstests
Testet Existenz von Tabellen, Spalten, Indizes mit SQLite-toleranten Checks
"""

import pytest
import sqlite3
from sqlalchemy import text
from tests.helpers.bootstrap_from_schema import make_fresh_db_at


class TestDatabaseSchemaAccessControl:
    """Testet AccessControl-Datenbankschema"""
    
    def test_users_table_structure(self, client):
        """Test: Users-Tabelle Struktur"""
        print("Teste Users-Tabelle Struktur...")
        
        # Frische DB für Schema-Test
        db_path = ".tmp/test_schema_users.db"
        make_fresh_db_at(db_path)
        
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Tabellen-Info abrufen
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        # Erwartete Spalten (SQLite-tolerante Checks)
        expected_columns = {
            'id': {'type': 'INTEGER', 'notnull': 1, 'pk': 1},
            'email': {'type': ['VARCHAR', 'TEXT'], 'notnull': 1, 'pk': 0},
            'full_name': {'type': ['VARCHAR', 'TEXT'], 'notnull': 1, 'pk': 0},
            'employee_id': {'type': ['VARCHAR', 'TEXT'], 'notnull': 0, 'pk': 0},
            'organizational_unit': {'type': ['VARCHAR', 'TEXT'], 'notnull': 0, 'pk': 0},
            'hashed_password': {'type': ['VARCHAR', 'TEXT'], 'notnull': 0, 'pk': 0},
            'individual_permissions': {'type': 'TEXT', 'notnull': 0, 'pk': 0},
            'is_department_head': {'type': ['BOOLEAN', 'INTEGER'], 'notnull': 1, 'pk': 0},
            'approval_level': {'type': 'INTEGER', 'notnull': 0, 'pk': 0},
            'is_active': {'type': ['BOOLEAN', 'INTEGER'], 'notnull': 1, 'pk': 0},
            'created_at': {'type': ['DATETIME', 'TEXT'], 'notnull': 1, 'pk': 0}
        }
        
        # Spalten prüfen
        for col_name, expected in expected_columns.items():
            col_found = False
            for col in columns:
                if col[1] == col_name:
                    col_found = True
                    expected_types = expected['type'] if isinstance(expected['type'], list) else [expected['type']]
                    col_type_upper = col[2].upper()
                    col_type_base = col_type_upper.split('(')[0]  # Remove length specifiers
                    expected_types_base = [t.upper().split('(')[0] for t in expected_types]
                    assert col_type_base in expected_types_base, f"Spalte {col_name} hat falschen Typ: {col[2]} (erwartet: {expected_types})"
                    assert col[3] == expected['notnull'], f"Spalte {col_name} hat falsche NOT NULL: {col[3]} (erwartet: {expected['notnull']})"
                    assert col[5] == expected['pk'], f"Spalte {col_name} hat falsche PK: {col[5]} (erwartet: {expected['pk']})"
                    break
            assert col_found, f"Spalte {col_name} nicht gefunden"
        
        connection.close()
        print(f"\n✅ Users-Tabelle Struktur erfolgreich getestet")
    
    def test_user_group_memberships_table_structure(self, client):
        """Test: User-Group-Memberships-Tabelle Struktur"""
        print("Teste User-Group-Memberships-Tabelle Struktur...")
        
        # Frische DB für Schema-Test
        db_path = ".tmp/test_schema_memberships.db"
        make_fresh_db_at(db_path)
        
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Tabellen-Info abrufen
        cursor.execute("PRAGMA table_info(user_group_memberships)")
        columns = cursor.fetchall()
        
        # Erwartete Spalten (SQLite-tolerante Checks)
        expected_columns = {
            'id': {'type': 'INTEGER', 'notnull': 1, 'pk': 1},
            'user_id': {'type': 'INTEGER', 'notnull': 1, 'pk': 0},
            'interest_group_id': {'type': 'INTEGER', 'notnull': 1, 'pk': 0},
            'role_in_group': {'type': ['VARCHAR', 'TEXT'], 'notnull': 0, 'pk': 0},
            'approval_level': {'type': 'INTEGER', 'notnull': 1, 'pk': 0},
            'is_department_head': {'type': ['BOOLEAN', 'INTEGER'], 'notnull': 1, 'pk': 0},
            'is_active': {'type': ['BOOLEAN', 'INTEGER'], 'notnull': 1, 'pk': 0},
            'joined_at': {'type': ['DATETIME', 'TEXT'], 'notnull': 1, 'pk': 0},
            'assigned_by_id': {'type': 'INTEGER', 'notnull': 0, 'pk': 0},
            'notes': {'type': 'TEXT', 'notnull': 0, 'pk': 0}
        }
        
        # Spalten prüfen
        for col_name, expected in expected_columns.items():
            col_found = False
            for col in columns:
                if col[1] == col_name:
                    col_found = True
                    expected_types = expected['type'] if isinstance(expected['type'], list) else [expected['type']]
                    col_type_upper = col[2].upper()
                    col_type_base = col_type_upper.split('(')[0]  # Remove length specifiers
                    expected_types_base = [t.upper().split('(')[0] for t in expected_types]
                    assert col_type_base in expected_types_base, f"Spalte {col_name} hat falschen Typ: {col[2]} (erwartet: {expected_types})"
                    assert col[3] == expected['notnull'], f"Spalte {col_name} hat falsche NOT NULL: {col[3]} (erwartet: {expected['notnull']})"
                    assert col[5] == expected['pk'], f"Spalte {col_name} hat falsche PK: {col[5]} (erwartet: {expected['pk']})"
                    break
            assert col_found, f"Spalte {col_name} nicht gefunden"
        
        connection.close()
        print(f"\n✅ User-Group-Memberships-Tabelle Struktur erfolgreich getestet")
    
    def test_accesscontrol_unique_constraints(self, client):
        """Test: AccessControl Unique Constraints"""
        print("Teste AccessControl Unique Constraints...")
        
        # Frische DB für Schema-Test
        db_path = ".tmp/test_schema_constraints.db"
        make_fresh_db_at(db_path)
        
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Unique-Indizes abrufen
        cursor.execute("PRAGMA index_list(users)")
        user_indexes = cursor.fetchall()
        
        cursor.execute("PRAGMA index_list(user_group_memberships)")
        membership_indexes = cursor.fetchall()
        
        # Unique-Index-Namen (tolerante Checks)
        user_unique_indexes = [idx[1] for idx in user_indexes if idx[2] == 1]  # unique = 1
        membership_unique_indexes = [idx[1] for idx in membership_indexes if idx[2] == 1]
        
        # Users: Email und Employee-ID müssen unique sein
        email_unique = any('email' in idx.lower() for idx in user_unique_indexes)
        employee_id_unique = any('employee_id' in idx.lower() for idx in user_unique_indexes)
        
        assert email_unique, f"Email-Index ist nicht unique. Gefundene Unique-Indizes: {user_unique_indexes}"
        assert employee_id_unique, f"Employee-ID-Index ist nicht unique. Gefundene Unique-Indizes: {user_unique_indexes}"
        
        # Memberships: User-Group-Kombination sollte unique sein (falls implementiert)
        # Dies ist optional, da ein User mehrere Rollen in derselben Gruppe haben könnte
        
        connection.close()
        print(f"\n✅ AccessControl Unique Constraints erfolgreich getestet")
    
    def test_accesscontrol_foreign_keys(self, client):
        """Test: AccessControl Foreign Keys"""
        print("Teste AccessControl Foreign Keys...")
        
        # Frische DB für Schema-Test
        db_path = ".tmp/test_schema_fks.db"
        make_fresh_db_at(db_path)
        
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Foreign Key Info abrufen
        cursor.execute("PRAGMA foreign_key_list(user_group_memberships)")
        fk_info = cursor.fetchall()
        
        # Erwartete Foreign Keys
        expected_fks = [
            ('user_id', 'users', 'id'),
            ('interest_group_id', 'interest_groups', 'id'),
            ('assigned_by_id', 'users', 'id')
        ]
        
        # Foreign Keys prüfen
        found_fks = []
        for fk in fk_info:
            found_fks.append((fk[3], fk[2], fk[4]))  # (column, table, ref_column)
        
        for expected_fk in expected_fks:
            assert expected_fk in found_fks, f"Foreign Key {expected_fk} nicht gefunden. Gefundene FKs: {found_fks}"
        
        connection.close()
        print(f"\n✅ AccessControl Foreign Keys erfolgreich getestet")
    
    def test_accesscontrol_table_size(self, client):
        """Test: AccessControl Tabellen-Größe"""
        print("Teste AccessControl Tabellen-Größe...")
        
        # Frische DB für Schema-Test
        db_path = ".tmp/test_schema_size.db"
        make_fresh_db_at(db_path)
        
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Tabellen-Größen prüfen
        tables = ['users', 'interest_groups', 'user_group_memberships']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            assert count >= 1, f"Tabelle {table} sollte mindestens 1 Eintrag haben, hat aber {count}"
        
        connection.close()
        print(f"\n✅ AccessControl Tabellen-Größe erfolgreich getestet")
    
    def test_accesscontrol_data_types(self, client):
        """Test: AccessControl Datentypen"""
        print("Teste AccessControl Datentypen...")
        
        # Frische DB für Schema-Test
        db_path = ".tmp/test_schema_types.db"
        make_fresh_db_at(db_path)
        
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Test-Daten einfügen
        import time
        unique_email = f"test_schema_user_{int(time.time())}@company.com"
        unique_employee_id = f"TEST_{int(time.time())}"
        
        cursor.execute("""
            INSERT INTO users (email, full_name, employee_id, organizational_unit, 
                             individual_permissions, is_department_head, approval_level, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            unique_email, "Test Schema User", unique_employee_id, "Test Department",
            '["test_permission"]', 0, 1, 1
        ))
        connection.commit()
        
        # Daten abrufen und Typen prüfen
        cursor.execute("SELECT * FROM users WHERE email = ?", (unique_email,))
        row = cursor.fetchone()
        
        # Typen prüfen (SQLite-spezifisch)
        assert isinstance(row[0], int), f"ID sollte Integer sein, ist {type(row[0])}"
        assert isinstance(row[1], str), f"Email sollte String sein, ist {type(row[1])}"
        assert isinstance(row[2], str), f"Full Name sollte String sein, ist {type(row[2])}"
        assert isinstance(row[3], str), f"Employee ID sollte String sein, ist {type(row[3])}"
        assert isinstance(row[4], str), f"Organizational Unit sollte String sein, ist {type(row[4])}"
        assert isinstance(row[5], str), f"Hashed Password sollte String sein, ist {type(row[5])}"
        assert isinstance(row[6], str), f"Individual Permissions sollte String sein, ist {type(row[6])}"
        assert isinstance(row[7], int), f"is_department_head sollte Integer sein (SQLite BOOLEAN), ist {type(row[7])}"
        assert isinstance(row[8], int), f"approval_level sollte Integer sein, ist {type(row[8])}"
        assert isinstance(row[9], int), f"is_active sollte Integer sein (SQLite BOOLEAN), ist {type(row[9])}"
        assert isinstance(row[10], str), f"created_at sollte String sein (SQLite DATETIME), ist {type(row[10])}"
        
        # Cleanup
        cursor.execute("DELETE FROM users WHERE email = ?", (unique_email,))
        connection.commit()
        connection.close()
        
        print(f"\n✅ AccessControl Datentypen erfolgreich getestet")
    
    def test_accesscontrol_constraints_enforcement(self, client):
        """Test: AccessControl Constraints Enforcement"""
        print("Teste AccessControl Constraints Enforcement...")
        
        # Frische DB für Schema-Test
        db_path = ".tmp/test_schema_constraints_enforcement.db"
        make_fresh_db_at(db_path)
        
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Test 1: Unique Email Constraint
        import time
        unique_email = f"unique_test_email_{int(time.time())}@company.com"
        
        # Ersten User einfügen
        cursor.execute("""
            INSERT INTO users (email, full_name, is_department_head, is_active)
            VALUES (?, ?, ?, ?)
        """, (unique_email, "First User", 0, 1))
        connection.commit()
        
        # Zweiten User mit gleicher Email (sollte fehlschlagen)
        try:
            cursor.execute("""
                INSERT INTO users (email, full_name, is_department_head, is_active)
                VALUES (?, ?, ?, ?)
            """, (unique_email, "Second User", 0, 1))
            connection.commit()
            assert False, "Unique Email Constraint wurde nicht durchgesetzt"
        except sqlite3.IntegrityError:
            # Erwarteter Fehler
            pass
        
        # Test 2: Unique Employee ID Constraint
        unique_employee_id = f"EMP_{int(time.time())}"
        
        # Ersten User mit Employee ID einfügen
        cursor.execute("""
            INSERT INTO users (email, full_name, employee_id, is_department_head, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (f"user1_{int(time.time())}@company.com", "User 1", unique_employee_id, 0, 1))
        connection.commit()
        
        # Zweiten User mit gleicher Employee ID (sollte fehlschlagen)
        try:
            cursor.execute("""
                INSERT INTO users (email, full_name, employee_id, is_department_head, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, (f"user2_{int(time.time())}@company.com", "User 2", unique_employee_id, 0, 1))
            connection.commit()
            assert False, "Unique Employee ID Constraint wurde nicht durchgesetzt"
        except sqlite3.IntegrityError:
            # Erwarteter Fehler
            pass
        
        # Cleanup
        cursor.execute("DELETE FROM users WHERE email LIKE ?", (f"%{int(time.time())}%",))
        connection.commit()
        connection.close()
        
        print(f"\n✅ AccessControl Constraints Enforcement erfolgreich getestet")

