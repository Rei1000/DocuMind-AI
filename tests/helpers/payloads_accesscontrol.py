"""
AccessControl Payload-Helper für konsistente Test-Payloads
Erstellt valide JSON-Bodies für RBAC-CRUD und Edge-Fälle
"""

import time
from typing import List, Dict, Any, Optional


def user_payload(
    email: str,
    full_name: str,
    employee_id: str,
    organizational_unit: str = "Test Department",
    individual_permissions: Optional[List[str]] = None,
    is_department_head: bool = False,
    approval_level: int = 1,
    is_active: bool = True,
    is_superuser: bool = False
) -> Dict[str, Any]:
    """
    Erstellt ein konsistentes JSON-Payload für User-CRUD
    
    Args:
        email: Email-Adresse
        full_name: Vollständiger Name
        employee_id: Mitarbeiternummer
        organizational_unit: Abteilung
        individual_permissions: Individuelle Berechtigungen
        is_department_head: Abteilungsleiter-Status
        approval_level: Freigabe-Level (1-5)
        is_active: Aktiver Status
        is_superuser: Superuser-Status
    
    Returns:
        dict: Konsistentes Payload für POST/PUT Requests
    """
    if individual_permissions is None:
        individual_permissions = []
    
    return {
        "email": email,
        "full_name": full_name,
        "employee_id": employee_id,
        "organizational_unit": organizational_unit,
        "individual_permissions": individual_permissions,
        "is_department_head": is_department_head,
        "approval_level": approval_level,
        "is_active": is_active,
        "is_superuser": is_superuser
    }


def unique_user_payload(
    base_email: str,
    base_name: str,
    base_employee_id: str,
    organizational_unit: str = "Test Department",
    individual_permissions: Optional[List[str]] = None,
    is_department_head: bool = False,
    approval_level: int = 1,
    is_active: bool = True,
    is_superuser: bool = False
) -> Dict[str, Any]:
    """
    Erstellt ein eindeutiges JSON-Payload für User-CRUD mit Zeitstempel
    
    Args:
        base_email: Basis-Email (ohne Domain)
        base_name: Basis-Name
        base_employee_id: Basis-Mitarbeiternummer
        organizational_unit: Abteilung
        individual_permissions: Individuelle Berechtigungen
        is_department_head: Abteilungsleiter-Status
        approval_level: Freigabe-Level (1-5)
    
    Returns:
        dict: Eindeutiges Payload für POST/PUT Requests
    """
    timestamp = int(time.time() * 1000)  # Millisekunden für Eindeutigkeit
    
    return user_payload(
        email=f"{base_email}_{timestamp}@company.com",
        full_name=f"{base_name} {timestamp}",
        employee_id=f"{base_employee_id}_{timestamp}",
        organizational_unit=organizational_unit,
        individual_permissions=individual_permissions,
        is_department_head=is_department_head,
        approval_level=approval_level,
        is_active=is_active,
        is_superuser=is_superuser
    )


def membership_payload(
    user_id: int,
    interest_group_id: int,
    role_in_group: str = "Member",
    approval_level: int = 1,
    is_department_head: bool = False,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Erstellt ein konsistentes JSON-Payload für Membership-CRUD
    
    Args:
        user_id: User-ID
        interest_group_id: Interest Group-ID
        role_in_group: Rolle in der Gruppe
        approval_level: Freigabe-Level in der Gruppe
        is_department_head: Abteilungsleiter-Status in der Gruppe
        notes: Bemerkungen
    
    Returns:
        dict: Konsistentes Payload für POST/PUT Requests
    """
    if notes is None:
        notes = f"Test membership for user {user_id} in group {interest_group_id}"
    
    return {
        "user_id": user_id,
        "interest_group_id": interest_group_id,
        "role_in_group": role_in_group,
        "approval_level": approval_level,
        "is_department_head": is_department_head,
        "notes": notes
    }


def login_payload(email: str, password: str) -> Dict[str, str]:
    """
    Erstellt ein Login-Payload
    
    Args:
        email: Email-Adresse
        password: Passwort
    
    Returns:
        dict: Login-Payload
    """
    return {
        "email": email,
        "password": password
    }


def password_change_payload(current_password: str, new_password: str) -> Dict[str, str]:
    """
    Erstellt ein Password-Change-Payload
    
    Args:
        current_password: Aktuelles Passwort
        new_password: Neues Passwort
    
    Returns:
        dict: Password-Change-Payload
    """
    return {
        "current_password": current_password,
        "new_password": new_password
    }


def document_status_change_payload(status: str, comment: Optional[str] = None) -> Dict[str, Any]:
    """
    Erstellt ein Document-Status-Change-Payload
    
    Args:
        status: Neuer Status (DRAFT, REVIEWED, APPROVED, OBSOLETE)
        comment: Optionaler Kommentar
    
    Returns:
        dict: Status-Change-Payload
    """
    payload = {
        "status": status
    }
    
    if comment:
        payload["comment"] = comment
    
    return payload


# Vordefinierte Test-Payloads für häufige Szenarien

def admin_user_payload() -> Dict[str, Any]:
    """Admin-User-Payload"""
    return user_payload(
        email="admin@company.com",
        full_name="System Administrator",
        employee_id="ADM001",
        organizational_unit="IT",
        individual_permissions=["system_administration", "user_management", "audit_management"],
        is_department_head=True,
        approval_level=5
    )


def qm_manager_payload() -> Dict[str, Any]:
    """QM-Manager-User-Payload"""
    return user_payload(
        email="qm.manager@company.com",
        full_name="Dr. Maria Qualität",
        employee_id="QM001",
        organizational_unit="Qualitätsmanagement",
        individual_permissions=["final_approval", "gap_analysis", "system_administration"],
        is_department_head=True,
        approval_level=4
    )


def dev_lead_payload() -> Dict[str, Any]:
    """Dev-Lead-User-Payload"""
    return user_payload(
        email="dev.lead@company.com",
        full_name="Tom Schneider",
        employee_id="DEV001",
        organizational_unit="Produktentwicklung",
        individual_permissions=["design_approval", "change_management"],
        is_department_head=True,
        approval_level=3
    )


def team_member_payload() -> Dict[str, Any]:
    """Team-Member-User-Payload"""
    return user_payload(
        email="team.member@company.com",
        full_name="Anna Müller",
        employee_id="TM001",
        organizational_unit="Produktentwicklung",
        individual_permissions=[],
        is_department_head=False,
        approval_level=1
    )


def external_auditor_payload() -> Dict[str, Any]:
    """External-Auditor-User-Payload"""
    return user_payload(
        email="auditor@external.com",
        full_name="John Auditor",
        employee_id="EXT001",
        organizational_unit="External",
        individual_permissions=["audit_read", "compliance_check"],
        is_department_head=False,
        approval_level=1
    )


def qm_membership_payload(user_id: int) -> Dict[str, Any]:
    """QM-Group-Membership-Payload"""
    return membership_payload(
        user_id=user_id,
        interest_group_id=1,  # Quality Management
        role_in_group="QM Member",
        approval_level=4,
        is_department_head=True,
        notes="QM Group Membership"
    )


def dev_membership_payload(user_id: int) -> Dict[str, Any]:
    """Dev-Group-Membership-Payload"""
    return membership_payload(
        user_id=user_id,
        interest_group_id=2,  # Product Development
        role_in_group="Developer",
        approval_level=1,
        is_department_head=False,
        notes="Dev Group Membership"
    )


def external_auditor_membership_payload(user_id: int) -> Dict[str, Any]:
    """External-Auditor-Group-Membership-Payload"""
    return membership_payload(
        user_id=user_id,
        interest_group_id=3,  # External Auditors
        role_in_group="External Auditor",
        approval_level=1,
        is_department_head=False,
        notes="External Auditor Membership"
    )


# Edge-Case-Payloads

def invalid_user_payload() -> Dict[str, Any]:
    """Ungültiger User-Payload (fehlende Pflichtfelder)"""
    return {
        "email": "invalid-email",  # Ungültige Email
        "full_name": "",  # Leerer Name
        "employee_id": "INV001",
        "approval_level": 6  # Ungültiger Level
    }


def duplicate_user_payload() -> Dict[str, Any]:
    """Duplikat-User-Payload (gleiche Email)"""
    return user_payload(
        email="admin@company.com",  # Gleiche Email wie Admin
        full_name="Duplicate Admin",
        employee_id="DUP001",
        organizational_unit="Test"
    )


def empty_permissions_payload() -> Dict[str, Any]:
    """User-Payload mit leeren Permissions"""
    return user_payload(
        email="empty.perms@company.com",
        full_name="Empty Permissions User",
        employee_id="EMP001",
        individual_permissions=[],
        approval_level=1
    )


def complex_permissions_payload() -> Dict[str, Any]:
    """User-Payload mit komplexen Permissions"""
    return user_payload(
        email="complex.perms@company.com",
        full_name="Complex Permissions User",
        employee_id="CPX001",
        individual_permissions=[
            "system_administration",
            "user_management",
            "audit_management",
            "final_approval",
            "gap_analysis",
            "design_approval",
            "change_management",
            "technical_review"
        ],
        approval_level=4
    )


def multi_group_membership_payload(user_id: int) -> List[Dict[str, Any]]:
    """Multi-Group-Membership-Payloads"""
    return [
        membership_payload(
            user_id=user_id,
            interest_group_id=1,  # Quality Management
            role_in_group="QM Representative",
            approval_level=2,
            is_department_head=False,
            notes="QM Rep"
        ),
        membership_payload(
            user_id=user_id,
            interest_group_id=2,  # Product Development
            role_in_group="Developer",
            approval_level=1,
            is_department_head=False,
            notes="Dev Member"
        )
    ]


def create_user_payload(
    email: str,
    full_name: str,
    employee_id: str,
    organizational_unit: str = "Test Department",
    individual_permissions: Optional[List[str]] = None,
    is_department_head: bool = False,
    approval_level: int = 1,
    is_active: bool = True,
    is_superuser: bool = False
) -> Dict[str, Any]:
    """
    Erstellt ein User-Create-Payload für POST /users
    
    Args:
        email: Email-Adresse
        full_name: Vollständiger Name
        employee_id: Mitarbeiternummer
        organizational_unit: Abteilung
        individual_permissions: Individuelle Berechtigungen
        is_department_head: Abteilungsleiter-Status
        approval_level: Freigabe-Level (1-5)
        is_active: Aktiver Status
        is_superuser: Superuser-Status
    
    Returns:
        dict: User-Create-Payload
    """
    return user_payload(
        email=email,
        full_name=full_name,
        employee_id=employee_id,
        organizational_unit=organizational_unit,
        individual_permissions=individual_permissions,
        is_department_head=is_department_head,
        approval_level=approval_level,
        is_active=is_active,
        is_superuser=is_superuser
    )


def update_user_payload(
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    employee_id: Optional[str] = None,
    organizational_unit: Optional[str] = None,
    individual_permissions: Optional[List[str]] = None,
    is_department_head: Optional[bool] = None,
    approval_level: Optional[int] = None,
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Erstellt ein User-Update-Payload für PUT /users/{id}
    
    Args:
        email: Email-Adresse (optional)
        full_name: Vollständiger Name (optional)
        employee_id: Mitarbeiternummer (optional)
        organizational_unit: Abteilung (optional)
        individual_permissions: Individuelle Berechtigungen (optional)
        is_department_head: Abteilungsleiter-Status (optional)
        approval_level: Freigabe-Level (optional)
        is_active: Aktiver Status (optional)
        is_superuser: Superuser-Status (optional)
    
    Returns:
        dict: User-Update-Payload (nur gesetzte Felder)
    """
    payload = {}
    
    if email is not None:
        payload["email"] = email
    if full_name is not None:
        payload["full_name"] = full_name
    if employee_id is not None:
        payload["employee_id"] = employee_id
    if organizational_unit is not None:
        payload["organizational_unit"] = organizational_unit
    if individual_permissions is not None:
        payload["individual_permissions"] = individual_permissions
    if is_department_head is not None:
        payload["is_department_head"] = is_department_head
    if approval_level is not None:
        payload["approval_level"] = approval_level
    if is_active is not None:
        payload["is_active"] = is_active
    if is_superuser is not None:
        payload["is_superuser"] = is_superuser
    
    return payload


def superuser_qms_admin_payload() -> Dict[str, Any]:
    """Superuser qms.admin Payload"""
    return user_payload(
        email="qms.admin",
        full_name="QMS Superuser",
        employee_id="QMS001",
        organizational_unit="System",
        individual_permissions=["*"],  # Vollzugriff
        is_department_head=True,
        approval_level=999,  # Höchste Stufe
        is_active=True,
        is_superuser=True
    )


def soft_delete_user_payload() -> Dict[str, Any]:
    """Soft Delete User Payload (is_active=false)"""
    return update_user_payload(is_active=False)


def hard_delete_user_payload() -> Dict[str, Any]:
    """Hard Delete User Payload (für DELETE /users/{id})"""
    return {}  # DELETE-Request braucht kein Body
