"""
KI-QMS Datenmodelle (SQLAlchemy ORM)

Dieses Modul definiert alle Datenmodelle für das KI-gestützte 
Qualitätsmanagementsystem. Die Modelle repräsentieren die Datenbankstrukturen
für das 13-Interessensgruppen-System und QMS-spezifische Entitäten.

Hauptkomponenten:
- InterestGroup: 13 praxisorientierte Stakeholder-Gruppen
- User: Benutzer mit Rollen und Abteilungszuordnung
- UserGroupMembership: Many-to-Many Beziehung User ↔ Groups
- Document: QMS-Dokumente mit 14 spezifischen Typen
- Norm: Compliance-Standards (ISO 13485, MDR, etc.)
- Equipment: Geräte-Management mit Kalibrierungs-Tracking
- Calibration: Kalibrierungsprotokoll mit Audit-Trail

Technologie:
- SQLAlchemy ORM für Datenbankoperationen
- Pydantic für Datenvalidierung
- Enum für typisierte Auswahlwerte
- JSON-Felder für flexible Datenstrukturen

Autoren: KI-QMS Entwicklungsteam
Version: 1.0.0 (MVP Phase 1)
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

# === ENUMS ===
class DocumentStatus(enum.Enum):
    """
    Dokumentenstatus für QM-Workflow nach ISO 13485.
    
    Vierstufiger Freigabe-Workflow:
    - DRAFT: Entwurf in Bearbeitung
    - REVIEWED: Fachlich geprüft, wartet auf QM-Freigabe  
    - APPROVED: QM-freigegeben, offiziell gültig
    - OBSOLETE: Nicht mehr gültig, archiviert
    """
    DRAFT = "draft"          # ✏️ Entwurf - wird erstellt/überarbeitet
    REVIEWED = "reviewed"    # 🔍 Geprüft - fachliche Prüfung abgeschlossen
    APPROVED = "approved"    # ✅ Freigegeben - QM-Freigabe erhalten
    OBSOLETE = "obsolete"    # 🗑️ Obsolet - nicht mehr gültig

class DocumentType(enum.Enum):
    """
    Dokumenttypen für QMS-spezifische Dokumentenverwaltung.
    
    Definiert 14+ standardisierte Dokumenttypen nach ISO 13485 und MDR
    für strukturierte Dokumentenverwaltung im Medizinprodukte-QMS.
    
    Kategorien:
    - Kerndokumente: QM_MANUAL, SOP, WORK_INSTRUCTION
    - Formulare & Vorlagen: FORM, USER_MANUAL, SERVICE_MANUAL
    - Analyse & Validierung: RISK_ASSESSMENT, VALIDATION_PROTOCOL
    - Prozesse: CALIBRATION_PROCEDURE, AUDIT_REPORT, CAPA_DOCUMENT
    - Training & Spezifikationen: TRAINING_MATERIAL, SPECIFICATION
    - Normen & Standards: STANDARD_NORM, REGULATION, GUIDANCE_DOCUMENT
    - Flexibilität: OTHER für kundenspezifische Typen
    """
    QM_MANUAL = "QM_MANUAL"                      # Qualitätsmanagement-Handbuch (Hauptdokument)
    SOP = "SOP"                                  # Standard Operating Procedure
    WORK_INSTRUCTION = "WORK_INSTRUCTION"        # Arbeitsanweisung (detaillierte Schritte)
    FORM = "FORM"                                # Formular/Vorlage für Dokumentation
    USER_MANUAL = "USER_MANUAL"                  # Benutzerhandbuch für Medizinprodukte
    SERVICE_MANUAL = "SERVICE_MANUAL"            # Servicehandbuch für Wartung
    RISK_ASSESSMENT = "RISK_ASSESSMENT"          # Risikoanalyse nach ISO 14971
    VALIDATION_PROTOCOL = "VALIDATION_PROTOCOL"  # Validierungsprotokoll (IQ/OQ/PQ)
    CALIBRATION_PROCEDURE = "CALIBRATION_PROCEDURE" # Kalibrierverfahren für Equipment
    AUDIT_REPORT = "AUDIT_REPORT"                # Audit-Berichte (intern/extern)
    CAPA_DOCUMENT = "CAPA_DOCUMENT"              # CAPA-Dokumentation (Corrective Action)
    TRAINING_MATERIAL = "TRAINING_MATERIAL"      # Schulungsunterlagen und -protokolle
    SPECIFICATION = "SPECIFICATION"              # Spezifikationen und Anforderungen
    STANDARD_NORM = "STANDARD_NORM"              # Standards und Normen (ISO, IEC, DIN, EN)
    REGULATION = "REGULATION"                    # Regulatorische Dokumente (MDR, FDA CFR)
    GUIDANCE_DOCUMENT = "GUIDANCE_DOCUMENT"      # Leitfäden und Guidance-Dokumente
    PROCESS = "PROCESS"                          # Prozessdokumente (Flussdiagramme, Workflows)
    PROMPT_TEST = "PROMPT_TEST"                  # Prompt-Test für Qualitätssicherung
    OTHER = "OTHER"                              # Sonstige/kundenspezifische Dokumente

class EquipmentStatus(enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"

# === KERN-MODELLE: 13-INTERESSENSGRUPPEN-SYSTEM ===

class InterestGroup(Base):
    """
    Interessensgruppen-Modell für das 13-Stakeholder-System.
    
    Repräsentiert die organisatorischen Einheiten des QMS, von internen
    Teams (Einkauf, QM, Entwicklung) bis zu externen Stakeholdern 
    (Auditoren, Lieferanten). Jede Gruppe hat spezifische Berechtigungen
    und KI-Funktionalitäten.
    
    Geschäftslogik:
    - Granulare Berechtigungssteuerung über permissions (JSON-Array)
    - KI-Funktionalitäten zugeschnitten auf Gruppenbedürfnisse
    - Unterscheidung zwischen internen/externen Gruppen
    - Soft-Delete über is_active für Audit-Trail
    
    Relationships:
    - users: Many-to-Many über UserGroupMembership
    """
    __tablename__ = "interest_groups"
    
    id = Column(Integer, primary_key=True, index=True, 
                comment="Eindeutige ID der Interessensgruppe")
    name = Column(String(100), unique=True, nullable=False, index=True,
                  comment="Vollständiger Name der Interessensgruppe")
    code = Column(String(50), unique=True, nullable=False, index=True,
                  comment="Eindeutiger Code für API-Zugriff und Referenzierung")
    description = Column(Text, nullable=True,
                        comment="Detaillierte Beschreibung der Aufgaben und Verantwortlichkeiten")
    group_permissions = Column(Text, comment="JSON-String mit spezifischen Gruppen-Berechtigungen (z.B. 'supplier_evaluation', 'audit_management')")
    
    def get_group_permissions_list(self):
        """Gruppen-Permissions als Python-Liste"""
        try:
            import json
            if hasattr(self, '_group_permissions_value') and self._group_permissions_value:
                return json.loads(self._group_permissions_value)
            elif hasattr(self, 'group_permissions') and getattr(self, 'group_permissions', None):
                return json.loads(getattr(self, 'group_permissions'))
            return []
        except (json.JSONDecodeError, TypeError, AttributeError):
            return []
    ai_functionality = Column(Text, comment="Beschreibung der verfügbaren KI-Funktionen für diese Gruppe")
    typical_tasks = Column(Text, comment="Typische Aufgaben und Anwendungsfälle der Gruppe")
    is_external = Column(Boolean, default=False, nullable=False,
                        comment="True für externe Stakeholder (Auditoren, Lieferanten)")
    is_active = Column(Boolean, default=True, nullable=False,
                      comment="Soft-Delete Flag: False = deaktiviert")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False,
                       comment="Zeitpunkt der Erstellung")
    
    # Relationships
    user_memberships = relationship("UserGroupMembership", back_populates="interest_group")

class User(Base):
    """
    Benutzer-Modell für Authentifizierung und Rollenverwaltung.
    
    Repräsentiert Benutzer des QMS-Systems mit ihren Rollen, Abteilungen
    und Authentifizierungsdaten. Unterstützt verschiedene Benutzertypen
    von internen Mitarbeitern bis zu externen Auditoren.
    
    Sicherheitsfeatures:
    - Verschlüsselte Passwort-Speicherung (hashed_password)
    - Eindeutige Username und Email-Adressen
    - Soft-Delete für Audit-Trail
    - Rollen-basierte Zugriffskontrolle
    
    Relationships:
    - interest_groups: Many-to-Many über UserGroupMembership
    - created_documents: One-to-Many zu Document
    - approved_documents: One-to-Many zu Document
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True,
                comment="Eindeutige Benutzer-ID")
    email = Column(String(100), unique=True, index=True, nullable=False,
                  comment="Email-Adresse (eindeutig, für Benachrichtigungen)")
    full_name = Column(String(200), nullable=False,
                      comment="Vollständiger Name (Vor- und Nachname)")
    employee_id = Column(String(50), unique=True,
                        comment="Mitarbeiternummer")
    organizational_unit = Column(String(100), comment="Organisatorische Einheit/Abteilung (unabhängig von funktionalen Interest Groups)")
    hashed_password = Column(String(255), comment="Gehashtes Passwort (bcrypt empfohlen)")
    # === INDIVIDUELLE BERECHTIGUNGEN ===
    individual_permissions = Column(Text, comment="JSON-String mit individuellen User-Berechtigungen (z.B. Abteilungsleiter-Rechte, Sonderzugänge)")
    is_department_head = Column(Boolean, default=False, nullable=False,
                               comment="Abteilungsleiter-Status für Freigabe-Berechtigungen")
    approval_level = Column(Integer, default=1, comment="Freigabe-Level: 1=Standard, 2=Teamleiter, 3=Abteilungsleiter, 4=QM-Manager, 5=System-Admin")
    is_active = Column(Boolean, default=True, nullable=False,
                      comment="Account-Status: False = deaktiviert")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False,
                       comment="Zeitpunkt der Account-Erstellung")
    
    # Relationships
    group_memberships = relationship("UserGroupMembership", back_populates="user", foreign_keys="UserGroupMembership.user_id")
    documents_created = relationship("Document", back_populates="creator", foreign_keys="Document.creator_id")
    calibrations_responsible = relationship("Calibration", back_populates="responsible_user")

class UserGroupMembership(Base):
    """
    Zuordnungstabelle für Many-to-Many Beziehung User ↔ InterestGroup.
    
    **ERWEITERT für Multiple Abteilungen pro User:**
    Ermöglicht flexible Zuordnung von Benutzern zu mehreren Interessensgruppen
    mit **individuellen Approval-Levels** je Abteilung. Unterstützt komplexe
    Organisationsstrukturen wo ein User verschiedene Rollen hat.
    
    **Beispiel:**
    ```
    User: reiner@company.com
    ├── QM-Abteilung (Level 2 - Teamleiter) 
    ├── Service (Level 3 - Abteilungsleiter)
    └── Entwicklung (Level 1 - Mitarbeiter)
    ```
    
    Geschäftslogik:
    - Ein User kann mehreren Gruppen angehören
    - **Verschiedene Approval-Levels** in verschiedenen Gruppen
    - Zeitstempel für Audit-Trail und Historisierung
    - Deaktivierung ohne Datenverlust möglich
    
    Anwendungsfälle:
    - QM-Manager in mehreren Produktgruppen
    - Entwickler in verschiedenen Projektteams  
    - Abteilungsleiter mit Mitarbeiter-Status in anderen Bereichen
    """
    __tablename__ = "user_group_memberships"
    
    id = Column(Integer, primary_key=True, index=True,
                comment="Eindeutige ID der Zuordnung")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True,
                     comment="Referenz auf User.id")
    interest_group_id = Column(Integer, ForeignKey("interest_groups.id"), nullable=False, index=True,
                              comment="Referenz auf InterestGroup.id")
    
    # === ERWEITERTE FELDER FÜR MULTIPLE ABTEILUNGEN ===
    role_in_group = Column(String(50), comment="Spezifische Rolle des Users in dieser Gruppe (z.B. 'Teamleiter', 'Fachexperte')")
    approval_level = Column(Integer, default=1, nullable=False,
                           comment="Freigabe-Level in dieser Abteilung: 1=Mitarbeiter, 2=Teamleiter, 3=Abteilungsleiter, 4=QM-Manager")
    is_department_head = Column(Boolean, default=False, nullable=False, 
                               comment="Abteilungsleiter-Status in dieser spezifischen Gruppe")
    
    # === AUDIT & VERWALTUNG ===
    is_active = Column(Boolean, default=True, nullable=False,
                      comment="Aktiv-Status der Zuordnung")
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False,
                      comment="Zeitpunkt des Beitritts zur Gruppe")
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True,
                           comment="System Admin der diese Zuordnung erstellt hat")
    notes = Column(Text, comment="Bemerkungen zur Zuordnung (z.B. 'Temporär für Projekt XY')")
    
    # Relationships
    user = relationship("User", back_populates="group_memberships", foreign_keys=[user_id])
    interest_group = relationship("InterestGroup", back_populates="user_memberships")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id], post_update=True)
    
    def __repr__(self):
        return f"<UserGroupMembership(user_id={self.user_id}, group_id={self.interest_group_id}, level={self.approval_level})>"

# === DOKUMENTEN-MODELL: QMS-SPEZIFISCHE DOKUMENTENVERWALTUNG ===

class Document(Base):
    """
    Dokumenten-Modell für QMS-Dokumentenverwaltung.
    
    Zentrale Entität für die Verwaltung aller QMS-relevanten Dokumente
    mit 14 spezialisierten Dokumenttypen, Versionskontrolle und 
    Freigabe-Workflow nach ISO 13485 Anforderungen.
    
    Features:
    - 14 QMS-spezifische Dokumenttypen
    - 4-stufiger Freigabe-Workflow (DRAFT → REVIEW → APPROVED → OBSOLETE)
    - Vollständiger Audit-Trail (Ersteller, Genehmiger, Zeitstempel)
    - Versionsverwaltung mit Semantic Versioning
    - Physische Dateispeicherung mit Hash-Validierung
    - RAG-ready Textindexierung
    
    Compliance:
    - ISO 13485 konforme Dokumentenkontrolle
    - MDR-konforme Dokumentation
    - FDA 21 CFR Part 820 Anforderungen
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True,
                comment="Eindeutige Dokument-ID")
    title = Column(String(255), nullable=False, index=True,
                  comment="Dokumententitel (sollte eindeutig sein)")
    document_number = Column(String(50), unique=True, nullable=False,
                            comment="Eindeutige Dokumentennummer")
    document_type = Column(Enum(DocumentType), default=DocumentType.OTHER,
                          comment="Dokumenttyp aus DocumentType Enum")
    version = Column(String(20), nullable=False, default="1.0",
                    comment="Versionsnummer (Semantic Versioning empfohlen)")
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT, index=True,
                   comment="Dokumentstatus aus DocumentStatus Enum")
    content = Column(Text, comment="Detaillierte Beschreibung des Dokumentinhalts")
    
    # === PHYSISCHE DATEI-MANAGEMENT ===
    file_path = Column(String(500), comment="Relativer Pfad zur physischen Datei")
    file_name = Column(String(500), comment="Originaler Dateiname (erweitert für lange Namen)")
    file_size = Column(Integer, comment="Dateigröße in Bytes")
    file_hash = Column(String(64), comment="SHA-256 Hash für Integrität")
    mime_type = Column(String(100), comment="MIME-Type der Datei")
    
    # === RAG-VORBEREITUNG ===
    extracted_text = Column(Text, comment="Extrahierter Text für RAG/AI-Indexierung")
    keywords = Column(String(1000), comment="Extrahierte Schlüsselwörter")
    
    # === VERSIONIERUNG ===
    parent_document_id = Column(Integer, ForeignKey("documents.id"), comment="Referenz auf Vorgängerversion")
    version_notes = Column(Text, comment="Änderungshinweise/Release Notes")
    
    # === QM-SPEZIFISCHE METADATEN ===
    tags = Column(String(500), comment="JSON string für Flexibilität")
    remarks = Column(Text, comment="QM-Manager Hinweise/Bemerkungen")
    chapter_numbers = Column(String(200), comment="Normkapitel (z.B. '4.2.3, 7.5.1')")
    
    # Norm-spezifische Felder
    compliance_status = Column(String(50), comment="Compliance-Status für Normen: ZU_BEWERTEN, EINGEHALTEN, TEILWEISE, NICHT_ZUTREFFEND")
    priority = Column(String(20), comment="Priorität für Normen: HOCH, MITTEL, NIEDRIG")
    scope = Column(Text, comment="Anwendungsbereich/Relevanz für Normen")
    
    # === WORKFLOW & FREIGABEN ===
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), comment="Prüfer (Abteilungsleiter)")
    reviewed_at = Column(DateTime, comment="Zeitpunkt der Prüfung")
    approved_by_id = Column(Integer, ForeignKey("users.id"), comment="Genehmiger (QM-Manager)")
    approved_at = Column(DateTime, comment="Zeitpunkt der Freigabe")
    
    # === STATUS-CHANGE TRACKING ===
    status_changed_by_id = Column(Integer, ForeignKey("users.id"), comment="User der letzten Status-Änderung")
    status_changed_at = Column(DateTime, default=datetime.utcnow, comment="Zeitpunkt der letzten Status-Änderung")
    status_comment = Column(Text, comment="Kommentar zur Status-Änderung")
    
    # === UPLOAD-METHODEN FELDER ===
    upload_method = Column(String(10), default='ocr', comment="Upload-Verarbeitungsmethode: ocr oder visio")
    validation_status = Column(String(50), comment="Validierungsstatus für Visio-Methode: VERIFIED, REVIEW_REQUIRED")
    structured_analysis = Column(Text, comment="JSON-strukturierte Analyse-Daten der Visio-Methode")
    prompt_used = Column(Text, comment="Verwendeter Prompt bei Visio-Verarbeitung")
    ocr_text_preview = Column(Text, comment="OCR-Text-Vorschau für Benutzer-Review")
    
    # Metadata
    creator_id = Column(Integer, ForeignKey("users.id"), comment="Ersteller des Dokuments (User.id)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Zeitpunkt der Erstellung")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Zeitpunkt der letzten Aktualisierung")
    
    # Relationships
    creator = relationship("User", back_populates="documents_created", foreign_keys=[creator_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    status_changed_by = relationship("User", foreign_keys=[status_changed_by_id])
    parent_document = relationship("Document", remote_side=[id], back_populates="child_documents")
    child_documents = relationship("Document", back_populates="parent_document")
    norm_mappings = relationship("DocumentNormMapping", back_populates="document")
    status_history = relationship("DocumentStatusHistory", back_populates="document", order_by="DocumentStatusHistory.changed_at.desc()")

# === NORMEN & COMPLIANCE ===

class Norm(Base):
    """
    Normen-Modell für Compliance-Standards und regulatorische Anforderungen.
    
    Verwaltet alle relevanten Normen, Standards und Verordnungen für
    das Medizinprodukte-QMS. Zentrale Referenz für Compliance-Prüfungen
    und Gap-Analysen.
    
    Normenkategorien:
    - QMS: ISO 13485, ISO 9001
    - REGULATION: MDR, FDA 21 CFR Part 820
    - RISK_MANAGEMENT: ISO 14971
    - SOFTWARE: IEC 62304
    - CLINICAL: ISO 14155, ICH-GCP
    - BIOCOMPATIBILITY: ISO 10993
    
    Compliance-Features:
    - Versionstracking für Norm-Updates
    - Effective Date für Übergangsfristen
    - Mandatory Flag für Pflicht vs. freiwillige Standards
    - Authority für herausgebende Organisation
    """
    __tablename__ = "norms"
    
    id = Column(Integer, primary_key=True, index=True,
                comment="Eindeutige Norm-ID")
    name = Column(String(100), unique=True, nullable=False, index=True,
                 comment="Offizielle Normbezeichnung (z.B. 'ISO 13485:2016')")
    full_title = Column(String(500), nullable=False,
                       comment="Vollständiger Titel der Norm")
    version = Column(String(20), comment="Norm-Version/Jahr (z.B. '2016', '2019')")
    description = Column(Text, comment="Zusammenfassung des Anwendungsbereichs")
    authority = Column(String(100), comment="Herausgebende Organisation (ISO, IEC, FDA, EU Commission)")
    effective_date = Column(DateTime, comment="Datum des Inkrafttretens")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Zeitpunkt der Erfassung im System")
    
    # Relationships
    document_mappings = relationship("DocumentNormMapping", back_populates="norm")
    calibration_requirements = relationship("CalibrationRequirement", back_populates="norm")

# === KALIBRIERUNGSMANAGEMENT ===

class Equipment(Base):
    """
    Equipment-Modell für Geräte- und Asset-Management.
    
    Verwaltet alle kalibrierpflichtigen Geräte, Messausrüstungen und
    kritischen Assets mit automatischer Kalibrierungs-Fristenüberwachung.
    
    Asset-Kategorien:
    - measuring_device: Präzisionsmessgeräte (Messschieber, Waagen)
    - laboratory_scale: Laborwaagen und Analysengeräte  
    - temperature_monitor: Klimaüberwachung und -prüfung
    - pressure_gauge: Druckmessgeräte und -prüfstände
    - test_equipment: Elektrische und mechanische Prüfgeräte
    - production_tool: Kritische Produktionswerkzeuge
    
    Kalibrierungs-Features:
    - Automatische Berechnung von Kalibrierungsterminen
    - Intervall-Management nach Gerätetyp
    - Überfälligkeits-Tracking für Compliance
    - Standort-Verfolgung für Asset-Management
    """
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True,
                comment="Eindeutige Equipment-ID")
    name = Column(String(255), nullable=False, index=True,
                 comment="Gerätename/Bezeichnung")
    equipment_number = Column(String(50), unique=True, nullable=False, index=True,
                              comment="Eindeutige Seriennummer des Geräts")
    manufacturer = Column(String(100), comment="Hersteller des Geräts")
    model = Column(String(100), comment="Modellbezeichnung")
    serial_number = Column(String(100), unique=True, nullable=False, index=True,
                          comment="Eindeutige Seriennummer des Geräts")
    location = Column(String(255), comment="Aktueller Standort des Geräts")
    status = Column(Enum(EquipmentStatus), default=EquipmentStatus.ACTIVE, index=True,
                   comment="Betriebsstatus (active, maintenance, retired)")
    
    # Kalibrierung
    calibration_interval_months = Column(Integer, comment="Kalibrierungsintervall in Monaten")
    last_calibration = Column(DateTime, comment="Datum der letzten Kalibrierung")
    next_calibration = Column(DateTime, index=True, comment="Datum der nächsten fälligen Kalibrierung")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="Zeitpunkt der Registrierung im System")
    
    # Relationships
    calibrations = relationship("Calibration", back_populates="equipment")

class Calibration(Base):
    """
    Kalibrierungs-Modell für Kalibrierungsprotokoll und Audit-Trail.
    
    Dokumentiert alle durchgeführten Kalibrierungen mit vollständiger
    Rückverfolgbarkeit. Erfüllt ISO 17025 Anforderungen für
    Kalibrierungsdokumentation.
    
    Kalibrierungs-Ergebnisse:
    - passed: Erfolgreich, alle Toleranzen eingehalten
    - failed: Fehlgeschlagen, außerhalb der Toleranzen  
    - conditional: Bedingt bestanden, mit Einschränkungen
    
    Compliance-Features:
    - Eindeutige Zertifikatsnummern für Rückverfolgbarkeit
    - Abweichungsdokumentation für Qualitätsbewertung
    - Automatische Equipment-Status-Updates
    - Audit-Trail für regulatorische Prüfungen
    """
    __tablename__ = "calibrations"
    
    id = Column(Integer, primary_key=True, index=True,
                comment="Eindeutige Kalibrierungs-ID")
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, index=True,
                         comment="Referenz auf das kalibrierte Equipment")
    calibration_date = Column(DateTime, nullable=False, index=True,
                             comment="Datum der durchgeführten Kalibrierung")
    next_due_date = Column(DateTime, nullable=False, comment="Geplanter Termin für nächste Kalibrierung")
    calibration_results = Column(Text, comment="JSON string mit Messwerten")
    certificate_path = Column(String(500), comment="Pfad zum Kalibrierungs-Zertifikat (PDF)")
    
    # Status
    status = Column(String(50), default="valid", comment="valid, expired, due")
    responsible_user_id = Column(Integer, ForeignKey("users.id"), comment="Durchführende Person/Organisation")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="Zeitpunkt der Protokoll-Erstellung")
    
    # Relationships
    equipment = relationship("Equipment", back_populates="calibrations")
    responsible_user = relationship("User", back_populates="calibrations_responsible")

# === MAPPING TABELLEN ===

class DocumentNormMapping(Base):
    """Verknüpfung zwischen Dokumenten und Normen"""
    __tablename__ = "document_norm_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    norm_id = Column(Integer, ForeignKey("norms.id"))
    relevant_clauses = Column(String(200))                  # z.B. "4.2.3, 7.5.1"
    compliance_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="norm_mappings")
    norm = relationship("Norm", back_populates="document_mappings")

class CalibrationRequirement(Base):
    """Kalibrierungsanforderungen aus Normen"""
    __tablename__ = "calibration_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    norm_id = Column(Integer, ForeignKey("norms.id"))
    equipment_type = Column(String(100))                    # z.B. "Messschieber", "Waage"
    required_interval_months = Column(Integer)
    requirements_text = Column(Text)
    
    # Relationships
    norm = relationship("Norm", back_populates="calibration_requirements")

class DocumentStatusHistory(Base):
    """
    Audit-Trail für Dokumentstatus-Änderungen.
    
    Vollständige Nachverfolgung aller Status-Wechsel für Compliance
    nach ISO 13485 Anforderungen. Unterstützt Rollback-Funktionalität
    und forensische Analyse.
    
    Workflow-Tracking:
    - Automatische Erfassung bei jedem Status-Change
    - User-Identifikation für Verantwortlichkeit
    - Kommentar-System für Begründungen
    - Unveränderlicher Audit-Trail
    """
    __tablename__ = "document_status_history"
    
    id = Column(Integer, primary_key=True, index=True,
                comment="Eindeutige History-Eintrag-ID")
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True,
                        comment="Referenz auf das Dokument")
    old_status = Column(Enum(DocumentStatus), comment="Vorheriger Status")
    new_status = Column(Enum(DocumentStatus), nullable=False,
                       comment="Neuer Status nach Änderung")
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False,
                          comment="User der die Änderung durchgeführt hat")
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True,
                       comment="Zeitpunkt der Status-Änderung")
    comment = Column(Text, comment="Kommentar/Begründung für Status-Änderung")
    
    # Relationships
    document = relationship("Document", back_populates="status_history")
    changed_by = relationship("User")

# === RAG & KI-ERWEITERTE MODELLE ===

class DocumentIndex(Base):
    """
    Index-Modell für RAG-System und KI-basierte Dokumentensuche.
    
    Verwaltet Embeddings und Metadaten für semantische Suche in QMS-Dokumenten.
    Optimiert für lokale Vector-Database (ChromaDB) Integration.
    
    Features:
    - Chunk-basierte Textindexierung
    - Embedding-Versionierung  
    - Search-Performance-Tracking
    - RAG-Query-Historie
    """
    __tablename__ = "document_indexes"
    
    id = Column(Integer, primary_key=True, index=True,
                comment="Eindeutige Index-ID")
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True,
                        comment="Referenz auf indexiertes Dokument")
    chunk_text = Column(Text, nullable=False,
                       comment="Textinhalt des Chunks")
    chunk_index = Column(Integer, nullable=False,
                        comment="Position des Chunks im Dokument")
    embedding_model = Column(String(100), default="all-MiniLM-L6-v2",
                           comment="Verwendetes Embedding-Model")
    indexed_at = Column(DateTime, default=datetime.utcnow, nullable=False,
                       comment="Zeitpunkt der Indexierung")
    search_count = Column(Integer, default=0,
                         comment="Anzahl der Suchtreffer für Analytics")
    
    # Relationships
    document = relationship("Document")

class RAGQuery(Base):
    """
    RAG-Query-Historie für Analytics und Verbesserung.
    
    Protokolliert alle RAG-Anfragen für Performance-Monitoring,
    Query-Optimierung und User-Experience-Verbesserung.
    """
    __tablename__ = "rag_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    query_text = Column(Text, nullable=False,
                       comment="Benutzer-Anfrage")
    response_text = Column(Text,
                          comment="KI-generierte Antwort")
    confidence_score = Column(Float,
                            comment="Konfidenz-Score der Antwort")
    processing_time = Column(Float,
                           comment="Verarbeitungszeit in Sekunden")
    sources_used = Column(Text,
                         comment="JSON mit verwendeten Quellen")
    provider_used = Column(String(50),
                          comment="Verwendeter KI-Provider")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User")

# === INTELLIGENTE WORKFLOW-MODELLE ===

class TaskStatus(str, Enum):
    """Task-Status für intelligente Workflows"""
    OPEN = "open"              # 📋 Neu erstellt, noch nicht begonnen
    IN_PROGRESS = "in_progress" # 🔄 In Bearbeitung
    WAITING = "waiting"         # ⏳ Wartet auf Input/Freigabe
    COMPLETED = "completed"     # ✅ Abgeschlossen
    CANCELLED = "cancelled"     # ❌ Storniert

class QMSTask(Base):
    """
    Task-Modell für intelligente Workflow-Engine.
    
    Zentrale Entität für alle automatisch generierten und manuellen
    QMS-Aufgaben. Unterstützt rollenbasierte Zuweisung, Abhängigkeiten
    und Compliance-Tracking.
    
    Features:
    - Automatische Workflow-Generierung
    - Rollenbasierte Zuweisungen
    - Abhängigkeiten zwischen Tasks
    - SLA-Monitoring
    - Approval-Workflows
    """
    __tablename__ = "qms_tasks"
    
    id = Column(Integer, primary_key=True, index=True,
                comment="Eindeutige Task-ID")
    title = Column(String(255), nullable=False,
                  comment="Task-Titel")
    description = Column(Text,
                        comment="Detaillierte Task-Beschreibung")
    status = Column(String(20), default="open", index=True,
                   comment="Aktueller Task-Status")
    priority = Column(String(20), default="MEDIUM",
                     comment="Priorität: CRITICAL, HIGH, MEDIUM, LOW")
    
    # Zuweisungen
    assigned_group_id = Column(Integer, ForeignKey("interest_groups.id"), index=True,
                              comment="Zugewiesene Interest Group")
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True,
                             comment="Spezifisch zugewiesener User")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False,
                       comment="Task-Ersteller")
    
    # Zeitmanagement
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    due_date = Column(DateTime, index=True,
                     comment="Fälligkeitsdatum")
    started_at = Column(DateTime,
                       comment="Zeitpunkt des Bearbeitungsbeginns")
    completed_at = Column(DateTime,
                         comment="Zeitpunkt der Fertigstellung")
    
    # Workflow-Integration
    workflow_id = Column(String(100), index=True,
                        comment="ID des auslösenden Workflows")
    workflow_context = Column(Text,
                             comment="JSON mit Workflow-Kontext")
    parent_task_id = Column(Integer, ForeignKey("qms_tasks.id"),
                           comment="Übergeordneter Task für Abhängigkeiten")
    
    # Dokumentation
    required_documents = Column(Text,
                               comment="JSON-Liste benötigter Dokumente")
    prerequisites = Column(Text,
                          comment="JSON-Liste von Voraussetzungen")
    completion_notes = Column(Text,
                             comment="Notizen zur Fertigstellung")
    
    # Approval
    approval_needed = Column(Boolean, default=False,
                           comment="Freigabe durch Vorgesetzten erforderlich")
    approved_by_id = Column(Integer, ForeignKey("users.id"),
                           comment="Freigebender User")
    approved_at = Column(DateTime,
                        comment="Freigabezeitpunkt")
    
    # Relationships
    assigned_group = relationship("InterestGroup")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by_id])
    parent_task = relationship("QMSTask", remote_side=[id], back_populates="subtasks")
    subtasks = relationship("QMSTask", back_populates="parent_task")
    comments = relationship("TaskComment", back_populates="task")

class TaskComment(Base):
    """
    Kommentar-System für Tasks.
    
    Ermöglicht Kommunikation und Dokumentation während
    der Task-Bearbeitung mit Audit-Trail.
    """
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("qms_tasks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment_text = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=True,
                        comment="Interne Notiz oder öffentlicher Kommentar")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    task = relationship("QMSTask", back_populates="comments")
    user = relationship("User")

class WorkflowTemplate(Base):
    """
    Template-System für wiederverwendbare Workflows.
    
    Ermöglicht Konfiguration und Versionierung von
    Standard-Workflows für häufige Szenarien.
    """
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    trigger_type = Column(String(50), nullable=False, index=True,
                         comment="Workflow-Trigger-Typ")
    template_config = Column(Text,
                            comment="JSON-Konfiguration des Templates")
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("User")

class WorkflowExecution(Base):
    """
    Workflow-Ausführungsprotokoll.
    
    Protokolliert alle ausgeführten Workflows für
    Analytics und Prozessoptimierung.
    """
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(100), unique=True, nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"))
    trigger_message = Column(Text,
                            comment="Auslösende Nachricht")
    trigger_context = Column(Text,
                            comment="JSON mit Trigger-Kontext")
    started_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime,
                         comment="Zeitpunkt der Workflow-Fertigstellung")
    status = Column(String(50), default="active",
                   comment="active, completed, cancelled, failed")
    tasks_created = Column(Integer, default=0,
                          comment="Anzahl erstellter Tasks")
    
    # Relationships
    template = relationship("WorkflowTemplate")
    starter = relationship("User") 