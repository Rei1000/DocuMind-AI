"""
🎯 Document-to-Image + Vision OCR Engine

Die ultimative Lösung für komplexe QM-Dokumente mit Flussdiagrammen:

Workflow:
1. 📄 Document → 🖼️ High-Quality Images (300 DPI)
2. 🤖 GPT-4o Vision API → Detaillierte Analyse
3. 📊 Structured JSON Response → >1000 Zeichen Text
4. ✅ Prozess-Referenzen & Compliance Check

Unterstützte Formate:
- PDF → PNG (PyMuPDF)
- DOCX → PDF → PNG (LibreOffice)
- Word → Images (Win32 COM)

Optimiert für: PA 8.2.1 Behandlung von Reparaturen (Ergosana)
"""

import base64
import json
import logging
import tempfile
import asyncio
import subprocess
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

# Document Processing
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# Image processing
try:
    from PIL import Image, ImageEnhance
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# OpenAI Vision API
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger("KI-QMS.DocumentVision")

class DocumentToImageVisionEngine:
    """
    🎯 Document-to-Image + Vision OCR Engine
    
    Konvertiert komplexe Dokumente zu Bildern und extrahiert
    mit GPT-4o Vision API maximalen Text aus Flussdiagrammen.
    """

    def __init__(self):
        self.model = "gpt-4o-mini"
        self.api_key = self._get_openai_key()
        self.client = OpenAI(api_key=self.api_key) if self.api_key and OPENAI_AVAILABLE else None
        
        # Feature Detection
        self.pymupdf_available = PYMUPDF_AVAILABLE
        self.pillow_available = PILLOW_AVAILABLE
        self.libreoffice_available = self._check_libreoffice()
        
        logger.info(f"🎯 Document-to-Image Vision Engine initialisiert")
        logger.info(f"📚 PyMuPDF: {'✅' if self.pymupdf_available else '❌'}")
        logger.info(f"🖼️ Pillow: {'✅' if self.pillow_available else '❌'}")
        logger.info(f"📄 LibreOffice: {'✅' if self.libreoffice_available else '❌'}")
        logger.info(f"🤖 OpenAI Vision: {'✅' if self.client else '❌'}")

    def _get_openai_key(self) -> Optional[str]:
        """OpenAI API Key laden"""
        return os.getenv('OPENAI_API_KEY')
    
    def _check_libreoffice(self) -> bool:
        """Prüft ob LibreOffice verfügbar ist"""
        try:
            result = subprocess.run(['libreoffice', '--version'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    async def extract_text_with_document_vision(self, file_path: str) -> Dict[str, Any]:
        """
        🎯 HAUPTFUNKTION: Document → Vision OCR → Text
        
        Args:
            file_path: Pfad zum Dokument
            
        Returns:
            Dict mit extrahiertem Text und Metadaten
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            return {
                "success": False,
                "error": f"Datei nicht gefunden: {file_path}",
                "extracted_text": "",
                "method": "file_not_found"
            }
        
        logger.info(f"🎯 Starte Document-Vision-OCR für: {file_path_obj.name}")
        
        try:
            # 1. Document → Images
            images = await self.convert_document_to_images(file_path_obj)
            
            if not images:
                return {
                    "success": False,
                    "error": "Keine Bilder aus Dokument extrahiert",
                    "extracted_text": "",
                    "method": "no_images"
                }
            
            # 2. Vision OCR auf alle Bilder
            vision_results = []
            total_text = ""
            all_process_refs = []
            
            for i, img_bytes in enumerate(images):
                logger.info(f"🔍 Analysiere Bild {i+1}/{len(images)} mit Vision API...")
                
                result = await self._analyze_image_with_vision(
                    img_bytes, f"Seite {i+1} von {file_path_obj.name}"
                )
                
                if result['success']:
                    vision_results.append(result)
                    total_text += result['extracted_text'] + "\n\n"
                    all_process_refs.extend(result.get('process_references', []))
            
            # 3. Combine Results
            combined_result = {
                "success": len(vision_results) > 0,
                "extracted_text": total_text.strip(),
                "method": "document_to_image_vision",
                "images_processed": len(images),
                "pages_analyzed": len(vision_results),
                "process_references": list(set(all_process_refs)),
                "vision_results": vision_results,
                "total_characters": len(total_text.strip()),
                "file_name": file_path_obj.name
            }
            
            # 4. Success Metrics
            if combined_result["total_characters"] > 1000:
                logger.info(f"🎉 ERFOLGREICH: {combined_result['total_characters']} Zeichen extrahiert!")
            else:
                logger.warning(f"⚠️ Wenig Text: {combined_result['total_characters']} Zeichen")
            
            return combined_result
            
        except Exception as e:
            logger.error(f"❌ Document-Vision-OCR fehlgeschlagen: {e}")
            return {
                "success": False,
                "error": str(e),
                "extracted_text": "",
                "method": "exception",
                "total_characters": 0
            }

    async def convert_document_to_images(self, file_path: Path, dpi: int = 300) -> List[bytes]:
        """
        🔄 Document → High-Quality Images
        
        Args:
            file_path: Dokumentpfad
            dpi: Bildauflösung (300 DPI für beste OCR-Qualität)
            
        Returns:
            Liste von PNG-Bildern als bytes
        """
        file_ext = file_path.suffix.lower()
        
        logger.info(f"🔄 Konvertiere {file_ext} → Bilder (DPI: {dpi})")
        
        if file_ext == '.pdf':
            return await self._pdf_to_images(file_path, dpi)
        elif file_ext in ['.docx', '.doc']:
            return await self._word_to_images(file_path, dpi)
        else:
            logger.error(f"❌ Unbekanntes Format: {file_ext}")
            return []

    async def _pdf_to_images(self, file_path: Path, dpi: int = 300) -> List[bytes]:
        """PDF → PNG mit PyMuPDF"""
        
        if not self.pymupdf_available:
            logger.error("❌ PyMuPDF nicht verfügbar")
            return []
        
        try:
            doc = fitz.open(file_path)
            images = []
            
            logger.info(f"📄 PDF: {len(doc)} Seiten gefunden")
            
            # Maximal 5 Seiten für Performance
            max_pages = min(len(doc), 5)
            
            for page_num in range(max_pages):
                page = doc.load_page(page_num)
                
                # High-Quality Matrix für DPI
                zoom = dpi / 72  # 72 DPI ist Standard
                mat = fitz.Matrix(zoom, zoom)
                
                # Render als PNG
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img_data = pix.tobytes("png")
                
                images.append(img_data)
                logger.info(f"✅ Seite {page_num + 1}: {len(img_data):,} bytes")
                
                # Memory cleanup
                pix = None
            
            doc.close()
            logger.info(f"🎉 PDF→PNG abgeschlossen: {len(images)} Bilder")
            return images
            
        except Exception as e:
            logger.error(f"❌ PDF Konvertierung fehlgeschlagen: {e}")
            return []

    async def _word_to_images(self, file_path: Path, dpi: int = 300) -> List[bytes]:
        """Word → Images via LibreOffice"""
        
        if not self.libreoffice_available:
            logger.error("❌ LibreOffice nicht verfügbar für Word-Konvertierung")
            return []
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 1. Word → PDF mit LibreOffice
                logger.info("🔄 Schritt 1: Word → PDF (LibreOffice)")
                pdf_path = await self._convert_word_to_pdf_libreoffice(file_path, temp_path)
                
                if not pdf_path or not pdf_path.exists():
                    logger.error("❌ Word → PDF Konvertierung fehlgeschlagen")
                    return []
                
                # 2. PDF → Images
                logger.info("🔄 Schritt 2: PDF → Images")
                images = await self._pdf_to_images(pdf_path, dpi)
                
                logger.info(f"🎉 Word→Images abgeschlossen: {len(images)} Bilder")
                return images
                
        except Exception as e:
            logger.error(f"❌ Word Konvertierung fehlgeschlagen: {e}")
            return []

    async def _convert_word_to_pdf_libreoffice(self, word_path: Path, output_dir: Path) -> Optional[Path]:
        """Word → PDF mit LibreOffice Headless"""
        
        try:
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(output_dir),
                str(word_path)
            ]
            
            logger.info(f"🔄 LibreOffice: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 Minuten Timeout
            )
            
            if result.returncode == 0:
                # PDF Datei finden
                pdf_files = list(output_dir.glob("*.pdf"))
                if pdf_files:
                    pdf_path = pdf_files[0]
                    logger.info(f"✅ PDF erstellt: {pdf_path.name} ({pdf_path.stat().st_size:,} bytes)")
                    return pdf_path
                else:
                    logger.error("❌ Keine PDF-Datei gefunden nach Konvertierung")
            else:
                logger.error(f"❌ LibreOffice Fehler: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("❌ LibreOffice Timeout (120s)")
        except Exception as e:
            logger.error(f"❌ LibreOffice Exception: {e}")
        
        return None

    async def _analyze_image_with_vision(self, image_bytes: bytes, context: str) -> Dict[str, Any]:
        """
        🤖 Analysiert Bild mit GPT-4o Vision API
        
        Args:
            image_bytes: PNG Bilddaten
            context: Kontext für bessere Analyse
            
        Returns:
            Strukturierte Vision-Analyse
        """
        
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI Client nicht verfügbar",
                "extracted_text": ""
            }
        
        try:
            # Base64 Encoding
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Optimierter Prompt für PA 8.2.1
            prompt = self._create_ergosana_vision_prompt(context)
            
            logger.info(f"🤖 Vision API Anfrage: {len(image_b64)} chars Base64")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_b64}",
                                "detail": "high"  # Maximale Detailanalyse
                            }
                        }
                    ]
                }],
                max_tokens=2000,  # Mehr Tokens für detaillierte Extraktion
                temperature=0.1   # Konsistente Ergebnisse
            )
            
            response_text = response.choices[0].message.content or ""
            logger.info(f"🤖 Vision API Response: {len(response_text)} Zeichen")
            
            # Parse JSON Response
            try:
                parsed_result = json.loads(response_text)
                
                # Add metadata
                parsed_result.update({
                    "success": True,
                    "context": context,
                    "image_size_bytes": len(image_bytes),
                    "response_length": len(response_text)
                })
                
                # Extract text if not present
                if "extracted_text" not in parsed_result:
                    parsed_result["extracted_text"] = response_text
                
                return parsed_result
                
            except json.JSONDecodeError:
                logger.warning("⚠️ JSON Parse Fehler - verwende Rohtext")
                return {
                    "success": True,
                    "extracted_text": response_text,
                    "context": context,
                    "process_references": self._extract_references_fallback(response_text),
                    "description": response_text,
                    "json_parse_error": True
                }
                
        except Exception as e:
            logger.error(f"❌ Vision API Fehler: {e}")
            return {
                "success": False,
                "error": str(e),
                "extracted_text": "",
                "context": context
            }

    def _create_ergosana_vision_prompt(self, context: str) -> str:
        """
        🎯 Optimierter Vision-Prompt für Ergosana PA 8.2.1
        """
        
        return f"""
Du analysierst ein Ergosana QM-Flussdiagramm für medizinische Gerätereparaturen. 
Extrahiere VOLLSTÄNDIG ALLE Informationen - Ziel: >1000 Zeichen Text!

🎯 SPEZIFISCHE ERKENNUNGSAUFGABEN:

1. VOLLSTÄNDIGER DOKUMENTENTITEL
   - "PA 8.2.1 [03] - Behandlung von Reparaturen" 
   - Ergosana Logo und Header-Informationen

2. KOMPLETTER PROZESSFLUSS (Schritt für Schritt):
   - Defektes Gerät → Gerät Reinigen → Wareneingang  
   - Reparaturerfassung → Fehlersuche → Wiederkehrender Fehler?
   - JA-Pfad: PA 8.5 QAB-Prozess / PA 8.5 CAPA-Prozess
   - NEIN-Pfad: KVA an Kunden → Reparatur durchführen
   - Finale Schritte: Gerät testen, Dokumentation

3. VERANTWORTLICHKEITEN (Spalten):
   - WE (Wareneingang)
   - Service (Reparaturbearbeitung)
   - Service/QMB (Qualitätsbewertung)
   - Service/Vertrieb (Kundenkommunikation)
   - Service/QMB (Qualitätsbewertung)
   - Service/Vertrieb (Kundenkommunikation)
</rewritten_file> 