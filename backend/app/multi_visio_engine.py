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
        
        # Prompts laden (konfigurierbar)
        from .config import get_prompts_dir
        self.prompts_dir = get_prompts_dir()
        self.prompts = self._load_prompts()
        
        # Cache für Bilder und Datei-Hashes
        self.cached_images = None
        self.cached_file_hash = None
        
        logger.info("🔍 Multi-Visio Engine v4.0 (5-Stufen Prompt-Chain) initialisiert")
    
    def _load_prompts(self) -> Dict[str, str]:
        """
        Lädt alle Multi-Visio Prompts DYNAMISCH - wie bei normaler Visio!
        
        Verwendet das neue multi_visio_prompts Management System für:
        - Automatische Updates bei Datei-Änderungen
        - Versionierung und Audit-Trail
        - Konsistente API wie visio_prompts
        """
        prompts = {}
        
        try:
            # ✅ NEUES SYSTEM: Dynamisches Laden wie bei visio_prompts
            from .multi_visio_prompts import get_multi_visio_prompt
            
            # Stufe 1: Experten-Einweisung
            stage1_data = get_multi_visio_prompt("expert_induction")
            prompts['context_setup'] = stage1_data["prompt"]
            logger.info(f"📝 Stage 1 geladen: {stage1_data['version']} ({len(stage1_data['prompt'])} Zeichen)")
            
            # Stufe 2: Strukturierte Analyse
            stage2_data = get_multi_visio_prompt("structured_analysis")
            prompts['structured_analysis'] = stage2_data["prompt"]
            logger.info(f"📝 Stage 2 geladen: {stage2_data['version']} ({len(stage2_data['prompt'])} Zeichen)")
            
            # Stufe 3: Textextraktion
            stage3_data = get_multi_visio_prompt("word_coverage")
            prompts['text_extraction'] = stage3_data["prompt"]
            logger.info(f"📝 Stage 3 geladen: {stage3_data['version']} ({len(stage3_data['prompt'])} Zeichen)")
            
            # Stufe 4: Verifikation (Backend-Logik)
            stage4_data = get_multi_visio_prompt("verification")
            prompts['verification'] = stage4_data["prompt"]
            logger.info(f"📝 Stage 4: Backend-Verifikation ({stage4_data['version']})")
            
            # Stufe 5: Normkonformität
            stage5_data = get_multi_visio_prompt("norm_compliance")
            prompts['norm_compliance'] = stage5_data["prompt"]
            logger.info(f"📝 Stage 5 geladen: {stage5_data['version']} ({len(stage5_data['prompt'])} Zeichen)")
            
            # ✅ AUDIT-TRAIL: Logge alle geladenen Versionen
            logger.info("🎯 MULTI-VISIO PROMPTS AUDIT:")
            for stage in ["expert_induction", "structured_analysis", "word_coverage", "verification", "norm_compliance"]:
                data = get_multi_visio_prompt(stage)
                logger.info(f"   {stage}: v{data['version']} ({data['metadata']['prompt_hash']})")
                
        except Exception as e:
            logger.error(f"❌ Fehler beim dynamischen Laden der Multi-Visio Prompts: {e}")
            # Fallback auf altes System
            logger.warning("⚡ Fallback: Verwende direktes Datei-Laden")
            prompts = self._load_prompts_fallback()
        
        return prompts
    
    def _load_prompts_fallback(self) -> Dict[str, str]:
        """Fallback: Direktes Laden aus Dateien (alte Methode)"""
        prompts = {}
        
        try:
            # Stufe 1: Bild übergeben & Kontext setzen
            context_prompt_path = self.prompts_dir / "01_expert_induction.txt"
            if context_prompt_path.exists():
                with open(context_prompt_path, 'r', encoding='utf-8') as f:
                    prompts['context_setup'] = f.read()
                logger.info("📝 Fallback: 01_expert_induction.txt")
            
            # Stufe 2: Strukturierte Analyse
            structured_analysis_prompt_path = self.prompts_dir / "02_structured_analysis.txt"
            if structured_analysis_prompt_path.exists():
                with open(structured_analysis_prompt_path, 'r', encoding='utf-8') as f:
                    prompts['structured_analysis'] = f.read()
                logger.info("📝 Fallback: 02_structured_analysis.txt")
            
            # Stufe 3: Textextraktion
            text_extraction_prompt_path = self.prompts_dir / "03_word_coverage.txt"
            if text_extraction_prompt_path.exists():
                with open(text_extraction_prompt_path, 'r', encoding='utf-8') as f:
                    prompts['text_extraction'] = f.read()
                logger.info("📝 Fallback: 03_word_coverage.txt")
            
            # Stufe 5: Normkonformität
            norm_compliance_prompt_path = self.prompts_dir / "05_norm_compliance.txt"
            if norm_compliance_prompt_path.exists():
                with open(norm_compliance_prompt_path, 'r', encoding='utf-8') as f:
                    prompts['norm_compliance'] = f.read()
                logger.info("📝 Fallback: 05_norm_compliance.txt")
                
        except Exception as e:
            logger.error(f"❌ Auch Fallback fehlgeschlagen: {e}")
        
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
            
            # Stufe 3: HYBRID - Backend-Processing von all_extracted_texts
            logger.info("🔄 Stufe 3/5: Hybrid Text-Processing (Backend)")
            stage3_result = await self._stage3_text_extraction_from_stage2(stage2_result)
            pipeline_results["stages"]["text_extraction"] = stage3_result
            
            if not stage3_result.get('success'):
                logger.error("❌ Pipeline abgebrochen: Stufe 3 fehlgeschlagen")
                return self._finalize_pipeline(pipeline_results, start_time, False)
            
            # Stufe 4: HYBRID - Verifikation Stage 2 vs Stage 3
            logger.info("🔄 Stufe 4/5: Hybrid-Verifikation (Stage 2 Referenz)")
            stage4_result = await self._stage4_verification_hybrid(
                stage3_result, stage2_result
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
    
    async def _stage4_verification_hybrid(self, stage3_result: Dict, stage2_result: Dict) -> Dict[str, Any]:
        """Stufe 4: HYBRID - Verifikation Stage 2 vs Stage 3 (Stage 2 = Referenz)"""
        try:
            start_time = datetime.now()
            
            logger.info("🔍 Starte Hybrid-Verifikation: Stage 2 (Referenz) vs Stage 3...")
            
            # 1. Extrahiere all_extracted_texts aus Stage 2 (REFERENZ)
            stage2_response = stage2_result.get("response", {})
            if isinstance(stage2_response, str):
                try:
                    import json
                    stage2_response = json.loads(stage2_response)
                except:
                    logger.error("❌ Konnte Stage 2 JSON nicht parsen")
                    stage2_response = {}
            
            reference_texts = stage2_response.get("all_extracted_texts", [])
            logger.info(f"📋 Stage 2 Referenz: {len(reference_texts)} Texte")
            
            # 2. Extrahiere Wörter aus Stage 3 (VERGLEICH)
            stage3_response = stage3_result.get('response', {})
            stage3_words = stage3_response.get('extracted_words', [])
            logger.info(f"📝 Stage 3 Extraktion: {len(stage3_words)} Wörter")
            
            # 3. Backend-Processing: Stage 2 Referenz-Wörter extrahieren
            import re
            reference_words = set()
            for text in reference_texts:
                if isinstance(text, str) and text.strip():
                    words = re.findall(r'\b[\wÄÖÜäöüß\-\/\.\(\)]+\b', text.lower())
                    for word in words:
                        if len(word) >= 2 and not word.isdigit():
                            reference_words.add(word)
            
            # 4. Stage 3 Wörter normalisieren
            stage3_normalized = {word.lower() for word in stage3_words if len(word) >= 2}
            
            # 5. Coverage-Berechnung (Stage 2 = 100% Referenz)
            matched_words = reference_words & stage3_normalized
            coverage_percentage = (len(matched_words) / len(reference_words)) * 100 if reference_words else 0
            missing_words = reference_words - stage3_normalized
            
            # 6. Quality Assessment
            from .config import get_quality_threshold
            high_threshold = get_quality_threshold("high_quality")
            medium_threshold = get_quality_threshold("medium_quality")
            
            if coverage_percentage >= high_threshold:
                quality_assessment = "hoch"
                verification_status = "verifiziert"
                rag_ready = True
            elif coverage_percentage >= medium_threshold:
                quality_assessment = "mittel"
                verification_status = "teilweise_verifiziert" 
                rag_ready = False
            else:
                quality_assessment = "niedrig"
                verification_status = "nicht_verifiziert"
                rag_ready = False
            
            # 7. Empfehlungen generieren
            recommendations = []
            if coverage_percentage < high_threshold:
                recommendations.append(f"Wortabdeckung nur {coverage_percentage:.1f}% - Manuelle Überprüfung empfohlen")
            if len(missing_words) > 0:
                recommendations.append(f"{len(missing_words)} Wörter fehlen in der Extraktion")
            if coverage_percentage >= high_threshold:
                recommendations.append("Dokument vollständig erfasst - RAG-Integration freigegeben")
            
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Hybrid-Verifikation: {coverage_percentage:.1f}% Coverage ({len(matched_words)}/{len(reference_words)})")
            
            return {
                "success": True,
                "stage": "verification",
                "method": "hybrid_stage2_reference",
                "provider_used": "backend_logic",
                "verification": {
                    "status": "VALIDATED" if rag_ready else "NOT_VALIDATED",
                    "coverage_percentage": coverage_percentage,
                    "missing_words": list(missing_words)[:10],  # Nur erste 10 für Frontend
                    "total_detected": len(stage3_words),
                    "total_in_reference": len(reference_words),
                    "matched_words": len(matched_words),
                    "verification_status": verification_status,
                    "quality_assessment": quality_assessment,
                    "recommendations": recommendations,
                    "rag_ready": rag_ready,
                    "validation_details": {
                        "validation_timestamp": datetime.now().isoformat(),
                        "method": "hybrid_stage2_reference",
                        "reference_source": "stage2_all_extracted_texts",
                        "comparison_source": "stage3_backend_processing"
                    }
                },
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"❌ Stufe 4 (Hybrid) fehlgeschlagen: {e}")
            return {
                "success": False,
                "stage": "verification",
                "method": "hybrid_stage2_reference",
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

    async def _stage3_text_extraction_from_stage2(self, stage2_result: Dict) -> Dict[str, Any]:
        """Stufe 3: HYBRID - Backend-Processing von all_extracted_texts aus Stage 2"""
        try:
            start_time = datetime.now()
            
            logger.info("🔄 Starte Hybrid Text-Processing aus Stage 2...")
            
            # Extrahiere all_extracted_texts aus Stage 2 JSON
            stage2_response = stage2_result.get("response", {})
            
            # Prüfe verschiedene mögliche JSON-Strukturen
            all_extracted_texts = None
            if isinstance(stage2_response, dict):
                all_extracted_texts = stage2_response.get("all_extracted_texts", [])
            elif isinstance(stage2_response, str):
                # Falls JSON als String vorliegt
                try:
                    import json
                    parsed_json = json.loads(stage2_response)
                    all_extracted_texts = parsed_json.get("all_extracted_texts", [])
                except:
                    logger.warning("⚠️ Konnte JSON-String nicht parsen")
            
            if not all_extracted_texts:
                logger.error("❌ Keine all_extracted_texts in Stage 2 gefunden!")
                return {
                    "success": False,
                    "stage": "text_extraction",
                    "error": "Keine all_extracted_texts in Stage 2 gefunden",
                    "stage2_response_type": type(stage2_response).__name__
                }
            
            logger.info(f"📝 {len(all_extracted_texts)} Texte aus Stage 2 erhalten")
            
            # Backend-Processing: Tokenisierung + Bereinigung
            processed_words = []
            import re
            
            for text in all_extracted_texts:
                if isinstance(text, str) and text.strip():
                    # Tokenisierung: Wörter extrahieren
                    words = re.findall(r'\b[\wÄÖÜäöüß\-\/\.\(\)]+\b', text)
                    
                    # Bereinigung: Mindestlänge, nur Buchstaben, etc.
                    for word in words:
                        if len(word) >= 2 and not word.isdigit():
                            processed_words.append(word)
            
            # Duplikate entfernen und sortieren
            unique_words = sorted(set(processed_words), key=lambda w: w.lower())
            
            # Qualitäts-Metriken
            response_data = {
                "extracted_words": unique_words,
                "total_words": len(unique_words),
                "source_texts_count": len(all_extracted_texts),
                "processing_method": "backend_tokenization",
                "duplicate_words_removed": len(processed_words) - len(unique_words)
            }
            
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Backend-Processing: {len(unique_words)} einzigartige Wörter aus {len(all_extracted_texts)} Texten")
            
            return {
                "success": True,
                "stage": "text_extraction",
                "response": response_data,
                "duration_seconds": duration,
                "method": "hybrid_backend_processing"
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