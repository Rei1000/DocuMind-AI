"""
Multi-Visio Engine - 5-Stufen Prompt-Chain für erweiterte Dokumentenvalidierung

Diese Engine implementiert eine 5-stufige Prompt-Chain für die Analyse von Dokumenten:
1. Bild übergeben & Kontext setzen
2. Strukturierte Analyse → JSON speichern
3. Textextraktion (OCR-ähnlich)
4. Verifikation (JSON vs. extrahierter Text)
5. Normkonformität (mit gespeicherter JSON)

Autor: DocuMind-AI Team
Version: 4.0 - 5-Stufen Prompt-Chain
"""

import json
import logging
import asyncio
import os
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .vision_ocr_engine import VisionOCREngine
from .word_extraction_engine import WordExtractionEngine

# Logger konfigurieren
logger = logging.getLogger(__name__)

class MultiVisioEngine:
    """
    Multi-Visio Engine - 5-Stufen Prompt-Chain mit Vision Engine
    """
    
    def __init__(self):
        """Initialisiert die Multi-Visio Engine"""
        # Verwende normale Vision Engine
        self.vision_engine = VisionOCREngine()
        
        # Word Extraction Engine
        self.word_engine = WordExtractionEngine()
        
        # Prompts laden
        self.prompts_dir = Path(__file__).parent / "multi_visio_prompts"
        self.prompts = self._load_prompts()
        
        # Cache für Bilder und Datei-Hashes
        self.cached_images = None
        self.cached_file_hash = None
        
        logger.info("🔍 Multi-Visio Engine v4.0 (5-Stufen Prompt-Chain) initialisiert")
    
    def _load_prompts(self) -> Dict[str, str]:
        """Lädt alle Multi-Visio Prompts"""
        prompts = {}
        
        try:
            # Stufe 1: Bild übergeben & Kontext setzen
            context_prompt_path = self.prompts_dir / "01_expert_induction.txt"
            if context_prompt_path.exists():
                with open(context_prompt_path, 'r', encoding='utf-8') as f:
                    prompts['context_setup'] = f.read()
                logger.info("📝 Prompt geladen: 01_expert_induction.txt")
            
            # Stufe 2: Strukturierte Analyse
            structured_analysis_prompt_path = self.prompts_dir / "02_structured_analysis.txt"
            if structured_analysis_prompt_path.exists():
                with open(structured_analysis_prompt_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    # Extrahiere den Prompt aus der Variable PROMPT_PROCESS_ANALYSE_EXTENDED
                    if 'PROMPT_PROCESS_ANALYSE_EXTENDED = """' in file_content:
                        start_marker = 'PROMPT_PROCESS_ANALYSE_EXTENDED = """'
                        start_idx = file_content.find(start_marker) + len(start_marker)
                        
                        # Finde das schließende """ aber ignoriere das erste (nach dem start_marker)
                        remaining_content = file_content[start_idx:]
                        end_idx = remaining_content.find('"""')
                        
                        if end_idx > 0:
                            extracted_prompt = remaining_content[:end_idx].strip()
                            prompts['structured_analysis'] = extracted_prompt
                            logger.info(f"✅ PROMPT_PROCESS_ANALYSE_EXTENDED extrahiert: {len(extracted_prompt)} Zeichen")
                        else:
                            prompts['structured_analysis'] = file_content
                            logger.warning("⚠️ Konnte PROMPT_PROCESS_ANALYSE_EXTENDED nicht extrahieren - verwende ganze Datei")
                    else:
                        prompts['structured_analysis'] = file_content
                        logger.warning("⚠️ PROMPT_PROCESS_ANALYSE_EXTENDED nicht gefunden - verwende ganze Datei")
                logger.info("📝 Prompt geladen: 02_structured_analysis.txt")
            
            # Stufe 3: Textextraktion
            text_extraction_prompt_path = self.prompts_dir / "03_word_coverage.txt"
            if text_extraction_prompt_path.exists():
                with open(text_extraction_prompt_path, 'r', encoding='utf-8') as f:
                    prompts['text_extraction'] = f.read()
                logger.info("📝 Prompt geladen: 03_word_coverage.txt")
            
            # Stufe 4: Verifikation (Backend-Logik - kein Prompt nötig)
            logger.info("📝 Stufe 4: Verifikation verwendet Backend-Logik")
            
            # Stufe 5: Normkonformität
            norm_compliance_prompt_path = self.prompts_dir / "05_norm_compliance.txt"
            if norm_compliance_prompt_path.exists():
                with open(norm_compliance_prompt_path, 'r', encoding='utf-8') as f:
                    prompts['norm_compliance'] = f.read()
                logger.info("📝 Prompt geladen: 05_norm_compliance.txt")
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Prompts: {e}")
        
        return prompts
    
    async def _get_or_convert_images(self, file_path: str) -> List[bytes]:
        """
        Cached Image Conversion - verhindert doppelte LibreOffice-Aufrufe
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            Liste der konvertierten Bilder (aus Cache oder neu konvertiert)
        """
        import hashlib
        
        # Berechne Datei-Hash für Cache-Validierung
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
                current_hash = hashlib.sha256(file_content).hexdigest()
        except Exception as e:
            logger.warning(f"⚠️ Kann Datei-Hash nicht berechnen: {e}")
            current_hash = f"{file_path}_{os.path.getmtime(file_path)}"
        
        # Prüfe Cache
        if self.cached_images and self.cached_file_hash == current_hash:
            logger.info(f"♻️ Verwende gecachte Bilder für {Path(file_path).name} (Hash: {current_hash[:8]}...)")
            return self.cached_images
        
        # Konvertiere neu und cache
        logger.info(f"🔄 Konvertiere Datei zu Bildern: {Path(file_path).name}")
        images = await self.vision_engine.convert_document_to_images(Path(file_path))
        
        if images:
            self.cached_images = images
            self.cached_file_hash = current_hash
            logger.info(f"📸 {len(images)} Bilder konvertiert und gecacht (Hash: {current_hash[:8]}...)")
        
        return images
    
    async def run_full_pipeline(
        self, 
        file_path: str,
        document_type: str,
        provider: str = "auto"
    ) -> Dict[str, Any]:
        """
        Führt 5-Stufen Prompt-Chain durch
        
        Args:
            file_path: Pfad zur Dokumentdatei
            document_type: Dokumenttyp (bleibt konstant)
            provider: AI-Provider (auto, openai, ollama, gemini)
            
        Returns:
            Dict mit allen 5 Stufen + Gesamtergebnis
        """
        try:
            logger.info(f"🔍 Multi-Visio Pipeline gestartet: {file_path} (Typ: {document_type})")
            start_time = datetime.now()
            
            # 1. Dokument zu Bildern konvertieren (mit Cache-Unterstützung)
            images = await self._get_or_convert_images(file_path)
            if not images:
                raise Exception("Dokument konnte nicht zu Bildern konvertiert werden")
            
            logger.info(f"📸 {len(images)} Bilder verfügbar für Pipeline")
            
            # Pipeline-Ergebnisse
            pipeline_results = {
                "document_type": document_type,
                "provider": provider,
                "stages": {},
                "pipeline_start": start_time.isoformat()
            }
            
            # Stufe 1: Bild übergeben & Kontext setzen (EINZIGER BILD-UPLOAD)
            logger.info("🔄 Stufe 1/5: Bild übergeben & Kontext setzen (EINZIGER BILD-UPLOAD)")
            stage1_result = await self._stage1_context_setup(self.cached_images, document_type, provider)
            pipeline_results["stages"]["context_setup"] = stage1_result
            
            if not stage1_result.get('success'):
                logger.error("❌ Pipeline abgebrochen: Stufe 1 fehlgeschlagen")
                return self._finalize_pipeline(pipeline_results, start_time, False)
            
            # Stufe 2: Strukturierte Analyse (MIT Multi-Visio Prompt)
            logger.info("🔄 Stufe 2/5: Strukturierte Analyse (MIT 02_structured_analysis.txt)")
            stage2_result = await self._stage2_structured_analysis(self.cached_images, document_type, provider)
            pipeline_results["stages"]["structured_analysis"] = stage2_result
            
            if not stage2_result.get('success'):
                logger.error("❌ Pipeline abgebrochen: Stufe 2 fehlgeschlagen")
                return self._finalize_pipeline(pipeline_results, start_time, False)
            
            # JSON-Daten für weitere Stufen extrahieren
            structured_json = self._extract_json_from_analysis(stage2_result)
            
            # Stufe 3: Textextraktion (TEXT-PROMPT ohne Bild)
            logger.info("🔄 Stufe 3/5: Textextraktion (TEXT-PROMPT)")
            stage3_result = await self._stage3_text_extraction_text_only(document_type, provider, stage1_result)
            pipeline_results["stages"]["text_extraction"] = stage3_result
            
            if not stage3_result.get('success'):
                logger.error("❌ Pipeline abgebrochen: Stufe 3 fehlgeschlagen")
                return self._finalize_pipeline(pipeline_results, start_time, False)
            
            # Stufe 4: Verifikation (Backend-Logik statt KI-Prompt)
            logger.info("🔄 Stufe 4/5: Verifikation (Backend-Logik)")
            stage4_result = await self._stage4_verification_backend(
                stage3_result, structured_json
            )
            pipeline_results["stages"]["verification"] = stage4_result
            
            # Stufe 5: Normkonformität (TEXT-PROMPT ohne Bild)
            logger.info("🔄 Stufe 5/5: Normkonformität (TEXT-PROMPT)")
            stage5_result = await self._stage5_norm_compliance_text_only(
                structured_json, document_type, provider, stage1_result
            )
            pipeline_results["stages"]["norm_compliance"] = stage5_result
            
            # Pipeline erfolgreich abgeschlossen
            return self._finalize_pipeline(pipeline_results, start_time, True)
            
        except Exception as e:
            logger.error(f"❌ Multi-Visio Pipeline Fehler: {e}")
            return {
                'success': False,
                'error': str(e),
                'methodology': '5_stage_prompt_chain'
            }
    
    async def _stage1_context_setup(self, images: List[bytes], document_type: str, provider: str) -> Dict[str, Any]:
        """Stufe 1: Bild übergeben & Kontext setzen"""
        try:
            start_time = datetime.now()
            
            # Verwende normale Vision Engine mit speziellem Prompt
            context_prompt = self.prompts.get('context_setup', 'Du bist ein KI-Experte für QMS-Dokumentenanalyse.')
            
            # Erstelle temporären Prompt für Kontext-Setup
            temp_prompt = f"""
{context_prompt}

**AUFGABE:** 
Das Prozessdiagramm (als PNG) wird dir einmalig übergeben.
Merke dir das Bild für alle kommenden Aufgaben.
Es findet noch keine Analyse statt – nur die Vorbereitung.

**BESTÄTIGUNG:** Bestätige den Erhalt des Bildes und dass du bereit bist für die Analyse.

[Bild wird übergeben]
"""
            
            # Verwende Vision Engine mit angepasstem Prompt
            result = await self.vision_engine.analyze_document_with_api_prompt(
                images=images,
                document_type=document_type,
                preferred_provider=provider,
                custom_prompt=temp_prompt
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": result.get('success', False),
                "stage": "context_setup",
                "response": result.get('analysis', ''),  # ✅ Verwende 'analysis' statt 'content'
                "provider_used": provider,
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"❌ Stufe 1 fehlgeschlagen: {e}")
            return {
                "success": False,
                "stage": "context_setup",
                "error": str(e)
            }
    
    async def _stage2_structured_analysis(self, images: List[bytes], document_type: str, provider: str) -> Dict[str, Any]:
        """Stufe 2: Strukturierte JSON-Analyse"""
        try:
            start_time = datetime.now()
            
            # Hole den spezialisierten Multi-Visio Prompt für Stufe 2
            structured_analysis_prompt = self.prompts.get('structured_analysis', '')
            if not structured_analysis_prompt:
                logger.warning("⚠️ Stufe 2 Prompt nicht gefunden - verwende Fallback")
                structured_analysis_prompt = "Analysiere das Dokument und gib eine strukturierte JSON-Analyse zurück."
            else:
                logger.info(f"✅ Stufe 2: Multi-Visio Prompt geladen ({len(structured_analysis_prompt)} Zeichen)")
                logger.info(f"🔍 Prompt-Anfang: {structured_analysis_prompt[:100]}...")
            
            # Verwende Vision Engine mit Multi-Visio Prompt
            result = await self.vision_engine.analyze_document_with_api_prompt(
                images=images,
                document_type=document_type,
                preferred_provider=provider,
                custom_prompt=structured_analysis_prompt
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": result.get('success', False),
                "stage": "structured_analysis",
                "response": result.get('analysis', ''),  # ✅ Verwende 'analysis' statt 'content'
                "json_data": self._extract_json_from_analysis(result),
                "provider_used": provider,
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"❌ Stufe 2 fehlgeschlagen: {e}")
            return {
                "success": False,
                "stage": "structured_analysis",
                "error": str(e)
            }
    
    async def _stage3_text_extraction(self, images: List[bytes], document_type: str, provider: str) -> Dict[str, Any]:
        """Stufe 3: Textextraktion (OCR-ähnlich)"""
        try:
            start_time = datetime.now()
            
            text_extraction_prompt = self.prompts.get('text_extraction', 'Du bist ein OCR-Experte.')
            
            temp_prompt = f"""
{text_extraction_prompt}

**AUFGABE:** 
Extrahiere alle sichtbaren Wörter, Symbole und Zeichen aus dem Diagramm.
Die Ausgabe ist eine alphabetisch sortierte, eindeutige Liste (ähnlich OCR).
Kein Verständnis, keine Interpretation – nur sichtbarer Text.

**AUSGABE:** Liste aller extrahierten Wörter, alphabetisch sortiert.

[Bild wird übergeben]
"""
            
            result = await self.vision_engine.analyze_document_with_api_prompt(
                images=images,
                document_type=document_type,
                preferred_provider=provider,
                custom_prompt=temp_prompt
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": result.get('success', False),
                "stage": "text_extraction",
                "response": result.get('analysis', ''),  # ✅ Verwende 'analysis' statt 'content'
                "provider_used": provider,
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"❌ Stufe 3 fehlgeschlagen: {e}")
            return {
                "success": False,
                "stage": "text_extraction",
                "error": str(e)
            }
    
    async def _stage4_verification_backend(self, text_extraction_result: Dict, structured_json: Dict) -> Dict[str, Any]:
        """Stufe 4: Erweiterte Verifikation mit Word Extraction Engine"""
        try:
            start_time = datetime.now()
            
            # Extrahiere Wörter aus Stufe 3 Ergebnis
            logger.info(f"🔍 DEBUG: text_extraction_result keys: {list(text_extraction_result.keys())}")
            
            response_content = text_extraction_result.get('response', {})
            logger.info(f"🔍 DEBUG: response_content type: {type(response_content)}")
            logger.info(f"🔍 DEBUG: response_content keys: {list(response_content.keys()) if isinstance(response_content, dict) else 'not a dict'}")
            
            if isinstance(response_content, dict):
                extracted_words = response_content.get('extracted_words', [])
                logger.info(f"🔍 DEBUG: extracted_words type: {type(extracted_words)}, length: {len(extracted_words)}")
            else:
                # Fallback für alte Format
                extracted_words = []
                logger.warning(f"⚠️ response_content ist kein dict: {type(response_content)}")
            
            logger.info(f"📝 {len(extracted_words)} Wörter aus Stufe 3 erhalten")
            
            # Verwende Word Extraction Engine für erweiterte Verifikation
            if self.cached_images and len(self.cached_images) > 0:
                # Extrahiere nochmal mit OCR falls verfügbar
                ocr_result = await self.word_engine.extract_words_with_ocr(self.cached_images[0])
                ocr_words = ocr_result.get('words', []) if ocr_result.get('success') else []
                
                # Führe erweiterte Verifikation durch
                verification_result = await self.word_engine.merge_and_verify_words(
                    llm_words=extracted_words,
                    ocr_words=ocr_words,
                    structured_json=structured_json
                )
                
                # Extrahiere Metriken
                metrics = verification_result.get('metrics', {})
                quality = verification_result.get('quality', {})
                
                duration = (datetime.now() - start_time).total_seconds()
                
                return {
                    "success": True,
                    "stage": "verification",
                    "method": "enhanced_word_extraction",
                    "provider_used": "backend_logic",
                    "extracted_words_count": len(extracted_words),
                    "verification_result": {
                        "status": "VALIDATED" if quality.get('rag_ready', False) else "NOT_VALIDATED",
                        "coverage_percentage": metrics.get('coverage_percentage', 0),
                        "missing_words": metrics.get('missing_in_extraction', []),
                        "total_detected": metrics.get('combined_words', 0),
                        "total_in_json": metrics.get('json_words', 0),
                        "verification_status": quality.get('completeness', 'unvollständig'),
                        "quality_assessment": quality.get('score', 0),
                        "recommendations": quality.get('recommendations', []),
                        "critical_terms_found": metrics.get('critical_terms_found', []),
                        "critical_terms_missing": metrics.get('critical_terms_missing', []),
                        "fuzzy_matches": metrics.get('fuzzy_matches', []),
                        "validation_details": {
                            "validation_timestamp": datetime.now().isoformat(),
                            "method": "enhanced_word_extraction",
                            "llm_words": metrics.get('llm_words', 0),
                            "ocr_words": metrics.get('ocr_words', 0)
                        }
                    },
                    "duration_seconds": duration
                }
            else:
                # Fallback ohne Bilder
                from .main import _validate_word_coverage
                verification_result = await _validate_word_coverage(extracted_words, structured_json)
                
                duration = (datetime.now() - start_time).total_seconds()
                
                return {
                    "success": True,
                    "stage": "verification",
                    "method": "backend_logic",
                    "provider_used": "backend_logic",
                    "extracted_words_count": len(extracted_words),
                    "verification_result": verification_result,
                    "duration_seconds": duration
                }
            
        except Exception as e:
            logger.error(f"❌ Stufe 4 (Backend) fehlgeschlagen: {e}")
            return {
                "success": False,
                "stage": "verification",
                "method": "backend_logic",
                "error": str(e)
            }
    
    async def _stage5_norm_compliance(self, images: List[bytes], structured_json: Dict, document_type: str, provider: str) -> Dict[str, Any]:
        """Stufe 5: Normkonformität (mit gespeicherter JSON)"""
        try:
            start_time = datetime.now()
            
            norm_compliance_prompt = self.prompts.get('norm_compliance', 'Du bist ein QMS-Experte für ISO 13485 und MDR.')
            
            temp_prompt = f"""
{norm_compliance_prompt}

**AUFGABE:** 
Bewerte, ob die Inhalte den Anforderungen eines relevanten ISO-/MDR-Kapitels entsprechen.

**STRUKTURIERTE JSON-ANALYSE:**
{json.dumps(structured_json, indent=2, ensure_ascii=False)}

**BEWERTUNG:**
- Identifiziere das passende Normkapitel
- Fasse dessen Zweck verständlich zusammen
- Bewertung: konform/teilweise_konform/nicht_konform
- Kurze Begründung

[Bild wird übergeben]
"""
            
            result = await self.vision_engine.analyze_document_with_api_prompt(
                images=images,
                document_type=document_type,
                preferred_provider=provider,
                custom_prompt=temp_prompt
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": result.get('success', False),
                "stage": "norm_compliance",
                "response": result.get('analysis', ''),  # ✅ Verwende 'analysis' statt 'content'
                "provider_used": provider,
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"❌ Stufe 5 fehlgeschlagen: {e}")
            return {
                "success": False,
                "stage": "norm_compliance",
                "error": str(e)
            }
    
    async def _stage2_structured_analysis_text_only(self, document_type: str, provider: str, stage1_result: Dict) -> Dict[str, Any]:
        """Stufe 2: Strukturierte JSON-Analyse (MIT BILD aus Cache)"""
        try:
            start_time = datetime.now()
            
            # Verwende normale Vision Engine mit strukturiertem Prompt
            result = await self.vision_engine.analyze_document_with_api_prompt(
                images=self.cached_images,  # Verwende gecachte Bilder
                document_type=document_type,
                preferred_provider=provider
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": result.get('success', False),
                "stage": "structured_analysis",
                "response": result.get('analysis', ''),
                "json_data": self._extract_json_from_analysis(result),
                "provider_used": provider,
                "duration_seconds": duration,
                "method": "with_image"
            }
            
        except Exception as e:
            logger.error(f"❌ Stufe 2 fehlgeschlagen: {e}")
            return {
                "success": False,
                "stage": "structured_analysis",
                "error": str(e)
            }

    async def _stage3_text_extraction_text_only(self, document_type: str, provider: str, stage1_result: Dict) -> Dict[str, Any]:
        """Stufe 3: Verbesserte zweistufige Textextraktion (LLM + OCR)"""
        try:
            start_time = datetime.now()
            
            logger.info("🔤 Starte zweistufige Wortextraktion...")
            
            # Prüfe cached_images
            if not self.cached_images or len(self.cached_images) == 0:
                logger.error("❌ Keine cached_images verfügbar für Textextraktion!")
                return {
                    "success": False,
                    "stage": "text_extraction",
                    "error": "Keine cached_images verfügbar"
                }
            
            logger.info(f"📸 {len(self.cached_images)} cached_images verfügbar")
            
            # Schritt 1: LLM-Wortextraktion
            llm_result = await self.word_engine.extract_words_with_llm(
                self.cached_images[0], 
                provider
            )
            
            # Schritt 2: OCR-Wortextraktion (wenn verfügbar)
            ocr_result = await self.word_engine.extract_words_with_ocr(
                self.cached_images[0]
            )
            
            # Kombiniere Ergebnisse
            llm_words = llm_result.get('words', []) if llm_result.get('success') else []
            ocr_words = ocr_result.get('words', []) if ocr_result.get('success') else []
            
            # Log Zwischenergebnisse
            logger.info(f"📊 LLM extrahierte {len(llm_words)} Wörter")
            logger.info(f"📊 OCR extrahierte {len(ocr_words)} Wörter")
            
            # Erstelle Response im erwarteten Format
            combined_words = sorted(set(llm_words + ocr_words), key=lambda w: w.lower())
            
            response_data = {
                "extracted_words": combined_words,
                "total_words": len(combined_words),
                "extraction_methods": {
                    "llm": {
                        "success": llm_result.get('success', False),
                        "count": len(llm_words)
                    },
                    "ocr": {
                        "success": ocr_result.get('success', False),
                        "count": len(ocr_words)
                    }
                }
            }
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "stage": "text_extraction",
                "response": response_data,
                "provider_used": provider,
                "duration_seconds": duration,
                "method": "two_stage_extraction"
            }
            
        except Exception as e:
            logger.error(f"❌ Stufe 3 fehlgeschlagen: {e}")
            return {
                "success": False,
                "stage": "text_extraction",
                "error": str(e)
            }

    async def _stage5_norm_compliance_text_only(self, structured_json: Dict, document_type: str, provider: str, stage1_result: Dict) -> Dict[str, Any]:
        """Stufe 5: Normkonformität (MIT BILD aus Cache)"""
        try:
            start_time = datetime.now()
            
            norm_compliance_prompt = self.prompts.get('norm_compliance', 'Du bist ein QMS-Experte für ISO 13485 und MDR.')
            
            temp_prompt = f"""
{norm_compliance_prompt}

**AUFGABE:** 
Bewerte, ob die Inhalte den Anforderungen eines relevanten ISO-/MDR-Kapitels entsprechen.

**STRUKTURIERTE JSON-ANALYSE:**
{json.dumps(structured_json, indent=2, ensure_ascii=False)}

**BEWERTUNG:**
- Identifiziere das passende Normkapitel
- Fasse dessen Zweck verständlich zusammen
- Bewertung: konform/teilweise_konform/nicht_konform
- Kurze Begründung

[Bild wird übergeben]
"""
            
            result = await self.vision_engine.analyze_document_with_api_prompt(
                images=self.cached_images,  # Verwende gecachte Bilder
                document_type=document_type,
                preferred_provider=provider,
                custom_prompt=temp_prompt
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": result.get('success', False),
                "stage": "norm_compliance",
                "response": result.get('analysis', ''),
                "provider_used": provider,
                "duration_seconds": duration,
                "method": "with_image"
            }
            
        except Exception as e:
            logger.error(f"❌ Stufe 5 fehlgeschlagen: {e}")
            return {
                "success": False,
                "stage": "norm_compliance",
                "error": str(e)
            }

    async def _call_text_only_api(self, prompt: str, provider: str) -> Dict[str, Any]:
        """Ruft AI Provider für Text-only Anfragen auf (ohne Bild)"""
        try:
            # Direkte Provider-Initialisierung
            if provider == "openai_4o_mini":
                from .ai_providers import OpenAI4oMiniProvider
                ai_provider = OpenAI4oMiniProvider()
            elif provider == "gemini":
                from .ai_providers import GoogleGeminiProvider
                ai_provider = GoogleGeminiProvider()
            elif provider == "ollama":
                from .ai_providers import OllamaProvider
                ai_provider = OllamaProvider()
            else:
                # Fallback zu OpenAI
                from .ai_providers import OpenAI4oMiniProvider
                ai_provider = OpenAI4oMiniProvider()
            
            # Text-only Anfrage (ohne Bild)
            result = await ai_provider.simple_prompt(prompt)
            
            return {
                "success": True,
                "response": result.get('response', result.get('ai_summary', '')),
                "provider": provider
            }
            
        except Exception as e:
            logger.error(f"❌ Text-only API Fehler: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_json_from_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiert JSON aus Vision Engine Analyse"""
        try:
            # ✅ KRITISCH: Die Vision API gibt das JSON im 'analysis' Feld zurück, nicht in 'content'!
            analysis = analysis_result.get('analysis', {})
            if isinstance(analysis, str):
                return json.loads(analysis)
            else:
                return analysis
        except Exception as e:
            logger.error(f"❌ JSON-Extraktion fehlgeschlagen: {e}")
            # Fallback: Versuche 'content' Feld
            try:
                content = analysis_result.get('content', '{}')
                if isinstance(content, str):
                    return json.loads(content)
                else:
                    return content
            except Exception as e2:
                logger.error(f"❌ JSON-Extraktion Fallback fehlgeschlagen: {e2}")
                raise Exception(f"JSON-Extraktion fehlgeschlagen: {str(e)}")
    
    def _finalize_pipeline(self, pipeline_results: Dict[str, Any], start_time: datetime, success: bool) -> Dict[str, Any]:
        """Finalisiert die Pipeline-Ergebnisse"""
        end_time = datetime.now()
        pipeline_duration = (end_time - start_time).total_seconds()
        
        pipeline_results["pipeline_duration_seconds"] = pipeline_duration
        pipeline_results["pipeline_success"] = success
        pipeline_results["methodology"] = "5_stage_prompt_chain"
        
        logger.info(f"🎉 Multi-Visio Pipeline abgeschlossen: {pipeline_duration:.2f}s")
        
        return pipeline_results 