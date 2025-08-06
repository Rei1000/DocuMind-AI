"""
Word Extraction Engine - Zweistufige Wortextraktion mit LLM und OCR
==================================================================

Diese Engine implementiert eine robuste Wortextraktion für QMS-Dokumente:
1. LLM extrahiert alle Wörter ohne Kontext
2. OCR verifiziert und ergänzt fehlende Wörter
3. Fuzzy-Matching und Bereinigung
4. Qualitätsmetriken für RAG-Tauglichkeit

Autor: DocuMind-AI Team
Version: 1.0
"""

import logging
import re
import json
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
from datetime import datetime
import hashlib

# OCR und Fuzzy-Matching
try:
    from PIL import Image
    import pytesseract
    from fuzzywuzzy import fuzz, process
except ImportError:
    logging.warning("OCR-Abhängigkeiten nicht installiert. Nur LLM-Extraktion verfügbar.")
    pytesseract = None
    fuzz = None

# Logger konfigurieren
logger = logging.getLogger(__name__)

class WordExtractionEngine:
    """
    Engine für zweistufige Wortextraktion aus Dokumenten
    """
    
    def __init__(self):
        """Initialisiert die Word Extraction Engine"""
        self.min_word_length = 3
        # Fuzzy-Matching Schwelle (konfigurierbar über Umgebungsvariable)
        import os
        self.fuzzy_threshold = int(os.getenv('FUZZY_THRESHOLD', '85'))
        
        # Kritische Begriffe für QMS-Dokumente
        self.critical_terms = [
            "ISO", "13485", "MDR", "FDA", "QMS", "SOP", "CAPA",
            "Validierung", "Verifizierung", "Risiko", "Audit",
            "Konformität", "Prozess", "Dokumentation", "Freigabe"
        ]
        
        # Blacklist für typische OCR-Fehler
        self.blacklist_patterns = [
            r'^[0-9]+$',  # Nur Zahlen
            r'^[^a-zA-ZäöüÄÖÜß]+$',  # Keine Buchstaben
            r'^.{1,2}$',  # Zu kurz
        ]
        
        # OCR-Artefakte
        self.ocr_artifacts = {
            'cckinoniogs', 'Rovardimerdieeum', 'aaeesies', 
            'Deteadbemetime', 'espana', 'aka', 'Gers',
            'Glinther', 'lérung', 'Heber', 'pee', 'ies'
        }
        
        logger.info("📝 Word Extraction Engine initialisiert")
    
    async def extract_words_with_llm(self, image_bytes: bytes, provider: str = "openai_4o_mini") -> Dict[str, any]:
        """
        Extrahiert Wörter mit LLM (ohne Kontext/Reihenfolge)
        """
        try:
            from .vision_ocr_engine import VisionOCREngine
            
            vision_engine = VisionOCREngine()
            
            # Spezieller Prompt für reine Wortextraktion
            word_extraction_prompt = """
Du bist ein präziser Text-Extraktor. Deine Aufgabe ist es, ALLE sichtbaren Wörter aus dem Dokument zu extrahieren.

**WICHTIG:**
- Extrahiere JEDES sichtbare Wort (auch kleine Schrift, Randnotizen, etc.)
- KEINE Interpretation oder Kontext
- KEINE Duplikate
- Alphabetisch sortiert
- Mindestens 3 Zeichen pro Wort

**Ausgabe NUR als JSON:**
{
  "extracted_words": ["Wort1", "Wort2", "Wort3", ...],
  "total_words": 123
}
"""
            
            # Analyse mit Vision Engine
            result = await vision_engine.analyze_document_with_api_prompt(
                images=[image_bytes],
                document_type="PROCESS",  # Verwende gültigen Dokumenttyp
                preferred_provider=provider,
                custom_prompt=word_extraction_prompt
            )
            
            if result.get('success'):
                # Parse JSON aus Antwort
                try:
                    analysis = result.get('analysis', '{}')
                    if isinstance(analysis, str):
                        word_data = json.loads(analysis)
                    else:
                        word_data = analysis
                    
                    return {
                        'success': True,
                        'words': word_data.get('extracted_words', []),
                        'count': word_data.get('total_words', 0),
                        'provider': provider,
                        'method': 'llm'
                    }
                except json.JSONDecodeError:
                    # Fallback: Extrahiere Wörter aus Text
                    text = str(analysis)
                    words = re.findall(r'\b[A-Za-zÄäÖöÜüß]{3,}\b', text)
                    unique_words = sorted(set(words), key=lambda w: w.lower())
                    
                    return {
                        'success': True,
                        'words': unique_words,
                        'count': len(unique_words),
                        'provider': provider,
                        'method': 'llm_fallback'
                    }
            
            return {
                'success': False,
                'error': 'LLM-Extraktion fehlgeschlagen',
                'words': [],
                'count': 0
            }
            
        except Exception as e:
            logger.error(f"❌ LLM-Wortextraktion fehlgeschlagen: {e}")
            return {
                'success': False,
                'error': str(e),
                'words': [],
                'count': 0
            }
    
    async def extract_words_with_ocr(self, image_bytes: bytes) -> Dict[str, any]:
        """
        Extrahiert Wörter mit OCR (Tesseract)
        """
        if not pytesseract:
            return {
                'success': False,
                'error': 'OCR nicht verfügbar',
                'words': [],
                'count': 0
            }
        
        try:
            # Bytes zu PIL Image
            import io
            img = Image.open(io.BytesIO(image_bytes))
            
            # OCR ausführen
            raw_text = pytesseract.image_to_string(img, lang='deu')
            
            # Wörter extrahieren
            words_raw = re.findall(r'\b[\wÄÖÜäöüß\-\/\.\(\)]+', raw_text)
            unique_words = sorted(set(words_raw), key=lambda w: w.lower())
            
            # Bereinigung
            cleaned_words = self._clean_ocr_words(unique_words)
            
            return {
                'success': True,
                'words': cleaned_words,
                'count': len(cleaned_words),
                'method': 'ocr'
            }
            
        except Exception as e:
            logger.error(f"❌ OCR-Extraktion fehlgeschlagen: {e}")
            return {
                'success': False,
                'error': str(e),
                'words': [],
                'count': 0
            }
    
    def _clean_ocr_words(self, words: List[str]) -> List[str]:
        """
        Bereinigt OCR-extrahierte Wörter
        """
        cleaned = []
        
        for word in words:
            # Längenprüfung
            if len(word) < self.min_word_length:
                continue
            
            # Blacklist-Patterns
            skip = False
            for pattern in self.blacklist_patterns:
                if re.match(pattern, word):
                    skip = True
                    break
            
            if skip:
                continue
            
            # OCR-Artefakte
            if word.lower() in self.ocr_artifacts:
                continue
            
            # Wort ist gültig
            cleaned.append(word)
        
        return cleaned
    
    async def merge_and_verify_words(
        self, 
        llm_words: List[str], 
        ocr_words: List[str],
        structured_json: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Kombiniert LLM- und OCR-Wörter und verifiziert gegen strukturierte JSON
        """
        # Normalisiere alle Wörter (lowercase)
        llm_set = {w.lower() for w in llm_words}
        ocr_set = {w.lower() for w in ocr_words}
        
        # Kombiniere Wortlisten
        all_words = llm_set.union(ocr_set)
        
        # Extrahiere Wörter aus strukturierter JSON
        json_words = self._extract_words_from_json(structured_json)
        json_set = {w.lower() for w in json_words}
        
        # Berechne Metriken
        coverage = len(json_set.intersection(all_words)) / len(json_set) * 100 if json_set else 0
        
        # Fehlende Wörter identifizieren
        missing_in_extraction = json_set - all_words
        missing_in_json = all_words - json_set
        
        # Fuzzy-Matching für fehlende Wörter
        fuzzy_matches = []
        if fuzz and missing_in_extraction:
            for missing_word in missing_in_extraction:
                match, score = process.extractOne(missing_word, list(all_words))
                if score >= self.fuzzy_threshold:
                    fuzzy_matches.append({
                        'original': missing_word,
                        'match': match,
                        'score': score
                    })
        
        # Kritische Begriffe prüfen
        critical_found = []
        critical_missing = []
        for term in self.critical_terms:
            term_lower = term.lower()
            if any(term_lower in word for word in all_words):
                critical_found.append(term)
            else:
                critical_missing.append(term)
        
        # Qualitätsbewertung
        quality_score = self._calculate_quality_score(
            coverage, 
            len(critical_found), 
            len(self.critical_terms),
            len(fuzzy_matches)
        )
        
        # Finale Wortliste
        final_words = sorted(all_words.union({w.lower() for w in self.critical_terms}))
        
        return {
            'success': True,
            'final_words': final_words,
            'total_words': len(final_words),
            'metrics': {
                'llm_words': len(llm_set),
                'ocr_words': len(ocr_set),
                'combined_words': len(all_words),
                'json_words': len(json_set),
                'coverage_percentage': round(coverage, 2),
                'missing_in_extraction': list(missing_in_extraction),
                'missing_in_json': list(missing_in_json)[:20],  # Limit für Übersichtlichkeit
                'fuzzy_matches': fuzzy_matches,
                'critical_terms_found': critical_found,
                'critical_terms_missing': critical_missing
            },
            'quality': {
                'score': quality_score,
                'rag_ready': quality_score >= 85,
                'completeness': 'vollständig' if coverage >= 95 else 'teilweise' if coverage >= 80 else 'unvollständig',
                'recommendations': self._get_recommendations(quality_score, coverage, critical_missing)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_words_from_json(self, json_data: Dict) -> List[str]:
        """
        Extrahiert alle Wörter aus der strukturierten JSON
        """
        words = []
        
        def extract_from_value(value):
            if isinstance(value, str):
                # Extrahiere Wörter aus String
                extracted = re.findall(r'\b[A-Za-zÄäÖöÜüß]{3,}\b', value)
                words.extend(extracted)
            elif isinstance(value, list):
                for item in value:
                    extract_from_value(item)
            elif isinstance(value, dict):
                for v in value.values():
                    extract_from_value(v)
        
        extract_from_value(json_data)
        return list(set(words))
    
    def _calculate_quality_score(
        self, 
        coverage: float, 
        critical_found: int, 
        critical_total: int,
        fuzzy_matches: int
    ) -> float:
        """
        Berechnet Qualitätsscore für RAG-Tauglichkeit
        """
        # Gewichtung
        coverage_weight = 0.5
        critical_weight = 0.3
        fuzzy_weight = 0.2
        
        # Scores
        coverage_score = min(coverage, 100)
        critical_score = (critical_found / critical_total * 100) if critical_total > 0 else 100
        fuzzy_penalty = max(0, 100 - (fuzzy_matches * 5))  # -5% pro Fuzzy-Match
        
        # Gesamtscore
        total_score = (
            coverage_score * coverage_weight +
            critical_score * critical_weight +
            fuzzy_penalty * fuzzy_weight
        )
        
        return round(total_score, 2)
    
    def _get_recommendations(
        self, 
        quality_score: float, 
        coverage: float,
        critical_missing: List[str]
    ) -> List[str]:
        """
        Erstellt Empfehlungen basierend auf Qualitätsmetriken
        """
        recommendations = []
        
        if quality_score < 85:
            recommendations.append("⚠️ Dokument sollte manuell überprüft werden")
        
        if coverage < 95:
            recommendations.append(f"📊 Wortabdeckung nur {coverage:.1f}% - Analyse könnte unvollständig sein")
        
        if critical_missing:
            recommendations.append(f"❌ Kritische Begriffe fehlen: {', '.join(critical_missing[:5])}")
        
        if quality_score >= 95:
            recommendations.append("✅ Dokument ist RAG-tauglich")
        
        return recommendations