"""
🎯 ENHANCED PROMPTS für KI-QMS - Enterprise Grade v3.1.0
═══════════════════════════════════════════════════════════

Optimierte AI-Prompts für konsistente Metadaten-Extraktion:

✅ FEATURES:
- 🎯 Temperature=0 für maximale Konsistenz
- 📊 Strukturierte JSON-Response-Templates
- 🔍 5-Layer Analyse-Prompts (Basic → Expert)
- 🏷️ QM-spezifische Klassifizierung
- 📏 ISO 13485 & MDR konforme Analyse
- 🎨 Few-Shot Learning mit Beispielen

🎯 PROMPT STRATEGY:
- Präzise Instruktionen für AI-Modelle
- Strukturierte JSON-Ausgabe garantiert
- Fallback-Strategien für Edge Cases
- Performance-optimierte Prompt-Längen

Author: Enhanced AI Assistant
Version: 3.1.0 - Enterprise Edition
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# 🎯 ENHANCED METADATA EXTRACTION PROMPTS
# ═══════════════════════════════════════════════════════════

ENHANCED_METADATA_EXTRACTION_PROMPT = """
Sie sind ein Experte für Qualitätsmanagement-Systeme (QMS) und Dokumentenanalyse. 
Analysieren Sie das folgende Dokument und extrahieren Sie umfassende Metadaten.

WICHTIGE INSTRUKTIONEN:
- Antworten Sie AUSSCHLIESSLICH mit gültigem JSON
- Verwenden Sie die exakte Struktur unten
- Seien Sie präzise und konsistent
- Bei Unsicherheit wählen Sie die wahrscheinlichste Option

DOKUMENT-INHALT:
{document_content}

ERWARTETE JSON-STRUKTUR:
{{
    "title": "Vollständiger Dokumenttitel",
    "document_type": "QM_PROCEDURE | WORK_INSTRUCTION | FORM | QM_MANUAL | QM_POLICY | ISO_STANDARD | SOP | PROTOCOL | CHECKLIST | AUDIT_REPORT | TEST_REPORT | VALIDATION_REPORT | RISK_ASSESSMENT | OTHER",
    "version": "Dokumentversion (z.B. '1.0', '2.1')",
    "main_category": "Hauptkategorie (z.B. 'Quality Management', 'Process Control')",
    "sub_category": "Unterkategorie (z.B. 'Procedures', 'Work Instructions')",
    "process_area": "Prozessbereich (z.B. 'Design Controls', 'Manufacturing', 'Quality Assurance')",
    "description": "Ausführliche Beschreibung des Dokuments (max 2000 Zeichen)",
    "summary": "Kurze Zusammenfassung (max 500 Zeichen)",
    "primary_keywords": [
        {{
            "term": "Hauptkeyword",
            "importance": "CRITICAL | HIGH | MEDIUM | LOW",
            "category": "qms | compliance | technical | process | safety",
            "confidence": 0.95
        }}
    ],
    "secondary_keywords": [
        {{
            "term": "Sekundäres Keyword",
            "importance": "MEDIUM",
            "category": "general",
            "confidence": 0.8
        }}
    ],
    "qm_keywords": [
        {{
            "term": "QM-spezifisches Keyword",
            "importance": "HIGH",
            "category": "qms",
            "confidence": 0.9
        }}
    ],
    "sections_detected": ["Erkannte Hauptsektionen/Kapitel"],
    "has_tables": true,
    "has_figures": false,
    "has_appendices": true,
    "iso_standards_referenced": ["ISO 13485", "ISO 14971"],
    "regulatory_references": ["FDA 21 CFR 820", "MDR 2017/745"],
    "compliance_areas": ["Design Controls", "Risk Management", "Clinical Evaluation"],
    "compliance_level": "CRITICAL | HIGH | MEDIUM | LOW | NOT_APPLICABLE",
    "quality_scores": {{
        "overall": 0.85,
        "content_quality": 0.9,
        "completeness": 0.8,
        "clarity": 0.85,
        "structure": 0.9,
        "compliance_readiness": 0.8
    }},
    "interest_groups": ["Quality Assurance", "Regulatory Affairs", "R&D", "Manufacturing"],
    "ai_confidence": 0.9,
    "ai_methodology": "enhanced_multilayer_analysis"
}}

ANALYSIEREN SIE NUN DAS DOKUMENT UND GEBEN SIE NUR DAS JSON ZURÜCK:
"""

# ═══════════════════════════════════════════════════════════
# 🏷️ DOCUMENT TYPE CLASSIFICATION PROMPT
# ═══════════════════════════════════════════════════════════

DOCUMENT_TYPE_CLASSIFICATION_PROMPT = """
Klassifizieren Sie den Dokumenttyp basierend auf Inhalt und Struktur.

DOKUMENT-INHALT:
{document_content}

VERFÜGBARE DOKUMENTTYPEN:
- QM_MANUAL: Qualitätsmanagement-Handbuch
- QM_POLICY: QM-Richtlinie oder Policy
- QM_PROCEDURE: QM-Verfahrensanweisung
- WORK_INSTRUCTION: Arbeitsanweisung
- FORM: Formular oder Template
- ISO_STANDARD: ISO-Norm oder Standard
- DIN_STANDARD: DIN-Norm
- EN_STANDARD: EN-Norm
- FDA_GUIDANCE: FDA-Leitfaden
- MDR_DOCUMENT: MDR-Dokument
- SOP: Standard Operating Procedure
- PROTOCOL: Protokoll oder Prüfanweisung
- CHECKLIST: Checkliste
- AUDIT_REPORT: Audit-Bericht
- TEST_REPORT: Prüfbericht
- VALIDATION_REPORT: Validierungsbericht
- RISK_ASSESSMENT: Risikobewertung
- RISK_CONTROL: Risikokontrolle
- TEMPLATE: Vorlage
- OTHER: Sonstiges

ANTWORTEN SIE NUR MIT DEM DOKUMENTTYP:
"""

# ═══════════════════════════════════════════════════════════
# 🔍 KEYWORD EXTRACTION PROMPT
# ═══════════════════════════════════════════════════════════

KEYWORD_EXTRACTION_PROMPT = """
Extrahieren Sie relevante Keywords aus dem Dokument mit Wichtigkeitsbewertung.

DOKUMENT-INHALT:
{document_content}

KEYWORD-KATEGORIEN:
- qms: Qualitätsmanagement-Begriffe
- compliance: Regulatory/Compliance-Begriffe
- technical: Technische Fachbegriffe
- process: Prozess-bezogene Begriffe
- safety: Sicherheits-relevante Begriffe
- general: Allgemeine Begriffe

WICHTIGKEITSSTUFEN:
- CRITICAL: Must-have für Suche (Gewicht: 1.0)
- HIGH: Sehr wichtig (Gewicht: 0.8)
- MEDIUM: Standard wichtig (Gewicht: 0.6)
- LOW: Unterstützend (Gewicht: 0.4)

JSON-FORMAT:
{{
    "primary_keywords": [
        {{
            "term": "Hauptkeyword",
            "importance": "CRITICAL",
            "category": "qms",
            "confidence": 0.95
        }}
    ],
    "secondary_keywords": [
        {{
            "term": "Sekundäres Keyword",
            "importance": "MEDIUM",
            "category": "technical",
            "confidence": 0.8
        }}
    ],
    "qm_keywords": [
        {{
            "term": "QM-spezifisches Keyword",
            "importance": "HIGH",
            "category": "qms",
            "confidence": 0.9
        }}
    ]
}}

EXTRAHIEREN SIE NUR RELEVANTE KEYWORDS (MAX 15 PRO KATEGORIE):
"""

# ═══════════════════════════════════════════════════════════
# 📊 QUALITY ASSESSMENT PROMPT
# ═══════════════════════════════════════════════════════════

QUALITY_ASSESSMENT_PROMPT = """
Bewerten Sie die Qualität des Dokuments in verschiedenen Dimensionen.

DOKUMENT-INHALT:
{document_content}

BEWERTUNGSKRITERIEN (0.0 - 1.0):

CONTENT_QUALITY:
- Fachliche Korrektheit
- Vollständigkeit der Informationen
- Aktualität der Inhalte

COMPLETENESS:
- Vollständigkeit der Struktur
- Alle notwendigen Sektionen vorhanden
- Keine offensichtlichen Lücken

CLARITY:
- Verständlichkeit der Sprache
- Klare Strukturierung
- Eindeutige Formulierungen

STRUCTURE:
- Logischer Aufbau
- Konsistente Gliederung
- Professionelle Formatierung

COMPLIANCE_READINESS:
- Regulatory Compliance
- ISO-Konformität
- Audit-Bereitschaft

JSON-FORMAT:
{{
    "quality_scores": {{
        "overall": 0.85,
        "content_quality": 0.9,
        "completeness": 0.8,
        "clarity": 0.85,
        "structure": 0.9,
        "compliance_readiness": 0.8
    }},
    "assessment_notes": "Kurze Begründung der Bewertung"
}}

BEWERTEN SIE DAS DOKUMENT:
"""

# ═══════════════════════════════════════════════════════════
# 🏢 INTEREST GROUP ANALYSIS PROMPT
# ═══════════════════════════════════════════════════════════

INTEREST_GROUP_ANALYSIS_PROMPT = """
Identifizieren Sie relevante Interessensgruppen für dieses Dokument.

DOKUMENT-INHALT:
{document_content}

VERFÜGBARE INTERESSENSGRUPPEN:
- Quality Assurance: QS-Abteilung
- Regulatory Affairs: Regulatory-Abteilung
- R&D: Forschung & Entwicklung
- Manufacturing: Fertigung/Produktion
- Clinical Affairs: Klinische Abteilung
- Risk Management: Risikomanagement
- Training & Competence: Schulung & Kompetenz
- Supplier Management: Lieferantenmanagement
- Customer Service: Kundendienst
- Management: Geschäftsführung
- IT & Data Management: IT-Abteilung
- Legal & Compliance: Rechtsabteilung
- Sales & Marketing: Vertrieb & Marketing
- Project Management: Projektmanagement
- Maintenance: Wartung & Instandhaltung

JSON-FORMAT:
{{
    "interest_groups": ["Quality Assurance", "Regulatory Affairs", "R&D"],
    "relevance_reasoning": "Kurze Begründung der Relevanz"
}}

IDENTIFIZIEREN SIE RELEVANTE GRUPPEN:
"""

# ═══════════════════════════════════════════════════════════
# 🔬 COMPLIANCE ANALYSIS PROMPT
# ═══════════════════════════════════════════════════════════

COMPLIANCE_ANALYSIS_PROMPT = """
Analysieren Sie Compliance-Aspekte und regulatorische Referenzen.

DOKUMENT-INHALT:
{document_content}

SUCHEN SIE NACH:

ISO STANDARDS:
- ISO 13485 (Medical Device QMS)
- ISO 14971 (Risk Management)
- ISO 27001 (Information Security)
- ISO 9001 (Quality Management)

REGULATORY FRAMEWORKS:
- FDA 21 CFR 820 (QSR)
- FDA 21 CFR 11 (Electronic Records)
- MDR 2017/745 (Medical Device Regulation)
- IVDR 2017/746 (In Vitro Diagnostic Regulation)
- GDPR (Data Protection)

COMPLIANCE AREAS:
- Design Controls
- Risk Management
- Clinical Evaluation
- Post-Market Surveillance
- Vigilance
- Quality System
- Manufacturing Controls
- Labeling
- Sterilization
- Biocompatibility

JSON-FORMAT:
{{
    "iso_standards_referenced": ["ISO 13485", "ISO 14971"],
    "regulatory_references": ["FDA 21 CFR 820", "MDR 2017/745"],
    "compliance_areas": ["Design Controls", "Risk Management"],
    "compliance_level": "CRITICAL | HIGH | MEDIUM | LOW | NOT_APPLICABLE",
    "compliance_notes": "Spezifische Compliance-Hinweise"
}}

ANALYSIEREN SIE COMPLIANCE-ASPEKTE:
"""

# ═══════════════════════════════════════════════════════════
# 🧩 CHUNKING METADATA PROMPT
# ═══════════════════════════════════════════════════════════

CHUNKING_METADATA_PROMPT = """
Analysieren Sie diesen Dokumentabschnitt für erweiterte Chunk-Metadaten.

CHUNK-INHALT:
{chunk_content}

DOKUMENT-KONTEXT:
- Titel: {document_title}
- Typ: {document_type}
- Sektion: {section_title}

ANALYSIEREN SIE:
- Wichtigkeit für das Gesamtdokument
- Relevante Keywords
- Interessensgruppen
- Compliance-Bezüge

JSON-FORMAT:
{{
    "section_title": "Sektions-/Kapitelname",
    "paragraph_number": 1,
    "word_count": 150,
    "keywords": [
        {{
            "term": "Chunk-spezifisches Keyword",
            "importance": "HIGH",
            "category": "process",
            "confidence": 0.85
        }}
    ],
    "importance_score": 0.8,
    "interest_groups": ["Quality Assurance", "R&D"],
    "chunk_summary": "Kurze Zusammenfassung des Chunk-Inhalts"
}}

ANALYSIEREN SIE DEN CHUNK:
"""

# ═══════════════════════════════════════════════════════════
# 🎯 FEW-SHOT LEARNING EXAMPLES
# ═══════════════════════════════════════════════════════════

EXAMPLE_QM_PROCEDURE = """
BEISPIEL - QM-VERFAHRENSANWEISUNG:

Eingabe: "QM-Verfahrensanweisung VA-001: Dokumentenlenkung
Version 2.1 vom 15.03.2024

1. Zweck und Anwendungsbereich
Diese Verfahrensanweisung regelt die Erstellung, Prüfung, Freigabe und Lenkung von QM-Dokumenten...

2. Verantwortlichkeiten
- QM-Leiter: Freigabe aller QM-Dokumente
- Fachbereichsleiter: Erstellung und Prüfung..."

Ausgabe:
{{
    "title": "QM-Verfahrensanweisung VA-001: Dokumentenlenkung",
    "document_type": "QM_PROCEDURE",
    "version": "2.1",
    "main_category": "Quality Management",
    "sub_category": "Procedures",
    "process_area": "Document Control",
    "description": "Verfahrensanweisung zur Regelung der Erstellung, Prüfung, Freigabe und Lenkung von QM-Dokumenten",
    "primary_keywords": [
        {{
            "term": "Dokumentenlenkung",
            "importance": "CRITICAL",
            "category": "qms",
            "confidence": 0.95
        }}
    ],
    "compliance_level": "HIGH",
    "quality_scores": {{
        "overall": 0.85,
        "content_quality": 0.9,
        "completeness": 0.8,
        "clarity": 0.85,
        "structure": 0.9,
        "compliance_readiness": 0.85
    }}
}}
"""

# ═══════════════════════════════════════════════════════════
# 🔧 PROMPT CONFIGURATION
# ═══════════════════════════════════════════════════════════

PROMPT_CONFIG = {
    "temperature": 0.0,  # Maximale Konsistenz
    "max_tokens": 4000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "stop": None
}

# ═══════════════════════════════════════════════════════════
# 🎯 PROMPT BUILDER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def build_enhanced_extraction_prompt(document_content: str, 
                                    document_title: Optional[str] = None,
                                    document_type_hint: Optional[str] = None) -> str:
    """
    Erstellt Enhanced Metadata Extraction Prompt
    
    Args:
        document_content: Vollständiger Dokumentinhalt
        document_title: Optional - Dokumenttitel als Hint
        document_type_hint: Optional - Dokumenttyp als Hint
        
    Returns:
        str: Fertiger Prompt für AI-Model
    """
    prompt = ENHANCED_METADATA_EXTRACTION_PROMPT.format(
        document_content=document_content[:8000]  # Limit für Token-Effizienz
    )
    
    if document_title:
        prompt += f"\n\nHINWEIS - DOKUMENTTITEL: {document_title}"
    
    if document_type_hint:
        prompt += f"\nHINWEIS - DOKUMENTTYP: {document_type_hint}"
    
    return prompt

def build_chunking_prompt(chunk_content: str,
                         document_title: str,
                         document_type: str,
                         section_title: Optional[str] = None) -> str:
    """
    Erstellt Chunking Metadata Prompt
    
    Args:
        chunk_content: Chunk-Inhalt
        document_title: Dokumenttitel
        document_type: Dokumenttyp
        section_title: Optional - Sektionsname
        
    Returns:
        str: Fertiger Prompt für Chunk-Analyse
    """
    return CHUNKING_METADATA_PROMPT.format(
        chunk_content=chunk_content[:2000],  # Limit für Chunk-Analyse
        document_title=document_title,
        document_type=document_type,
        section_title=section_title or "Unbekannt"
    )

def build_quality_assessment_prompt(document_content: str) -> str:
    """Erstellt Quality Assessment Prompt"""
    return QUALITY_ASSESSMENT_PROMPT.format(
        document_content=document_content[:6000]
    )

def build_compliance_analysis_prompt(document_content: str) -> str:
    """Erstellt Compliance Analysis Prompt"""
    return COMPLIANCE_ANALYSIS_PROMPT.format(
        document_content=document_content[:6000]
    )

def build_interest_group_prompt(document_content: str) -> str:
    """Erstellt Interest Group Analysis Prompt"""
    return INTEREST_GROUP_ANALYSIS_PROMPT.format(
        document_content=document_content[:4000]
    )

def get_prompt_config() -> Dict[str, Any]:
    """Gibt optimierte Prompt-Konfiguration zurück"""
    return PROMPT_CONFIG.copy()

# ═══════════════════════════════════════════════════════════
# 🎯 PROMPT VALIDATION
# ═══════════════════════════════════════════════════════════

def validate_prompt_length(prompt: str, max_tokens: int = 8000) -> bool:
    """
    Validiert Prompt-Länge für Token-Limits
    
    Args:
        prompt: Zu validierender Prompt
        max_tokens: Maximum erlaubte Tokens (approximiert)
        
    Returns:
        bool: True wenn Prompt innerhalb Limits
    """
    # Approximation: 1 Token ≈ 4 Zeichen
    estimated_tokens = len(prompt) / 4
    return estimated_tokens <= max_tokens

def optimize_prompt_for_model(prompt: str, model_name: str = "gpt-4o-mini") -> str:
    """
    Optimiert Prompt für spezifisches AI-Model
    
    Args:
        prompt: Original-Prompt
        model_name: Name des AI-Models
        
    Returns:
        str: Optimierter Prompt
    """
    # Model-spezifische Optimierungen
    if "gpt-4o-mini" in model_name:
        # GPT-4o-mini bevorzugt strukturierte Prompts
        if not prompt.startswith("Sie sind ein Experte"):
            prompt = "Sie sind ein Experte für Qualitätsmanagement. " + prompt
    
    elif "gemini" in model_name:
        # Gemini bevorzugt klarere Instruktionen
        prompt = prompt.replace("ANTWORTEN SIE", "Bitte antworten Sie")
    
    return prompt

# ═══════════════════════════════════════════════════════════
# 🎯 EXPORT der wichtigsten Prompts
# ═══════════════════════════════════════════════════════════

__all__ = [
    "ENHANCED_METADATA_EXTRACTION_PROMPT",
    "DOCUMENT_TYPE_CLASSIFICATION_PROMPT", 
    "KEYWORD_EXTRACTION_PROMPT",
    "QUALITY_ASSESSMENT_PROMPT",
    "COMPLIANCE_ANALYSIS_PROMPT",
    "CHUNKING_METADATA_PROMPT",
    "PROMPT_CONFIG",
    "build_enhanced_extraction_prompt",
    "build_chunking_prompt",
    "build_quality_assessment_prompt",
    "build_compliance_analysis_prompt",
    "get_prompt_config",
    "validate_prompt_length",
    "optimize_prompt_for_model"
]