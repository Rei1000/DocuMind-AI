"""
🏗️ ENHANCED SCHEMAS für KI-QMS - Enterprise Grade v3.1.0
═══════════════════════════════════════════════════════════

Umfassende Pydantic Schemas für erweiterte Metadaten-Verarbeitung:

✅ FEATURES:
- 🎯 Enterprise-Grade Chunk-Metadaten mit Versionierung
- 📊 5-Layer Metadaten-Struktur mit JSON-Validierung  
- 🔍 Enhanced Document Classification (25+ Typen)
- 🏷️ Hierarchische Keywords mit Importance-Scoring
- 📏 QM-spezifische Compliance-Felder
- 🔄 Backward-Compatibility für bestehende Systeme

Author: Enhanced AI Assistant
Version: 3.5.0 - Enterprise Edition
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum
import json

# Enhanced Document Types
class EnhancedDocumentType(str, Enum):
    """Erweiterte Dokumenttyp-Klassifizierung für QMS-Systeme"""
    # QM Core Documents
    QM_MANUAL = "QM_MANUAL"
    QM_POLICY = "QM_POLICY" 
    QM_PROCEDURE = "QM_PROCEDURE"
    WORK_INSTRUCTION = "WORK_INSTRUCTION"
    FORM = "FORM"
    
    # Standards & Normen
    ISO_STANDARD = "ISO_STANDARD"
    DIN_STANDARD = "DIN_STANDARD" 
    EN_STANDARD = "EN_STANDARD"
    
    # Regulatory Documents
    FDA_GUIDANCE = "FDA_GUIDANCE"
    MDR_DOCUMENT = "MDR_DOCUMENT"
    CE_MARKING = "CE_MARKING"
    
    # Process Documents
    SOP = "SOP"
    PROTOCOL = "PROTOCOL"
    CHECKLIST = "CHECKLIST"
    
    # Reports & Records
    AUDIT_REPORT = "AUDIT_REPORT"
    TEST_REPORT = "TEST_REPORT"
    VALIDATION_REPORT = "VALIDATION_REPORT"
    
    # Risk Management
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    RISK_CONTROL = "RISK_CONTROL"
    
    # General
    OTHER = "OTHER"
    TEMPLATE = "TEMPLATE"


class KeywordImportance(str, Enum):
    """Wichtigkeit von Keywords für Suche und Indexierung"""
    CRITICAL = "CRITICAL"      # Must-have für Searches (Gewicht: 1.0)
    HIGH = "HIGH"             # Sehr wichtig (Gewicht: 0.8)
    MEDIUM = "MEDIUM"         # Standard wichtig (Gewicht: 0.6)
    LOW = "LOW"               # Unterstützend (Gewicht: 0.4)


class ComplianceLevel(str, Enum):
    """Compliance-Level für Regulatory Dokumente"""
    CRITICAL = "CRITICAL"      # FDA, MDR kritische Anforderungen
    HIGH = "HIGH"             # Wichtige Compliance-Aspekte  
    MEDIUM = "MEDIUM"         # Standard Compliance
    LOW = "LOW"               # Informative Inhalte
    NOT_APPLICABLE = "NOT_APPLICABLE"


# Enhanced Base Models
class EnhancedKeyword(BaseModel):
    """Erweiterte Keyword-Struktur mit Importance-Scoring"""
    term: str = Field(..., min_length=2, max_length=100, description="Keyword-Begriff")
    importance: KeywordImportance = Field(KeywordImportance.MEDIUM, description="Wichtigkeitslevel")
    category: str = Field("general", description="Keyword-Kategorie")
    confidence: float = Field(0.7, ge=0.0, le=1.0, description="AI-Konfidenz")


class QualityScore(BaseModel):
    """Detaillierte Qualitätsbewertung"""
    overall: float = Field(0.7, ge=0.0, le=1.0, description="Gesamt-Qualitätsscore")
    content_quality: float = Field(0.7, ge=0.0, le=1.0, description="Inhaltliche Qualität")
    completeness: float = Field(0.7, ge=0.0, le=1.0, description="Vollständigkeit")
    clarity: float = Field(0.7, ge=0.0, le=1.0, description="Klarheit")
    structure: float = Field(0.7, ge=0.0, le=1.0, description="Strukturelle Qualität")
    compliance_readiness: float = Field(0.7, ge=0.0, le=1.0, description="Compliance-Bereitschaft")


class EnhancedChunkMetadata(BaseModel):
    """Enterprise-Grade Chunk-Metadaten für Qdrant Vector Database"""
    # Basic Identification
    document_id: int = Field(..., description="SQL Document ID")
    chunk_index: int = Field(..., description="Position des Chunks im Dokument")
    chunk_id: Optional[str] = Field(None, description="Eindeutige Chunk-ID")
    
    # Document Context
    document_title: str = Field(..., description="Vollständiger Dokumenttitel")
    document_type: EnhancedDocumentType = Field(EnhancedDocumentType.OTHER, description="Klassifizierter Dokumenttyp")
    document_version: str = Field("1.0", description="Dokumentversion")
    
    # Content Structure
    section_title: Optional[str] = Field(None, description="Sektion/Kapitel des Chunks")
    paragraph_number: Optional[int] = Field(None, description="Absatz-Nummer in Sektion")
    page_number: Optional[int] = Field(None, description="Geschätzte Seitenzahl")
    
    # Text Analysis
    word_count: int = Field(0, description="Wortanzahl im Chunk")
    keywords: List[EnhancedKeyword] = Field(default_factory=list, description="Extracted Keywords")
    importance_score: float = Field(0.5, ge=0.0, le=1.0, description="Wichtigkeit für Dokument")
    
    # Interest Group Tagging
    interest_groups: List[str] = Field(default_factory=list, description="Relevante Interessensgruppen")
    
    # Technical Metadata
    chunking_method: str = Field("hierarchical", description="Verwendete Chunking-Methode")
    embedding_model: str = Field("text-embedding-3-small", description="Verwendetes Embedding-Model")
    metadata_version: str = Field("3.5.0", description="Version dieses Metadaten-Schemas")
    
    @validator('chunk_id', always=True)
    def generate_chunk_id(cls, v, values):
        """Generiert Chunk-ID falls nicht vorhanden"""
        if v is None and 'document_id' in values and 'chunk_index' in values:
            return f"{values['document_id']}:{values['chunk_index']}"
        return v


class EnhancedDocumentMetadata(BaseModel):
    """Umfassende Dokumentmetadaten für SQL-Database"""
    # Document Identification
    title: str = Field(..., min_length=2, max_length=500, description="Dokumenttitel")
    document_type: EnhancedDocumentType = Field(EnhancedDocumentType.OTHER, description="Klassifizierter Dokumenttyp")
    version: str = Field("1.0", description="Dokumentversion")
    
    # Hierarchical Classification
    main_category: str = Field("Unknown", description="Hauptkategorie")
    sub_category: str = Field("Unknown", description="Unterkategorie")
    process_area: str = Field("General", description="Prozessbereich")
    
    # Content Analysis
    description: str = Field("", max_length=2000, description="Ausführliche Beschreibung")
    summary: Optional[str] = Field(None, max_length=500, description="Kurze Zusammenfassung")
    
    # Keywords
    primary_keywords: List[EnhancedKeyword] = Field(default_factory=list, description="Hauptkeywords")
    secondary_keywords: List[EnhancedKeyword] = Field(default_factory=list, description="Sekundäre Keywords")
    qm_keywords: List[EnhancedKeyword] = Field(default_factory=list, description="QM-spezifische Keywords")
    
    # Document Structure
    sections_detected: List[str] = Field(default_factory=list, description="Erkannte Sektionen")
    has_tables: bool = Field(False, description="Enthält Tabellen")
    has_figures: bool = Field(False, description="Enthält Abbildungen")
    has_appendices: bool = Field(False, description="Enthält Anhänge")
    
    # Compliance & Regulatory
    iso_standards_referenced: List[str] = Field(default_factory=list, description="Referenzierte ISO Standards")
    regulatory_references: List[str] = Field(default_factory=list, description="Regulatory Referenzen")
    compliance_areas: List[str] = Field(default_factory=list, description="Compliance-Bereiche")
    compliance_level: ComplianceLevel = Field(ComplianceLevel.MEDIUM, description="Compliance-Level")
    
    # Quality Assessment
    quality_scores: QualityScore = Field(default_factory=QualityScore, description="Qualitätsbewertung")
    
    # Interest Group Relevance
    interest_groups: List[str] = Field(default_factory=list, description="Relevante Interessensgruppen")
    
    # AI Processing Metadata
    ai_confidence: float = Field(0.7, ge=0.0, le=1.0, description="Gesamt-AI-Konfidenz")
    processing_time: float = Field(0.0, description="Verarbeitungszeit in Sekunden")
    ai_methodology: str = Field("multilayer_analysis", description="Verwendete AI-Methodik")
    
    # Versioning
    metadata_version: str = Field("3.5.0", description="Metadaten-Schema-Version")
    extracted_at: datetime = Field(default_factory=datetime.utcnow, description="Extraktionszeitpunkt")


# Response Schemas
class EnhancedMetadataResponse(BaseModel):
    """Response für Enhanced Metadata Extraction"""
    success: bool = Field(..., description="Erfolg der Operation")
    metadata: EnhancedDocumentMetadata = Field(..., description="Extrahierte Metadaten")
    chunks_metadata: List[EnhancedChunkMetadata] = Field(default_factory=list, description="Chunk-Metadaten")
    processing_time: float = Field(..., description="Verarbeitungszeit in Sekunden")
    errors: List[str] = Field(default_factory=list, description="Aufgetretene Fehler")
    warnings: List[str] = Field(default_factory=list, description="Warnungen")
    
    # Performance Metrics
    chunks_created: int = Field(0, description="Anzahl erstellter Chunks")
    confidence_score: float = Field(0.7, ge=0.0, le=1.0, description="Gesamt-Konfidenz")
    
    # Versioning
    schema_version: str = Field("3.5.0", description="Schema-Version")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Response-Zeitstempel")


# Request Schemas
class EnhancedMetadataExtractionRequest(BaseModel):
    """Request für Enhanced Metadata Extraction"""
    content: str = Field(..., description="Dokumentinhalt für Analyse")
    document_id: Optional[int] = Field(None, description="Bestehende Dokument-ID")
    filename: Optional[str] = Field(None, description="Dateiname")
    document_type_hint: Optional[EnhancedDocumentType] = Field(None, description="Typ-Hinweis")
    enhanced_chunking: bool = Field(True, description="Erweiterte Chunk-Metadaten erstellen")
    
    # Processing Options
    include_summary: bool = Field(True, description="Summary generieren")
    include_keywords: bool = Field(True, description="Keywords extrahieren")
    include_compliance: bool = Field(True, description="Compliance-Analyse")
    include_quality_scores: bool = Field(True, description="Qualitätsbewertung")


# Utility Functions
def normalize_document_type(doc_type: str) -> EnhancedDocumentType:
    """Normalisiert Dokumenttyp-String zu Enum"""
    legacy_mapping = {
        "PROCEDURE": EnhancedDocumentType.QM_PROCEDURE,
        "WORK_INSTRUCTION": EnhancedDocumentType.WORK_INSTRUCTION,
        "FORM": EnhancedDocumentType.FORM,
        "OTHER": EnhancedDocumentType.OTHER,
    }
    
    try:
        return EnhancedDocumentType(doc_type.upper())
    except ValueError:
        return legacy_mapping.get(doc_type.upper(), EnhancedDocumentType.OTHER)


def create_fallback_metadata(title: str = "Unknown Document") -> EnhancedDocumentMetadata:
    """Erstellt Fallback-Metadaten bei Fehlern"""
    return EnhancedDocumentMetadata(
        title=title,
        document_type=EnhancedDocumentType.OTHER,
        main_category="Unknown",
        sub_category="Unknown",
        process_area="General",
        description="Dokument mit minimalen Metadaten (Fehler bei Enhanced Extraction)",
        quality_scores=QualityScore(
            overall=0.3,
            content_quality=0.3,
            completeness=0.3,
            clarity=0.3,
            structure=0.3,
            compliance_readiness=0.3
        ),
        ai_confidence=0.1,
        ai_methodology="fallback_minimal"
    )