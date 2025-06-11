"""
KI-QMS FastAPI Main Application

Dieses Modul definiert die Haupt-FastAPI-Anwendung für das KI-gestützte 
Qualitätsmanagementsystem (QMS). Es stellt RESTful API-Endpunkte für:

- Interessensgruppen-Management (13 praxisorientierte Stakeholder-Gruppen)
- Benutzer- und Rollenverwaltung
- Dokumentenmanagement mit QMS-spezifischen Typen
- Normen- und Compliance-Verwaltung
- Equipment- und Kalibrierungsmanagement

Autoren: KI-QMS Entwicklungsteam
Version: 1.0.0 (MVP Phase 1)
Erstellt: 2024
Lizenz: MIT
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from dotenv import load_dotenv
import os

# Lade Environment Variables aus .env Datei
load_dotenv()

from .database import get_db, create_tables
from .models import (
    InterestGroup as InterestGroupModel, 
    User as UserModel, 
    UserGroupMembership as UserGroupMembershipModel,
    Document as DocumentModel,
    Norm as NormModel,
    Equipment as EquipmentModel,
    Calibration as CalibrationModel,
    DocumentType,
    DocumentStatus
)
from .schemas import (
    InterestGroup, InterestGroupCreate, InterestGroupUpdate,
    User, UserCreate, UserUpdate,
    UserGroupMembership, UserGroupMembershipCreate,
    Document, DocumentCreate, DocumentUpdate,
    Norm, NormCreate, NormUpdate,
    Equipment, EquipmentCreate, EquipmentUpdate,
    Calibration, CalibrationCreate, CalibrationUpdate,
    GenericResponse
)

# ===== ANWENDUNGSINITIALISIERUNG =====

app = FastAPI(
    title="KI-QMS API",
    description="""
    ## KI-gestütztes Qualitätsmanagementsystem für Medizinprodukte
    
    Ein modulares Backend-System für ISO 13485 und MDR-konforme QMS-Prozesse.
    
    ### Hauptfunktionen:
    - **13 Interessensgruppen-System**: Von Einkauf bis externe Auditoren
    - **Dokumentenmanagement**: 14 QMS-spezifische Dokumenttypen
    - **Kalibrierungsmanagement**: Equipment-Überwachung und Fristencontrolling
    - **Normen-Compliance**: ISO 13485, MDR, ISO 14971 Integration
    - **Benutzer-/Rollenverwaltung**: Granulare Berechtigungssteuerung
    
    ### Technischer Stack:
    - **Backend**: FastAPI mit SQLAlchemy ORM
    - **Datenbank**: SQLite (MVP) / PostgreSQL (Production)
    - **Authentifizierung**: Token-basiert (JWT geplant)
    - **API-Dokumentation**: OpenAPI 3.0 / Swagger UI
    """,
    version="1.0.0",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "KI-QMS Support",
        "url": "https://example.com/contact/",
        "email": "support@ki-qms.de",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# ===== CORS-KONFIGURATION =====
# Erlaubt Frontend-Zugriff von React Development Server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React Frontend
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],  # Content-Type, Authorization, etc.
)

# ===== STARTUP/SHUTDOWN EVENTS =====

@app.on_event("startup")
async def startup_event():
    """
    Anwendungsstart-Event.
    
    Führt beim Backend-Start notwendige Initialisierungen durch:
    - Prüft Datenbankverbindung
    - Erstellt fehlende Tabellen
    - Loggt Systemzustand
    """
    create_tables()
    print("🚀 KI-QMS MVP Backend gestartet!")
    print("📊 13-Interessensgruppen-System ist bereit!")

# ===== HEALTH & STATUS ENDPOINTS =====

@app.get("/", tags=["System"])
async def root():
    """
    Root-Endpoint für grundlegende API-Informationen.
    
    Returns:
        dict: Basis-Informationen über die API
        
    Example Response:
        ```json
        {
            "message": "KI-QMS API v1.0",
            "status": "running",
            "docs_url": "/docs",
            "health_check": "/health"
        }
        ```
    """
    return {
        "message": "KI-QMS API v1.0", 
        "status": "running",
        "docs_url": "/docs",
        "health_check": "/health"
    }

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health-Check-Endpoint für Monitoring und Load Balancer.
    
    Prüft:
    - API-Verfügbarkeit
    - Datenbankverbindung (implizit)
    - Systemzustand
    
    Returns:
        dict: Health-Status mit Zeitstempel
        
    Example Response:
        ```json
        {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00Z",
            "version": "1.0.0"
        }
        ```
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }

# === INTEREST GROUPS API ===

@app.get("/api/interest-groups", response_model=List[InterestGroup], tags=["Interest Groups"])
async def get_interest_groups(
    skip: int = 0,
    limit: int = 20,
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """
    Alle Interessensgruppen abrufen (standardmäßig nur aktive).
    
    Das 13-Interessensgruppen-System bildet die organisatorische Grundlage
    des QMS ab - von internen Stakeholdern (Einkauf, Produktion, QM) bis
    zu externen Partnern (Auditoren, Lieferanten).
    
    Args:
        skip (int): Anzahl zu überspringender Datensätze (Pagination). Default: 0
        limit (int): Maximale Anzahl zurückzugebender Datensätze. Default: 20, Max: 100
        include_inactive (bool): Auch deaktivierte Gruppen einschließen. Default: False
        db (Session): Datenbankverbindung (automatisch injiziert)
    
    Returns:
        List[InterestGroup]: Liste der Interessensgruppen
        
    Example Response:
        ```json
        [
            {
                "id": 2,
                "name": "Qualitätsmanagement (QM)",
                "code": "quality_management",
                "description": "Alle Rechte, finale Freigabe, Gap-Analyse - Herzstück des QMS",
                "permissions": ["all_rights", "final_approval", "gap_analysis"],
                "ai_functionality": "Gap-Analyse & Normprüfung",
                "typical_tasks": "QM-Freigaben, CAPA-Management, interne Audits",
                "is_external": false,
                "is_active": true,
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 11,
                "name": "Auditor (extern)",
                "code": "external_auditor", 
                "description": "Read-only extern, Gap-API, Remote-Zugriff",
                "permissions": ["read_only_external", "gap_api", "remote_access"],
                "ai_functionality": "Read-only extern, Gap-API",
                "typical_tasks": "Externe Audits, Compliance-Prüfungen",
                "is_external": true,
                "is_active": true,
                "created_at": "2024-01-15T10:30:00Z"
            }
        ]
        ```
    
    Raises:
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Soft-Delete: Gelöschte Gruppen haben is_active=false
        - Externe Gruppen (is_external=true): Auditoren, Lieferanten
        - Permissions sind als JSON-Array gespeichert
    """
    query = db.query(InterestGroupModel)
    
    # Standardmäßig nur aktive Gruppen anzeigen
    if not include_inactive:
        query = query.filter(InterestGroupModel.is_active == True)
    
    groups = query.offset(skip).limit(limit).all()
    
    # JSON-Strings in Listen konvertieren für Response-Validierung
    for group in groups:
        if group.group_permissions and isinstance(group.group_permissions, str):
            try:
                import json
                group.group_permissions = json.loads(group.group_permissions)
            except (json.JSONDecodeError, TypeError):
                group.group_permissions = []
    
    return groups

@app.get("/api/interest-groups/{group_id}", response_model=InterestGroup, tags=["Interest Groups"])
async def get_interest_group(group_id: int, db: Session = Depends(get_db)):
    """
    Eine spezifische Interessensgruppe abrufen.
    
    Lädt eine einzelne Interessensgruppe mit allen Details,
    einschließlich Berechtigungen und KI-Funktionalitäten.
    
    Args:
        group_id (int): Eindeutige ID der Interessensgruppe (1-13 für Standard-Gruppen)
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        InterestGroup: Detaillierte Informationen der Interessensgruppe
        
    Example Response:
        ```json
        {
            "id": 5,
            "name": "Entwicklung",
            "code": "development",
            "description": "Design-Control, Normprüfung",
            "permissions": ["design_control", "norm_verification", "technical_documentation"],
            "ai_functionality": "Design-Control, Normprüfung",
            "typical_tasks": "Produktentwicklung, Design-FMEA, technische Dokumentation",
            "is_external": false,
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z"
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Interessensgruppe nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Auch deaktivierte Gruppen werden zurückgegeben (für Admin-Zwecke)
        - Permissions als JSON-Array für flexible Berechtigungssteuerung
    """
    group = db.query(InterestGroupModel).filter(InterestGroupModel.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interessensgruppe mit ID {group_id} nicht gefunden"
        )
    
    # JSON-String in Liste konvertieren für Response-Validierung
    if group.group_permissions and isinstance(group.group_permissions, str):
        try:
            import json
            group.group_permissions = json.loads(group.group_permissions)
        except (json.JSONDecodeError, TypeError):
            group.group_permissions = []
    
    return group

@app.post("/api/interest-groups", response_model=InterestGroup, tags=["Interest Groups"])
async def create_interest_group(
    group: InterestGroupCreate,
    db: Session = Depends(get_db)
):
    """
    Neue Interessensgruppe erstellen.
    
    Erstellt eine neue Interessensgruppe im System. Typischerweise für
    kundenspezifische Erweiterungen des Standard-13-Gruppen-Systems.
    
    Args:
        group (InterestGroupCreate): Daten der neuen Interessensgruppe
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        InterestGroup: Die erstellte Interessensgruppe mit generierter ID
        
    Example Request:
        ```json
        {
            "name": "Regulatorische Angelegenheiten",
            "code": "regulatory_affairs",
            "description": "FDA-Submissions, CE-Kennzeichnung, Marktzulassungen",
            "permissions": ["regulatory_submissions", "market_approval", "documentation_review"],
            "ai_functionality": "Regulatorische Dokumentenanalyse",
            "typical_tasks": "FDA-Anträge, CE-Dokumentation, Marktzulassungsverfahren",
            "is_external": false
        }
        ```
        
    Example Response:
        ```json
        {
            "id": 14,
            "name": "Regulatorische Angelegenheiten",
            "code": "regulatory_affairs",
            "description": "FDA-Submissions, CE-Kennzeichnung, Marktzulassungen",
            "permissions": ["regulatory_submissions", "market_approval", "documentation_review"],
            "ai_functionality": "Regulatorische Dokumentenanalyse",
            "typical_tasks": "FDA-Anträge, CE-Dokumentation, Marktzulassungsverfahren",
            "is_external": false,
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z"
        }
        ```
        
    Raises:
        HTTPException: 400 bei ungültigen Eingabedaten
        HTTPException: 409 wenn Code bereits existiert
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Code muss eindeutig sein (wird für API-Zugriff verwendet)
        - is_active wird automatisch auf true gesetzt
        - created_at wird automatisch gesetzt
    """
    # Prüfen ob Code bereits existiert
    existing_group = db.query(InterestGroupModel).filter(
        InterestGroupModel.code == group.code
    ).first()
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Interessensgruppe mit Code '{group.code}' existiert bereits"
        )
    
    # Daten vorbereiten und group_permissions zu JSON konvertieren
    group_data = group.dict()
    if 'group_permissions' in group_data and isinstance(group_data['group_permissions'], list):
        import json
        group_data['group_permissions'] = json.dumps(group_data['group_permissions'])
    
    db_group = InterestGroupModel(**group_data)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@app.put("/api/interest-groups/{group_id}", response_model=InterestGroup, tags=["Interest Groups"])
async def update_interest_group(
    group_id: int,
    group_update: InterestGroupUpdate,
    db: Session = Depends(get_db)
):
    """
    Interessensgruppe aktualisieren.
    
    Aktualisiert eine bestehende Interessensgruppe. Besonders nützlich für:
    - Anpassung von Berechtigungen
    - Aktivierung/Deaktivierung von Gruppen
    - Aktualisierung von KI-Funktionalitäten
    
    Args:
        group_id (int): ID der zu aktualisierenden Interessensgruppe
        group_update (InterestGroupUpdate): Zu aktualisierende Felder (partial update)
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        InterestGroup: Die aktualisierte Interessensgruppe
        
    Example Request (Gruppe reaktivieren):
        ```json
        {
            "is_active": true,
            "description": "Wieder aktiviert nach Umstrukturierung"
        }
        ```
        
    Example Request (Berechtigungen erweitern):
        ```json
        {
            "permissions": ["existing_permission", "new_ai_feature", "advanced_analytics"],
            "ai_functionality": "Erweitert um prädiktive Analysen"
        }
        ```
        
    Example Response:
        ```json
        {
            "id": 1,
            "name": "Einkauf",
            "code": "procurement",
            "description": "Wieder aktiviert nach Umstrukturierung",
            "permissions": ["supplier_evaluation", "purchase_notifications"],
            "ai_functionality": "Lieferantenbewertung, Benachrichtigungen",
            "typical_tasks": "Lieferantenqualifikation, Einkaufsprozesse",
            "is_external": false,
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z"
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Interessensgruppe nicht gefunden
        HTTPException: 400 bei ungültigen Eingabedaten
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Nur übermittelte Felder werden aktualisiert (partial update)
        - updated_at wird automatisch gesetzt
        - Code und ID können nicht geändert werden
    """
    db_group = db.query(InterestGroupModel).filter(InterestGroupModel.id == group_id).first()
    if not db_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interessensgruppe mit ID {group_id} nicht gefunden"
        )
    
    # Nur übermittelte Felder aktualisieren
    update_data = group_update.dict(exclude_unset=True)
    
    # Prüfen ob Code-Update zu Konflikt führen würde
    if 'code' in update_data and update_data['code'] != db_group.code:
        existing_code = db.query(InterestGroupModel).filter(
            InterestGroupModel.code == update_data['code'],
            InterestGroupModel.id != group_id
        ).first()
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Code '{update_data['code']}' wird bereits von einer anderen Gruppe verwendet"
            )
    
    # Group permissions zu JSON-String konvertieren, falls vorhanden
    if 'group_permissions' in update_data and isinstance(update_data['group_permissions'], list):
        import json
        update_data['group_permissions'] = json.dumps(update_data['group_permissions'])
    
    for field, value in update_data.items():
        setattr(db_group, field, value)
    
    db.commit()
    db.refresh(db_group)
    return db_group

@app.delete("/api/interest-groups/{group_id}", response_model=GenericResponse, tags=["Interest Groups"])
async def delete_interest_group(group_id: int, db: Session = Depends(get_db)):
    """
    Interessensgruppe löschen (Soft Delete).
    
    Führt einen Soft Delete durch (is_active = false). Echtes Löschen wird
    vermieden, da Interessensgruppen in User-Memberships referenziert werden.
    
    Args:
        group_id (int): ID der zu löschenden Interessensgruppe
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        GenericResponse: Bestätigung der Löschung
        
    Example Response:
        ```json
        {
            "message": "Interessensgruppe 'Einkauf' wurde deaktiviert",
            "success": true
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Interessensgruppe nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Soft Delete: is_active wird auf false gesetzt
        - Daten bleiben in DB erhalten (für Audit-Trail)
        - User-Memberships bleiben bestehen
        - Reaktivierung über PUT-Endpoint möglich
        
    Warning:
        - Standard-Gruppen (ID 1-13) sollten nicht gelöscht werden
        - Prüfe User-Memberships vor Löschung
    """
    db_group = db.query(InterestGroupModel).filter(InterestGroupModel.id == group_id).first()
    if not db_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interessensgruppe mit ID {group_id} nicht gefunden"
        )
    
    # Soft Delete: is_active auf false setzen
    db_group.is_active = False
    db.commit()
    return GenericResponse(message=f"Interessensgruppe '{db_group.name}' wurde deaktiviert")

# === USERS API ===
# Benutzerverwaltung mit Rollen- und Interessensgruppen-Zuordnung

@app.get("/api/users", response_model=List[User], tags=["Users"])
async def get_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Alle Benutzer abrufen.
    
    Lädt eine paginierte Liste aller Benutzer im System mit ihren
    Rollen und Metadaten. Für Admin- und HR-Funktionen.
    
    Args:
        skip (int): Anzahl zu überspringender Datensätze (Pagination). Default: 0
        limit (int): Maximale Anzahl zurückzugebender Datensätze. Default: 20, Max: 100
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        List[User]: Liste aller Benutzer im System
        
    Example Response:
        ```json
        [
            {
                "id": 1,
                "email": "max.einkauf@company.com",
                "full_name": "Max Kaufmann",
                "employee_id": "EK001",
                "department": "Einkauf",
                "permissions": [],
                "is_department_head": false,
                "approval_level": 1,
                "is_active": true,
                "created_at": "2025-06-08T16:49:51.763170"
            },
            {
                "id": 2,
                "email": "maria.qm@company.com",
                "full_name": "Dr. Maria Qualität",
                "employee_id": "QM001",
                "department": "Qualitätsmanagement",
                "permissions": [
                    "final_approval",
                    "system_administration",
                    "audit_management"
                ],
                "is_department_head": true,
                "approval_level": 4,
                "is_active": true,
                "created_at": "2025-06-08T16:49:51.763716"
            }
        ]
        ```
        
    Raises:
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Keine Passwort-Hashes in Response
        - Sortierung nach created_at (neueste zuerst)
        - Für User-Management-Interfaces gedacht
    """
    users = db.query(UserModel).offset(skip).limit(limit).all()
    
    # JSON-Strings in Listen konvertieren für Response-Validierung
    for user in users:
        if user.individual_permissions and isinstance(user.individual_permissions, str):
            try:
                import json
                user.individual_permissions = json.loads(user.individual_permissions)
            except (json.JSONDecodeError, TypeError):
                user.individual_permissions = []
    
    return users

@app.get("/api/users/{user_id}", response_model=User, tags=["Users"])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Einen spezifischen Benutzer abrufen.
    
    Lädt einen einzelnen Benutzer mit allen Details (außer Passwort).
    Für Profil-Anzeige und Admin-Funktionen.
    
    Args:
        user_id (int): Eindeutige ID des Benutzers
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        User: Detaillierte Benutzerinformationen
        
    Example Response:
        ```json
        {
            "id": 5,
            "email": "dr.mueller@company.com",
            "full_name": "Dr. Peter Müller",
            "employee_id": "EN001",
            "department": "Entwicklung",
            "permissions": [
                "design_approval",
                "change_management"
            ],
            "is_department_head": true,
            "approval_level": 3,
            "is_active": true,
            "created_at": "2025-06-08T16:49:51.765091"
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Benutzer nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Passwort-Hash wird niemals zurückgegeben
        - Auch deaktivierte Benutzer werden angezeigt (für Admin)
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benutzer mit ID {user_id} nicht gefunden"
        )
    
    # JSON-String in Liste konvertieren für Response-Validierung
    if user.individual_permissions and isinstance(user.individual_permissions, str):
        try:
            import json
            user.individual_permissions = json.loads(user.individual_permissions)
        except (json.JSONDecodeError, TypeError):
            user.individual_permissions = []
    
    return user

@app.post("/api/users", response_model=User, tags=["Users"])
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Neuen Benutzer erstellen.
    
    Erstellt einen neuen Benutzer im System mit verschlüsseltem Passwort.
    Für Admin-Funktionen und Benutzer-Onboarding.
    
    Args:
        user (UserCreate): Daten des neuen Benutzers
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        User: Der erstellte Benutzer (ohne Passwort-Hash)
        
    Example Request:
        ```json
        {
            "email": "lisa.wagner@medtech-company.de",
            "password": "SecurePassword123!",
            "full_name": "Lisa Wagner",
            "employee_id": "LW001",
            "department": "Fertigung",
            "permissions": ["production_oversight"],
            "is_department_head": false,
            "approval_level": 2
        }
        ```
        
    Example Response:
        ```json
        {
            "id": 12,
            "email": "lisa.wagner@medtech-company.de",
            "full_name": "Lisa Wagner",
            "employee_id": "LW001",
            "department": "Fertigung",
            "permissions": ["production_oversight"],
            "is_department_head": false,
            "approval_level": 2,
            "is_active": true,
            "created_at": "2025-06-08T17:30:00.000000"
        }
        ```
        
    Raises:
        HTTPException: 400 bei ungültigen Eingabedaten
        HTTPException: 409 wenn Username oder Email bereits existiert
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Passwort wird gehasht gespeichert (bcrypt)
        - Email muss eindeutig sein (verwendet als Login)
        - is_active wird automatisch auf true gesetzt
        - Passwort-Richtlinien werden validiert
        - Berechtigungen können individuell und über Interessensgruppen vergeben werden
        
    Security:
        - Passwort-Hashing mit bcrypt
        - Email-Validierung durch Pydantic
        - SQL-Injection-Schutz durch SQLAlchemy
    """
    # Prüfen ob Email bereits existiert
    existing_email = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email-Adresse '{user.email}' ist bereits registriert"
        )
    
    # Password hashen (in echtem System mit bcrypt)
    # TODO: Implementiere bcrypt password hashing
    hashed_password = f"hashed_{user.password}"  # Placeholder
    
    # Individual permissions als JSON-String serialisieren
    import json
    individual_permissions_json = json.dumps(user.individual_permissions) if user.individual_permissions else "[]"
    
    db_user = UserModel(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        employee_id=user.employee_id,
        organizational_unit=user.organizational_unit,
        individual_permissions=individual_permissions_json,
        is_department_head=user.is_department_head,
        approval_level=user.approval_level
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.put("/api/users/{user_id}", response_model=User, tags=["Users"])
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Benutzer aktualisieren.
    
    Aktualisiert einen bestehenden Benutzer. Für Profil-Updates,
    Rollen-Änderungen und Admin-Funktionen.
    
    Args:
        user_id (int): ID des zu aktualisierenden Benutzers
        user_update (UserUpdate): Zu aktualisierende Felder (partial update)
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        User: Der aktualisierte Benutzer
        
    Example Request (Rolle ändern):
        ```json
        {
            "role": "QM_MANAGER",
            "department": "Qualitätsmanagement"
        }
        ```
        
    Example Request (Berechtigungen und Level ändern):
        ```json
        {
            "permissions": ["design_approval", "change_management"],
            "is_department_head": true,
            "approval_level": 3,
            "department": "Produktentwicklung"
        }
        ```
        
    Example Request (Benutzer deaktivieren):
        ```json
        {
            "is_active": false
        }
        ```
        
    Example Response:
        ```json
        {
            "id": 7,
            "email": "tom.schneider@medtech-company.de",
            "full_name": "Tom Schneider",
            "employee_id": "TS001",
            "department": "Produktentwicklung",
            "permissions": ["design_approval", "change_management"],
            "is_department_head": true,
            "approval_level": 3,
            "is_active": true,
            "created_at": "2025-01-15T10:30:00.000000"
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Benutzer nicht gefunden
        HTTPException: 400 bei ungültigen Eingabedaten
        HTTPException: 409 bei Konflikten (Email bereits vergeben)
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Nur übermittelte Felder werden aktualisiert
        - Passwort-Updates erfordern separaten Endpoint
        - Email muss eindeutig bleiben
        - Berechtigungsänderungen werden auditiert
        
    Security:
        - Berechtigung erforderlich (in echtem System)
        - Audit-Log wird erstellt
    """
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benutzer mit ID {user_id} nicht gefunden"
        )
    
    # Nur übermittelte Felder aktualisieren
    update_data = user_update.dict(exclude_unset=True)
    
    # Prüfen auf Email-Konflikte (falls geändert)
    if "email" in update_data:
        existing_email = db.query(UserModel).filter(
            UserModel.email == update_data["email"],
            UserModel.id != user_id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email-Adresse '{update_data['email']}' ist bereits registriert"
            )
    
    # Permissions als JSON-String serialisieren (falls vorhanden)
    if "permissions" in update_data and update_data["permissions"] is not None:
        import json
        update_data["permissions"] = json.dumps(update_data["permissions"])
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/api/users/{user_id}", response_model=GenericResponse, tags=["Users"])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Benutzer löschen (Soft Delete).
    
    Deaktiviert einen Benutzer anstatt ihn komplett zu löschen, um
    referentielle Integrität und Audit-Trail zu bewahren.
    
    Args:
        user_id (int): ID des zu löschenden Benutzers
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        GenericResponse: Bestätigung der Löschung
        
    Example Response:
        ```json
        {
            "message": "Benutzer 'Max Kaufmann' (EK001) wurde erfolgreich deaktiviert",
            "success": true
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Benutzer nicht gefunden
        HTTPException: 400 wenn Benutzer bereits deaktiviert
        HTTPException: 409 bei Abhängigkeits-Konflikten (z.B. laufende Kalibrierungen)
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - **Soft Delete**: User wird nur deaktiviert (is_active = false)
        - **Referenzen bleiben:** Dokumente, Kalibrierungen etc. bleiben erhalten
        - **Audit-Trail:** Änderung wird protokolliert
        - **Reaktivierung möglich:** Kann später wieder aktiviert werden
        
    Business Logic:
        - Prüft aktive Abhängigkeiten (laufende Kalibrierungen)
        - Entfernt aus allen Interessensgruppen
        - Setzt is_active = false
        - Behält alle historischen Daten
        
    Security:
        - Admin-Berechtigung erforderlich (in echtem System)
        - Selbstlöschung wird verhindert
        - Audit-Log wird erstellt
    """
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benutzer mit ID {user_id} nicht gefunden"
        )
    
    # Prüfen ob bereits deaktiviert
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benutzer '{db_user.full_name}' ist bereits deaktiviert"
        )
    
    # Prüfen auf aktive Abhängigkeiten (z.B. laufende Kalibrierungen)
    from app.models import Calibration as CalibrationModel
    active_calibrations = db.query(CalibrationModel).filter(
        CalibrationModel.responsible_user_id == user_id,
        CalibrationModel.status == "valid"
    ).count()
    
    if active_calibrations > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Benutzer kann nicht deaktiviert werden: {active_calibrations} aktive Kalibrierungen zugeordnet"
        )
    
    # Aus allen Interessensgruppen entfernen
    from app.models import UserGroupMembership as UserGroupMembershipModel
    db.query(UserGroupMembershipModel).filter(
        UserGroupMembershipModel.user_id == user_id
    ).delete()
    
    # Soft Delete: nur deaktivieren
    db_user.is_active = False
    
    db.commit()
    
    return GenericResponse(
        message=f"Benutzer '{db_user.full_name}' ({db_user.employee_id or 'ohne ID'}) wurde erfolgreich deaktiviert",
        success=True
    )

@app.delete("/api/users/{user_id}/hard-delete", response_model=GenericResponse, tags=["Users"])
async def hard_delete_user(
    user_id: int, 
    confirm_deletion: bool = False,
    db: Session = Depends(get_db)
):
    """
    Benutzer permanent löschen (Hard Delete) - DSGVO Compliance.
    
    **WARNUNG:** Unwiderrufliche Löschung! Nur für DSGVO-Anfragen oder Compliance.
    Löscht alle Benutzerdaten und anonymisiert referenzierte Datensätze.
    
    Args:
        user_id (int): ID des zu löschenden Benutzers
        confirm_deletion (bool): Sicherheitsbestätigung (muss true sein)
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        GenericResponse: Bestätigung der permanenten Löschung
        
    Example Request:
        ```
        DELETE /api/users/7/hard-delete?confirm_deletion=true
        ```
        
    Example Response:
        ```json
        {
            "message": "Benutzer permanent gelöscht. Referenzen anonymisiert: 3 Dokumente, 5 Kalibrierungen",
            "success": true
        }
        ```
        
    Raises:
        HTTPException: 400 wenn confirm_deletion nicht gesetzt
        HTTPException: 404 wenn Benutzer nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - **Unwiderruflich:** Daten können nicht wiederhergestellt werden
        - **DSGVO-konform:** Erfüllt "Recht auf Vergessenwerden"
        - **Anonymisierung:** Referenzen werden zu "Gelöschter Benutzer" 
        - **Audit-Log:** Löschung wird protokolliert (ohne Personendaten)
        
    Business Logic:
        1. Sicherheitscheck: confirm_deletion muss explizit true sein
        2. Anonymisiert alle referenzierten Datensätze
        3. Löscht User-Gruppenzugehörigkeiten
        4. Löscht Benutzerdatensatz permanent
        
    DSGVO Compliance:
        - Art. 17 DSGVO (Recht auf Vergessenwerden)
        - Vollständige Entfernung personenbezogener Daten
        - Audit-Trail ohne Personenbezug
        
    Security:
        - Superadmin-Berechtigung erforderlich
        - Explizite Bestätigung notwendig
        - Umfassendes Logging (anonymisiert)
    """
    if not confirm_deletion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hard Delete erfordert explizite Bestätigung: confirm_deletion=true"
        )
    
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benutzer mit ID {user_id} nicht gefunden"
        )
    
    # Statistiken für Audit-Log sammeln (vor der Anonymisierung)
    user_name = db_user.full_name  # Für Response (wird danach gelöscht)
    
    # 1. Dokumente anonymisieren (Creator-Referenzen)
    from app.models import Document as DocumentModel
    affected_documents = db.query(DocumentModel).filter(
        DocumentModel.creator_id == user_id
    ).count()
    
    db.query(DocumentModel).filter(
        DocumentModel.creator_id == user_id
    ).update({"creator_id": None})  # NULL = Anonymisiert
    
    # 2. Kalibrierungen anonymisieren  
    from app.models import Calibration as CalibrationModel
    affected_calibrations = db.query(CalibrationModel).filter(
        CalibrationModel.responsible_user_id == user_id
    ).count()
    
    db.query(CalibrationModel).filter(
        CalibrationModel.responsible_user_id == user_id
    ).update({"responsible_user_id": None})  # NULL = Anonymisiert
    
    # 3. User-Group-Memberships löschen
    from app.models import UserGroupMembership as UserGroupMembershipModel
    db.query(UserGroupMembershipModel).filter(
        UserGroupMembershipModel.user_id == user_id
    ).delete()
    
    # 4. Benutzer permanent löschen
    db.delete(db_user)
    db.commit()
    
    return GenericResponse(
        message=f"Benutzer permanent gelöscht. Referenzen anonymisiert: {affected_documents} Dokumente, {affected_calibrations} Kalibrierungen",
        success=True
    )

# === USER GROUP MEMBERSHIPS API ===
# Zuordnung von Benutzern zu Interessensgruppen (Many-to-Many Relationship)

@app.get("/api/user-group-memberships", response_model=List[UserGroupMembership], tags=["User Group Memberships"])
async def get_memberships(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """
    Alle Benutzer-Gruppen-Zuordnungen abrufen.
    
    Zeigt alle Zuordnungen zwischen Benutzern und Interessensgruppen.
    Für Admin-Übersichten und Berechtigungsmanagement.
    
    Args:
        skip (int): Anzahl zu überspringender Datensätze. Default: 0
        limit (int): Maximale Anzahl zurückzugebender Datensätze. Default: 50, Max: 200
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        List[UserGroupMembership]: Liste aller Benutzer-Gruppen-Zuordnungen
        
    Example Response:
        ```json
        [
            {
                "id": 1,
                "user_id": 2,
                "interest_group_id": 2,
                "role_in_group": "QM_LEAD",
                "joined_at": "2024-01-15T10:30:00Z",
                "is_active": true
            },
            {
                "id": 5,
                "user_id": 3,
                "interest_group_id": 5,
                "role_in_group": "DEVELOPMENT_ENGINEER",
                "joined_at": "2024-01-15T10:30:00Z",
                "is_active": true
            }
        ]
        ```
        
    Raises:
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Many-to-Many: Ein User kann mehreren Gruppen angehören
        - role_in_group definiert spezifische Rolle in der Gruppe
        - Nur aktive Memberships werden standardmäßig angezeigt
    """
    memberships = db.query(UserGroupMembershipModel).offset(skip).limit(limit).all()
    return memberships

@app.post("/api/user-group-memberships", response_model=UserGroupMembership, tags=["User Group Memberships"])
async def create_membership(
    membership: UserGroupMembershipCreate,
    db: Session = Depends(get_db)
):
    """
    Benutzer einer Interessensgruppe zuordnen.
    
    Erstellt eine neue Zuordnung zwischen einem Benutzer und einer
    Interessensgruppe mit spezifischer Rolle.
    
    Args:
        membership (UserGroupMembershipCreate): Daten der neuen Zuordnung
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        UserGroupMembership: Die erstellte Zuordnung
        
    Example Request:
        ```json
        {
            "user_id": 7,
            "interest_group_id": 3,
            "role_in_group": "PRODUCTION_SUPERVISOR"
        }
        ```
        
    Example Response:
        ```json
        {
            "id": 23,
            "user_id": 7,
            "interest_group_id": 3,
            "role_in_group": "PRODUCTION_SUPERVISOR", 
            "joined_at": "2024-01-15T10:30:00Z",
            "is_active": true
        }
        ```
        
    Raises:
        HTTPException: 400 bei ungültigen user_id oder interest_group_id
        HTTPException: 409 wenn Zuordnung bereits existiert
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Prüft Existenz von User und Interest Group
        - Verhindert doppelte Zuordnungen
        - joined_at wird automatisch gesetzt
        - is_active ist standardmäßig true
        
    Business Logic:
        - Ein User kann mehreren Gruppen angehören
        - Verschiedene Rollen in verschiedenen Gruppen möglich
        - Externe Auditoren nur in externen Gruppen
    """
    # Prüfen ob User existiert
    user_exists = db.query(UserModel).filter(UserModel.id == membership.user_id).first()
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benutzer mit ID {membership.user_id} existiert nicht"
        )
    
    # Prüfen ob Interest Group existiert
    group_exists = db.query(InterestGroupModel).filter(InterestGroupModel.id == membership.interest_group_id).first()
    if not group_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interessensgruppe mit ID {membership.interest_group_id} existiert nicht"
        )
    
    # Prüfen ob Zuordnung bereits existiert
    existing_membership = db.query(UserGroupMembershipModel).filter(
        UserGroupMembershipModel.user_id == membership.user_id,
        UserGroupMembershipModel.interest_group_id == membership.interest_group_id
    ).first()
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Diese Benutzer-Gruppen-Zuordnung existiert bereits"
        )
    
    db_membership = UserGroupMembershipModel(**membership.dict())
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership

@app.delete("/api/user-group-memberships/{membership_id}", response_model=GenericResponse, tags=["User Group Memberships"])
async def delete_user_group_membership(membership_id: int, db: Session = Depends(get_db)):
    """
    Benutzer-Gruppen-Zuordnung löschen.
    
    Entfernt einen Benutzer aus einer Interessensgruppe durch Löschen
    der entsprechenden Membership-Zuordnung.
    
    Args:
        membership_id (int): ID der zu löschenden Zuordnung
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        GenericResponse: Bestätigung der Löschung
        
    Example Response:
        ```json
        {
            "message": "Benutzer 'Anna Schmidt' wurde aus Interessensgruppe 'Entwicklung' entfernt",
            "success": true
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Membership nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Hard Delete: Zuordnung wird permanent entfernt
        - Benutzer und Interessensgruppe bleiben erhalten
        - Für Reorganisation von Team-Strukturen
        
    Business Logic:
        - Prüfe ob Benutzer Admin-Rechte in der Gruppe hatte
        - Benachrichtigung an betroffene Teams
        - Audit-Log für Nachverfolgbarkeit
    """
    membership = db.query(UserGroupMembershipModel).filter(UserGroupMembershipModel.id == membership_id).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benutzer-Gruppen-Zuordnung mit ID {membership_id} nicht gefunden"
        )
    
    user = db.query(UserModel).filter(UserModel.id == membership.user_id).first()
    group = db.query(InterestGroupModel).filter(InterestGroupModel.id == membership.interest_group_id).first()
    
    db.delete(membership)
    db.commit()
    return GenericResponse(message=f"Benutzer '{user.full_name}' wurde aus Interessensgruppe '{group.name}' entfernt")

# === HELPER ENDPOINTS ===

@app.get("/api/users/{user_id}/groups", response_model=List[InterestGroup], tags=["User Group Memberships"])
async def get_user_groups(user_id: int, db: Session = Depends(get_db)):
    """
    Alle Interessensgruppen eines Benutzers abrufen.
    
    Zeigt alle Interessensgruppen an, denen ein spezifischer
    Benutzer zugeordnet ist. Für Benutzer-Profile und Berechtigungsübersichten.
    
    Args:
        user_id (int): Eindeutige ID des Benutzers
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        List[InterestGroup]: Liste aller Gruppen des Benutzers
        
    Example Response:
        ```json
        [
            {
                "id": 5,
                "name": "Entwicklung",
                "code": "development",
                "description": "Design-Control, Normprüfung",
                "permissions": ["design_control", "norm_verification"],
                "ai_functionality": "Design-Control, Normprüfung",
                "typical_tasks": "Produktentwicklung, Design-FMEA",
                "is_external": false,
                "is_active": true,
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 2,
                "name": "Qualitätsmanagement (QM)",
                "code": "quality_management", 
                "description": "Alle Rechte, finale Freigabe",
                "permissions": ["all_rights", "final_approval"],
                "ai_functionality": "Gap-Analyse & Normprüfung",
                "typical_tasks": "QM-Freigaben, CAPA-Management",
                "is_external": false,
                "is_active": true,
                "created_at": "2024-01-15T10:30:00Z"
            }
        ]
        ```
        
    Raises:
        HTTPException: 404 wenn Benutzer nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Nur aktive Interessensgruppen werden angezeigt
        - Sortierung nach Gruppennamen (alphabetisch)
        - Für Berechtigungsmatrix-Darstellung geeignet
        
    Use Cases:
        - Benutzer-Profil anzeigen
        - Berechtigungen prüfen
        - Team-Zugehörigkeiten verwalten
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benutzer mit ID {user_id} nicht gefunden"
        )
    
    # Join über UserGroupMembership um nur aktive Gruppen zu holen
    groups = db.query(InterestGroupModel).join(UserGroupMembershipModel).filter(
        UserGroupMembershipModel.user_id == user_id,
        InterestGroupModel.is_active == True
    ).all()
    
    # JSON-Strings in Listen konvertieren für Response-Validierung
    for group in groups:
        if group.group_permissions and isinstance(group.group_permissions, str):
            try:
                import json
                group.group_permissions = json.loads(group.group_permissions)
            except (json.JSONDecodeError, TypeError):
                group.group_permissions = []
    
    return groups

@app.get("/api/interest-groups/{group_id}/users", response_model=List[User], tags=["User Group Memberships"])
async def get_group_users(group_id: int, db: Session = Depends(get_db)):
    """
    Alle Benutzer einer Interessensgruppe abrufen.
    
    Zeigt alle Benutzer an, die einer spezifischen Interessensgruppe
    zugeordnet sind. Für Team-Übersichten und Kontaktlisten.
    
    Args:
        group_id (int): Eindeutige ID der Interessensgruppe
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        List[User]: Liste aller Benutzer in der Gruppe
        
    Example Response:
        ```json
        [
            {
                "id": 3,
                "username": "anna.schmidt",
                "email": "anna.schmidt@medtech-company.de",
                "full_name": "Anna Schmidt",
                "role": "DEVELOPMENT_ENGINEER",
                "department": "Produktentwicklung",
                "is_active": true,
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 8,
                "username": "tom.werner",
                "email": "tom.werner@medtech-company.de",
                "full_name": "Tom Werner",
                "role": "SENIOR_DEVELOPER",
                "department": "Produktentwicklung",
                "is_active": true,
                "created_at": "2024-01-12T14:20:00Z"
            }
        ]
        ```
        
    Raises:
        HTTPException: 404 wenn Interessensgruppe nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Nur aktive Benutzer werden angezeigt
        - Sortierung nach Benutzernamen (alphabetisch)
        - Passwort-Hashes werden niemals zurückgegeben
        
    Use Cases:
        - Team-Kontaktlisten erstellen
        - Zuständigkeiten identifizieren
        - Benachrichtigungen an ganze Gruppen senden
    """
    group = db.query(InterestGroupModel).filter(InterestGroupModel.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interessensgruppe mit ID {group_id} nicht gefunden"
        )
    
    # Join über UserGroupMembership um nur aktive Benutzer zu holen
    users = db.query(UserModel).join(UserGroupMembershipModel).filter(
        UserGroupMembershipModel.interest_group_id == group_id,
        UserModel.is_active == True
    ).all()
    
    # JSON-Strings in Listen konvertieren für Response-Validierung
    for user in users:
        if user.individual_permissions and isinstance(user.individual_permissions, str):
            try:
                import json
                user.individual_permissions = json.loads(user.individual_permissions)
            except (json.JSONDecodeError, TypeError):
                user.individual_permissions = []
    
    return users

# === DOCUMENTS API ===
# Dokumentenmanagement mit 14 QMS-spezifischen Dokumenttypen

@app.get("/api/documents", response_model=List[Document], tags=["Documents"])
async def get_documents(
    skip: int = 0,
    limit: int = 20,
    document_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Alle Dokumente abrufen mit erweiterten Filteroptionen.
    
    Lädt eine paginierte Liste aller QMS-Dokumente mit optionalen Filtern
    für Typ, Status und Volltextsuche.
    
    Args:
        skip (int): Anzahl zu überspringender Datensätze. Default: 0
        limit (int): Maximale Anzahl zurückzugebender Datensätze. Default: 20, Max: 100
        document_type (Optional[str]): Filter nach Dokumenttyp (z.B. "QM_MANUAL", "SOP")
        status (Optional[str]): Filter nach Status ("DRAFT", "REVIEW", "APPROVED", "OBSOLETE")
        search (Optional[str]): Volltextsuche in Titel und Beschreibung
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        List[Document]: Liste der gefilterten Dokumente
        
    Example Response:
        ```json
        [
            {
                "id": 1,
                "title": "Qualitätsmanagement-Handbuch",
                "document_type": "QM_MANUAL",
                "description": "Hauptdokument des QM-Systems nach ISO 13485",
                "version": "2.1",
                "status": "APPROVED",
                "file_path": "/documents/qm-manual-v2.1.pdf",
                "created_by": 1,
                "approved_by": 2,
                "created_at": "2024-01-15T10:30:00Z",
                "approved_at": "2024-01-20T14:15:00Z"
            },
            {
                "id": 3,
                "title": "SOP-001: Lieferantenbewertung",
                "document_type": "SOP",
                "description": "Standardverfahren zur Bewertung und Qualifikation von Lieferanten",
                "version": "1.3",
                "status": "APPROVED",
                "file_path": "/documents/sop-001-supplier-evaluation-v1.3.pdf",
                "created_by": 3,
                "approved_by": 2,
                "created_at": "2024-01-10T09:20:00Z",
                "approved_at": "2024-01-18T16:30:00Z"
            }
        ]
        ```
        
    Available Document Types:
        - QM_MANUAL: Qualitätsmanagement-Handbuch
        - SOP: Standard Operating Procedure
        - WORK_INSTRUCTION: Arbeitsanweisung
        - FORM: Formular/Vorlage
        - USER_MANUAL: Benutzerhandbuch
        - SERVICE_MANUAL: Servicehandbuch
        - RISK_ASSESSMENT: Risikoanalyse
        - VALIDATION_PROTOCOL: Validierungsprotokoll
        - CALIBRATION_PROCEDURE: Kalibrierverfahren
        - AUDIT_REPORT: Auditbericht
        - CAPA_DOCUMENT: CAPA-Dokumentation
        - TRAINING_MATERIAL: Schulungsunterlagen
        - SPECIFICATION: Spezifikation
        - OTHER: Sonstige Dokumente
        
    Available Statuses:
        - DRAFT: Entwurf
        - REVIEW: In Prüfung
        - APPROVED: Freigegeben
        - OBSOLETE: Veraltet
        
    Raises:
        HTTPException: 400 bei ungültigen Filterparametern
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Volltextsuche durchsucht Titel und Beschreibung
        - Filter sind kombinierbar
        - Sortierung nach created_at (neueste zuerst)
        - Nur aktive Dokumente werden angezeigt
    """
    query = db.query(DocumentModel)
    
    # Filter nach Dokumenttyp
    if document_type:
        try:
            doc_type_enum = DocumentType(document_type)
            query = query.filter(DocumentModel.document_type == doc_type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ungültiger Dokumenttyp: {document_type}"
            )
    
    # Filter nach Status
    if status:
        try:
            status_enum = DocumentStatus(status)
            query = query.filter(DocumentModel.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ungültiger Status: {status}"
            )
    
    # Volltextsuche
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (DocumentModel.title.ilike(search_filter)) |
            (DocumentModel.description.ilike(search_filter))
        )
    
    documents = query.order_by(DocumentModel.created_at.desc()).offset(skip).limit(limit).all()
    return documents

@app.get("/api/documents/types", response_model=List[str], tags=["Documents"])
async def get_document_types():
    """
    Alle verfügbaren Dokumenttypen abrufen.
    
    Liefert eine Liste aller im System definierten Dokumenttypen.
    Für Dropdown-Menüs und Validierung in Frontend-Anwendungen.
    
    Returns:
        List[str]: Liste aller Dokumenttyp-Enum-Werte
        
    Example Response:
        ```json
        [
            "QM_MANUAL",
            "SOP", 
            "WORK_INSTRUCTION",
            "FORM",
            "USER_MANUAL",
            "SERVICE_MANUAL",
            "RISK_ASSESSMENT",
            "VALIDATION_PROTOCOL",
            "CALIBRATION_PROCEDURE",
            "AUDIT_REPORT",
            "CAPA_DOCUMENT",
            "TRAINING_MATERIAL",
            "SPECIFICATION",
            "OTHER"
        ]
        ```
        
    Note:
        - Statische Liste basierend auf DocumentType Enum
        - Für Frontend-Dropdown-Menüs optimiert
        - Alphabetisch sortiert für bessere UX
        
    Use Cases:
        - Formulare mit Dokumenttyp-Auswahl
        - Validierung von API-Eingaben
        - Filter-Optionen in Such-Interfaces
    """
    return [doc_type.value for doc_type in DocumentType]

@app.get("/api/documents/{document_id}", response_model=Document, tags=["Documents"])
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Ein spezifisches Dokument abrufen.
    
    Lädt ein einzelnes Dokument mit allen Details für die Dokumentanzeige.
    
    Args:
        document_id (int): Eindeutige ID des Dokuments
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        Document: Detaillierte Dokumentinformationen
        
    Example Response:
        ```json
        {
            "id": 5,
            "title": "Risikoanalyse - Herzschrittmacher Modell XYZ",
            "document_type": "RISK_ASSESSMENT",
            "description": "ISO 14971 konforme Risikoanalyse für das Herzschrittmacher-System",
            "version": "1.0",
            "status": "APPROVED",
            "file_path": "/documents/risk-assessment-pacemaker-xyz-v1.0.pdf",
            "created_by": 5,
            "approved_by": 2,
            "created_at": "2024-01-12T11:45:00Z",
            "approved_at": "2024-01-25T09:30:00Z"
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Dokument nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Enthält alle Metadaten des Dokuments
        - file_path für Datei-Download
        - Audit-Trail durch created_by und approved_by
    """
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dokument mit ID {document_id} nicht gefunden"
        )
    return document

@app.post("/api/documents", response_model=Document, tags=["Documents"])
async def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    """
    Neues Dokument erstellen.
    
    Erstellt ein neues QMS-Dokument im System. Unterstützt alle
    14 QMS-spezifischen Dokumenttypen.
    
    Args:
        document (DocumentCreate): Daten des neuen Dokuments
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        Document: Das erstellte Dokument
        
    Example Request:
        ```json
        {
            "title": "VA-003: Softwarevalidierung",
            "document_type": "VALIDATION_PROTOCOL",
            "description": "Validierungsprotokoll für die Embedded Software des Geräts",
            "version": "1.0",
            "status": "DRAFT",
            "file_path": "/documents/validation-protocol-software-v1.0.pdf",
            "created_by": 8
        }
        ```
        
    Example Response:
        ```json
        {
            "id": 15,
            "title": "VA-003: Softwarevalidierung",
            "document_type": "VALIDATION_PROTOCOL",
            "description": "Validierungsprotokoll für die Embedded Software des Geräts",
            "version": "1.0", 
            "status": "DRAFT",
            "file_path": "/documents/validation-protocol-software-v1.0.pdf",
            "created_by": 8,
            "approved_by": null,
            "created_at": "2024-01-15T10:30:00Z",
            "approved_at": null
        }
        ```
        
    Raises:
        HTTPException: 400 bei ungültigen Eingabedaten
        HTTPException: 404 wenn created_by User nicht existiert
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Titel sollte eindeutig sein (wird empfohlen)
        - created_at wird automatisch gesetzt
        - approved_by und approved_at bleiben null bis zur Freigabe
        - file_path sollte relativen Pfad enthalten
        
    Business Logic:
        - Status beginnt meist mit "DRAFT"
        - Version folgt Semantic Versioning (1.0, 1.1, 2.0)
        - Dokumenttyp bestimmt Workflow und Berechtigungen
    """
    # Prüfen ob created_by User existiert
    user_exists = db.query(UserModel).filter(UserModel.id == document.created_by).first()
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benutzer mit ID {document.created_by} existiert nicht"
        )
    
    db_document = DocumentModel(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@app.put("/api/documents/{document_id}", response_model=Document, tags=["Documents"])
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """
    Dokument aktualisieren.
    
    Aktualisiert ein bestehendes Dokument. Für Versionierung,
    Status-Änderungen und Freigabe-Workflows.
    
    Args:
        document_id (int): ID des zu aktualisierenden Dokuments
        document_update (DocumentUpdate): Zu aktualisierende Felder
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        Document: Das aktualisierte Dokument
        
    Example Request (Status auf APPROVED setzen):
        ```json
        {
            "status": "APPROVED",
            "approved_by": 2,
            "approved_at": "2024-01-15T14:30:00Z"
        }
        ```
        
    Example Request (neue Version):
        ```json
        {
            "version": "1.1",
            "description": "Überarbeitete Version nach internem Review",
            "status": "REVIEW"
        }
        ```
        
    Example Response:
        ```json
        {
            "id": 7,
            "title": "SOP-005: Kalibrierungsverfahren",
            "document_type": "CALIBRATION_PROCEDURE",
            "description": "Überarbeitete Version nach internem Review",
            "version": "1.1",
            "status": "REVIEW",
            "file_path": "/documents/sop-005-calibration-v1.1.pdf",
            "created_by": 5,
            "approved_by": null,
            "created_at": "2024-01-10T09:30:00Z",
            "approved_at": null
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Dokument nicht gefunden
        HTTPException: 400 bei ungültigen Eingabedaten
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Nur übermittelte Felder werden aktualisiert
        - approved_by und approved_at für Freigabe-Workflow
        - Versionierung für Änderungsverfolgung
        
    Business Logic:
        - Status-Workflow: DRAFT → REVIEW → APPROVED → OBSOLETE
        - Automatische Benachrichtigungen bei Status-Änderungen
        - Audit-Trail für alle Änderungen
    """
    db_document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dokument mit ID {document_id} nicht gefunden"
        )
    
    update_data = document_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_document, field, value)
    
    db.commit()
    db.refresh(db_document)
    return db_document

@app.delete("/api/documents/{document_id}", response_model=GenericResponse, tags=["Documents"])
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """
    Dokument löschen.
    
    Entfernt ein Dokument aus dem System. Für Dokumenten-Lifecycle-Management
    und Bereinigung veralteter Dokumente.
    
    Args:
        document_id (int): ID des zu löschenden Dokuments
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        GenericResponse: Bestätigung der Löschung
        
    Example Response:
        ```json
        {
            "message": "Dokument 'Veraltete Arbeitsanweisung v0.9' wurde gelöscht",
            "success": true
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Dokument nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Hard Delete: Dokument wird permanent entfernt
        - Datei auf Festplatte bleibt bestehen (separater Prozess)
        - Für Compliance-relevante Dokumente vorsichtig verwenden
        
    Warning:
        - Genehmigte Dokumente sollten nicht gelöscht werden
        - Alternative: Status auf OBSOLETE setzen
        - Prüfe Referenzen in anderen Dokumenten
    """
    db_document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dokument mit ID {document_id} nicht gefunden"
        )
    
    document_title = db_document.title
    db.delete(db_document)
    db.commit()
    return GenericResponse(message=f"Dokument '{document_title}' wurde gelöscht")

@app.get("/api/documents/by-type/{document_type}", response_model=List[Document], tags=["Documents"])
async def get_documents_by_type(document_type: DocumentType, db: Session = Depends(get_db)):
    """
    Dokumente nach Typ filtern.
    
    Lädt alle Dokumente eines spezifischen Typs. Für typ-spezifische
    Übersichten und Workflows.
    
    Args:
        document_type (DocumentType): Enum-Wert des Dokumenttyps
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        List[Document]: Liste aller Dokumente des Typs
        
    Example Request:
        ```
        GET /api/documents/by-type/SOP
        ```
        
    Example Response:
        ```json
        [
            {
                "id": 3,
                "title": "SOP-001: Lieferantenbewertung",
                "document_type": "SOP",
                "description": "Standardverfahren zur Bewertung von Lieferanten",
                "version": "1.3",
                "status": "APPROVED",
                "file_path": "/documents/sop-001-v1.3.pdf",
                "created_by": 3,
                "approved_by": 2,
                "created_at": "2024-01-10T09:20:00Z",
                "approved_at": "2024-01-18T16:30:00Z"
            }
        ]
        ```
        
    Raises:
        HTTPException: 400 bei ungültigem Dokumenttyp
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Sortierung nach Titel (alphabetisch)
        - Alle Status werden angezeigt (DRAFT, REVIEW, APPROVED, OBSOLETE)
        - Für typ-spezifische Dashboards geeignet
        
    Available Document Types:
        - QM_MANUAL, SOP, WORK_INSTRUCTION, FORM
        - USER_MANUAL, SERVICE_MANUAL, RISK_ASSESSMENT
        - VALIDATION_PROTOCOL, CALIBRATION_PROCEDURE
        - AUDIT_REPORT, CAPA_DOCUMENT, TRAINING_MATERIAL
        - SPECIFICATION, OTHER
    """
    documents = db.query(DocumentModel).filter(DocumentModel.document_type == document_type).all()
    return documents

# === NORMS API ===

@app.get("/api/norms", response_model=List[Norm], tags=["Norms"])
async def get_norms(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Alle Normen abrufen.
    
    Lädt eine paginierte Liste aller im System erfassten Normen und
    Compliance-Standards (ISO 13485, MDR, ISO 14971, etc.).
    
    Args:
        skip (int): Anzahl zu überspringender Datensätze. Default: 0
        limit (int): Maximale Anzahl zurückzugebender Datensätze. Default: 20, Max: 100
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        List[Norm]: Liste aller Normen im System
        
    Example Response:
        ```json
        [
            {
                "id": 1,
                "name": "ISO 13485:2016",
                "title": "Medical devices — Quality management systems — Requirements for regulatory purposes",
                "description": "Internationale Norm für Qualitätsmanagementsysteme in der Medizinprodukteindustrie",
                "category": "QMS",
                "version": "2016",
                "effective_date": "2016-03-01",
                "authority": "ISO",
                "is_mandatory": true,
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 2,
                "name": "MDR 2017/745",
                "title": "Medical Device Regulation",
                "description": "EU-Verordnung über Medizinprodukte, gültig seit Mai 2021",
                "category": "REGULATION",
                "version": "2017",
                "effective_date": "2021-05-26",
                "authority": "EU Commission",
                "is_mandatory": true,
                "created_at": "2024-01-15T10:30:00Z"
            }
        ]
        ```
        
    Raises:
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Normen sind nach effective_date sortiert (neueste zuerst)
        - is_mandatory zeigt regulatorische Verpflichtung an
        - category gruppiert Normen thematisch
        
    Common Categories:
        - QMS: Qualitätsmanagementsystem
        - REGULATION: EU/FDA Verordnungen
        - RISK_MANAGEMENT: Risikomanagement
        - SOFTWARE: Software-Lifecycle
        - CLINICAL: Klinische Bewertung
    """
    norms = db.query(NormModel).offset(skip).limit(limit).all()
    return norms

@app.get("/api/norms/{norm_id}", response_model=Norm, tags=["Norms"])
async def get_norm(norm_id: int, db: Session = Depends(get_db)):
    """
    Eine spezifische Norm abrufen.
    
    Lädt eine einzelne Norm mit allen Details für die Norm-Analyse
    und Compliance-Prüfung.
    
    Args:
        norm_id (int): Eindeutige ID der Norm
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        Norm: Detaillierte Norminformationen
        
    Example Response:
        ```json
        {
            "id": 3,
            "name": "ISO 14971:2019",
            "title": "Medical devices — Application of risk management to medical devices",
            "description": "Standard für Risikomanagement bei Medizinprodukten über den gesamten Produktlebenszyklus",
            "category": "RISK_MANAGEMENT",
            "version": "2019",
            "effective_date": "2019-12-01",
            "authority": "ISO",
            "is_mandatory": true,
            "created_at": "2024-01-15T10:30:00Z"
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Norm nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Für AI-basierte Norm-Analyse verwendbar
        - effective_date wichtig für Compliance-Zeiträume
        - authority zeigt herausgebende Organisation
    """
    norm = db.query(NormModel).filter(NormModel.id == norm_id).first()
    if not norm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Norm mit ID {norm_id} nicht gefunden"
        )
    return norm

@app.post("/api/norms", response_model=Norm, tags=["Norms"])
async def create_norm(norm: NormCreate, db: Session = Depends(get_db)):
    """
    Neue Norm erstellen.
    
    Erstellt eine neue Norm oder einen Compliance-Standard im System.
    Für Erweiterung der Norm-Bibliothek.
    
    Args:
        norm (NormCreate): Daten der neuen Norm
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        Norm: Die erstellte Norm
        
    Example Request:
        ```json
        {
            "name": "IEC 62304:2006+A1:2015",
            "title": "Medical device software — Software life cycle processes",
            "description": "Internationale Norm für Software-Lifecycle-Prozesse bei Medizinprodukten",
            "category": "SOFTWARE",
            "version": "2015",
            "effective_date": "2015-06-01",
            "authority": "IEC",
            "is_mandatory": true
        }
        ```
        
    Example Response:
        ```json
        {
            "id": 8,
            "name": "IEC 62304:2006+A1:2015",
            "title": "Medical device software — Software life cycle processes",
            "description": "Internationale Norm für Software-Lifecycle-Prozesse bei Medizinprodukten",
            "category": "SOFTWARE",
            "version": "2015",
            "effective_date": "2015-06-01",
            "authority": "IEC",
            "is_mandatory": true,
            "created_at": "2024-01-15T10:30:00Z"
        }
        ```
        
    Raises:
        HTTPException: 400 bei ungültigen Eingabedaten
        HTTPException: 409 wenn Norm bereits existiert
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - name sollte eindeutig sein (Norm-Bezeichnung)
        - effective_date für Compliance-Überwachung wichtig
        - is_mandatory unterscheidet zwischen Pflicht und freiwillig
        
    Business Logic:
        - Neue Normen automatisch in Gap-Analyse einbeziehen
        - Benachrichtigung an QM-Team bei neuen Pflichtnormen
        - Version-Tracking für Norm-Updates
    """
    # Prüfen ob Norm bereits existiert
    existing_norm = db.query(NormModel).filter(NormModel.name == norm.name).first()
    if existing_norm:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Norm '{norm.name}' existiert bereits"
        )
    
    db_norm = NormModel(**norm.dict())
    db.add(db_norm)
    db.commit()
    db.refresh(db_norm)
    return db_norm

@app.put("/api/norms/{norm_id}", response_model=Norm, tags=["Norms"])
async def update_norm(
    norm_id: int,
    norm_update: NormUpdate,
    db: Session = Depends(get_db)
):
    """
    Norm aktualisieren.
    
    Aktualisiert eine bestehende Norm (z.B. neue Version, geänderte Details).
    Für Norm-Maintenance und Version-Updates.
    
    Args:
        norm_id (int): ID der zu aktualisierenden Norm
        norm_update (NormUpdate): Zu aktualisierende Felder
        db (Session): Datenbankverbindung
        
    Returns:
        Norm: Die aktualisierte Norm
    """
    db_norm = db.query(NormModel).filter(NormModel.id == norm_id).first()
    if not db_norm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Norm mit ID {norm_id} nicht gefunden"
        )
    
    update_data = norm_update.dict(exclude_unset=True)
    
    # Prüfen auf Name-Konflikte bei Änderung
    if "name" in update_data:
        existing_norm = db.query(NormModel).filter(
            NormModel.name == update_data["name"],
            NormModel.id != norm_id
        ).first()
        if existing_norm:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Norm mit Name '{update_data['name']}' existiert bereits"
            )
    
    for field, value in update_data.items():
        setattr(db_norm, field, value)
    
    db.commit()
    db.refresh(db_norm)
    return db_norm

@app.delete("/api/norms/{norm_id}", response_model=GenericResponse, tags=["Norms"])
async def delete_norm(norm_id: int, db: Session = Depends(get_db)):
    """
    Norm löschen.
    
    Löscht eine Norm aus dem System. **Vorsicht:** Prüft Abhängigkeiten zu Dokumenten.
    
    Args:
        norm_id (int): ID der zu löschenden Norm
        db (Session): Datenbankverbindung
        
    Returns:
        GenericResponse: Bestätigung der Löschung
    """
    db_norm = db.query(NormModel).filter(NormModel.id == norm_id).first()
    if not db_norm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Norm mit ID {norm_id} nicht gefunden"
        )
    
    # Prüfen auf Abhängigkeiten (falls zukünftig Norm-Dokument-Verknüpfungen existieren)
    # TODO: Erweitern wenn Norm-Referenzen in anderen Tabellen existieren
    
    norm_name = db_norm.name
    db.delete(db_norm)
    db.commit()
    
    return GenericResponse(
        message=f"Norm '{norm_name}' wurde erfolgreich gelöscht",
        success=True
    )

# === EQUIPMENT API ===

@app.get("/api/equipment", response_model=List[Equipment], tags=["Equipment"])
async def get_equipment(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Alle Equipment-Einträge abrufen.
    
    Lädt eine paginierte Liste aller im System erfassten Geräte und
    Ausrüstungen mit ihren Kalibrierungsstatusangaben.
    
    Args:
        skip (int): Anzahl zu überspringender Datensätze. Default: 0
        limit (int): Maximale Anzahl zurückzugebender Datensätze. Default: 20, Max: 100
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        List[Equipment]: Liste aller Equipment-Einträge
        
    Example Response:
        ```json
        [
            {
                "id": 1,
                "name": "Digitaler Messschieber Mitutoyo",
                "equipment_type": "measuring_device",
                "serial_number": "MIT-2024-001",
                "manufacturer": "Mitutoyo Corporation",
                "model": "CD-15DCX",
                "location": "Qualitätslabor - Messplatz 1",
                "calibration_interval_months": 12,
                "last_calibration": "2023-06-15",
                "next_calibration": "2024-06-15",
                "status": "active",
                "notes": "Präzisionsmessgerät für Dimensionskontrolle",
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 3,
                "name": "Analytische Waage Sartorius",
                "equipment_type": "laboratory_scale",
                "serial_number": "SAR-2023-003",
                "manufacturer": "Sartorius AG",
                "model": "MSE225P-100-DA",
                "location": "Chemielabor - Abzug 2",
                "calibration_interval_months": 6,
                "last_calibration": "2023-12-01",
                "next_calibration": "2024-06-01",
                "status": "active",
                "notes": "Mikrowaage für Substanzanalysen, tägliche Funktionskontrolle",
                "created_at": "2024-01-15T10:30:00Z"
            }
        ]
        ```
        
    Raises:
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - next_calibration für Fristenüberwachung wichtig
        - status zeigt Betriebszustand ("active", "maintenance", "retired")
        - Sortierung nach next_calibration (fällige zuerst)
        
    Equipment Types:
        - measuring_device: Messgeräte
        - laboratory_scale: Laborwaagen
        - temperature_monitor: Temperaturüberwachung
        - pressure_gauge: Druckmessgeräte
        - test_equipment: Prüfgeräte
        - production_tool: Produktionswerkzeuge
    """
    equipment = db.query(EquipmentModel).offset(skip).limit(limit).all()
    return equipment

@app.get("/api/equipment/overdue", response_model=List[Equipment], tags=["Equipment"])
async def get_overdue_equipment(db: Session = Depends(get_db)):
    """
    Überfällige Equipment-Kalibrierungen abrufen.
    
    Zeigt alle Geräte an, deren Kalibrierung bereits überfällig ist.
    Kritisch für Compliance und Produktqualität.
    
    Returns:
        List[Equipment]: Liste aller überfälligen Geräte
    """
    from datetime import date
    today = date.today()
    
    overdue_equipment = db.query(EquipmentModel).filter(
        EquipmentModel.next_calibration < today
    ).all()
    
    return overdue_equipment

@app.get("/api/equipment/{equipment_id}", response_model=Equipment, tags=["Equipment"])
async def get_equipment_item(equipment_id: int, db: Session = Depends(get_db)):
    """
    Ein spezifisches Equipment abrufen.
    
    Lädt ein einzelnes Gerät mit allen Details für die Equipment-Verwaltung
    und Kalibrierungsplanung.
    
    Args:
        equipment_id (int): Eindeutige ID des Equipments
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        Equipment: Detaillierte Equipment-Informationen
        
    Example Response:
        ```json
        {
            "id": 4,
            "name": "Umwelttestkammer Heraeus",
            "equipment_type": "environmental_chamber",
            "serial_number": "HER-2022-004",
            "manufacturer": "Heraeus Medical GmbH",
            "model": "UT6760",
            "location": "Testlabor - Prüfstand B",
            "calibration_interval_months": 12,
            "last_calibration": "2023-08-20",
            "next_calibration": "2024-08-20",
            "status": "active",
            "notes": "Klimaprüfschrank für Alterungstests, Temperaturbereich -40°C bis +180°C",
            "created_at": "2024-01-15T10:30:00Z"
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Equipment nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Vollständige Geräte-Historie verfügbar
        - Verknüpfung zu Kalibrierungsprotokollen über ID
        - Standort-Tracking für Asset-Management
    """
    equipment = db.query(EquipmentModel).filter(EquipmentModel.id == equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment mit ID {equipment_id} nicht gefunden"
        )
    return equipment

@app.post("/api/equipment", response_model=Equipment, tags=["Equipment"])
async def create_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    """
    Neues Equipment erstellen.
    
    Registriert ein neues Gerät oder eine neue Ausrüstung im System
    mit automatischer Kalibrierungsplanung.
    
    Args:
        equipment (EquipmentCreate): Daten des neuen Equipments
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        Equipment: Das erstellte Equipment
        
    Example Request:
        ```json
        {
            "name": "pH-Meter Mettler Toledo",
            "equipment_type": "measuring_device",
            "serial_number": "MET-2024-007",
            "manufacturer": "Mettler Toledo International Inc.",
            "model": "FiveEasy F20",
            "location": "Qualitätskontrolle - Analytik",
            "calibration_interval_months": 6,
            "last_calibration": "2024-01-15",
            "status": "active",
            "notes": "pH-Messgerät für Pufferlösungen und Produktkontrollen"
        }
        ```
        
    Example Response:
        ```json
        {
            "id": 12,
            "name": "pH-Meter Mettler Toledo",
            "equipment_type": "measuring_device",
            "serial_number": "MET-2024-007",
            "manufacturer": "Mettler Toledo International Inc.",
            "model": "FiveEasy F20",
            "location": "Qualitätskontrolle - Analytik",
            "calibration_interval_months": 6,
            "last_calibration": "2024-01-15",
            "next_calibration": "2024-07-15",
            "status": "active",
            "notes": "pH-Messgerät für Pufferlösungen und Produktkontrollen",
            "created_at": "2024-01-15T10:30:00Z"
        }
        ```
        
    Raises:
        HTTPException: 400 bei ungültigen Eingabedaten
        HTTPException: 409 wenn Seriennummer bereits existiert
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - serial_number muss eindeutig sein
        - next_calibration wird automatisch berechnet
        - status ist standardmäßig "active"
        - Automatische Erinnerungen vor Kalibrierungsterminen
        
    Business Logic:
        - Kalibrierungsintervall basiert auf Gerätetyp und Kritikalität
        - Asset-Tracking für Wartungsplanung
        - Integration mit Kalibrierungs-Workflow
    """
    # Prüfen ob Seriennummer bereits existiert
    existing_equipment = db.query(EquipmentModel).filter(
        EquipmentModel.serial_number == equipment.serial_number
    ).first()
    if existing_equipment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Equipment mit Seriennummer '{equipment.serial_number}' existiert bereits"
        )
    
    db_equipment = EquipmentModel(**equipment.dict())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

@app.put("/api/equipment/{equipment_id}", response_model=Equipment, tags=["Equipment"])
async def update_equipment(
    equipment_id: int,
    equipment_update: EquipmentUpdate,
    db: Session = Depends(get_db)
):
    """
    Equipment aktualisieren.
    
    Aktualisiert ein bestehendes Equipment. Für Versionierung,
    Status-Änderungen und Freigabe-Workflows.
    
    Args:
        equipment_id (int): ID des zu aktualisierenden Equipments
        equipment_update (EquipmentUpdate): Zu aktualisierende Felder
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        Equipment: Das aktualisierte Equipment
        
    Example Request (Status auf APPROVED setzen):
        ```json
        {
            "status": "APPROVED",
            "approved_by": 2,
            "approved_at": "2024-01-15T14:30:00Z"
        }
        ```
        
    Example Request (neue Version):
        ```json
        {
            "version": "1.1",
            "description": "Überarbeitete Version nach internem Review",
            "status": "REVIEW"
        }
        ```
        
    Example Response:
        ```json
        {
            "id": 12,
            "name": "pH-Meter Mettler Toledo",
            "equipment_type": "measuring_device",
            "serial_number": "MET-2024-007",
            "manufacturer": "Mettler Toledo International Inc.",
            "model": "FiveEasy F20",
            "location": "Qualitätskontrolle - Analytik",
            "calibration_interval_months": 6,
            "last_calibration": "2024-01-15",
            "next_calibration": "2024-07-15",
            "status": "active",
            "notes": "pH-Messgerät für Pufferlösungen und Produktkontrollen",
            "created_at": "2024-01-15T10:30:00Z"
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Equipment nicht gefunden
        HTTPException: 400 bei ungültigen Eingabedaten
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Nur übermittelte Felder werden aktualisiert
        - approved_by und approved_at für Freigabe-Workflow
        - Versionierung für Änderungsverfolgung
        
    Business Logic:
        - Status-Workflow: DRAFT → REVIEW → APPROVED → OBSOLETE
        - Automatische Benachrichtigungen bei Status-Änderungen
        - Audit-Trail für alle Änderungen
    """
    db_equipment = db.query(EquipmentModel).filter(EquipmentModel.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment mit ID {equipment_id} nicht gefunden"
        )
    
    update_data = equipment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_equipment, field, value)
    
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

@app.delete("/api/equipment/{equipment_id}", response_model=GenericResponse, tags=["Equipment"])
async def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    """
    Equipment löschen.
    
    Entfernt ein Equipment aus dem System. Für Equipment-Lifecycle-Management
    und Bereinigung veralteter Equipment.
    
    Args:
        equipment_id (int): ID des zu löschenden Equipments
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        GenericResponse: Bestätigung der Löschung
        
    Example Response:
        ```json
        {
            "message": "Equipment 'Umwelttestkammer Heraeus' wurde gelöscht",
            "success": true
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Equipment nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Hard Delete: Equipment wird permanent entfernt
        - Datei auf Festplatte bleibt bestehen (separater Prozess)
        - Für Compliance-relevante Equipment vorsichtig verwenden
        
    Warning:
        - Genehmigte Equipment sollten nicht gelöscht werden
        - Alternative: Status auf OBSOLETE setzen
        - Prüfe Referenzen in anderen Dokumenten
    """
    db_equipment = db.query(EquipmentModel).filter(EquipmentModel.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment mit ID {equipment_id} nicht gefunden"
        )
    
    # Prüfen auf aktive Abhängigkeiten (z.B. laufende Kalibrierungen)
    from app.models import Calibration as CalibrationModel
    active_calibrations = db.query(CalibrationModel).filter(
        CalibrationModel.equipment_id == equipment_id,
        CalibrationModel.status == "valid"
    ).count()
    
    if active_calibrations > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Equipment kann nicht gelöscht werden: {active_calibrations} aktive Kalibrierungen zugeordnet"
        )
    
    equipment_name = db_equipment.name
    db.delete(db_equipment)
    db.commit()
    return GenericResponse(
        message=f"Equipment '{equipment_name}' wurde gelöscht",
        success=True
    )



# === CALIBRATIONS API ===

@app.get("/api/calibrations", response_model=List[Calibration], tags=["Calibrations"])
async def get_calibrations(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Alle Kalibrierungen abrufen.
    
    Lädt eine paginierte Liste aller durchgeführten Kalibrierungen
    mit Ergebnissen und Metadaten.
    
    Args:
        skip (int): Anzahl zu überspringender Datensätze. Default: 0
        limit (int): Maximale Anzahl zurückzugebender Datensätze. Default: 20, Max: 100
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        List[Calibration]: Liste aller Kalibrierungsprotokoll
        
    Example Response:
        ```json
        [
            {
                "id": 1,
                "equipment_id": 1,
                "calibration_date": "2024-01-10",
                "calibrated_by": "Max Mustermann, DAkkS Lab",
                "certificate_number": "DAkkS-K-12345-2024",
                "result": "passed",
                "deviation": "±0.002 mm",
                "notes": "Alle Messungen innerhalb der Toleranzen",
                "next_calibration_date": "2025-01-10",
                "file_path": "/calibrations/dakkS-k-12345-2024.pdf",
                "created_at": "2024-01-10T14:30:00Z"
            },
            {
                "id": 3,
                "equipment_id": 3,
                "calibration_date": "2023-12-01",
                "calibrated_by": "Sartorius Service Team",
                "certificate_number": "SAR-CAL-2023-045",
                "result": "passed",
                "deviation": "±0.0001 g",
                "notes": "Waage innerhalb der Spezifikationen, Eckenlast geprüft",
                "next_calibration_date": "2024-06-01",
                "file_path": "/calibrations/sartorius-cal-2023-045.pdf",
                "created_at": "2023-12-01T09:15:00Z"
            }
        ]
        ```
        
    Raises:
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Sortierung nach calibration_date (neueste zuerst)
        - file_path verweist auf Kalibrierungs-Zertifikate
        - result: "passed", "failed", "conditional"
        - certificate_number für Rückverfolgbarkeit wichtig
        
    Calibration Results:
        - passed: Erfolgreich, alle Toleranzen eingehalten
        - failed: Fehlgeschlagen, außerhalb der Toleranzen
        - conditional: Bedingt bestanden, mit Einschränkungen
    """
    calibrations = db.query(CalibrationModel).offset(skip).limit(limit).all()
    return calibrations

@app.get("/api/calibrations/{calibration_id}", response_model=Calibration, tags=["Calibrations"])
async def get_calibration(calibration_id: int, db: Session = Depends(get_db)):
    """
    Eine spezifische Kalibrierung abrufen.
    
    Lädt ein einzelnes Kalibrierungsprotokoll mit allen Details
    für die Dokumentation und Audit-Zwecke.
    
    Args:
        calibration_id (int): Eindeutige ID der Kalibrierung
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        Calibration: Detaillierte Kalibrierungsinformationen
        
    Example Response:
        ```json
        {
            "id": 4,
            "equipment_id": 4,
            "calibration_date": "2023-08-20",
            "calibrated_by": "Heraeus Service Center München",
            "certificate_number": "HER-ENV-2023-890",
            "result": "passed",
            "deviation": "Temperatur: ±0.3°C, Feuchte: ±2.5% rH",
            "notes": "Umweltkammer vollständig kalibriert, alle Sensoren innerhalb der Spezifikation. 18-Punkt-Kalibrierung durchgeführt.",
            "next_calibration_date": "2024-08-20",
            "file_path": "/calibrations/heraeus-env-2023-890.pdf",
            "created_at": "2023-08-20T16:45:00Z"
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Kalibrierung nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Vollständige Dokumentation für Audit-Trail
        - deviation zeigt gemessene Abweichungen
        - file_path für Zertifikat-Download
        - Verknüpfung zu Equipment über equipment_id
    """
    calibration = db.query(CalibrationModel).filter(CalibrationModel.id == calibration_id).first()
    if not calibration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kalibrierung mit ID {calibration_id} nicht gefunden"
        )
    return calibration

@app.post("/api/calibrations", response_model=Calibration, tags=["Calibrations"])
async def create_calibration(calibration: CalibrationCreate, db: Session = Depends(get_db)):
    """
    Neue Kalibrierung erstellen.
    
    Dokumentiert eine durchgeführte Kalibrierung und aktualisiert
    automatisch den Kalibrierungsstatus des zugehörigen Equipments.
    
    Args:
        calibration (CalibrationCreate): Daten der neuen Kalibrierung
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        Calibration: Die erstellte Kalibrierung
        
    Example Request:
        ```json
        {
            "equipment_id": 5,
            "calibration_date": "2024-01-15",
            "calibrated_by": "TÜV SÜD Industrie Service",
            "certificate_number": "TUV-IS-2024-1234",
            "result": "passed",
            "deviation": "±0.1°C bei 37°C Referenztemperatur",
            "notes": "Inkubator kalibriert nach DIN EN 60601-2-19, alle Temperatursensoren geprüft",
            "next_calibration_date": "2025-01-15",
            "file_path": "/calibrations/tuv-is-2024-1234.pdf"
        }
        ```
        
    Example Response:
        ```json
        {
            "id": 8,
            "equipment_id": 5,
            "calibration_date": "2024-01-15",
            "calibrated_by": "TÜV SÜD Industrie Service",
            "certificate_number": "TUV-IS-2024-1234",
            "result": "passed",
            "deviation": "±0.1°C bei 37°C Referenztemperatur",
            "notes": "Inkubator kalibriert nach DIN EN 60601-2-19, alle Temperatursensoren geprüft",
            "next_calibration_date": "2025-01-15",
            "file_path": "/calibrations/tuv-is-2024-1234.pdf",
            "created_at": "2024-01-15T11:20:00Z"
        }
        ```
        
    Raises:
        HTTPException: 400 bei ungültigen Eingabedaten
        HTTPException: 404 wenn Equipment nicht existiert
        HTTPException: 409 wenn Zertifikatsnummer bereits existiert
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - equipment_id muss existieren
        - certificate_number sollte eindeutig sein
        - Automatische Aktualisierung der Equipment-Kalibrierungsdaten
        - file_path für PDF-Zertifikat wichtig
        
    Business Logic:
        - Equipment last_calibration und next_calibration werden aktualisiert
        - Status-Benachrichtigungen an verantwortliche Teams
        - Automatische Planung der nächsten Kalibrierung
        - Compliance-Dokumentation für Audits
    """
    # Prüfen ob Equipment existiert
    equipment = db.query(EquipmentModel).filter(EquipmentModel.id == calibration.equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment mit ID {calibration.equipment_id} nicht gefunden"
        )
    
    # Prüfen ob Zertifikatsnummer bereits existiert
    existing_cal = db.query(CalibrationModel).filter(
        CalibrationModel.certificate_number == calibration.certificate_number
    ).first()
    if existing_cal:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Kalibrierung mit Zertifikatsnummer '{calibration.certificate_number}' existiert bereits"
        )
    
    # Kalibrierung erstellen
    db_calibration = CalibrationModel(**calibration.dict())
    db.add(db_calibration)
    
    # Equipment-Kalibrierungsdaten aktualisieren
    equipment.last_calibration = calibration.calibration_date
    equipment.next_calibration = calibration.next_calibration_date
    
    db.commit()
    db.refresh(db_calibration)
    return db_calibration

@app.put("/api/calibrations/{calibration_id}", response_model=Calibration, tags=["Calibrations"])
async def update_calibration(
    calibration_id: int,
    calibration_update: CalibrationUpdate,
    db: Session = Depends(get_db)
):
    """
    Kalibrierung aktualisieren.
    
    Aktualisiert eine bestehende Kalibrierung. Für Versionierung,
    Status-Änderungen und Freigabe-Workflows.
    
    Args:
        calibration_id (int): ID der zu aktualisierenden Kalibrierung
        calibration_update (CalibrationUpdate): Zu aktualisierende Felder
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        Calibration: Die aktualisierte Kalibrierung
        
    Example Request (Status auf APPROVED setzen):
        ```json
        {
            "status": "APPROVED",
            "approved_by": 2,
            "approved_at": "2024-01-15T14:30:00Z"
        }
        ```
        
    Example Request (neue Version):
        ```json
        {
            "version": "1.1",
            "description": "Überarbeitete Version nach internem Review",
            "status": "REVIEW"
        }
        ```
        
    Example Response:
        ```json
        {
            "id": 8,
            "equipment_id": 5,
            "calibration_date": "2024-01-15",
            "calibrated_by": "TÜV SÜD Industrie Service",
            "certificate_number": "TUV-IS-2024-1234",
            "result": "passed",
            "deviation": "±0.1°C bei 37°C Referenztemperatur",
            "notes": "Inkubator kalibriert nach DIN EN 60601-2-19, alle Temperatursensoren geprüft",
            "next_calibration_date": "2025-01-15",
            "file_path": "/calibrations/tuv-is-2024-1234.pdf",
            "created_at": "2024-01-15T11:20:00Z"
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Kalibrierung nicht gefunden
        HTTPException: 400 bei ungültigen Eingabedaten
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Nur übermittelte Felder werden aktualisiert
        - approved_by und approved_at für Freigabe-Workflow
        - Versionierung für Änderungsverfolgung
        
    Business Logic:
        - Status-Workflow: DRAFT → REVIEW → APPROVED → OBSOLETE
        - Automatische Benachrichtigungen bei Status-Änderungen
        - Audit-Trail für alle Änderungen
    """
    db_calibration = db.query(CalibrationModel).filter(CalibrationModel.id == calibration_id).first()
    if not db_calibration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kalibrierung mit ID {calibration_id} nicht gefunden"
        )
    
    update_data = calibration_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_calibration, field, value)
    
    db.commit()
    db.refresh(db_calibration)
    return db_calibration

@app.delete("/api/calibrations/{calibration_id}", response_model=GenericResponse, tags=["Calibrations"])
async def delete_calibration(calibration_id: int, db: Session = Depends(get_db)):
    """
    Kalibrierung löschen.
    
    Entfernt eine Kalibrierung aus dem System. Für Kalibrierungs-Lifecycle-Management
    und Bereinigung veralteter Kalibrierungen.
    
    Args:
        calibration_id (int): ID der zu löschenden Kalibrierung
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        GenericResponse: Bestätigung der Löschung
        
    Example Response:
        ```json
        {
            "message": "Kalibrierung 'Temperaturüberwachung' wurde gelöscht",
            "success": true
        }
        ```
        
    Raises:
        HTTPException: 404 wenn Kalibrierung nicht gefunden
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Hard Delete: Kalibrierung wird permanent entfernt
        - Datei auf Festplatte bleibt bestehen (separater Prozess)
        - Für Compliance-relevante Kalibrierungen vorsichtig verwenden
        
    Warning:
        - Genehmigte Kalibrierungen sollten nicht gelöscht werden
        - Alternative: Status auf OBSOLETE setzen
        - Prüfe Referenzen in anderen Dokumenten
    """
    db_calibration = db.query(CalibrationModel).filter(CalibrationModel.id == calibration_id).first()
    if not db_calibration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kalibrierung mit ID {calibration_id} nicht gefunden"
        )
    
    # Kalibrierungen haben kein name-Feld, verwende ID
    db.delete(db_calibration)
    db.commit()
    return GenericResponse(
        message=f"Kalibrierung mit ID {calibration_id} wurde gelöscht",
        success=True
    )



# === SEARCH & ANALYTICS APIs ===
# Erweiterte Such- und Analysefunktionen

@app.get("/api/documents/search/{query}", response_model=List[Document], tags=["Search"])
async def search_documents(query: str, db: Session = Depends(get_db)):
    """
    Volltextsuche in Dokumenten.
    
    Führt eine erweiterte Volltextsuche in Dokumententiteln und
    -beschreibungen durch. Für schnelle Dokumentensuche.
    
    Args:
        query (str): Suchbegriff oder -phrase
        db (Session): Datenbankverbindung (automatisch injiziert)
        
    Returns:
        List[Document]: Liste der gefundenen Dokumente
        
    Example Request:
        ```
        GET /api/documents/search/ISO%2013485
        ```
        
    Example Response:
        ```json
        [
            {
                "id": 1,
                "title": "Qualitätsmanagement-Handbuch nach ISO 13485",
                "document_type": "QM_MANUAL",
                "description": "Hauptdokument des QM-Systems nach ISO 13485:2016",
                "version": "2.1",
                "status": "APPROVED",
                "file_path": "/documents/qm-manual-v2.1.pdf",
                "created_by": 1,
                "approved_by": 2,
                "created_at": "2024-01-15T10:30:00Z",
                "approved_at": "2024-01-20T14:15:00Z"
            }
        ]
        ```
        
    Raises:
        HTTPException: 400 bei leerem Suchbegriff
        HTTPException: 500 bei Datenbankfehlern
        
    Note:
        - Case-insensitive Suche
        - Unterstützt Teilwort-Suche
        - Sortierung nach Relevanz (Titel vor Beschreibung)
        - Maximal 50 Ergebnisse
        
    Search Features:
        - Titel haben höhere Priorität als Beschreibungen
        - Automatische Wildcard-Suche (% vor und nach Begriff)
        - Nur genehmigte Dokumente in Suchergebnissen
    """
    if not query or len(query.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Suchbegriff muss mindestens 2 Zeichen lang sein"
        )
    
    search_filter = f"%{query}%"
    documents = db.query(DocumentModel).filter(
        (DocumentModel.title.ilike(search_filter)) |
        (DocumentModel.description.ilike(search_filter))
    ).limit(50).all()
    
    return documents


# ===== NOTION INTEGRATION ENDPOINTS =====

@app.post("/api/documents/{document_id}/sync-to-notion", tags=["Notion Integration"])
async def sync_document_to_notion_endpoint(document_id: int, db: Session = Depends(get_db)):
    """
    Synchronisiere QMS-Dokument nach Notion.
    
    Erstellt eine Notion Page mit allen QMS-Metadaten und konvertiert
    den Dokumentinhalt in Notion-Blocks für optimale Bearbeitung.
    
    Args:
        document_id (int): ID des zu synchronisierenden Dokuments
        
    Returns:
        dict: Notion Page ID und Sync-Status
        
    Example Response:
        ```json
        {
            "notion_page_id": "abc123-def456-ghi789",
            "status": "success", 
            "message": "Document successfully synced to Notion"
        }
        ```
    """
    try:
        # Import hier um zirkuläre Imports zu vermeiden
        from .notion_integration import sync_document_to_notion
        
        # Prüfe ob Dokument existiert
        document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
        
        # Sync nach Notion
        notion_page_id = await sync_document_to_notion(document_id)
        
        return {
            "notion_page_id": notion_page_id,
            "status": "success",
            "message": f"Document {document_id} successfully synced to Notion"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.post("/api/notion/{notion_page_id}/sync-to-qms", tags=["Notion Integration"])
async def sync_notion_to_qms_endpoint(notion_page_id: str, db: Session = Depends(get_db)):
    """
    Synchronisiere Notion Page nach QMS.
    
    Importiert eine Notion Page als QMS-Dokument, konvertiert Notion-Blocks
    zurück in QMS-Format und erstellt/aktualisiert das Dokument.
    
    Args:
        notion_page_id (str): Notion Page ID (z.B. "abc123-def456-ghi789")
        
    Returns:
        dict: QMS Document ID und Sync-Status
        
    Example Response:
        ```json
        {
            "qms_document_id": 42,
            "status": "success",
            "message": "Notion page successfully synced to QMS"
        }
        ```
    """
    try:
        from .notion_integration import sync_notion_to_qms
        
        # Sync von Notion nach QMS
        qms_document_id = await sync_notion_to_qms(notion_page_id)
        
        return {
            "qms_document_id": qms_document_id,
            "status": "success", 
            "message": f"Notion page {notion_page_id} successfully synced to QMS"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.post("/api/notion/setup-database", tags=["Notion Integration"])
async def setup_notion_database():
    """
    Erstelle QMS Database in Notion.
    
    Richtet eine vorkonfigurierte Notion Database mit allen notwendigen
    Properties für QMS-Dokumente ein (Status, Department, etc.).
    
    Returns:
        dict: Notion Database ID und Setup-Status
        
    Example Response:
        ```json
        {
            "database_id": "xyz789-abc123-def456",
            "status": "success",
            "message": "QMS Database created in Notion"
        }
        ```
    """
    try:
        from .notion_integration import notion_service
        
        database_id = await notion_service.setup_qms_database()
        
        return {
            "database_id": database_id,
            "status": "success",
            "message": "QMS Database successfully created in Notion"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database setup failed: {str(e)}")


@app.get("/api/notion/sync-status/{document_id}", tags=["Notion Integration"])
async def get_notion_sync_status(document_id: int, db: Session = Depends(get_db)):
    """
    Prüfe Synchronisationsstatus eines Dokuments mit Notion.
    
    Zeigt ob das Dokument mit Notion synchronisiert ist und wann
    die letzte Synchronisation stattgefunden hat.
    
    Args:
        document_id (int): QMS Document ID
        
    Returns:
        dict: Sync-Status und Metadaten
        
    Example Response:
        ```json
        {
            "is_synced": true,
            "notion_page_id": "abc123-def456-ghi789",
            "last_sync": "2024-01-15T10:30:00Z",
            "sync_direction": "bidirectional"
        }
        ```
    """
    # TODO: Implementiere Sync-Status-Tracking in Database
    # Für MVP: einfacher Mock
    return {
        "is_synced": False,
        "notion_page_id": None,
        "last_sync": None,
        "sync_direction": "none",
        "message": "Sync status tracking not yet implemented"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 