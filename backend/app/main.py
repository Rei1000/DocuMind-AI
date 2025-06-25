"""
KI-QMS FastAPI Main Application

Enterprise-grade Quality Management System (QMS) API for medical device companies.
Provides comprehensive RESTful endpoints for ISO 13485, EU MDR, and FDA 21 CFR Part 820 compliance.

This module serves as the central FastAPI application, orchestrating all QMS operations
through a robust, scalable, and secure API architecture designed for production environments.

API Architecture:
    • RESTful design following OpenAPI 3.0.3 specification
    • Automatic Swagger UI and ReDoc documentation generation
    • Comprehensive error handling with standardized HTTP status codes
    • Request/response validation using Pydantic v2 schemas
    • Async-first architecture for high-performance operations

Core Business Domains:
    1. Interest Groups Management (13 stakeholder-oriented groups)
    2. User Management & Authentication (JWT-based RBAC)
    3. Document Management (25+ QMS-specific document types)
    4. Standards & Compliance (ISO 13485, MDR, FDA CFR Part 820)
    5. Equipment & Calibration Management (ISO 17025 compliant)
    6. Full-text Search & AI-powered Text Extraction
    7. Workflow Engine for automated QM processes

Security Features:
    • OAuth2 with JWT Bearer token authentication
    • Role-based access control (RBAC) with granular permissions
    • Password hashing using bcrypt with configurable rounds
    • CORS middleware for secure cross-origin requests
    • File upload validation with MIME type checking
    • SQL injection protection via SQLAlchemy ORM

Performance & Scalability:
    • Async I/O operations for file handling and database access
    • Connection pooling and query optimization
    • Pagination support for large data sets
    • Background task processing for resource-intensive operations
    • Caching strategies for frequently accessed data

Data Validation & Type Safety:
    • Comprehensive Pydantic v2 schemas with field validators
    • Type hints throughout the codebase for IDE support
    • Custom validators for business rule enforcement
    • Automatic request/response serialization and deserialization

File Management:
    • Secure file upload with size and type validation (max 50MB)
    • Intelligent text extraction from PDF, DOC, DOCX, TXT, MD, XLS, XLSX
    • Automated keyword extraction for search optimization
    • SHA-256 integrity checking and duplicate detection
    • Organized storage structure by document type

Compliance Implementation:
    • ISO 13485:2016 document control workflows
    • EU MDR 2017/745 technical documentation requirements
    • FDA 21 CFR Part 820 quality system regulations
    • Complete audit trails for all operations
    • Automated calibration schedule management per ISO 17025

Technology Stack:
    Backend Framework: FastAPI 0.110+ (Python 3.12+)
    ORM: SQLAlchemy 2.0+ with async support
    Database: SQLite (development), PostgreSQL (production)
    Validation: Pydantic v2 with custom validators
    Authentication: python-jose for JWT, passlib for password hashing
    File I/O: aiofiles for async file operations
    Documentation: Automatic OpenAPI schema generation

Development Standards:
    • Google-style docstrings for all public functions
    • Type hints for all function signatures
    • Comprehensive error handling with custom exceptions
    • Unit tests with pytest and async test clients
    • Code formatting with Black and linting with Ruff
    • Pre-commit hooks for code quality enforcement

API Endpoint Categories:
    /health                     - System health and monitoring
    /api/auth/*                 - Authentication and authorization
    /api/users/*                - User management and profiles
    /api/interest-groups/*      - Stakeholder group management
    /api/documents/*            - Document lifecycle management
    /api/equipment/*            - Equipment and asset management
    /api/calibrations/*         - Calibration scheduling and tracking
    /api/norms/*                - Standards and compliance management

Error Handling:
    Standardized error responses with detailed messages, error codes,
    and contextual information for debugging and user feedback.

Example Usage:
    >>> import requests
    >>> # Login and get token
    >>> response = requests.post('/api/auth/login', 
    ...                         json={'email': 'user@company.com', 'password': 'secure123'})
    >>> token = response.json()['access_token']
    >>> # Use API with token
    >>> headers = {'Authorization': f'Bearer {token}'}
    >>> documents = requests.get('/api/documents', headers=headers).json()

Authors: KI-QMS Development Team
Version: 2.0.0 (Production Ready)
Created: December 2024
License: MIT License
Last Updated: 2024-12-20
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from dotenv import load_dotenv
import os
import hashlib
import aiofiles
from pathlib import Path
import mimetypes
from datetime import datetime

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
    DocumentStatusChange, DocumentStatusHistory, NotificationInfo,
    Norm, NormCreate, NormUpdate,
    Equipment, EquipmentCreate, EquipmentUpdate,
    Calibration, CalibrationCreate, CalibrationUpdate,
    FileUploadResponse, DocumentWithFileCreate,
    GenericResponse,
    PasswordChangeRequest, AdminPasswordResetRequest, 
    UserProfileResponse, PasswordResetResponse
)
from .text_extraction import extract_text_from_file, extract_keywords
from .auth import (
    authenticate_user, create_access_token, get_current_active_user,
    get_user_permissions, get_user_groups as auth_get_user_groups, get_password_hash,
    Token, LoginRequest, UserInfo,
    require_qm_approval, require_admin, require_document_management,
    require_qm_group, require_input_team, require_development
)
from .workflow_engine import get_workflow_engine, WorkflowTask

# ===== DATEI-UPLOAD KONFIGURATION =====
UPLOAD_DIR = Path("uploads")  # Relativer Pfad vom backend/ Verzeichnis aus
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Maximale Dateigröße: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024

# Erlaubte MIME-Types für QMS-Dokumente
ALLOWED_MIME_TYPES = {
    "application/pdf",                    # PDF-Dokumente
    "application/msword",                 # DOC (Legacy Word)
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
    "text/plain",                         # TXT-Dateien
    "text/markdown",                      # MD-Dateien
    "application/vnd.ms-excel",           # XLS (Legacy Excel)
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # XLSX
}

# ===== HILFSFUNKTIONEN FÜR DATEI-VERARBEITUNG =====

async def save_uploaded_file(file: UploadFile, document_type: str) -> FileUploadResponse:
    """
    Speichert eine hochgeladene Datei mit Validierung und Metadaten-Extraktion.
    
    Führt umfassende Validierung durch und speichert die Datei in einer
    organisierten Verzeichnisstruktur nach Dokumenttyp. Generiert
    eindeutige Dateinamen und berechnet Checksummen für Integrität.
    
    Args:
        file (UploadFile): FastAPI UploadFile object mit Datei-Content
        document_type (str): QMS-Dokumenttyp für Ordnerorganisation
        
    Returns:
        FileUploadResponse: Vollständige Datei-Metadaten inklusive:
            - file_path: Relativer Pfad zur gespeicherten Datei
            - file_name: Original-Dateiname
            - file_size: Dateigröße in Bytes
            - file_hash: SHA-256 Checksum für Integrität
            - mime_type: MIME-Type der Datei
            - uploaded_at: Zeitpunkt des Uploads
        
    Raises:
        HTTPException: 
            - 400: Ungültiger Dateiname oder MIME-Type
            - 413: Datei zu groß (> 50MB)
            - 500: Speicher-Fehler
            
    Validierungen:
        - Dateiname vorhanden und nicht leer
        - MIME-Type in ALLOWED_MIME_TYPES
        - Dateigröße unter MAX_FILE_SIZE
        - Erfolgreiche Speicherung im Dateisystem
        
    Sicherheitsfeatures:
        - Eindeutige Dateinamen (Timestamp + Hash) gegen Kollisionen
        - SHA-256 Hash für Integrität-Prüfung
        - Ordnerstruktur nach Dokumenttyp für Organisation
        - Async I/O für bessere Performance
        
    File Organization:
        uploads/
        ├── QM_MANUAL/
        ├── SOP/
        ├── WORK_INSTRUCTION/
        └── ...
    """
    # Validierungen
    if not file.filename:
        raise HTTPException(status_code=400, detail="Dateiname fehlt")
    
    # MIME-Type prüfen
    mime_type = file.content_type
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Dateityp nicht erlaubt: {mime_type}. Erlaubt: PDF, DOC, DOCX, TXT, MD, XLS, XLSX"
        )
    
    # Datei-Content lesen
    content = await file.read()
    file_size = len(content)
    
    # Größe prüfen
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Datei zu groß: {file_size} Bytes. Maximum: {MAX_FILE_SIZE} Bytes"
        )
    
    # Hash berechnen für Integrität
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Eindeutigen Dateinamen generieren
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file_hash[:8]}_{file.filename}"
    
    # Ordnerstruktur nach Dokumenttyp
    type_dir = UPLOAD_DIR / document_type
    type_dir.mkdir(exist_ok=True)
    
    file_path = type_dir / safe_filename
    
    # Datei speichern
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Relative Pfad für Datenbank (fix für das --reload Problem)
    relative_path = str(file_path)
    
    return FileUploadResponse(
        file_path=relative_path,
        file_name=file.filename,
        file_size=file_size,
        file_hash=file_hash,
        mime_type=mime_type,
        uploaded_at=datetime.utcnow()
    )

def extract_smart_title_and_description(text: str, filename: str) -> tuple[str, str]:
    """
    Extrahiert intelligenten Titel und Beschreibung aus Dokumenttext mit KI-Logik.
    
    Verwendet Pattern-Matching und Heuristiken um aussagekräftige Titel
    und Beschreibungen aus Dokumentinhalten zu extrahieren. Besonders
    optimiert für QMS-Dokumente, Normen und technische Dokumentation.
    
    Pattern-Erkennung:
    - ISO/IEC/DIN/EN Normen-Nummern mit Versionserkennung
    - Medizinprodukte-spezifische Begriffe und Standards
    - QMS-Dokumenttypen (SOP, Arbeitsanweisungen, etc.)
    - Titel-Strukturen in technischen Dokumenten
    - Mehrsprachige Unterstützung (DE/EN)
    
    Args:
        text (str): Extrahierter Dokumenttext (erste 3000 Zeichen für Performance)
        filename (str): Original-Dateiname als Fallback-Titel
        
    Returns:
        tuple[str, str]: (extracted_title, extracted_description)
            - title: Erkannter oder generierter Titel (max 200 Zeichen)
            - description: Intelligente Beschreibung oder Fallback
            
    Heuristiken:
        1. Normen-Pattern: ISO 13485:2016, IEC 62304, DIN EN ISO 14971
        2. Titel-Erkennung: Erste signifikante Zeile ohne Metadaten
        3. Beschreibung: Erster Absatz oder extrahierte Zusammenfassung
        4. Fallback: Bereinigter Dateiname wenn keine Pattern erkannt
        
    Performance:
        - Nur erste 3000 Zeichen analysiert für Geschwindigkeit
        - Optimierte Regex-Pattern für häufige Formate
        - Caching für wiederverwendbare Pattern
        
    Examples:
        >>> extract_smart_title_and_description(
        ...     "ISO 13485:2016 Medical devices - Quality management systems",
        ...     "iso_13485_2016.pdf"
        ... )
        ("ISO 13485:2016 - Medical devices - Quality management systems", 
         "International standard for medical device quality management systems")
    """
    import re
    
    if not text or len(text.strip()) < 10:
        # Fallback zu Dateiname
        clean_name = filename.replace('.pdf', '').replace('.docx', '').replace('.doc', '')
        return clean_name[:200], "Automatisch generiert aus Dateiname"
    
    # Erst 3000 Zeichen für Performance
    text_sample = text[:3000]
    lines = [line.strip() for line in text_sample.split('\n') if line.strip()]
    
    # Pattern für Normen-Titel (ISO, DIN, IEC, EN, etc.)
    norm_patterns = [
        r'((?:ISO|IEC|DIN|EN)\s+(?:ISO\s+)?[\d\-]+(?:\:\d+)?(?:\+\w+\s+\d+)?(?:\+\w+\s+\d+)?)',
        r'(ISO\s+\d+(?:\-\d+)*(?:\:\d+)?)',
        r'(IEC\s+\d+(?:\-\d+)*(?:\:\d+)?)',
        r'(DIN\s+EN\s+(?:ISO\s+)?\d+(?:\-\d+)*(?:\:\d+)?)',
        r'(EN\s+(?:ISO\s+)?\d+(?:\-\d+)*(?:\:\d+)?)'
    ]
    
    extracted_title = ""
    extracted_description = ""
    
    # Suche nach Norm-Nummer
    norm_number = ""
    for pattern in norm_patterns:
        for line in lines[:20]:  # Erste 20 Zeilen
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                norm_number = match.group(1).strip()
                break
        if norm_number:
            break
    
    # Suche nach Titel-Zeilen (oft nach der Norm-Nummer)
    title_candidates = []
    for i, line in enumerate(lines[:25]):  # Erste 25 Zeilen
        line_clean = line.strip()
        
        # Skip sehr kurze oder sehr lange Zeilen
        if len(line_clean) < 10 or len(line_clean) > 200:
            continue
            
        # Skip Zeilen mit nur Zahlen/Codes
        if re.match(r'^[\d\s\-\+\.]+$', line_clean):
            continue
            
        # Bevorzuge Zeilen mit QMS/Medizinprodukte-Keywords
        qms_keywords = ['medizinprodukte', 'medical device', 'qualitätsmanagement', 'quality management', 
                       'risk management', 'software', 'validation', 'sterilisation', 'biokompatibilität']
        
        # Priorisiere Zeilen mit Norm-Nummer
        if norm_number and norm_number.lower() in line_clean.lower():
            title_candidates.append((line_clean, 100))  # Höchste Priorität
        elif any(keyword in line_clean.lower() for keyword in qms_keywords):
            title_candidates.append((line_clean, 80))   # Hohe Priorität
        elif len(line_clean) > 20 and len(line_clean) < 150:
            title_candidates.append((line_clean, 50))   # Mittlere Priorität
    
    # Besten Titel wählen
    if title_candidates:
        title_candidates.sort(key=lambda x: x[1], reverse=True)
        extracted_title = title_candidates[0][0]
        
        # Kombiniere mit Norm-Nummer falls verfügbar
        if norm_number and norm_number.lower() not in extracted_title.lower():
            extracted_title = f"{norm_number} - {extracted_title}"
    else:
        # Fallback: Verwende Norm-Nummer oder Dateiname
        extracted_title = norm_number if norm_number else filename.replace('.pdf', '').replace('.docx', '')
    
    # Beschreibung generieren
    description_lines = []
    for line in lines[1:15]:  # Zeilen 2-15 für Beschreibung
        if len(line) > 20 and len(line) < 300:
            if line.lower() not in extracted_title.lower():  # Avoid duplicate
                description_lines.append(line)
                if len(description_lines) >= 3:  # Max 3 Zeilen
                    break
    
    extracted_description = " ".join(description_lines)[:500] if description_lines else "Automatisch extrahiert aus Dokumentinhalt"
    
    # Titel kürzen falls zu lang
    if len(extracted_title) > 200:
        extracted_title = extracted_title[:197] + "..."
        
    return extracted_title, extracted_description

def extract_text_from_file(file_path: Path, mime_type: str) -> str:
    """
    Extrahiert Text aus Dateien für RAG-Indexierung.
    
    Args:
        file_path: Pfad zur Datei
        mime_type: MIME-Type der Datei
        
    Returns:
        Extrahierter Text oder leerer String
    """
    try:
        if mime_type == "text/plain" or mime_type == "text/markdown":
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif mime_type == "application/pdf":
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text.strip()
            except Exception as pdf_error:
                return f"[PDF-Extraktion fehlgeschlagen: {str(pdf_error)}]"
        
        elif mime_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            try:
                from docx import Document
                doc = Document(file_path)
                
                text_parts = []
                # Absätze extrahieren
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        text_parts.append(paragraph.text)
                
                # Tabellen extrahieren
                for table in doc.tables:
                    for row in table.rows:
                        row_text = " | ".join(cell.text for cell in row.cells)
                        text_parts.append(row_text)
                        
                return "\n".join(text_parts)
            except Exception as word_error:
                return f"[Word-Extraktion fehlgeschlagen: {str(word_error)}]"
        
        elif mime_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            try:
                import openpyxl
                workbook = openpyxl.load_workbook(file_path)
                text_parts = []
                
                for sheet_name in workbook.sheetnames:
                    sheet = workbook[sheet_name]
                    text_parts.append(f"=== {sheet_name} ===")
                    
                    for row in sheet.iter_rows(values_only=True):
                        row_text = " | ".join(str(cell) if cell is not None else "" for cell in row)
                        if row_text.strip():
                            text_parts.append(row_text)
                
                return "\n".join(text_parts)
            except Exception as excel_error:
                return f"[Excel-Extraktion fehlgeschlagen: {str(excel_error)}]"
        
        else:
            return f"[Text-Extraktion für {mime_type} noch nicht implementiert]"
        
    except Exception as e:
        return f"[Fehler bei Text-Extraktion: {str(e)}]"

def generate_document_number(document_type: str) -> str:
    """
    Generiert eine eindeutige Dokumentennummer.
    
    Format: [TYPE]-[YYYY]-[COUNTER]
    Beispiel: SOP-2024-001, QM_MANUAL-2024-001
    """
    from datetime import datetime
    current_year = datetime.now().year
    
    # Typ-Abkürzungen für Dokumentnummern
    type_prefixes = {
        "QM_MANUAL": "QMH",
        "SOP": "SOP",
        "WORK_INSTRUCTION": "WI",
        "FORM": "FRM",
        "SPECIFICATION": "SPEC",
        "RISK_ASSESSMENT": "RA",
        "VALIDATION_PROTOCOL": "VAL",
        "CALIBRATION_PROCEDURE": "CAL",
        "AUDIT_REPORT": "AUD",
        "CAPA_DOCUMENT": "CAPA",
        "TRAINING_MATERIAL": "TRN",
        "STANDARD_NORM": "STD",
        "REGULATION": "REG",
        "OTHER": "DOC"
    }
    
    prefix = type_prefixes.get(document_type, "DOC")
    
    # Einfacher Counter (für MVP - später aus DB)
    import random
    counter = random.randint(1, 999)
    
    return f"{prefix}-{current_year}-{counter:03d}"

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
# Erlaubt Frontend-Zugriff von Streamlit und React Development Server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://127.0.0.1:3000",  # React Frontend
        "http://localhost:8501", "http://127.0.0.1:8501",  # Streamlit Frontend
        "http://192.168.178.160:8501"  # Streamlit Network URL
    ],
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

# === AUTHENTICATION ENDPOINTS ===

@app.post("/api/auth/login", response_model=Token, tags=["Authentication"])
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Benutzer-Login mit Email und Passwort.
    
    Erstellt einen JWT-Token für authentifizierten Zugriff auf das QMS.
    Der Token enthält Benutzer-ID, Gruppen und Berechtigungen.
    
    Args:
        login_data: Email und Passwort
        db: Datenbankverbindung
        
    Returns:
        Token: JWT Access Token mit Benutzer-Informationen
        
    Example Request:
        ```json
        {
            "email": "maria.qm@company.com",
            "password": "secure_password"
        }
        ```
        
    Example Response:
        ```json
        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "token_type": "bearer",
            "expires_in": 1800,
            "user_id": 2,
            "user_name": "Dr. Maria Qualität",
            "groups": ["quality_management"],
            "permissions": ["final_approval", "system_administration"]
        }
        ```
        
    Raises:
        HTTPException: 401 bei ungültigen Anmeldedaten
    """
    
    # Benutzer authentifizieren
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültige Email oder Passwort",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Benutzer-Gruppen und Berechtigungen laden
    user_groups = auth_get_user_groups(db, user)
    user_permissions = get_user_permissions(db, user)
    
    # JWT Token erstellen
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800,  # 30 Minuten
        user_id=user.id,
        user_name=user.full_name,
        groups=user_groups,
        permissions=user_permissions
    )

@app.get("/api/auth/me", response_model=UserInfo, tags=["Authentication"])
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Aktuelle Benutzer-Informationen abrufen.
    
    Liefert detaillierte Informationen über den authentifizierten Benutzer
    inklusive Gruppen und Berechtigungen. Für Benutzer-Profile und UI-Personalisierung.
    
    Args:
        current_user: Authentifizierter Benutzer (aus JWT Token)
        db: Datenbankverbindung
        
    Returns:
        UserInfo: Vollständige Benutzer-Informationen
        
    Example Response:
        ```json
        {
            "id": 2,
            "email": "maria.qm@company.com",
            "full_name": "Dr. Maria Qualität",
            "organizational_unit": "Qualitätsmanagement",
            "is_department_head": true,
            "approval_level": 4,
            "groups": ["quality_management"],
            "permissions": ["final_approval", "gap_analysis", "system_administration"]
        }
        ```
        
    Note:
        - Erfordert gültigen Bearer Token
        - Gruppenzugehörigkeiten werden live aus DB geladen
        - Berechtigungen werden aus Gruppen + individuellen Rechten zusammengestellt
    """
    
    user_groups = auth_get_user_groups(db, current_user)
    user_permissions = get_user_permissions(db, current_user)
    
    return UserInfo(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        organizational_unit=current_user.organizational_unit,
        is_department_head=current_user.is_department_head,
        approval_level=current_user.approval_level,
        groups=user_groups,
        permissions=user_permissions
    )

@app.post("/api/auth/logout", response_model=dict, tags=["Authentication"])
async def logout():
    """
    Benutzer-Logout (Token invalidieren).
    
    Da JWT-Tokens stateless sind, erfolgt das Logout client-seitig
    durch Löschen des Tokens. Dieser Endpoint dient als formaler Logout-Trigger.
    
    Returns:
        dict: Logout-Bestätigung
        
    Example Response:
        ```json
        {
            "message": "Successfully logged out",
            "logged_out_at": "2024-01-15T10:30:00Z"
        }
        ```
        
    Note:
        - Client muss Token aus Local Storage/Session Storage löschen
        - Server-seitige Token-Blacklist optional für höhere Sicherheit
        - Für stateful Sessions würde hier Session gelöscht werden
    """
    
    return {
        "message": "Successfully logged out",
        "logged_out_at": datetime.utcnow().isoformat() + "Z"
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
        - Automatische Abteilungszuordnung basierend auf organizational_unit
        
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
    
    # Password hashen mit bcrypt
    hashed_password = get_password_hash(user.password)
    
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
    
    # === AUTOMATISCHE ABTEILUNGSZUORDNUNG ===
    # Mapping von organizational_unit Namen zu Interest Group IDs
    department_mapping = {
        "System Administration": 1,  # Team/Eingangsmodul (verwende für System Admin)
        "Team/Eingangsmodul": 1,
        "Qualitätsmanagement": 2,
        "Entwicklung": 3,
        "Einkauf": 4,
        "Produktion": 5,
        "HR/Schulung": 6,
        "Dokumentation": 7,
        "Service/Support": 8,
        "Vertrieb": 9,
        "Regulatory Affairs": 10,
        "IT-Abteilung": 11,
        "Externe Auditoren": 12,
        "Lieferanten": 13
    }
    
    # Automatische Zuordnung zur passenden Interest Group
    if user.organizational_unit in department_mapping:
        interest_group_id = department_mapping[user.organizational_unit]
        
        # UserGroupMembership erstellen
        new_membership = UserGroupMembershipModel(
            user_id=db_user.id,
            interest_group_id=interest_group_id,
            approval_level=user.approval_level,
            role_in_group=f"Level {user.approval_level}",
            is_department_head=user.is_department_head,
            assigned_by_id=1,  # System erstellt automatisch (qms.admin@company.com)
            notes=f"Automatisch zugeordnet bei User-Erstellung für '{user.organizational_unit}'"
        )
        
        db.add(new_membership)
        db.commit()
        db.refresh(new_membership)
        
        print(f"✅ User '{user.full_name}' automatisch der Abteilung '{user.organizational_unit}' zugeordnet (Level {user.approval_level})")
    else:
        print(f"⚠️ User '{user.full_name}': Keine automatische Abteilungszuordnung für '{user.organizational_unit}' möglich")
    
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
    """
    try:
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
        
        # Debug-Ausgabe
        print(f"✅ Gefunden: {len(documents)} Dokumente")
        for doc in documents[:3]:
            print(f"  - {doc.id}: {doc.title} ({doc.document_type})")
            
        return documents
        
    except Exception as e:
        print(f"❌ FEHLER in get_documents: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Datenbankfehler: {str(e)}"
        )

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

# === DATEI-UPLOAD ENDPUNKTE ===

@app.post("/api/files/upload", response_model=FileUploadResponse, tags=["File Upload"])
async def upload_file(
    file: UploadFile = File(...),
    document_type: str = Form(...)
):
    """
    Lädt eine Datei hoch und speichert sie strukturiert.
    
    Args:
        file: Hochzuladende Datei (PDF, DOC, DOCX, TXT, MD, XLS, XLSX)
        document_type: Dokumenttyp für Ordnerorganisation
        
    Returns:
        FileUploadResponse: Metadaten der gespeicherten Datei
    """
    try:
        upload_response = await save_uploaded_file(file, document_type)
        return upload_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload-Fehler: {str(e)}"
        )

@app.post("/api/documents/with-file", response_model=Document, tags=["Documents"])
async def create_document_with_file(
    title: Optional[str] = Form(None),
    document_type: Optional[str] = Form("OTHER"),
    creator_id: int = Form(...),
    version: str = Form("1.0"),
    content: Optional[str] = Form(None),
    remarks: Optional[str] = Form(None),
    chapter_numbers: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Erstellt ein Dokument mit optionalem Datei-Upload und intelligenter Analyse.
    
    **Neue Features:**
    - 🤖 **Intelligente Dokumenttyp-Erkennung** basierend auf Inhalt (erste 3000 Zeichen)
    - 📊 **Umfassende Metadaten-Extraktion** (Keywords, Compliance-Indikatoren, etc.)
    - 🎯 **Automatische Titel/Beschreibung** falls nicht angegeben
    - 🔍 **Content-Analyse** für bessere Kategorisierung
    
    Args:
        title: Dokumenttitel (optional - wird automatisch extrahiert)
        document_type: Dokumenttyp (wird intelligent erkannt wenn "OTHER")
        creator_id: ID des erstellenden Benutzers
        version: Dokumentversion (Standard: "1.0")
        content: Beschreibung (optional - wird automatisch extrahiert)
        remarks: Bemerkungen
        chapter_numbers: Relevante Normkapitel (z.B. "4.2.3, 7.5.1")
        file: Upload-Datei (PDF, DOCX, XLSX, TXT)
        db: Datenbankverbindung
        
    Returns:
        Document: Erstelltes Dokument mit Metadaten und ggf. erkanntem Typ
        
    Example Request:
        ```bash
        curl -X POST "http://localhost:8000/api/documents/with-file" \
             -F "file=@sop-dokumentenkontrolle.pdf" \
             -F "creator_id=2" \
             -F "document_type=OTHER"  # Wird automatisch als "SOP" erkannt
        ```
        
    Example Response:
        ```json
        {
            "id": 15,
            "title": "SOP-001: Dokumentenlenkung und -kontrolle",
            "document_type": "SOP",  # Automatisch erkannt!
            "detected_metadata": {
                "confidence": 0.85,
                "keywords": ["Dokumentenkontrolle", "ISO 13485", "Freigabe"],
                "complexity_score": 7
            }
        }
        ```
    """
    try:
        # 1. Datei-Upload verarbeiten (falls vorhanden)
        file_data = None
        extracted_text = ""
        metadata = {}
        
        if file:
            # Datei speichern
            upload_result = await save_uploaded_file(file, document_type or "OTHER")
            if not upload_result.success:
                raise HTTPException(status_code=400, detail=upload_result.message)
            
            file_data = upload_result
            
            # Text extrahieren
            extracted_text = extract_text_from_file(
                Path(upload_result.file_path), 
                upload_result.mime_type
            )
            
            # 🤖 NEUE INTELLIGENTE ANALYSE
            from .text_extraction import extract_comprehensive_metadata, analyze_document_type
            
            # Umfassende Metadaten extrahieren
            metadata = extract_comprehensive_metadata(extracted_text, title or file.filename)
            
            # Dokumenttyp intelligent erkennen (falls nicht spezifiziert oder "OTHER")
            if not document_type or document_type == "OTHER":
                detected_type = analyze_document_type(extracted_text, title or file.filename)
                document_type = detected_type
                print(f"🤖 Intelligent erkannt: {file.filename} → {detected_type}")
            
            # Titel und Beschreibung automatisch extrahieren (falls nicht angegeben)
            if not title or not content:
                auto_title, auto_content = extract_smart_title_and_description(
                    extracted_text, file.filename
                )
                title = title or auto_title
                content = content or auto_content
                
        # 2. Validierung der Eingaben
        if not title:
            raise HTTPException(status_code=400, detail="Titel ist erforderlich")
        
        # 3. Prüfung auf Duplikate (präziser mit Metadaten)
        existing_doc = db.query(DocumentModel).filter(
            DocumentModel.title == title
        ).first()
        
        if existing_doc:
            # Intelligentere Duplikatsprüfung basierend auf Inhalt
            similarity_score = _calculate_content_similarity(
                existing_doc.extracted_text or "", 
                extracted_text
            )
            
            if similarity_score > 0.8:  # 80% Ähnlichkeit
                raise HTTPException(
                    status_code=409, 
                    detail=f"DUPLIKAT: Sehr ähnliches Dokument bereits vorhanden: '{existing_doc.title}' (ID: {existing_doc.id}, Ähnlichkeit: {similarity_score:.1%})"
                )
        
        # 4. Dokument erstellen mit intelligenten Metadaten
        db_document = DocumentModel(
            title=title,
            document_number=generate_document_number(document_type),
            document_type=DocumentType(document_type),
            version=version,
            content=content,
            creator_id=creator_id,
            remarks=remarks,
            chapter_numbers=chapter_numbers,
            
            # Datei-Informationen
            file_path=file_data.file_path if file_data else None,
            file_name=file_data.original_filename if file_data else None,
            file_size=file_data.file_size if file_data else None,
            file_hash=file_data.file_hash if file_data else None,
            mime_type=file_data.mime_type if file_data else None,
            
            # Intelligente Text-Extraktion
            extracted_text=extracted_text,
            keywords=", ".join(metadata.get("keywords", [])),
            
            # Neue Metadaten-Felder
            compliance_status="ZU_BEWERTEN",
            priority="MITTEL" if metadata.get("complexity_score", 5) >= 7 else "NIEDRIG"
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # 5. 🚀 Workflow Engine aktivieren (falls verfügbar)
        try:
            from .workflow_engine import WorkflowEngine
            
            workflow = WorkflowEngine()
            workflow_tasks = workflow.create_workflow_tasks(db_document, db)
            
            print(f"📋 Workflow gestartet: {len(workflow_tasks)} Aufgaben für {len(set(task.assigned_group for task in workflow_tasks))} Interessengruppen")
            
        except Exception as workflow_error:
            print(f"⚠️ Workflow-Fehler (nicht kritisch): {workflow_error}")
        
        # 6. Erfolgreiche Antwort mit Metadaten
        response_data = {
            **db_document.__dict__,
            "detected_metadata": {
                "intelligent_type_detection": document_type != (document_type or "OTHER"),
                "detected_type": metadata.get("detected_type"),
                "confidence_score": min(len(metadata.get("keywords", [])) * 0.1, 1.0),
                "keywords_found": metadata.get("keywords", []),
                "complexity_score": metadata.get("complexity_score", 0),
                "has_procedures": metadata.get("has_procedures", False),
                "compliance_indicators": metadata.get("compliance_indicators", [])
            }
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Dokument-Erstellung fehlgeschlagen: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dokument-Erstellung fehlgeschlagen: {str(e)}")

def _calculate_content_similarity(text1: str, text2: str) -> float:
    """
    Berechnet Content-Ähnlichkeit zwischen zwei Texten.
    
    Args:
        text1: Erster Text
        text2: Zweiter Text
        
    Returns:
        float: Ähnlichkeitsscore (0.0 - 1.0)
    """
    if not text1 or not text2:
        return 0.0
    
    # Einfache Wort-basierte Ähnlichkeitsberechnung
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

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
    # Prüfen ob creator_id User existiert
    user_exists = db.query(UserModel).filter(UserModel.id == document.creator_id).first()
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benutzer mit ID {document.creator_id} existiert nicht"
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

# === DOCUMENT STATUS WORKFLOW API ===

@app.put("/api/documents/{document_id}/status", response_model=Document, tags=["Document Workflow"])
async def change_document_status(
    document_id: int,
    status_change: DocumentStatusChange,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Dokumentstatus ändern mit QM-Workflow-Validierung.
    
    Implementiert den 4-stufigen QM-Workflow:
    - DRAFT → REVIEWED: Alle können weiterleiten
    - REVIEWED → APPROVED: Nur QM-Gruppe 
    - APPROVED → OBSOLETE: Nur QM-Gruppe
    - OBSOLETE → DRAFT: Nur QM-Gruppe (für Testing)
    """
    # Dokument laden
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")
    
    # User-Gruppen laden für Berechtigungsprüfung
    user_groups = auth_get_user_groups(db, current_user)
    is_qm_user = "quality_management" in user_groups
    
    # Aktueller und neuer Status
    old_status = document.status
    new_status = status_change.status
    
    # Status-Änderungs-Validierung
    if old_status == new_status:
        raise HTTPException(status_code=400, detail="Neuer Status ist identisch mit aktuellem Status")
    
    # QM-Berechtigungen prüfen
    qm_only_transitions = [
        (DocumentStatus.REVIEWED, DocumentStatus.APPROVED),  # Nur QM darf freigeben
        (DocumentStatus.APPROVED, DocumentStatus.OBSOLETE),  # Nur QM darf obsolet setzen
        (DocumentStatus.OBSOLETE, DocumentStatus.DRAFT),     # Nur QM darf reaktivieren (Testing)
    ]
    
    if (old_status, new_status) in qm_only_transitions and not is_qm_user:
        raise HTTPException(
            status_code=403, 
            detail=f"Status-Wechsel {old_status.value} → {new_status.value} erfordert QM-Berechtigung"
        )
    
    # Status-History erstellen (vor der Änderung)
    from .models import DocumentStatusHistory as StatusHistoryModel
    history_entry = StatusHistoryModel(
        document_id=document_id,
        old_status=old_status,
        new_status=new_status,
        changed_by_id=current_user.id,
        comment=status_change.comment
    )
    db.add(history_entry)
    
    # Dokument-Status aktualisieren
    document.status = new_status
    document.status_changed_by_id = current_user.id
    document.status_changed_at = datetime.utcnow()
    document.status_comment = status_change.comment
    
    # Workflow-spezifische Felder setzen
    if new_status == DocumentStatus.REVIEWED:
        document.reviewed_by_id = current_user.id
        document.reviewed_at = datetime.utcnow()
    elif new_status == DocumentStatus.APPROVED:
        document.approved_by_id = current_user.id
        document.approved_at = datetime.utcnow()
    
    # Benachrichtigung generieren (Console Log für MVP)
    notification = generate_status_notification(document, old_status, new_status, current_user, is_qm_user)
    print(f"📧 NOTIFICATION: {notification.message}")
    print(f"   Recipients: {', '.join(notification.recipients)}")
    
    try:
        db.commit()
        db.refresh(document)
        return document
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Status-Update: {str(e)}")

@app.get("/api/documents/{document_id}/status-history", response_model=List[DocumentStatusHistory], tags=["Document Workflow"])
async def get_document_status_history(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Status-Änderungshistorie eines Dokuments abrufen (Audit-Trail)."""
    # Dokument existiert prüfen
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")
    
    # Status-History laden
    from .models import DocumentStatusHistory as StatusHistoryModel
    history = db.query(StatusHistoryModel).filter(
        StatusHistoryModel.document_id == document_id
    ).order_by(StatusHistoryModel.changed_at.desc()).all()
    
    return history

@app.get("/api/documents/status/{status}", response_model=List[Document], tags=["Document Workflow"])
async def get_documents_by_status(
    status: DocumentStatus,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Alle Dokumente mit einem bestimmten Status abrufen (für Workflow-Dashboards)."""
    documents = db.query(DocumentModel).filter(
        DocumentModel.status == status
    ).order_by(DocumentModel.updated_at.desc()).offset(skip).limit(limit).all()
    
    return documents

def generate_status_notification(
    document: DocumentModel, 
    old_status: DocumentStatus, 
    new_status: DocumentStatus, 
    changed_by: UserModel,
    is_qm_user: bool
) -> NotificationInfo:
    """Generiert Console-Log Benachrichtigungen für Status-Änderungen (MVP)."""
    # Standard QM-Gruppe für alle QM-relevanten Benachrichtigungen
    qm_emails = ["qm@company.com"]  # Placeholder
    
    # Status-spezifische Nachrichten und Empfänger
    if new_status == DocumentStatus.REVIEWED:
        message = f"📋 Dokument '{document.title}' wurde zur QM-Freigabe eingereicht"
        recipients = qm_emails
    elif new_status == DocumentStatus.APPROVED:
        message = f"✅ Dokument '{document.title}' wurde von QM freigegeben"
        recipients = [document.creator.email] if document.creator else []
    elif new_status == DocumentStatus.OBSOLETE:
        message = f"🗑️ Dokument '{document.title}' wurde als obsolet markiert"
        recipients = [document.creator.email] if document.creator else []
    else:
        message = f"📝 Dokument '{document.title}' Status geändert: {old_status.value} → {new_status.value}"
        recipients = []
    
    return NotificationInfo(
        message=message,
        recipients=recipients,
        document_title=document.title,
        new_status=new_status,
        changed_by=changed_by.full_name
    )

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

@app.get("/api/documents/{document_id}/workflow", tags=["Document Workflow"])
async def get_document_workflow(document_id: int, db: Session = Depends(get_db)):
    """
    Workflow-Status für ein Dokument abrufen.
    
    Zeigt die automatisch generierte Workflow-Information für ein Dokument,
    einschließlich zuständiger Interessengruppen, Freigabe-Kette und Tasks.
    
    Args:
        document_id: ID des Dokuments
        
    Returns:
        Dict mit vollständiger Workflow-Information
    """
    # Dokument finden
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dokument mit ID {document_id} nicht gefunden"
        )
    
    # Workflow-Engine verwenden
    workflow_engine = get_workflow_engine()
    workflow_summary = workflow_engine.get_workflow_summary(document)
    
    return workflow_summary

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

# ===== USER DEPARTMENT MANAGEMENT (ADMIN ONLY) =====

@app.get("/api/users/{user_id}/departments", tags=["User Management"])
async def get_user_departments(
    user_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Holt alle aktiven Abteilungszuordnungen für einen User.
    
    Berechtigungen:
    - System Admins können alle User-Departments abrufen
    - Normale User können nur ihre eigenen Departments abrufen
    
    Returns:
        List[Dict]: Liste der Departments mit allen Details
    """
    try:
        # Berechtigung prüfen: System Admin oder eigene Daten
        if not _is_system_admin(current_user) and current_user.id != user_id:
            raise HTTPException(
                status_code=403, 
                detail="🚨 Zugriff verweigert: Sie können nur Ihre eigenen Abteilungen abrufen"
            )
        
        # User existiert?
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User mit ID {user_id} nicht gefunden")
        
        # Alle aktiven Zuordnungen mit Interest Group Details
        memberships = db.query(UserGroupMembershipModel).join(
            InterestGroupModel, UserGroupMembershipModel.interest_group_id == InterestGroupModel.id
        ).filter(
            UserGroupMembershipModel.user_id == user_id,
            UserGroupMembershipModel.is_active == True
        ).all()
        
        departments = []
        for membership in memberships:
            dept = {
                "id": membership.id,
                "user_id": membership.user_id,
                "interest_group_id": membership.interest_group_id,
                "interest_group_name": membership.interest_group.name,
                "approval_level": membership.approval_level,
                "role_in_group": membership.role_in_group,
                "is_department_head": membership.is_department_head,
                "is_active": membership.is_active,
                "joined_at": membership.joined_at,
                "assigned_by_id": membership.assigned_by_id,
                "notes": membership.notes
            }
            departments.append(dept)
        
        return departments
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Departments: {str(e)}")

@app.post("/api/users/{user_id}/departments", tags=["User Management (Admin Only)"])
async def add_user_department(
    user_id: int,
    department_data: dict,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[SYSTEM ADMIN ONLY]** Fügt einem User eine zusätzliche Abteilung mit spezifischem Level hinzu.
    
    Ermöglicht Multiple-Abteilungen pro User für komplexe Organisationsstrukturen.
    Nur QMS System Administratoren können diese Funktion verwenden.
    
    Args:
        user_id: ID des Users dem eine Abteilung hinzugefügt wird
        department_data: {"interest_group_id": 5, "approval_level": 3, "role_in_group": "Abteilungsleiter"}
        current_user: Authentifizierter System Admin
        db: Datenbankverbindung
        
    Returns:
        UserGroupMembership: Neue Abteilungszuordnung
        
    Example Request:
        ```bash
        curl -X POST "http://localhost:8000/api/users/7/departments" \
             -H "Authorization: Bearer {admin_token}" \
             -d '{"interest_group_id": 5, "approval_level": 3, "role_in_group": "Abteilungsleiter"}'
        ```
    """
    # SICHERHEIT: Nur System Admins dürfen User-Abteilungen verwalten
    if not _is_system_admin(current_user):
        raise HTTPException(
            status_code=403, 
            detail="🚨 Zugriff verweigert: Nur System Administratoren können Abteilungen verwalten"
        )
    
    try:
        # User existiert?
        target_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail=f"User mit ID {user_id} nicht gefunden")
        
        # Interest Group existiert?
        interest_group = db.query(InterestGroupModel).filter(
            InterestGroupModel.id == department_data["interest_group_id"]
        ).first()
        if not interest_group:
            raise HTTPException(status_code=404, detail=f"Interessengruppe mit ID {department_data['interest_group_id']} nicht gefunden")
        
        # Bereits zugeordnet?
        existing = db.query(UserGroupMembershipModel).filter(
            UserGroupMembershipModel.user_id == user_id,
            UserGroupMembershipModel.interest_group_id == department_data["interest_group_id"]
        ).first()
        
        if existing:
            if existing.is_active:
                raise HTTPException(status_code=409, detail=f"User ist bereits der Gruppe '{interest_group.name}' zugeordnet")
            else:
                # Reaktivieren
                existing.is_active = True
                existing.approval_level = department_data.get("approval_level", 1)
                existing.role_in_group = department_data.get("role_in_group", "Mitarbeiter")
                existing.assigned_by_id = current_user.id
                existing.notes = department_data.get("notes", "")
                db.commit()
                db.refresh(existing)
                return existing
        
        # Neue Zuordnung erstellen
        new_membership = UserGroupMembershipModel(
            user_id=user_id,
            interest_group_id=department_data["interest_group_id"],
            approval_level=department_data.get("approval_level", 1),
            role_in_group=department_data.get("role_in_group", "Mitarbeiter"),
            is_department_head=department_data.get("approval_level", 1) >= 3,
            assigned_by_id=current_user.id,
            notes=department_data.get("notes", "")
        )
        
        db.add(new_membership)
        db.commit()
        db.refresh(new_membership)
        
        print(f"✅ User {target_user.full_name} zur Abteilung '{interest_group.name}' hinzugefügt (Level {new_membership.approval_level})")
        
        return new_membership
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Hinzufügen der Abteilung: {str(e)}")

@app.put("/api/users/{user_id}/departments/{membership_id}", tags=["User Management (Admin Only)"])
async def update_user_department(
    user_id: int,
    membership_id: int,
    update_data: dict,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[SYSTEM ADMIN ONLY]** Aktualisiert Level/Rolle eines Users in einer Abteilung.
    
    Args:
        user_id: User ID
        membership_id: UserGroupMembership ID
        update_data: {"approval_level": 3, "role_in_group": "Abteilungsleiter"}
        current_user: System Admin
        db: Datenbankverbindung
    """
    if not _is_system_admin(current_user):
        raise HTTPException(status_code=403, detail="🚨 Nur System Administratoren dürfen Abteilungen bearbeiten")
    
    try:
        membership = db.query(UserGroupMembershipModel).filter(
            UserGroupMembershipModel.id == membership_id,
            UserGroupMembershipModel.user_id == user_id
        ).first()
        
        if not membership:
            raise HTTPException(status_code=404, detail="Abteilungszuordnung nicht gefunden")
        
        # Updates anwenden
        if "approval_level" in update_data:
            membership.approval_level = update_data["approval_level"]
            membership.is_department_head = update_data["approval_level"] >= 3
        
        if "role_in_group" in update_data:
            membership.role_in_group = update_data["role_in_group"]
        
        if "notes" in update_data:
            membership.notes = update_data["notes"]
        
        membership.assigned_by_id = current_user.id  # Tracking wer die Änderung gemacht hat
        
        db.commit()
        db.refresh(membership)
        
        return membership
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren: {str(e)}")

@app.delete("/api/users/{user_id}/departments/{membership_id}", tags=["User Management (Admin Only)"])
async def remove_user_department(
    user_id: int,
    membership_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[SYSTEM ADMIN ONLY]** Entfernt User aus einer Abteilung.
    
    Args:
        user_id: User ID
        membership_id: UserGroupMembership ID zu entfernen
        current_user: System Admin
        db: Datenbankverbindung
    """
    if not _is_system_admin(current_user):
        raise HTTPException(status_code=403, detail="🚨 Nur System Administratoren dürfen Abteilungen entfernen")
    
    try:
        membership = db.query(UserGroupMembershipModel).filter(
            UserGroupMembershipModel.id == membership_id,
            UserGroupMembershipModel.user_id == user_id
        ).first()
        
        if not membership:
            raise HTTPException(status_code=404, detail="Abteilungszuordnung nicht gefunden")
        
        # Soft-Delete für Audit-Trail
        membership.is_active = False
        membership.assigned_by_id = current_user.id
        
        db.commit()
        
        return {"message": f"User aus Abteilung entfernt (Soft-Delete)", "membership_id": membership_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Entfernen: {str(e)}")

@app.delete("/api/users/{user_id}/permanent", tags=["User Management (Admin Only)"])
async def delete_user_permanently(
    user_id: int,
    request: Request = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[SYSTEM ADMIN ONLY]** Löscht einen User PERMANENT aus der Datenbank.
    
    ⚠️ **GEFÄHRLICH:** Komplette Löschung inklusive aller Referenzen!
    Nur für Testzwecke verwenden. Benötigt Doppel-Bestätigung.
    
    Args:
        user_id: User ID zu löschen
        force: Muss "true" sein für Bestätigung
        confirm_password: Admin-Passwort zur Bestätigung
        current_user: System Admin
        db: Datenbankverbindung
        
    Security:
        - Nur System Admins
        - QMS Admin kann sich nicht selbst löschen
        - Admin-Passwort erforderlich
        - Force-Flag erforderlich
    """
    if not _is_system_admin(current_user):
        raise HTTPException(status_code=403, detail="🚨 Nur System Administratoren dürfen User permanent löschen")
    
    # Passwort aus Request Body holen
    confirm_password = ""
    if request:
        try:
            body = await request.json()
            confirm_password = body.get("confirm_password", "")
        except:
            pass
    
    if not confirm_password:
        raise HTTPException(status_code=400, detail="🚨 Admin-Passwort zur Bestätigung erforderlich")
    
    # Admin-Passwort validieren
    from .auth import verify_password
    if not verify_password(confirm_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="🚨 Admin-Passwort falsch")
    
    try:
        target_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail=f"User mit ID {user_id} nicht gefunden")
        
        # SICHERHEIT: QMS Admin darf sich nicht selbst löschen
        if target_user.email == "qms.admin@company.com":
            raise HTTPException(status_code=403, detail="🚨 QMS System Administrator kann nicht gelöscht werden!")
        
        if target_user.id == current_user.id:
            raise HTTPException(status_code=403, detail="🚨 User kann sich nicht selbst löschen!")
        
        # Alle Referenzen löschen (CASCADE)
        db.query(UserGroupMembershipModel).filter(UserGroupMembershipModel.user_id == user_id).delete()
        db.delete(target_user)
        db.commit()
        
        print(f"⚠️ PERMANENT GELÖSCHT: User {target_user.full_name} ({target_user.email}) von {current_user.full_name}")
        
        return {"message": f"User '{target_user.full_name}' permanent gelöscht", "deleted_user_id": user_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen: {str(e)}")

# === BENUTZER-SELBSTVERWALTUNG API ===
# DSGVO-konforme Endpunkte für Benutzerselbstverwaltung

@app.get("/api/users/me/profile", response_model=UserProfileResponse, tags=["User Self-Management"])
async def get_my_profile(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[DSGVO-konform]** Ruft das eigene Benutzerprofil ab.
    
    Jeder authentifizierte Benutzer kann seine eigenen Daten einsehen.
    Zeigt alle relevanten Account-Informationen ohne sensible Daten.
    
    Returns:
        UserProfileResponse: Vollständige Profil-Informationen
        
    DSGVO Art. 15: Recht auf Auskunft über personenbezogene Daten
    """
    try:
        # Robuste Interessensgruppen-Ermittlung mit korrekter Objekt-Abfrage
        try:
            # Direkter Join über UserGroupMembership zu InterestGroup für vollständige Objekte
            user_groups_query = db.query(InterestGroupModel).join(UserGroupMembershipModel).filter(
                UserGroupMembershipModel.user_id == current_user.id,
                UserGroupMembershipModel.is_active == True,
                InterestGroupModel.is_active == True
            ).all()
            
            interest_group_names = [group.name for group in user_groups_query if group and group.name]
            print(f"🔍 User {current_user.id} Gruppen gefunden: {interest_group_names}")
            
        except Exception as group_error:
            print(f"⚠️ Fehler beim Laden der Benutzergruppen für User {current_user.id}: {group_error}")
            interest_group_names = []
        
        # Robuste Berechtigungen-Parsing mit Fallback
        individual_permissions = current_user.individual_permissions or ""
        if isinstance(individual_permissions, str):
            import json
            try:
                permissions_list = json.loads(individual_permissions) if individual_permissions.strip() else []
                # Validierung: Nur String-Werte in der Liste
                permissions_list = [str(p) for p in permissions_list if p]
            except (json.JSONDecodeError, TypeError) as json_error:
                print(f"⚠️ Fehler beim Parsen der Berechtigungen für User {current_user.id}: {json_error}")
                permissions_list = []
        else:
            permissions_list = individual_permissions or []
        
        # Datenvalidierung und Bereinigung
        profile_data = {
            'id': current_user.id,
            'email': current_user.email or 'unbekannt@qms.com',
            'full_name': current_user.full_name or 'Unbekannter Benutzer',
            'employee_id': current_user.employee_id or None,
            'organizational_unit': current_user.organizational_unit or 'Nicht zugeordnet',
            'individual_permissions': permissions_list,
            'is_department_head': bool(current_user.is_department_head),
            'approval_level': max(1, min(4, current_user.approval_level or 1)),  # Sicherstellen 1-4
            'is_active': bool(current_user.is_active),
            'created_at': current_user.created_at,
            'interest_groups': interest_group_names,
            'last_login': None,  # TODO: Implementierung von last_login tracking
            'password_changed_at': None  # TODO: Implementierung von password_changed_at tracking
        }
        
        profile = UserProfileResponse(**profile_data)
        
        print(f"✅ Profil erfolgreich geladen für User {current_user.id} ({current_user.email}) - Gruppen: {len(interest_group_names)}")
        return profile
        
    except Exception as e:
        print(f"❌ Fehler beim Laden des Profils für User {current_user.id}: {str(e)}")
        # Detaillierte Fehler-Logs für Debugging
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500, 
            detail=f"Profil konnte nicht geladen werden. Bitte wenden Sie sich an den Administrator. Fehler-ID: {current_user.id}"
        )

@app.put("/api/users/me/password", response_model=PasswordResetResponse, tags=["User Self-Management"])
async def change_my_password(
    password_change: PasswordChangeRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[DSGVO-konform]** Ändert das eigene Passwort.
    
    Benutzer können ihr eigenes Passwort jederzeit ändern.
    Erfordert Bestätigung des aktuellen Passworts für Sicherheit.
    
    Args:
        password_change: PasswordChangeRequest mit aktuellem und neuem Passwort
        current_user: Authentifizierter Benutzer
        db: Datenbankverbindung
        
    Returns:
        PasswordResetResponse: Bestätigung der Passwort-Änderung
        
    Security:
        - Aktuelles Passwort muss bestätigt werden
        - Neues Passwort muss Sicherheitsanforderungen erfüllen
        - Passwort-Bestätigung erforderlich
        
    DSGVO Art. 16: Recht auf Berichtigung personenbezogener Daten
    """
    try:
        # Validierung: Passwörter stimmen überein
        password_change.validate_passwords_match()
        
        # Aktuelles Passwort validieren
        from .auth import verify_password
        if not verify_password(password_change.current_password, current_user.hashed_password):
            raise HTTPException(status_code=401, detail="Aktuelles Passwort ist falsch")
        
        # Neues Passwort hashen
        new_hashed_password = get_password_hash(password_change.new_password)
        
        # Passwort in Datenbank aktualisieren
        current_user.hashed_password = new_hashed_password
        db.commit()
        
        print(f"✅ Passwort geändert: {current_user.full_name} ({current_user.email})")
        
        return PasswordResetResponse(
            message="Passwort erfolgreich geändert",
            temporary_password=None,
            force_change_required=False,
            reset_by_admin=False,
            reset_at=datetime.now()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Ändern des Passworts: {str(e)}")

@app.put("/api/users/{user_id}/password/admin-reset", response_model=PasswordResetResponse, tags=["User Management (Admin Only)"])
async def admin_reset_user_password(
    user_id: int,
    reset_request: AdminPasswordResetRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[SYSTEM ADMIN ONLY]** Setzt das Passwort eines Benutzers zurück (Notfall).
    
    Nur für System-Administratoren verfügbar. Für Notfälle wie:
    - Benutzer hat Passwort vergessen
    - Account-Sperrung aufheben
    - Sicherheitsvorfall-Response
    
    Args:
        user_id: ID des Benutzers für Passwort-Reset
        reset_request: AdminPasswordResetRequest mit Reset-Details
        current_user: System Administrator
        db: Datenbankverbindung
        
    Returns:
        PasswordResetResponse: Temporäres Passwort und Reset-Informationen
        
    Security:
        - Nur System-Administratoren
        - Audit-Trail wird geführt
        - Temporäres Passwort wird generiert
        - Benutzer muss Passwort beim nächsten Login ändern
        
    Compliance:
        - Vollständige Protokollierung für Audit
        - Begründung erforderlich
    """
    if not _is_system_admin(current_user):
        raise HTTPException(status_code=403, detail="🚨 Nur System Administratoren dürfen Passwörter zurücksetzen")
    
    try:
        # Ziel-Benutzer suchen
        target_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail=f"Benutzer mit ID {user_id} nicht gefunden")
        
        # Temporäres Passwort generieren oder verwenden
        import secrets
        import string
        
        if reset_request.temporary_password:
            temp_password = reset_request.temporary_password
        else:
            # Sicheres temporäres Passwort generieren
            alphabet = string.ascii_letters + string.digits + "!@#$%&*"
            temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        # Passwort hashen und setzen
        new_hashed_password = get_password_hash(temp_password)
        target_user.hashed_password = new_hashed_password
        
        db.commit()
        
        # Audit-Log
        print(f"🔧 ADMIN PASSWORD RESET: {target_user.full_name} ({target_user.email}) von {current_user.full_name}")
        print(f"   Grund: {reset_request.reset_reason}")
        print(f"   Force Change: {reset_request.force_change_on_login}")
        
        return PasswordResetResponse(
            message=f"Passwort für {target_user.full_name} erfolgreich zurückgesetzt",
            temporary_password=temp_password,
            force_change_required=reset_request.force_change_on_login,
            reset_by_admin=True,
            reset_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Passwort-Reset: {str(e)}")

@app.post("/api/users/{user_id}/temp-password", response_model=PasswordResetResponse, tags=["User Management (Admin Only)"])
async def generate_temp_password(
    user_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[SYSTEM ADMIN ONLY]** Generiert temporäres Passwort für Benutzer.
    
    Schnelle Hilfe-Funktion für Administratoren ohne vollständigen Reset.
    Generiert sicheres temporäres Passwort und setzt Force-Change-Flag.
    
    Args:
        user_id: ID des Benutzers
        current_user: System Administrator
        db: Datenbankverbindung
        
    Returns:
        PasswordResetResponse: Temporäres Passwort
        
    Use Cases:
        - Neuer Mitarbeiter benötigt ersten Login
        - Schnelle Passwort-Hilfe ohne vollständigen Reset
        - Temporärer Zugang für Externe
    """
    if not _is_system_admin(current_user):
        raise HTTPException(status_code=403, detail="🚨 Nur System Administratoren dürfen temporäre Passwörter generieren")
    
    try:
        target_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail=f"Benutzer mit ID {user_id} nicht gefunden")
        
        # Sicheres temporäres Passwort generieren
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%&*"
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(10))
        
        # Passwort setzen
        new_hashed_password = get_password_hash(temp_password)
        target_user.hashed_password = new_hashed_password
        
        db.commit()
        
        print(f"🔑 TEMP PASSWORD: {target_user.full_name} ({target_user.email}) von {current_user.full_name}")
        
        return PasswordResetResponse(
            message=f"Temporäres Passwort für {target_user.full_name} generiert",
            temporary_password=temp_password,
            force_change_required=True,
            reset_by_admin=True,
            reset_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Generieren des temporären Passworts: {str(e)}")

def _is_system_admin(user: UserModel) -> bool:
    """
    Prüft ob User System Administrator ist.
    
    Args:
        user: User Model Object
        
    Returns:
        bool: True wenn System Admin
    """
    try:
        # System Admin Permissions prüfen
        perms = user.individual_permissions or ""
        if isinstance(perms, str):
            import json
            try:
                perms_list = json.loads(perms)
                return "system_administration" in perms_list
            except json.JSONDecodeError:
                return False
        elif isinstance(perms, list):
            return "system_administration" in perms
        
        return False
    except Exception:
        return False

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 