"""
KI-QMS Authentication & Authorization System

Implementiert rollenbasierte Authentifizierung (RBAC) für das KI-QMS System
mit JWT-Tokens und Interessengruppen-basierten Berechtigungen.

Features:
- JWT Token Authentication
- Role-Based Access Control (RBAC)
- Interest Group Permissions
- Password Hashing (bcrypt)
- Session Management

Technologie:
- FastAPI Security Utilities
- python-jose für JWT
- passlib für Password Hashing
- python-multipart für Form Data

Autoren: KI-QMS Entwicklungsteam
Version: 1.0.0 (MVP Phase 1)
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from .database import get_db
from .models import User as UserModel, InterestGroup as InterestGroupModel, UserGroupMembership

# Environment Variables laden
load_dotenv()

# === KONFIGURATION ===
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# === SECURITY SETUP ===
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# === PASSWORD UTILITIES ===

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifiziert ein Klartext-Passwort gegen einen BCrypt-Hash.
    
    Args:
        plain_password (str): Klartext-Passwort vom Benutzer
        hashed_password (str): BCrypt-Hash aus der Datenbank
        
    Returns:
        bool: True wenn Passwort korrekt, False sonst
        
    Security:
        - Verwendet BCrypt für sichere Passwort-Verifikation
        - Timing-Attack resistent durch bcrypt.checkpw()
        - Automatisches Salt-Handling
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Erstellt einen sicheren BCrypt-Hash für ein Passwort.
    
    Args:
        password (str): Klartext-Passwort
        
    Returns:
        str: BCrypt-Hash für Datenbank-Speicherung
        
    Security:
        - BCrypt mit automatischem Salt-Generation
        - Standard-Rounds für sichere aber performante Hashing
        - Einweg-Hash (nicht umkehrbar)
        
    Usage:
        ```python
        password_hash = get_password_hash("user_password123")
        # Speichere password_hash in Datenbank
        ```
    """
    return pwd_context.hash(password)

# === JWT TOKEN UTILITIES ===

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT Access Token erstellen"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """JWT Token verifizieren und Payload extrahieren"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        return {"user_id": user_id, "payload": payload}
    except JWTError:
        return None

# === AUTHENTICATION ===

def authenticate_user(db: Session, email: str, password: str) -> Optional[UserModel]:
    """Benutzer authentifizieren"""
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        return None
    if not user.hashed_password or not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> UserModel:
    """Aktuell authentifizierten Benutzer abrufen"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Token aus Authorization Header extrahieren
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None:
        raise credentials_exception
    
    # Benutzer aus Datenbank laden
    user = db.query(UserModel).filter(UserModel.id == token_data["user_id"]).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """Aktiven (nicht deaktivierten) Benutzer abrufen"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# === AUTHORIZATION (RBAC) ===

def is_qms_admin(user: UserModel) -> bool:
    """
    Prüft ob ein Benutzer der QMS System Administrator ist.
    
    QMS Admin-Kriterien:
    - Email: qms.admin@company.com
    - Approval Level: 4 oder 5
    - Employee ID: QMS001 oder ADMIN001
    - Organizational Unit: QMS System oder IT/System
    
    Args:
        user: UserModel-Instanz
        
    Returns:
        bool: True wenn QMS Admin, False sonst
    """
    return (
        user.email == "qms.admin@company.com" and 
        user.approval_level >= 4 and
        (user.employee_id == "QMS001" or user.employee_id == "ADMIN001")
    )

def is_system_admin(user: UserModel) -> bool:
    """
    Prüft ob ein Benutzer System-Admin-Rechte hat.
    
    System Admins:
    - QMS Admin (qms.admin@company.com)
    - Weitere System Admins (Level 4 + is_department_head)
    
    Args:
        user: UserModel-Instanz
        
    Returns:
        bool: True wenn System Admin, False sonst
    """
    return (
        is_qms_admin(user) or 
        (user.approval_level == 4 and user.is_department_head and user.organizational_unit == "System Administration")
    )

def get_user_permissions(db: Session, user: UserModel) -> List[str]:
    """Alle Berechtigungen eines Benutzers sammeln"""
    permissions = set()
    
    # ✅ SPEZIAL: QMS Admin bekommt automatisch alle Admin-Rechte
    if is_qms_admin(user):
        permissions.update([
            "system_administration",
            "user_management", 
            "all_rights",
            "final_approval",
            "document_management",
            "equipment_management",
            "norm_management"
        ])
        return list(permissions)
    
    # Individuelle Berechtigungen
    if user.individual_permissions:
        try:
            import json
            individual_perms = json.loads(user.individual_permissions)
            if isinstance(individual_perms, list):
                permissions.update(individual_perms)
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Gruppen-Berechtigungen
    memberships = db.query(UserGroupMembership).filter(
        UserGroupMembership.user_id == user.id,
        UserGroupMembership.is_active == True
    ).all()
    
    for membership in memberships:
        group = membership.interest_group
        if group and group.group_permissions:
            try:
                import json
                group_perms = json.loads(group.group_permissions)
                if isinstance(group_perms, list):
                    permissions.update(group_perms)
            except (json.JSONDecodeError, TypeError):
                pass
    
    return list(permissions)

def get_user_groups(db: Session, user: UserModel) -> List[str]:
    """Alle Interessengruppen-Codes eines Benutzers"""
    memberships = db.query(UserGroupMembership).filter(
        UserGroupMembership.user_id == user.id,
        UserGroupMembership.is_active == True
    ).all()
    
    return [membership.interest_group.code for membership in memberships if membership.interest_group]

class PermissionChecker:
    """Klasse für Berechtigungsprüfungen"""
    
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
    
    def __call__(
        self, 
        current_user: UserModel = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> UserModel:
        """Prüfe ob Benutzer erforderliche Berechtigungen hat"""
        user_permissions = get_user_permissions(db, current_user)
        
        # QM hat alle Rechte
        if "all_rights" in user_permissions:
            return current_user
        
        # Prüfe spezifische Berechtigungen
        for required_perm in self.required_permissions:
            if required_perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {required_perm}"
                )
        
        return current_user

class GroupChecker:
    """Klasse für Gruppenzugehörigkeits-Prüfungen"""
    
    def __init__(self, required_groups: List[str]):
        self.required_groups = required_groups
    
    def __call__(
        self, 
        current_user: UserModel = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> UserModel:
        """Prüfe ob Benutzer zu erforderlichen Gruppen gehört"""
        user_groups = get_user_groups(db, current_user)
        
        # QM hat Zugriff auf alle Gruppen
        if "quality_management" in user_groups:
            return current_user
        
        # Prüfe spezifische Gruppenzugehörigkeit
        for required_group in self.required_groups:
            if required_group not in user_groups:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Group membership required: {required_group}"
                )
        
        return current_user

# === CONVENIENCE FUNCTIONS ===

def require_permissions(permissions: List[str]):
    """Decorator-ähnliche Funktion für Berechtigungsprüfungen"""
    return PermissionChecker(permissions)

def require_groups(groups: List[str]):
    """Erstellt einen Dependency-Checker für erforderliche Interessensgruppen"""
    return GroupChecker(groups)

# Häufig verwendete Berechtigungsprüfungen
require_qm_approval = require_permissions(["final_approval"])
require_admin = require_permissions(["system_administration"])
require_document_management = require_permissions(["document_creation", "document_approval"])

# Häufig verwendete Gruppen-Prüfungen  
require_qm_group = require_groups(["quality_management"])
require_input_team = require_groups(["input_team"])
require_development = require_groups(["development"])

# === PYDANTIC SCHEMAS ===

from pydantic import BaseModel

class Token(BaseModel):
    """JWT Token Response Schema"""
    access_token: str
    token_type: str
    expires_in: int
    user_id: int
    user_name: str
    groups: List[str]
    permissions: List[str]

class LoginRequest(BaseModel):
    """Login Request Schema"""
    email: str
    password: str

class UserInfo(BaseModel):
    """Benutzer-Info für Token Response"""
    id: int
    email: str
    full_name: str
    organizational_unit: Optional[str]
    is_department_head: bool
    approval_level: int
    is_active: bool  # ✅ HINZUGEFÜGT: Account-Status
    groups: List[str]
    permissions: List[str]
    
    class Config:
        from_attributes = True 

# === ADMIN REQUIREMENT FUNCTIONS ===

async def require_qms_admin(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Dependency-Funktion: Erfordert QMS Admin-Rechte.
    
    Nur qms.admin@company.com darf diese Endpoints nutzen.
    
    Returns:
        UserModel: Authentifizierter QMS Admin
        
    Raises:
        HTTPException: 403 wenn nicht QMS Admin
    """
    if not is_qms_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur QMS System Administrator (qms.admin@company.com) hat Zugriff auf diese Funktion"
        )
    return current_user

async def require_system_admin(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Dependency-Funktion: Erfordert System Admin-Rechte.
    
    QMS Admin und andere Level-4-Department-Heads haben Zugriff.
    
    Returns:
        UserModel: Authentifizierter System Admin
        
    Raises:
        HTTPException: 403 wenn nicht System Admin
    """
    if not is_system_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System Administrator-Rechte erforderlich (Level 4 Department Head oder QMS Admin)"
        )
    return current_user

async def require_admin_or_qm(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Dependency-Funktion: Erfordert Admin-Rechte oder QM-Gruppe.
    
    Für Benutzer-Management, das QMs und Admins erlaubt ist.
    
    Returns:
        UserModel: Authentifizierter Admin oder QM-User
        
    Raises:
        HTTPException: 403 wenn keine Berechtigung
    """
    # System Admin hat immer Zugriff
    if is_system_admin(current_user):
        return current_user
    
    # QM-Gruppe prüfen
    user_groups = get_user_groups(db, current_user)
    if "quality_management" in user_groups and current_user.approval_level >= 3:
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Berechtigung erforderlich: System Admin oder QM-Gruppe (Level 3+)"
    ) 