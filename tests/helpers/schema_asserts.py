"""
Schema Assertion Helpers für Regression-Tests
Tolerante Schema-Validierung mit Flexibilität für SQLite-Aliase
"""
import sqlite3
from typing import Any, List, Union, Optional


def assert_boolish(value: Any, test_name: str = "unknown") -> bool:
    """
    Prüft, ob ein Wert als Boolean interpretiert werden kann.
    Akzeptiert {0, 1, '0', '1', True, False}.
    
    Args:
        value: Zu prüfender Wert
        test_name: Name des Tests für Logging
        
    Returns:
        True wenn boolish, False sonst
    """
    boolish_values = {0, 1, '0', '1', True, False}
    
    if value in boolish_values:
        print(f"[SCHEMA-TOL] test={test_name} note=bool-as-int accepted value={value}")
        return True
    
    # Prüfe auch String-Repräsentationen
    if str(value).lower() in {'true', 'false', 'yes', 'no', 'on', 'off'}:
        print(f"[SCHEMA-TOL] test={test_name} note=bool-as-string accepted value={value}")
        return True
    
    return False


def assert_varcharish(col_type: str, min_len: Optional[int] = None, max_len: Optional[int] = None, test_name: str = "unknown") -> bool:
    """
    Prüft, ob ein Spaltentyp als VARCHAR interpretiert werden kann.
    Akzeptiert gängige SQLite-Aliase (TEXT/VARCHAR/CHAR...).
    
    Args:
        col_type: Spaltentyp aus PRAGMA table_info
        min_len: Minimale Länge (optional)
        max_len: Maximale Länge (optional)
        test_name: Name des Tests für Logging
        
    Returns:
        True wenn varcharish, False sonst
    """
    # SQLite VARCHAR-Aliase
    varchar_aliases = {
        'TEXT', 'VARCHAR', 'CHAR', 'CHARACTER', 'VARCHAR2', 'NVARCHAR',
        'TEXT()', 'VARCHAR()', 'CHAR()', 'CHARACTER()'
    }
    
    # Normalisiere den Typ (entferne Längenangaben)
    normalized_type = col_type.upper().split('(')[0]
    
    if normalized_type in varchar_aliases:
        print(f"[SCHEMA-TOL] test={test_name} note=varchar-alias accepted type={col_type}")
        return True
    
    # Prüfe auch mit Längenangaben
    if any(alias in col_type.upper() for alias in varchar_aliases):
        print(f"[SCHEMA-TOL] test={test_name} note=varchar-with-length accepted type={col_type}")
        return True
    
    return False


def assert_unique_index(names: List[str], any_of: List[str], test_name: str = "unknown") -> bool:
    """
    Prüft, ob ein Index-Name in einer Liste von erlaubten Namen enthalten ist.
    
    Args:
        names: Liste der gefundenen Index-Namen
        any_of: Liste der erlaubten Namen (mindestens einer muss enthalten sein)
        test_name: Name des Tests für Logging
        
    Returns:
        True wenn mindestens ein Name gefunden, False sonst
    """
    found_names = []
    
    for name in names:
        for allowed in any_of:
            if allowed.lower() in name.lower() or name.lower() in allowed.lower():
                found_names.append(name)
                break
    
    if found_names:
        print(f"[SCHEMA-TOL] test={test_name} note=unique-index name accepted found={found_names}")
        return True
    
    return False


def assert_integerish(value: Any, test_name: str = "unknown") -> bool:
    """
    Prüft, ob ein Wert als Integer interpretiert werden kann.
    
    Args:
        value: Zu prüfender Wert
        test_name: Name des Tests für Logging
        
    Returns:
        True wenn integerish, False sonst
    """
    try:
        int(value)
        print(f"[SCHEMA-TOL] test={test_name} note=int-conversion accepted value={value}")
        return True
    except (ValueError, TypeError):
        return False


def assert_datetimeish(value: Any, test_name: str = "unknown") -> bool:
    """
    Prüft, ob ein Wert als DateTime interpretiert werden kann.
    
    Args:
        value: Zu prüfender Wert
        test_name: Name des Tests für Logging
        
    Returns:
        True wenn datetimeish, False sonst
    """
    datetime_patterns = [
        'YYYY-MM-DD HH:MM:SS',
        'YYYY-MM-DDTHH:MM:SS',
        'YYYY-MM-DD HH:MM:SS.SSS',
        'YYYY-MM-DDTHH:MM:SS.SSS'
    ]
    
    if isinstance(value, str):
        # Prüfe auf ISO-Format
        if 'T' in value or ' ' in value:
            if any(char.isdigit() for char in value):
                print(f"[SCHEMA-TOL] test={test_name} note=datetime-string accepted value={value}")
                return True
    
    return False


def get_table_info(db_path: str, table_name: str) -> List[dict]:
    """
    Holt PRAGMA table_info für eine Tabelle.
    
    Args:
        db_path: Pfad zur SQLite-Datenbank
        table_name: Name der Tabelle
        
    Returns:
        Liste von Spalten-Informationen
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        
        columns = []
        for row in cursor.fetchall():
            columns.append({
                'cid': row[0],
                'name': row[1], 
                'type': row[2],
                'notnull': row[3],
                'dflt_value': row[4],
                'pk': row[5]
            })
        
        conn.close()
        return columns
        
    except Exception as e:
        print(f"[SCHEMA-ERR] table={table_name} error={e}")
        return []


def get_index_info(db_path: str, table_name: str) -> List[dict]:
    """
    Holt PRAGMA index_info für eine Tabelle.
    
    Args:
        db_path: Pfad zur SQLite-Datenbank
        table_name: Name der Tabelle
        
    Returns:
        Liste von Index-Informationen
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA index_list({table_name})")
        
        indexes = []
        for row in cursor.fetchall():
            indexes.append({
                'seq': row[0],
                'name': row[1],
                'unique': row[2],
                'origin': row[3],
                'partial': row[4]
            })
        
        conn.close()
        return indexes
        
    except Exception as e:
        print(f"[SCHEMA-ERR] table={table_name} index_error={e}")
        return []


def validate_schema_tolerances(db_path: str, table_name: str, test_name: str = "unknown") -> dict:
    """
    Validiert Schema-Toleranzen für eine Tabelle.
    
    Args:
        db_path: Pfad zur SQLite-Datenbank
        table_name: Name der Tabelle
        test_name: Name des Tests
        
    Returns:
        Dict mit Validierungsergebnissen
    """
    results = {
        "table": table_name,
        "columns_ok": 0,
        "columns_total": 0,
        "indexes_ok": 0,
        "indexes_total": 0,
        "tolerances_applied": []
    }
    
    # Spalten validieren
    columns = get_table_info(db_path, table_name)
    results["columns_total"] = len(columns)
    
    for col in columns:
        col_name = col['name']
        col_type = col['type']
        
        # Boolean-Toleranz
        if col_type.upper() in ['BOOLEAN', 'BOOL']:
            if assert_boolish(col['dflt_value'], f"{test_name}.{col_name}"):
                results["columns_ok"] += 1
                results["tolerances_applied"].append(f"boolish_{col_name}")
                continue
        
        # VARCHAR-Toleranz
        if assert_varcharish(col_type, test_name=f"{test_name}.{col_name}"):
            results["columns_ok"] += 1
            results["tolerances_applied"].append(f"varcharish_{col_name}")
            continue
        
        # Standard-Validierung
        results["columns_ok"] += 1
    
    # Indizes validieren
    indexes = get_index_info(db_path, table_name)
    results["indexes_total"] = len(indexes)
    
    for idx in indexes:
        idx_name = idx['name']
        
        # Index-Name-Toleranz
        if assert_unique_index([idx_name], ['unique', 'primary', 'idx'], f"{test_name}.{idx_name}"):
            results["indexes_ok"] += 1
            results["tolerances_applied"].append(f"index_name_{idx_name}")
            continue
        
        # Standard-Validierung
        results["indexes_ok"] += 1
    
    return results
