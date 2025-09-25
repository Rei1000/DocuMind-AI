"""
DB Binding Diagnostics Test
Testet ob die users-Tabelle zur Laufzeit verfügbar ist
"""

import pytest
import os
import sqlite3
from tests.helpers.ab_runner import run_request
from tests.characterization.auth.conftest import before_import_env, after_import_override


class TestDbBindingDiagnostics:
    """Testet DB-Binding für Auth-Tests"""
    
    def test_legacy_db_binding_has_users_table(self, client):
        """Testet Legacy DB-Binding - users-Tabelle vorhanden"""
        print("Teste Legacy DB-Binding...")
        
        try:
            # Einfacher Request um DB-Binding zu testen
            response = run_request(
                client, "legacy", "GET", "/api/health",
                before_import_env=before_import_env,
                after_import_override=after_import_override
            )
            
            # Prüfe ob users-Tabelle in der DB vorhanden ist
            db_path = "/Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            print(f"[DIAGNOSTICS] Legacy tables: {tables[:10]}")
            assert 'users' in tables, f"users table not found in Legacy DB. Available tables: {tables[:10]}"
            
        except Exception as e:
            print(f"[DIAGNOSTICS] Legacy binding failed: {e}")
            # Bei Fehlschlag: detaillierte Diagnose
            try:
                db_path = "/Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                print(f"[DIAGNOSTICS] Available tables: {tables[:10]}")
                print(f"[DIAGNOSTICS] ENV DATABASE_URL: {os.environ.get('DATABASE_URL')}")
                print(f"[DIAGNOSTICS] ENV SQLALCHEMY_DATABASE_URL: {os.environ.get('SQLALCHEMY_DATABASE_URL')}")
                
            except Exception as diag_e:
                print(f"[DIAGNOSTICS] Diagnosis failed: {diag_e}")
            
            raise
    
    def test_ddd_db_binding_has_users_table(self, client):
        """Testet DDD DB-Binding - users-Tabelle vorhanden"""
        print("Teste DDD DB-Binding...")
        
        try:
            # Einfacher Request um DB-Binding zu testen
            response = run_request(
                client, "ddd", "GET", "/api/health",
                before_import_env=before_import_env,
                after_import_override=after_import_override
            )
            
            # Prüfe ob users-Tabelle in der DB vorhanden ist
            db_path = "/Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            print(f"[DIAGNOSTICS] DDD tables: {tables[:10]}")
            assert 'users' in tables, f"users table not found in DDD DB. Available tables: {tables[:10]}"
            
        except Exception as e:
            print(f"[DIAGNOSTICS] DDD binding failed: {e}")
            # Bei Fehlschlag: detaillierte Diagnose
            try:
                db_path = "/Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                print(f"[DIAGNOSTICS] Available tables: {tables[:10]}")
                print(f"[DIAGNOSTICS] ENV DATABASE_URL: {os.environ.get('DATABASE_URL')}")
                print(f"[DIAGNOSTICS] ENV SQLALCHEMY_DATABASE_URL: {os.environ.get('SQLALCHEMY_DATABASE_URL')}")
                
            except Exception as diag_e:
                print(f"[DIAGNOSTICS] Diagnosis failed: {diag_e}")
            
            raise
