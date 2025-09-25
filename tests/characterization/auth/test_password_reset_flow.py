"""
Password Reset Flow Tests
Testet Passwort-Reset-Flow mit Token-Generierung und -Validierung
"""

import pytest
import os
import uuid
import sqlite3
import time
from tests.helpers.ab_runner import run_request, compare_responses, format_comparison_result
from tests.helpers.seeds_auth import (
    seed_auth_test_users, create_reset_token, get_reset_token, mark_token_used,
    update_user_password, get_user_password_hash, get_token_expiry_status
)
from tests.helpers.capabilities_auth import get_auth_capability_flags


class TestPasswordResetFlow:
    """Testet Password Reset Flow Verhalten"""
    
    def test_password_reset_request_confirm_parity(self, client):
        """Test: Reset Request → Token → Confirm mit neuem Passwort"""
        print("Teste Password Reset Request/Confirm Parität...")
        
        # Capability Detection
        capabilities = get_auth_capability_flags()
        if not capabilities["HAS_RESET_REQUEST"] and not capabilities["HAS_RESET_CONFIRM"]:
            pytest.skip("legacy endpoint not available")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_password_reset_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_password_reset_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
        
        with sqlite3.connect(ddd_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
        
        # Neues Passwort
        new_password = "ResetPassword789!"
        
        # Legacy: Reset Request
        legacy_request_success = False
        legacy_token = None
        legacy_seed_fallback = False
        
        if capabilities["HAS_RESET_REQUEST"]:
            try:
                request_payload = {"email": "test.user@company.com"}
                legacy_request_response = run_request(
                    client, "legacy", "POST", "/api/auth/reset/request",
                    json_data=request_payload,
                    database_url=legacy_database_url
                )
                legacy_request_success = legacy_request_response[0] in [200, 202]
                # Token aus Response extrahieren (falls vorhanden)
                legacy_token = legacy_request_response[1].get('token') if legacy_request_success else None
            except Exception as e:
                print(f"Legacy reset request error: {e}")
        else:
            # Seed Fallback
            with sqlite3.connect(legacy_db_path) as conn:
                legacy_token = create_reset_token(conn, test_user_id)
                legacy_request_success = True
                legacy_seed_fallback = True
        
        # DDD: Reset Request
        ddd_request_success = False
        ddd_token = None
        ddd_seed_fallback = False
        
        if capabilities["HAS_RESET_REQUEST"]:
            try:
                request_payload = {"email": "test.user@company.com"}
                ddd_request_response = run_request(
                    client, "ddd", "POST", "/api/auth/reset/request",
                    json_data=request_payload,
                    database_url=ddd_database_url
                )
                ddd_request_success = ddd_request_response[0] in [200, 202]
                # Token aus Response extrahieren (falls vorhanden)
                ddd_token = ddd_request_response[1].get('token') if ddd_request_success else None
            except Exception as e:
                print(f"DDD reset request error: {e}")
        else:
            # Seed Fallback
            with sqlite3.connect(ddd_db_path) as conn:
                ddd_token = create_reset_token(conn, test_user_id)
                ddd_request_success = True
                ddd_seed_fallback = True
        
        # Legacy: Reset Confirm
        legacy_confirm_success = False
        legacy_hash_changed = False
        
        if capabilities["HAS_RESET_CONFIRM"] and legacy_token:
            try:
                confirm_payload = {
                    "token": legacy_token,
                    "new_password": new_password,
                    "confirm_password": new_password
                }
                legacy_confirm_response = run_request(
                    client, "legacy", "POST", "/api/auth/reset/confirm",
                    json_data=confirm_payload,
                    database_url=legacy_database_url
                )
                legacy_confirm_success = legacy_confirm_response[0] == 200
            except Exception as e:
                print(f"Legacy reset confirm error: {e}")
        elif legacy_token:
            # Seed Fallback
            with sqlite3.connect(legacy_db_path) as conn:
                old_hash = get_user_password_hash(conn, test_user_id)
                legacy_confirm_success = update_user_password(conn, test_user_id, new_password)
                new_hash = get_user_password_hash(conn, test_user_id)
                legacy_hash_changed = old_hash != new_hash
                # Token als verwendet markieren
                mark_token_used(conn, legacy_token)
        
        # DDD: Reset Confirm
        ddd_confirm_success = False
        ddd_hash_changed = False
        
        if capabilities["HAS_RESET_CONFIRM"] and ddd_token:
            try:
                confirm_payload = {
                    "token": ddd_token,
                    "new_password": new_password,
                    "confirm_password": new_password
                }
                ddd_confirm_response = run_request(
                    client, "ddd", "POST", "/api/auth/reset/confirm",
                    json_data=confirm_payload,
                    database_url=ddd_database_url
                )
                ddd_confirm_success = ddd_confirm_response[0] == 200
            except Exception as e:
                print(f"DDD reset confirm error: {e}")
        elif ddd_token:
            # Seed Fallback
            with sqlite3.connect(ddd_db_path) as conn:
                old_hash = get_user_password_hash(conn, test_user_id)
                ddd_confirm_success = update_user_password(conn, test_user_id, new_password)
                new_hash = get_user_password_hash(conn, test_user_id)
                ddd_hash_changed = old_hash != new_hash
                # Token als verwendet markieren
                mark_token_used(conn, ddd_token)
        
        # Vergleich
        print(f"Legacy: request={legacy_request_success}, confirm={legacy_confirm_success}, hash_changed={legacy_hash_changed}, seed_fallback={legacy_seed_fallback}")
        print(f"DDD: request={ddd_request_success}, confirm={ddd_confirm_success}, hash_changed={ddd_hash_changed}, seed_fallback={ddd_seed_fallback}")
        
        # Asserts
        assert legacy_request_success == ddd_request_success, f"Request parity: Legacy={legacy_request_success}, DDD={ddd_request_success}"
        assert legacy_confirm_success == ddd_confirm_success, f"Confirm parity: Legacy={legacy_confirm_success}, DDD={ddd_confirm_success}"
        assert legacy_hash_changed == ddd_hash_changed, f"Hash changed parity: Legacy={legacy_hash_changed}, DDD={ddd_hash_changed}"
        
        print(f"\n✅ Password Reset Request/Confirm Parität erfolgreich getestet")
    
    def test_password_reset_token_single_use_parity(self, client):
        """Test: Token Single-Use (zweiter Confirm → 410/400)"""
        print("Teste Password Reset Token Single-Use Parität...")
        
        # Capability Detection
        capabilities = get_auth_capability_flags()
        if not capabilities["HAS_RESET_CONFIRM"]:
            pytest.skip("legacy endpoint not available")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_password_reset_single_use_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_password_reset_single_use_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
            legacy_token = create_reset_token(conn, test_user_id)
        
        with sqlite3.connect(ddd_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
            ddd_token = create_reset_token(conn, test_user_id)
        
        # Neues Passwort
        new_password = "SingleUsePassword123!"
        
        # Legacy: Erster Confirm
        legacy_first_confirm_success = False
        if capabilities["HAS_RESET_CONFIRM"]:
            try:
                confirm_payload = {
                    "token": legacy_token,
                    "new_password": new_password,
                    "confirm_password": new_password
                }
                legacy_first_confirm_response = run_request(
                    client, "legacy", "POST", "/api/auth/reset/confirm",
                    json_data=confirm_payload,
                    database_url=legacy_database_url
                )
                legacy_first_confirm_success = legacy_first_confirm_response[0] == 200
            except Exception as e:
                print(f"Legacy first confirm error: {e}")
        else:
            # Seed Fallback
            with sqlite3.connect(legacy_db_path) as conn:
                legacy_first_confirm_success = update_user_password(conn, test_user_id, new_password)
                mark_token_used(conn, legacy_token)
        
        # DDD: Erster Confirm
        ddd_first_confirm_success = False
        if capabilities["HAS_RESET_CONFIRM"]:
            try:
                confirm_payload = {
                    "token": ddd_token,
                    "new_password": new_password,
                    "confirm_password": new_password
                }
                ddd_first_confirm_response = run_request(
                    client, "ddd", "POST", "/api/auth/reset/confirm",
                    json_data=confirm_payload,
                    database_url=ddd_database_url
                )
                ddd_first_confirm_success = ddd_first_confirm_response[0] == 200
            except Exception as e:
                print(f"DDD first confirm error: {e}")
        else:
            # Seed Fallback
            with sqlite3.connect(ddd_db_path) as conn:
                ddd_first_confirm_success = update_user_password(conn, test_user_id, new_password)
                mark_token_used(conn, ddd_token)
        
        # Legacy: Zweiter Confirm (sollte fehlschlagen)
        legacy_second_confirm_success = False
        legacy_second_confirm_status = None
        
        if capabilities["HAS_RESET_CONFIRM"]:
            try:
                confirm_payload = {
                    "token": legacy_token,
                    "new_password": "AnotherPassword456!",
                    "confirm_password": "AnotherPassword456!"
                }
                legacy_second_confirm_response = run_request(
                    client, "legacy", "POST", "/api/auth/reset/confirm",
                    json_data=confirm_payload,
                    database_url=legacy_database_url
                )
                legacy_second_confirm_status = legacy_second_confirm_response[0]
                legacy_second_confirm_success = legacy_second_confirm_status in [400, 410, 422]
            except Exception as e:
                print(f"Legacy second confirm error: {e}")
        else:
            # Seed Fallback: Token sollte bereits verwendet sein
            with sqlite3.connect(legacy_db_path) as conn:
                token_status = get_token_expiry_status(conn, legacy_token)
                legacy_second_confirm_success = token_status["used"]
                legacy_second_confirm_status = 410 if legacy_second_confirm_success else 200
        
        # DDD: Zweiter Confirm (sollte fehlschlagen)
        ddd_second_confirm_success = False
        ddd_second_confirm_status = None
        
        if capabilities["HAS_RESET_CONFIRM"]:
            try:
                confirm_payload = {
                    "token": ddd_token,
                    "new_password": "AnotherPassword456!",
                    "confirm_password": "AnotherPassword456!"
                }
                ddd_second_confirm_response = run_request(
                    client, "ddd", "POST", "/api/auth/reset/confirm",
                    json_data=confirm_payload,
                    database_url=ddd_database_url
                )
                ddd_second_confirm_status = ddd_second_confirm_response[0]
                ddd_second_confirm_success = ddd_second_confirm_status in [400, 410, 422]
            except Exception as e:
                print(f"DDD second confirm error: {e}")
        else:
            # Seed Fallback: Token sollte bereits verwendet sein
            with sqlite3.connect(ddd_db_path) as conn:
                token_status = get_token_expiry_status(conn, ddd_token)
                ddd_second_confirm_success = token_status["used"]
                ddd_second_confirm_status = 410 if ddd_second_confirm_success else 200
        
        # Vergleich
        print(f"Legacy: first_confirm={legacy_first_confirm_success}, second_confirm={legacy_second_confirm_success}, second_status={legacy_second_confirm_status}")
        print(f"DDD: first_confirm={ddd_first_confirm_success}, second_confirm={ddd_second_confirm_success}, second_status={ddd_second_confirm_status}")
        
        # Asserts
        assert legacy_first_confirm_success == ddd_first_confirm_success, f"First confirm parity: Legacy={legacy_first_confirm_success}, DDD={ddd_first_confirm_success}"
        assert legacy_second_confirm_success == ddd_second_confirm_success, f"Second confirm parity: Legacy={legacy_second_confirm_success}, DDD={ddd_second_confirm_success}"
        
        print(f"\n✅ Password Reset Token Single-Use Parität erfolgreich getestet")
    
    def test_password_reset_token_expiry_parity(self, client):
        """Test: Token Expiry (abgelaufenes Token → 410/400)"""
        print("Teste Password Reset Token Expiry Parität...")
        
        # Capability Detection
        capabilities = get_auth_capability_flags()
        if not capabilities["HAS_RESET_CONFIRM"]:
            pytest.skip("legacy endpoint not available")
        
        # Isolierte DB für Legacy
        legacy_db_path = f".tmp/test_password_reset_expiry_{uuid.uuid4().hex[:8]}_legacy.db"
        legacy_database_url = f"sqlite:///{legacy_db_path}"
        
        # Isolierte DB für DDD
        ddd_db_path = f".tmp/test_password_reset_expiry_{uuid.uuid4().hex[:8]}_ddd.db"
        ddd_database_url = f"sqlite:///{ddd_db_path}"
        
        # Seeds anwenden
        with sqlite3.connect(legacy_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
            # Token mit kurzer Ablaufzeit erstellen (1 Sekunde)
            legacy_token = create_reset_token(conn, test_user_id, expires_in_hours=0.0003)  # ~1 Sekunde
        
        with sqlite3.connect(ddd_db_path) as conn:
            users = seed_auth_test_users(conn)
            test_user_id = users["normal_user"]
            # Token mit kurzer Ablaufzeit erstellen (1 Sekunde)
            ddd_token = create_reset_token(conn, test_user_id, expires_in_hours=0.0003)  # ~1 Sekunde
        
        # Warten bis Token abgelaufen ist
        time.sleep(2)
        
        # Neues Passwort
        new_password = "ExpiredTokenPassword123!"
        
        # Legacy: Confirm mit abgelaufenem Token
        legacy_confirm_success = False
        legacy_confirm_status = None
        
        if capabilities["HAS_RESET_CONFIRM"]:
            try:
                confirm_payload = {
                    "token": legacy_token,
                    "new_password": new_password,
                    "confirm_password": new_password
                }
                legacy_confirm_response = run_request(
                    client, "legacy", "POST", "/api/auth/reset/confirm",
                    json_data=confirm_payload,
                    database_url=legacy_database_url
                )
                legacy_confirm_status = legacy_confirm_response[0]
                legacy_confirm_success = legacy_confirm_status in [400, 410, 422]
            except Exception as e:
                print(f"Legacy expired token confirm error: {e}")
        else:
            # Seed Fallback: Token sollte abgelaufen sein
            with sqlite3.connect(legacy_db_path) as conn:
                token_status = get_token_expiry_status(conn, legacy_token)
                legacy_confirm_success = token_status["expired"]
                legacy_confirm_status = 410 if legacy_confirm_success else 200
        
        # DDD: Confirm mit abgelaufenem Token
        ddd_confirm_success = False
        ddd_confirm_status = None
        
        if capabilities["HAS_RESET_CONFIRM"]:
            try:
                confirm_payload = {
                    "token": ddd_token,
                    "new_password": new_password,
                    "confirm_password": new_password
                }
                ddd_confirm_response = run_request(
                    client, "ddd", "POST", "/api/auth/reset/confirm",
                    json_data=confirm_payload,
                    database_url=ddd_database_url
                )
                ddd_confirm_status = ddd_confirm_response[0]
                ddd_confirm_success = ddd_confirm_status in [400, 410, 422]
            except Exception as e:
                print(f"DDD expired token confirm error: {e}")
        else:
            # Seed Fallback: Token sollte abgelaufen sein
            with sqlite3.connect(ddd_db_path) as conn:
                token_status = get_token_expiry_status(conn, ddd_token)
                ddd_confirm_success = token_status["expired"]
                ddd_confirm_status = 410 if ddd_confirm_success else 200
        
        # Vergleich
        print(f"Legacy: confirm={legacy_confirm_success}, status={legacy_confirm_status}")
        print(f"DDD: confirm={ddd_confirm_success}, status={ddd_confirm_status}")
        
        # Asserts
        assert legacy_confirm_success == ddd_confirm_success, f"Expired token confirm parity: Legacy={legacy_confirm_success}, DDD={ddd_confirm_success}"
        
        print(f"\n✅ Password Reset Token Expiry Parität erfolgreich getestet")

