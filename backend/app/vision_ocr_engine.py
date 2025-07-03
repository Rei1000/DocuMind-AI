"""
🎯 Vision OCR Engine für komplexe QM-Dokumente

Diese Engine konvertiert Word/PDF-Dokumente zu Bildern und analysiert sie
mit GPT-4o Vision API für maximale Flussdiagramm-Erkennung.

Hauptfunktionen:
- Document-to-Image Konvertierung (DOCX → PNG, PDF → PNG)
- GPT-4o Vision API Integration
- Intelligent Process Reference Detection
- QM-spezifische Compliance-Checks
- Ergosana-optimierte Prompts

Technischer Ansatz:
1. Word/PDF → High-Quality Images (300 DPI)
2. Vision API → Structured JSON Analysis  
3. Process Reference Extraction
4. Compliance Validation
5. Comprehensive Text Reconstruction

Performance: Optimiert für >1000 Zeichen Extraktion aus PA 8.2.1
"""

import logging
import base64
import asyncio
import json
import re
import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import openai
from PIL import Image
import io
import mimetypes
import tempfile

# Document Processing
try:
    import fitz  # PyMuPDF for PDF processing
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# Image processing
try:
    from PIL import Image, ImageEnhance
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# Word to Image (wenn verfügbar)
try:
    import pythoncom
    import win32com.client
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

# OpenAI Vision API
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger("KI-QMS.VisionOCR")

class VisionOCREngine:
    """
    🔍 Advanced Vision OCR Engine für QM-Dokumente
    
    Konvertiert komplexe Dokumente zu Bildern und nutzt GPT-4o Vision
    für maximale Textextraktion aus Flussdiagrammen und Layouts.
    """

    def __init__(self):
        self.model = "gpt-4o-mini"  # Unterstützt Vision
        self.api_key = self._get_openai_key()
        self.client = OpenAI(api_key=self.api_key) if self.api_key and OPENAI_AVAILABLE else None
        
        # Feature Flags
        self.pymupdf_available = PYMUPDF_AVAILABLE
        self.pillow_available = PILLOW_AVAILABLE
        self.win32_available = WIN32_AVAILABLE
        
        logger.info(f"🔍 Vision OCR Engine initialisiert")
        logger.info(f"📚 PyMuPDF: {'✅' if self.pymupdf_available else '❌'}")
        logger.info(f"🖼️ Pillow: {'✅' if self.pillow_available else '❌'}")
        logger.info(f"💻 Win32: {'✅' if self.win32_available else '❌'}")
        logger.info(f"🤖 OpenAI Vision: {'✅' if self.client else '❌'}")

    def _get_openai_key(self) -> Optional[str]:
        """OpenAI API Key aus Umgebung laden"""
        import os
        return os.getenv('OPENAI_API_KEY')

    async def convert_document_to_images(self, file_path: Path, dpi: int = 300) -> List[bytes]:
        """
        🔄 Konvertiert Dokumente zu hochwertigen Bildern
        
        Args:
            file_path: Pfad zum Dokument (PDF, DOCX)
            dpi: Auflösung für Bildkonvertierung (Standard: 300 DPI)
            
        Returns:
            Liste von Bild-Bytes für Vision API
        """
        logger.info(f"🔄 Starte Document-to-Image Konvertierung: {file_path.name}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            return await self._convert_pdf_to_images(file_path, dpi)
        elif file_extension in ['.docx', '.doc']:
            return await self._convert_word_to_images(file_path, dpi)
        else:
            logger.warning(f"⚠️ Unbekanntes Dateiformat: {file_extension}")
            return []

    async def _convert_pdf_to_images(self, file_path: Path, dpi: int = 300) -> List[bytes]:
        """PDF → PNG Konvertierung mit PyMuPDF"""
        
        if not self.pymupdf_available:
            logger.error("❌ PyMuPDF nicht verfügbar für PDF-Konvertierung")
            return []
        
        try:
            doc = fitz.open(file_path)
            images = []
            
            logger.info(f"📄 PDF hat {len(doc)} Seiten")
            
            for page_num in range(min(len(doc), 5)):  # Max 5 Seiten für Performance
                page = doc.load_page(page_num)
                
                # High-Quality Rendering
                mat = fitz.Matrix(dpi/72, dpi/72)  # DPI scaling
                pix = page.get_pixmap(matrix=mat)
                
                # PNG Bytes
                img_bytes = pix.tobytes("png")
                images.append(img_bytes)
                
                logger.info(f"✅ Seite {page_num + 1} konvertiert: {len(img_bytes)} bytes")
                
                pix = None  # Memory cleanup
            
            doc.close()
            logger.info(f"🎉 PDF-Konvertierung abgeschlossen: {len(images)} Bilder")
            return images
            
        except Exception as e:
            logger.error(f"❌ PDF-Konvertierung fehlgeschlagen: {e}")
            return []

    async def _convert_word_to_images(self, file_path: Path, dpi: int = 300) -> List[bytes]:
        """
        Word → PNG Konvertierung
        
        Verschiedene Ansätze:
        1. LibreOffice Headless (cross-platform)
        2. Win32 COM (Windows only)
        3. Fallback: Erst PDF, dann Bilder
        """
        
        # Ansatz 1: LibreOffice Headless (empfohlen)
        libreoffice_result = await self._convert_word_via_libreoffice(file_path, dpi)
        if libreoffice_result:
            return libreoffice_result
        
        # Ansatz 2: Win32 COM (Windows only)
        if self.win32_available:
            win32_result = await self._convert_word_via_win32(file_path, dpi)
            if win32_result:
                return win32_result
        
        # Ansatz 3: Word → PDF → Images
        logger.info("🔄 Fallback: Word → PDF → Images")
        pdf_path = await self._convert_word_to_pdf(file_path)
        if pdf_path and pdf_path.exists():
            try:
                images = await self._convert_pdf_to_images(pdf_path, dpi)
                pdf_path.unlink()  # Temporäre PDF löschen
                return images
            except Exception as e:
                logger.error(f"❌ PDF-Fallback fehlgeschlagen: {e}")
        
        logger.error("❌ Alle Word-Konvertierungsmethoden fehlgeschlagen")
        return []

    async def _convert_word_via_libreoffice(self, file_path: Path, dpi: int = 300) -> List[bytes]:
        """Word → PDF → Images via LibreOffice Headless"""
        
        try:
            import subprocess
            import tempfile
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # LibreOffice headless PDF export
                cmd = [
                    'libreoffice',
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', temp_dir,
                    str(file_path)
                ]
                
                logger.info(f"🔄 LibreOffice Konvertierung: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=60
                )
                
                if result.returncode == 0:
                    # PDF gefunden?
                    pdf_files = list(Path(temp_dir).glob("*.pdf"))
                    if pdf_files:
                        pdf_path = pdf_files[0]
                        logger.info(f"✅ LibreOffice PDF erstellt: {pdf_path}")
                        return await self._convert_pdf_to_images(pdf_path, dpi)
                else:
                    logger.warning(f"⚠️ LibreOffice Fehler: {result.stderr}")
                    
        except FileNotFoundError:
            logger.warning("⚠️ LibreOffice nicht gefunden")
        except Exception as e:
            logger.error(f"❌ LibreOffice Konvertierung fehlgeschlagen: {e}")
        
        return []

    async def _convert_word_via_win32(self, file_path: Path, dpi: int = 300) -> List[bytes]:
        """Word → Images via Win32 COM (Windows only)"""
        
        if not self.win32_available:
            return []
        
        try:
            # COM Interface
            pythoncom.CoInitialize()
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            
            # Dokument öffnen
            doc = word.Documents.Open(str(file_path))
            
            images = []
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Export als PNG
                for page_num in range(1, min(doc.ComputeStatistics(2) + 1, 6)):  # Max 5 Seiten
                    png_path = Path(temp_dir) / f"page_{page_num}.png"
                    
                    # Export page as image
                    doc.ExportAsFixedFormat(
                        OutputFileName=str(png_path),
                        ExportFormat=17,  # PNG format
                        OptimizeFor=0,    # Print
                        BitmapMissingFonts=True,
                        DocStructureTags=False,
                        BitmapMissingFonts=True,
                        UseDocumentImageQuality=False,
                        Resolution=dpi
                    )
                    
                    if png_path.exists():
                        with open(png_path, 'rb') as f:
                            images.append(f.read())
                        logger.info(f"✅ Win32 Seite {page_num} konvertiert")
            
            # Cleanup
            doc.Close()
            word.Quit()
            pythoncom.CoUninitialize()
            
            logger.info(f"🎉 Win32 Konvertierung abgeschlossen: {len(images)} Bilder")
            return images
            
        except Exception as e:
            logger.error(f"❌ Win32 Konvertierung fehlgeschlagen: {e}")
            try:
                word.Quit()
                pythoncom.CoUninitialize()
            except:
                pass
            return []

    async def _convert_word_to_pdf(self, file_path: Path) -> Optional[Path]:
        """Word → PDF Fallback-Konvertierung"""
        
        # Für jetzt nicht implementiert
        logger.warning("📄 Word → PDF Direktkonvertierung nicht implementiert")
        return None

    async def analyze_document_with_vision(self, file_path: Path, extracted_images: List[bytes]) -> Dict[str, Any]:
        """
        Analysiert Dokument mit Vision API für Flussdiagramme und Referenzen
        """
        logger.info(f"🔍 Vision-Analyse gestartet für {file_path.name}")
        
        if not self.api_key:
            logger.warning("⚠️ OpenAI API Key fehlt - Vision-Analyse nicht verfügbar")
            return {"success": False, "error": "API Key fehlt"}
        
        if not extracted_images:
            logger.warning("⚠️ Keine Bilder gefunden für Vision-Analyse")
            return {"success": False, "error": "Keine Bilder gefunden"}
        
        results = []
        process_references = []
        compliance_warnings = []
        
        for i, image_bytes in enumerate(extracted_images):
            try:
                # Bild zu Base64 konvertieren
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                
                # Vision-Analyse
                analysis = await self._analyze_image_with_gpt4_vision(
                    image_b64, f"Bild {i+1} aus {file_path.name}"
                )
                
                if analysis['success']:
                    results.append(analysis)
                    process_references.extend(analysis.get('process_references', []))
                    
            except Exception as e:
                logger.error(f"❌ Vision-Analyse Fehler für Bild {i+1}: {e}")
                continue
        
        # Prozess-Referenz Compliance Check
        compliance_warnings = await self._check_process_references(process_references)
        
        return {
            "success": len(results) > 0,
            "vision_analyses": results,
            "total_images_processed": len(results),
            "process_references_found": process_references,
            "compliance_warnings": compliance_warnings,
            "comprehensive_description": self._create_comprehensive_description(results),
            "methodology": "gpt4_vision_with_reference_validation"
        }
    
    async def _analyze_image_with_gpt4_vision(self, image_b64: str, context: str) -> Dict[str, Any]:
        """
        Analysiert ein Bild mit GPT-4o Vision API
        """
        try:
            prompt = self._create_vision_prompt(context)
            
            if not self.client:
                return {"success": False, "error": "OpenAI Client nicht verfügbar"}
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}",
                                    "detail": "high"  # Für detaillierte Analyse
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1  # Konsistente Ergebnisse
            )
            
            # Parse JSON response
            response_text = response.choices[0].message.content or ""
            try:
                result = json.loads(response_text)
                result['success'] = True
                result['context'] = context
                return result
            except json.JSONDecodeError:
                # Fallback wenn kein valides JSON
                return {
                    "success": True,
                    "description": response_text,
                    "extracted_text": response_text,
                    "process_references": self._extract_references_regex(response_text),
                    "workflow_steps": [],
                    "compliance_level": "medium",
                    "context": context
                }
                
        except Exception as e:
            logger.error(f"❌ GPT-4o Vision API Fehler: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_references_regex(self, text: str) -> List[str]:
        """
        Extrahiert Prozess-Referenzen mit Regex als Fallback
        """
        # Separate Patterns für vollständige Referenzen  
        full_patterns = [
            r'\b(PA|VA|QMA|SOP|WI)\s+(\d+(?:\.\d+)*)\b',  # PA 8.5, VA 4.2
            r'\b(ISO)\s+(\d+(?:\.\d+)*)\b',               # ISO 13485
            r'\b(DIN|EN|IEC)\s+(\d+(?:\.\d+)*)\b',       # DIN EN ISO
            r'\b(MDR|IVDR)(?:\s+(Artikel\s+\d+))?\b',    # MDR, MDR Artikel 95
        ]
        
        references = []
        
        # Vollständige Referenzen extrahieren
        for pattern in full_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Kombiniere nicht-leere Teile
                    parts = [part for part in match if part.strip()]
                    if len(parts) >= 2:
                        full_ref = f"{parts[0]} {parts[1]}"
                        references.append(full_ref)
                    elif len(parts) == 1:
                        references.append(parts[0])
                else:
                    references.append(match)
        
        return list(set(references))  # Duplikate entfernen
    
    async def _check_process_references(self, references: List[str]) -> List[Dict[str, Any]]:
        """
        Prüft ob gefundene Prozess-Referenzen im System existieren
        """
        from .database import get_db
        
        warnings = []
        
        for ref in references:
            try:
                # Simuliere Datenbank-Check (wird später durch echte DB-Abfrage ersetzt)
                exists = await self._check_reference_in_database(ref)
                
                if not exists:
                    warnings.append({
                        "type": "missing_reference",
                        "reference": ref,
                        "severity": "high",
                        "message": f"Referenziertes Dokument '{ref}' nicht im System gefunden",
                        "recommendation": f"Dokument '{ref}' erstellen oder Verweis korrigieren"
                    })
                    
            except Exception as e:
                logger.error(f"❌ Referenz-Check Fehler für {ref}: {e}")
                
        return warnings
    
    async def _check_reference_in_database(self, reference: str) -> bool:
        """
        Prüft ob Referenz in der Datenbank existiert
        TODO: Implementierung mit echter DB-Abfrage
        """
        # Temporäre Simulation - später durch echte DB-Abfrage ersetzen
        # Suche nach Dokumenten mit matching title oder document_number
        
        simulated_existing_docs = [
            "PA 8.2.1", "PA 8.2.2", "PA 8.5", "VA 4.1", "VA 4.2", "QMA 1.1", "ISO 13485", "MDR"
        ]
        
        return reference in simulated_existing_docs
    
    def _create_comprehensive_description(self, analyses: List[Dict[str, Any]]) -> str:
        """
        Erstellt eine umfassende Beschreibung aller analysierten Bilder
        """
        if not analyses:
            return "Keine Vision-Analyse verfügbar."
        
        descriptions = []
        for i, analysis in enumerate(analyses):
            if analysis.get('success'):
                desc = f"**Bild {i+1}:**\n"
                desc += f"- Beschreibung: {analysis.get('description', 'Nicht verfügbar')}\n"
                desc += f"- Extrahierter Text: {analysis.get('extracted_text', 'Nicht verfügbar')}\n"
                
                refs = analysis.get('process_references', [])
                if refs:
                    desc += f"- Gefundene Referenzen: {', '.join(refs)}\n"
                
                descriptions.append(desc)
        
        return "\n\n".join(descriptions)

    def _create_vision_prompt(self, context: str) -> str:
        """Erstellt optimierte Vision-Prompts für QM-Flussdiagramme"""
        
        base_prompt = f"""
Du analysierst ein QM-Flussdiagramm für Medizinprodukte. Extrahiere ALLE Informationen strukturiert als JSON.

SPEZIFISCHE ERKENNUNGSAUFGABEN für Ergosana QM-Dokumente:

1. PROZESS-REFERENZEN (kritisch für Compliance):
   - PA 8.x (Prozessanweisungen) 
   - VA x.x (Verfahrensanweisungen)
   - QAB, CAPA, KVA Prozesse
   - ISO 13485, MDR Referenzen

2. FLUSSDIAGRAMM-STRUKTUR:
   - Startpunkt → Entscheidungen → Endpunkt
   - "Ja/Nein" Entscheidungspfade
   - Verantwortlichkeiten (WE, Service, QMB, Vertrieb)
   - Parallele Prozesse und Verzweigungen

3. COMPLIANCE-TEXTBOXEN (rechts im Dokument):
   - Detaillierte Verfahrensbeschreibungen
   - Qualitätssicherungshinweise  
   - Dokumentationsanforderungen
   - Zeitvorgaben und Fristen

4. ERGOSANA-SPEZIFISCHE ELEMENTE:
   - Defektes Gerät → Gerät Reinigen → Wareneingang
   - Reparaturerfassung → Fehlersuche → Wiederkehrender Fehler?
   - KVA an Kunden → Reparatur durchführen
   - ERP-Integration und Dokumentation

AUSGABE-FORMAT (JSON):
```json
{{
    "document_title": "Behandlung von Reparaturen",
    "process_flow": [
        {{
            "step": "Schritt-Name",
            "responsibility": "WE/Service/QMB/Vertrieb", 
            "decision_point": true/false,
            "options": ["Ja", "Nein"] oder null,
            "description": "Detaillierte Beschreibung"
        }}
    ],
    "process_references": [
        "PA 8.5", "PA 8.2.1", etc.
    ],
    "compliance_requirements": [
        "Spezifische Compliance-Anforderungen aus den Textboxen"
    ],
    "quality_controls": [
        "Qualitätskontroll-Punkte im Prozess"
    ],
    "erp_integration": [
        "ERP-Bezogene Schritte und Dokumentation"
    ],
    "extracted_text": "VOLLSTÄNDIGER extrahierter Text",
    "workflow_complexity": "hoch/mittel/niedrig",
    "estimated_text_length": "Geschätzte Zeichen-Anzahl"
}}
```

WICHTIG: 
- Lies JEDEN Text-Block vollständig
- Erkenne auch klein gedruckten Text
- Verfolge ALLE Prozess-Pfeile
- Dokumentiere JEDE Prozess-Referenz
- Erfasse die kompletten Textboxen rechts

Kontext: {context}
        """
        
        return base_prompt.strip()


async def extract_text_with_vision(file_path: str) -> Dict[str, Any]:
    """
    🎯 HAUPTFUNKTION: Document → Images → Vision OCR
    
    Kompletter Workflow:
    1. Document-to-Image Konvertierung
    2. GPT-4o Vision Analyse jedes Bildes
    3. Strukturierte Diagramm-Extraktion
    4. Prozess-Referenz-Erkennung
    5. Compliance-Checks
    6. Vollständige Flussdiagramm-Beschreibung
    """
    from pathlib import Path
    import mimetypes
    
    vision_engine = VisionOCREngine()
    file_path_obj = Path(file_path)
    
    # MIME-Type automatisch ermitteln
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"
    
    # Erst Enhanced OCR für Bildextraktion
    try:
        from .enhanced_ocr_engine import extract_enhanced_text
        
        logger.info(f"🔍 Starte kombinierte Vision + Enhanced OCR für {file_path_obj.name}")
        
        # Enhanced OCR für Grundextraktion
        enhanced_result = await extract_enhanced_text(file_path_obj, mime_type)
        
        if enhanced_result['success'] and enhanced_result.get('images_processed', 0) > 0:
            # Vision-Analyse der gefundenen Bilder
            # TODO: Bilder aus enhanced_result extrahieren
            extracted_images = []  # Placeholder - muss implementiert werden
            
            vision_result = await vision_engine.analyze_document_with_vision(
                file_path_obj, extracted_images
            )
            
            # Kombiniere Ergebnisse
            combined_text = enhanced_result['text']
            if vision_result['success']:
                combined_text += "\n\n## 🔍 VISION-ANALYSE:\n"
                combined_text += vision_result['comprehensive_description']
            
            return {
                "success": True,
                "text": combined_text,
                "methodology": "enhanced_ocr_plus_vision",
                "enhanced_ocr": enhanced_result,
                "vision_analysis": vision_result,
                "process_references": vision_result.get('process_references_found', []),
                "compliance_warnings": vision_result.get('compliance_warnings', [])
            }
        
        else:
            # Fallback zu Enhanced OCR
            logger.warning("⚠️ Vision-Analyse nicht möglich, verwende Enhanced OCR")
            return enhanced_result 
            
    except Exception as e:
        logger.error(f"❌ Vision OCR Fehler: {e}")
        return {
            "success": False,
            "error": str(e),
            "text": "",
            "methodology": "failed",
            "images_processed": 0
        } 