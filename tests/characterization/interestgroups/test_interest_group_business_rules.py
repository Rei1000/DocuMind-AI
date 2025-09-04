"""
Charakterisierungstest für InterestGroup Business Rules
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


class TestInterestGroupBusinessRules:
    """Test für InterestGroup Business Rules und Validierungen (Legacy vs DDD)"""
    
    def test_interest_group_entity_creation(self):
        """Test: InterestGroup Entity kann erstellt werden (Legacy vs DDD)"""
        timestamp = int(time.time())
        
        # Test mit minimalen Daten
        payload = ig_payload(
            code=f"test_business_group_{timestamp}",
            name="Test Business Group",
            perms_input=None
        )
        
        # Legacy-Lauf: Frische DB erstellen
        legacy_db_path = f".tmp/perm_legacy_{timestamp}.db"
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
        ddd_db_path = f".tmp/perm_ddd_{timestamp}.db"
        make_fresh_db_at(ddd_db_path)
        set_env_db(ddd_db_path)
        
        # DDD-Create (mit anderem Code für frischen DB-Zustand)
        ddd_payload = ig_payload(
            code=f"ddd_test_business_group_{timestamp}",
            name="Test Business Group",  # Gleicher Name wie Legacy
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
            f"Entity Creation Statuscode-Parität verletzt: Legacy={legacy_status}, DDD={ddd_status}"
        
        print(f"Entity Creation Test - Legacy: {legacy_status}, DDD: {ddd_status}")
        
        # Wenn beide erfolgreich waren, vergleiche die Responses
        if legacy_status == 200 and ddd_status == 200:
            # Grundlegende Felder sollten identisch sein
            assert legacy_body["name"] == ddd_body["name"], "Name sollte identisch sein"
            assert legacy_body["is_active"] == ddd_body["is_active"], "is_active sollte identisch sein"
    
    def test_interest_group_permissions_parsing(self):
        """Test: get_group_permissions_list() parst verschiedene Formate identisch (Legacy vs DDD)"""
        timestamp = int(time.time())
        
        # Test 1: JSON-String
        json_payload = ig_payload(
            code=f"json_permissions_group_{timestamp}",
            name="JSON Permissions Group",
            perms_input='["perm1", "perm2", "perm3"]'
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
            json_data=json_payload
        )
        
        # DDD-Lauf: Frische DB erstellen
        ddd_db_path = f".tmp/perm_ddd_json_{timestamp}.db"
        make_fresh_db_at(ddd_db_path)
        set_env_db(ddd_db_path)
        
        # DDD-Create (mit anderem Code für frischen DB-Zustand)
        ddd_payload = ig_payload(
            code=f"ddd_json_permissions_group_{timestamp}",
            name="DDD JSON Permissions Group",
            perms_input='["perm1", "perm2", "perm3"]'
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
        
        # Test 2: Komma-separierte Strings
        comma_payload = ig_payload(
            code=f"comma_permissions_group_{timestamp}",
            name="Comma Permissions Group",
            perms_input="perm1, perm2, perm3"
        )
        
        # Legacy-Lauf: Frische DB erstellen
        legacy_comma_db_path = f".tmp/perm_legacy_comma_{timestamp}.db"
        make_fresh_db_at(legacy_comma_db_path)
        set_env_db(legacy_comma_db_path)
        
        # Legacy-Create
        legacy_comma_status, legacy_comma_body = run_legacy(
            "backend.app.main:app", 
            legacy_comma_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=comma_payload
        )
        
        # DDD-Lauf: Frische DB erstellen
        ddd_comma_db_path = f".tmp/perm_ddd_comma_{timestamp}.db"
        make_fresh_db_at(ddd_comma_db_path)
        set_env_db(ddd_comma_db_path)
        
        # DDD-Create (mit anderem Code für frischen DB-Zustand)
        ddd_comma_payload = ig_payload(
            code=f"ddd_comma_permissions_group_{timestamp}",
            name="DDD Comma Permissions Group",
            perms_input="perm1, perm2, perm3"
        )
        
        ddd_comma_status, ddd_comma_body = run_ddd(
            "backend.app.main:app", 
            ddd_comma_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=ddd_comma_payload
        )
        
        # Parität: Beide Modi sollten identischen Statuscode zurückgeben
        assert legacy_comma_status == ddd_comma_status, \
            f"Comma-String Statuscode-Parität verletzt: Legacy={legacy_comma_status}, DDD={ddd_comma_status}"
        
        print(f"Comma-String Test - Legacy: {legacy_comma_status}, DDD: {ddd_comma_status}")
        
        # Test 3: Liste von Strings
        list_payload = ig_payload(
            code=f"list_permissions_group_{timestamp}",
            name="List Permissions Group",
            perms_input=["perm1", "perm2", "perm3"]
        )
        
        # Legacy-Lauf: Frische DB erstellen
        legacy_list_db_path = f".tmp/perm_legacy_list_{timestamp}.db"
        make_fresh_db_at(legacy_list_db_path)
        set_env_db(legacy_list_db_path)
        
        # Legacy-Create
        legacy_list_status, legacy_list_body = run_legacy(
            "backend.app.main:app", 
            legacy_list_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=list_payload
        )
        
        # DDD-Lauf: Frische DB erstellen
        ddd_list_db_path = f".tmp/perm_ddd_list_{timestamp}.db"
        make_fresh_db_at(ddd_list_db_path)
        set_env_db(ddd_list_db_path)
        
        # DDD-Create (mit anderem Code für frischen DB-Zustand)
        ddd_list_payload = ig_payload(
            code=f"ddd_list_permissions_group_{timestamp}",
            name="DDD List Permissions Group",
            perms_input=["perm1", "perm2", "perm3"]
        )
        
        ddd_list_status, ddd_list_body = run_ddd(
            "backend.app.main:app", 
            ddd_list_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=ddd_list_payload
        )
        
        # Parität: Beide Modi sollten identischen Statuscode zurückgeben
        assert legacy_list_status == ddd_list_status, \
            f"List-Input Statuscode-Parität verletzt: Legacy={legacy_list_status}, DDD={ddd_list_status}"
        
        print(f"List-Input Test - Legacy: {legacy_list_status}, DDD: {ddd_list_status}")
        
        # Test 4: Leere Permissions
        empty_payload = ig_payload(
            code=f"empty_permissions_group_{timestamp}",
            name="Empty Permissions Group",
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
            code=f"ddd_empty_permissions_group_{timestamp}",
            name="DDD Empty Permissions Group",
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
            f"Empty-String Statuscode-Parität verletzt: Legacy={legacy_empty_status}, DDD={ddd_empty_status}"
        
        print(f"Empty-String Test - Legacy: {legacy_empty_status}, DDD: {ddd_empty_status}")
        
        # Test 5: None Permissions
        none_payload = ig_payload(
            code=f"none_permissions_group_{timestamp}",
            name="None Permissions Group",
            perms_input=None
        )
        
        # Legacy-Lauf: Frische DB erstellen
        legacy_none_db_path = f".tmp/perm_legacy_none_{timestamp}.db"
        make_fresh_db_at(legacy_none_db_path)
        set_env_db(legacy_none_db_path)
        
        # Legacy-Create
        legacy_none_status, legacy_none_body = run_legacy(
            "backend.app.main:app", 
            legacy_none_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=none_payload
        )
        
        # DDD-Lauf: Frische DB erstellen
        ddd_none_db_path = f".tmp/perm_ddd_none_{timestamp}.db"
        make_fresh_db_at(ddd_none_db_path)
        set_env_db(ddd_none_db_path)
        
        # DDD-Create (mit anderem Code für frischen DB-Zustand)
        ddd_none_payload = ig_payload(
            code=f"ddd_none_permissions_group_{timestamp}",
            name="DDD None Permissions Group",
            perms_input=None
        )
        
        ddd_none_status, ddd_none_body = run_ddd(
            "backend.app.main:app", 
            ddd_none_db_path, 
            "POST", 
            "/api/interest-groups", 
            json_data=ddd_none_payload
        )
        
        # Parität: Beide Modi sollten identischen Statuscode zurückgeben
        assert legacy_none_status == ddd_none_status, \
            f"None-Input Statuscode-Parität verletzt: Legacy={legacy_none_status}, DDD={ddd_none_status}"
        
        print(f"None-Input Test - Legacy: {legacy_none_status}, DDD: {ddd_none_status}")
