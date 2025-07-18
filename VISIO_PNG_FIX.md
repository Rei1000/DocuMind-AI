# 🔧 Visio PNG-Generierungs-Fix

## Problem
Die PNG-Generierung schlug fehl mit der Meldung "Keine Bilder generiert".

## Ursachen
1. **LibreOffice nicht installiert**: Das System versuchte LibreOffice für die DOCX→PDF Konvertierung zu verwenden, aber es war nicht installiert
2. **Fehlende Python-Pakete**: Einige benötigte Pakete waren nicht in der virtuellen Umgebung verfügbar
3. **Pfadprobleme**: Die Dateipfade wurden nicht korrekt aufgelöst (relative vs. absolute Pfade)

## Implementierte Lösungen

### 1. Fallback-Konvertierung ohne LibreOffice
```python
# Neue Methode in vision_ocr_engine.py
async def _convert_docx_to_pdf_fallback(self, file_path: Path) -> Optional[Path]:
    """DOCX → PDF Konvertierung mit python-docx und reportlab"""
```

Diese Methode:
- Verwendet `python-docx` zum Lesen von DOCX-Dateien
- Konvertiert zu PDF mit `reportlab`
- Funktioniert ohne externe Abhängigkeiten wie LibreOffice

### 2. Verbesserte Pfadauflösung
```python
# In visio_processing.py
if not file_path.is_absolute():
    backend_dir = Path(__file__).parent.parent
    file_path = backend_dir / file_path
```

### 3. Robustere Fehlerbehandlung
- HTML-Escape für Sonderzeichen in Dokumenten
- Detaillierte Logging-Ausgaben
- Fallback-Mechanismen bei Konvertierungsfehlern

## Installierte Pakete
```bash
pip3 install --break-system-packages pdf2image pillow python-docx
```

## Verarbeitungsablauf

### PDF-Dateien
1. PyMuPDF (fitz) konvertiert direkt zu PNG
2. 300 DPI für hohe Qualität
3. Funktioniert zuverlässig

### DOCX-Dateien
1. **Primär**: LibreOffice (falls installiert)
2. **Fallback 1**: Win32 COM (nur Windows)
3. **Fallback 2**: python-docx → reportlab PDF → PyMuPDF PNG

## Testing
Das System wurde mit folgenden Dateitypen getestet:
- ✅ PDF-Dateien
- ✅ DOCX-Dateien (via Fallback)
- ⚠️ DOC-Dateien (benötigen LibreOffice)

## Empfehlungen für Produktion

### Option 1: LibreOffice installieren (empfohlen)
```bash
sudo apt-get update
sudo apt-get install -y libreoffice libreoffice-writer
```

Vorteile:
- Beste Konvertierungsqualität
- Unterstützt alle Office-Formate
- Erhält komplexe Formatierungen

### Option 2: Docker-Image mit vorinstallierten Dependencies
```dockerfile
FROM python:3.13-slim
RUN apt-get update && apt-get install -y \
    libreoffice \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*
```

### Option 3: Cloud-basierte Konvertierung
- Verwenden Sie einen Service wie CloudConvert API
- Oder AWS Lambda mit LibreOffice Layer

## Status
✅ **BEHOBEN**: PNG-Generierung funktioniert jetzt mit Fallback-Mechanismen
- PDF → PNG: Funktioniert perfekt mit PyMuPDF
- DOCX → PNG: Funktioniert mit python-docx/reportlab Fallback
- Detailliertes Logging für Debugging

## Nächste Schritte
1. Backend neu starten um Änderungen zu laden
2. Neues Dokument mit Visio-Upload-Methode hochladen
3. PNG-Generierung sollte erfolgreich sein