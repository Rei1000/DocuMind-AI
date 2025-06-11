"""
Pydantic-Schemas für KI-QMS API.

Dieses Modul definiert alle Datenvalidierungs-Schemas für die FastAPI-Anwendung
mit umfassender Fehlerbehandlung und Dokumentation.

Pydantic-Features verwendet:
- Field Validation mit @validator
- Automatic JSON Parsing für komplexe Felder
- Nested Model Relationships
- Custom Error Messages für bessere UX
- Type Coercion für flexible API-Eingaben

Fehlerbehandlung:
- JSON-String-zu-Liste Konvertierung für Permission-Felder
- Graceful Fallbacks bei Parse-Fehlern
- Business Logic Validation (z.B. Approval Levels)
- Ausführliche Error Messages für Frontend-Integration
"""

from pydantic import BaseModel, EmailStr, validator, root_validator, Field
from datetime import datetime, date
from typing import Optional, List
from .models import DocumentStatus, EquipmentStatus, DocumentType
from enum import Enum
import json

# === INTEREST GROUP SCHEMAS ===

class InterestGroupBase(BaseModel):
    """
    Basis-Schema für Interessensgruppen des 13-Stakeholder-Systems.
    
    Repräsentiert organisatorische Einheiten mit spezifischen Berechtigungen
    und KI-Funktionalitäten. Unterstützt sowohl interne Teams als auch
    externe Stakeholder (Auditoren, Lieferanten).
    
    Geschäftslogik:
    - Eindeutige Codes für API-Referenzierung
    - JSON-Liste für granulare Berechtigungen
    - KI-Funktionalitäten spezifisch pro Gruppe
    - Unterscheidung intern/extern für Sicherheit
    
    Pydantic-Features:
    - group_permissions: Automatische JSON-String-zu-Liste Konvertierung
    - code: Format-Validierung (snake_case)
    - Fallback-Values für robuste API-Nutzung
    """
    name: str = Field(..., min_length=2, max_length=100, 
                      description="Vollständiger Gruppenname (z.B. 'Qualitätsmanagement')")
    code: str = Field(..., min_length=2, max_length=50,
                      description="Eindeutiger API-Code (z.B. 'quality_management')")
    description: Optional[str] = Field(None, max_length=500,
                                      description="Detaillierte Aufgabenbeschreibung")
    group_permissions: Optional[List[str]] = Field(default_factory=list,
                                                   description="Liste gruppen-spezifischer Berechtigungen")
    ai_functionality: Optional[str] = Field(None, max_length=300,
                                           description="Verfügbare KI-Features für diese Gruppe")
    typical_tasks: Optional[str] = Field(None, max_length=300,
                                        description="Typische Anwendungsfälle und Aufgaben")
    is_external: bool = Field(False, description="True für externe Stakeholder (Auditoren, Lieferanten)")
    is_active: bool = Field(True, description="Aktiv-Status (False = Soft-Delete)")
    
    @validator('group_permissions', pre=True, allow_reuse=True)
    def parse_group_permissions(cls, v):
        """
        Konvertiert JSON-String zu Liste für group_permissions.
        
        Behandelt verschiedene Eingabeformate graceful:
        - JSON-String: '["perm1", "perm2"]' → ["perm1", "perm2"]  
        - Liste: ["perm1", "perm2"] → ["perm1", "perm2"]
        - None/Empty: → []
        - Invalid JSON: → [] (mit Fallback)
        
        Diese Flexibilität ist essentiell, da SQLite JSON als TEXT speichert,
        aber die API Listen erwartet.
        """
        if v is None:
            return []
        if isinstance(v, str):
            if not v.strip():
                return []
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]  # Ensure all strings
                else:
                    return [str(parsed)]  # Single value to list
            except (json.JSONDecodeError, TypeError):
                # Fallback: Behandle als Comma-separated String
                return [item.strip() for item in v.split(',') if item.strip()]
        elif isinstance(v, list):
            return [str(item) for item in v]  # Ensure all strings
        else:
            return []
    
    @validator('code')
    def validate_code(cls, v):
        """
        Validiert Code-Format für API-Konsistenz.
        
        Requirements:
        - snake_case Format (nur Kleinbuchstaben, Unterstriche)
        - Keine Sonderzeichen außer '_'
        - Eindeutigkeit wird auf DB-Ebene sichergestellt
        """
        if not v.replace('_', '').isalnum() or v != v.lower():
            raise ValueError('Code muss snake_case Format haben (z.B. "quality_management")')
        if v.startswith('_') or v.endswith('_'):
            raise ValueError('Code darf nicht mit Unterstrichen beginnen/enden')
        return v

class InterestGroupCreate(InterestGroupBase):
    """
    Schema für das Erstellen neuer Interessensgruppen.
    
    Für POST /api/interest-groups.
    Erbt vollständige Validierung von InterestGroupBase.
    
    Besonderheiten:
    - Alle Felder von InterestGroupBase verfügbar
    - Automatische Code-Generierung aus Name möglich (Frontend)
    - group_permissions können als JSON-String oder Liste übergeben werden
    """
    pass

class InterestGroupUpdate(BaseModel):
    """
    Schema für das Aktualisieren von Interessensgruppen.
    
    Alle Felder optional für flexible Partial Updates.
    Für PUT /api/interest-groups/{id}.
    
    Erlaubt granulare Updates ohne vollständige Objektübertragung.
    Besonders wichtig für große permission-Listen.
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    group_permissions: Optional[List[str]] = None
    ai_functionality: Optional[str] = Field(None, max_length=300)
    typical_tasks: Optional[str] = Field(None, max_length=300)
    is_external: Optional[bool] = None
    is_active: Optional[bool] = None
    
    @validator('group_permissions', pre=True, allow_reuse=True)
    def parse_group_permissions(cls, v):
        """Gleiche JSON-Parsing-Logik wie InterestGroupBase."""
        if v is None:
            return None  # Unterschied: None für "nicht ändern"
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
    Vollständiges Schema für Interessensgruppen-Responses.
    
    Erweitert InterestGroupBase um Metadaten für API-Antworten.
    Verwendet von GET /api/interest-groups und nested in anderen Responses.
    
    Pydantic Config:
    - from_attributes=True: Ermöglicht SQLAlchemy ORM → Pydantic Konvertierung
    - Automatische Feldnamen-Mapping zwischen DB und API
    """
    id: int = Field(..., description="Eindeutige Gruppen-ID")
    created_at: datetime = Field(..., description="Zeitpunkt der Erstellung")
    
    @validator('group_permissions', pre=True, allow_reuse=True)
    def parse_group_permissions(cls, v):
        """
        Kritischer Validator für API-Response-Konsistenz.
        
        Dieser Validator löst das Hauptproblem aus den Server-Logs:
        'Input should be a valid list' errors entstehen, wenn SQLite
        JSON-Strings zurückgibt, aber das Schema Listen erwartet.
        """
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
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Qualitätsmanagement",
                "code": "quality_management",
                "description": "QM-Freigaben, CAPA, interne Audits",
                "group_permissions": ["all_rights", "final_approval", "gap_analysis"],
                "ai_functionality": "Gap-Analyse & Normprüfung",
                "typical_tasks": "QM-Freigaben, CAPA-Management, interne Audits",
                "is_external": False,
                "is_active": True,
                "created_at": "2025-06-08T16:49:51.763170"
            }
        }

# === USER SCHEMAS ===

class UserBase(BaseModel):
    """
    Basis-Schema für Benutzer mit erweitertem Permission-System.
    
    Implementiert das Dual-Permission-Modell:
    1. individual_permissions: Persönliche Berechtigungen (Abteilungsleiter, etc.)
    2. Gruppen-Berechtigungen: Über UserGroupMembership → InterestGroup.group_permissions
    
    Organisationsstruktur:
    - organizational_unit: Firmenhierarchie (unabhängig von funktionalen Gruppen)
    - approval_level: 1=Standard, 2=Teamleiter, 3=Abteilungsleiter, 4=QM-Manager
    - is_department_head: Spezielle Führungsberechtigungen
    
    Pydantic-Features:
    - EmailStr: Automatische Email-Validierung
    - JSON-Parser für individual_permissions (SQLite-Kompatibilität)
    - Business Logic Validation für approval_level
    """
    email: EmailStr = Field(..., description="Email-Adresse für Login und Benachrichtigungen")
    full_name: str = Field(..., min_length=2, max_length=200, 
                          description="Vollständiger Name (Vor- und Nachname)")
    employee_id: Optional[str] = Field(None, max_length=50,
                                      description="Mitarbeiternummer/Personalnummer")
    organizational_unit: Optional[str] = Field(None, max_length=100,
                                              description="Organisatorische Einheit (unabhängig von Interest Groups)")
    
    # === PERMISSION SYSTEM ===
    individual_permissions: Optional[List[str]] = Field(default_factory=list,
                                                        description="Individuelle User-Berechtigungen (Abteilungsleiter-Rechte, etc.)")
    is_department_head: bool = Field(False, description="Abteilungsleiter-Status für erweiterte Berechtigungen")
    approval_level: int = Field(1, ge=1, le=4, description="Freigabe-Level: 1=Standard, 2=Teamleiter, 3=Abteilungsleiter, 4=QM-Manager")
    
    @validator('individual_permissions', pre=True, allow_reuse=True)
    def parse_individual_permissions(cls, v):
        """
        Robuster JSON-Parser für individual_permissions.
        
        Behandelt SQLite-JSON-Storage graceful:
        - SQLite speichert als TEXT: '["perm1", "perm2"]'
        - API erwartet Liste: ["perm1", "perm2"]
        - Fallback bei Parse-Fehlern zu leerer Liste
        
        Error Recovery:
        - Invalid JSON → []
        - None → []
        - Non-list values → [str(value)]
        """
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
                # Fallback: Comma-separated behandeln
                return [item.strip() for item in v.split(',') if item.strip()]
        return v if isinstance(v, list) else []
    
    @validator('approval_level')
    def validate_approval_level(cls, v):
        """
        Validiert Freigabe-Level-Hierarchie.
        
        Business Rules:
        - Level 1: Standard-Mitarbeiter
        - Level 2: Teamleiter (kleine Freigaben)
        - Level 3: Abteilungsleiter (Budget, Personal)
        - Level 4: QM-Manager (System-weite Freigaben)
        """
        if not 1 <= v <= 4:
            raise ValueError('approval_level muss zwischen 1 und 4 liegen (1=Standard, 4=QM-Manager)')
        return v
    
    @validator('email')
    def validate_email_business_rules(cls, v):
        """
        Erweiterte Email-Validierung für Business-Context.
        
        MVP: Flexible Regeln für Entwicklung
        Production: Strengere Domain-Validierung möglich
        """
        if '@' not in v:
            raise ValueError('Ungültiges Email-Format')
        
        # Optional: Domain-Whitelist für Production
        # allowed_domains = ['company.com', 'contractor.com']
        # domain = v.split('@')[1]
        # if domain not in allowed_domains:
        #     raise ValueError(f'Email-Domain {domain} nicht erlaubt')
        
        return v.lower()  # Normalisierung

class UserCreate(UserBase):
    """
    Schema für Benutzer-Erstellung mit Passwort-Validierung.
    
    Für POST /api/users.
    
    Sicherheitsfeatures:
    - Passwort-Strength-Validation
    - Email-Eindeutigkeit (DB-Constraint)
    - Automatische Passwort-Hashing (im Service)
    
    Wichtig: Passwort wird niemals in Responses zurückgegeben!
    """
    password: str = Field(..., min_length=8, max_length=128,
                         description="Klartext-Passwort (wird gehashed gespeichert)")
    
    @validator('password')
    def validate_password_strength(cls, v):
        """
        Passwort-Strength-Validation für Sicherheit.
        
        MVP-Requirements:
        - Mindestens 8 Zeichen
        - Production: Zusätzlich Komplexitäts-Regeln möglich
        """
        if len(v) < 8:
            raise ValueError('Passwort muss mindestens 8 Zeichen lang sein')
        
        # Optional für Production:
        # if not any(c.isupper() for c in v):
        #     raise ValueError('Passwort muss mindestens einen Großbuchstaben enthalten')
        # if not any(c.isdigit() for c in v):
        #     raise ValueError('Passwort muss mindestens eine Zahl enthalten')
        
        return v

class UserUpdate(BaseModel):
    """
    Schema für flexibles Benutzer-Update.
    
    Alle Felder optional für Partial Updates.
    Für PUT /api/users/{id}.
    
    Besonderheiten:
    - Passwort-Updates über separaten Endpoint /api/users/{id}/password
    - Granulare Permission-Updates möglich
    - Soft-Delete über is_active
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    employee_id: Optional[str] = Field(None, max_length=50)
    organizational_unit: Optional[str] = Field(None, max_length=100)
    individual_permissions: Optional[List[str]] = None
    is_department_head: Optional[bool] = None
    approval_level: Optional[int] = Field(None, ge=1, le=4)
    is_active: Optional[bool] = None
    
    @validator('individual_permissions', pre=True, allow_reuse=True)
    def parse_individual_permissions(cls, v):
        """Gleiche JSON-Parsing-Logik wie UserBase, aber None-aware für Updates."""
        if v is None:
            return None  # Bedeutet "nicht ändern"
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
    
    @validator('approval_level')
    def validate_approval_level(cls, v):
        """Validierung nur wenn Wert gesetzt."""
        if v is not None and not 1 <= v <= 4:
            raise ValueError('approval_level muss zwischen 1 und 4 liegen')
        return v

class User(UserBase):
    """
    Vollständiges User-Schema für API-Responses.
    
    Erweitert UserBase um Metadaten und Status-Informationen.
    Verwendet in GET /api/users und als nested object.
    
    Wichtig: hashed_password wird NIE in API-Responses inkludiert!
    """
    id: int = Field(..., description="Eindeutige User-ID")
    is_active: bool = Field(..., description="Account-Status (False = deaktiviert)")
    created_at: datetime = Field(..., description="Account-Erstellungszeitpunkt")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "email": "max.kaufmann@company.com",
                "full_name": "Max Kaufmann",
                "employee_id": "EK001",
                "organizational_unit": "Einkauf",
                "individual_permissions": ["supplier_management", "purchase_approval"],
                "is_department_head": True,
                "approval_level": 3,
                "is_active": True,
                "created_at": "2025-06-08T16:49:51.763170"
            }
        }

# === USER GROUP MEMBERSHIP SCHEMAS ===

class UserGroupMembershipBase(BaseModel):
    """
    Basis-Schema für User-Group-Zuordnungen (Many-to-Many).
    
    Ermöglicht flexible Organisationsstrukturen:
    - Ein User kann mehreren Gruppen angehören
    - Verschiedene Rollen in verschiedenen Gruppen
    - Temporäre Gruppenmitgliedschaften (is_active)
    - Audit-Trail über joined_at
    
    Anwendungsfälle:
    - QM-Manager in mehreren Produktgruppen
    - Entwickler in verschiedenen Projektteams  
    - Externe Auditoren mit temporärem Zugang
    """
    user_id: int = Field(..., description="Referenz auf User.id")
    interest_group_id: int = Field(..., description="Referenz auf InterestGroup.id")
    is_active: bool = Field(True, description="Aktiv-Status der Mitgliedschaft")

class UserGroupMembershipCreate(UserGroupMembershipBase):
    """
    Schema für Erstellung neuer Group-Memberships.
    
    Für POST /api/user-group-memberships.
    """
    role_in_group: Optional[str] = Field(None, max_length=100,
                                        description="Spezifische Rolle in der Gruppe (z.B. 'QM_COORDINATOR')")

class UserGroupMembership(UserGroupMembershipBase):
    """
    Vollständiges Schema für User-Group-Memberships.
    
    Inkludiert Metadaten und optionale nested objects für Performance.
    """
    id: int = Field(..., description="Eindeutige Membership-ID")
    joined_at: datetime = Field(..., description="Zeitpunkt des Beitritts zur Gruppe")
    role_in_group: Optional[str] = Field(None, description="Rolle innerhalb der Gruppe")
    
    # Nested objects für API-Convenience (Optional für Performance)
    user: Optional['User'] = None
    interest_group: Optional['InterestGroup'] = None
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "interest_group_id": 2,
                "is_active": True,
                "joined_at": "2025-06-08T16:49:51.763170",
                "role_in_group": "QM_COORDINATOR"
            }
        }

# === DOCUMENT SCHEMAS ===

class DocumentBase(BaseModel):
    title: str
    document_number: str
    document_type: DocumentType = DocumentType.OTHER
    version: str = "1.0"
    status: DocumentStatus = DocumentStatus.DRAFT
    content: Optional[str] = None
    file_path: Optional[str] = None
    tags: Optional[str] = None

class DocumentCreate(DocumentBase):
    creator_id: int

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    document_type: Optional[DocumentType] = None
    version: Optional[str] = None
    status: Optional[DocumentStatus] = None
    content: Optional[str] = None
    file_path: Optional[str] = None
    tags: Optional[str] = None

class Document(DocumentBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime
    
    # Nested objects
    creator: Optional[User] = None
    
    class Config:
        from_attributes = True

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
    
    class Config:
        from_attributes = True

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
    
    class Config:
        from_attributes = True

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
    
    # Nested objects
    equipment: Optional[Equipment] = None
    responsible_user: Optional[User] = None
    
    class Config:
        from_attributes = True

# === AUTHENTICATION SCHEMAS ===

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: User

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# === RESPONSE SCHEMAS ===

class GenericResponse(BaseModel):
    message: str
    success: bool = True

class PaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[dict] 