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

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

# === ENUMS ===
class DocumentStatus(enum.Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    OBSOLETE = "obsolete"

class DocumentType(enum.Enum):
    """
    Dokumenttypen für QMS-spezifische Dokumentenverwaltung.
    
    Definiert 14 standardisierte Dokumenttypen nach ISO 13485 und MDR
    für strukturierte Dokumentenverwaltung im Medizinprodukte-QMS.
    
    Kategorien:
    - Kerndokumente: QM_MANUAL, SOP, WORK_INSTRUCTION
    - Formulare & Vorlagen: FORM, USER_MANUAL, SERVICE_MANUAL
    - Analyse & Validierung: RISK_ASSESSMENT, VALIDATION_PROTOCOL
    - Prozesse: CALIBRATION_PROCEDURE, AUDIT_REPORT, CAPA_DOCUMENT
    - Training & Spezifikationen: TRAINING_MATERIAL, SPECIFICATION
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
    
    @property
    def group_permissions_list(self):
        """Gruppen-Permissions als Python-Liste"""
        if self.group_permissions:
            try:
                import json
                return json.loads(self.group_permissions)
            except (json.JSONDecodeError, TypeError):
                return []
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
    approval_level = Column(Integer, default=1, comment="Freigabe-Level: 1=Standard, 2=Teamleiter, 3=Abteilungsleiter, 4=QM-Manager")
    is_active = Column(Boolean, default=True, nullable=False,
                      comment="Account-Status: False = deaktiviert")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False,
                       comment="Zeitpunkt der Account-Erstellung")
    
    # Relationships
    group_memberships = relationship("UserGroupMembership", back_populates="user", foreign_keys="UserGroupMembership.user_id")
    documents_created = relationship("Document", back_populates="creator")
    calibrations_responsible = relationship("Calibration", back_populates="responsible_user")

class UserGroupMembership(Base):
    """
    Zuordnungstabelle für Many-to-Many Beziehung User ↔ InterestGroup.
    
    Ermöglicht flexible Zuordnung von Benutzern zu mehreren Interessensgruppen
    mit spezifischen Rollen innerhalb jeder Gruppe. Unterstützt komplexe
    Organisationsstrukturen und Matrix-Organisationen.
    
    Geschäftslogik:
    - Ein User kann mehreren Gruppen angehören
    - Verschiedene Rollen in verschiedenen Gruppen möglich
    - Zeitstempel für Audit-Trail und Historisierung
    - Deaktivierung ohne Datenverlust möglich
    
    Anwendungsfälle:
    - QM-Manager in mehreren Produktgruppen
    - Entwickler in verschiedenen Projektteams
    - Externe Auditoren mit temporärem Zugang
    """
    __tablename__ = "user_group_memberships"
    
    id = Column(Integer, primary_key=True, index=True,
                comment="Eindeutige ID der Zuordnung")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True,
                     comment="Referenz auf User.id")
    interest_group_id = Column(Integer, ForeignKey("interest_groups.id"), nullable=False, index=True,
                              comment="Referenz auf InterestGroup.id")
    role_in_group = Column(String(50), comment="Spezifische Rolle des Users in dieser Gruppe")
    is_active = Column(Boolean, default=True, nullable=False,
                      comment="Aktiv-Status der Zuordnung")
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False,
                      comment="Zeitpunkt des Beitritts zur Gruppe")
    
    # Relationships
    user = relationship("User", back_populates="group_memberships")
    interest_group = relationship("InterestGroup", back_populates="user_memberships")

# === DOKUMENTENMANAGEMENT ===

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
    - Dateipfad-Referenzierung für physische Dokumente
    
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
    file_path = Column(String(500), comment="Relativer Pfad zur physischen Datei")
    tags = Column(String(500), comment="JSON string für Flexibilität")
    
    # Metadata
    creator_id = Column(Integer, ForeignKey("users.id"), comment="Ersteller des Dokuments (User.id)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Zeitpunkt der Erstellung")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Zeitpunkt der letzten Aktualisierung")
    
    # Relationships
    creator = relationship("User", back_populates="documents_created", foreign_keys=[creator_id])
    norm_mappings = relationship("DocumentNormMapping", back_populates="document")

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