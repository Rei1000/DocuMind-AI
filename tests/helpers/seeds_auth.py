"""
Authentication Seeds für deterministische Test-Daten
Erstellt Users mit Passwörtern und Reset-Tokens für Auth-Tests
"""

import sqlite3
import json
import secrets
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .password_policy import make_password_hash, generate_secure_password


def seed_user_with_password(
    connection: sqlite3.Connection,
    email: str,
    plain_password: str,
    full_name: str = "Test User",
    employee_id: str = "TEST001",
    organizational_unit: str = "Test",
    is_superuser: bool = False,
    is_active: bool = True
) -> int:
    """
    Legt deterministisch einen User mit Passwort per direkter DB-Insert an
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
        email: Email-Adresse
        plain_password: Klartext-Passwort (wird gehasht)
        full_name: Vollständiger Name
        employee_id: Mitarbeiternummer
        organizational_unit: Abteilung
        is_superuser: Superuser-Status
        is_active: Aktiver Status
    
    Returns:
        int: ID des erstellten Users
    """
    cursor = connection.cursor()
    
    # Hole nächste verfügbare ID
    cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM users")
    user_id = cursor.fetchone()[0]
    
    # Passwort hashen (BCrypt)
    hashed_password = make_password_hash(plain_password, "bcrypt")
    
    user_data = {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "employee_id": employee_id,
        "organizational_unit": organizational_unit,
        "hashed_password": hashed_password,
        "individual_permissions": json.dumps([]),
        "is_department_head": False,
        "approval_level": 1,
        "is_active": is_active,
        "is_superuser": is_superuser,
        "created_at": datetime.now().isoformat()
    }
    
    cursor.execute("""
        INSERT OR REPLACE INTO users 
        (id, email, full_name, employee_id, organizational_unit, hashed_password, 
         individual_permissions, is_department_head, approval_level, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_data["id"], user_data["email"], user_data["full_name"], user_data["employee_id"],
        user_data["organizational_unit"], user_data["hashed_password"], user_data["individual_permissions"],
        user_data["is_department_head"], user_data["approval_level"], user_data["is_active"],
        user_data["created_at"]
    ))
    
    connection.commit()
    return user_id


def create_reset_token(
    connection: sqlite3.Connection,
    user_id: int,
    expires_in_hours: int = 24
) -> str:
    """
    Generiert testseitiges Reset-Token (falls kein Endpoint)
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
        user_id: ID des Users
        expires_in_hours: Ablaufzeit in Stunden
    
    Returns:
        str: Reset-Token
    """
    cursor = connection.cursor()
    
    # Erstelle reset_tokens Tabelle falls nicht vorhanden
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires_at TEXT NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Generiere Token
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + timedelta(hours=expires_in_hours)).isoformat()
    created_at = datetime.now().isoformat()
    
    # Speichere Token
    cursor.execute("""
        INSERT INTO reset_tokens (user_id, token, expires_at, used, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, token, expires_at, False, created_at))
    
    connection.commit()
    return token


def get_reset_token(
    connection: sqlite3.Connection,
    token: str
) -> Optional[Dict[str, Any]]:
    """
    Holt Reset-Token aus der DB
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
        token: Token-String
    
    Returns:
        Dict mit Token-Daten oder None
    """
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT user_id, token, expires_at, used, created_at
            FROM reset_tokens
            WHERE token = ?
        """, (token,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            "user_id": row[0],
            "token": row[1],
            "expires_at": row[2],
            "used": bool(row[3]),
            "created_at": row[3]
        }
    except Exception as e:
        print(f"[SEEDS] Get reset token failed: {e}")
        return None


def mark_token_used(
    connection: sqlite3.Connection,
    token: str
) -> bool:
    """
    Markiert Token als verwendet
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
        token: Token-String
    
    Returns:
        bool: True wenn erfolgreich
    """
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            UPDATE reset_tokens
            SET used = TRUE
            WHERE token = ?
        """, (token,))
        
        connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"[SEEDS] Mark token used failed: {e}")
        return False


def update_user_password(
    connection: sqlite3.Connection,
    user_id: int,
    new_password: str
) -> bool:
    """
    Aktualisiert User-Passwort per direkter DB-Update (nur Tests!)
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
        user_id: ID des Users
        new_password: Neues Klartext-Passwort
    
    Returns:
        bool: True wenn erfolgreich aktualisiert
    """
    cursor = connection.cursor()
    
    try:
        # Prüfe ob User existiert
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            return False
        
        # Passwort hashen
        hashed_password = make_password_hash(new_password, "bcrypt")
        
        # Update Passwort
        cursor.execute("UPDATE users SET hashed_password = ? WHERE id = ?", (hashed_password, user_id))
        connection.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"[SEEDS] Update password failed: {e}")
        return False


def get_user_password_hash(
    connection: sqlite3.Connection,
    user_id: int
) -> Optional[str]:
    """
    Holt User-Passwort-Hash per direkter DB-Abfrage (nur Tests!)
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
        user_id: ID des Users
    
    Returns:
        Hash-Wert oder None
    """
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT hashed_password FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return row[0]
    except Exception as e:
        print(f"[SEEDS] Get password hash failed: {e}")
        return None


def seed_auth_test_users(connection: sqlite3.Connection) -> Dict[str, int]:
    """
    Erstellt Test-Users für Auth-Tests
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
    
    Returns:
        Dict mit User-IDs
    """
    users = {}
    
    # Superuser
    users["superuser"] = seed_user_with_password(
        connection, "qms.admin", "SuperSecure123!", "QMS Superuser", "QMS001", "System", True, True
    )
    
    # Normaler User
    users["normal_user"] = seed_user_with_password(
        connection, "test.user@company.com", "TestPassword123!", "Test User", "TU001", "Test", False, True
    )
    
    # Inaktiver User
    users["inactive_user"] = seed_user_with_password(
        connection, "inactive@company.com", "InactivePass123!", "Inactive User", "IU001", "Test", False, False
    )
    
    # User mit schwachem Passwort
    users["weak_password_user"] = seed_user_with_password(
        connection, "weak@company.com", "123456", "Weak Password User", "WP001", "Test", False, True
    )
    
    return users


def seed_superuser_qms_admin(connection: sqlite3.Connection) -> int:
    """
    Legt Superuser qms.admin an
    
    Returns:
        user_id des Superusers
    """
    return seed_user_with_password(
        connection, "qms.admin@local", "adminpass123", 
        "QMS Admin", "ADMIN001", "Administration", True, True
    )


def seed_basic_user(connection: sqlite3.Connection, email: str = "user1@local") -> int:
    """
    Legt normalen aktiven User an
    
    Returns:
        user_id des Users
    """
    return seed_user_with_password(
        connection, email, "userpass123", 
        "Test User", "USER001", "Test Department", False, True
    )


def ensure_admin_role_assignment(connection: sqlite3.Connection, user_id: int) -> None:
    """
    Legt Rolle "admin" an und verknüpft sie mit dem User
    """
    cursor = connection.cursor()
    
    # Rolle "admin" anlegen falls nicht vorhanden
    cursor.execute("INSERT OR IGNORE INTO roles (name) VALUES (?)", ("admin",))
    role_id = cursor.lastrowid
    if role_id == 0:
        cursor.execute("SELECT id FROM roles WHERE name = ?", ("admin",))
        role_id = cursor.fetchone()[0]
    
    # User-Rolle verknüpfen
    cursor.execute("INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
    connection.commit()


def seed_permissions_for_admin(connection: sqlite3.Connection, permissions: List[str]) -> None:
    """
    Legt Permissions an und ordnet sie der admin-Rolle zu
    """
    cursor = connection.cursor()
    
    # Admin-Rolle finden
    cursor.execute("SELECT id FROM roles WHERE name = ?", ("admin",))
    admin_role = cursor.fetchone()
    if not admin_role:
        return
    role_id = admin_role[0]
    
    for perm_code in permissions:
        # Permission anlegen
        cursor.execute("INSERT OR IGNORE INTO permissions (code) VALUES (?)", (perm_code,))
        perm_id = cursor.lastrowid
        if perm_id == 0:
            cursor.execute("SELECT id FROM permissions WHERE code = ?", (perm_code,))
            perm_id = cursor.fetchone()[0]
        
        # Role-Permission verknüpfen
        cursor.execute("INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)", (role_id, perm_id))
    
    connection.commit()


def cleanup_reset_tokens(connection: sqlite3.Connection) -> None:
    """
    Bereinigt abgelaufene Reset-Tokens
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
    """
    cursor = connection.cursor()
    
    try:
        now = datetime.now().isoformat()
        cursor.execute("DELETE FROM reset_tokens WHERE expires_at < ?", (now,))
        connection.commit()
    except Exception as e:
        print(f"[SEEDS] Cleanup reset tokens failed: {e}")


def get_token_expiry_status(
    connection: sqlite3.Connection,
    token: str
) -> Dict[str, Any]:
    """
    Prüft Token-Ablaufstatus
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
        token: Token-String
    
    Returns:
        Dict mit Status-Informationen
    """
    token_data = get_reset_token(connection, token)
    if not token_data:
        return {"valid": False, "expired": False, "used": False, "reason": "Token not found"}
    
    now = datetime.now()
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    
    if token_data["used"]:
        return {"valid": False, "expired": False, "used": True, "reason": "Token already used"}
    
    if now > expires_at:
        return {"valid": False, "expired": True, "used": False, "reason": "Token expired"}
    
    return {"valid": True, "expired": False, "used": False, "reason": "Token valid"}


def seed_token_for_user(
    user_id: int,
    email: str = "test@company.com",
    is_superuser: bool = False,
    claims_override: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generiert Test-JWT für User (Seed-Fallback)
    
    Args:
        user_id: User-ID
        email: Email-Adresse
        is_superuser: Superuser-Status
        claims_override: Zusätzliche Claims
    
    Returns:
        str: JWT-Token
    """
    from .jwt_utils import issue_test_jwt, set_test_secret_keys
    
    # Test-Secret setzen
    set_test_secret_keys()
    
    # JWT generieren
    token = issue_test_jwt(user_id, email, is_superuser, claims_override=claims_override)
    
    print(f"[SEEDS] Test JWT generated for user {user_id}: {token[:20]}...")
    return token


def seed_user_with_jwt(
    connection: sqlite3.Connection,
    email: str,
    plain_password: str,
    full_name: str = "Test User",
    employee_id: str = "TEST001",
    organizational_unit: str = "Test",
    is_superuser: bool = False,
    is_active: bool = True
) -> Dict[str, Any]:
    """
    Legt User mit Passwort an und generiert JWT (Seed-Fallback)
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
        email: Email-Adresse
        plain_password: Klartext-Passwort
        full_name: Vollständiger Name
        employee_id: Mitarbeiternummer
        organizational_unit: Abteilung
        is_superuser: Superuser-Status
        is_active: Aktiver Status
    
    Returns:
        Dict mit user_id und jwt_token
    """
    # User erstellen
    user_id = seed_user_with_password(
        connection, email, plain_password, full_name, employee_id, 
        organizational_unit, is_superuser, is_active
    )
    
    # JWT generieren
    jwt_token = seed_token_for_user(user_id, email, is_superuser)
    
    return {
        "user_id": user_id,
        "jwt_token": jwt_token,
        "email": email,
        "is_superuser": is_superuser
    }
