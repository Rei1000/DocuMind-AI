"""
🔧 ENHANCED JSON PARSER für KI-QMS - Enterprise Grade v3.1.0
═══════════════════════════════════════════════════════════════

Robuster JSON Parser mit umfassenden Fallback-Mechanismen:

✅ FEATURES:
- 🛡️ 5-Layer Fallback-System für JSON-Parsing
- 🔍 Fuzzy-Matching für Partial JSON Recovery
- 📊 Strukturierte Error-Handling mit Logging
- 🎯 Schema-Validierung mit Pydantic Integration
- 🔄 Automatic Repair für Common JSON Errors
- 📈 Performance-Optimierung für Large Documents

🎯 FALLBACK STRATEGY:
1. Standard JSON Parse
2. Regex-basierte Reparatur
3. Partial JSON Extraction
4. Fuzzy Field Matching
5. Minimal Fallback Schema

Author: Enhanced AI Assistant
Version: 3.1.0 - Enterprise Edition
"""

import json
import re
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
import traceback

from pydantic import ValidationError
from schemas_enhanced import (
    EnhancedDocumentMetadata,
    EnhancedDocumentType,
    EnhancedKeyword,
    KeywordImportance,
    QualityScore,
    ComplianceLevel,
    normalize_document_type,
    create_fallback_metadata
)

# Setup Logging
logger = logging.getLogger(__name__)

class JSONParseError(Exception):
    """Custom Exception für JSON-Parsing-Fehler"""
    pass

class EnhancedJSONParser:
    """
    🎯 Enterprise-Grade JSON Parser mit 5-Layer Fallback-System
    
    Designed für robuste Metadaten-Extraktion aus AI-Responses mit:
    - Automatic JSON Repair
    - Fuzzy Field Matching
    - Schema Validation
    - Performance Monitoring
    """
    
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging
        self.parse_attempts = 0
        self.last_error = None
        self.performance_metrics = {
            'total_parses': 0,
            'successful_parses': 0,
            'fallback_uses': 0,
            'average_parse_time': 0.0
        }
    
    def parse_enhanced_metadata(self, 
                              json_response: str, 
                              document_title: str = "Unknown Document",
                              strict_mode: bool = False) -> EnhancedDocumentMetadata:
        """
        🎯 Hauptfunktion für Enhanced Metadata Parsing
        
        Args:
            json_response: AI-Response mit JSON-Struktur
            document_title: Fallback-Titel falls Parsing fehlschlägt
            strict_mode: Ob strenge Validierung verwendet werden soll
            
        Returns:
            EnhancedDocumentMetadata: Validierte Metadaten
        """
        start_time = datetime.now()
        self.parse_attempts = 0
        
        try:
            # Layer 1: Standard JSON Parse
            metadata = self._parse_standard_json(json_response)
            if metadata:
                self._log_success("Standard JSON Parse", start_time)
                return metadata
            
            # Layer 2: Regex-basierte Reparatur
            metadata = self._parse_with_regex_repair(json_response)
            if metadata:
                self._log_success("Regex Repair", start_time)
                return metadata
            
            # Layer 3: Partial JSON Extraction
            metadata = self._parse_partial_json(json_response)
            if metadata:
                self._log_success("Partial JSON", start_time)
                return metadata
            
            # Layer 4: Fuzzy Field Matching
            metadata = self._parse_fuzzy_matching(json_response)
            if metadata:
                self._log_success("Fuzzy Matching", start_time)
                return metadata
            
            # Layer 5: Minimal Fallback
            if not strict_mode:
                metadata = self._create_minimal_fallback(json_response, document_title)
                self._log_fallback("Minimal Fallback", start_time)
                return metadata
            
            raise JSONParseError("Alle Parsing-Versuche fehlgeschlagen")
            
        except Exception as e:
            self.last_error = str(e)
            if self.enable_logging:
                logger.error(f"JSON Parser Error: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
            
            if strict_mode:
                raise JSONParseError(f"Strict Mode: {e}")
            
            return create_fallback_metadata(document_title)
    
    def _parse_standard_json(self, json_response: str) -> Optional[EnhancedDocumentMetadata]:
        """Layer 1: Standard JSON Parsing"""
        self.parse_attempts += 1
        
        try:
            # Bereinige Response
            cleaned_json = self._clean_json_response(json_response)
            
            # Parse JSON
            data = json.loads(cleaned_json)
            
            # Validiere und konvertiere zu Pydantic Model
            return self._convert_to_enhanced_metadata(data)
            
        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            if self.enable_logging:
                logger.debug(f"Standard JSON Parse failed: {e}")
            return None
    
    def _parse_with_regex_repair(self, json_response: str) -> Optional[EnhancedDocumentMetadata]:
        """Layer 2: Regex-basierte JSON Reparatur"""
        self.parse_attempts += 1
        
        try:
            # Häufige JSON-Fehler reparieren
            repaired_json = self._repair_common_json_errors(json_response)
            
            # Parse repariertes JSON
            data = json.loads(repaired_json)
            
            return self._convert_to_enhanced_metadata(data)
            
        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            if self.enable_logging:
                logger.debug(f"Regex Repair failed: {e}")
            return None
    
    def _parse_partial_json(self, json_response: str) -> Optional[EnhancedDocumentMetadata]:
        """Layer 3: Partial JSON Extraction"""
        self.parse_attempts += 1
        
        try:
            # Extrahiere JSON-ähnliche Blöcke
            json_blocks = self._extract_json_blocks(json_response)
            
            for block in json_blocks:
                try:
                    data = json.loads(block)
                    # Prüfe ob genügend Felder vorhanden sind
                    if self._has_minimum_fields(data):
                        return self._convert_to_enhanced_metadata(data)
                except:
                    continue
            
            return None
            
        except Exception as e:
            if self.enable_logging:
                logger.debug(f"Partial JSON extraction failed: {e}")
            return None
    
    def _parse_fuzzy_matching(self, json_response: str) -> Optional[EnhancedDocumentMetadata]:
        """Layer 4: Fuzzy Field Matching"""
        self.parse_attempts += 1
        
        try:
            # Extrahiere Felder mit Regex-Patterns
            extracted_fields = self._extract_fields_with_regex(json_response)
            
            if len(extracted_fields) >= 3:  # Mindestens 3 Felder
                return self._convert_to_enhanced_metadata(extracted_fields)
            
            return None
            
        except Exception as e:
            if self.enable_logging:
                logger.debug(f"Fuzzy matching failed: {e}")
            return None
    
    def _create_minimal_fallback(self, json_response: str, document_title: str) -> EnhancedDocumentMetadata:
        """Layer 5: Minimal Fallback mit Text-Analyse"""
        self.parse_attempts += 1
        
        # Extrahiere was möglich ist aus dem Text
        extracted_info = self._extract_minimal_info(json_response)
        
        return EnhancedDocumentMetadata(
            title=extracted_info.get('title', document_title),
            document_type=normalize_document_type(extracted_info.get('document_type', 'OTHER')),
            description=extracted_info.get('description', 'Metadaten durch Fallback-Parser extrahiert'),
            main_category=extracted_info.get('main_category', 'Unknown'),
            sub_category=extracted_info.get('sub_category', 'Unknown'),
            process_area=extracted_info.get('process_area', 'General'),
            quality_scores=QualityScore(
                overall=0.4,
                content_quality=0.4,
                completeness=0.3,
                clarity=0.4,
                structure=0.4,
                compliance_readiness=0.3
            ),
            ai_confidence=0.2,
            ai_methodology="fallback_minimal_extraction"
        )
    
    def _clean_json_response(self, json_response: str) -> str:
        """Bereinigt JSON-Response von häufigen Problemen"""
        # Entferne Markdown-Blöcke
        cleaned = re.sub(r'```json\s*', '', json_response)
        cleaned = re.sub(r'```\s*$', '', cleaned)
        
        # Entferne führende/nachfolgende Whitespaces
        cleaned = cleaned.strip()
        
        # Entferne Kommentare
        cleaned = re.sub(r'//.*$', '', cleaned, flags=re.MULTILINE)
        
        return cleaned
    
    def _repair_common_json_errors(self, json_str: str) -> str:
        """Repariert häufige JSON-Syntax-Fehler"""
        repaired = json_str
        
        # Repariere trailing commas
        repaired = re.sub(r',\s*}', '}', repaired)
        repaired = re.sub(r',\s*]', ']', repaired)
        
        # Repariere fehlende Anführungszeichen bei Keys
        repaired = re.sub(r'(\w+):', r'"\1":', repaired)
        
        # Repariere single quotes zu double quotes
        repaired = re.sub(r"'([^']*)':", r'"\1":', repaired)
        
        # Repariere unescaped quotes in strings
        repaired = re.sub(r':\s*"([^"]*)"([^",}\]]*)"', r': "\1\2"', repaired)
        
        return repaired
    
    def _extract_json_blocks(self, text: str) -> List[str]:
        """Extrahiert JSON-ähnliche Blöcke aus Text"""
        # Finde alle { } Blöcke
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        return matches
    
    def _has_minimum_fields(self, data: Dict[str, Any]) -> bool:
        """Prüft ob JSON-Objekt Mindestfelder hat"""
        required_fields = ['title', 'document_type']
        return all(field in data for field in required_fields)
    
    def _extract_fields_with_regex(self, text: str) -> Dict[str, Any]:
        """Extrahiert Felder mit Regex-Patterns"""
        patterns = {
            'title': r'["\']?title["\']?\s*:\s*["\']([^"\']+)["\']',
            'document_type': r'["\']?document_type["\']?\s*:\s*["\']([^"\']+)["\']',
            'description': r'["\']?description["\']?\s*:\s*["\']([^"\']+)["\']',
            'main_category': r'["\']?main_category["\']?\s*:\s*["\']([^"\']+)["\']',
            'quality_score': r'["\']?quality_score["\']?\s*:\s*([0-9.]+)'
        }
        
        extracted = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[field] = match.group(1)
        
        return extracted
    
    def _extract_minimal_info(self, text: str) -> Dict[str, Any]:
        """Extrahiert minimale Informationen aus Text"""
        info = {}
        
        # Versuche häufige Patterns zu finden
        title_patterns = [
            r'titel?\s*[:\-]\s*(.+)',
            r'document\s*title\s*[:\-]\s*(.+)',
            r'name\s*[:\-]\s*(.+)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['title'] = match.group(1).strip()
                break
        
        # Dokumenttyp-Erkennung
        doc_type_keywords = {
            'procedure': 'QM_PROCEDURE',
            'work instruction': 'WORK_INSTRUCTION',
            'form': 'FORM',
            'manual': 'QM_MANUAL',
            'policy': 'QM_POLICY'
        }
        
        for keyword, doc_type in doc_type_keywords.items():
            if keyword.lower() in text.lower():
                info['document_type'] = doc_type
                break
        
        return info
    
    def _convert_to_enhanced_metadata(self, data: Dict[str, Any]) -> EnhancedDocumentMetadata:
        """Konvertiert Dict zu EnhancedDocumentMetadata mit Validierung"""
        # Normalisiere Dokumenttyp
        if 'document_type' in data:
            data['document_type'] = normalize_document_type(data['document_type'])
        
        # Konvertiere Keywords falls vorhanden
        if 'primary_keywords' in data and isinstance(data['primary_keywords'], list):
            keywords = []
            for kw in data['primary_keywords']:
                if isinstance(kw, str):
                    keywords.append(EnhancedKeyword(term=kw))
                elif isinstance(kw, dict):
                    keywords.append(EnhancedKeyword(**kw))
            data['primary_keywords'] = keywords
        
        # Konvertiere Quality Scores
        if 'quality_scores' in data and isinstance(data['quality_scores'], dict):
            data['quality_scores'] = QualityScore(**data['quality_scores'])
        
        # Setze Defaults für fehlende Felder
        defaults = {
            'main_category': 'Unknown',
            'sub_category': 'Unknown',
            'process_area': 'General',
            'description': 'Automatisch extrahierte Metadaten',
            'ai_confidence': 0.7,
            'ai_methodology': 'enhanced_json_parser'
        }
        
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        # Erstelle und validiere Pydantic Model
        return EnhancedDocumentMetadata(**data)
    
    def _log_success(self, method: str, start_time: datetime):
        """Loggt erfolgreiche Parsing-Versuche"""
        duration = (datetime.now() - start_time).total_seconds()
        self.performance_metrics['total_parses'] += 1
        self.performance_metrics['successful_parses'] += 1
        
        if self.enable_logging:
            logger.info(f"JSON Parser Success: {method} in {duration:.3f}s after {self.parse_attempts} attempts")
    
    def _log_fallback(self, method: str, start_time: datetime):
        """Loggt Fallback-Nutzung"""
        duration = (datetime.now() - start_time).total_seconds()
        self.performance_metrics['total_parses'] += 1
        self.performance_metrics['fallback_uses'] += 1
        
        if self.enable_logging:
            logger.warning(f"JSON Parser Fallback: {method} in {duration:.3f}s after {self.parse_attempts} attempts")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Gibt Performance-Metriken zurück"""
        total = self.performance_metrics['total_parses']
        if total > 0:
            success_rate = self.performance_metrics['successful_parses'] / total * 100
            fallback_rate = self.performance_metrics['fallback_uses'] / total * 100
        else:
            success_rate = 0
            fallback_rate = 0
        
        return {
            **self.performance_metrics,
            'success_rate': f"{success_rate:.1f}%",
            'fallback_rate': f"{fallback_rate:.1f}%",
            'last_error': self.last_error
        }


# Utility Functions
def parse_ai_response(json_response: str, 
                     document_title: str = "Unknown Document",
                     strict_mode: bool = False) -> EnhancedDocumentMetadata:
    """
    🎯 Convenience Function für AI-Response Parsing
    
    Args:
        json_response: AI-Response mit JSON-Struktur
        document_title: Fallback-Titel
        strict_mode: Strenge Validierung
        
    Returns:
        EnhancedDocumentMetadata: Validierte Metadaten
    """
    parser = EnhancedJSONParser()
    return parser.parse_enhanced_metadata(json_response, document_title, strict_mode)


def validate_json_response(json_response: str) -> Tuple[bool, Optional[str]]:
    """
    🔍 Validiert JSON-Response ohne Parsing
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        parser = EnhancedJSONParser(enable_logging=False)
        cleaned = parser._clean_json_response(json_response)
        json.loads(cleaned)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"JSON Syntax Error: {e}"
    except Exception as e:
        return False, f"Validation Error: {e}"


# Global Parser Instance für Performance
_global_parser = EnhancedJSONParser()

def get_global_parser() -> EnhancedJSONParser:
    """Gibt globale Parser-Instanz zurück"""
    return _global_parser