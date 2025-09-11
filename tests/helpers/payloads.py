"""
Helper-Funktionen für konsistente Test-Payloads
"""
import time
import json
from typing import List, Union, Any

def ig_payload(code: str, name: str, perms_input) -> dict:
    """
    Erstellt ein konsistentes JSON-Payload für Interest Groups
    
    Args:
        code: Eindeutiger Code der Gruppe
        name: Name der Gruppe
        perms_input: Permissions - kann sein:
            - Liste: ["read", "write", "delete"]
            - String-JSON: '["read", "write"]'
            - Komma-String: 'read, write'
            - None oder ""
    
    Returns:
        dict: Konsistentes Payload für POST/PUT Requests
    """
    return {
        "code": code,
        "name": name,
        "is_active": True,
        "group_permissions": perms_input
    }

def unique_ig_payload(base_code: str, base_name: str, perms_input) -> dict:
    """
    Erstellt ein eindeutiges JSON-Payload für Interest Groups mit Zeitstempel
    
    Args:
        base_code: Basis-Code der Gruppe
        base_name: Basis-Name der Gruppe
        perms_input: Permissions (siehe ig_payload)
    
    Returns:
        dict: Eindeutiges Payload für POST/PUT Requests
    """
    timestamp = int(time.time() * 1000)  # Millisekunden für Eindeutigkeit
    return ig_payload(
        code=f"{base_code}_{timestamp}",
        name=f"{base_name} {timestamp}",
        perms_input=perms_input
    )


def add_permissions(payload: dict, kind: str) -> dict:
    """
    Fügt Permissions zu einem Payload hinzu basierend auf dem gewünschten Format.
    
    Args:
        payload: Basis-Payload (wird kopiert)
        kind: Art der Permissions - einer von:
            - "empty": Keine Permissions (None oder [])
            - "simple": Einfache Liste ["read", "write"]
            - "complex": Komplexe Liste ["read", "write", "delete", "admin"]
            - "json_string": JSON-String '["read", "write"]'
            - "comma_string": Komma-getrennt "read, write, delete"
            - "list": Standard-Liste ["read", "write", "delete"]
    
    Returns:
        dict: Payload mit hinzugefügten Permissions
    """
    # Payload kopieren
    result = payload.copy()
    
    # Stabile, deduplizierte Permissions basierend auf kind
    if kind == "empty":
        result["group_permissions"] = []
    elif kind == "simple":
        result["group_permissions"] = ["read", "write"]
    elif kind == "complex":
        result["group_permissions"] = ["read", "write", "delete", "admin", "approve"]
    elif kind == "json_string":
        result["group_permissions"] = '["read", "write", "delete"]'
    elif kind == "comma_string":
        result["group_permissions"] = "read, write, delete"
    elif kind == "list":
        result["group_permissions"] = ["read", "write", "delete"]
    else:
        # Fallback zu einfacher Liste
        result["group_permissions"] = ["read", "write"]
    
    return result
