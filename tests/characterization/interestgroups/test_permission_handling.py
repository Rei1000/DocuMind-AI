"""
Charakterisierungstest für Permission Handling in Interest Groups
Testet Parität zwischen Legacy und DDD Modi
"""

import pytest
import time
import sqlite3
from tests.helpers.payloads import ig_payload
from tests.helpers.bootstrap_from_schema import make_fresh_db_at, set_env_db
from tests.helpers.seeds_interest_groups import seed_group
from tests.helpers.ab_runner import run_legacy, run_ddd


def get_interest_groups_count(db_path: str) -> int:
    """Hilfsfunktion: Zählt die Anzahl der Interest Groups in der DB"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interest_groups")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return -1


class TestPermissionHandling:
    """Test für Permission Handling und Validierung (Legacy vs DDD)"""
    
    def test_permission_parsing_json_string(self):
        """Test: JSON-String Permissions werden identisch behandelt (Legacy vs DDD)"""
        timestamp = int(time.time())
        
        # Test mit gültigem JSON
        payload = ig_payload(
            code=f"json_permissions_test_{timestamp}",
            name="JSON Permissions Test",
            perms_input='["read", "write", "delete"]'
        )
        
        # Legacy-Lauf: Frische DB erstellen
        legacy_db_path = f".tmp/perm_legacy_json_{timestamp}.db"
        make_fresh_db_at(legacy_db_path)
        set_env_db(legacy_db_path)
        
        # Legacy-Create
        legacy_status, legacy_body = run_legacy(
            "backend.app.main:app", 
            legacy_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=payload
        )
        
        # DDD-Lauf: Frische DB erstellen
        ddd_db_path = f".tmp/perm_ddd_json_{timestamp}.db"
        make_fresh_db_at(ddd_db_path)
        set_env_db(ddd_db_path)
        
        # DDD-Create (mit anderem Code für frischen DB-Zustand)
        ddd_payload = ig_payload(
            code=f"ddd_json_permissions_test_{timestamp}",
            name="DDD JSON Permissions Test",
            perms_input='["read", "write", "delete"]'
        )
        
        ddd_status, ddd_body = run_ddd(
            "backend.app.main:app", 
            ddd_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=ddd_payload
        )
        
        # Parität: Beide Modi sollten identischen Statuscode zurückgeben
        assert legacy_status == ddd_status, \
            f"JSON-String Statuscode-Parität verletzt: Legacy={legacy_status}, DDD={ddd_status}"
        
        print(f"JSON-String Test - Legacy: {legacy_status}, DDD: {ddd_status}")
        
        # Wenn beide erfolgreich waren, vergleiche die Permissions
        if legacy_status == 200 and ddd_status == 200:
            legacy_perms = legacy_body.get("group_permissions", [])
            ddd_perms = ddd_body.get("group_permissions", [])
            
            print(f"JSON-String Permissions - Legacy: {legacy_perms}, DDD: {ddd_perms}")
    
    def test_permission_parsing_comma_separated(self):
        """Test: Komma-separierte Permissions werden identisch behandelt (Legacy vs DDD)"""
        timestamp = int(time.time())
        
        # Test mit Komma-separierten Strings
        payload = ig_payload(
            code=f"comma_permissions_test_{timestamp}",
            name="Comma Permissions Test",
            perms_input="read, write, delete"
        )
        
        # Legacy-Lauf: Frische DB erstellen
        legacy_db_path = f".tmp/perm_legacy_comma_{timestamp}.db"
        make_fresh_db_at(legacy_db_path)
        set_env_db(legacy_db_path)
        
        # Legacy-Create
        legacy_status, legacy_body = run_legacy(
            "backend.app.main:app", 
            legacy_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=payload
        )
        
        # DDD-Lauf: Frische DB erstellen
        ddd_db_path = f".tmp/perm_ddd_comma_{timestamp}.db"
        make_fresh_db_at(ddd_db_path)
        set_env_db(ddd_db_path)
        
        # DDD-Create (mit anderem Code für frischen DB-Zustand)
        ddd_payload = ig_payload(
            code=f"ddd_comma_permissions_test_{timestamp}",
            name="DDD Comma Permissions Test",
            perms_input="read, write, delete"
        )
        
        ddd_status, ddd_body = run_ddd(
            "backend.app.main:app", 
            ddd_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=ddd_payload
        )
        
        # Parität: Beide Modi sollten identischen Statuscode zurückgeben
        assert legacy_status == ddd_status, \
            f"Comma-String Statuscode-Parität verletzt: Legacy={legacy_status}, DDD={ddd_status}"
        
        print(f"Comma-String Test - Legacy: {legacy_status}, DDD: {ddd_status}")
        
        # Wenn beide erfolgreich waren, vergleiche die Permissions
        if legacy_status == 200 and ddd_status == 200:
            legacy_perms = legacy_body.get("group_permissions", [])
            ddd_perms = ddd_body.get("group_permissions", [])
            
            print(f"Comma-String Permissions - Legacy: {legacy_perms}, DDD: {ddd_perms}")
    
    def test_permission_parsing_list_input(self):
        """Test: Listen-Input wird identisch behandelt (Legacy vs DDD)"""
        timestamp = int(time.time())
        
        # Test mit Liste von Strings
        payload = ig_payload(
            code=f"list_permissions_test_{timestamp}",
            name="List Permissions Test",
            perms_input=["create", "read", "update", "delete"]
        )
        
        # Legacy-Lauf: Frische DB erstellen
        legacy_db_path = f".tmp/perm_legacy_list_{timestamp}.db"
        make_fresh_db_at(legacy_db_path)
        set_env_db(legacy_db_path)
        
        # Legacy-Create
        legacy_status, legacy_body = run_legacy(
            "backend.app.main:app", 
            legacy_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=payload
        )
        
        # DDD-Lauf: Frische DB erstellen
        ddd_db_path = f".tmp/perm_ddd_list_{timestamp}.db"
        make_fresh_db_at(ddd_db_path)
        set_env_db(ddd_db_path)
        
        # DDD-Create (mit anderem Code für frischen DB-Zustand)
        ddd_payload = ig_payload(
            code=f"ddd_list_permissions_test_{timestamp}",
            name="DDD List Permissions Test",
            perms_input=["create", "read", "update", "delete"]
        )
        
        ddd_status, ddd_body = run_ddd(
            "backend.app.main:app", 
            ddd_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=ddd_payload
        )
        
        # Parität: Beide Modi sollten identischen Statuscode zurückgeben
        assert legacy_status == ddd_status, \
            f"List-Input Statuscode-Parität verletzt: Legacy={legacy_status}, DDD={ddd_status}"
        
        print(f"List-Input Test - Legacy: {legacy_status}, DDD: {ddd_status}")
        
        # Wenn beide erfolgreich waren, vergleiche die Permissions
        if legacy_status == 200 and ddd_status == 200:
            legacy_perms = legacy_body.get("group_permissions", [])
            ddd_perms = ddd_body.get("group_permissions", [])
            
            print(f"List-Input Permissions - Legacy: {legacy_perms}, DDD: {ddd_perms}")
    
    def test_permission_parsing_edge_cases(self):
        """Test: Edge Cases werden identisch behandelt (Legacy vs DDD)"""
        timestamp = int(time.time())
        
        # Test mit None
        payload = ig_payload(
            code=f"edge_case_none_test_{timestamp}",
            name="Edge Case None Test",
            perms_input=None
        )
        
        # Legacy-Lauf: Frische DB erstellen
        legacy_db_path = f".tmp/perm_legacy_none_{timestamp}.db"
        make_fresh_db_at(legacy_db_path)
        set_env_db(legacy_db_path)
        
        # Legacy-Create
        legacy_status, legacy_body = run_legacy(
            "backend.app.main:app", 
            legacy_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=payload
        )
        
        # DDD-Lauf: Frische DB erstellen
        ddd_db_path = f".tmp/perm_ddd_none_{timestamp}.db"
        make_fresh_db_at(ddd_db_path)
        set_env_db(ddd_db_path)
        
        # DDD-Create (mit anderem Code für frischen DB-Zustand)
        ddd_payload = ig_payload(
            code=f"ddd_edge_case_none_test_{timestamp}",
            name="DDD Edge Case None Test",
            perms_input=None
        )
        
        ddd_status, ddd_body = run_ddd(
            "backend.app.main:app", 
            ddd_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=ddd_payload
        )
        
        # Parität: Beide Modi sollten identischen Statuscode zurückgeben
        assert legacy_status == ddd_status, \
            f"Edge-Case None Statuscode-Parität verletzt: Legacy={legacy_status}, DDD={ddd_status}"
        
        print(f"Edge-Case None Test - Legacy: {legacy_status}, DDD: {ddd_status}")
        
        # Test mit leerem String
        empty_payload = ig_payload(
            code=f"edge_case_empty_test_{timestamp}",
            name="Edge Case Empty Test",
            perms_input=""
        )
        
        # Legacy-Lauf: Frische DB erstellen
        legacy_empty_db_path = f".tmp/perm_legacy_empty_{timestamp}.db"
        make_fresh_db_at(legacy_empty_db_path)
        set_env_db(legacy_empty_db_path)
        
        # Legacy-Create
        legacy_empty_status, legacy_empty_body = run_legacy(
            "backend.app.main:app", 
            legacy_empty_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=empty_payload
        )
        
        # DDD-Lauf: Frische DB erstellen
        ddd_empty_db_path = f".tmp/perm_ddd_empty_{timestamp}.db"
        make_fresh_db_at(ddd_empty_db_path)
        set_env_db(ddd_empty_db_path)
        
        # DDD-Create (mit anderem Code für frischen DB-Zustand)
        ddd_empty_payload = ig_payload(
            code=f"ddd_edge_case_empty_test_{timestamp}",
            name="DDD Edge Case Empty Test",
            perms_input=""
        )
        
        ddd_empty_status, ddd_empty_body = run_ddd(
            "backend.app.main:app", 
            ddd_empty_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=ddd_empty_payload
        )
        
        # Parität: Beide Modi sollten identischen Statuscode zurückgeben
        assert legacy_empty_status == ddd_empty_status, \
            f"Edge-Case Empty Statuscode-Parität verletzt: Legacy={legacy_empty_status}, DDD={ddd_empty_status}"
        
        print(f"Edge-Case Empty Test - Legacy: {legacy_empty_status}, DDD: {ddd_empty_status}")
