"""
Login-Parität: Legacy vs. DDD
Testet die Parität zwischen Legacy- und DDD-Auth-Login
"""

import pytest
from tests.helpers.ab_runner import run_request
from tests.helpers.auth_flow import get_test_credentials


class TestLoginParity:
    """Testet Login-Parität zwischen Legacy und DDD"""
    
    def _ensure_test_users_exist(self):
        """Stellt sicher, dass Test-Users in der DB existieren"""
        import sqlite3
        import bcrypt
        
        db_path = "/Users/reiner/Documents/DocuMind-AI/.tmp/test_qms_mvp.db"
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Lösche bestehende Test-Users
                cursor.execute('DELETE FROM users WHERE email IN ("test@example.com", "qms.admin")')
                
                # Test-Users mit korrekten bcrypt-Hashes erstellen
                test_users = [
                    {
                        'email': 'test@example.com',
                        'password': 'test123',
                        'full_name': 'Test User',
                        'is_active': True
                    },
                    {
                        'email': 'qms.admin', 
                        'password': 'admin123',
                        'full_name': 'QMS Admin',
                        'is_active': True
                    }
                ]
                
                for user in test_users:
                    # Bcrypt-Hash erstellen
                    password_hash = bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    
                    cursor.execute('''
                        INSERT INTO users (email, hashed_password, full_name, is_active, created_at)
                        VALUES (?, ?, ?, ?, datetime("now"))
                    ''', (
                        user['email'],
                        password_hash,
                        user['full_name'],
                        user['is_active']
                    ))
                    
                    print(f'[SEED] user_created={user["email"]} is_active={user["is_active"]} hash_prefix={password_hash[:20]}...')
                
                conn.commit()
                print('[SEED] test users created with bcrypt hashes in test DB')
                
        except Exception as e:
            print(f'[SEED] ensure_test_users_error: {e}')
    
    def test_valid_credentials_parity(self, client):
        """Test: Gültige Credentials - Legacy vs. DDD"""
        print("Teste gültige Credentials...")
        
        # Stelle sicher, dass Test-Users in der DB existieren
        self._ensure_test_users_exist()
        
        credentials = get_test_credentials()
        user_creds = credentials["user"]
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "POST", "/api/auth/login",
            json_data={"email": user_creds["email"], "password": user_creds["password"]}
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "POST", "/api/auth/login",
            json_data={"email": user_creds["email"], "password": user_creds["password"]}
        )
        
        # Status-Codes prüfen
        legacy_status = legacy_response[0]
        ddd_status = ddd_response[0]
        
        print(f"[LOGIN] legacy status={legacy_status} ddd status={ddd_status}")
        
        # Beide sollten 200 zurückgeben
        assert legacy_status == 200, f"Legacy sollte 200 zurückgeben, aber gab {legacy_status} zurück"
        assert ddd_status == 200, f"DDD sollte 200 zurückgeben, aber gab {ddd_status} zurück"
        
        # Response-Struktur prüfen
        legacy_data = legacy_response[1] if len(legacy_response) > 1 else {}
        ddd_data = ddd_response[1] if len(ddd_response) > 1 else {}
        
        # Erwartete Schlüssel prüfen
        expected_keys = ["access_token", "token_type", "expires_in", "user_id", "user_name", "groups", "permissions"]
        
        for key in expected_keys:
            assert key in legacy_data, f"Legacy-Response fehlt Schlüssel: {key}"
            assert key in ddd_data, f"DDD-Response fehlt Schlüssel: {key}"
        
        # Token-Typ prüfen
        assert legacy_data["token_type"] == "bearer", f"Legacy token_type sollte 'bearer' sein, ist aber '{legacy_data['token_type']}'"
        assert ddd_data["token_type"] == "bearer", f"DDD token_type sollte 'bearer' sein, ist aber '{ddd_data['token_type']}'"
        
        # User-ID prüfen
        assert legacy_data["user_id"] is not None, "Legacy user_id sollte nicht None sein"
        assert ddd_data["user_id"] is not None, "DDD user_id sollte nicht None sein"
        
        print(f"[LOGIN] legacy user_id={legacy_data['user_id']} ddd user_id={ddd_data['user_id']}")
        print("✅ Gültige Credentials erfolgreich getestet")
    
    def test_invalid_password_parity(self, client):
        """Test: Ungültiges Passwort - Legacy vs. DDD"""
        print("Teste ungültiges Passwort...")
        
        credentials = get_test_credentials()
        user_creds = credentials["user"]
        
        # Legacy-Request mit falschem Passwort
        legacy_response = run_request(
            client, "legacy", "POST", "/api/auth/login",
            json_data={"email": user_creds["email"], "password": "wrong_password"}
        )
        
        # DDD-Request mit falschem Passwort
        ddd_response = run_request(
            client, "ddd", "POST", "/api/auth/login",
            json_data={"email": user_creds["email"], "password": "wrong_password"}
        )
        
        # Status-Codes prüfen
        legacy_status = legacy_response[0]
        ddd_status = ddd_response[0]
        
        print(f"[LOGIN] legacy status={legacy_status} ddd status={ddd_status}")
        
        # Beide sollten 401 zurückgeben
        assert legacy_status == 401, f"Legacy sollte 401 zurückgeben, aber gab {legacy_status} zurück"
        assert ddd_status == 401, f"DDD sollte 401 zurückgeben, aber gab {ddd_status} zurück"
        
        print("✅ Ungültiges Passwort erfolgreich getestet")
    
    def test_invalid_email_parity(self, client):
        """Test: Ungültige E-Mail - Legacy vs. DDD"""
        print("Teste ungültige E-Mail...")
        
        # Legacy-Request mit falscher E-Mail
        legacy_response = run_request(
            client, "legacy", "POST", "/api/auth/login",
            json_data={"email": "nonexistent@example.com", "password": "test123"}
        )
        
        # DDD-Request mit falscher E-Mail
        ddd_response = run_request(
            client, "ddd", "POST", "/api/auth/login",
            json_data={"email": "nonexistent@example.com", "password": "test123"}
        )
        
        # Status-Codes prüfen
        legacy_status = legacy_response[0]
        ddd_status = ddd_response[0]
        
        print(f"[LOGIN] legacy status={legacy_status} ddd status={ddd_status}")
        
        # Beide sollten 401 zurückgeben
        assert legacy_status == 401, f"Legacy sollte 401 zurückgeben, aber gab {legacy_status} zurück"
        assert ddd_status == 401, f"DDD sollte 401 zurückgeben, aber gab {ddd_status} zurück"
        
        print("✅ Ungültige E-Mail erfolgreich getestet")
    
    def test_inactive_user_parity(self, client):
        """Test: Inaktiver User - Legacy vs. DDD"""
        print("Teste inaktiven User...")
        
        # TODO: Implementiere Test für inaktiven User
        # Dafür müsste ein User in der DB auf is_active=False gesetzt werden
        
        # Für jetzt: Test überspringen
        pytest.skip("Inaktiver User Test noch nicht implementiert")
    
    def test_missing_fields_parity(self, client):
        """Test: Fehlende Felder - Legacy vs. DDD"""
        print("Teste fehlende Felder...")
        
        # Legacy-Request ohne E-Mail
        legacy_response = run_request(
            client, "legacy", "POST", "/api/auth/login",
            json_data={"password": "test123"}
        )
        
        # DDD-Request ohne E-Mail
        ddd_response = run_request(
            client, "ddd", "POST", "/api/auth/login",
            json_data={"password": "test123"}
        )
        
        # Status-Codes prüfen
        legacy_status = legacy_response[0]
        ddd_status = ddd_response[0]
        
        print(f"[LOGIN] legacy status={legacy_status} ddd status={ddd_status}")
        
        # Beide sollten 422 zurückgeben (Validation Error)
        assert legacy_status == 422, f"Legacy sollte 422 zurückgeben, aber gab {legacy_status} zurück"
        assert ddd_status == 422, f"DDD sollte 422 zurückgeben, aber gab {ddd_status} zurück"
        
        print("✅ Fehlende Felder erfolgreich getestet")
    
    def test_admin_credentials_parity(self, client):
        """Test: Admin-Credentials - Legacy vs. DDD"""
        print("Teste Admin-Credentials...")
        
        credentials = get_test_credentials()
        admin_creds = credentials["admin"]
        
        # Legacy-Request
        legacy_response = run_request(
            client, "legacy", "POST", "/api/auth/login",
            json_data={"email": admin_creds["email"], "password": admin_creds["password"]}
        )
        
        # DDD-Request
        ddd_response = run_request(
            client, "ddd", "POST", "/api/auth/login",
            json_data={"email": admin_creds["email"], "password": admin_creds["password"]}
        )
        
        # Status-Codes prüfen
        legacy_status = legacy_response[0]
        ddd_status = ddd_response[0]
        
        print(f"[LOGIN] legacy status={legacy_status} ddd status={ddd_status}")
        
        # Beide sollten 200 zurückgeben
        assert legacy_status == 200, f"Legacy sollte 200 zurückgeben, aber gab {legacy_status} zurück"
        assert ddd_status == 200, f"DDD sollte 200 zurückgeben, aber gab {ddd_status} zurück"
        
        # Response-Struktur prüfen
        legacy_data = legacy_response[1] if len(legacy_response) > 1 else {}
        ddd_data = ddd_response[1] if len(ddd_response) > 1 else {}
        
        # User-ID prüfen
        assert legacy_data["user_id"] is not None, "Legacy user_id sollte nicht None sein"
        assert ddd_data["user_id"] is not None, "DDD user_id sollte nicht None sein"
        
        print(f"[LOGIN] legacy admin user_id={legacy_data['user_id']} ddd admin user_id={ddd_data['user_id']}")
        print("✅ Admin-Credentials erfolgreich getestet")
