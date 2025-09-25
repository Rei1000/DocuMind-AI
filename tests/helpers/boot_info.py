"""
Boot-Info Helper für Regression-Tests
Sichere Ausgabe von Datenbank-Bootstrap-Informationen
"""
import os
import sqlite3
import time
from typing import Optional


def print_boot_info(db_path_abs: str) -> None:
    """
    Gibt Bootstrap-Informationen für die Test-Datenbank aus.
    
    Args:
        db_path_abs: Absoluter Pfad zur SQLite-Datenbank
    """
    # Prüfe, ob die Datei existiert
    if not os.path.exists(db_path_abs):
        print(f"[BOOT] missing db={db_path_abs}")
        return
    
    try:
        # Verbindung mit Timeout und Retry-Logik
        conn = None
        for attempt in range(2):
            try:
                conn = sqlite3.connect(
                    db_path_abs, 
                    timeout=2.0 if attempt > 0 else 1.0,
                    check_same_thread=False
                )
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt == 0:
                    time.sleep(0.2)
                    continue
                raise
        
        if conn is None:
            print(f"[BOOT-ERR] sqlite3.OperationalError: Could not connect after retries")
            return
        
        cursor = conn.cursor()
        
        # PRAGMA database_list holen
        cursor.execute("PRAGMA database_list")
        pragma_result = cursor.fetchone()
        pragma_file = pragma_result[2] if pragma_result else "unknown"
        
        # Tabellen-Namen holen (erste 5)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name LIMIT 5")
        table_names = [row[0] for row in cursor.fetchall()]
        first5 = ",".join(table_names)
        
        # Tabellen-Anzahl holen
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        # Ausgabe
        print(f"[BOOT] db={db_path_abs} pragma_file={pragma_file} tables={table_count} first5={first5}")
        
        conn.close()
        
    except Exception as e:
        exc_class = type(e).__name__
        msg = str(e)
        print(f"[BOOT-ERR] {exc_class}: {msg}")
        if conn:
            try:
                conn.close()
            except:
                pass
