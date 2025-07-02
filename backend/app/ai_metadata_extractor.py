"""
🤖 ADVANCED AI METADATA EXTRACTOR für KI-QMS - Enterprise Grade 2024
==================================================================

Erweiterte AI-basierte Metadaten-Extraktion mit:
- Multi-Layer Analysis (Struktur, Inhalt, Semantik)
- QM-spezifische Klassifizierung  
- Erweiterte Keyword-Extraktion
- Compliance-Erkennung
- Automatische Kategorisierung
- Strukturierte Dokumenten-Analyse

Author: AI Assistant
Version: 2.0 - Enterprise Grade
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
import re
import time
import json
from dataclasses import dataclass
from enum import Enum

# Google Gemini Integration
import google.generativeai as genai
import os

logger = logging.getLogger("KI-QMS.AdvancedMetadataExtractor")

class DocumentTypeClassification(Enum):
    """Erweiterte Dokumenttyp-Klassifizierung"""
    # QM Core Documents
    QM_MANUAL = "QM_MANUAL"
    QM_POLICY = "QM_POLICY"
    SOP = "SOP"
    WORK_INSTRUCTION = "WORK_INSTRUCTION"
    
    # Standards & Norms
    STANDARD_NORM = "STANDARD_NORM"
    ISO_STANDARD = "ISO_STANDARD"
    DIN_STANDARD = "DIN_STANDARD"
    
    # Regulatory
    REGULATORY_DOCUMENT = "REGULATORY_DOCUMENT"
    COMPLIANCE_DOCUMENT = "COMPLIANCE_DOCUMENT"
    FDA_GUIDANCE = "FDA_GUIDANCE"
    MDR_DOCUMENT = "MDR_DOCUMENT"
    
    # Processes
    PROCESS_DESCRIPTION = "PROCESS_DESCRIPTION"
    FLOW_CHART = "FLOW_CHART"
    CHECKLIST = "CHECKLIST"
    
    # Forms & Templates
    FORM = "FORM"
    TEMPLATE = "TEMPLATE"
    PROTOCOL = "PROTOCOL"
    
    # Records
    AUDIT_REPORT = "AUDIT_REPORT"
    TEST_REPORT = "TEST_REPORT"
    VALIDATION_REPORT = "VALIDATION_REPORT"
    
    # Other
    TRAINING_MATERIAL = "TRAINING_MATERIAL"
    SPECIFICATION = "SPECIFICATION"
    OTHER = "OTHER"

@dataclass
class AdvancedMetadata:
    """Erweiterte Metadaten-Struktur"""
    # Basis-Informationen
    title: str
    document_type: DocumentTypeClassification
    description: str
    
    # Erweiterte Klassifizierung
    main_category: str
    sub_category: str
    process_area: str
    
    # Keywords & Tags
    primary_keywords: List[str]
    secondary_keywords: List[str]
    qm_keywords: List[str]
    compliance_keywords: List[str]
    
    # Strukturelle Analyse
    document_structure: Dict[str, Any]
    sections_detected: List[str]
    has_tables: bool
    has_figures: bool
    has_appendices: bool
    
    # Compliance & Standards
    iso_standards_referenced: List[str]
    regulatory_references: List[str]
    compliance_areas: List[str]
    
    # Qualitäts-Indikatoren
    content_quality_score: float
    completeness_score: float
    clarity_score: float
    
    # AI-Analyse
    ai_confidence: float
    ai_processing_time: float
    ai_methodology: str
    
    # Version & Tracking
    extraction_version: str = "2.0"
    processed_timestamp: Optional[str] = None

class AdvancedAIMetadataExtractor:
    """
    🤖 Enterprise-Grade AI Metadata Extractor
    
    Features:
    - Multi-Layer Content Analysis
    - QM-Domain Expert Knowledge
    - Advanced Pattern Recognition
    - Structured Data Extraction
    - Quality Scoring
    """
    
    def __init__(self):
        self.client = None
        self.is_initialized = False
        self.model_name = "gemini-1.5-flash"
        self.extraction_prompts = self._create_extraction_prompts()
        
        # QM Domain Knowledge
        self.qm_patterns = self._initialize_qm_patterns()
        self.iso_standards = self._initialize_iso_standards()
        self.regulatory_patterns = self._initialize_regulatory_patterns()
        
    async def initialize(self):
        """🔧 Initialisiert Advanced AI Metadata Extractor"""
        try:
            logger.info("🤖 Initialisiere Advanced AI Metadata Extractor...")
            
            # Google Gemini Setup
            api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_GEMINI_API_KEY nicht gefunden")
            
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model_name)
            
            # Test API Connection
            test_response = self.client.generate_content("Test")
            logger.info(f"✅ Gemini API erfolgreich verbunden: {self.model_name}")
            
            self.is_initialized = True
            logger.info("🎉 Advanced AI Metadata Extractor erfolgreich initialisiert")
            
        except Exception as e:
            logger.error(f"❌ Initialisierung fehlgeschlagen: {e}")
            self.is_initialized = False
            raise
    
    def _create_extraction_prompts(self) -> Dict[str, str]:
        """Erstellt erweiterte AI-Prompts für verschiedene Analyseebenen"""
        return {
            "document_analysis": """
Du bist ein Experte für Qualitätsmanagement-Systeme und Dokumentenanalyse. 
Analysiere das folgende Dokument umfassend und strukturiert.

DOKUMENT:
{content}

ANALYSE-AUFGABEN:
1. DOKUMENTTYP-KLASSIFIZIERUNG:
   - Bestimme den exakten Dokumenttyp (QM_MANUAL, SOP, STANDARD_NORM, etc.)
   - Begründe deine Klassifizierung

2. TITEL-EXTRAKTION:
   - Extrahiere den offiziellen Titel
   - Falls kein Titel vorhanden, generiere einen passenden

3. BESCHREIBUNG:
   - Erstelle eine präzise 2-3 Satz Beschreibung
   - Fokus auf Zweck und Hauptinhalt

4. KATEGORISIERUNG:
   - Hauptkategorie (z.B. "Qualitätsmanagement", "Normen", "Prozesse")
   - Unterkategorie (spezifischer)
   - Prozessbereich (falls zutreffend)

Antworte im JSON-Format:
{{
    "document_type": "...",
    "title": "...",
    "description": "...",
    "main_category": "...",
    "sub_category": "...",
    "process_area": "...",
    "reasoning": "..."
}}
""",
            
            "keyword_extraction": """
Du bist ein QM-Spezialist. Extrahiere Keywords aus diesem Dokument:

DOKUMENT:
{content}

KEYWORD-KATEGORIEN:
1. PRIMARY_KEYWORDS (3-5): Wichtigste Begriffe des Dokuments
2. SECONDARY_KEYWORDS (5-8): Unterstützende Begriffe  
3. QM_KEYWORDS: QM-spezifische Fachbegriffe
4. COMPLIANCE_KEYWORDS: Regulatory/Compliance Begriffe

Antwort als JSON:
{{
    "primary_keywords": [...],
    "secondary_keywords": [...], 
    "qm_keywords": [...],
    "compliance_keywords": [...]
}}
""",

            "structure_analysis": """
Analysiere die Struktur dieses Dokuments:

DOKUMENT:
{content}

STRUKTUR-ANALYSE:
1. Erkannte Abschnitte/Kapitel
2. Vorhandensein von Tabellen
3. Vorhandensein von Abbildungen
4. Anhänge vorhanden
5. Numerierung/Gliederung

JSON-Antwort:
{{
    "sections_detected": [...],
    "has_tables": true/false,
    "has_figures": true/false, 
    "has_appendices": true/false,
    "structure_type": "...",
    "numbering_scheme": "..."
}}
""",

            "compliance_analysis": """
Du bist ein Regulatory Affairs Experte. Analysiere Compliance-Aspekte:

DOKUMENT:
{content}

COMPLIANCE-ANALYSE:
1. Referenzierte ISO Standards
2. Regulatory Referenzen (FDA, MDR, etc.)
3. Compliance-Bereiche
4. Normenbezug

JSON-Antwort:
{{
    "iso_standards_referenced": [...],
    "regulatory_references": [...],
    "compliance_areas": [...],
    "standards_compliance_level": "..."
}}
""",

            "quality_assessment": """
Bewerte die Qualität dieses Dokuments als QM-Experte:

DOKUMENT:
{content}

QUALITÄTS-BEWERTUNG (0.0-1.0):
1. CONTENT_QUALITY: Inhaltliche Qualität und Fachlichkeit
2. COMPLETENESS: Vollständigkeit der Informationen  
3. CLARITY: Klarheit und Verständlichkeit

JSON-Antwort:
{{
    "content_quality_score": 0.0-1.0,
    "completeness_score": 0.0-1.0,
    "clarity_score": 0.0-1.0,
    "overall_assessment": "...",
    "improvement_suggestions": [...]
}}
"""
        }
    
    def _initialize_qm_patterns(self) -> Dict[str, List[str]]:
        """QM-Domain-spezifische Muster und Begriffe"""
        return {
            "quality_management": [
                "Qualitätsmanagement", "QM", "Quality Management", "QMS",
                "Qualitätssicherung", "Quality Assurance", "QA",
                "Qualitätskontrolle", "Quality Control", "QC"
            ],
            "processes": [
                "Prozess", "Verfahren", "Ablauf", "Workflow", "Procedure",
                "Standard Operating Procedure", "SOP", "Arbeitsanweisung"
            ],
            "documentation": [
                "Dokumentation", "Dokument", "Handbuch", "Manual",
                "Richtlinie", "Policy", "Anweisung", "Instruction"
            ],
            "audit": [
                "Audit", "Überprüfung", "Prüfung", "Assessment", "Review",
                "Kontrolle", "Inspection", "Bewertung"
            ],
            "validation": [
                "Validierung", "Validation", "Verifizierung", "Verification",
                "Qualifizierung", "Qualification", "Test", "Testing"
            ]
        }
    
    def _initialize_iso_standards(self) -> List[str]:
        """Bekannte ISO Standards für QM/Medizinprodukte"""
        return [
            "ISO 13485", "ISO 14971", "ISO 62304", "ISO 10993",
            "ISO 11607", "ISO 15223", "ISO 20417", "ISO 27001",
            "ISO 9001", "ISO 14155", "ISO 62366", "ISO 14708"
        ]
    
    def _initialize_regulatory_patterns(self) -> Dict[str, List[str]]:
        """Regulatory/Compliance Muster"""
        return {
            "fda": ["FDA", "21 CFR", "510(k)", "PMA", "QSR", "CDRH"],
            "eu": ["MDR", "MDD", "IVDR", "CE", "Notified Body", "EUDAMED"],
            "iso": ["ISO", "IEC", "EN", "DIN", "ANSI"],
            "gmp": ["GMP", "Good Manufacturing Practice", "cGMP"]
        }
    
    async def extract_advanced_metadata(
        self, 
        content: str, 
        document_id: Optional[int] = None,
        filename: Optional[str] = None
    ) -> AdvancedMetadata:
        """
        🔧 Führt erweiterte AI-basierte Metadaten-Extraktion durch
        
        Multi-Layer Analysis:
        1. Document Analysis (Type, Title, Description)
        2. Keyword Extraction (Multiple Categories) 
        3. Structure Analysis (Sections, Tables, etc.)
        4. Compliance Analysis (Standards, Regulatory)
        5. Quality Assessment (Scores, Recommendations)
        """
        start_time = time.time()
        
        try:
            if not self.is_initialized:
                await self.initialize()
            
            logger.info(f"🤖 Starte erweiterte Metadaten-Extraktion für Dokument {document_id}")
            
            # Content Preprocessing
            processed_content = self._preprocess_content(content)
            
            # Multi-Layer AI Analysis
            analysis_results = await self._perform_multilayer_analysis(processed_content)
            
            # Pattern-based Enhancement
            enhanced_results = self._enhance_with_patterns(processed_content, analysis_results)
            
            # Quality Assessment
            quality_scores = await self._assess_document_quality(processed_content)
            
            # Structure Advanced Metadata
            metadata = self._create_advanced_metadata(
                enhanced_results, 
                quality_scores,
                start_time,
                document_id,
                filename
            )
            
            processing_time = time.time() - start_time
            metadata.ai_processing_time = processing_time
            metadata.processed_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"✅ Erweiterte Metadaten-Extraktion abgeschlossen in {processing_time:.2f}s")
            logger.info(f"📊 Erkannter Typ: {metadata.document_type.value}")
            logger.info(f"📊 Qualitäts-Score: {metadata.content_quality_score:.2f}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Erweiterte Metadaten-Extraktion fehlgeschlagen: {e}")
            # Fallback zu Basis-Metadaten
            return self._create_fallback_metadata(content, str(e), time.time() - start_time)
    
    def _preprocess_content(self, content: str) -> str:
        """Erweiterte Content-Vorverarbeitung"""
        # Text Normalisierung
        content = re.sub(r'\s+', ' ', content)  # Multiple whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)  # Multiple newlines
        
        # OCR Error Correction
        content = content.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
        content = content.replace('„', '"').replace('"', '"')
        
        # Length Management (Gemini Token Limits)
        max_length = 30000  # Conservative limit
        if len(content) > max_length:
            # Intelligent truncation - keep beginning and end
            start_part = content[:max_length//2]
            end_part = content[-max_length//2:]
            content = start_part + "\n\n[... Mittelteil gekürzt ...]\n\n" + end_part
        
        return content.strip()
    
    async def _perform_multilayer_analysis(self, content: str) -> Dict[str, Any]:
        """Führt Multi-Layer AI-Analyse durch"""
        results = {}
        
        try:
            # Layer 1: Document Analysis
            logger.info("🔍 Layer 1: Document Analysis...")
            doc_analysis = await self._ai_analysis(
                self.extraction_prompts["document_analysis"].format(content=content)
            )
            results["document_analysis"] = doc_analysis
            
            # Layer 2: Keyword Extraction  
            logger.info("🔍 Layer 2: Keyword Extraction...")
            keyword_analysis = await self._ai_analysis(
                self.extraction_prompts["keyword_extraction"].format(content=content)
            )
            results["keyword_analysis"] = keyword_analysis
            
            # Layer 3: Structure Analysis
            logger.info("🔍 Layer 3: Structure Analysis...")
            structure_analysis = await self._ai_analysis(
                self.extraction_prompts["structure_analysis"].format(content=content)
            )
            results["structure_analysis"] = structure_analysis
            
            # Layer 4: Compliance Analysis
            logger.info("🔍 Layer 4: Compliance Analysis...")
            compliance_analysis = await self._ai_analysis(
                self.extraction_prompts["compliance_analysis"].format(content=content)
            )
            results["compliance_analysis"] = compliance_analysis
            
            # Layer 5: Quality Assessment
            logger.info("🔍 Layer 5: Quality Assessment...")
            quality_analysis = await self._ai_analysis(
                self.extraction_prompts["quality_assessment"].format(content=content)
            )
            results["quality_analysis"] = quality_analysis
            
            return results
            
        except Exception as e:
            logger.warning(f"⚠️ Multi-Layer Analysis teilweise fehlgeschlagen: {e}")
            return results  # Return partial results
    
    async def _ai_analysis(self, prompt: str) -> Dict[str, Any]:
        """Führt einzelne AI-Analyse durch mit Fehlerbehandlung"""
        try:
            if not self.client:
                raise RuntimeError("AI Client nicht initialisiert")
            
            response = self.client.generate_content(prompt)
            response_text = response.text
            
            # JSON Parsing mit Fehlerbehandlung
            try:
                # Clean response (remove markdown formatting)
                json_text = re.sub(r'^```json\s*', '', response_text)
                json_text = re.sub(r'\s*```$', '', json_text)
                
                result = json.loads(json_text)
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ JSON Parsing fehlgeschlagen: {e}")
                # Fallback: Extract key information manually
                return self._manual_extract_from_response(response_text)
                
        except Exception as e:
            logger.error(f"❌ AI Analysis fehlgeschlagen: {e}")
            return {}
    
    def _manual_extract_from_response(self, response_text: str) -> Dict[str, Any]:
        """Manueller Fallback für AI Response Parsing"""
        result = {}
        
        # Extract common patterns
        if "document_type" in response_text.lower():
            type_match = re.search(r'"document_type":\s*"([^"]+)"', response_text)
            if type_match:
                result["document_type"] = type_match.group(1)
        
        if "title" in response_text.lower():
            title_match = re.search(r'"title":\s*"([^"]+)"', response_text)
            if title_match:
                result["title"] = title_match.group(1)
        
        return result
    
    def _enhance_with_patterns(self, content: str, ai_results: Dict[str, Any]) -> Dict[str, Any]:
        """Erweitert AI-Ergebnisse mit Pattern-basierter Analyse"""
        enhanced = ai_results.copy()
        
        # QM Pattern Detection
        detected_qm_patterns = []
        content_lower = content.lower()
        
        for category, patterns in self.qm_patterns.items():
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    detected_qm_patterns.append(pattern)
        
        enhanced["detected_qm_patterns"] = detected_qm_patterns
        
        # ISO Standard Detection
        detected_iso = []
        for iso_std in self.iso_standards:
            if iso_std.lower() in content_lower:
                detected_iso.append(iso_std)
        
        enhanced["detected_iso_standards"] = detected_iso
        
        # Regulatory Pattern Detection
        detected_regulatory = []
        for category, patterns in self.regulatory_patterns.items():
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    detected_regulatory.append(pattern)
        
        enhanced["detected_regulatory"] = detected_regulatory
        
        return enhanced
    
    async def _assess_document_quality(self, content: str) -> Dict[str, float]:
        """Erweiterte Qualitätsbewertung"""
        scores = {
            "content_quality_score": 0.7,  # Default
            "completeness_score": 0.7,
            "clarity_score": 0.7
        }
        
        try:
            # Length-based assessment
            if len(content) < 200:
                scores["completeness_score"] = 0.3
            elif len(content) > 2000:
                scores["completeness_score"] = 0.9
            
            # Structure-based assessment
            sections = len(re.findall(r'\n\s*\d+\.', content))
            if sections > 3:
                scores["content_quality_score"] += 0.1
            
            # QM Keywords presence
            qm_keyword_count = sum(1 for category in self.qm_patterns.values() 
                                 for pattern in category 
                                 if pattern.lower() in content.lower())
            
            if qm_keyword_count > 5:
                scores["content_quality_score"] += 0.1
            
            # Normalize scores
            for key in scores:
                scores[key] = min(1.0, max(0.0, scores[key]))
            
        except Exception as e:
            logger.warning(f"⚠️ Quality Assessment fehlgeschlagen: {e}")
        
        return scores
    
    def _create_advanced_metadata(
        self, 
        analysis_results: Dict[str, Any],
        quality_scores: Dict[str, float],
        start_time: float,
        document_id: Optional[int],
        filename: Optional[str]
    ) -> AdvancedMetadata:
        """Erstellt strukturierte Advanced Metadata"""
        
        # Extract from AI analysis with fallbacks
        doc_analysis = analysis_results.get("document_analysis", {})
        keyword_analysis = analysis_results.get("keyword_analysis", {})
        structure_analysis = analysis_results.get("structure_analysis", {})
        compliance_analysis = analysis_results.get("compliance_analysis", {})
        
        # Document Type Classification
        doc_type_str = doc_analysis.get("document_type", "OTHER")
        try:
            document_type = DocumentTypeClassification(doc_type_str)
        except ValueError:
            document_type = DocumentTypeClassification.OTHER
        
        # Create Advanced Metadata
        metadata = AdvancedMetadata(
            # Basis
            title=doc_analysis.get("title", filename or f"Dokument {document_id}" or "Unbekanntes Dokument"),
            document_type=document_type,
            description=doc_analysis.get("description", "Automatisch extrahiertes QM-Dokument"),
            
            # Kategorisierung
            main_category=doc_analysis.get("main_category", "Unbekannt"),
            sub_category=doc_analysis.get("sub_category", "Unbekannt"),
            process_area=doc_analysis.get("process_area", "Allgemein"),
            
            # Keywords
            primary_keywords=keyword_analysis.get("primary_keywords", []),
            secondary_keywords=keyword_analysis.get("secondary_keywords", []),
            qm_keywords=keyword_analysis.get("qm_keywords", analysis_results.get("detected_qm_patterns", [])),
            compliance_keywords=keyword_analysis.get("compliance_keywords", analysis_results.get("detected_regulatory", [])),
            
            # Struktur
            document_structure=structure_analysis,
            sections_detected=structure_analysis.get("sections_detected", []),
            has_tables=structure_analysis.get("has_tables", False),
            has_figures=structure_analysis.get("has_figures", False),
            has_appendices=structure_analysis.get("has_appendices", False),
            
            # Compliance
            iso_standards_referenced=compliance_analysis.get("iso_standards_referenced", analysis_results.get("detected_iso_standards", [])),
            regulatory_references=compliance_analysis.get("regulatory_references", []),
            compliance_areas=compliance_analysis.get("compliance_areas", []),
            
            # Qualität
            content_quality_score=quality_scores.get("content_quality_score", 0.7),
            completeness_score=quality_scores.get("completeness_score", 0.7),
            clarity_score=quality_scores.get("clarity_score", 0.7),
            
            # AI
            ai_confidence=self._calculate_ai_confidence(analysis_results),
            ai_processing_time=0.0,  # Will be set later
            ai_methodology="multilayer_analysis_with_pattern_enhancement"
        )
        
        return metadata
    
    def _calculate_ai_confidence(self, analysis_results: Dict[str, Any]) -> float:
        """Berechnet AI-Konfidenz basierend auf Analyse-Vollständigkeit"""
        total_layers = 5
        completed_layers = len([k for k in analysis_results.keys() if analysis_results[k]])
        
        base_confidence = completed_layers / total_layers
        
        # Bonus für vollständige Ergebnisse
        if analysis_results.get("document_analysis", {}).get("document_type"):
            base_confidence += 0.1
        if analysis_results.get("keyword_analysis", {}).get("primary_keywords"):
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _create_fallback_metadata(self, content: str, error_msg: str, processing_time: float) -> AdvancedMetadata:
        """Erstellt Fallback-Metadaten bei AI-Fehlern"""
        logger.warning(f"⚠️ Erstelle Fallback-Metadaten: {error_msg}")
        
        # Basic pattern-based analysis
        title = "Automatisch extrahiertes Dokument"
        if "iso" in content.lower():
            title = "ISO Standard Dokument"
            doc_type = DocumentTypeClassification.ISO_STANDARD
        elif "sop" in content.lower() or "standard operating" in content.lower():
            title = "Standard Operating Procedure"
            doc_type = DocumentTypeClassification.SOP
        elif "manual" in content.lower() or "handbuch" in content.lower():
            title = "QM Handbuch"
            doc_type = DocumentTypeClassification.QM_MANUAL
        else:
            doc_type = DocumentTypeClassification.OTHER
        
        return AdvancedMetadata(
            title=title,
            document_type=doc_type,
            description="Dokument mit Basis-Metadaten (AI-Extraktion fehlgeschlagen)",
            main_category="Unbekannt",
            sub_category="Unbekannt", 
            process_area="Allgemein",
            primary_keywords=[],
            secondary_keywords=[],
            qm_keywords=[],
            compliance_keywords=[],
            document_structure={},
            sections_detected=[],
            has_tables=False,
            has_figures=False,
            has_appendices=False,
            iso_standards_referenced=[],
            regulatory_references=[],
            compliance_areas=[],
            content_quality_score=0.5,
            completeness_score=0.5,
            clarity_score=0.5,
            ai_confidence=0.1,
            ai_processing_time=processing_time,
            ai_methodology="fallback_pattern_based",
            processed_timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

# Global Instance
advanced_metadata_extractor = AdvancedAIMetadataExtractor()

# Convenience Functions
async def extract_advanced_metadata(
    content: str, 
    document_id: Optional[int] = None,
    filename: Optional[str] = None
) -> AdvancedMetadata:
    """🤖 Erweiterte AI-Metadaten-Extraktion"""
    return await advanced_metadata_extractor.extract_advanced_metadata(content, document_id, filename)

async def initialize_advanced_extractor():
    """🔧 Initialisiert Advanced Metadata Extractor"""
    await advanced_metadata_extractor.initialize()

# Legacy-kompatible Funktion für bestehende Imports
async def extract_document_metadata(
    content: str, 
    document_id: Optional[int] = None,
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """🔄 Legacy-kompatible Metadaten-Extraktion (für main.py Import)"""
    try:
        metadata = await extract_advanced_metadata(content, document_id, filename)
        
        # Konvertiere zu Legacy-Format
        return {
            "title": metadata.title,
            "document_type": metadata.document_type.value,
            "description": metadata.description,
            "keywords": metadata.primary_keywords + metadata.secondary_keywords,
            "qm_keywords": metadata.qm_keywords,
            "compliance_keywords": metadata.compliance_keywords,
            "iso_standards": metadata.iso_standards_referenced,
            "quality_score": metadata.content_quality_score,
            "ai_confidence": metadata.ai_confidence,
            "processing_time": metadata.ai_processing_time
        }
    except Exception as e:
        logger.error(f"❌ Legacy Metadata Extraction fehlgeschlagen: {e}")
        return {
            "title": filename or "Dokument",
            "document_type": "OTHER",
            "description": "Basis-Metadaten (Fehler bei AI-Extraktion)",
            "keywords": [],
            "qm_keywords": [],
            "compliance_keywords": [],
            "iso_standards": [],
            "quality_score": 0.5,
            "ai_confidence": 0.1,
            "processing_time": 0.0
        } 