"""
Helper-Funktionen für konsistente Test-Payloads
"""

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
