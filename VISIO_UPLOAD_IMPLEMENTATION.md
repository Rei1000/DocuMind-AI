# Visio-Upload-Implementierung für KI-QMS

## Übersicht

Die Visio-Upload-Funktionalität erweitert das KI-QMS um die Möglichkeit, bildbasierte Dokumente (Flussdiagramme, SOPs mit Grafiken, technische Zeichnungen) strukturiert zu verarbeiten und zu validieren.

## Architektur

### Backend-Komponenten

1. **Datenbank-Erweiterungen** (`models.py`)
   - `upload_method`: Art des Uploads (ocr/visio)
   - `validation_status`: PENDING/VERIFIED/REVIEW_REQUIRED
   - `structured_analysis`: JSON-strukturierte Analyse
   - `processing_state`: State Machine für Verarbeitung
   - `vision_results`: Ergebnisse der Vision-API
   - `used_prompts`: Nachvollziehbarkeit der Prompts
   - `qm_release_at/by`: QM-Freigabe-Tracking

2. **Visio Processing Engine** (`visio_processing.py`)
   - Schrittweise Verarbeitung mit State Machine
   - PNG-Generierung (300 DPI)
   - Vision API Integration
   - Validierung mit 95% Schwellwert
   - Asynchrone RAG-Indexierung nach Freigabe

3. **Visio Prompts** (`visio_prompts.py`)
   - Dokumenttyp-spezifische Prompts
   - `visio_words`: Wort-Extraktion
   - `visio_analysis`: Strukturierte JSON-Analyse

4. **API-Endpunkte** (`main.py`)
   - `GET /api/documents/{id}/visio-status`: Verarbeitungsstatus
   - `GET /api/documents/{id}/visio-preview`: PNG-Vorschau
   - `GET /api/documents/{id}/visio-prompts`: Verwendete Prompts
   - `GET /api/documents/{id}/visio-analysis`: Strukturierte Analyse
   - `POST /api/documents/{id}/visio-qm-release`: QM-Freigabe
   - `POST /api/documents/{id}/visio-restart`: Neustart bei Fehlern

### Frontend-Komponenten

1. **Upload-Formular** (`streamlit_app.py`)
   - Radio-Button für Upload-Methode (OCR/Visio)
   - Automatische Weiterleitung zur Visio-Verarbeitung

2. **Visio-Verarbeitungsseite**
   - Schrittweise Vorschau-Module
   - PNG-Vorschau der ersten Seite
   - Prompt-Anzeige
   - JSON-Analyse-Viewer
   - Validierungs-Ergebnisse
   - QM-Freigabe-Interface

## Verarbeitungsablauf

### 1. Upload (State: UPLOADED)
- Dokument wird mit `upload_method="visio"` hochgeladen
- Asynchrone Verarbeitung startet automatisch

### 2. PNG-Generierung (State: PNG_GENERATED)
- Konvertierung zu 300 DPI PNG-Bildern
- Speicherung der ersten Seite als Vorschau

### 3. Wort-Extraktion (State: WORDS_EXTRACTED)
- Vision API mit `visio_words` Prompt
- Extraktion aller sichtbaren Wörter

### 4. Strukturanalyse (State: ANALYSIS_COMPLETE)
- Vision API mit `visio_analysis` Prompt
- JSON-strukturierte Dokumentanalyse

### 5. Validierung (State: VALIDATED)
- Vergleich extrahierte Wörter vs. JSON-Inhalt
- ≥95% = VERIFIED, <95% = REVIEW_REQUIRED

### 6. QM-Freigabe (State: QM_APPROVED)
- Manuelle Freigabe durch QM-Manager
- Dokumentation der Freigabe

### 7. RAG-Indexierung (State: INDEXED)
- Automatisch nach QM-Freigabe
- Verwendung der strukturierten JSON-Daten

## Installation

### 1. Datenbank-Migration
```bash
cd backend/scripts
python add_visio_fields.py
```

### 2. Backend neu starten
```bash
./restart_backend.sh
```

### 3. Frontend verwenden
- Dokument mit "Visio" Upload-Methode hochladen
- Zur "🖼️ Visio-Verarbeitung" Seite navigieren
- Verarbeitungsfortschritt überwachen
- QM-Freigabe erteilen

## Konfiguration

### Umgebungsvariablen
- `OPENAI_API_KEY`: Für Vision API (GPT-4o)

### Prompt-Anpassung
Prompts können in `visio_prompts.py` angepasst werden:
- Default-Prompts für alle Dokumenttypen
- Spezifische Prompts für SOP, WORK_INSTRUCTION, FORM

## Best Practices

1. **Dokumentqualität**
   - Hochauflösende Scans verwenden
   - Klare, lesbare Schrift
   - Kontrastreiche Darstellung

2. **Validierung**
   - Bei <95% Abdeckung manuell prüfen
   - Fehlende Wörter dokumentieren
   - Ggf. Prompts optimieren

3. **Performance**
   - Große Dokumente in Batches verarbeiten
   - Asynchrone Verarbeitung nutzen
   - PNG-Cache implementieren

## Troubleshooting

### "PNG-Generierung fehlgeschlagen"
- PyMuPDF installieren: `pip install pymupdf`
- Für Word-Dokumente: LibreOffice installieren

### "Vision API Fehler"
- OpenAI API-Key prüfen
- Rate Limits beachten
- Bildgröße <20MB

### "Validierung fehlgeschlagen"
- Prompt-Qualität prüfen
- Dokumentqualität verbessern
- Schwellwert anpassen (default: 95%)

## Erweiterungsmöglichkeiten

1. **Multi-Page-Support**
   - Alle Seiten verarbeiten
   - Seitenweise Navigation

2. **Batch-Verarbeitung**
   - Mehrere Dokumente gleichzeitig
   - Fortschrittsanzeige

3. **Export-Funktionen**
   - Validierungsberichte
   - Analyse-Exporte

4. **KI-Optimierung**
   - Fine-tuning der Prompts
   - Alternative Vision-Modelle
   - Confidence-Scores