"""
KI-QMS API Schemas - Pydantic v2 Datenvalidierung

Dieses Modul definiert alle Datenvalidierungs-Schemas für die FastAPI-Anwendung
mit umfassender Fehlerbehandlung, Type Safety und automatischer API-Dokumentation.

Pydantic v2 Features verwendet:
- @field_validator statt @validator (v1 deprecated)
- ConfigDict statt Config Klassen 
- Field() für erweiterte Feldvalidierung
- EmailStr für E-Mail-Validierung
- Automatische OpenAPI Schema-Generierung

Schema-Kategorien:
- InterestGroup: 13-Stakeholder-System Schemas
- User: Benutzerverwaltung mit Rollensystem
- Document: QMS-Dokumentenverwaltung (14 Dokumenttypen)
- Equipment: Asset-Management mit Kalibrierung
- Authentication: Login/Token Management
- API Responses: Standardisierte API-Antworten

Technologie-Stack:
- FastAPI + Pydantic v2 für automatische Validierung
- SQLAlchemy ORM Kompatibilität über from_attributes=True
- JSON Schema für OpenAPI/Swagger Dokumentation
- Type Safety durch umfassende Type Hints

Autoren: KI-QMS Entwicklungsteam
Version: 2.0.0 (Pydantic v2 Migration)
"""

from pydantic import BaseModel, EmailStr, field_validator, Field, ConfigDict
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from .models import DocumentStatus, EquipmentStatus, DocumentType
from enum import Enum
import json

# === INTEREST GROUP SCHEMAS ===

class InterestGroupBase(BaseModel):
    """
    Basis-Schema für Interessensgruppen im 13-Stakeholder-System.
    
    Definiert die Grundstruktur für alle InterestGroup-bezogenen Schemas
    mit Validierung für Namenskonventionen und Berechtigungsstrukturen.
    
    Validation Rules:
    - code: snake_case Format erforderlich
    - group_permissions: Flexible JSON/String/List Eingabe
    - Standard-Felder für alle CRUD-Operationen
    """
    name: str = Field(..., min_length=2, max_length=100, 
                     description="Vollständiger Name der Interessensgruppe")
    code: str = Field(..., min_length=2, max_length=50,
                     description="Eindeutiger Code in snake_case Format")
    description: Optional[str] = Field(None, max_length=500,
                                     description="Detaillierte Beschreibung der Aufgaben")
    group_permissions: Optional[List[str]] = Field(default_factory=list,
                                                  description="Liste der Gruppen-Berechtigungen")
    ai_functionality: Optional[str] = Field(None, max_length=300,
                                          description="Verfügbare KI-Funktionen")
    typical_tasks: Optional[str] = Field(None, max_length=300,
                                       description="Typische Aufgaben der Gruppe")
    is_external: bool = Field(False, description="True für externe Stakeholder")
    is_active: bool = Field(True, description="Aktiv-Status der Gruppe")
    
    @field_validator('group_permissions', mode='before')
    @classmethod
    def parse_group_permissions(cls, v: Union[str, List[str], None]) -> List[str]:
        """
        Flexible Validierung für group_permissions.
        
        Akzeptiert JSON-String, komma-separierte Strings oder Listen
        und konvertiert zu standardisierter Liste.
        """
        if v is None:
            return []
        if isinstance(v, str):
            if not v.strip():
                return []
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
                else:
                    return [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                return [item.strip() for item in v.split(',') if item.strip()]
        elif isinstance(v, list):
            return [str(item) for item in v]
        else:
            return []
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """
        Validiert Code-Format für API-Konsistenz.
        
        Enforces:
        - snake_case Format (nur lowercase, underscores)
        - Keine führenden/nachfolgenden Underscores
        - Alphanumerische Zeichen + Underscores
        """
        if not v.replace('_', '').isalnum() or v != v.lower():
            raise ValueError('Code muss snake_case Format haben')
        if v.startswith('_') or v.endswith('_'):
            raise ValueError('Code darf nicht mit Unterstrichen beginnen/enden')
        return v

class InterestGroupCreate(InterestGroupBase):
    """Schema für Erstellung neuer Interessensgruppen."""
    pass

class InterestGroupUpdate(BaseModel):
    """
    Schema für Aktualisierung bestehender Interessensgruppen.
    
    Alle Felder optional für partielle Updates. Validation Rules
    gelten analog zu InterestGroupBase.
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    group_permissions: Optional[List[str]] = None
    ai_functionality: Optional[str] = Field(None, max_length=300)
    typical_tasks: Optional[str] = Field(None, max_length=300)
    is_external: Optional[bool] = None
    is_active: Optional[bool] = None
    
    @field_validator('group_permissions', mode='before')
    @classmethod
    def parse_group_permissions(cls, v: Union[str, List[str], None]) -> Optional[List[str]]:
        """Analog zu InterestGroupBase, aber None-tolerant für Updates."""
        if v is None:
            return None
        if isinstance(v, str):
            if not v.strip():
                return []
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                return [item.strip() for item in v.split(',') if item.strip()]
        elif isinstance(v, list):
            return [str(item) for item in v]
        else:
            return []

class InterestGroup(InterestGroupBase):
    """
    Vollständiges InterestGroup-Schema mit Metadaten.
    
    Verwendet für API-Responses mit allen Datenbankfeldern
    inklusive Auto-generierter Werte (id, created_at).
    """
    id: int = Field(description="Eindeutige Interessensgruppen-ID")
    created_at: datetime = Field(description="Zeitpunkt der Erstellung")
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('group_permissions', mode='before')
    @classmethod
    def parse_group_permissions(cls, v: Union[str, List[str], None]) -> List[str]:
        """Konsistente group_permissions Parsing für API-Responses."""
        if v is None:
            return []
        if isinstance(v, str):
            if not v.strip():
                return []
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError):
                return []
        elif isinstance(v, list):
            return v
        else:
            return []

# === USER SCHEMAS ===

class UserBase(BaseModel):
    """
    Basis-Schema für Benutzerverwaltung.
    
    Definiert die Grundstruktur für alle User-bezogenen Schemas
    mit Validierung für Rollen-System und Berechtigungen.
    
    Permission System:
    - individual_permissions: Benutzer-spezifische Rechte
    - approval_level: 1=Standard, 2=Teamleiter, 3=Abteilungsleiter, 4=QM-Manager
    - is_department_head: Sonderrecht für Freigabe-Workflows
    """
    email: EmailStr = Field(..., description="Email-Adresse (eindeutig)")
    full_name: str = Field(..., min_length=2, max_length=200,
                          description="Vollständiger Name (Vor- und Nachname)")
    employee_id: Optional[str] = Field(None, max_length=50,
                                     description="Mitarbeiternummer")
    organizational_unit: Optional[str] = Field(None, max_length=100,
                                             description="Abteilung/Organisationseinheit")
    individual_permissions: Optional[List[str]] = Field(default_factory=list,
                                                      description="Individuelle Benutzer-Berechtigungen")
    is_department_head: bool = Field(False, description="Abteilungsleiter-Status")
    approval_level: int = Field(1, ge=1, le=4, description="Freigabe-Level (1-4)")
    
    @field_validator('individual_permissions', mode='before')
    @classmethod
    def parse_individual_permissions(cls, v: Union[str, List[str], None]) -> List[str]:
        """Flexible Parsing für individual_permissions analog zu group_permissions."""
        if v is None:
            return []
        if isinstance(v, str):
            if not v.strip():
                return []
            try:
                import json
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                return [item.strip() for item in v.split(',') if item.strip()]
        return v if isinstance(v, list) else []
    
    @field_validator('approval_level')
    @classmethod
    def validate_approval_level(cls, v: int) -> int:
        """Validiert Freigabe-Level im gültigen Bereich."""
        if not 1 <= v <= 4:
            raise ValueError('approval_level muss zwischen 1 und 4 liegen')
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email_business_rules(cls, v: str) -> str:
        """Business-Rules für Email-Adressen."""
        if '@' not in v:
            raise ValueError('Ungültiges Email-Format')
        return v.lower()

class UserCreate(UserBase):
    """
    Schema für Benutzer-Erstellung mit Passwort.
    
    Erweitert UserBase um Passwort-Validierung für sichere
    Account-Erstellung.
    """
    password: str = Field(..., min_length=8, max_length=128,
                         description="Passwort (mindestens 8 Zeichen)")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Basis-Passwort-Validierung."""
        if len(v) < 8:
            raise ValueError('Passwort muss mindestens 8 Zeichen lang sein')
        return v

class UserUpdate(BaseModel):
    """
    Schema für Benutzer-Updates.
    
    Alle Felder optional für partielle Updates. Passwort wird
    separat über spezielle Endpoints verwaltet.
    """
    email: Optional[EmailStr] = Field(None, description="Neue Email-Adresse")
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    employee_id: Optional[str] = Field(None, max_length=50)
    organizational_unit: Optional[str] = Field(None, max_length=100)
    individual_permissions: Optional[List[str]] = None
    is_department_head: Optional[bool] = None
    approval_level: Optional[int] = Field(None, ge=1, le=4)
    is_active: Optional[bool] = None
    
    @field_validator('individual_permissions', mode='before')
    @classmethod
    def parse_individual_permissions(cls, v: Union[str, List[str], None]) -> Optional[List[str]]:
        """None-tolerante Version für Updates."""
        if v is None:
            return None
        if isinstance(v, str):
            if not v.strip():
                return []
            try:
                import json
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                return [item.strip() for item in v.split(',') if item.strip()]
        return v if isinstance(v, list) else []
    
    @field_validator('approval_level')
    @classmethod
    def validate_approval_level(cls, v: Optional[int]) -> Optional[int]:
        """Validierung für optionale approval_level Updates."""
        if v is not None and not 1 <= v <= 4:
            raise ValueError('approval_level muss zwischen 1 und 4 liegen')
        return v

class User(UserBase):
    """
    Vollständiges User-Schema für API-Responses.
    
    Inklusive Metadaten und ohne sensible Daten (Passwort).
    """
    id: int = Field(description="Eindeutige Benutzer-ID")
    is_active: bool = Field(description="Account-Status (aktiv/deaktiviert)")
    created_at: datetime = Field(description="Zeitpunkt der Account-Erstellung")
    
    model_config = ConfigDict(from_attributes=True)

# === USER GROUP MEMBERSHIP SCHEMAS ===

class UserGroupMembershipBase(BaseModel):
    """
    Basis-Schema für Many-to-Many Beziehung User ↔ InterestGroup.
    
    Ermöglicht flexible Zuordnung von Benutzern zu mehreren Interessensgruppen
    mit spezifischen Rollen. Unterstützt Matrix-Organisationen.
    """
    user_id: int = Field(description="Referenz auf User")
    interest_group_id: int = Field(description="Referenz auf InterestGroup")
    is_active: bool = Field(True, description="Aktiv-Status der Zuordnung")

class UserGroupMembershipCreate(UserGroupMembershipBase):
    """Schema für Erstellung neuer User-Group Zuordnungen."""
    role_in_group: Optional[str] = Field(None, max_length=100,
                                       description="Spezifische Rolle in der Gruppe")

class UserGroupMembership(UserGroupMembershipBase):
    """
    Vollständiges UserGroupMembership-Schema mit Metadaten.
    
    Inklusive Relationships für vollständige API-Responses.
    """
    id: int = Field(description="Eindeutige Zuordnungs-ID")
    joined_at: datetime = Field(description="Zeitpunkt des Beitritts")
    role_in_group: Optional[str] = Field(None, description="Rolle in der Gruppe")
    user: Optional['User'] = Field(None, description="Vollständige User-Daten")
    interest_group: Optional['InterestGroup'] = Field(None, description="Vollständige Group-Daten")
    
    model_config = ConfigDict(from_attributes=True)

# === DOCUMENT SCHEMAS ===

class DocumentBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    document_number: str = Field(..., max_length=50)
    document_type: DocumentType = DocumentType.OTHER
    version: str = Field("1.0", max_length=20)
    status: DocumentStatus = DocumentStatus.DRAFT
    content: Optional[str] = Field(None, max_length=10000)
    
    # === PHYSISCHE DATEI-FELDER ===
    file_path: Optional[str] = Field(None, max_length=500)
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    file_hash: Optional[str] = Field(None, max_length=64)
    mime_type: Optional[str] = Field(None, max_length=100)
    
    # === RAG-VORBEREITUNG ===
    extracted_text: Optional[str] = Field(None, max_length=500000)
    keywords: Optional[str] = Field(None, max_length=1000)
    
    # === VERSIONIERUNG ===
    parent_document_id: Optional[int] = None
    version_notes: Optional[str] = Field(None, max_length=1000)
    
    # === QM-METADATEN ===
    tags: Optional[str] = Field(None, max_length=500)
    remarks: Optional[str] = Field(None, max_length=2000)
    chapter_numbers: Optional[str] = Field(None, max_length=200)
    
    # === NORM-SPEZIFISCHE FELDER ===
    compliance_status: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, max_length=20)
    scope: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('version')
    @classmethod
    def validate_version(cls, v):
        """Validiert Semantic Versioning Format (1.0, 1.1, 2.0, etc.)"""
        import re
        if not re.match(r'^\d+\.\d+(\.\d+)?$', v):
            raise ValueError('Version muss im Format X.Y oder X.Y.Z sein (z.B. 1.0, 1.1, 2.0)')
        return v

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    document_type: DocumentType = DocumentType.OTHER
    version: str = Field("1.0", max_length=20)
    content: Optional[str] = Field(None, max_length=10000)
    creator_id: int
    
    # === OPTIONALE DATEI-FELDER ===
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    
    # === QM-METADATEN ===
    remarks: Optional[str] = Field(None, max_length=2000)
    chapter_numbers: Optional[str] = Field(None, max_length=200)
    
    # === NORM-SPEZIFISCHE FELDER ===
    compliance_status: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, max_length=20)
    scope: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('version')
    @classmethod
    def validate_version(cls, v):
        import re
        if not re.match(r'^\d+\.\d+(\.\d+)?$', v):
            raise ValueError('Version muss im Format X.Y oder X.Y.Z sein')
        return v

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    document_type: Optional[DocumentType] = None
    version: Optional[str] = Field(None, max_length=20)
    status: Optional[DocumentStatus] = None
    content: Optional[str] = Field(None, max_length=10000)
    
    # === QM-METADATEN ===
    remarks: Optional[str] = Field(None, max_length=2000)
    chapter_numbers: Optional[str] = Field(None, max_length=200)
    version_notes: Optional[str] = Field(None, max_length=1000)
    
    # === WORKFLOW-FELDER ===
    reviewed_by_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    
    # === NORM-SPEZIFISCHE FELDER ===
    compliance_status: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, max_length=20)
    scope: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('version')
    @classmethod
    def validate_version(cls, v):
        if v is not None:
            import re
            if not re.match(r'^\d+\.\d+(\.\d+)?$', v):
                raise ValueError('Version muss im Format X.Y oder X.Y.Z sein')
        return v

class Document(DocumentBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime
    
    # === WORKFLOW-INFORMATIONEN ===
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    
    # === RELATIONSHIPS ===
    creator: Optional[User] = None
    reviewed_by: Optional[User] = None
    approved_by: Optional[User] = None
    parent_document: Optional['Document'] = None
    
    model_config = ConfigDict(from_attributes=True)

# === FILE UPLOAD SCHEMAS ===

class FileUploadResponse(BaseModel):
    """Response für erfolgreichen Datei-Upload"""
    file_path: str
    file_name: str
    file_size: int
    file_hash: str
    mime_type: str
    uploaded_at: datetime
    
class DocumentWithFileCreate(BaseModel):
    """Schema für Dokument-Erstellung mit Datei-Upload"""
    # Dokument-Basis-Daten
    title: str = Field(..., min_length=2, max_length=255)
    document_type: DocumentType = DocumentType.OTHER
    version: str = Field("1.0", max_length=20)
    content: Optional[str] = Field(None, max_length=10000)
    creator_id: int
    
    # QM-Metadaten
    remarks: Optional[str] = Field(None, max_length=2000)
    chapter_numbers: Optional[str] = Field(None, max_length=200)
    
    # Datei-Informationen (vom Frontend bereitgestellt)
    file_upload_response: Optional[FileUploadResponse] = None

# === NORM SCHEMAS ===

class NormBase(BaseModel):
    name: str
    full_title: str
    version: Optional[str] = None
    description: Optional[str] = None
    authority: Optional[str] = None
    effective_date: Optional[datetime] = None

class NormCreate(NormBase):
    pass

class NormUpdate(BaseModel):
    name: Optional[str] = None
    full_title: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    authority: Optional[str] = None
    effective_date: Optional[datetime] = None

class Norm(NormBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# === EQUIPMENT SCHEMAS ===

class EquipmentBase(BaseModel):
    name: str
    equipment_number: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    status: EquipmentStatus = EquipmentStatus.ACTIVE
    calibration_interval_months: int = 12

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    status: Optional[EquipmentStatus] = None
    calibration_interval_months: Optional[int] = None
    last_calibration: Optional[datetime] = None
    next_calibration: Optional[datetime] = None

class Equipment(EquipmentBase):
    id: int
    last_calibration: Optional[datetime] = None
    next_calibration: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# === CALIBRATION SCHEMAS ===

class CalibrationBase(BaseModel):
    equipment_id: int
    calibration_date: datetime
    next_due_date: datetime
    calibration_results: Optional[str] = None
    certificate_path: Optional[str] = None
    status: str = "valid"
    responsible_user_id: int

class CalibrationCreate(CalibrationBase):
    pass

class CalibrationUpdate(BaseModel):
    calibration_date: Optional[datetime] = None
    next_due_date: Optional[datetime] = None
    calibration_results: Optional[str] = None
    certificate_path: Optional[str] = None
    status: Optional[str] = None
    responsible_user_id: Optional[int] = None

class Calibration(CalibrationBase):
    id: int
    created_at: datetime
    equipment: Optional[Equipment] = None
    responsible_user: Optional[User] = None
    
    model_config = ConfigDict(from_attributes=True)

# === AUTH SCHEMAS ===

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: int
    user_name: str
    groups: List[str] = []
    permissions: List[str] = []

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# === GENERIC SCHEMAS ===

# === DOCUMENT STATUS WORKFLOW SCHEMAS ===

class DocumentStatusChange(BaseModel):
    """Schema für Dokumentstatus-Änderungen"""
    status: DocumentStatus = Field(..., description="Neuer Dokumentstatus")
    comment: Optional[str] = Field(None, max_length=1000, description="Kommentar zur Status-Änderung")
    
    @field_validator('comment')
    @classmethod
    def validate_comment(cls, v):
        if v and len(v.strip()) == 0:
            return None
        return v

class DocumentStatusHistory(BaseModel):
    """Status-Change History für Audit-Trail"""
    id: int
    document_id: int
    old_status: Optional[DocumentStatus]
    new_status: DocumentStatus
    changed_by_id: int
    changed_at: datetime
    comment: Optional[str]
    changed_by: Optional[User] = None
    
    model_config = ConfigDict(from_attributes=True)

class NotificationInfo(BaseModel):
    """Benachrichtigung für Status-Änderungen"""
    message: str
    recipients: List[str]  # Email-Adressen
    document_title: str
    new_status: DocumentStatus
    changed_by: str

# === GENERIC RESPONSES ===

class GenericResponse(BaseModel):
    message: str
    success: bool = True

class PaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[dict]

# === BENUTZER-SELBSTVERWALTUNG SCHEMAS ===

class PasswordChangeRequest(BaseModel):
    """
    Schema für Benutzer-Passwort-Änderung (Selbstverwaltung).
    
    DSGVO-konform: Benutzer können eigenes Passwort ändern.
    Erfordert Bestätigung des aktuellen Passworts für Sicherheit.
    """
    current_password: str = Field(..., min_length=1, max_length=128,
                                description="Aktuelles Passwort zur Bestätigung")
    new_password: str = Field(..., min_length=8, max_length=128,
                            description="Neues Passwort (min. 8 Zeichen)")
    confirm_password: str = Field(..., min_length=8, max_length=128,
                                description="Bestätigung des neuen Passworts")
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Passwort-Stärke Validierung für Sicherheit.
        
        Anforderungen:
        - Mindestens 8 Zeichen
        - Mindestens ein Großbuchstabe
        - Mindestens eine Zahl oder Sonderzeichen
        """
        if len(v) < 8:
            raise ValueError('Passwort muss mindestens 8 Zeichen haben')
        if not any(c.isupper() for c in v):
            raise ValueError('Passwort muss mindestens einen Großbuchstaben enthalten')
        if not any(c.isdigit() or not c.isalnum() for c in v):
            raise ValueError('Passwort muss mindestens eine Zahl oder ein Sonderzeichen enthalten')
        return v
    
    def validate_passwords_match(self) -> 'PasswordChangeRequest':
        """Validiert, dass neues Passwort und Bestätigung übereinstimmen."""
        if self.new_password != self.confirm_password:
            raise ValueError('Neues Passwort und Bestätigung stimmen nicht überein')
        return self

class AdminPasswordResetRequest(BaseModel):
    """
    Schema für Admin-Passwort-Reset (Notfall-Funktion).
    
    Nur für System-Administratoren verfügbar.
    Generiert temporäres Passwort für Benutzer.
    """
    user_id: int = Field(..., description="Benutzer-ID für Passwort-Reset")
    temporary_password: Optional[str] = Field(None, min_length=12, max_length=128,
                                            description="Optionales temporäres Passwort (wird generiert falls leer)")
    force_change_on_login: bool = Field(True, 
                                      description="Benutzer muss Passwort beim nächsten Login ändern")
    reset_reason: str = Field(..., min_length=5, max_length=500,
                            description="Grund für den Admin-Reset (Audit-Trail)")

class UserProfileResponse(BaseModel):
    """
    Schema für Benutzerprofil-Anzeige (Selbstverwaltung).
    
    DSGVO-konform: Benutzer können eigene Daten einsehen.
    Zeigt alle relevanten Account-Informationen ohne sensible Daten.
    """
    id: int = Field(description="Benutzer-ID")
    email: EmailStr = Field(description="Email-Adresse")
    full_name: str = Field(description="Vollständiger Name")
    employee_id: Optional[str] = Field(None, description="Mitarbeiternummer")
    organizational_unit: Optional[str] = Field(None, description="Abteilung/Organisationseinheit")
    individual_permissions: List[str] = Field(default_factory=list, 
                                            description="Individuelle Berechtigungen")
    is_department_head: bool = Field(description="Abteilungsleiter-Status")
    approval_level: int = Field(description="Freigabe-Level (1-4)")
    is_active: bool = Field(description="Account-Status")
    created_at: datetime = Field(description="Account-Erstellungsdatum")
    
    # Zusätzliche Profile-Informationen
    interest_groups: List[str] = Field(default_factory=list,
                                     description="Zugeordnete Interessensgruppen")
    last_login: Optional[datetime] = Field(None, description="Letzter Login")
    password_changed_at: Optional[datetime] = Field(None, description="Letzter Passwort-Wechsel")
    
    model_config = ConfigDict(from_attributes=True)

class PasswordResetResponse(BaseModel):
    """Response für erfolgreichen Passwort-Reset."""
    message: str = Field(description="Bestätigungsnachricht")
    temporary_password: Optional[str] = Field(None, description="Temporäres Passwort (nur bei Admin-Reset)")
    force_change_required: bool = Field(description="Passwort-Änderung beim nächsten Login erforderlich")
    reset_by_admin: bool = Field(description="Reset wurde von Administrator durchgeführt")
    reset_at: datetime = Field(description="Zeitpunkt des Resets") 