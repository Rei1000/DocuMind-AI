"""
Helper-Funktionen für konsistente Test-Payloads
"""
import time

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
