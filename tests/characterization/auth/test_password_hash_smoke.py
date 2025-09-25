"""
Password Hash Smoke Test
Testet bcrypt-Hashing und Klartext-Schutz
"""

import pytest
import sqlite3
from tests.helpers.ab_runner import run_request
from tests.helpers.seeds_auth import seed_user_with_password
from tests.helpers.password_policy import detect_hash_scheme
from tests.characterization.auth.conftest import before_import_env, after_import_override


class TestPasswordHashSmoke:
    """Smoke-Tests für Password-Hashing"""
    
    def test_bcrypt_hash_scheme_and_no_plaintext(self, client):
        """Testet bcrypt-Schema und Klartext-Schutz"""
        print("Teste Password-Hash Smoke...")
        
        # DB-Isolation sicherstellen
        db_path = "/Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        
        # ENV setzen
        import os
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
        os.environ["SQLALCHEMY_DATABASE_URL"] = f"sqlite:///{db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(db_path) as conn:
            user_id = seed_user_with_password(conn, "smoke@local", "P@ssw0rd!")
            
            # Password-Hash aus DB holen
            cursor = conn.execute("SELECT hashed_password FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            password_hash = result[0] if result else None
            
            # Tabellen für Runtime-Log
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
        
        # Runtime-Log
        print(f"[RUNTIME] engine_url=sqlite:///{db_path} tables_first5={tables[:5]}")
        
        assert password_hash is not None, "Password hash not found in DB"
        
        # Hash-Prefix prüfen
        if not password_hash.startswith("$2"):
            print(f"[HASH-ERROR] Hash-Prefix (maskiert): {password_hash[:10]}...")
            pytest.fail(f"Hash does not start with $2, got: {password_hash[:10]}...")
        
        # Hash-Schema prüfen
        hash_info = detect_hash_scheme(password_hash)
        assert hash_info["scheme"] == "bcrypt", f"Expected bcrypt, got {hash_info['scheme']}"
        assert hash_info["valid"] == True, f"Hash validation failed: {hash_info.get('error', 'unknown')}"
        
        # Klartext-Schutz prüfen (maskiert loggen)
        plaintext = "P@ssw0rd!"
        if plaintext in password_hash:
            print(f"[SECURITY-ERROR] Plaintext found in hash (maskiert): {password_hash[:20]}...")
            pytest.fail("Plaintext password found in hash")
        
        if plaintext in str(password_hash):
            print(f"[SECURITY-ERROR] Plaintext found in hash string (maskiert): {str(password_hash)[:20]}...")
            pytest.fail("Plaintext password found in hash string")
        
        print("✅ bcrypt ok")
        print("✅ no_plaintext ok")
