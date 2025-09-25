"""
Auth Flow Helper für Regression-Tests
Einheitliche Login- und Guard-Tests für Legacy und DDD Modi
"""
import requests
from typing import Dict, Any, Optional, Tuple
import os


def login_with_client(client, email: str, password: str, mode: str = "legacy") -> Tuple[int, Optional[str]]:
    """
    Führt Login mit TestClient durch und gibt Status-Code und Access-Token zurück.
    
    Args:
        client: FastAPI TestClient
        email: Benutzer-E-Mail
        password: Passwort
        mode: "legacy" oder "ddd"
        
    Returns:
        Tuple von (status_code, access_token)
    """
    try:
        # Login-Payload
        login_data = {
            "email": email,
            "password": password
        }
        
        # Login-Request mit TestClient
        response = client.post("/api/auth/login", json=login_data)
        
        status_code = response.status_code
        
        if status_code == 200:
            try:
                response_data = response.json()
                access_token = response_data.get("access_token")
                print(f"[AUTHFIX] mode={mode} login=200 guard=token_obtained")
                return status_code, access_token
            except Exception as e:
                print(f"[AUTHFIX] mode={mode} login=200 guard=json_error: {e}")
                return status_code, None
        else:
            print(f"[AUTHFIX] mode={mode} login={status_code} guard=failed")
            return status_code, None
            
    except Exception as e:
        print(f"[AUTHFIX] mode={mode} login=error guard=exception: {e}")
        return 500, None


def auth_headers(token: str) -> Dict[str, str]:
    """
    Erstellt Authorization-Header mit Bearer-Token.
    
    Args:
        token: Access-Token
        
    Returns:
        Dict mit Authorization-Header
    """
    return {"Authorization": f"Bearer {token}"}


def guard_get(mode: str, headers: Optional[Dict[str, str]] = None) -> Tuple[int, str]:
    """
    Führt Guard-Request durch (GET /api/auth/me oder ähnlich).
    
    Args:
        mode: "legacy" oder "ddd"
        headers: Optional Authorization-Header
        
    Returns:
        Tuple von (status_code, response_body_preview)
    """
    try:
        base_url = "http://testserver"
        
        # Guard-Endpoint (versuche verschiedene Pfade)
        guard_endpoints = [
            "/api/auth/me",
            "/api/users/me", 
            "/api/auth/guard",
            "/api/guard"
        ]
        
        for endpoint in guard_endpoints:
            try:
                response = requests.get(
                    f"{base_url}{endpoint}",
                    headers=headers or {},
                    timeout=5.0
                )
                
                status_code = response.status_code
                body_preview = response.text[:200] if response.text else ""
                
                print(f"[AUTHFIX] mode={mode} login=ok guard={status_code} endpoint={endpoint}")
                return status_code, body_preview
                
            except requests.exceptions.RequestException:
                continue
        
        # Fallback: Kein Guard-Endpoint gefunden
        print(f"[AUTHFIX] mode={mode} login=ok guard=404 endpoint=not_found")
        return 404, "No guard endpoint found"
        
    except Exception as e:
        print(f"[AUTHFIX] mode={mode} login=ok guard=error: {e}")
        return 500, str(e)


def test_auth_flow_parity() -> Dict[str, Any]:
    """
    Testet Auth-Flow-Parität zwischen Legacy und DDD.
    
    Returns:
        Dict mit Testergebnissen
    """
    results = {
        "legacy": {"login": None, "guard": None},
        "ddd": {"login": None, "guard": None}
    }
    
    # Test-Credentials
    test_users = [
        {"email": "qms.admin", "password": "admin123"},
        {"email": "test@example.com", "password": "test123"}
    ]
    
    for user in test_users:
        for mode in ["legacy", "ddd"]:
            # Login testen
            login_status, token = login(user["email"], user["password"], mode)
            results[mode]["login"] = login_status
            
            if token:
                # Guard testen
                headers = auth_headers(token)
                guard_status, guard_body = guard_get(mode, headers)
                results[mode]["guard"] = guard_status
            else:
                results[mode]["guard"] = "no_token"
    
    return results


def get_test_credentials() -> Dict[str, Dict[str, str]]:
    """
    Gibt Test-Credentials für verschiedene Benutzer zurück.
    
    Returns:
        Dict mit Benutzer-Credentials
    """
    return {
        "admin": {
            "email": "qms.admin",
            "password": "admin123"
        },
        "user": {
            "email": "test@example.com", 
            "password": "test123"
        },
        "normal": {
            "email": "normal@example.com",
            "password": "normal123"
        }
    }


def add_role_to_token(token: str, role: str) -> str:
    """
    Fügt eine Rolle zu einem Token hinzu (nur für Tests).
    
    Args:
        token: Bestehender Token
        role: Rolle die hinzugefügt werden soll
        
    Returns:
        Token mit zusätzlicher Rolle
    """
    try:
        import jwt
        import os
        
        # Token dekodieren
        secret = os.getenv("SECRET_KEY", "test-secret-123")
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        
        # Rolle hinzufügen
        if 'roles' not in payload:
            payload['roles'] = []
        if role not in payload['roles']:
            payload['roles'].append(role)
        
        # Token neu signieren
        new_token = jwt.encode(payload, secret, algorithm=algorithm)
        print(f"[AUTHFIX] role_added={role} to_token")
        return new_token
        
    except Exception as e:
        print(f"[AUTHFIX] role_add_error: {e}")
        return token


def ensure_user_active_in_db(email: str, db_path: str = "/Users/reiner/Documents/DocuMind-AI/.tmp/regression.db") -> bool:
    """
    Stellt sicher, dass ein User in der DB aktiv ist.
    
    Args:
        email: User-E-Mail
        db_path: Pfad zur Datenbank
        
    Returns:
        True wenn User aktiv ist oder aktiviert wurde
    """
    try:
        import sqlite3
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Prüfe ob User existiert und aktiv ist
            cursor.execute("SELECT is_active FROM users WHERE email = ?", (email,))
            result = cursor.fetchone()
            
            if result:
                is_active = result[0]
                if not is_active:
                    # User aktivieren
                    cursor.execute("UPDATE users SET is_active = 1 WHERE email = ?", (email,))
                    conn.commit()
                    print(f"[AUTHFIX] user_activated={email}")
                    return True
                else:
                    print(f"[AUTHFIX] user_already_active={email}")
                    return True
            else:
                print(f"[AUTHFIX] user_not_found={email}")
                return False
                
    except Exception as e:
        print(f"[AUTHFIX] ensure_user_active_error: {e}")
        return False


def add_role_to_user(email: str, role_name: str, db_path: str = "/Users/reiner/Documents/DocuMind-AI/.tmp/regression.db") -> bool:
    """
    Fügt einem User eine Rolle hinzu (nur für Tests).
    
    Args:
        email: User-E-Mail
        role_name: Name der Rolle
        db_path: Pfad zur Datenbank
        
    Returns:
        True wenn Rolle erfolgreich hinzugefügt wurde
    """
    try:
        import sqlite3
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Prüfe ob User existiert
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            user_result = cursor.fetchone()
            
            if not user_result:
                print(f"[AUTHFIX] user_not_found_for_role={email}")
                return False
            
            user_id = user_result[0]
            
            # Prüfe ob Rolle existiert
            cursor.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
            role_result = cursor.fetchone()
            
            if not role_result:
                # Rolle erstellen falls nicht vorhanden
                cursor.execute("INSERT INTO roles (name, description) VALUES (?, ?)", (role_name, f"Test role: {role_name}"))
                role_id = cursor.lastrowid
                print(f"[AUTHFIX] role_created={role_name}")
            else:
                role_id = role_result[0]
            
            # Prüfe ob User-Rolle-Zuordnung bereits existiert
            cursor.execute("SELECT id FROM user_roles WHERE user_id = ? AND role_id = ?", (user_id, role_id))
            if cursor.fetchone():
                print(f"[AUTHFIX] user_role_already_exists={email} role={role_name}")
                return True
            
            # User-Rolle-Zuordnung erstellen
            cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
            conn.commit()
            print(f"[AUTHFIX] role_added_to_user={email} role={role_name}")
            return True
                
    except Exception as e:
        print(f"[AUTHFIX] add_role_to_user_error: {e}")
        return False
