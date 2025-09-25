"""
Password Security Smoke Tests
Quick checks für Passwort-Sicherheit (keine Klartext-Logs, Hash-Länge, etc.)
"""

import pytest
import os
import uuid
import sqlite3
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from tests.helpers.seeds_auth import seed_auth_test_users, get_user_password_hash
from tests.helpers.password_policy import detect_hash_scheme, validate_password_complexity, is_common_password


class TestPasswordSecuritySmoke:
    """Testet Password Security Smoke Checks"""
    
    def test_password_hash_security_parity(self, client):
        """Test: Keine Klartext-Passwörter in Logs, Hash-Länge plausibel, Scheme erkennbar"""
        print("Teste Password Hash Security Parität...")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_password_security_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_password_security_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            users = seed_auth_test_users(conn)
        
        with sqlite3.connect(ddd_db_path) as conn:
            users = seed_auth_test_users(conn)
        
        # Hash-Sicherheit prüfen
        legacy_hashes = []
        ddd_hashes = []
        
        for user_type, user_id in users.items():
            # Legacy Hash
            with sqlite3.connect(legacy_db_path) as conn:
                legacy_hash = get_user_password_hash(conn, user_id)
                if legacy_hash:
                    legacy_hashes.append(legacy_hash)
            
            # DDD Hash
            with sqlite3.connect(ddd_db_path) as conn:
                ddd_hash = get_user_password_hash(conn, user_id)
                if ddd_hash:
                    ddd_hashes.append(ddd_hash)
        
        # Hash-Schema erkennen
        legacy_schemes = [detect_hash_scheme(h) for h in legacy_hashes]
        ddd_schemes = [detect_hash_scheme(h) for h in ddd_hashes]
        
        # Hash-Länge prüfen
        legacy_lengths = [len(h) for h in legacy_hashes]
        ddd_lengths = [len(h) for h in ddd_hashes]
        
        # Vergleich
        print(f"Legacy schemes: {[s['scheme'] for s in legacy_schemes]}")
        print(f"DDD schemes: {[s['scheme'] for s in ddd_schemes]}")
        print(f"Legacy lengths: {legacy_lengths}")
        print(f"DDD lengths: {ddd_lengths}")
        
        # Asserts
        assert all(s['scheme'] == 'bcrypt' for s in legacy_schemes), "Legacy should use bcrypt"
        assert all(s['scheme'] == 'bcrypt' for s in ddd_schemes), "DDD should use bcrypt"
        assert all(s['valid'] for s in legacy_schemes), "Legacy hashes should be valid"
        assert all(s['valid'] for s in ddd_schemes), "DDD hashes should be valid"
        assert all(l >= 50 for l in legacy_lengths), "Legacy hashes should be long enough"
        assert all(l >= 50 for l in ddd_lengths), "DDD hashes should be long enough"
        
        print(f"\n✅ Password Hash Security Parität erfolgreich getestet")
    
    def test_password_complexity_policy_parity(self, client):
        """Test: Passwort-Komplexität Policy (Common Passwords, Mindestlänge)"""
        print("Teste Password Complexity Policy Parität...")
        
        # Test-Passwörter
        test_passwords = [
            ("SecurePassword123!", "strong"),
            ("123456", "weak"),
            ("password", "common"),
            ("admin", "common"),
            ("qwerty", "common"),
            ("", "empty"),
            ("a", "too_short"),
            ("abcdefgh", "no_complexity")
        ]
        
        legacy_complexity_results = []
        ddd_complexity_results = []
        
        for password, category in test_passwords:
            # Legacy Komplexität
            legacy_complexity = validate_password_complexity(password)
            legacy_complexity_results.append(legacy_complexity)
            
            # DDD Komplexität
            ddd_complexity = validate_password_complexity(password)
            ddd_complexity_results.append(ddd_complexity)
        
        # Common Password Checks
        legacy_common_results = [is_common_password(pw) for pw, _ in test_passwords]
        ddd_common_results = [is_common_password(pw) for pw, _ in test_passwords]
        
        # Vergleich
        print(f"Legacy complexity valid: {[c['valid'] for c in legacy_complexity_results]}")
        print(f"DDD complexity valid: {[c['valid'] for c in ddd_complexity_results]}")
        print(f"Legacy common passwords: {legacy_common_results}")
        print(f"DDD common passwords: {ddd_common_results}")
        
        # Asserts
        assert legacy_complexity_results == ddd_complexity_results, "Complexity validation should be identical"
        assert legacy_common_results == ddd_common_results, "Common password detection should be identical"
        
        # Spezifische Checks
        assert not legacy_complexity_results[0]['valid'], "Strong password should be valid"
        assert not legacy_complexity_results[1]['valid'], "Weak password should be invalid"
        assert not legacy_complexity_results[2]['valid'], "Common password should be invalid"
        assert legacy_common_results[1], "123456 should be detected as common"
        assert legacy_common_results[2], "password should be detected as common"
        
        print(f"\n✅ Password Complexity Policy Parität erfolgreich getestet")
    
    def test_password_no_plaintext_logs_parity(self, client):
        """Test: Keine Klartext-Passwörter in Logs (nur dokumentieren)"""
        print("Teste Password No Plaintext Logs Parität...")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_password_no_logs_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_password_no_logs_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            users = seed_auth_test_users(conn)
        
        with sqlite3.connect(ddd_db_path) as conn:
            users = seed_auth_test_users(conn)
        
        # Test-Passwörter (sollten nicht in Logs erscheinen)
        test_passwords = [
            "SecurePassword123!",
            "123456",
            "password",
            "admin",
            "qwerty"
        ]
        
        # Hash-Werte prüfen (sollten keine Klartext-Passwörter enthalten)
        legacy_hashes = []
        ddd_hashes = []
        
        for user_type, user_id in users.items():
            # Legacy Hash
            with sqlite3.connect(legacy_db_path) as conn:
                legacy_hash = get_user_password_hash(conn, user_id)
                if legacy_hash:
                    legacy_hashes.append(legacy_hash)
            
            # DDD Hash
            with sqlite3.connect(ddd_db_path) as conn:
                ddd_hash = get_user_password_hash(conn, user_id)
                if ddd_hash:
                    ddd_hashes.append(ddd_hash)
        
        # Prüfen ob Klartext-Passwörter in Hashes enthalten sind
        legacy_plaintext_found = []
        ddd_plaintext_found = []
        
        for password in test_passwords:
            for hash_val in legacy_hashes:
                if password in hash_val:
                    legacy_plaintext_found.append(password)
                    break
        
        for password in test_passwords:
            for hash_val in ddd_hashes:
                if password in hash_val:
                    ddd_plaintext_found.append(password)
                    break
        
        # Vergleich
        print(f"Legacy plaintext found: {legacy_plaintext_found}")
        print(f"DDD plaintext found: {ddd_plaintext_found}")
        
        # Asserts
        assert len(legacy_plaintext_found) == 0, f"Legacy should not contain plaintext passwords: {legacy_plaintext_found}"
        assert len(ddd_plaintext_found) == 0, f"DDD should not contain plaintext passwords: {ddd_plaintext_found}"
        
        print(f"\n✅ Password No Plaintext Logs Parität erfolgreich getestet")
    
    def test_password_hash_consistency_parity(self, client):
        """Test: Hash-Konsistenz (gleiche Passwörter → gleiche Hashes)"""
        print("Teste Password Hash Consistency Parität...")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_password_consistency_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_password_consistency_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            users = seed_auth_test_users(conn)
        
        with sqlite3.connect(ddd_db_path) as conn:
            users = seed_auth_test_users(conn)
        
        # Hash-Konsistenz prüfen
        legacy_hashes = []
        ddd_hashes = []
        
        for user_type, user_id in users.items():
            # Legacy Hash
            with sqlite3.connect(legacy_db_path) as conn:
                legacy_hash = get_user_password_hash(conn, user_id)
                if legacy_hash:
                    legacy_hashes.append(legacy_hash)
            
            # DDD Hash
            with sqlite3.connect(ddd_db_path) as conn:
                ddd_hash = get_user_password_hash(conn, user_id)
                if ddd_hash:
                    ddd_hashes.append(ddd_hash)
        
        # Hash-Schema-Konsistenz
        legacy_schemes = [detect_hash_scheme(h)['scheme'] for h in legacy_hashes]
        ddd_schemes = [detect_hash_scheme(h)['scheme'] for h in ddd_hashes]
        
        # Hash-Längen-Konsistenz
        legacy_lengths = [len(h) for h in legacy_hashes]
        ddd_lengths = [len(h) for h in ddd_hashes]
        
        # Vergleich
        print(f"Legacy schemes: {legacy_schemes}")
        print(f"DDD schemes: {ddd_schemes}")
        print(f"Legacy lengths: {legacy_lengths}")
        print(f"DDD lengths: {ddd_lengths}")
        
        # Asserts
        assert all(s == 'bcrypt' for s in legacy_schemes), "Legacy should use consistent bcrypt"
        assert all(s == 'bcrypt' for s in ddd_schemes), "DDD should use consistent bcrypt"
        assert len(set(legacy_lengths)) <= 2, "Legacy hash lengths should be consistent"
        assert len(set(ddd_lengths)) <= 2, "DDD hash lengths should be consistent"
        
        print(f"\n✅ Password Hash Consistency Parität erfolgreich getestet")

