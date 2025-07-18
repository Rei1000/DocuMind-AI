"""
Visio Processing Engine für schrittweise Dokumentverarbeitung

Diese Engine implementiert den mehrstufigen Verarbeitungsprozess für Visio-Uploads:
1. PNG-Generierung aus Dokumenten
2. Prompt-Ausführung (visio_words, visio_analysis)
3. Verifikation der extrahierten Wörter
4. QM-Freigabe mit Vorschau
5. RAG-Indexierung nach Freigabe
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
import tempfile
import os

from sqlalchemy.orm import Session
from sqlalchemy import text

from .vision_ocr_engine import VisionOCREngine
from .visio_prompts import get_visio_prompt, validate_visio_json_response
from .models import Document as DocumentModel
from .database import get_db

logger = logging.getLogger("KI-QMS.VisioProcessing")

class ProcessingState(str, Enum):
    """Verarbeitungszustände für State Machine"""
    UPLOADED = "UPLOADED"
    PNG_GENERATED = "PNG_GENERATED"
    WORDS_EXTRACTED = "WORDS_EXTRACTED"
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"
    VALIDATED = "VALIDATED"
    QM_APPROVED = "QM_APPROVED"
    INDEXED = "INDEXED"
    ERROR = "ERROR"

class ValidationStatus(str, Enum):
    """Validierungsstatus"""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"

class VisioProcessingEngine:
    """
    Engine für die schrittweise Verarbeitung von Visio-Uploads
    """
    
    def __init__(self):
        self.vision_engine = VisionOCREngine()
        self.temp_dir = Path(tempfile.gettempdir()) / "ki_qms_visio"
        self.temp_dir.mkdir(exist_ok=True)
        logger.info("✅ Visio Processing Engine initialisiert")
    
    async def process_visio_upload(self, document_id: int, db: Session) -> Dict[str, Any]:
        """
        Hauptfunktion für die Visio-Verarbeitung
        
        Args:
            document_id: ID des hochgeladenen Dokuments
            db: Datenbankverbindung
        
        Returns:
            Status-Dictionary mit Verarbeitungsergebnissen
        """
        try:
            # Dokument laden
            document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
            if not document:
                raise ValueError(f"Dokument {document_id} nicht gefunden")
            
            # Prüfe ob Visio-Upload
            if document.upload_method != "visio":
                return {
                    "success": False,
                    "error": "Dokument ist kein Visio-Upload",
                    "state": document.processing_state
                }
            
            logger.info(f"🔄 Starte Visio-Verarbeitung für Dokument {document_id}")
            
            # State Machine basierend auf aktuellem Zustand
            current_state = ProcessingState(document.processing_state or ProcessingState.UPLOADED)
            
            if current_state == ProcessingState.UPLOADED:
                # Schritt 1: PNG-Generierung
                result = await self._generate_png(document, db)
                if not result["success"]:
                    return result
                    
            if current_state in [ProcessingState.UPLOADED, ProcessingState.PNG_GENERATED]:
                # Schritt 2: Wort-Extraktion
                result = await self._extract_words(document, db)
                if not result["success"]:
                    return result
                    
            if current_state in [ProcessingState.UPLOADED, ProcessingState.PNG_GENERATED, 
                               ProcessingState.WORDS_EXTRACTED]:
                # Schritt 3: Strukturierte Analyse
                result = await self._analyze_structure(document, db)
                if not result["success"]:
                    return result
                    
            if current_state in [ProcessingState.UPLOADED, ProcessingState.PNG_GENERATED,
                               ProcessingState.WORDS_EXTRACTED, ProcessingState.ANALYSIS_COMPLETE]:
                # Schritt 4: Validierung
                result = await self._validate_extraction(document, db)
                if not result["success"]:
                    return result
            
            # Rückgabe des aktuellen Status
            return self._get_current_status(document)
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Visio-Verarbeitung: {e}")
            # Update Dokument-Status auf ERROR
            document.processing_state = ProcessingState.ERROR
            document.vision_results = json.dumps({"error": str(e)})
            db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "state": ProcessingState.ERROR
            }
    
    async def _generate_png(self, document: DocumentModel, db: Session) -> Dict[str, Any]:
        """
        Schritt 1: PNG-Generierung aus Dokument
        """
        try:
            logger.info(f"📸 Generiere PNG für Dokument {document.id}")
            
            # Datei-Pfad - korrigiere relative Pfade
            file_path = Path(document.file_path)
            
            # Wenn der Pfad nicht absolut ist, füge das backend-Verzeichnis hinzu
            if not file_path.is_absolute():
                # Wir sind im backend/app Verzeichnis, also gehe eine Ebene hoch
                backend_dir = Path(__file__).parent.parent
                file_path = backend_dir / file_path
            
            if not file_path.exists():
                logger.error(f"❌ Datei nicht gefunden: {file_path}")
                logger.error(f"   Absoluter Pfad: {file_path.absolute()}")
                logger.error(f"   Original Pfad: {document.file_path}")
                raise FileNotFoundError(f"Datei nicht gefunden: {file_path}")
            
            logger.info(f"📄 Datei gefunden: {file_path}")
            logger.info(f"   Größe: {file_path.stat().st_size} bytes")
            logger.info(f"   Typ: {file_path.suffix}")
            
            # Konvertiere zu PNG (300 DPI)
            images = await self.vision_engine.convert_document_to_images(file_path, dpi=300)
            
            if not images:
                raise ValueError("Keine Bilder generiert")
            
            # Speichere erste Seite als Vorschau
            preview_path = self.temp_dir / f"doc_{document.id}_preview.png"
            with open(preview_path, "wb") as f:
                f.write(images[0])
            
            # Update Dokument
            vision_results = json.loads(document.vision_results or "{}")
            vision_results["png_generated"] = True
            vision_results["png_count"] = len(images)
            vision_results["preview_path"] = str(preview_path)
            vision_results["generated_at"] = datetime.utcnow().isoformat()
            
            document.vision_results = json.dumps(vision_results)
            document.processing_state = ProcessingState.PNG_GENERATED
            db.commit()
            
            logger.info(f"✅ PNG-Generierung abgeschlossen: {len(images)} Seiten")
            
            return {
                "success": True,
                "state": ProcessingState.PNG_GENERATED,
                "png_count": len(images),
                "preview_path": str(preview_path)
            }
            
        except Exception as e:
            logger.error(f"❌ PNG-Generierung fehlgeschlagen: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": f"PNG-Generierung fehlgeschlagen: {str(e)}",
                "state": ProcessingState.ERROR
            }
    
    async def _extract_words(self, document: DocumentModel, db: Session) -> Dict[str, Any]:
        """
        Schritt 2: Wort-Extraktion mit visio_words Prompt
        """
        try:
            logger.info(f"📝 Extrahiere Wörter für Dokument {document.id}")
            
            # Hole visio_words Prompt
            prompt = get_visio_prompt(document.document_type, "visio_words")
            
            # Hole PNG-Bilder
            vision_results = json.loads(document.vision_results or "{}")
            preview_path = vision_results.get("preview_path")
            
            if not preview_path or not Path(preview_path).exists():
                # Regeneriere PNG wenn nötig
                png_result = await self._generate_png(document, db)
                if not png_result["success"]:
                    return png_result
                preview_path = png_result["preview_path"]
            
            # Rufe Vision API auf
            with open(preview_path, "rb") as f:
                image_data = f.read()
            
            words_response = await self.vision_engine.analyze_image_with_prompt(
                image_data=image_data,
                prompt=prompt,
                max_tokens=2000
            )
            
            if not words_response:
                raise ValueError("Keine Antwort von Vision API")
            
            # Extrahiere Wörter (durch Leerzeichen getrennt)
            extracted_words = words_response.strip().split()
            
            # Update Dokument
            vision_results["extracted_words"] = extracted_words
            vision_results["word_count"] = len(extracted_words)
            vision_results["words_extracted_at"] = datetime.utcnow().isoformat()
            
            # Speichere verwendeten Prompt
            used_prompts = json.loads(document.used_prompts or "{}")
            used_prompts["visio_words"] = prompt[:200] + "..."  # Gekürzt speichern
            
            document.vision_results = json.dumps(vision_results)
            document.used_prompts = json.dumps(used_prompts)
            document.processing_state = ProcessingState.WORDS_EXTRACTED
            db.commit()
            
            logger.info(f"✅ Wort-Extraktion abgeschlossen: {len(extracted_words)} Wörter")
            
            return {
                "success": True,
                "state": ProcessingState.WORDS_EXTRACTED,
                "word_count": len(extracted_words),
                "sample_words": extracted_words[:10]  # Erste 10 Wörter als Beispiel
            }
            
        except Exception as e:
            logger.error(f"❌ Wort-Extraktion fehlgeschlagen: {e}")
            return {
                "success": False,
                "error": f"Wort-Extraktion fehlgeschlagen: {str(e)}",
                "state": ProcessingState.ERROR
            }
    
    async def _analyze_structure(self, document: DocumentModel, db: Session) -> Dict[str, Any]:
        """
        Schritt 3: Strukturierte Analyse mit visio_analysis Prompt
        """
        try:
            logger.info(f"🔍 Analysiere Struktur für Dokument {document.id}")
            
            # Hole visio_analysis Prompt
            prompt = get_visio_prompt(document.document_type, "visio_analysis")
            
            # Hole PNG
            vision_results = json.loads(document.vision_results or "{}")
            preview_path = vision_results.get("preview_path")
            
            if not preview_path or not Path(preview_path).exists():
                raise ValueError("PNG-Datei nicht gefunden")
            
            # Rufe Vision API auf
            with open(preview_path, "rb") as f:
                image_data = f.read()
            
            analysis_response = await self.vision_engine.analyze_image_with_prompt(
                image_data=image_data,
                prompt=prompt,
                max_tokens=4000  # Mehr Tokens für detaillierte Analyse
            )
            
            if not analysis_response:
                raise ValueError("Keine Antwort von Vision API")
            
            # Validiere und parse JSON
            structured_analysis = validate_visio_json_response(analysis_response)
            
            # Update Dokument
            document.structured_analysis = json.dumps(structured_analysis)
            vision_results["analysis_completed"] = True
            vision_results["analysis_completed_at"] = datetime.utcnow().isoformat()
            
            # Speichere verwendeten Prompt
            used_prompts = json.loads(document.used_prompts or "{}")
            used_prompts["visio_analysis"] = prompt[:200] + "..."
            
            document.vision_results = json.dumps(vision_results)
            document.used_prompts = json.dumps(used_prompts)
            document.processing_state = ProcessingState.ANALYSIS_COMPLETE
            db.commit()
            
            logger.info(f"✅ Strukturanalyse abgeschlossen")
            
            return {
                "success": True,
                "state": ProcessingState.ANALYSIS_COMPLETE,
                "document_type": structured_analysis.get("document_info", {}).get("type", "OTHER"),
                "has_flowchart": structured_analysis.get("quality_indicators", {}).get("contains_flowchart", False)
            }
            
        except Exception as e:
            logger.error(f"❌ Strukturanalyse fehlgeschlagen: {e}")
            return {
                "success": False,
                "error": f"Strukturanalyse fehlgeschlagen: {str(e)}",
                "state": ProcessingState.ERROR
            }
    
    async def _validate_extraction(self, document: DocumentModel, db: Session) -> Dict[str, Any]:
        """
        Schritt 4: Validierung - Vergleiche extrahierte Wörter mit JSON-Analyse
        """
        try:
            logger.info(f"✔️ Validiere Extraktion für Dokument {document.id}")
            
            # Hole extrahierte Wörter
            vision_results = json.loads(document.vision_results or "{}")
            extracted_words = vision_results.get("extracted_words", [])
            
            # Hole strukturierte Analyse
            structured_analysis = json.loads(document.structured_analysis or "{}")
            
            # Sammle alle Wörter aus der JSON-Analyse
            json_words = self._extract_words_from_json(structured_analysis)
            
            # Normalisiere für Vergleich (lowercase)
            extracted_set = set(word.lower() for word in extracted_words)
            json_set = set(word.lower() for word in json_words)
            
            # Berechne Übereinstimmung
            if extracted_set:
                coverage = len(json_set.intersection(extracted_set)) / len(json_set) if json_set else 1.0
                missing_words = list(json_set - extracted_set)
            else:
                coverage = 0.0
                missing_words = list(json_set)
            
            # Bestimme Validierungsstatus
            if coverage >= 0.95:
                validation_status = ValidationStatus.VERIFIED
                logger.info(f"✅ Validierung erfolgreich: {coverage:.1%} Abdeckung")
            else:
                validation_status = ValidationStatus.REVIEW_REQUIRED
                logger.warning(f"⚠️ Review erforderlich: {coverage:.1%} Abdeckung")
            
            # Update Dokument
            document.validation_status = validation_status
            vision_results["validation_coverage"] = coverage
            vision_results["missing_words"] = missing_words[:20]  # Max 20 fehlende Wörter
            vision_results["validated_at"] = datetime.utcnow().isoformat()
            
            document.vision_results = json.dumps(vision_results)
            document.processing_state = ProcessingState.VALIDATED
            db.commit()
            
            return {
                "success": True,
                "state": ProcessingState.VALIDATED,
                "validation_status": validation_status,
                "coverage": coverage,
                "missing_words_count": len(missing_words)
            }
            
        except Exception as e:
            logger.error(f"❌ Validierung fehlgeschlagen: {e}")
            return {
                "success": False,
                "error": f"Validierung fehlgeschlagen: {str(e)}",
                "state": ProcessingState.ERROR
            }
    
    def _extract_words_from_json(self, data: Dict, words: Optional[List[str]] = None) -> List[str]:
        """
        Rekursiv alle Text-Wörter aus JSON-Struktur extrahieren
        """
        if words is None:
            words = []
        
        if isinstance(data, dict):
            for value in data.values():
                self._extract_words_from_json(value, words)
        elif isinstance(data, list):
            for item in data:
                self._extract_words_from_json(item, words)
        elif isinstance(data, str):
            # Splitte String in Wörter
            words.extend(data.split())
        
        return words
    
    async def approve_qm_release(self, document_id: int, user_id: int, db: Session) -> Dict[str, Any]:
        """
        QM-Freigabe erteilen und RAG-Indexierung starten
        """
        try:
            document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
            if not document:
                raise ValueError(f"Dokument {document_id} nicht gefunden")
            
            # Prüfe ob bereits validiert
            if document.processing_state != ProcessingState.VALIDATED:
                return {
                    "success": False,
                    "error": "Dokument muss erst validiert werden"
                }
            
            # Setze QM-Freigabe
            document.qm_release_at = datetime.utcnow()
            document.qm_release_by_id = user_id
            document.processing_state = ProcessingState.QM_APPROVED
            
            db.commit()
            
            # Starte RAG-Indexierung (async im Hintergrund)
            asyncio.create_task(self._index_to_rag(document_id, db))
            
            logger.info(f"✅ QM-Freigabe erteilt für Dokument {document_id}")
            
            return {
                "success": True,
                "state": ProcessingState.QM_APPROVED,
                "released_at": document.qm_release_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ QM-Freigabe fehlgeschlagen: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _index_to_rag(self, document_id: int, db: Session):
        """
        RAG-Indexierung nach QM-Freigabe
        """
        try:
            # Importiere RAG Engine
            from .advanced_rag_engine import index_document_advanced
            
            logger.info(f"🔍 Starte RAG-Indexierung für Dokument {document_id}")
            
            # Indexiere Dokument
            result = await index_document_advanced(document_id)
            
            if result.get("success"):
                # Update Status
                document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
                document.processing_state = ProcessingState.INDEXED
                db.commit()
                
                logger.info(f"✅ RAG-Indexierung abgeschlossen für Dokument {document_id}")
            else:
                logger.error(f"❌ RAG-Indexierung fehlgeschlagen: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ RAG-Indexierung Exception: {e}")
    
    def _get_current_status(self, document: DocumentModel) -> Dict[str, Any]:
        """
        Aktuellen Verarbeitungsstatus zurückgeben
        """
        vision_results = json.loads(document.vision_results or "{}")
        
        return {
            "success": True,
            "document_id": document.id,
            "state": document.processing_state,
            "validation_status": document.validation_status,
            "has_preview": bool(vision_results.get("preview_path")),
            "word_count": vision_results.get("word_count", 0),
            "validation_coverage": vision_results.get("validation_coverage", 0),
            "qm_released": document.qm_release_at is not None,
            "vision_results": vision_results
        }

# Singleton-Instanz
visio_processing_engine = VisioProcessingEngine()