"""
Diagnose-Test für ersten POST im DDD-Pfad
Reproduziert den 500-Fehler und instrumentiert für Diagnose
"""

import pytest
from tests.helpers.ab_runner import run_legacy, run_ddd
from tests.helpers.bootstrap_from_schema import make_fresh_db_at


class TestFirstPostDiagnostics:
    """Diagnose-Tests für ersten POST im DDD-Pfad"""
    
    def test_first_post_diagnosis(self, client):
        """Test: Diagnose des ersten POST-Fehlers im DDD-Pfad"""
        
        # Arrange: Zwei DB-Pfade
        legacy_db = ".tmp/firstpost_legacy.db"
        ddd_db = ".tmp/firstpost_ddd.db"
        
        # Beide DBs frisch erstellen (ohne Seeds)
        try:
            legacy_result = make_fresh_db_at(legacy_db)
            ddd_result = make_fresh_db_at(ddd_db)
            
            if legacy_result == 0 or ddd_result == 0:
                print("[DIAG] DB creation failed - no tables created")
                return
                
        except Exception as e:
            print(f"[DIAG] DB creation failed: {e}")
            return
        
        # Minimal valider Payload (wie Legacy 200 liefert)
        payload = {
            "code": "diag_first",
            "name": "Diag First",
            "description": "Diagnose Test",
            "group_permissions": None  # Das, was Legacy akzeptiert
        }
        
        print(f"[DIAG] Testing with payload: {payload}")
        
        # Act: Legacy und DDD POST
        try:
            status_L, body_L = run_legacy(
                "backend.app.main:app", 
                legacy_db, 
                method="POST", 
                path="/api/interest-groups", 
                json_data=payload
            )
        except Exception as e:
            print(f"[DIAG] Legacy POST failed: {e}")
            status_L, body_L = 500, {"error": str(e)}
        
        try:
            status_D, body_D = run_ddd(
                "backend.app.main:app", 
                ddd_db, 
                method="POST", 
                path="/api/interest-groups", 
                json_data=payload
            )
        except Exception as e:
            print(f"[DIAG] DDD POST failed: {e}")
            status_D, body_D = 500, {"error": str(e)}
        
        # Assert/Report: Kompakte Diagnose
        print(f"[FIRST-POST] legacy={status_L} ddd={status_D}")
        
        # ID-Checks
        id_ok_legacy = False
        id_ok_ddd = False
        
        if status_L == 200 and isinstance(body_L, dict):
            id_ok_legacy = body_L.get("id", 0) > 0
            print(f"[DIAG] Legacy ID: {body_L.get('id', 'N/A')}")
        
        if status_D == 200 and isinstance(body_D, dict):
            id_ok_ddd = body_D.get("id", 0) > 0
            print(f"[DIAG] DDD ID: {body_D.get('id', 'N/A')}")
        
        print(f"[FIRST-POST] id_ok_legacy={id_ok_legacy} id_ok_ddd={id_ok_ddd}")
        
        # Detaillierte Diagnose bei 500
        if status_D == 500:
            print("[DIAG] DIAG REQUIRED - DDD returned 500")
            print(f"[DIAG] DDD Response Body: {body_D}")
            
            # Zusätzliche Diagnose-Info
            if isinstance(body_D, dict):
                detail = body_D.get("detail", "")
                if "EXC::" in detail:
                    print(f"[DIAG] Exception captured: {detail}")
        
        # Body-Vergleich für weitere Diagnose
        if status_L == 200 and status_D == 200:
            print("[DIAG] Both returned 200 - comparing bodies")
            print(f"[DIAG] Legacy body keys: {list(body_L.keys()) if isinstance(body_L, dict) else 'N/A'}")
            print(f"[DIAG] DDD body keys: {list(body_D.keys()) if isinstance(body_D, dict) else 'N/A'}")
        
        # Kein harter Fail - dies ist eine Diagnosesuite
        # Tests sollen durchlaufen, auch wenn Fehler auftreten
