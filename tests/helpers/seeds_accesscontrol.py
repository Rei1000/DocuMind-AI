"""
AccessControl Seeds für deterministische Test-Daten
Erstellt Users, Roles, Permissions, Memberships für RBAC-Tests
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


def seed_accesscontrol_tables(connection: sqlite3.Connection) -> None:
    """
    Erstellt deterministische Seeds für AccessControl-Tests
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
    """
    cursor = connection.cursor()
    
    # 1. Interest Groups (falls nicht vorhanden)
    interest_groups = [
        {
            "id": 1,
            "name": "Quality Management",
            "code": "quality_management",
            "description": "Qualitätsmanagement und Compliance",
            "group_permissions": json.dumps(["final_approval", "system_administration", "audit_management"]),
            "is_external": False,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": 2,
            "name": "Product Development",
            "code": "product_development",
            "description": "Produktentwicklung und Design",
            "group_permissions": json.dumps(["design_approval", "change_management", "technical_review"]),
            "is_external": False,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": 3,
            "name": "External Auditors",
            "code": "external_auditors",
            "description": "Externe Auditoren und Zertifizierer",
            "group_permissions": json.dumps(["audit_read", "compliance_check"]),
            "is_external": True,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for group in interest_groups:
        cursor.execute("""
            INSERT OR IGNORE INTO interest_groups 
            (id, name, code, description, group_permissions, is_external, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            group["id"], group["name"], group["code"], group["description"],
            group["group_permissions"], group["is_external"], group["is_active"], group["created_at"]
        ))
    
    # 2. Users mit verschiedenen Rollen und Berechtigungen
    users = [
        {
            "id": 1,
            "email": "admin@company.com",
            "full_name": "System Administrator",
            "employee_id": "ADM001",
            "organizational_unit": "IT",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K.8K.8K",  # "admin123"
            "individual_permissions": json.dumps(["system_administration", "user_management", "audit_management"]),
            "is_department_head": True,
            "approval_level": 5,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": 2,
            "email": "qm.manager@company.com",
            "full_name": "Dr. Maria Qualität",
            "employee_id": "QM001",
            "organizational_unit": "Qualitätsmanagement",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K.8K.8K",  # "qm123"
            "individual_permissions": json.dumps(["final_approval", "gap_analysis", "system_administration"]),
            "is_department_head": True,
            "approval_level": 4,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": 3,
            "email": "dev.lead@company.com",
            "full_name": "Tom Schneider",
            "employee_id": "DEV001",
            "organizational_unit": "Produktentwicklung",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K.8K.8K",  # "dev123"
            "individual_permissions": json.dumps(["design_approval", "change_management"]),
            "is_department_head": True,
            "approval_level": 3,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": 4,
            "email": "team.member@company.com",
            "full_name": "Anna Müller",
            "employee_id": "TM001",
            "organizational_unit": "Produktentwicklung",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K.8K.8K",  # "team123"
            "individual_permissions": json.dumps([]),
            "is_department_head": False,
            "approval_level": 1,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": 5,
            "email": "auditor@external.com",
            "full_name": "John Auditor",
            "employee_id": "EXT001",
            "organizational_unit": "External",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K.8K.8K",  # "audit123"
            "individual_permissions": json.dumps(["audit_read", "compliance_check"]),
            "is_department_head": False,
            "approval_level": 1,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for user in users:
        cursor.execute("""
            INSERT OR IGNORE INTO users 
            (id, email, full_name, employee_id, organizational_unit, hashed_password, 
             individual_permissions, is_department_head, approval_level, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user["id"], user["email"], user["full_name"], user["employee_id"],
            user["organizational_unit"], user["hashed_password"], user["individual_permissions"],
            user["is_department_head"], user["approval_level"], user["is_active"], user["created_at"]
        ))
    
    # 3. User-Group-Memberships (Many-to-Many)
    memberships = [
        {
            "id": 1,
            "user_id": 1,  # Admin
            "interest_group_id": 1,  # Quality Management
            "role_in_group": "System Administrator",
            "approval_level": 5,
            "is_department_head": True,
            "is_active": True,
            "joined_at": datetime.now().isoformat(),
            "assigned_by_id": 1,
            "notes": "System Admin in QM"
        },
        {
            "id": 2,
            "user_id": 2,  # QM Manager
            "interest_group_id": 1,  # Quality Management
            "role_in_group": "QM Manager",
            "approval_level": 4,
            "is_department_head": True,
            "is_active": True,
            "joined_at": datetime.now().isoformat(),
            "assigned_by_id": 1,
            "notes": "QM Manager"
        },
        {
            "id": 3,
            "user_id": 3,  # Dev Lead
            "interest_group_id": 2,  # Product Development
            "role_in_group": "Team Lead",
            "approval_level": 3,
            "is_department_head": True,
            "is_active": True,
            "joined_at": datetime.now().isoformat(),
            "assigned_by_id": 1,
            "notes": "Dev Team Lead"
        },
        {
            "id": 4,
            "user_id": 4,  # Team Member
            "interest_group_id": 2,  # Product Development
            "role_in_group": "Developer",
            "approval_level": 1,
            "is_department_head": False,
            "is_active": True,
            "joined_at": datetime.now().isoformat(),
            "assigned_by_id": 3,
            "notes": "Team Member"
        },
        {
            "id": 5,
            "user_id": 5,  # External Auditor
            "interest_group_id": 3,  # External Auditors
            "role_in_group": "External Auditor",
            "approval_level": 1,
            "is_department_head": False,
            "is_active": True,
            "joined_at": datetime.now().isoformat(),
            "assigned_by_id": 1,
            "notes": "External Auditor"
        },
        {
            "id": 6,
            "user_id": 2,  # QM Manager (Multi-Group)
            "interest_group_id": 2,  # Product Development
            "role_in_group": "QM Representative",
            "approval_level": 2,
            "is_department_head": False,
            "is_active": True,
            "joined_at": datetime.now().isoformat(),
            "assigned_by_id": 1,
            "notes": "QM Rep in Dev"
        }
    ]
    
    for membership in memberships:
        cursor.execute("""
            INSERT OR IGNORE INTO user_group_memberships 
            (id, user_id, interest_group_id, role_in_group, approval_level, 
             is_department_head, is_active, joined_at, assigned_by_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            membership["id"], membership["user_id"], membership["interest_group_id"],
            membership["role_in_group"], membership["approval_level"], membership["is_department_head"],
            membership["is_active"], membership["joined_at"], membership["assigned_by_id"], membership["notes"]
        ))
    
    connection.commit()


def get_test_user_data(user_type: str) -> Dict[str, Any]:
    """
    Gibt Test-User-Daten für verschiedene Szenarien zurück
    
    Args:
        user_type: "admin", "qm_manager", "dev_lead", "team_member", "external_auditor"
        
    Returns:
        Dict mit User-Daten
    """
    user_data = {
        "admin": {
            "email": "admin@company.com",
            "full_name": "System Administrator",
            "employee_id": "ADM001",
            "organizational_unit": "IT",
            "individual_permissions": ["system_administration", "user_management", "audit_management"],
            "is_department_head": True,
            "approval_level": 5
        },
        "qm_manager": {
            "email": "qm.manager@company.com",
            "full_name": "Dr. Maria Qualität",
            "employee_id": "QM001",
            "organizational_unit": "Qualitätsmanagement",
            "individual_permissions": ["final_approval", "gap_analysis", "system_administration"],
            "is_department_head": True,
            "approval_level": 4
        },
        "dev_lead": {
            "email": "dev.lead@company.com",
            "full_name": "Tom Schneider",
            "employee_id": "DEV001",
            "organizational_unit": "Produktentwicklung",
            "individual_permissions": ["design_approval", "change_management"],
            "is_department_head": True,
            "approval_level": 3
        },
        "team_member": {
            "email": "team.member@company.com",
            "full_name": "Anna Müller",
            "employee_id": "TM001",
            "organizational_unit": "Produktentwicklung",
            "individual_permissions": [],
            "is_department_head": False,
            "approval_level": 1
        },
        "external_auditor": {
            "email": "auditor@external.com",
            "full_name": "John Auditor",
            "employee_id": "EXT001",
            "organizational_unit": "External",
            "individual_permissions": ["audit_read", "compliance_check"],
            "is_department_head": False,
            "approval_level": 1
        }
    }
    
    return user_data.get(user_type, {})


def get_test_group_data(group_type: str) -> Dict[str, Any]:
    """
    Gibt Test-Group-Daten für verschiedene Szenarien zurück
    
    Args:
        group_type: "quality_management", "product_development", "external_auditors"
        
    Returns:
        Dict mit Group-Daten
    """
    group_data = {
        "quality_management": {
            "name": "Quality Management",
            "code": "quality_management",
            "description": "Qualitätsmanagement und Compliance",
            "group_permissions": ["final_approval", "system_administration", "audit_management"],
            "is_external": False
        },
        "product_development": {
            "name": "Product Development",
            "code": "product_development",
            "description": "Produktentwicklung und Design",
            "group_permissions": ["design_approval", "change_management", "technical_review"],
            "is_external": False
        },
        "external_auditors": {
            "name": "External Auditors",
            "code": "external_auditors",
            "description": "Externe Auditoren und Zertifizierer",
            "group_permissions": ["audit_read", "compliance_check"],
            "is_external": True
        }
    }
    
    return group_data.get(group_type, {})


def get_test_membership_data(user_id: int, group_id: int, role: str = "Member") -> Dict[str, Any]:
    """
    Gibt Test-Membership-Daten zurück
    
    Args:
        user_id: User-ID
        group_id: Group-ID
        role: Rolle in der Gruppe
        
    Returns:
        Dict mit Membership-Daten
    """
    return {
        "user_id": user_id,
        "interest_group_id": group_id,
        "role_in_group": role,
        "approval_level": 1,
        "is_department_head": False,
        "is_active": True,
        "notes": f"Test membership for user {user_id} in group {group_id}"
    }


def seed_superuser_qms_admin(connection: sqlite3.Connection) -> None:
    """
    Legt Superuser qms.admin mit aktivem Status und Superuser-Kennzeichen an
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
    """
    cursor = connection.cursor()
    
    # Superuser qms.admin
    superuser = {
        "id": 999,
        "email": "qms.admin",
        "full_name": "QMS Superuser",
        "employee_id": "QMS001",
        "organizational_unit": "System",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K.8K.8K",  # "admin123"
        "individual_permissions": json.dumps(["*"]),  # Vollzugriff
        "is_department_head": True,
        "approval_level": 999,  # Höchste Stufe
        "is_active": True,
        "is_superuser": True,  # Superuser-Flag
        "created_at": datetime.now().isoformat()
    }
    
    cursor.execute("""
        INSERT OR REPLACE INTO users 
        (id, email, full_name, employee_id, organizational_unit, hashed_password, 
         individual_permissions, is_department_head, approval_level, is_active, is_superuser, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        superuser["id"], superuser["email"], superuser["full_name"], superuser["employee_id"],
        superuser["organizational_unit"], superuser["hashed_password"], superuser["individual_permissions"],
        superuser["is_department_head"], superuser["approval_level"], superuser["is_active"], 
        superuser["is_superuser"], superuser["created_at"]
    ))
    
    connection.commit()


def seed_basic_users(connection: sqlite3.Connection, n: int = 2) -> None:
    """
    Legt n normale, aktive Benutzer an
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
        n: Anzahl der Benutzer (default: 2)
    """
    cursor = connection.cursor()
    
    for i in range(1, n + 1):
        user = {
            "id": 100 + i,
            "email": f"user{i}@company.com",
            "full_name": f"Test User {i}",
            "employee_id": f"TU{i:03d}",
            "organizational_unit": "Test",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K.8K.8K",  # "user123"
            "individual_permissions": json.dumps([]),  # Keine speziellen Permissions
            "is_department_head": False,
            "approval_level": 1,
            "is_active": True,
            "is_superuser": False,
            "created_at": datetime.now().isoformat()
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO users 
            (id, email, full_name, employee_id, organizational_unit, hashed_password, 
             individual_permissions, is_department_head, approval_level, is_active, is_superuser, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user["id"], user["email"], user["full_name"], user["employee_id"],
            user["organizational_unit"], user["hashed_password"], user["individual_permissions"],
            user["is_department_head"], user["approval_level"], user["is_active"], 
            user["is_superuser"], user["created_at"]
        ))
    
    connection.commit()


def seed_roles_and_permissions(connection: sqlite3.Connection) -> None:
    """
    Legt Rollen und Permissions an (falls separate Tabellen vorhanden)
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
    """
    cursor = connection.cursor()
    
    # Prüfe ob roles-Tabelle existiert
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")
    if cursor.fetchone():
        # Roles
        roles = [
            {"id": 1, "name": "admin", "description": "System Administrator", "is_active": True},
            {"id": 2, "name": "editor", "description": "Content Editor", "is_active": True},
            {"id": 3, "name": "viewer", "description": "Read-only User", "is_active": True}
        ]
        
        for role in roles:
            cursor.execute("""
                INSERT OR REPLACE INTO roles 
                (id, name, description, is_active)
                VALUES (?, ?, ?, ?)
            """, (role["id"], role["name"], role["description"], role["is_active"]))
    
    # Prüfe ob permissions-Tabelle existiert
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='permissions'")
    if cursor.fetchone():
        # Permissions
        permissions = [
            {"id": 1, "code": "users:create", "name": "Create Users", "description": "Create new users"},
            {"id": 2, "code": "users:update", "name": "Update Users", "description": "Update existing users"},
            {"id": 3, "code": "users:delete", "name": "Delete Users", "description": "Delete users"},
            {"id": 4, "code": "users:read", "name": "Read Users", "description": "View user information"},
            {"id": 5, "code": "roles:assign", "name": "Assign Roles", "description": "Assign roles to users"},
            {"id": 6, "code": "roles:revoke", "name": "Revoke Roles", "description": "Revoke roles from users"},
            {"id": 7, "code": "system:admin", "name": "System Administration", "description": "Full system access"}
        ]
        
        for perm in permissions:
            cursor.execute("""
                INSERT OR REPLACE INTO permissions 
                (id, code, name, description)
                VALUES (?, ?, ?, ?)
            """, (perm["id"], perm["code"], perm["name"], perm["description"]))
    
    connection.commit()


def seed_user(
    connection: sqlite3.Connection,
    email: str,
    full_name: str = "Test User",
    employee_id: str = "TEST001",
    organizational_unit: str = "Test",
    individual_permissions: Optional[List[str]] = None,
    is_active: bool = True,
    is_superuser: bool = False,
    approval_level: int = 1
) -> int:
    """
    Legt deterministisch einen User per direkter DB-Insert an
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
        email: Email-Adresse
        full_name: Vollständiger Name
        employee_id: Mitarbeiternummer
        organizational_unit: Abteilung
        individual_permissions: Individuelle Berechtigungen
        is_active: Aktiver Status
        is_superuser: Superuser-Status
        approval_level: Freigabe-Level
    
    Returns:
        int: ID des erstellten Users
    """
    cursor = connection.cursor()
    
    if individual_permissions is None:
        individual_permissions = []
    
    # Hole nächste verfügbare ID
    cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM users")
    user_id = cursor.fetchone()[0]
    
    user_data = {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "employee_id": employee_id,
        "organizational_unit": organizational_unit,
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K.8K.8K",  # "test123"
        "individual_permissions": json.dumps(individual_permissions, ensure_ascii=False),
        "is_department_head": False,
        "approval_level": approval_level,
        "is_active": is_active,
        "is_superuser": is_superuser,
        "created_at": datetime.now().isoformat()
    }
    
    cursor.execute("""
        INSERT OR REPLACE INTO users 
        (id, email, full_name, employee_id, organizational_unit, hashed_password, 
         individual_permissions, is_department_head, approval_level, is_active, is_superuser, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_data["id"], user_data["email"], user_data["full_name"], user_data["employee_id"],
        user_data["organizational_unit"], user_data["hashed_password"], user_data["individual_permissions"],
        user_data["is_department_head"], user_data["approval_level"], user_data["is_active"], 
        user_data["is_superuser"], user_data["created_at"]
    ))
    
    connection.commit()
    return user_id


def hard_delete_user(connection: sqlite3.Connection, user_id: int) -> bool:
    """
    Löscht testseitig per DB-Delete (nur Tests!)
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
        user_id: ID des zu löschenden Users
    
    Returns:
        bool: True wenn erfolgreich gelöscht
    """
    cursor = connection.cursor()
    
    try:
        # Prüfe ob User existiert
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            return False
        
        # Lösche User
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        connection.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"[SEEDS] Hard delete failed: {e}")
        return False


def update_user_field(
    connection: sqlite3.Connection,
    user_id: int,
    field: str,
    value: Any
) -> bool:
    """
    Aktualisiert ein User-Feld per direkter DB-Update (nur Tests!)
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
        user_id: ID des Users
        field: Feldname
        value: Neuer Wert
    
    Returns:
        bool: True wenn erfolgreich aktualisiert
    """
    cursor = connection.cursor()
    
    try:
        # Prüfe ob User existiert
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            return False
        
        # Update Feld
        if field == "individual_permissions" and isinstance(value, list):
            value = json.dumps(value, ensure_ascii=False)
        
        cursor.execute(f"UPDATE users SET {field} = ? WHERE id = ?", (value, user_id))
        connection.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"[SEEDS] Update field failed: {e}")
        return False


def get_user_by_id(connection: sqlite3.Connection, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Holt User per direkter DB-Abfrage (nur Tests!)
    
    Args:
        connection: SQLite3-Verbindung zur Test-DB
        user_id: ID des Users
    
    Returns:
        Dict mit User-Daten oder None
    """
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Hole Spaltennamen
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Erstelle Dict
        user_data = dict(zip(columns, row))
        
        # Parse individual_permissions
        if user_data.get('individual_permissions'):
            try:
                user_data['individual_permissions'] = json.loads(user_data['individual_permissions'])
            except (json.JSONDecodeError, TypeError):
                user_data['individual_permissions'] = []
        
        return user_data
    except Exception as e:
        print(f"[SEEDS] Get user failed: {e}")
        return None
