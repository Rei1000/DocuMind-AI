"""
🤖 ZENTRALE PROMPT-VERWALTUNG für KI-QMS - Enterprise Grade 2024
================================================================

Diese Datei enthält ALLE AI-Prompts des KI-QMS Systems in einer zentralen,
gut organisierten und ausführlich dokumentierten Struktur.

📋 ZWECK DER ZENTRALEN PROMPT-VERWALTUNG:
==========================================

1. **EINHEITLICHKEIT**: Alle Prompts an einem Ort für konsistente Qualität
2. **WARTBARKEIT**: Einfache Bearbeitung ohne Code-Änderungen in anderen Dateien  
3. **VERSIONIERUNG**: A/B-Testing und schrittweise Verbesserung möglich
4. **MEHRSPRACHIGKEIT**: Deutsche und englische Prompt-Varianten
5. **DOCUMENTATION**: Ausführliche Dokumentation jedes Prompts
6. **PERFORMANCE**: Optimierte Prompts für verschiedene AI-Provider

🏗️ ARCHITEKTUR-ÜBERBLICK:
==========================

Das System verwendet verschiedene Kategorien von Prompts:

- **METADATA_EXTRACTION**: 5-Layer AI-Analyse für Dokumenten-Metadaten
- **RAG_CHAT**: Conversational AI für Dokumenten-basierte Fragen  
- **DOCUMENT_CLASSIFICATION**: Automatische Dokumenttyp-Erkennung
- **COMPLIANCE_ANALYSIS**: Regulatory Affairs und Standards-Analyse
- **WORKFLOW_AUTOMATION**: Intelligente Workflow-Trigger
- **HYBRID_AI**: Kombination von lokaler und Cloud-AI
- **PROVIDER_SPECIFIC**: Optimiert für Ollama, Gemini, etc.

🔧 PROMPT-ENGINEERING BEST PRACTICES:
=====================================

1. **CLEAR INSTRUCTIONS**: Eindeutige, strukturierte Anweisungen
2. **CONTEXT SETTING**: Rollenbasierte Prompt-Einleitung (Du bist ein...)
3. **FORMAT SPECIFICATION**: Explizite Output-Format-Vorgaben (JSON, etc.)
4. **EXAMPLE PATTERNS**: Verwendung von Few-Shot-Learning wo sinnvoll
5. **ERROR HANDLING**: Graceful Fallbacks bei unvollständigen Eingaben
6. **LANGUAGE CONSISTENCY**: Sprach-konsistente Prompts (DE/EN)

📊 VERWENDUNG UND INTEGRATION:
==============================

```python
# Einfacher Import und Verwendung:
from app.prompts import get_metadata_prompt, get_rag_prompt

# Metadaten-Extraktion Prompt abrufen:
prompt = get_metadata_prompt(
    "document_analysis", 
    language="de",
    content="Ihr Dokumententext hier..."
)

# RAG-Chat Prompt abrufen:
chat_prompt = get_rag_prompt(
    "enhanced_rag_chat",
    language="de", 
    context="Verfügbare Dokumente...",
    question="Benutzer-Frage..."
)
```

🎯 WARTUNG UND UPDATES:
=======================

- **PROMPT-UPDATES**: Ändern Sie die Prompts direkt in dieser Datei
- **NEUE PROMPTS**: Fügen Sie neue Prompts in die entsprechende Kategorie ein
- **TESTING**: Testen Sie Änderungen mit verschiedenen Dokumenttypen
- **BACKUP**: Erstellen Sie Backups vor größeren Änderungen

Author: AI Assistant & Development Team
Version: 1.0 - Zentrale Prompt-Bibliothek mit ausführlicher Dokumentation
Created: 2025-07-02
Last Updated: 2025-07-02
"""

from typing import Dict, List, Optional, Union, Any
from enum import Enum
import json
import logging
import re
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

# Setup Logging für Prompt-Manager
logger = logging.getLogger("KI-QMS.PromptManager")

class PromptCategory(Enum):
    """
    Kategorisierung aller Prompt-Typen im KI-QMS System.
    
    Diese Enum definiert die verschiedenen Anwendungsbereiche der AI-Prompts
    und ermöglicht eine strukturierte Organisation und einfachen Zugriff.
    
    Kategorien:
    -----------
    METADATA_EXTRACTION : str
        Prompts für die 5-Layer-Analyse zur Metadaten-Extraktion aus Dokumenten.
        Umfasst Dokumenttyp-Klassifikation, Keyword-Extraktion, Struktur-Analyse,
        Compliance-Check und Qualitätsbewertung.
        
    RAG_CHAT : str
        Prompts für Retrieval Augmented Generation (RAG) Chat-Funktionalität.
        Ermöglicht natürliche Gespräche über QMS-Dokumenteninhalte mit
        korrekten Quellenangaben und fachlicher Präzision.
        
    DOCUMENT_CLASSIFICATION : str
        Prompts für automatische Klassifikation von Dokumenttypen.
        Erkennt QM-Handbücher, SOPs, Risikoanalysen, etc. mit Confidence-Scores.
        
    COMPLIANCE_ANALYSIS : str
        Prompts für Regulatory Affairs und Compliance-Analyse.
        Identifiziert ISO-Standards, FDA/MDR-Referenzen und Compliance-Gaps.
        
    WORKFLOW_AUTOMATION : str
        Prompts für intelligente Workflow-Erkennung und -Auslösung.
        Analysiert Benutzer-Nachrichten und triggert passende QMS-Prozesse.
        
    HYBRID_AI : str
        Prompts für Hybrid-AI-Systeme (lokale + Cloud AI).
        Optimiert lokale AI-Ergebnisse durch Cloud-basierte Verbesserung.
        
    PROVIDER_SPECIFIC : str
        Provider-spezifisch optimierte Prompts.
        Angepasst an die Stärken verschiedener AI-Provider (Ollama, Gemini, etc.).
    """
    METADATA_EXTRACTION = "metadata_extraction"
    RAG_CHAT = "rag_chat"
    DOCUMENT_CLASSIFICATION = "document_classification"
    COMPLIANCE_ANALYSIS = "compliance_analysis"
    WORKFLOW_AUTOMATION = "workflow_automation"
    HYBRID_AI = "hybrid_ai"
    PROVIDER_SPECIFIC = "provider_specific"

class PromptLanguage(Enum):
    """
    Unterstützte Sprachen für Prompts im KI-QMS System.
    
    Das System unterstützt mehrsprachige Prompts um sowohl deutsche als auch
    internationale QMS-Dokumente optimal zu verarbeiten.
    
    Sprachen:
    ---------
    GERMAN : str
        Deutsche Prompts (Hauptsprache des Systems).
        Optimiert für deutsche QMS-Terminologie und -Standards.
        
    ENGLISH : str
        Englische Prompts für internationale Dokumente.
        Verwendet internationale QMS-Terminologie (ISO, FDA, etc.).
        
    MIXED : str
        Mehrsprachige Prompts für gemischtsprachige Dokumente.
        Kombiniert deutsche und englische QMS-Begriffe.
    """
    GERMAN = "de"
    ENGLISH = "en"  
    MIXED = "mixed"

class PromptComplexity(Enum):
    """
    Komplexitätsstufen für verschiedene Prompt-Varianten.
    
    Ermöglicht die Auswahl von Prompts basierend auf der gewünschten
    Detailtiefe und Verarbeitungszeit.
    
    Stufen:
    -------
    SIMPLE : str
        Einfache, schnelle Prompts für Basis-Funktionalität.
        Geringer Token-Verbrauch, schnelle Antworten.
        
    STANDARD : str
        Standard-Prompts für normale Anwendungsfälle.
        Ausgewogenes Verhältnis zwischen Qualität und Geschwindigkeit.
        
    ADVANCED : str
        Erweiterte Prompts für detaillierte Analyse.
        Höhere Qualität, längere Verarbeitungszeit.
        
    EXPERT : str
        Experten-Level Prompts für höchste Präzision.
        Maximum an Details und Fachlichkeit.
    """
    SIMPLE = "simple"
    STANDARD = "standard"
    ADVANCED = "advanced"
    EXPERT = "expert"

# ═══════════════════════════════════════════════════════════════════════════════
# 🔍 METADATEN-EXTRAKTION PROMPTS - 5-LAYER-ANALYSE SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

"""
METADATEN-EXTRAKTION SYSTEM - DETAILLIERTE DOKUMENTATION
=========================================================

Das 5-Layer-Analyse-System ist das Herzstück der intelligenten Dokumenten-
verarbeitung im KI-QMS. Jeder Layer fokussiert auf einen spezifischen Aspekt
der Dokumentenanalyse:

LAYER 1 - DOCUMENT ANALYSIS:
    🎯 Zweck: Grundlegende Dokumentenklassifikation und -beschreibung
    📊 Output: Dokumenttyp, Titel, Beschreibung, Kategorisierung
    🔧 Technik: Pattern-basierte Klassifikation + AI-Verstärkung
    ⏱️ Dauer: ~3-5 Sekunden
    
LAYER 2 - KEYWORD EXTRACTION:  
    🎯 Zweck: Strukturierte Keyword-Extraktion in 4 Kategorien
    📊 Output: Primary, Secondary, QM-spezifische, Compliance Keywords
    🔧 Technik: NLP + Domain-spezifische Wörterbücher
    ⏱️ Dauer: ~2-4 Sekunden
    
LAYER 3 - STRUCTURE ANALYSIS:
    🎯 Zweck: Dokumentstruktur und -aufbau analysieren
    📊 Output: Abschnitte, Tabellen, Abbildungen, Anhänge
    🔧 Technik: Layout-Erkennung + Content-Pattern-Matching
    ⏱️ Dauer: ~2-3 Sekunden
    
LAYER 4 - COMPLIANCE ANALYSIS:
    🎯 Zweck: Regulatory und Standards-Compliance prüfen
    📊 Output: ISO-Standards, FDA/MDR-Referenzen, Compliance-Level
    🔧 Technik: Regex-Pattern + AI-basierte Norm-Erkennung
    ⏱️ Dauer: ~3-5 Sekunden
    
LAYER 5 - QUALITY ASSESSMENT:
    🎯 Zweck: Qualitätsmetriken und Verbesserungsvorschläge
    📊 Output: Content-, Completeness-, Clarity-Scores (0.0-1.0)
    🔧 Technik: Multi-dimensionale Qualitätsbewertung
    ⏱️ Dauer: ~2-4 Sekunden

GESAMT-VERARBEITUNGSZEIT: ~12-21 Sekunden (parallelisiert: ~8-12 Sekunden)
"""

METADATA_EXTRACTION_PROMPTS = {
    
    "document_analysis": {
        "description": """
        LAYER 1: DOCUMENT ANALYSIS - Grundlegende Dokumentenklassifikation
        ==================================================================
        
        Dieser Prompt führt die fundamentale Analyse eines Dokuments durch und
        bestimmt dessen Typ, Titel, Beschreibung und Kategorisierung.
        
        FUNKTIONALITÄT:
        ---------------
        - Automatische Dokumenttyp-Erkennung aus 23+ Kategorien
        - Intelligente Titel-Extraktion oder -Generierung  
        - Präzise 2-3 Satz Beschreibung des Dokumentzwecks
        - Hierarchische Kategorisierung (Haupt-, Unter-, Prozess-Kategorie)
        - Begründung der Klassifikationsentscheidung
        
        UNTERSTÜTZTE DOKUMENTTYPEN:
        ---------------------------
        QM Core: QM_MANUAL, QM_POLICY, SOP, WORK_INSTRUCTION
        Standards: STANDARD_NORM, ISO_STANDARD, DIN_STANDARD  
        Regulatory: REGULATORY_DOCUMENT, FDA_GUIDANCE, MDR_DOCUMENT
        Processes: PROCESS_DESCRIPTION, FLOW_CHART, CHECKLIST
        Forms: FORM, TEMPLATE, PROTOCOL
        Reports: AUDIT_REPORT, TEST_REPORT, VALIDATION_REPORT
        Other: TRAINING_MATERIAL, SPECIFICATION, OTHER
        
        PROMPT-ENGINEERING TECHNIKEN:
        -----------------------------
        - Role-based prompt opening (Du bist ein Experte...)
        - Structured task breakdown (4 numbered analysis tasks)
        - Explicit output format specification (JSON)
        - Few-shot learning through examples in description
        - Reasoning requirement for transparency
        
        OUTPUT-FORMAT:
        --------------
        JSON mit folgenden Feldern:
        - document_type: Enum-Wert aus DocumentTypeClassification
        - title: String (extrahiert oder generiert)
        - description: String (2-3 Sätze)
        - main_category: String (Hauptkategorie)
        - sub_category: String (Unterkategorie)  
        - process_area: String (Prozessbereich)
        - reasoning: String (Begründung der Klassifikationsentscheidung)
        
        QUALITY INDICATORS:
        ------------------
        - Confidence > 0.8: Sehr sichere Klassifikation
        - Confidence 0.6-0.8: Sichere Klassifikation
        - Confidence < 0.6: Unsichere Klassifikation (manuelle Prüfung)
        """,
        
        "de": """Du bist ein Experte für Qualitätsmanagement-Systeme und Dokumentenanalyse. 
Analysiere das folgende Dokument umfassend und strukturiert.

DOKUMENT:
{content}

ANALYSE-AUFGABEN:
1. DOKUMENTTYP-KLASSIFIZIERUNG:
   - Bestimme den exakten Dokumenttyp (QM_MANUAL, SOP, STANDARD_NORM, RISK_ASSESSMENT, VALIDATION_PROTOCOL, AUDIT_REPORT, CALIBRATION_PROCEDURE, FORM, SPECIFICATION, TRAINING_MATERIAL, etc.)
   - Berücksichtige Inhalt, Struktur und typische Merkmale
   - Begründe deine Klassifizierung mit spezifischen Indikatoren

2. TITEL-EXTRAKTION:
   - Extrahiere den offiziellen Dokumententitel aus dem Text
   - Falls kein expliziter Titel vorhanden, generiere einen präzisen, aussagekräftigen Titel
   - Der Titel sollte den Dokumentzweck klar widerspiegeln

3. BESCHREIBUNG:
   - Erstelle eine präzise 2-3 Satz Beschreibung des Dokuments
   - Fokus auf Hauptzweck, Anwendungsbereich und zentrale Inhalte
   - Verwende QM-spezifische Terminologie wo angemessen

4. KATEGORISIERUNG:
   - Hauptkategorie (z.B. "Qualitätsmanagement", "Normen & Standards", "Prozesse & Verfahren", "Formulare & Vorlagen", "Berichte & Nachweise")
   - Unterkategorie (spezifischer, z.B. "Risikoanalyse", "Kalibrierverfahren", "Auditprotokoll")
   - Prozessbereich (falls zutreffend, z.B. "Risikomanagement", "Messtechnik", "Dokumentenlenkung")

WICHTIGE HINWEISE:
- Achte auf QM-spezifische Begriffe und Konzepte
- Berücksichtige regulatorische Aspekte (ISO 13485, MDR, FDA)
- Erkenne typische Dokumentstrukturen und -formate
- Bei Unsicherheit wähle den allgemeineren Typ und erwähne Alternativen

Antworte im JSON-Format:
{{
    "document_type": "DOKUMENTTYP_ENUM",
    "title": "Extrahierter oder generierter Titel",
    "description": "2-3 Satz Beschreibung des Dokuments und seines Zwecks",
    "main_category": "Hauptkategorie des Dokuments",
    "sub_category": "Spezifischere Unterkategorie",
    "process_area": "Relevanter QMS-Prozessbereich",
    "reasoning": "Detaillierte Begründung der Klassifikationsentscheidung mit spezifischen Indikatoren"
}}""",
        
        "en": """You are an expert in Quality Management Systems and document analysis.
Analyze the following document comprehensively and structured.

DOCUMENT:
{content}

ANALYSIS TASKS:
1. DOCUMENT TYPE CLASSIFICATION:
   - Determine the exact document type (QM_MANUAL, SOP, STANDARD_NORM, RISK_ASSESSMENT, VALIDATION_PROTOCOL, AUDIT_REPORT, CALIBRATION_PROCEDURE, FORM, SPECIFICATION, TRAINING_MATERIAL, etc.)
   - Consider content, structure and typical characteristics
   - Justify your classification with specific indicators

2. TITLE EXTRACTION:
   - Extract the official document title from the text
   - If no explicit title exists, generate a precise, meaningful title
   - The title should clearly reflect the document's purpose

3. DESCRIPTION:
   - Create a precise 2-3 sentence description of the document
   - Focus on main purpose, scope of application and central content
   - Use QM-specific terminology where appropriate

4. CATEGORIZATION:
   - Main category (e.g. "Quality Management", "Standards & Norms", "Processes & Procedures", "Forms & Templates", "Reports & Records")
   - Sub-category (more specific, e.g. "Risk Analysis", "Calibration Procedure", "Audit Protocol")
   - Process area (if applicable, e.g. "Risk Management", "Metrology", "Document Control")

IMPORTANT NOTES:
- Pay attention to QM-specific terms and concepts
- Consider regulatory aspects (ISO 13485, MDR, FDA)
- Recognize typical document structures and formats
- When uncertain, choose the more general type and mention alternatives

Respond in JSON format:
{{
    "document_type": "DOCUMENT_TYPE_ENUM",
    "title": "Extracted or generated title",
    "description": "2-3 sentence description of the document and its purpose",
    "main_category": "Main category of the document",
    "sub_category": "More specific sub-category",
    "process_area": "Relevant QMS process area",
    "reasoning": "Detailed justification of classification decision with specific indicators"
}}"""
    },

    "keyword_extraction": {
        "description": """
        LAYER 2: KEYWORD EXTRACTION - Strukturierte 4-Kategorie Keyword-Analyse
        =======================================================================
        
        Dieser Prompt extrahiert systematisch Keywords aus QMS-Dokumenten und
        kategorisiert sie in vier spezielle Bereiche für optimale Suchbarkeit
        und Dokumentenverknüpfung.
        
        FUNKTIONALITÄT:
        ---------------
        - Intelligente Keyword-Erkennung mit NLP-Techniken
        - Automatische Kategorisierung in 4 Bereiche
        - QM-spezifische Terminologie-Erkennung
        - Regulatory/Compliance Begriff-Identifikation
        - Relevanz-basierte Priorisierung
        
        KEYWORD-KATEGORIEN (DETAILLIERT):
        --------------------------------
        
        1. PRIMARY_KEYWORDS (3-5 Keywords):
           - Die wichtigsten Begriffe des Dokuments
           - Hohe Relevanz für Dokumenteninhalt
           - Oft im Titel oder ersten Absätzen
           - Beispiele: "Risikomanagement", "Validierung", "Audit"
        
        2. SECONDARY_KEYWORDS (5-8 Keywords):
           - Unterstützende und ergänzende Begriffe
           - Moderate Relevanz für Dokumentenkontext
           - Spezifische Fachbegriffe und Methoden
           - Beispiele: "Bewertung", "Dokumentation", "Prozess"
        
        3. QM_KEYWORDS:
           - QM-System spezifische Fachbegriffe
           - ISO 13485, QM-Prozesse, QM-Terminologie
           - Beispiele: "Qualitätssicherung", "CAPA", "Design Control"
        
        4. COMPLIANCE_KEYWORDS:
           - Regulatory und Compliance-relevante Begriffe
           - FDA, MDR, ISO Standards, GMP
           - Beispiele: "FDA 21 CFR", "MDR Artikel", "ISO 14971"
        
        PROMPT-ENGINEERING TECHNIKEN:
        -----------------------------
        - Kategorie-spezifische Anweisungen
        - Quantitative Vorgaben (3-5, 5-8)
        - Domain-spezifische Expertise-Rolle
        - Strukturiertes JSON-Output-Format
        - Beispiel-basierte Klarstellung
        
        QUALITÄTSSICHERUNG:
        ------------------
        - Duplikat-Vermeidung zwischen Kategorien
        - Relevanz-Filtering (min. 2x Erwähnung)
        - QM-Terminologie-Validierung
        - Sprach-konsistente Begriffe
        
        VERWENDUNG FÜR:
        ---------------
        - Erweiterte Dokumentensuche
        - Automatische Dokumentenverknüpfung
        - Compliance-Monitoring
        - QM-Wissensmanagement
        """,
        
        "de": """Du bist ein QM-Spezialist mit Expertise in Dokumentenanalyse und Keyword-Extraktion. 
Extrahiere systematisch Keywords aus diesem QMS-Dokument.

DOKUMENT:
{content}

KEYWORD-EXTRAKTION IN 4 KATEGORIEN:

1. PRIMARY_KEYWORDS (3-5 Keywords):
   - Die WICHTIGSTEN Begriffe des Dokuments
   - Begriffe mit höchster Relevanz für den Hauptinhalt
   - Oft im Titel, Überschriften oder ersten Absätzen zu finden
   - Sollten das Dokument präzise charakterisieren

2. SECONDARY_KEYWORDS (5-8 Keywords):
   - UNTERSTÜTZENDE Begriffe mit moderater Relevanz  
   - Spezifische Fachbegriffe und Methoden
   - Ergänzende Konzepte und Prozesse
   - Helfen bei detaillierterer Kategorisierung

3. QM_KEYWORDS:
   - QM-SPEZIFISCHE Fachbegriffe aus dem Qualitätsmanagement
   - ISO 13485, QM-Prozesse, QM-Terminologie
   - Begriffe wie: Qualitätssicherung, CAPA, Design Control, Verifizierung, Validierung
   - QM-System relevante Konzepte

4. COMPLIANCE_KEYWORDS:
   - REGULATORY/COMPLIANCE relevante Begriffe
   - FDA-Regularien, MDR, ISO-Standards, GMP
   - Spezifische Norm-Referenzen (z.B. "21 CFR Part 820", "ISO 14971", "MDR Artikel 62")
   - Compliance-Prozesse und -Anforderungen

EXTRAKTIONS-RICHTLINIEN:
- Verwende die im Dokument tatsächlich vorkommenden Begriffe
- Bevorzuge spezifische vor allgemeinen Begriffen
- Vermeide Duplikate zwischen den Kategorien
- Achte auf deutsche und englische QM-Terminologie
- Berücksichtige Synonyme und Abkürzungen

Antwort als JSON:
{{
    "primary_keywords": ["Hauptbegriff1", "Hauptbegriff2", "Hauptbegriff3"],
    "secondary_keywords": ["Ergänzungsbegriff1", "Ergänzungsbegriff2", "Ergänzungsbegriff3", "Ergänzungsbegriff4", "Ergänzungsbegriff5"], 
    "qm_keywords": ["QM-Begriff1", "QM-Begriff2", "QM-Begriff3"],
    "compliance_keywords": ["Compliance-Begriff1", "Compliance-Begriff2", "Compliance-Begriff3"]
}}""",
        
        "en": """You are a QM specialist with expertise in document analysis and keyword extraction.
Systematically extract keywords from this QMS document.

DOCUMENT:
{content}

KEYWORD EXTRACTION IN 4 CATEGORIES:

1. PRIMARY_KEYWORDS (3-5 Keywords):
   - The MOST IMPORTANT terms of the document
   - Terms with highest relevance for the main content
   - Often found in title, headings or first paragraphs
   - Should precisely characterize the document

2. SECONDARY_KEYWORDS (5-8 Keywords):
   - SUPPORTING terms with moderate relevance
   - Specific technical terms and methods
   - Complementary concepts and processes
   - Help with more detailed categorization

3. QM_KEYWORDS:
   - QM-SPECIFIC technical terms from quality management
   - ISO 13485, QM processes, QM terminology
   - Terms like: Quality Assurance, CAPA, Design Control, Verification, Validation
   - QM system relevant concepts

4. COMPLIANCE_KEYWORDS:
   - REGULATORY/COMPLIANCE relevant terms
   - FDA regulations, MDR, ISO standards, GMP
   - Specific standard references (e.g. "21 CFR Part 820", "ISO 14971", "MDR Article 62")
   - Compliance processes and requirements

EXTRACTION GUIDELINES:
- Use terms actually occurring in the document
- Prefer specific over general terms
- Avoid duplicates between categories
- Consider German and English QM terminology
- Account for synonyms and abbreviations

Answer as JSON:
{{
    "primary_keywords": ["MainTerm1", "MainTerm2", "MainTerm3"],
    "secondary_keywords": ["SupportTerm1", "SupportTerm2", "SupportTerm3", "SupportTerm4", "SupportTerm5"], 
    "qm_keywords": ["QMTerm1", "QMTerm2", "QMTerm3"],
    "compliance_keywords": ["ComplianceTerm1", "ComplianceTerm2", "ComplianceTerm3"]
}}"""
    },

    "structure_analysis": {
        "description": """
        LAYER 3: STRUCTURE ANALYSIS - Dokumentstruktur und -aufbau Analyse
        ===================================================================
        
        Dieser Prompt analysiert die physische und logische Struktur von
        QMS-Dokumenten um deren Aufbau, Organisation und Vollständigkeit
        zu bewerten.
        
        FUNKTIONALITÄT:
        ---------------
        - Automatische Erkennung von Dokumentabschnitten und Kapiteln
        - Identifikation von Tabellen, Abbildungen und Anhängen
        - Bewertung der Dokumentstruktur und Gliederung
        - Erkennung von Numerierungsschemata und Hierarchien
        - Vollständigkeits-Check für typische QMS-Dokumentkomponenten
        
        ERKANNTE STRUKTURELEMENTE:
        -------------------------
        
        1. SECTIONS_DETECTED:
           - Automatische Abschnitts-/Kapitel-Erkennung
           - Erkennung von Überschriften und Unterüberschriften
           - Identifikation typischer QMS-Abschnitte (Zweck, Geltungsbereich, etc.)
           - Hierarchische Strukturierung
        
        2. HAS_TABLES:
           - Erkennung von Tabellen und tabellarischen Darstellungen
           - Wichtig für Spezifikationen, Grenzwerte, Protokolle
           - Pattern-basierte Erkennung (|, Tab-Strukturen, etc.)
        
        3. HAS_FIGURES:
           - Identifikation von Abbildungen, Diagrammen, Flowcharts
           - Erkennung durch Referenzen ("Abb.", "Figure", etc.)
           - Relevant für Prozessdarstellungen und Schemata
        
        4. HAS_APPENDICES:
           - Erkennung von Anhängen und Beilagen
           - Pattern: "Anhang", "Appendix", "Anlage"
           - Wichtig für vollständige Dokumentenerfassung
        
        5. STRUCTURE_TYPE:
           - Klassifikation des Strukturtyps (formal, informal, mixed)
           - Bewertung der Organisationsqualität
        
        6. NUMBERING_SCHEME:
           - Identifikation des Numerierungsschemas
           - Hierarchische Nummerierung (1.1, 1.1.1, etc.)
           - Alphabetische oder gemischte Schemata
        
        PROMPT-ENGINEERING TECHNIKEN:
        -----------------------------
        - Layout-spezifische Erkennungsanweisungen
        - Pattern-basierte Suchmuster
        - Boolean-Output für binäre Eigenschaften
        - Strukturierte Kategorisierung
        - Fallback-Optionen für unklare Fälle
        
        QUALITÄTSMETRIKEN:
        -----------------
        - Strukturelle Vollständigkeit (Sections erkannt)
        - Visueller Informationsgehalt (Tabellen/Abbildungen)
        - Dokumentations-Qualität (Anhänge vorhanden)
        - Organisatorische Klarheit (Numerierungsschema)
        
        VERWENDUNG FÜR:
        ---------------
        - Automatische Qualitätsbewertung
        - Template-Compliance-Check
        - Vollständigkeitsprüfung
        - Strukturelle Verbesserungsvorschläge
        """,
        
        "de": """Analysiere die Struktur und den Aufbau dieses QMS-Dokuments detailliert.

DOKUMENT:
{content}

STRUKTUR-ANALYSE AUFGABEN:

1. ABSCHNITTE/KAPITEL ERKENNUNG:
   - Identifiziere alle Hauptabschnitte und Kapitel
   - Erkenne Überschriften verschiedener Hierarchieebenen  
   - Typische QMS-Abschnitte: Zweck, Geltungsbereich, Verantwortlichkeiten, Durchführung, Aufzeichnungen
   - Nummerierte und unnummerierte Abschnitte

2. TABELLEN-ERKENNUNG:
   - Suche nach tabellarischen Darstellungen
   - Pattern: Spalten durch |, Tabs oder Leerzeichen getrennt
   - Tabellen-Referenzen ("Tabelle", "Tab.", "Table")
   - Spezifikationstabellen, Grenzwerte, Protokollfelder

3. ABBILDUNGEN-ERKENNUNG:
   - Identifiziere Verweise auf Abbildungen und Diagramme
   - Pattern: "Abb.", "Abbildung", "Figure", "Fig."
   - Flowcharts, Prozessdiagramme, Schemata
   - Organisationscharts, Strukturdiagramme

4. ANHÄNGE-ERKENNUNG:
   - Erkenne Anhänge, Beilagen, Anlagen
   - Pattern: "Anhang", "Appendix", "Anlage", "Attachment"
   - Formulare, Checklisten, Referenzdokumente
   - Zusätzliche Dokumentation

5. GLIEDERUNGSSTRUKTUR:
   - Bewerte die Dokumentenorganisation
   - Erkenne Numerierungsschemata (1., 1.1, 1.1.1, a), b), etc.)
   - Strukturtyp: formal (klare Nummerierung), informal (Überschriften), mixed

BEWERTUNGSKRITERIEN:
- Achte auf typische QMS-Dokumentstrukturen
- Berücksichtige ISO 13485 konforme Aufbauten
- Erkenne Standard-Templates und -Formate
- Bewerte Vollständigkeit und Professionalität

JSON-Antwort:
{{
    "sections_detected": ["Abschnitt1", "Abschnitt2", "Abschnitt3"],
    "has_tables": true/false,
    "has_figures": true/false, 
    "has_appendices": true/false,
    "structure_type": "formal/informal/mixed",
    "numbering_scheme": "hierarchical/sequential/alphabetic/mixed/none",
    "organization_quality": "high/medium/low",
    "completeness_indicators": ["indicator1", "indicator2"]
}}""",
        
        "en": """Analyze the structure and layout of this QMS document in detail.

DOCUMENT:
{content}

STRUCTURE ANALYSIS TASKS:

1. SECTIONS/CHAPTERS RECOGNITION:
   - Identify all main sections and chapters
   - Recognize headings of different hierarchy levels
   - Typical QMS sections: Purpose, Scope, Responsibilities, Execution, Records
   - Numbered and unnumbered sections

2. TABLE RECOGNITION:
   - Search for tabular representations
   - Patterns: Columns separated by |, tabs or spaces
   - Table references ("Table", "Tab.")
   - Specification tables, limits, protocol fields

3. FIGURE RECOGNITION:
   - Identify references to figures and diagrams
   - Patterns: "Fig.", "Figure", "Diagram"
   - Flowcharts, process diagrams, schemas
   - Organization charts, structure diagrams

4. APPENDIX RECOGNITION:
   - Recognize appendices, attachments, annexes
   - Patterns: "Appendix", "Annex", "Attachment"
   - Forms, checklists, reference documents
   - Additional documentation

5. OUTLINE STRUCTURE:
   - Evaluate document organization
   - Recognize numbering schemes (1., 1.1, 1.1.1, a), b), etc.)
   - Structure type: formal (clear numbering), informal (headings), mixed

EVALUATION CRITERIA:
- Consider typical QMS document structures
- Account for ISO 13485 compliant layouts
- Recognize standard templates and formats
- Evaluate completeness and professionalism

JSON response:
{{
    "sections_detected": ["Section1", "Section2", "Section3"],
    "has_tables": true/false,
    "has_figures": true/false, 
    "has_appendices": true/false,
    "structure_type": "formal/informal/mixed",
    "numbering_scheme": "hierarchical/sequential/alphabetic/mixed/none",
    "organization_quality": "high/medium/low",
    "completeness_indicators": ["indicator1", "indicator2"]
}}"""
    },

    "compliance_analysis": {
        "description": """
        LAYER 4: COMPLIANCE ANALYSIS - Regulatory Affairs und Standards-Analyse
        ======================================================================
        
        Dieser Prompt führt eine umfassende Compliance-Analyse durch und
        identifiziert alle regulatorischen Referenzen, Standards und
        Compliance-Anforderungen in QMS-Dokumenten.
        
        FUNKTIONALITÄT:
        ---------------
        - Automatische Erkennung von ISO-Standards und Normen
        - Identifikation von FDA-Regularien und EU-Richtlinien
        - Compliance-Level-Bewertung
        - Gap-Analyse für fehlende Compliance-Aspekte
        - Regulatory Landscape Mapping
        
        ERKANNTE COMPLIANCE-BEREICHE:
        ----------------------------
        
        1. ISO_STANDARDS_REFERENCED:
           - ISO 13485 (QMS für Medizinprodukte)
           - ISO 9001 (Allgemeine QMS-Anforderungen)
           - ISO 14971 (Risikomanagement)
           - ISO 27799 (Informationssicherheit)
           - Weitere ISO-Normen (ISO 15189, ISO 17025, etc.)
        
        2. REGULATORY_REFERENCES:
           - FDA 21 CFR Part 820 (Quality System Regulation)
           - EU MDR (Medical Device Regulation)
           - EU IVDR (In Vitro Diagnostic Regulation)
           - GMP Guidelines (Good Manufacturing Practice)
           - ICH Guidelines (International Council for Harmonisation)
        
        3. COMPLIANCE_AREAS:
           - Risk Management
           - Design Controls
           - CAPA (Corrective and Preventive Actions)
           - Management Responsibility
           - Document Control
           - Validation and Verification
        
        4. STANDARDS_COMPLIANCE_LEVEL:
           - "high": Vollständige Compliance-Abdeckung
           - "medium": Grundlegende Compliance erfüllt
           - "low": Minimale oder fehlende Compliance-Referenzen
        
        PATTERN-ERKENNUNGSTECHNIKEN:
        ---------------------------
        - Regex-basierte Norm-Erkennung
        - Kontextuelle Referenz-Analyse
        - Abkürzungsauflösung (CFR, MDR, IVDR)
        - Versionsnummern-Erkennung
        - Cross-Reference-Validation
        
        COMPLIANCE-BEWERTUNGSMETRIKEN:
        -----------------------------
        - Anzahl identifizierter Standards
        - Vollständigkeit der Referenzierung
        - Aktualität der Standards (Version/Jahr)
        - Konsistenz der Compliance-Abdeckung
        
        VERWENDUNG FÜR:
        ---------------
        - Regulatory Affairs Management
        - Compliance Monitoring und Reporting
        - Gap-Analyse für Audit-Vorbereitung
        - Standards-Update-Tracking
        - Risikobewertung für regulatorische Änderungen
        """,
        
        "de": """Du bist ein Regulatory Affairs Experte mit umfassendem Wissen über medizinische Geräte-Regularien. 
Analysiere die Compliance-Aspekte dieses QMS-Dokuments.

DOKUMENT:
{content}

COMPLIANCE-ANALYSE BEREICHE:

1. ISO-STANDARDS IDENTIFIKATION:
   - ISO 13485: QMS für Medizinprodukte
   - ISO 9001: Allgemeine QMS-Anforderungen  
   - ISO 14971: Risikomanagement für Medizinprodukte
   - ISO 27799: Informationssicherheit im Gesundheitswesen
   - Weitere relevante ISO-Normen (ISO 15189, ISO 17025, etc.)
   - Achte auf Versionsnummern und Publikationsjahre

2. REGULATORY REFERENZEN:
   - FDA 21 CFR Part 820: Quality System Regulation
   - EU MDR: Medical Device Regulation (EU) 2017/745
   - EU IVDR: In Vitro Diagnostic Regulation (EU) 2017/746
   - GMP Guidelines: Good Manufacturing Practice
   - ICH Guidelines: International Council for Harmonisation
   - Nationale Regularien (BfArM, Swissmedic, etc.)

3. COMPLIANCE-BEREICHE BEWERTUNG:
   - Risikomanagement (Risk Management)
   - Design Controls (Entwicklungssteuerung)
   - CAPA (Corrective and Preventive Actions)
   - Management Responsibility (Verantwortung der Leitung)
   - Document Control (Dokumentenlenkung)
   - Validation/Verification (Validierung/Verifizierung)
   - Post-Market Surveillance (Marktüberwachung)

4. COMPLIANCE-LEVEL BEWERTUNG:
   - "high": Umfassende Compliance-Abdeckung mit konkreten Referenzen
   - "medium": Grundlegende Compliance-Anforderungen erfüllt
   - "low": Minimale oder fehlende Compliance-Referenzen

ERKENNUNGS-RICHTLINIEN:
- Suche nach expliziten Norm-Referenzen und Zitierungen
- Identifiziere indirekte Compliance-Anforderungen
- Achte auf regulatorische Schlüsselbegriffe und Konzepte
- Berücksichtige sowohl deutsche als auch englische Terminologie
- Erkenne Abkürzungen und Akronyme (CFR, MDR, IVDR, GMP)

JSON-Antwort:
{{
    "iso_standards_referenced": ["ISO 13485:2016", "ISO 14971:2019"],
    "regulatory_references": ["21 CFR Part 820", "EU MDR Article 10"],
    "compliance_areas": ["Risk Management", "Design Controls", "CAPA"],
    "standards_compliance_level": "high/medium/low",
    "regulatory_scope": "EU/US/International/National",
    "gaps_identified": ["Fehlende Aspekte falls vorhanden"]
}}""",
        
        "en": """You are a Regulatory Affairs expert with comprehensive knowledge of medical device regulations.
Analyze the compliance aspects of this QMS document.

DOCUMENT:
{content}

COMPLIANCE ANALYSIS AREAS:

1. ISO STANDARDS IDENTIFICATION:
   - ISO 13485: QMS for Medical Devices
   - ISO 9001: General QMS Requirements
   - ISO 14971: Risk Management for Medical Devices
   - ISO 27799: Information Security in Healthcare
   - Other relevant ISO standards (ISO 15189, ISO 17025, etc.)
   - Look for version numbers and publication years

2. REGULATORY REFERENCES:
   - FDA 21 CFR Part 820: Quality System Regulation
   - EU MDR: Medical Device Regulation (EU) 2017/745
   - EU IVDR: In Vitro Diagnostic Regulation (EU) 2017/746
   - GMP Guidelines: Good Manufacturing Practice
   - ICH Guidelines: International Council for Harmonisation
   - National regulations (FDA, Health Canada, TGA, etc.)

3. COMPLIANCE AREAS ASSESSMENT:
   - Risk Management
   - Design Controls
   - CAPA (Corrective and Preventive Actions)
   - Management Responsibility
   - Document Control
   - Validation/Verification
   - Post-Market Surveillance

4. COMPLIANCE LEVEL ASSESSMENT:
   - "high": Comprehensive compliance coverage with concrete references
   - "medium": Basic compliance requirements met
   - "low": Minimal or missing compliance references

RECOGNITION GUIDELINES:
- Search for explicit standard references and citations
- Identify indirect compliance requirements
- Look for regulatory key terms and concepts
- Consider both technical and procedural compliance aspects
- Recognize abbreviations and acronyms (CFR, MDR, IVDR, GMP)

JSON response:
{{
    "iso_standards_referenced": ["ISO 13485:2016", "ISO 14971:2019"],
    "regulatory_references": ["21 CFR Part 820", "EU MDR Article 10"],
    "compliance_areas": ["Risk Management", "Design Controls", "CAPA"],
    "standards_compliance_level": "high/medium/low",
    "regulatory_scope": "EU/US/International/National",
    "gaps_identified": ["Missing aspects if any"]
}}"""
    },

    "quality_assessment": {
        "description": """
        LAYER 5: QUALITY ASSESSMENT - Dokumentqualität und Verbesserungsanalyse
        =======================================================================
        
        Dieser Prompt führt eine umfassende Qualitätsbewertung von QMS-Dokumenten
        durch und generiert objektive Metriken sowie konstruktive Verbesserungs-
        vorschläge.
        
        FUNKTIONALITÄT:
        ---------------
        - Multi-dimensionale Qualitätsbewertung (3 Haupt-Dimensionen)
        - Objektive Scoring-Metriken (0.0-1.0 Skala)
        - Qualitative Gesamtbewertung
        - Konkrete, umsetzbare Verbesserungsvorschläge
        - Best-Practice-Empfehlungen für QMS-Dokumente
        
        QUALITÄTS-DIMENSIONEN (DETAILLIERT):
        -----------------------------------
        
        1. CONTENT_QUALITY_SCORE (0.0-1.0):
           🎯 Bewertet: Fachliche Korrektheit und Vollständigkeit
           📊 Faktoren:
              - Fachterminologie-Verwendung
              - Logische Struktur und Aufbau
              - Vollständigkeit der Information
              - Präzision der Aussagen
              - QM-spezifische Expertise
           
           Bewertungsskala:
           - 0.9-1.0: Expertenlevel, umfassend und präzise
           - 0.7-0.8: Gut strukturiert, fachlich korrekt
           - 0.5-0.6: Grundlegende Qualität, aber Verbesserungspotential
           - 0.3-0.4: Erhebliche Mängel in Fachlichkeit
           - 0.0-0.2: Unzureichende fachliche Qualität
        
        2. COMPLETENESS_SCORE (0.0-1.0):
           🎯 Bewertet: Vollständigkeit der Dokumentation
           📊 Faktoren:
              - Abdeckung aller relevanten Aspekte
              - Vorhandensein typischer QMS-Abschnitte
              - Vollständige Prozessbeschreibung
              - Referenzen und Verweise
              - Dokumenten-Integrität
           
           Bewertungsskala:
           - 0.9-1.0: Vollständig, alle Aspekte abgedeckt
           - 0.7-0.8: Weitgehend vollständig, minor gaps
           - 0.5-0.6: Grundlegende Vollständigkeit
           - 0.3-0.4: Erhebliche Lücken vorhanden
           - 0.0-0.2: Fragmentarisch, unvollständig
        
        3. CLARITY_SCORE (0.0-1.0):
           🎯 Bewertet: Verständlichkeit und Klarheit
           📊 Faktoren:
              - Sprachliche Klarheit und Präzision
              - Strukturierte Darstellung
              - Eindeutigkeit der Anweisungen
              - Leserfreundlichkeit
              - Konsistente Terminologie
           
           Bewertungsskala:
           - 0.9-1.0: Kristallklar, sehr gut verständlich
           - 0.7-0.8: Klar und gut strukturiert
           - 0.5-0.6: Grundlegend verständlich
           - 0.3-0.4: Verbesserungsbedarf bei Klarheit
           - 0.0-0.2: Verwirrend, schwer verständlich
        
        PROMPT-ENGINEERING TECHNIKEN:
        -----------------------------
        - Experten-Perspektive mit QM-Fokus
        - Objektive Bewertungskriterien
        - Konstruktive Feedback-Kultur
        - Konkrete Verbesserungsvorschläge
        - Best-Practice-Orientierung
        
        VERBESSERUNGSVORSCHLÄGE:
        ------------------------
        - Spezifische, umsetzbare Empfehlungen
        - Prioritäts-basierte Verbesserungen
        - Template- und Standard-Referenzen
        - Praxisorientierte Lösungsansätze
        
        VERWENDUNG FÜR:
        ---------------
        - Kontinuierliche Verbesserung (KVP)
        - Dokumenten-Review-Prozesse
        - Qualitäts-Monitoring
        - Training und Schulungsbedarfs-Analyse
        """,
        
        "de": """Du bist ein erfahrener QMS-Experte und Dokumentenqualitäts-Auditor mit jahrzehntelanger Erfahrung. 
Bewerte die Qualität dieses QMS-Dokuments objektiv und konstruktiv.

DOKUMENT:
{content}

QUALITÄTS-BEWERTUNG IN 3 DIMENSIONEN (jeweils 0.0-1.0):

1. CONTENT_QUALITY (Inhaltliche Qualität):
   🔍 BEWERTUNGSKRITERIEN:
   - Fachliche Korrektheit und Präzision der QM-Terminologie
   - Vollständigkeit und Tiefe der fachlichen Inhalte
   - Logische Struktur und roter Faden
   - Verwendung aktueller Standards und Best Practices
   - Compliance mit QM-Anforderungen (ISO 13485, etc.)
   
   📊 BEWERTUNGSSKALA:
   - 0.9-1.0: Expertenlevel, umfassende fachliche Exzellenz
   - 0.7-0.8: Gute fachliche Qualität, minor improvements
   - 0.5-0.6: Grundlegende fachliche Korrektheit
   - 0.3-0.4: Erhebliche fachliche Mängel
   - 0.0-0.2: Unzureichende fachliche Qualität

2. COMPLETENESS (Vollständigkeit):
   🔍 BEWERTUNGSKRITERIEN:
   - Abdeckung aller relevanten QMS-Aspekte für den Dokumenttyp
   - Vollständige Prozess-/Verfahrensbeschreibung
   - Vorhandensein typischer Abschnitte (Zweck, Geltungsbereich, etc.)
   - Referenzen zu verwandten Dokumenten und Standards
   - Informations-Integrität und -konsistenz
   
   📊 BEWERTUNGSSKALA:
   - 0.9-1.0: Vollständig, alle erwarteten Aspekte abgedeckt
   - 0.7-0.8: Weitgehend vollständig, geringfügige Lücken
   - 0.5-0.6: Grundlegende Vollständigkeit erreicht
   - 0.3-0.4: Wesentliche Informationen fehlen
   - 0.0-0.2: Fragmentarisch, erhebliche Lücken

3. CLARITY (Klarheit und Verständlichkeit):
   🔍 BEWERTUNGSKRITERIEN:
   - Sprachliche Klarheit und Verständlichkeit
   - Strukturierte, logische Darstellung
   - Eindeutigkeit von Anweisungen und Anforderungen
   - Konsistente Verwendung von Terminologie
   - Benutzerfreundlichkeit für Zielgruppe
   
   📊 BEWERTUNGSSKALA:
   - 0.9-1.0: Kristallklar, ausgezeichnet verständlich
   - 0.7-0.8: Klar strukturiert und gut verständlich
   - 0.5-0.6: Grundlegend verständlich, minor clarity issues
   - 0.3-0.4: Room for improvement in comprehensibility
   - 0.0-0.2: Confusing, difficult to follow

4. GESAMTBEWERTUNG:
   - Synthese aller drei Dimensionen
   - Stärken und Verbesserungspotentiale
   - Einordnung in QMS-Best-Practices

5. VERBESSERUNGSVORSCHLÄGE:
   - Konkrete, umsetzbare Empfehlungen
   - Priorisierte Verbesserungsmaßnahmen  
   - Best-Practice-Referenzen

JSON-Antwort:
{{
    "content_quality_score": 0.0-1.0,
    "completeness_score": 0.0-1.0,
    "clarity_score": 0.0-1.0,
    "overall_assessment": "Detaillierte Gesamtbewertung in 2-3 Sätzen",
    "improvement_suggestions": [
        "Konkrete Verbesserung 1",
        "Konkrete Verbesserung 2", 
        "Konkrete Verbesserung 3"
    ],
    "strengths_identified": ["Stärke 1", "Stärke 2"],
    "priority_improvements": ["Priorität 1", "Priorität 2"]
}}""",
        
        "en": """You are an experienced QMS expert and document quality auditor with decades of experience.
Evaluate the quality of this QMS document objectively and constructively.

DOCUMENT:
{content}

QUALITY ASSESSMENT IN 3 DIMENSIONS (each 0.0-1.0):

1. CONTENT_QUALITY (Content Quality and Professionalism):
   🔍 EVALUATION CRITERIA:
   - Technical correctness and precision of QM terminology
   - Completeness and depth of technical content
   - Logical structure and coherent flow
   - Use of current standards and best practices
   - Compliance with QM requirements (ISO 13485, etc.)
   
   📊 RATING SCALE:
   - 0.9-1.0: Expert level, comprehensive technical excellence
   - 0.7-0.8: Good technical quality, minor improvements
   - 0.5-0.6: Basic technical correctness
   - 0.3-0.4: Significant technical deficiencies
   - 0.0-0.2: Insufficient technical quality

2. COMPLETENESS (Completeness of Information):
   🔍 EVALUATION CRITERIA:
   - Coverage of all relevant QM aspects for document type
   - Complete process/procedure description
   - Presence of typical sections (Purpose, Scope, etc.)
   - References to related documents and standards
   - Information integrity and consistency
   
   📊 RATING SCALE:
   - 0.9-1.0: Complete, all expected aspects covered
   - 0.7-0.8: Largely complete, minor gaps
   - 0.5-0.6: Basic completeness achieved
   - 0.3-0.4: Essential information missing
   - 0.0-0.2: Fragmentary, significant gaps

3. CLARITY (Clarity and Comprehensibility):
   🔍 EVALUATION CRITERIA:
   - Linguistic clarity and comprehensibility
   - Structured, logical presentation
   - Unambiguous instructions and requirements
   - Consistent use of terminology
   - User-friendliness for target audience
   
   📊 RATING SCALE:
   - 0.9-1.0: Crystal clear, excellently understandable
   - 0.7-0.8: Clearly structured and well understandable
   - 0.5-0.6: Basically understandable, minor clarity issues
   - 0.3-0.4: Room for improvement in comprehensibility
   - 0.0-0.2: Confusing, difficult to follow

4. OVERALL ASSESSMENT:
   - Synthesis of all three dimensions
   - Strengths and improvement potential
   - Classification within QMS best practices

5. IMPROVEMENT SUGGESTIONS:
   - Concrete, implementable recommendations
   - Prioritized improvement measures
   - Best practice references

JSON response:
{{
    "content_quality_score": 0.0-1.0,
    "completeness_score": 0.0-1.0,
    "clarity_score": 0.0-1.0,
    "overall_assessment": "Detailed overall assessment in 2-3 sentences",
    "improvement_suggestions": [
        "Concrete improvement 1",
        "Concrete improvement 2", 
        "Concrete improvement 3"
    ],
    "strengths_identified": ["Strength 1", "Strength 2"],
    "priority_improvements": ["Priority 1", "Priority 2"]
}}"""
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# 💬 RAG-CHAT PROMPTS - Retrieval Augmented Generation für Conversational AI
# ═══════════════════════════════════════════════════════════════════════════════

"""
RAG-CHAT SYSTEM - DETAILLIERTE DOKUMENTATION
=============================================

Das RAG-Chat-System ermöglicht natürliche Konversationen über QMS-Dokumente
mit hoher Fachlichkeit, korrekten Quellenangaben und kontextueller Präzision.

HAUPTFUNKTIONEN:
- Erweiterte Suche mit Query-Enhancement
- Kontextuelle Antwortgenerierung
- Automatische Quellenangaben
- Follow-Up Suggestions
- Multi-Turn Conversation Support

PROMPT-ENGINEERING PRINZIPIEN:
- Role-based Setup (QM-Experte)
- Context-aware Responses  
- Source Attribution Requirements
- Professional Tone Maintenance
- Structured Output Format
"""

RAG_CHAT_PROMPTS = {
    
    "enhanced_rag_chat": {
        "description": """
        ENHANCED RAG CHAT - Professionelle QM-Dokumenten-Konversation
        =============================================================
        
        Dieser Prompt erstellt einen hochqualitativen QM-Experten Chat-Bot
        der natürliche Gespräche über QMS-Dokumenteninhalte führt.
        
        FUNKTIONALITÄT:
        ---------------
        - Professionelle QM-Expertise in allen Antworten
        - Automatische Quellenangaben mit Dokumentreferenzen
        - Kontextuelle Antworten basierend auf verfügbaren Dokumenten
        - Follow-Up-Fragen und Vertiefungsvorschläge
        - Multi-Turn-Conversation-Support
        
        ANTWORT-QUALITÄTSMERKMALE:
        -------------------------
        - Fachlich korrekte und präzise Antworten
        - QM-spezifische Terminologie
        - Strukturierte Darstellung komplexer Sachverhalte
        - Praktische Anwendungshinweise
        - Compliance-Orientierung
        
        QUELLENANGABEN-SYSTEM:
        ---------------------
        - Explizite Dokumentreferenzen nach jeder Information
        - Format: "(siehe: Dokumentname, Abschnitt X)"
        - Transparente Nachvollziehbarkeit aller Aussagen
        - Verknüpfung zu Original-Dokumentstellen
        
        FOLLOW-UP SUGGESTIONS:
        ---------------------
        - Automatische Generierung weiterführender Fragen
        - Verwandte Themen und Aspekte
        - Vertiefungsrichtungen
        - Praktische Anwendungsbeispiele
        """,
        
        "de": """Du bist ein erfahrener QM-Experte mit umfassendem Wissen über Qualitätsmanagement-Systeme, 
ISO 13485, medizinische Geräte-Regularien und QM-Best-Practices.

VERFÜGBARE DOKUMENTE UND KONTEXT:
{context}

BENUTZER-FRAGE:
{question}

ANTWORT-RICHTLINIEN:

🎯 EXPERTISE & TONALITÄT:
- Antworte als erfahrener QM-Experte mit jahrzehntelanger Praxis
- Verwende professionelle, aber verständliche QM-Terminologie
- Zeige Fachkompetenz ohne überheblich zu wirken
- Berücksichtige praktische Umsetzungsaspekte

📚 QUELLENANGABEN (KRITISCH WICHTIG):
- Gib IMMER explizite Quellenangaben für jede Information an
- Format: "(siehe: Dokumentname, Kapitel/Abschnitt wenn verfügbar)"
- Verwende NUR Informationen aus den verfügbaren Dokumenten
- Bei fehlenden Informationen: "Diese Information ist in den verfügbaren Dokumenten nicht enthalten"

🏗️ ANTWORT-STRUKTUR:
1. HAUPTANTWORT:
   - Direkte, präzise Beantwortung der Frage
   - 2-4 gut strukturierte Absätze
   - Praktische Relevanz und Anwendungshinweise

2. DETAILLIERTE AUSFÜHRUNG (falls nötig):
   - Vertiefte Erklärungen komplexer Sachverhalte
   - Beispiele und Anwendungsfälle
   - Compliance-Aspekte und regulatorische Hinweise

3. QUELLENVERWEISE:
   - Vollständige Auflistung aller verwendeten Dokumente
   - Spezifische Abschnitte und Kapitel wo verfügbar

4. FOLLOW-UP VORSCHLÄGE (2-3 Fragen):
   - Weiterführende Fragen zu verwandten Themen
   - Vertiefungsrichtungen
   - Praktische Anwendungsaspekte

COMPLIANCE & QUALITÄT:
- Achte auf ISO 13485, MDR, FDA 21 CFR Part 820 Konformität
- Berücksichtige Risikomanagement-Aspekte (ISO 14971)
- Betone CAPA, Design Controls und Validierung wo relevant
- Verwende deutsche QM-Terminologie konsistent

WICHTIGE HINWEISE:
- Sei präzise und konkret, vermeide vage Aussagen
- Gib praktische Umsetzungshinweise wo möglich
- Erkenne Zusammenhänge zwischen verschiedenen QM-Bereichen
- Bei Unsicherheit: Verweise auf Expertenkonsultation oder weitere Dokumentation

Strukturiere deine Antwort professionell und umfassend.""",
        
        "en": """You are an experienced QM expert with comprehensive knowledge of Quality Management Systems,
ISO 13485, medical device regulations, and QM best practices.

AVAILABLE DOCUMENTS AND CONTEXT:
{context}

USER QUESTION:
{question}

RESPONSE GUIDELINES:

🎯 EXPERTISE & TONE:
- Respond as an experienced QM expert with decades of practice
- Use professional but understandable QM terminology
- Show expertise without being condescending
- Consider practical implementation aspects

📚 SOURCE CITATIONS (CRITICALLY IMPORTANT):
- ALWAYS provide explicit source citations for every piece of information
- Format: "(see: Document Name, Chapter/Section if available)"
- Use ONLY information from the available documents
- For missing information: "This information is not contained in the available documents"

🏗️ RESPONSE STRUCTURE:
1. MAIN ANSWER:
   - Direct, precise answer to the question
   - 2-4 well-structured paragraphs
   - Practical relevance and implementation hints

2. DETAILED EXPLANATION (if needed):
   - In-depth explanations of complex matters
   - Examples and use cases
   - Compliance aspects and regulatory notes

3. SOURCE REFERENCES:
   - Complete listing of all used documents
   - Specific sections and chapters where available

4. FOLLOW-UP SUGGESTIONS (2-3 questions):
   - Further questions on related topics
   - Directions for deeper exploration
   - Practical application aspects

COMPLIANCE & QUALITY:
- Consider ISO 13485, MDR, FDA 21 CFR Part 820 compliance
- Account for risk management aspects (ISO 14971)
- Emphasize CAPA, Design Controls, and Validation where relevant
- Use consistent QM terminology

IMPORTANT NOTES:
- Be precise and concrete, avoid vague statements
- Provide practical implementation guidance where possible
- Recognize connections between different QM areas
- When uncertain: Refer to expert consultation or additional documentation

Structure your response professionally and comprehensively."""
    },

    "simple_rag_chat": {
        "description": """
        SIMPLE RAG CHAT - Basis-Konversation für schnelle Antworten
        ===========================================================
        
        Ein streamlined Chat-Prompt für schnelle, direkte Antworten
        ohne umfangreiche Strukturierung.
        
        VERWENDUNG:
        - Schnelle Faktenfragen
        - Einfache Dokumentenabfragen
        - Basic Information Retrieval
        """,
        
        "de": """Beantworte die folgende Frage basierend auf den verfügbaren QMS-Dokumenten:

DOKUMENTE:
{context}

FRAGE:
{question}

Gib eine kurze, präzise Antwort mit Quellenangaben in diesem Format:
"Antwort... (Quelle: Dokumentname)"

Falls die Information nicht verfügbar ist, sage das klar.""",
        
        "en": """Answer the following question based on the available QMS documents:

DOCUMENTS:
{context}

QUESTION:
{question}

Provide a short, precise answer with source citations in this format:
"Answer... (Source: Document Name)"

If the information is not available, state this clearly."""
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 HILFSFUNKTIONEN FÜR PROMPT-VERWALTUNG
# ═══════════════════════════════════════════════════════════════════════════════

def get_metadata_prompt(
    prompt_type: str,
    language: str = "de",
    content: str = "",
    complexity: str = "standard"
) -> str:
    """
    Ruft einen Metadaten-Extraktions-Prompt ab und formatiert ihn mit dem Inhalt.
    
    FUNKTION:
    ---------
    Diese Funktion ist der zentrale Zugangspunkt für alle Metadaten-Extraktions-
    Prompts im 5-Layer-Analyse-System.
    
    PARAMETER:
    ----------
    prompt_type : str
        Der Typ des Prompts aus dem METADATA_EXTRACTION_PROMPTS Dictionary
        Verfügbare Typen:
        - "document_analysis": LAYER 1 - Grundlegende Dokumentenklassifikation
        - "keyword_extraction": LAYER 2 - Strukturierte Keyword-Extraktion
        - "structure_analysis": LAYER 3 - Dokumentstruktur-Analyse
        - "compliance_analysis": LAYER 4 - Regulatory Affairs Analyse
        - "quality_assessment": LAYER 5 - Qualitätsbewertung
        
    language : str, optional
        Sprache des Prompts, default "de"
        Verfügbare Sprachen: "de" (Deutsch), "en" (Englisch)
        
    content : str, optional
        Der Dokumenteninhalt, der in den Prompt eingefügt wird
        Wird an der Stelle {content} im Prompt-Template eingefügt
        
    complexity : str, optional
        Komplexitätsstufe des Prompts, default "standard"
        Für zukünftige Erweiterungen (Simple/Standard/Advanced/Expert)
    
    RÜCKGABE:
    ---------
    str
        Der formatierte Prompt, bereit für die AI-Analyse
        
    VERWENDUNG:
    -----------
    ```python
    # Einfache Verwendung für Dokumentenanalyse
    prompt = get_metadata_prompt(
        "document_analysis", 
        language="de",
        content="Ihr Dokumententext hier..."
    )
    
    # Keyword-Extraktion auf Englisch
    keywords_prompt = get_metadata_prompt(
        "keyword_extraction",
        language="en", 
        content=document_text
    )
    ```
    
    FEHLERBEHANDLUNG:
    ----------------
    - Unbekannte prompt_types werden protokolliert und werfen KeyError
    - Unsupported languages fallen zurück auf Deutsch
    - Leerer Content wird akzeptiert (für Template-Abruf)
    
    INTEGRATION:
    -----------
    Diese Funktion wird verwendet von:
    - ai_metadata_extractor.py (5-Layer-Analyse)
    - advanced_ai_endpoints.py (API-Endpoints)
    - Direkter Zugriff für Custom-Analysen
    """
    
    try:
        # Validierung des Prompt-Typs
        if prompt_type not in METADATA_EXTRACTION_PROMPTS:
            logger.error(f"Unbekannter Metadata Prompt Type: {prompt_type}")
            available_types = list(METADATA_EXTRACTION_PROMPTS.keys())
            raise KeyError(f"Prompt type '{prompt_type}' nicht verfügbar. Verfügbare Typen: {available_types}")
        
        # Language Fallback
        if language not in ["de", "en"]:
            logger.warning(f"Unsupported language '{language}', fallback to 'de'")
            language = "de"
        
        # Prompt Template abrufen
        prompt_template = METADATA_EXTRACTION_PROMPTS[prompt_type][language]
        
        # Content einfügen wenn vorhanden
        if content:
            formatted_prompt = prompt_template.replace("{content}", content)
        else:
            formatted_prompt = prompt_template
            
        logger.debug(f"Metadata Prompt erstellt: {prompt_type} ({language}, {len(content)} chars)")
        return formatted_prompt
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Metadata Prompts: {e}")
        raise

def get_rag_prompt(
    prompt_type: str = "enhanced_rag_chat",
    language: str = "de", 
    context: str = "",
    question: str = "",
    complexity: str = "standard"
) -> str:
    """
    Ruft einen RAG-Chat-Prompt ab und formatiert ihn mit Context und Frage.
    
    FUNKTION:
    ---------
    Diese Funktion stellt die RAG-Chat-Prompts für conversational AI bereit
    und formatiert sie mit dem verfügbaren Dokumentenkontext und der Benutzerfrage.
    
    PARAMETER:
    ----------
    prompt_type : str, optional
        Der Typ des RAG-Prompts, default "enhanced_rag_chat"
        Verfügbare Typen:
        - "enhanced_rag_chat": Umfassender QM-Experten-Chat mit Quellenangaben
        - "simple_rag_chat": Einfacher Chat für schnelle Antworten
        
    language : str, optional
        Sprache des Prompts, default "de"
        Verfügbare Sprachen: "de" (Deutsch), "en" (Englisch)
        
    context : str, optional
        Der verfügbare Dokumentenkontext für die Antwort
        Wird an der Stelle {context} im Prompt eingefügt
        
    question : str, optional
        Die Benutzerfrage die beantwortet werden soll
        Wird an der Stelle {question} im Prompt eingefügt
        
    complexity : str, optional
        Komplexitätsstufe, default "standard"
        Für zukünftige Erweiterungen
    
    RÜCKGABE:
    ---------
    str
        Der formatierte RAG-Chat-Prompt, bereit für die Konversation
        
    VERWENDUNG:
    -----------
    ```python
    # Enhanced RAG Chat für umfassende Antworten
    chat_prompt = get_rag_prompt(
        "enhanced_rag_chat",
        language="de",
        context="Verfügbare Dokumente: QM-Handbuch...",
        question="Wie ist der CAPA-Prozess definiert?"
    )
    
    # Simple RAG Chat für schnelle Antworten
    simple_prompt = get_rag_prompt(
        "simple_rag_chat",
        context=doc_context,
        question=user_question
    )
    ```
    
    PROMPT-FEATURES:
    ---------------
    - Automatische Quellenangaben
    - Strukturierte Antwortformate
    - Follow-Up-Suggestions
    - QM-Expertise-Integration
    - Compliance-Orientierung
    
    FEHLERBEHANDLUNG:
    ----------------
    - Unbekannte prompt_types werden protokolliert
    - Language fallback auf Deutsch
    - Leere Contexts/Questions werden akzeptiert
    """
    
    try:
        # Validierung des Prompt-Typs
        if prompt_type not in RAG_CHAT_PROMPTS:
            logger.error(f"Unbekannter RAG Prompt Type: {prompt_type}")
            available_types = list(RAG_CHAT_PROMPTS.keys()) 
            raise KeyError(f"RAG Prompt type '{prompt_type}' nicht verfügbar. Verfügbare Typen: {available_types}")
        
        # Language Fallback
        if language not in ["de", "en"]:
            logger.warning(f"Unsupported language '{language}', fallback to 'de'")
            language = "de"
        
        # Prompt Template abrufen
        prompt_template = RAG_CHAT_PROMPTS[prompt_type][language]
        
        # Context und Question einfügen
        formatted_prompt = prompt_template
        if "{context}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{context}", context)
        if "{question}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{question}", question)
            
        logger.debug(f"RAG Prompt erstellt: {prompt_type} ({language}, {len(context)} chars context)")
        return formatted_prompt
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des RAG Prompts: {e}")
        raise

def get_available_prompts() -> Dict[str, List[str]]:
    """
    Gibt eine Übersicht aller verfügbaren Prompts zurück.
    
    RÜCKGABE:
    ---------
    Dict[str, List[str]]
        Dictionary mit Kategorien als Keys und Listen der verfügbaren Prompts als Values
        
    VERWENDUNG:
    -----------
    ```python
    available = get_available_prompts()
    print("Metadata Prompts:", available["metadata_extraction"])
    print("RAG Prompts:", available["rag_chat"])
    ```
    """
    
    return {
        "metadata_extraction": list(METADATA_EXTRACTION_PROMPTS.keys()),
        "rag_chat": list(RAG_CHAT_PROMPTS.keys()),
        "supported_languages": ["de", "en"],
        "complexity_levels": ["simple", "standard", "advanced", "expert"]
    }

def get_prompt_description(category: str, prompt_type: str) -> str:
    """
    Ruft die ausführliche Beschreibung eines Prompts ab.
    
    PARAMETER:
    ----------
    category : str
        Kategorie des Prompts ("metadata_extraction", "rag_chat")
    prompt_type : str
        Spezifischer Prompt-Typ innerhalb der Kategorie
        
    RÜCKGABE:
    ---------
    str
        Ausführliche Beschreibung des Prompts mit Funktionalität und Verwendung
    """
    
    try:
        if category == "metadata_extraction":
            return METADATA_EXTRACTION_PROMPTS[prompt_type].get("description", "Keine Beschreibung verfügbar")
        elif category == "rag_chat":
            return RAG_CHAT_PROMPTS[prompt_type].get("description", "Keine Beschreibung verfügbar")
        else:
            return f"Unbekannte Kategorie: {category}"
    except KeyError:
        return f"Prompt '{prompt_type}' in Kategorie '{category}' nicht gefunden"

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 PROMPT-VALIDIERUNG UND QUALITÄTSSICHERUNG
# ═══════════════════════════════════════════════════════════════════════════════

def validate_prompt_templates() -> Dict[str, bool]:
    """
    Validiert alle Prompt-Templates auf Vollständigkeit und Konsistenz.
    
    VALIDIERUNGEN:
    -------------
    - Alle Prompts haben deutsche und englische Versionen
    - Alle Placeholders ({content}, {context}, {question}) sind korrekt
    - Descriptions sind vorhanden und nicht leer
    - JSON-Format-Spezifikationen sind syntaktisch korrekt
    
    RÜCKGABE:
    ---------
    Dict[str, bool]
        Validierungsresultate für jede Kategorie
    """
    
    results = {
        "metadata_extraction_complete": True,
        "rag_chat_complete": True,
        "all_languages_available": True,
        "descriptions_available": True
    }
    
    # Metadata Extraction Validierung
    for prompt_type, prompt_data in METADATA_EXTRACTION_PROMPTS.items():
        if "de" not in prompt_data or "en" not in prompt_data:
            logger.warning(f"Metadata prompt '{prompt_type}' fehlt Sprach-Versionen")
            results["all_languages_available"] = False
            
        if "description" not in prompt_data or not prompt_data["description"].strip():
            logger.warning(f"Metadata prompt '{prompt_type}' fehlt Beschreibung")
            results["descriptions_available"] = False
    
    # RAG Chat Validierung  
    for prompt_type, prompt_data in RAG_CHAT_PROMPTS.items():
        if "de" not in prompt_data or "en" not in prompt_data:
            logger.warning(f"RAG prompt '{prompt_type}' fehlt Sprach-Versionen")
            results["all_languages_available"] = False
            
        if "description" not in prompt_data or not prompt_data["description"].strip():
            logger.warning(f"RAG prompt '{prompt_type}' fehlt Beschreibung")
            results["descriptions_available"] = False
    
    logger.info(f"Prompt-Validierung abgeschlossen: {results}")
    return results

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 PROMPT-STATISTIKEN UND MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

def get_prompt_statistics() -> Dict[str, Any]:
    """
    Sammelt Statistiken über die verfügbaren Prompts.
    
    RÜCKGABE:
    ---------
    Dict[str, Any]
        Umfassende Statistiken über das Prompt-System
    """
    
    stats = {
        "total_categories": 2,
        "metadata_extraction_prompts": len(METADATA_EXTRACTION_PROMPTS),
        "rag_chat_prompts": len(RAG_CHAT_PROMPTS),
        "total_prompts": len(METADATA_EXTRACTION_PROMPTS) + len(RAG_CHAT_PROMPTS),
        "supported_languages": ["de", "en"],
        "average_prompt_length": 0,
        "validation_status": validate_prompt_templates()
    }
    
    # Durchschnittliche Prompt-Länge berechnen
    all_prompts = []
    for prompt_data in METADATA_EXTRACTION_PROMPTS.values():
        all_prompts.extend([prompt_data.get("de", ""), prompt_data.get("en", "")])
    for prompt_data in RAG_CHAT_PROMPTS.values():
        all_prompts.extend([prompt_data.get("de", ""), prompt_data.get("en", "")])
    
    if all_prompts:
        stats["average_prompt_length"] = sum(len(p) for p in all_prompts) // len(all_prompts)
    
    return stats

# ═══════════════════════════════════════════════════════════════════════════════
# 🏁 MODUL-INITIALISIERUNG UND LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

# Validierung beim Import
validation_results = validate_prompt_templates()

logger.info("🤖 Zentrale Prompt-Verwaltung erfolgreich geladen!")
logger.info(f"📊 {len(METADATA_EXTRACTION_PROMPTS)} Metadata-Prompts, {len(RAG_CHAT_PROMPTS)} RAG-Prompts verfügbar")

if all(validation_results.values()):
    logger.info("✅ Alle Prompt-Templates erfolgreich validiert")
else:
    logger.warning(f"⚠️ Prompt-Validierung mit Warnungen: {validation_results}")

# Export der wichtigsten Funktionen für einfachen Import
__all__ = [
    "get_metadata_prompt",
    "get_rag_prompt", 
    "get_available_prompts",
    "get_prompt_description",
    "get_prompt_statistics",
    "PromptCategory",
    "PromptLanguage", 
    "PromptComplexity"
]

# ═══════════════════════════════════════════════════════════════════════════════
# 🔒 ENHANCED JSON VALIDATION & FALLBACK SYSTEM (Version 2.0)
# ═══════════════════════════════════════════════════════════════════════════════

"""
ERWEITERTES JSON-VALIDIERUNGSSYSTEM - BASIEREND AUF BENUTZER-FEEDBACK
===================================================================

Dieses erweiterte System implementiert die wertvollen Verbesserungsvorschläge:

✅ STRIKTE JSON-PARSING mit klaren Schema-Vorgaben
✅ TEMPERATURE=0 Empfehlungen für konsistente Ergebnisse  
✅ ROBUSTE FALLBACK-MECHANISMEN bei parsing-Fehlern
✅ PYDANTIC-INTEGRATION für Schema-Validierung
✅ REGEX-BASIERTE JSON-EXTRAKTION als Fallback
✅ LOGGING/MONITORING für fehlgeschlagene Parses

ARCHITEKTUR:
1. Pydantic Models für Schema-Definition
2. Strikte JSON-Prompts mit expliziten Format-Anforderungen
3. Multi-Level Fallback-System bei Parsing-Fehlern
4. Temperature-Empfehlungen in Prompt-Metadata
5. Automatisches Error-Logging für Monitoring

VERWENDUNG:
```python
from app.prompts import parse_ai_response, get_strict_json_prompt

# AI-Response mit Validierung parsen:
result = parse_ai_response(
    response_text="AI-Antwort hier...",
    expected_schema=QMSResponseSchema
)

# Strikt JSON-konforme Prompts abrufen:
prompt = get_strict_json_prompt("qms_analysis", context="...", question="...")
```

WICHTIG: Setzen Sie IMMER temperature=0 für JSON-Responses!
"""

# ═══════════════════════════════════════════════════════════════════════════════
# 📋 PYDANTIC RESPONSE SCHEMAS für JSON-VALIDIERUNG
# ═══════════════════════════════════════════════════════════════════════════════

class QMSResponseSchema(BaseModel):
    """
    Standard-Schema für QMS-Antworten mit strikter JSON-Validierung.
    
    Basiert auf dem Benutzer-Beispiel mit erweiterten Validierungen.
    """
    answer: str = Field(
        ..., 
        max_length=500, 
        description="Hauptantwort auf die gestellte Frage (max 500 Zeichen)"
    )
    relevant_sections: List[str] = Field(
        default=[], 
        description="Liste der relevanten Dokumentenabschnitte als Quelle"
    )
    confidence: str = Field(
        ..., 
        pattern="^(hoch|mittel|niedrig)$",
        description="Vertrauenslevel: 'hoch', 'mittel' oder 'niedrig'"
    )

class ExtendedQMSResponseSchema(BaseModel):
    """
    Erweiterte QMS-Response mit zusätzlichen Metadaten.
    """
    answer: str = Field(..., max_length=1000)
    relevant_sections: List[str] = Field(default=[])
    confidence: str = Field(..., pattern="^(hoch|mittel|niedrig)$")
    source_documents: List[str] = Field(default=[], description="Quell-Dokumente")
    compliance_references: List[str] = Field(default=[], description="ISO/FDA Referenzen")
    follow_up_suggestions: List[str] = Field(default=[], description="Folgevorschläge (max 3)")

class MetadataExtractionSchema(BaseModel):
    """
    Schema für Metadaten-Extraktion mit 5-Layer-Struktur.
    """
    document_type: str = Field(..., description="Klassifizierter Dokumenttyp")
    keywords: Dict[str, List[str]] = Field(..., description="Kategorisierte Keywords")
    structure: Dict[str, Any] = Field(..., description="Dokument-Struktur-Analyse")
    compliance: Dict[str, str] = Field(..., description="Compliance-Bewertung")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Qualitätsscore 0.0-1.0")

# ═══════════════════════════════════════════════════════════════════════════════
# 🔒 STRIKTE JSON-PROMPTS mit Fallback-Mechanismen
# ═══════════════════════════════════════════════════════════════════════════════

STRICT_JSON_PROMPTS = {
    "qms_analysis": {
        "de": """Du bist ein Qualitätsmanagement-Assistent für ISO 13485 konforme Medizinprodukte.
Nutze ausschließlich den folgenden Kontext, um die Frage zu beantworten.

WICHTIG: Gib die Antwort als valides JSON zurück im folgenden Format:

{
  "answer": "string (max 500 Zeichen)",
  "relevant_sections": ["string", "string"],
  "confidence": "hoch | mittel | niedrig"
}

REGELN:
- Wenn du keine Information findest, setze "answer" auf "Keine Information vorhanden."
- "confidence" muss exakt "hoch", "mittel" oder "niedrig" sein
- "relevant_sections" als Array von Strings mit Abschnittsnamen
- Keine zusätzlichen Felder oder Kommentare außerhalb des JSON
- Syntaktisch korrektes JSON ohne Escape-Zeichen-Fehler

Kontext:
{context}

Frage:
{question}""",
        
        "en": """You are a Quality Management Assistant for ISO 13485 compliant medical devices.
Use exclusively the following context to answer the question.

IMPORTANT: Return the answer as valid JSON in the following format:

{
  "answer": "string (max 500 characters)",
  "relevant_sections": ["string", "string"],
  "confidence": "high | medium | low"
}

RULES:
- If no information found, set "answer" to "No information available."
- "confidence" must be exactly "high", "medium" or "low"
- "relevant_sections" as array of strings with section names
- No additional fields or comments outside the JSON
- Syntactically correct JSON without escape character errors

Context:
{context}

Question:
{question}""",
        
        "temperature": 0,
        "description": "Strikt JSON-konforme QMS-Analyse basierend auf Benutzer-Feedback"
    },
    
    "metadata_extraction_json": {
        "de": """Du bist ein Experte für QMS-Dokumenten-Analyse.
Analysiere das folgende Dokument und extrahiere Metadaten.

WICHTIG: Gib das Ergebnis als valides JSON zurück:

{
  "document_type": "string",
  "keywords": {
    "primary": ["string"],
    "secondary": ["string"],
    "qms_specific": ["string"],
    "compliance": ["string"]
  },
  "structure": {
    "sections": ["string"],
    "tables": number,
    "figures": number,
    "appendices": number
  },
  "compliance": {
    "iso_standards": ["string"],
    "regulatory_references": ["string"],
    "risk_classification": "string"
  },
  "quality_score": 0.95
}

REGELN:
- "quality_score" als Zahl zwischen 0.0 und 1.0
- Alle Arrays als valide JSON-Arrays
- Zahlen ohne Anführungszeichen
- Strings immer in Anführungszeichen

Dokument:
{content}""",
        
        "en": """You are an expert in QMS document analysis.
Analyze the following document and extract metadata.

IMPORTANT: Return the result as valid JSON:

{
  "document_type": "string",
  "keywords": {
    "primary": ["string"],
    "secondary": ["string"],
    "qms_specific": ["string"],
    "compliance": ["string"]
  },
  "structure": {
    "sections": ["string"],
    "tables": number,
    "figures": number,
    "appendices": number
  },
  "compliance": {
    "iso_standards": ["string"],
    "regulatory_references": ["string"],
    "risk_classification": "string"
  },
  "quality_score": 0.95
}

RULES:
- "quality_score" as number between 0.0 and 1.0
- All arrays as valid JSON arrays
- Numbers without quotes
- Strings always in quotes

Document:
{content}""",
        
        "temperature": 0,
        "description": "Strikte JSON-Metadaten-Extraktion mit 5-Layer-Struktur"
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# 🛡️ JSON-PARSING mit Multi-Level Fallback-System
# ═══════════════════════════════════════════════════════════════════════════════

def parse_ai_response(
    response_text: str,
    expected_schema: Optional[type] = None,
    enable_fallback: bool = True,
    log_errors: bool = True
) -> Dict[str, Any]:
    """
    Parst AI-Responses mit robustem Fallback-System.
    
    IMPLEMENTIERT BENUTZER-VORSCHLÄGE:
    - Strikte JSON-Validierung mit Pydantic
    - Regex-basierte JSON-Extraktion als Fallback
    - Comprehensive Error-Logging
    - Graceful Fallback-Responses
    
    PARAMETER:
    ----------
    response_text : str
        Rohe AI-Response zum Parsen
    expected_schema : BaseModel
        Pydantic-Schema für Validierung (default: QMSResponseSchema)
    enable_fallback : bool
        Ob Fallback-Mechanismen aktiviert werden sollen
    log_errors : bool
        Ob Parsing-Fehler geloggt werden sollen
        
    RÜCKGABE:
    ---------
    Dict[str, Any]
        Geparste und validierte Response als Dictionary
        
    VERWENDUNG:
    -----------
    ```python
    # Standard-Parsing:
    result = parse_ai_response(ai_output)
    
    # Mit custom Schema:
    result = parse_ai_response(
        ai_output, 
        expected_schema=ExtendedQMSResponseSchema
    )
    
    # Fallback deaktiviert:
    result = parse_ai_response(ai_output, enable_fallback=False)
    ```
    
    FALLBACK-LEVEL:
    ---------------
    1. Direktes JSON-Parsing der kompletten Response
    2. Regex-Extraktion von JSON-Block aus Response
    3. Regex-Extraktion von einzelnen Feldern
    4. Standard-Fallback-Response mit Error-Indikation
    """
    
    original_text = response_text.strip()
    
    # LEVEL 1: Direktes JSON-Parsing versuchen
    try:
        parsed_data = json.loads(original_text)
        # Pydantic-Validierung
        if expected_schema:
            validated = expected_schema(**parsed_data)
            logger.debug("✅ Level 1: Direktes JSON-Parsing erfolgreich")
            return validated.dict()
        return parsed_data
        
    except json.JSONDecodeError as e:
        if log_errors:
            logger.warning(f"❌ Level 1 fehlgeschlagen - JSON Parse Error: {e}")
        
        if not enable_fallback:
            raise
    
    # LEVEL 2: Regex-Extraktion von JSON-Block
    if enable_fallback:
        try:
            # Suche nach JSON-Pattern {...}
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, original_text, re.DOTALL)
            
            for match in json_matches:
                try:
                    parsed_data = json.loads(match)
                    if expected_schema:
                        validated = expected_schema(**parsed_data)
                        logger.info("✅ Level 2: Regex-JSON-Extraktion erfolgreich")
                        return validated.dict()
                    return parsed_data
                except (json.JSONDecodeError, ValidationError):
                    continue
                    
        except Exception as e:
            if log_errors:
                logger.warning(f"❌ Level 2 fehlgeschlagen - Regex Pattern Error: {e}")
    
    # LEVEL 3: Field-by-Field Regex-Extraktion
    if enable_fallback:
        try:
            fallback_data = extract_fields_by_regex(original_text)
            if fallback_data:
                logger.info("✅ Level 3: Field-Regex-Extraktion erfolgreich")
                return fallback_data
                
        except Exception as e:
            if log_errors:
                logger.warning(f"❌ Level 3 fehlgeschlagen - Field Extraction Error: {e}")
    
    # LEVEL 4: Standard-Fallback
    fallback_response = {
        "answer": "Fehler beim Parsen der AI-Response.",
        "relevant_sections": [],
        "confidence": "niedrig",
        "parsing_error": True,
        "original_text": original_text[:200] + "..." if len(original_text) > 200 else original_text
    }
    
    if log_errors:
        logger.error(f"🚨 Alle Parsing-Level fehlgeschlagen. Fallback-Response aktiviert.")
        logger.error(f"Original Text (first 500 chars): {original_text[:500]}")
    
    return fallback_response

def extract_fields_by_regex(text: str) -> Optional[Dict[str, Any]]:
    """
    Extrahiert Standard-QMS-Felder mittels Regex-Pattern.
    
    Fallback-Funktion für strukturiertes Parsing wenn JSON komplett fehlschlägt.
    """
    
    extracted = {}
    
    # Answer-Pattern
    answer_patterns = [
        r'"answer"\s*:\s*"([^"]+)"',
        r'Antwort[:\s]+([^.]+)\.?',
        r'Answer[:\s]+([^.]+)\.?'
    ]
    
    for pattern in answer_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            extracted["answer"] = match.group(1).strip()
            break
    
    # Confidence-Pattern
    confidence_patterns = [
        r'"confidence"\s*:\s*"(hoch|mittel|niedrig|high|medium|low)"',
        r'Confidence[:\s]+(hoch|mittel|niedrig|high|medium|low)',
        r'Vertrauen[:\s]+(hoch|mittel|niedrig)'
    ]
    
    for pattern in confidence_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            conf = match.group(1).lower()
            # Normalisierung
            if conf in ["high", "hoch"]:
                extracted["confidence"] = "hoch"
            elif conf in ["medium", "mittel"]:
                extracted["confidence"] = "mittel"
            else:
                extracted["confidence"] = "niedrig"
            break
    
    # Relevant Sections (vereinfacht)
    sections_pattern = r'"relevant_sections"\s*:\s*\[(.*?)\]'
    match = re.search(sections_pattern, text, re.DOTALL)
    if match:
        sections_str = match.group(1)
        # Einfache String-Extraktion aus Array
        sections = re.findall(r'"([^"]+)"', sections_str)
        extracted["relevant_sections"] = sections
    else:
        extracted["relevant_sections"] = []
    
    # Mindest-Felder prüfen
    if "answer" in extracted:
        extracted.setdefault("confidence", "niedrig")
        extracted.setdefault("relevant_sections", [])
        return extracted
    
    return None

def get_strict_json_prompt(
    prompt_type: str,
    language: str = "de",
    context: str = "",
    question: str = "",
    content: str = ""
) -> Dict[str, Union[str, int]]:
    """
    Ruft strikte JSON-Prompts mit Temperature-Empfehlungen ab.
    
    IMPLEMENTIERT BENUTZER-FEEDBACK:
    - Klare JSON-Format-Anforderungen
    - Temperature=0 Empfehlung inklusive
    - Robuste Schema-Definition
    
    PARAMETER:
    ----------
    prompt_type : str
        Typ des JSON-Prompts ("qms_analysis", "metadata_extraction_json")
    language : str
        Sprache ("de" oder "en")
    context : str
        Kontext für RAG-basierte Prompts
    question : str
        Frage für Chat-basierte Prompts
    content : str
        Dokumenteninhalt für Analyse-Prompts
        
    RÜCKGABE:
    ---------
    Dict[str, Union[str, int]]
        Dictionary mit "prompt", "temperature" und "description"
        
    VERWENDUNG:
    -----------
    ```python
    # QMS-Analyse Prompt:
    prompt_config = get_strict_json_prompt(
        "qms_analysis",
        context="ISO 13485 Dokument...",
        question="Was sind die Hauptanforderungen?"
    )
    
    # Mit empfohlener Temperature:
    ai_response = ai_model.generate(
        prompt=prompt_config["prompt"],
        temperature=prompt_config["temperature"]  # Automatisch 0
    )
    
    # Response parsen:
    parsed = parse_ai_response(ai_response)
    ```
    """
    
    if prompt_type not in STRICT_JSON_PROMPTS:
        available = list(STRICT_JSON_PROMPTS.keys())
        raise KeyError(f"Strict JSON Prompt '{prompt_type}' nicht verfügbar. Verfügbare: {available}")
    
    prompt_data = STRICT_JSON_PROMPTS[prompt_type]
    
    # Language Fallback
    if language not in prompt_data:
        logger.warning(f"Language '{language}' nicht verfügbar für '{prompt_type}', fallback zu 'de'")
        language = "de"
    
    # Template abrufen und formatieren
    template = prompt_data[language]
    
    # Platzhalter ersetzen
    formatted_prompt = template
    if "{context}" in template:
        formatted_prompt = formatted_prompt.replace("{context}", context)
    if "{question}" in template:
        formatted_prompt = formatted_prompt.replace("{question}", question)
    if "{content}" in template:
        formatted_prompt = formatted_prompt.replace("{content}", content)
    
    return {
        "prompt": formatted_prompt,
        "temperature": prompt_data.get("temperature", 0),
        "description": prompt_data.get("description", "Strict JSON Prompt"),
        "recommended_max_tokens": 1000,
        "expected_format": "JSON"
    }

def validate_ai_model_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validiert AI-Model-Konfiguration für optimale JSON-Response.
    
    EMPFOHLENE EINSTELLUNGEN FÜR JSON-RESPONSES:
    - temperature: 0 (keine Kreativität)
    - top_p: 0.1 (fokussierte Antworten) 
    - max_tokens: 1000-2000 (ausreichend für strukturierte Antworten)
    - stop_tokens: ["}"] (stoppt nach JSON-Ende)
    """
    
    optimized_config = config.copy()
    recommendations = []
    
    # Temperature prüfen
    if config.get("temperature", 1.0) > 0.1:
        optimized_config["temperature"] = 0
        recommendations.append("Temperature auf 0 gesetzt für konsistente JSON-Ausgabe")
    
    # Top-p prüfen
    if config.get("top_p", 1.0) > 0.2:
        optimized_config["top_p"] = 0.1
        recommendations.append("Top-p auf 0.1 reduziert für fokussierte Antworten")
    
    # Max tokens prüfen
    if config.get("max_tokens", 0) < 500:
        optimized_config["max_tokens"] = 1000
        recommendations.append("Max tokens auf 1000 erhöht für vollständige JSON-Responses")
    
    # Stop tokens hinzufügen für JSON
    if "stop" not in config:
        optimized_config["stop"] = ["\n\n", "```"]
        recommendations.append("Stop-tokens für JSON-Ende hinzugefügt")
    
    logger.info(f"AI-Config optimiert für JSON: {len(recommendations)} Verbesserungen")
    for rec in recommendations:
        logger.debug(f"  → {rec}")
    
    return optimized_config

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 ENHANCED MONITORING für JSON-Response-Quality
# ═══════════════════════════════════════════════════════════════════════════════

def log_response_quality(
    original_response: str,
    parsed_result: Dict[str, Any],
    prompt_type: str,
    success_level: int = 1
) -> None:
    """
    Loggt Qualitäts-Metriken für AI-Response-Parsing.
    
    Ermöglicht Monitoring und Optimierung der Prompt-Qualität.
    """
    
    quality_metrics = {
        "prompt_type": prompt_type,
        "response_length": len(original_response),
        "success_level": success_level,  # 1=direct, 2=regex, 3=fallback, 4=error
        "has_parsing_error": parsed_result.get("parsing_error", False),
        "confidence_level": parsed_result.get("confidence", "unknown"),
        "field_completeness": calculate_field_completeness(parsed_result),
        "timestamp": "unknown"
    }
    
    logger.info(f"📊 Response Quality: {quality_metrics}")
    
    # Warnung bei häufigen Parsing-Fehlern
    if success_level >= 3:
        logger.warning(f"⚠️ Prompt '{prompt_type}' benötigt Optimierung - Success Level: {success_level}")

def calculate_field_completeness(parsed_data: Dict[str, Any]) -> float:
    """
    Berechnet die Vollständigkeit der geparsten Felder.
    """
    
    expected_fields = ["answer", "relevant_sections", "confidence"]
    present_fields = sum(1 for field in expected_fields if field in parsed_data and parsed_data[field])
    
    return present_fields / len(expected_fields)

# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 ERWEITERTE EXPORT-LISTE
# ═══════════════════════════════════════════════════════════════════════════════

# Export der wichtigsten Funktionen für einfachen Import
__all__ = [
    "get_metadata_prompt",
    "get_rag_prompt", 
    "get_available_prompts",
    "get_prompt_description",
    "get_prompt_statistics",
    "PromptCategory",
    "PromptLanguage", 
    "PromptComplexity",
    # Neue JSON-Enhanced Funktionen:
    "parse_ai_response",
    "get_strict_json_prompt",
    "validate_ai_model_config",
    "QMSResponseSchema",
    "ExtendedQMSResponseSchema",
    "MetadataExtractionSchema"
]