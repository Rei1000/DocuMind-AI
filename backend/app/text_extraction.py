"""
Text-Extraktion für KI-QMS Dokumentenmanagement

Dieses Modul extrahiert Text aus verschiedenen Dateiformaten für
RAG-Indexierung und KI-Verarbeitung.

Unterstützte Formate:
- PDF: PyPDF2
- Word: python-docx (DOCX)
- Excel: openpyxl (XLSX)
- Text: TXT, MD (Plain Text)

Autoren: KI-QMS Entwicklungsteam
Version: 1.0.0
"""

from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def extract_text_from_file(file_path: Path, mime_type: str) -> str:
    """
    Extrahiert Text aus verschiedenen Dateiformaten.
    
    Args:
        file_path: Pfad zur Datei
        mime_type: MIME-Type der Datei
        
    Returns:
        str: Extrahierter Text oder Fehlermeldung
    """
    try:
        if mime_type in ["text/plain", "text/markdown"]:
            return _extract_text_file(file_path)
        
        elif mime_type == "application/pdf":
            return _extract_pdf_text(file_path)
        
        elif mime_type in [
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]:
            return _extract_word_text(file_path)
        
        elif mime_type in [
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ]:
            return _extract_excel_text(file_path)
        
        else:
            return f"[Text-Extraktion für {mime_type} noch nicht implementiert]"
        
    except Exception as e:
        logger.error(f"Fehler bei Text-Extraktion für {file_path}: {str(e)}")
        return f"[Fehler bei Text-Extraktion: {str(e)}]"

def _extract_text_file(file_path: Path) -> str:
    """Extrahiert Text aus TXT/MD Dateien."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback für andere Encodings
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()

def _extract_pdf_text(file_path: Path) -> str:
    """Extrahiert Text aus PDF-Dateien mit PyPDF2."""
    try:
        import PyPDF2
        
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text_parts = []
            
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_parts.append(f"=== Seite {page_num} ===")
                        text_parts.append(page_text)
                except Exception as page_error:
                    text_parts.append(f"[Fehler auf Seite {page_num}: {str(page_error)}]")
            
            return "\n".join(text_parts) if text_parts else "[Kein Text extrahiert]"
            
    except ImportError:
        return "[PyPDF2 nicht installiert]"
    except Exception as e:
        return f"[PDF-Extraktion fehlgeschlagen: {str(e)}]"

def _extract_word_text(file_path: Path) -> str:
    """Extrahiert Text aus Word-Dokumenten (.docx)."""
    try:
        from docx import Document
        
        doc = Document(file_path)
        text_parts = []
        
        # Absätze extrahieren
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        # Tabellen extrahieren
        for table_num, table in enumerate(doc.tables, 1):
            text_parts.append(f"\n=== Tabelle {table_num} ===")
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells)
                if row_text.strip():
                    text_parts.append(row_text)
        
        return "\n".join(text_parts) if text_parts else "[Kein Text gefunden]"
        
    except ImportError:
        return "[python-docx nicht installiert]"
    except Exception as e:
        return f"[Word-Extraktion fehlgeschlagen: {str(e)}]"

def _extract_excel_text(file_path: Path) -> str:
    """Extrahiert Text aus Excel-Dateien (.xlsx)."""
    try:
        import openpyxl
        
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        text_parts = []
        
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            text_parts.append(f"\n=== {sheet_name} ===")
            
            # Nur nicht-leere Zeilen verarbeiten
            for row in sheet.iter_rows(values_only=True):
                row_values = [str(cell) if cell is not None else "" for cell in row]
                row_text = " | ".join(row_values).strip()
                
                if row_text and row_text != " | " * (len(row_values) - 1):
                    text_parts.append(row_text)
        
        return "\n".join(text_parts) if text_parts else "[Kein Inhalt gefunden]"
        
    except ImportError:
        return "[openpyxl nicht installiert]"
    except Exception as e:
        return f"[Excel-Extraktion fehlgeschlagen: {str(e)}]"

def extract_keywords(text: str) -> list[str]:
    """
    Extrahiert QMS-relevante Keywords aus Text.
    
    Args:
        text: Eingabetext
        
    Returns:
        list[str]: Gefundene Keywords
    """
    # QMS-spezifische Keywords
    qms_keywords = [
        "ISO 13485", "ISO 9001", "ISO 14971", "IEC 62304",
        "MDR", "FDA", "CFR", "GMP", "GLP", "GCP",
        "Kalibrierung", "Validierung", "Verifikation",
        "Risiko", "CAPA", "Audit", "Korrektur",
        "Qualitätspolitik", "Qualitätsziel", "Qualitätsmanagement",
        "Dokumentenkontrolle", "Lenkung von Dokumenten",
        "Aufzeichnungen", "QMH", "Qualitätshandbuch",
        "SOP", "Arbeitsanweisung", "Verfahren",
        "Medizinprodukt", "CE-Kennzeichnung", "Konformität",
        "Überwachung", "Messung", "Prüfung",
        "Lieferant", "Beschaffung", "Einkauf",
        "Schulung", "Kompetenz", "Bewusstsein"
    ]
    
    found_keywords = []
    text_lower = text.lower()
    
    for keyword in qms_keywords:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords

def clean_extracted_text(text: str) -> str:
    """
    Bereinigt extrahierten Text für bessere Verarbeitung.
    
    Args:
        text: Eingabetext
        
    Returns:
        str: Bereinigter Text
    """
    if not text:
        return ""
    
    # Mehrfache Zeilenendings normalisieren
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Leerzeichen normalisieren
        line = ' '.join(line.split())
        
        # Sehr kurze oder nur-Leerzeichen Zeilen überspringen
        if len(line.strip()) > 2:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines) 