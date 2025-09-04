import pytest
import sqlite3
import os
from pathlib import Path

class TestDBSanity:
    @pytest.fixture(scope="class")
    def test_db_path(self):
        return Path("/Users/reiner/Documents/DocuMind-AI/.tmp/test_qms_mvp.db")
    
    @pytest.fixture(scope="class")
    def db_connection(self, test_db_path):
        if not test_db_path.exists():
            pytest.fail(f"Test database not found at {test_db_path}")
        
        conn = sqlite3.connect(test_db_path)
        yield conn
        conn.close()
    
    def test_database_connection(self, db_connection):
        """Test basic database connectivity"""
        cursor = db_connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
    
    def test_interest_groups_table_exists(self, db_connection):
        """Test that interest_groups table exists"""
        cursor = db_connection.cursor()
        result = cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='interest_groups'
        """)
        table_exists = result.fetchone() is not None
        assert table_exists, "Tabelle 'interest_groups' existiert nicht"
    
    def test_user_group_memberships_table_exists(self, db_connection):
        """Test that user_group_memberships table exists"""
        cursor = db_connection.cursor()
        result = cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_group_memberships'
        """)
        table_exists = result.fetchone() is not None
        assert table_exists, "Tabelle 'user_group_memberships' existiert nicht"
    
    def test_interest_groups_columns_exist(self, db_connection):
        """Test that required columns exist in interest_groups"""
        cursor = db_connection.cursor()
        cursor.execute("PRAGMA table_info(interest_groups)")
        columns = {row[1] for row in cursor.fetchall()}
        
        required_columns = {"id", "name", "code", "is_active"}
        missing_columns = required_columns - columns
        
        assert not missing_columns, f"Fehlende Spalten in interest_groups: {missing_columns}"
    
    def test_interest_groups_has_data(self, db_connection):
        """Test that interest_groups table has at least one row"""
        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM interest_groups")
        row_count = cursor.fetchone()[0]
        assert row_count > 0, f"Tabelle 'interest_groups' hat keine Daten (Zeilen: {row_count})"
    
    def test_environment_variables_correct(self):
        """Test that the app actually uses the test database"""
        # Check that the test database file exists
        test_db_path = Path("/Users/reiner/Documents/DocuMind-AI/.tmp/test_qms_mvp.db")
        assert test_db_path.exists(), f"Test-DB existiert nicht: {test_db_path}"
        
        # Check that the app's database module uses the test database
        from backend.app.database import DATABASE_URL
        expected_url = f"sqlite:////{str(test_db_path).lstrip('/')}"
        assert DATABASE_URL == expected_url, f"App verwendet nicht die Test-DB: {DATABASE_URL} != {expected_url}"
        
        # Verify the database has the expected tables
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        table_count = cursor.fetchone()[0]
        conn.close()
        
        assert table_count == 4, f"Test-DB hat nicht die erwartete Anzahl Tabellen: {table_count} != 4"
