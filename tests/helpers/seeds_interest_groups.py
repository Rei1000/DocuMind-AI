"""
Seed Helper für Interest Groups Tests

Ermöglicht das Einfügen von Test-Daten in frische Test-Datenbanken.
"""

import sqlite3
import json
from typing import Union, List, Optional


def seed_group(db_path: str, code: str, name: str, permissions: Union[List[str], str, None], is_active: bool = True) -> None:
    """
    Fügt einen Interest Group Datensatz in die Datenbank ein
    
    Args:
        db_path: Pfad zur SQLite-Datenbank
        code: Eindeutiger Code der Gruppe
        name: Name der Gruppe
        permissions: Berechtigungen (Liste, JSON-String, Komma-String oder None)
        is_active: Aktiv-Status der Gruppe
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe ob Gruppe bereits existiert (Idempotenz)
        cursor.execute("SELECT id FROM interest_groups WHERE code = ?", (code,))
        if cursor.fetchone():
            # Gruppe existiert bereits, nichts tun
            conn.close()
            return
        
        # Bereite permissions für Speicherung vor
        if isinstance(permissions, list):
            # Liste zu JSON-String konvertieren
            perms_storage = json.dumps(permissions)
        elif isinstance(permissions, str):
            # String unverändert speichern
            perms_storage = permissions
        else:
            # None oder andere Typen als leeren String speichern
            perms_storage = ""
        
        # Füge Gruppe ein
        cursor.execute("""
            INSERT INTO interest_groups (
                code, name, description, group_permissions, 
                ai_functionality, typical_tasks, is_external, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            code, name, None, perms_storage, 
            None, None, False, is_active
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        raise RuntimeError(f"Failed to seed group {code} in {db_path}: {e}")


def seed_clear(db_path: str) -> None:
    """
    Löscht alle Zeilen aus der interest_groups Tabelle (nur für Tests)
    
    Args:
        db_path: Pfad zur SQLite-Datenbank
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM interest_groups")
        conn.commit()
        conn.close()
        
    except Exception as e:
        raise RuntimeError(f"Failed to clear interest_groups in {db_path}: {e}")
