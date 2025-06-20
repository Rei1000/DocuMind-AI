"""
Pydantic v2 kompatible Schemas für KI-QMS API.

Dieses Modul definiert alle Datenvalidierungs-Schemas für die FastAPI-Anwendung
mit umfassender Fehlerbehandlung und Dokumentation.

Pydantic v2 Features:
- @field_validator statt @validator
- ConfigDict statt Config Klassen
- json_schema_extra statt schema_extra
"""

from pydantic import BaseModel, EmailStr, field_validator, Field, ConfigDict
from datetime import datetime, date
from typing import Optional, List
from .models import DocumentStatus, EquipmentStatus, DocumentType
from enum import Enum
import json

# === INTEREST GROUP SCHEMAS ===

class InterestGroupBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    group_permissions: Optional[List[str]] = Field(default_factory=list)
    ai_functionality: Optional[str] = Field(None, max_length=300)
    typical_tasks: Optional[str] = Field(None, max_length=300)
    is_external: bool = Field(False)
    is_active: bool = Field(True)
    
    @field_validator('group_permissions', mode='before')
    @classmethod
    def parse_group_permissions(cls, v):
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
    def validate_code(cls, v):
        if not v.replace('_', '').isalnum() or v != v.lower():
            raise ValueError('Code muss snake_case Format haben')
        if v.startswith('_') or v.endswith('_'):
            raise ValueError('Code darf nicht mit Unterstrichen beginnen/enden')
        return v

class InterestGroupCreate(InterestGroupBase):
    pass

class InterestGroupUpdate(BaseModel):
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
    def parse_group_permissions(cls, v):
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
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('group_permissions', mode='before')
    @classmethod
    def parse_group_permissions(cls, v):
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
    email: EmailStr = Field(...)
    full_name: str = Field(..., min_length=2, max_length=200)
    employee_id: Optional[str] = Field(None, max_length=50)
    organizational_unit: Optional[str] = Field(None, max_length=100)
    individual_permissions: Optional[List[str]] = Field(default_factory=list)
    is_department_head: bool = Field(False)
    approval_level: int = Field(1, ge=1, le=4)
    
    @field_validator('individual_permissions', mode='before')
    @classmethod
    def parse_individual_permissions(cls, v):
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
    def validate_approval_level(cls, v):
        if not 1 <= v <= 4:
            raise ValueError('approval_level muss zwischen 1 und 4 liegen')
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email_business_rules(cls, v):
        if '@' not in v:
            raise ValueError('Ungültiges Email-Format')
        return v.lower()

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Passwort muss mindestens 8 Zeichen lang sein')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    employee_id: Optional[str] = Field(None, max_length=50)
    organizational_unit: Optional[str] = Field(None, max_length=100)
    individual_permissions: Optional[List[str]] = None
    is_department_head: Optional[bool] = None
    approval_level: Optional[int] = Field(None, ge=1, le=4)
    is_active: Optional[bool] = None
    
    @field_validator('individual_permissions', mode='before')
    @classmethod
    def parse_individual_permissions(cls, v):
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
    def validate_approval_level(cls, v):
        if v is not None and not 1 <= v <= 4:
            raise ValueError('approval_level muss zwischen 1 und 4 liegen')
        return v

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# === MEMBERSHIP SCHEMAS ===

class UserGroupMembershipBase(BaseModel):
    user_id: int
    interest_group_id: int
    is_active: bool = Field(True)

class UserGroupMembershipCreate(UserGroupMembershipBase):
    role_in_group: Optional[str] = Field(None, max_length=100)

class UserGroupMembership(UserGroupMembershipBase):
    id: int
    joined_at: datetime
    role_in_group: Optional[str] = None
    user: Optional['User'] = None
    interest_group: Optional['InterestGroup'] = None
    
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
    user: User

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# === GENERIC SCHEMAS ===

class GenericResponse(BaseModel):
    message: str
    success: bool = True

class PaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[dict] 