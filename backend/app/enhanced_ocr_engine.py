"""
Enhanced OCR Engine für komplexe QM-Dokumente
============================================

Multi-Layer OCR Pipeline für:
- Word-Dokumente mit eingebetteten Bildern
- Flussdiagramme und SmartArt
- Technische Zeichnungen
- Formulare mit Grafiken
- Arbeitsanweisungen mit visuellen Elementen

Technologien:
- Tesseract OCR für Bildbereiche
- EasyOCR für komplexe Layouts
- python-docx für Textextraktion
- Pillow für Bildverarbeitung
- OpenCV für Bildvorverarbeitung (falls verfügbar)
"""

import logging
import asyncio
import io
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import zipfile
import xml.etree.ElementTree as ET

# Standard Libraries
from PIL import Image, ImageEnhance, ImageFilter
import fitz  # PyMuPDF

# OCR Libraries
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# OpenCV (optional für erweiterte Bildverarbeitung)
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# Document processing
from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

logger = logging.getLogger("KI-QMS.EnhancedOCR")

class EnhancedOCREngine:
    """
    Enhanced OCR Engine für komplexe QM-Dokumente
    
    Features:
    - Multi-Layer Text Extraction
    - Image-based OCR (Tesseract + EasyOCR)
    - Flussdiagramm-Erkennung
    - SmartArt Text-Extraktion
    - Bildvorverarbeitung für bessere OCR-Qualität
    """
    
    def __init__(self):
        self.tesseract_available = TESSERACT_AVAILABLE
        self.easyocr_available = EASYOCR_AVAILABLE
        self.opencv_available = OPENCV_AVAILABLE
        
        # EasyOCR Reader initialisieren (unterstützt Deutsch und Englisch)
        self.easyocr_reader = None
        if self.easyocr_available:
            try:
                self.easyocr_reader = easyocr.Reader(['de', 'en'], gpu=False)
                logger.info("✅ EasyOCR Reader initialisiert (DE, EN)")
            except Exception as e:
                logger.warning(f"⚠️ EasyOCR Initialisierung fehlgeschlagen: {e}")
                self.easyocr_available = False
        
        # Tesseract Konfiguration
        self.tesseract_config = r'--oem 3 --psm 6 -l deu+eng'
        
        logger.info(f"🔧 Enhanced OCR Engine initialisiert:")
        logger.info(f"   Tesseract: {'✅' if self.tesseract_available else '❌'}")
        logger.info(f"   EasyOCR: {'✅' if self.easyocr_available else '❌'}")
        logger.info(f"   OpenCV: {'✅' if self.opencv_available else '❌'}")

    async def extract_enhanced_text(self, file_path: Path, mime_type: str) -> Dict[str, Any]:
        """
        Hauptmethode für erweiterte Textextraktion
        
        Returns:
            Dict mit extrahiertem Text und Metadaten
        """
        try:
            logger.info(f"🔍 Enhanced OCR gestartet für: {file_path.name}")
            
            if mime_type == 'application/pdf':
                return await self._extract_from_pdf(file_path)
            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return await self._extract_from_docx(file_path)
            else:
                logger.warning(f"⚠️ Unbekannter MIME-Type: {mime_type}")
                return {
                    'text': '[Unbekanntes Dateiformat]',
                    'images_processed': 0,
                    'ocr_method': 'none',
                    'success': False
                }
                
        except Exception as e:
            logger.error(f"❌ Enhanced OCR fehlgeschlagen: {e}")
            return {
                'text': '[Enhanced OCR Fehler]',
                'images_processed': 0,
                'ocr_method': 'error',
                'success': False,
                'error': str(e)
            }

    async def _extract_from_pdf(self, file_path: Path) -> Dict[str, Any]:
        """PDF-Textextraktion mit Bildverarbeitung"""
        try:
            doc = fitz.open(file_path)
            full_text = []
            images_processed = 0
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Normaler Textinhalt
                text = page.get_text()
                if text.strip():
                    full_text.append(text)
                
                # Bilder auf der Seite verarbeiten
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        # Bild extrahieren
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            
                            # OCR auf Bild anwenden
                            ocr_text = await self._ocr_from_bytes(img_data)
                            if ocr_text.strip():
                                full_text.append(f"\n[Bild {page_num+1}.{img_index+1}]: {ocr_text}")
                                images_processed += 1
                        
                        pix = None
                    except Exception as e:
                        logger.warning(f"⚠️ Bild-OCR Fehler (Seite {page_num+1}): {e}")
            
            doc.close()
            
            result_text = '\n'.join(full_text)
            logger.info(f"✅ PDF verarbeitet: {len(result_text)} Zeichen, {images_processed} Bilder")
            
            return {
                'text': result_text,
                'images_processed': images_processed,
                'ocr_method': 'pdf_with_images',
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ PDF OCR fehlgeschlagen: {e}")
            return {
                'text': '[PDF OCR Fehler]',
                'images_processed': 0,
                'ocr_method': 'error',
                'success': False,
                'error': str(e)
            }

    async def _extract_from_docx(self, file_path: Path) -> Dict[str, Any]:
        """Word-Dokumentextraktion mit Bildverarbeitung und SmartArt"""
        try:
            # Standard Text-Extraktion
            doc = Document(file_path)
            text_parts = []
            images_processed = 0
            
            # 1. Normale Absätze und Tabellen
            for element in doc.element.body:
                if isinstance(element, CT_P):
                    paragraph = Paragraph(element, doc)
                    if paragraph.text.strip():
                        text_parts.append(paragraph.text)
                elif isinstance(element, CT_Tbl):
                    table = Table(element, doc)
                    table_text = self._extract_table_text(table)
                    if table_text.strip():
                        text_parts.append(table_text)
            
            # 2. Bilder aus Word-Dokument extrahieren
            images_text = await self._extract_images_from_docx(file_path)
            if images_text:
                text_parts.extend(images_text)
                images_processed = len(images_text)
            
            # 3. SmartArt und Shapes (experimentell)
            shapes_text = await self._extract_shapes_from_docx(file_path)
            if shapes_text:
                text_parts.extend(shapes_text)
            
            result_text = '\n'.join(text_parts)
            
            # Fallback: Wenn immer noch kein Text, versuche Document-zu-PDF Konvertierung
            if len(result_text.strip()) < 50:
                logger.info("🔄 Fallback: Konvertiere DOCX zu Bildern für OCR")
                fallback_result = await self._docx_to_image_ocr(file_path)
                if fallback_result['success']:
                    return fallback_result
            
            logger.info(f"✅ DOCX verarbeitet: {len(result_text)} Zeichen, {images_processed} Bilder")
            
            return {
                'text': result_text,
                'images_processed': images_processed,
                'ocr_method': 'docx_enhanced',
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ DOCX Enhanced OCR fehlgeschlagen: {e}")
            return {
                'text': '[DOCX Enhanced OCR Fehler]',
                'images_processed': 0,
                'ocr_method': 'error',
                'success': False,
                'error': str(e)
            }

    async def _extract_images_from_docx(self, file_path: Path) -> List[str]:
        """Extrahiert und verarbeitet Bilder aus Word-Dokumenten"""
        try:
            images_text = []
            
            # Word-Dokument ist eine ZIP-Datei
            with zipfile.ZipFile(file_path, 'r') as docx_zip:
                # Finde alle Bild-Dateien
                image_files = [f for f in docx_zip.namelist() 
                              if f.startswith('word/media/') and 
                              any(f.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp'])]
                
                logger.info(f"📸 Gefunden {len(image_files)} Bilder in DOCX")
                
                for img_file in image_files:
                    try:
                        img_data = docx_zip.read(img_file)
                        ocr_text = await self._ocr_from_bytes(img_data)
                        
                        if ocr_text.strip():
                            images_text.append(f"\n[Bild {img_file}]: {ocr_text}")
                            logger.info(f"✅ OCR Text aus {img_file}: {len(ocr_text)} Zeichen")
                    
                    except Exception as e:
                        logger.warning(f"⚠️ Bild-OCR Fehler für {img_file}: {e}")
            
            return images_text
            
        except Exception as e:
            logger.error(f"❌ Bild-Extraktion aus DOCX fehlgeschlagen: {e}")
            return []

    async def _extract_shapes_from_docx(self, file_path: Path) -> List[str]:
        """Versucht Text aus Shapes und SmartArt zu extrahieren"""
        try:
            shapes_text = []
            
            # XML-Analyse für eingebettete Texte in Shapes
            with zipfile.ZipFile(file_path, 'r') as docx_zip:
                try:
                    # Hauptdokument analysieren
                    document_xml = docx_zip.read('word/document.xml')
                    root = ET.fromstring(document_xml)
                    
                    # Suche nach Drawing-Elementen
                    for drawing in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing'):
                        # Textinhalte in Drawings finden
                        for text_elem in drawing.iter():
                            if text_elem.text and text_elem.text.strip():
                                shapes_text.append(f"[Shape]: {text_elem.text}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ XML-Shape-Analyse fehlgeschlagen: {e}")
            
            if shapes_text:
                logger.info(f"✅ {len(shapes_text)} Texte aus Shapes extrahiert")
            
            return shapes_text
            
        except Exception as e:
            logger.error(f"❌ Shape-Extraktion fehlgeschlagen: {e}")
            return []

    async def _docx_to_image_ocr(self, file_path: Path) -> Dict[str, Any]:
        """
        Fallback: Konvertiert DOCX-Seiten zu Bildern und führt OCR durch
        Nutzt python-docx2txt als Fallback wenn verfügbar
        """
        try:
            # Für jetzt ein einfacher Fallback
            logger.warning("📄 DOCX-zu-Bild OCR nicht implementiert - nutze Standard-Extraktion")
            
            return {
                'text': '[DOCX-zu-Bild OCR nicht verfügbar]',
                'images_processed': 0,
                'ocr_method': 'fallback_failed',
                'success': False
            }
            
        except Exception as e:
            logger.error(f"❌ DOCX-zu-Bild OCR fehlgeschlagen: {e}")
            return {
                'text': '[DOCX-zu-Bild OCR Fehler]',
                'images_processed': 0,
                'ocr_method': 'error',
                'success': False,
                'error': str(e)
            }

    async def _ocr_from_bytes(self, image_bytes: bytes) -> str:
        """Führt OCR auf Bilddaten durch mit mehreren Engines"""
        try:
            # Bild aus Bytes laden
            image = Image.open(io.BytesIO(image_bytes))
            
            # Bildvorverarbeitung für bessere OCR-Qualität
            processed_image = self._preprocess_image(image)
            
            ocr_results = []
            
            # 1. Tesseract OCR
            if self.tesseract_available:
                try:
                    tesseract_text = pytesseract.image_to_string(
                        processed_image, 
                        config=self.tesseract_config
                    ).strip()
                    if tesseract_text:
                        ocr_results.append(('tesseract', tesseract_text))
                except Exception as e:
                    logger.warning(f"⚠️ Tesseract OCR Fehler: {e}")
            
            # 2. EasyOCR
            if self.easyocr_available and self.easyocr_reader:
                try:
                    # Konvertiere PIL zu numpy array für EasyOCR
                    img_array = np.array(processed_image)
                    easyocr_results = self.easyocr_reader.readtext(img_array, detail=0)
                    easyocr_text = ' '.join(easyocr_results).strip()
                    if easyocr_text:
                        ocr_results.append(('easyocr', easyocr_text))
                except Exception as e:
                    logger.warning(f"⚠️ EasyOCR Fehler: {e}")
            
            # Bestes Ergebnis auswählen (längstes)
            if ocr_results:
                best_result = max(ocr_results, key=lambda x: len(x[1]))
                logger.debug(f"🔍 OCR verwendet {best_result[0]}: {len(best_result[1])} Zeichen")
                return best_result[1]
            else:
                return ""
                
        except Exception as e:
            logger.error(f"❌ Bild-OCR fehlgeschlagen: {e}")
            return ""

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Bildvorverarbeitung für bessere OCR-Qualität"""
        try:
            # Konvertiere zu Graustufen falls nicht bereits
            if image.mode != 'L':
                image = image.convert('L')
            
            # Kontrast erhöhen
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Schärfen
            image = image.filter(ImageFilter.SHARPEN)
            
            # OpenCV erweiterte Vorverarbeitung (falls verfügbar)
            if self.opencv_available:
                img_array = np.array(image)
                
                # Gaussian Blur zur Rauschreduktion
                img_array = cv2.GaussianBlur(img_array, (1, 1), 0)
                
                # Adaptive Thresholding
                img_array = cv2.adaptiveThreshold(
                    img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY, 11, 2
                )
                
                image = Image.fromarray(img_array)
            
            return image
            
        except Exception as e:
            logger.warning(f"⚠️ Bildvorverarbeitung fehlgeschlagen: {e}")
            return image  # Rückgabe des ursprünglichen Bildes

    def _extract_table_text(self, table: Table) -> str:
        """Extrahiert Text aus Word-Tabellen"""
        try:
            table_text = []
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text:
                        row_text.append(cell_text)
                if row_text:
                    table_text.append(' | '.join(row_text))
            
            return '\n'.join(table_text)
            
        except Exception as e:
            logger.warning(f"⚠️ Tabellen-Extraktion fehlgeschlagen: {e}")
            return ""

# Globale Instanz
enhanced_ocr_engine = EnhancedOCREngine()

async def extract_enhanced_text(file_path: Path, mime_type: str) -> Dict[str, Any]:
    """
    Hauptfunktion für erweiterte Textextraktion
    
    Args:
        file_path: Pfad zur Datei
        mime_type: MIME-Type der Datei
        
    Returns:
        Dict mit extrahiertem Text und Metadaten
    """
    return await enhanced_ocr_engine.extract_enhanced_text(file_path, mime_type)