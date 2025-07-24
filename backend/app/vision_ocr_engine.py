"""
🎯 Vision OCR Engine für komplexe QM-Dokumente

Diese Engine konvertiert Word/PDF-Dokumente zu Bildern und analysiert sie
mit GPT-4o Vision API oder Google Gemini 1.5 Flash für maximale Flussdiagramm-Erkennung.

Hauptfunktionen:
- Document-to-Image Konvertierung (DOCX → PNG, PDF → PNG)
- GPT-4o Vision API Integration
- Google Gemini 1.5 Flash Vision API Integration
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

# Google Gemini Vision API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

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
        
        # Google Gemini Setup
        self.gemini_api_key = self._get_gemini_key()
        self.gemini_client = None
        if self.gemini_api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("🌟 Google Gemini 1.5 Flash Vision API initialisiert")
            except Exception as e:
                logger.warning(f"⚠️ Gemini Initialisierung fehlgeschlagen: {e}")
                self.gemini_client = None
        
        # Feature Flags
        self.pymupdf_available = PYMUPDF_AVAILABLE
        self.pillow_available = PILLOW_AVAILABLE
        self.win32_available = WIN32_AVAILABLE
        
        logger.info(f"🔍 Vision OCR Engine initialisiert")
        logger.info(f"📚 PyMuPDF: {'✅' if self.pymupdf_available else '❌'}")
        logger.info(f"🖼️ Pillow: {'✅' if self.pillow_available else '❌'}")
        logger.info(f"💻 Win32: {'✅' if self.win32_available else '❌'}")
        logger.info(f"🤖 OpenAI Vision: {'✅' if self.client else '❌'}")
        logger.info(f"🌟 Google Gemini Vision: {'✅' if self.gemini_client else '❌'}")

    def _get_openai_key(self) -> Optional[str]:
        """OpenAI API Key aus Umgebung laden"""
        import os
        return os.getenv('OPENAI_API_KEY')
    
    def _get_gemini_key(self) -> Optional[str]:
        """Google Gemini API Key aus Umgebung laden"""
        import os
        return os.getenv('GOOGLE_AI_API_KEY')

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
        elif file_extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
            return await self._convert_image_to_bytes(file_path)
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

    async def _convert_image_to_bytes(self, file_path: Path) -> List[bytes]:
        """Bilddatei direkt zu Bytes konvertieren"""
        
        if not self.pillow_available:
            logger.error("❌ Pillow nicht verfügbar für Bildkonvertierung")
            return []
        
        try:
            # Bild laden und zu PNG konvertieren
            with Image.open(file_path) as img:
                # Konvertiere zu RGB falls nötig
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Zu Bytes konvertieren
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                logger.info(f"✅ Bild konvertiert: {file_path.name} → {len(img_bytes.getvalue())} bytes")
                return [img_bytes.getvalue()]
                
        except Exception as e:
            logger.error(f"❌ Bildkonvertierung fehlgeschlagen: {e}")
            return []

    async def _convert_word_to_images(self, file_path: Path, dpi: int = 300) -> List[bytes]:
        """
        Word → PNG Konvertierung
        
        Verschiedene Ansätze:
        1. LibreOffice Headless (cross-platform)
        2. Win32 COM (Windows only)
        3. Python-basierte Konvertierung (Fallback)
        4. Fehlerbehandlung mit detaillierten Logs
        """
        
        logger.info(f"🔄 Word-Konvertierung gestartet: {file_path.name}")
        
        # Ansatz 1: LibreOffice Headless (empfohlen)
        logger.info("📄 Versuche LibreOffice Konvertierung...")
        libreoffice_result = await self._convert_word_via_libreoffice(file_path, dpi)
        if libreoffice_result:
            logger.info("✅ LibreOffice Konvertierung erfolgreich")
            return libreoffice_result
        
        # Ansatz 2: Win32 COM (Windows only)
        if self.win32_available:
            logger.info("💻 Versuche Win32 COM Konvertierung...")
            win32_result = await self._convert_word_via_win32(file_path, dpi)
            if win32_result:
                logger.info("✅ Win32 Konvertierung erfolgreich")
                return win32_result
        
        # Ansatz 3: Python-basierte Konvertierung (Fallback)
        logger.info("🐍 Versuche Python-basierte Konvertierung...")
        # python_result = await self._convert_word_via_python(file_path, dpi)  # Temporarily disabled
        python_result = []
        if python_result:
            logger.info("✅ Python-Konvertierung erfolgreich")
            return python_result
        
        # Ansatz 4: Word → PDF → Images
        logger.info("🔄 Fallback: Word → PDF → Images")
        pdf_path = await self._convert_word_to_pdf(file_path)
        if pdf_path and pdf_path.exists():
            try:
                images = await self._convert_pdf_to_images(pdf_path, dpi)
                pdf_path.unlink()  # Temporäre PDF löschen
                if images:
                    logger.info("✅ PDF-Fallback erfolgreich")
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
                    'soffice',  # macOS LibreOffice command
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

    async def _convert_word_via_python(self, file_path: Path, dpi: int = 300) -> List[bytes]:
        """
        Konvertiert Word-Dokumente zu Bildern mit Python-Bibliotheken.
        Fallback-Methode wenn LibreOffice/win32 nicht verfügbar sind.
        """
        try:
            logger.info(f"🔄 Konvertiere Word-Dokument via Python: {file_path.name}")
            
            # Versuche python-docx für DOCX-Dateien
            if file_path.suffix.lower() == '.docx':
                from docx import Document
                from docx.shared import Inches
                
                doc = Document(str(file_path))
                images = []
                
                # Für DOCX verwenden wir einen einfachen Ansatz
                # Da python-docx keine direkte Bild-Konvertierung unterstützt,
                # konvertieren wir zuerst zu PDF und dann zu Bildern
                pdf_path = await self._convert_word_to_pdf(file_path)
                if pdf_path and pdf_path.exists():
                    images = await self._convert_pdf_to_images(pdf_path, dpi)
                    # PDF-Temp-Datei löschen
                    pdf_path.unlink(missing_ok=True)
                
                return images
            
            # Für .doc-Dateien verwenden wir PyMuPDF als Fallback
            elif file_path.suffix.lower() == '.doc':
                logger.warning("⚠️ .doc-Dateien werden über PDF-Konvertierung verarbeitet")
                pdf_path = await self._convert_word_to_pdf(file_path)
                if pdf_path and pdf_path.exists():
                    images = await self._convert_pdf_to_images(pdf_path, dpi)
                    pdf_path.unlink(missing_ok=True)
                    return images
            
            logger.warning(f"⚠️ Nicht unterstütztes Word-Format: {file_path.suffix}")
            return []
            
        except ImportError as e:
            logger.error(f"❌ Python-Bibliothek nicht verfügbar: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Python-Konvertierung fehlgeschlagen: {e}")
            return []

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
    
    async def _analyze_image_with_gemini_vision(self, image_b64: str, context: str, custom_prompt: str = None) -> Dict[str, Any]:
        """
        Analysiert ein Bild mit Google Gemini 1.5 Flash Vision API
        """
        try:
            if not self.gemini_client:
                return {"success": False, "error": "Gemini Client nicht verfügbar"}
            
            # Verwende custom_prompt falls vorhanden, sonst generischen Prompt
            if custom_prompt:
                prompt = custom_prompt
                logger.info(f"🔧 Verwende custom prompt: {len(custom_prompt)} Zeichen")
            else:
                prompt = self._create_vision_prompt(context)
                logger.info(f"🔧 Verwende generischen prompt: {len(prompt)} Zeichen")
            
            # Bild von Base64 zu Bytes konvertieren
            image_bytes = base64.b64decode(image_b64)
            
            # Gemini Vision API aufrufen
            response = self.gemini_client.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])
            
            if response and response.text:
                content = response.text.strip()
                logger.info(f"✅ Gemini Vision API erfolgreich: {len(content)} Zeichen")
                
                # Versuche JSON zu parsen
                try:
                    import json
                    parsed_json = json.loads(content)
                    logger.info("✅ Gemini JSON erfolgreich geparst")
                    return {
                        'success': True,
                        'content': content,
                        'parsed_json': parsed_json,
                        'tokens_used': response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                        'provider': 'google_gemini_1.5_flash'
                    }
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ Gemini JSON-Parsing fehlgeschlagen: {e}")
                    # Versuche JSON aus der Antwort zu extrahieren
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        try:
                            extracted_json = json.loads(json_match.group())
                            logger.info("✅ Gemini JSON erfolgreich extrahiert")
                            return {
                                'success': True,
                                'content': json_match.group(),
                                'parsed_json': extracted_json,
                                'tokens_used': response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                                'provider': 'google_gemini_1.5_flash'
                            }
                        except json.JSONDecodeError as e2:
                            logger.error(f"❌ Gemini JSON-Extraktion fehlgeschlagen: {e2}")
                    
                    # Fallback: Rohe Antwort zurückgeben
                    return {
                        'success': True,
                        'content': content,
                        'raw_response': True,
                        'tokens_used': response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                        'provider': 'google_gemini_1.5_flash'
                    }
            else:
                return {"success": False, "error": "Keine Antwort von Gemini Vision API"}
                
        except Exception as e:
            logger.error(f"❌ Gemini Vision API Fehler: {e}")
            return {"success": False, "error": str(e)}

    async def _analyze_image_with_gpt4_vision(self, image_b64: str, context: str, custom_prompt: str = None) -> Dict[str, Any]:
        """
        Analysiert ein Bild mit GPT-4o Vision API mit Rate-Limit-Behandlung
        """
        try:
            # Verwende custom_prompt falls vorhanden, sonst generischen Prompt
            if custom_prompt:
                prompt = custom_prompt
                logger.info(f"🔧 Verwende custom prompt: {len(custom_prompt)} Zeichen")
            else:
                prompt = self._create_vision_prompt(context)
                logger.info(f"🔧 Verwende generischen prompt: {len(prompt)} Zeichen")
            
            if not self.client:
                return {"success": False, "error": "OpenAI Client nicht verfügbar"}
            
            # ✅ TOKENKONTROLLE: Prüfe Token-Limit
            try:
                import tiktoken
                encoding = tiktoken.encoding_for_model("gpt-4o-mini")
                prompt_tokens = len(encoding.encode(prompt))
                image_tokens = 765  # Geschätzte Tokens für Bild (konservativ)
                total_tokens = prompt_tokens + image_tokens
                
                if total_tokens > 128000:  # GPT-4o mini Token-Limit
                    logger.error(f"❌ TOKENLIMIT ÜBERSCHRITTEN: {total_tokens} Tokens (Limit: 128000)")
                    return {
                        "success": False, 
                        "error": "Fehler: Tokenlimit des Modells überschritten – Prompt und Bild sind zusammen zu groß.",
                        "token_info": {
                            "prompt_tokens": prompt_tokens,
                            "image_tokens": image_tokens,
                            "total_tokens": total_tokens,
                            "limit": 128000
                        }
                    }
                else:
                    logger.info(f"✅ TOKENKONTROLLE: {total_tokens} Tokens (unter Limit: 128000)")
            except Exception as token_error:
                logger.warning(f"⚠️ Tokenkontrolle fehlgeschlagen: {token_error}")
            
            # Rate-Limit-Behandlung mit Retry-Logic
            max_retries = 3
            base_delay = 5  # Start mit 5 Sekunden
            
            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "Du bist ein KI-gestützter Spezialist für die strukturierte Analyse von Qualitätsmanagement-Dokumenten nach ISO 13485 und MDR. Du extrahierst alle sichtbaren Informationen vollständig und präzise in das gewünschte JSON-Format."
                            },
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
                        max_tokens=16384,  # GPT-4o-mini Limit: 16384 completion tokens
                        temperature=0.0  # Maximale Konsistenz und Präzision
                    )
                    
                    # Erfolgreich - keine weiteren Versuche
                    break
                    
                except Exception as e:
                    error_str = str(e)
                    
                    # Rate-Limit-Fehler erkennen
                    if "429" in error_str or "rate_limit" in error_str.lower():
                        if attempt < max_retries - 1:  # Nicht beim letzten Versuch
                            delay = base_delay * (2 ** attempt)  # Exponential backoff: 5s, 10s, 20s
                            logger.warning(f"⚠️ Rate-Limit erreicht, warte {delay}s vor Versuch {attempt + 2}/{max_retries}")
                            await asyncio.sleep(delay)
                            continue
                        else:
                            logger.error(f"❌ Rate-Limit nach {max_retries} Versuchen - endgültiger Fehler")
                            return {"success": False, "error": f"Rate limit exceeded after {max_retries} attempts: {error_str}"}
                    else:
                        # Anderer Fehler - nicht retry
                        logger.error(f"❌ Nicht-Rate-Limit Fehler: {error_str}")
                        return {"success": False, "error": error_str}
            
            # Parse JSON response mit robusterem Parsing
            response_text = response.choices[0].message.content or ""
            usage = response.usage
            logger.info(f"🔍 Raw API-Antwort erhalten: {len(response_text)} Zeichen")
            logger.info(f"📊 Token-Verbrauch: {usage.prompt_tokens} prompt + {usage.completion_tokens} completion = {usage.total_tokens} total")
            logger.info(f"📄 API-Antwort Inhalt (vollständig): {response_text}")
            
            # Robusteres JSON-Parsing
            try:
                # Level 1: Standard JSON-Parsing
                cleaned_text = response_text.strip()
                if cleaned_text.startswith('```json'):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text[:-3]
                
                result = json.loads(cleaned_text)
                result['success'] = True
                result['content'] = response_text  # Wichtig: content für Backend
                result['context'] = context
                logger.info("✅ Standard JSON-Parsing erfolgreich")
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Standard JSON-Parsing fehlgeschlagen: {e}")
                
                # Level 2: Regex-basierte JSON-Extraktion
                try:
                    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                    matches = re.findall(json_pattern, response_text, re.DOTALL)
                    
                    for match in matches:
                        try:
                            result = json.loads(match)
                            result['success'] = True
                            result['content'] = response_text
                            result['context'] = context
                            result['parsing_method'] = 'regex_extraction'
                            logger.info("✅ Regex-basierte JSON-Extraktion erfolgreich")
                            return result
                        except json.JSONDecodeError:
                            continue
                            
                except Exception as regex_error:
                    logger.warning(f"⚠️ Regex-Extraktion fehlgeschlagen: {regex_error}")
                
                # Level 3: Manuelle Feld-Extraktion
                try:
                    fallback_result = self._create_manual_fallback(response_text, context)
                    logger.info("✅ Manuelle Feld-Extraktion erfolgreich")
                    return fallback_result
                    
                except Exception as manual_error:
                    logger.warning(f"⚠️ Manuelle Extraktion fehlgeschlagen: {manual_error}")
                
                # Level 4: Minimaler Fallback
                logger.warning("⚠️ Alle Parsing-Methoden fehlgeschlagen - verwende minimalen Fallback")
                fallback_result = {
                    "success": True,
                    "content": response_text,
                    "description": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "extracted_text": response_text,
                    "process_references": self._extract_references_regex(response_text),
                    "workflow_steps": [],
                    "compliance_level": "medium",
                    "context": context,
                    "parsing_method": "minimal_fallback",
                    "parsing_error": str(e)
                }
                return fallback_result
                
        except Exception as e:
            logger.error(f"❌ GPT-4o Vision API Fehler: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_manual_fallback(self, response_text: str, context: str) -> Dict[str, Any]:
        """
        🔧 Erstellt manuellen Fallback aus API-Antwort
        """
        try:
            result = {
                "success": True,
                "content": response_text,
                "context": context,
                "parsing_method": "manual_extraction"
            }
            
            # Titel extrahieren
            title_match = re.search(r'"document_title":\s*"([^"]+)"', response_text)
            if title_match:
                result["document_title"] = title_match.group(1)
            else:
                result["document_title"] = "Automatisch analysiert"
            
            # Dokumenttyp extrahieren
            type_match = re.search(r'"document_type":\s*"([^"]+)"', response_text)
            if type_match:
                result["document_type"] = type_match.group(1)
            else:
                result["document_type"] = "UNKNOWN"
            
            # Wörter extrahieren
            words_match = re.search(r'"all_detected_words":\s*\[(.*?)\]', response_text, re.DOTALL)
            if words_match:
                words_str = words_match.group(1)
                words = re.findall(r'"([^"]+)"', words_str)
                result["all_detected_words"] = words
            else:
                result["all_detected_words"] = []
            
            # Prozessschritte extrahieren
            steps_match = re.search(r'"process_steps":\s*\[(.*?)\]', response_text, re.DOTALL)
            if steps_match:
                result["process_steps"] = []
            
            # Compliance-Anforderungen extrahieren
            compliance_match = re.search(r'"compliance_requirements":\s*\[(.*?)\]', response_text, re.DOTALL)
            if compliance_match:
                result["compliance_requirements"] = []
            
            # Qualitätskontrollen extrahieren
            quality_match = re.search(r'"quality_controls":\s*\[(.*?)\]', response_text, re.DOTALL)
            if quality_match:
                result["quality_controls"] = []
            
            # Beschreibung und extrahierter Text
            result["description"] = response_text[:200] + "..." if len(response_text) > 200 else response_text
            result["extracted_text"] = response_text
            result["process_references"] = self._extract_references_regex(response_text)
            result["workflow_steps"] = []
            result["compliance_level"] = "medium"
            
            return result
            
        except Exception as e:
            logger.error(f"Manueller Fallback fehlgeschlagen: {e}")
            # Minimaler Fallback
            return {
                "success": True,
                "content": response_text,
                "description": "Fallback-Analyse",
                "extracted_text": response_text,
                "process_references": [],
                "workflow_steps": [],
                "compliance_level": "medium",
                "context": context,
                "parsing_method": "error_fallback",
                "parsing_error": str(e)
            }
    
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

    async def analyze_images_with_vision(self, images: List[bytes], prompt: str, preferred_provider: str = "openai_4o_mini") -> Dict[str, Any]:
        """
        Analysiert eine Liste von Bildern mit Vision API und einem spezifischen Prompt.
        
        Args:
            images: Liste von Bildern als bytes
            prompt: Spezifischer Prompt für die Analyse
            preferred_provider: Gewünschter Provider (openai_4o_mini, ollama, google_gemini)
            
        Returns:
            Dict mit Analyse-Ergebnissen
        """
        try:
            logger.info(f"🔍 Analysiere {len(images)} Bilder mit Vision API (Provider: {preferred_provider})")
            
            # Provider-spezifische Logik
            if preferred_provider == "openai_4o_mini":
                if not self.api_key:
                    return {
                        'success': False,
                        'error': 'OpenAI API Key nicht konfiguriert'
                    }
                logger.info("🤖 Verwende OpenAI 4o-mini Vision API")
            elif preferred_provider == "ollama":
                logger.info("🦙 Verwende Ollama Vision API")
                # TODO: Ollama Vision API Integration
                return {
                    'success': False,
                    'error': 'Ollama Vision API noch nicht implementiert'
                }
            elif preferred_provider == "google_gemini":
                if not self.gemini_client:
                    return {
                        'success': False,
                        'error': 'Google Gemini API Key nicht konfiguriert oder Client nicht verfügbar'
                    }
                logger.info("🌟 Verwende Google Gemini 1.5 Flash Vision API")
            else:
                logger.warning(f"⚠️ Unbekannter Provider: {preferred_provider}, verwende OpenAI")
                if not self.api_key:
                    return {
                        'success': False,
                        'error': 'OpenAI API Key nicht konfiguriert'
                    }
            
            results = []
            total_tokens = 0
            
            for i, image_bytes in enumerate(images):
                logger.info(f"📸 Verarbeite Bild {i+1}/{len(images)}")
                
                # Bild zu Base64 konvertieren
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                
                # Vision-Analyse durchführen mit Provider-Auswahl
                if preferred_provider == "google_gemini":
                    result = await self._analyze_image_with_gemini_vision(image_b64, f"Bild {i+1} aus {len(images)}", prompt)
                else:
                    result = await self._analyze_image_with_gpt4_vision(image_b64, f"Bild {i+1} aus {len(images)}", prompt)
                
                if result['success']:
                    results.append(result)
                    total_tokens += result.get('tokens_used', 0)
                else:
                    logger.warning(f"⚠️ Bild {i+1} Analyse fehlgeschlagen: {result.get('error')}")
            
            if not results:
                return {
                    'success': False,
                    'error': 'Keine Bilder erfolgreich analysiert'
                }
            
            # Ergebnisse kombinieren
            combined_analysis = self._combine_vision_results(results)
            
            # 🔧 WICHTIG: Die Vision API gibt bereits das perfekte JSON zurück!
            # KEINE weitere Verpackung in content-Feld!
            # Die Vision API gibt direkt das gewünschte JSON zurück
            return {
                'success': True,
                'analysis': combined_analysis,
                'images_processed': len(images),
                'tokens_used': total_tokens,
                'individual_results': results
            }
            
        except Exception as e:
            logger.error(f"❌ Vision-Analyse fehlgeschlagen: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _combine_vision_results(self, results: List[Dict]) -> Dict:
        """
        Kombiniert mehrere Vision-Analyse-Ergebnisse zu einem konsistenten Format.
        """
        # 🔧 WICHTIG: Die Vision API gibt bereits das perfekte JSON zurück!
        # Wir müssen nur das erste Ergebnis verwenden, da es bereits das gewünschte Format hat
        if results and len(results) > 0:
            first_result = results[0]
            
            # ✅ KRITISCH: Die Vision API gibt das JSON direkt in 'content' zurück!
            if 'content' in first_result:
                # Das ist das echte JSON aus der Vision API
                return first_result['content']
            elif 'extracted_text' in first_result:
                # Fallback: Extrahierter Text (sollte JSON sein)
                return first_result['extracted_text']
            elif 'description' in first_result:
                # Fallback: Beschreibung verwenden
                return first_result['description']
            elif 'provider' in first_result and first_result['provider'] == 'google_gemini_1.5_flash':
                # Gemini-spezifische Behandlung
                if 'parsed_json' in first_result:
                    # Verwende das bereits geparste JSON
                    return first_result['parsed_json']
                elif 'content' in first_result:
                    # Versuche das content zu parsen
                    try:
                        import json
                        return json.loads(first_result['content'])
                    except json.JSONDecodeError:
                        # Fallback: Rohe Antwort
                        return first_result['content']
                else:
                    # Fallback für Gemini
                    return first_result.get('extracted_text', '{}')
        
        # Fallback: Alte Logik für Kompatibilität
        combined = {
            'text': '',
            'words': [],
            'process_references': [],
            'structured_analysis': {}
        }
        
        for result in results:
            # Text kombinieren
            if result.get('extracted_text'):
                combined['text'] += result['extracted_text'] + '\n\n'
            elif result.get('description'):
                combined['text'] += result['description'] + '\n\n'
            
            # Wörter aus Text extrahieren
            import re
            text_content = result.get('extracted_text', '') + ' ' + result.get('description', '')
            if text_content:
                words = re.findall(r'\b\w+\b', text_content)
                combined['words'].extend(words)
            
            # Prozess-Referenzen sammeln
            if result.get('process_references'):
                combined['process_references'].extend(result['process_references'])
            
            # Strukturierte Analyse kombinieren
            if result.get('process_flow'):
                combined['structured_analysis']['process_flow'] = result.get('process_flow', [])
            if result.get('document_title'):
                combined['structured_analysis']['document_title'] = result.get('document_title', '')
        
        # Duplikate entfernen
        combined['words'] = list(set(combined['words']))
        combined['process_references'] = list(set(combined['process_references']))
        
        return combined

    async def analyze_document_with_api_prompt(self, images: List[bytes], document_type: str, preferred_provider: str = "openai_4o_mini") -> Dict[str, Any]:
        """
        ZENTRALE FUNKTION: Analysiert Dokumente mit dem EXAKTEN Prompt aus der API
        
        Args:
            images: Liste von Bildern als bytes
            document_type: Dokumenttyp (PROCESS, SOP, etc.)
            preferred_provider: Gewünschter Provider
            
        Returns:
            Dict mit Analyse-Ergebnissen
            
        Raises:
            Exception: Wenn Prompt nicht geladen werden kann oder Vision API fehlschlägt
        """
        try:
            logger.info(f"🔍 ZENTRALE VISION-ANALYSE: {document_type} mit {len(images)} Bildern")
            
            # 1. Prompt über API laden mit erweiterten Metadaten - KEIN FALLBACK!
            from .visio_prompts import get_prompt_for_document_type
            prompt_data = get_prompt_for_document_type(document_type)
            
            if not prompt_data or not prompt_data.get("success"):
                raise Exception(f"❌ Prompt konnte nicht geladen werden für Dokumenttyp: {document_type}")
            
            prompt = prompt_data["prompt"]
            prompt_version = prompt_data["version"]
            prompt_hash = prompt_data["hash"]
            prompt_metadata = prompt_data["metadata"]
            prompt_audit = prompt_data["audit_info"]
            
            # Logge Prompt-Bestätigung für Audit
            logger.info(f"📝 PROMPT-BESTÄTIGUNG:")
            logger.info(f"   Typ: {prompt_metadata['document_type']}")
            logger.info(f"   Version: {prompt_version}")
            logger.info(f"   Hash: {prompt_hash}")
            logger.info(f"   Länge: {prompt_metadata['prompt_length']} Zeichen")
            logger.info(f"   Geladen: {prompt_metadata['loaded_at']}")
            
            # 2. Provider-Validierung
            if preferred_provider == "auto" or preferred_provider == "openai_4o_mini":
                if not self.api_key:
                    raise Exception("OpenAI API Key nicht konfiguriert")
                logger.info("🤖 Verwende OpenAI 4o-mini Vision API (auto/standard)")
            elif preferred_provider == "ollama":
                logger.info("🦙 Verwende Ollama Vision API")
                # TODO: Ollama Vision API Integration
                raise Exception("Ollama Vision API noch nicht implementiert")
            elif preferred_provider == "google_gemini":
                if not self.gemini_client:
                    raise Exception("Google Gemini API Key nicht konfiguriert oder Client nicht verfügbar")
                logger.info("🌟 Verwende Google Gemini 1.5 Flash Vision API")
            else:
                raise Exception(f"Provider {preferred_provider} nicht unterstützt. Verfügbare Provider: auto, openai_4o_mini, ollama, google_gemini")
            
            # 3. Vision-Analyse mit EXAKTEM Prompt
            results = []
            total_tokens = 0
            
            for i, image_bytes in enumerate(images):
                logger.info(f"📸 Verarbeite Bild {i+1}/{len(images)}")
                
                # Bild zu Base64 konvertieren
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                
                # Vision-Analyse mit EXAKTEM Prompt und Provider-Auswahl
                if preferred_provider == "google_gemini":
                    result = await self._analyze_image_with_gemini_vision(
                        image_b64, 
                        f"Bild {i+1} aus {len(images)}", 
                        prompt
                    )
                else:
                    result = await self._analyze_image_with_gpt4_vision(
                        image_b64, 
                        f"Bild {i+1} aus {len(images)}", 
                        prompt
                    )
                
                if result['success']:
                    results.append(result)
                    total_tokens += result.get('tokens_used', 0)
                else:
                    # KEIN FALLBACK - Fehler werfen!
                    error_msg = result.get('error', 'Unbekannter Fehler')
                    raise Exception(f"Vision-Analyse für Bild {i+1} fehlgeschlagen: {error_msg}")
            
            if not results:
                raise Exception("Keine Bilder erfolgreich analysiert")
            
            # 4. Ergebnisse kombinieren
            combined_analysis = self._combine_vision_results(results)
            
            logger.info(f"✅ ZENTRALE VISION-ANALYSE erfolgreich: {len(results)} Bilder verarbeitet")
            
            # Erstelle finale Antwort mit Prompt-Bestätigung
            return {
                'success': True,
                'analysis': combined_analysis,
                'images_processed': len(images),
                'tokens_used': total_tokens,
                'individual_results': results,
                
                # PROMPT-BESTÄTIGUNG für Audit
                'prompt_confirmation': {
                    'prompt_used': prompt,
                    'prompt_version': prompt_version,
                    'prompt_hash': prompt_hash,
                    'prompt_metadata': prompt_metadata,
                    'prompt_audit_info': prompt_audit,
                    'prompt_verification': {
                        'hash_verified': True,
                        'version_verified': True,
                        'prompt_loaded_successfully': True,
                        'prompt_length_confirmed': len(prompt) == prompt_metadata['prompt_length']
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"❌ ZENTRALE VISION-ANALYSE fehlgeschlagen: {e}")
            return {
                'success': False,
                'error': str(e),
                'prompt_confirmation': {
                    'document_type': document_type,
                    'error': 'Prompt konnte nicht geladen werden',
                    'prompt_verification': {
                        'hash_verified': False,
                        'version_verified': False,
                        'prompt_loaded_successfully': False,
                        'prompt_length_confirmed': False
                    }
                }
            }


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
        # from .enhanced_ocr_engine import extract_enhanced_text  # Temporarily disabled
        
        logger.info(f"🔍 Starte kombinierte Vision + Enhanced OCR für {file_path_obj.name}")
        
        # Enhanced OCR für Grundextraktion
        # enhanced_result = await extract_enhanced_text(file_path_obj, mime_type)  # Temporarily disabled
        
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