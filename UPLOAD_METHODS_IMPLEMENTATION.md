# KI-QMS: Zwei Upload-Methoden (OCR vs. Visio)

## Übersicht

Diese Erweiterung fügt dem KI-QMS System zwei verschiedene Upload-Methoden für Dokumente hinzu:

1. **OCR-Methode**: Für textbasierte Dokumente (Normen, Richtlinien)
2. **Visio-Methode**: Für grafisch strukturierte Dokumente (Flussdiagramme, SOPs)

## Implementierte Änderungen

### 1. Datenbank-Erweiterungen

Neue Felder in der `documents` Tabelle:

- `upload_method` (VARCHAR(10)): Speichert die gewählte Methode ('ocr' oder 'visio')
- `validation_status` (VARCHAR(50)): Validierungsstatus für Visio-Methode
- `structured_analysis` (TEXT): JSON-strukturierte Analyse der Visio-Methode
- `prompt_used` (TEXT): Verwendete Prompts bei Visio-Verarbeitung
- `ocr_text_preview` (TEXT): OCR-Text-Vorschau für Benutzer-Review

**Migration ausführen:**
```bash
cd backend
python scripts/add_upload_method_fields.py
```

### 2. Backend-Erweiterungen

#### Neue Dateien:
- `backend/app/visio_prompts.py`: Zentrale Prompt-Verwaltung für verschiedene Dokumenttypen

#### Geänderte Dateien:
- `backend/app/models.py`: Document-Model um neue Felder erweitert
- `backend/app/main.py`: 
  - Upload-Endpoint erweitert um `upload_method` Parameter
  - Neuer Vorschau-Endpoint `/api/documents/preview`

### 3. Frontend-Erweiterungen

- **Upload-Formular**: Dropdown zur Auswahl der Upload-Methode
- **Zweistufiger Prozess**: 
  1. Vorschau generieren
  2. Nach Freigabe final speichern
- **Vorschau-Ansichten**:
  - OCR: Text-Vorschau mit erkannten Kapiteln
  - Visio: Bild-Vorschau, Wortliste, strukturierte Analyse, Validierung

## Verarbeitungsablauf

### OCR-Methode

1. **Text-Extraktion**: Verwendung von `text_extraction.extract_text_from_file()`
2. **Fallback**: Bei wenig Text wird Vision OCR als Fallback aktiviert
3. **Metadaten**: Enhanced Metadata Extractor für Keywords, Compliance etc.
4. **Vorschau**: Extrahierter Text mit erkannten Kapiteln
5. **Freigabe**: Nach QM-Freigabe → RAG-Indexierung

### Visio-Methode

1. **Prompt-Auswahl**: Dokumenttyp-spezifische Prompts aus `visio_prompts.py`
2. **Bild-Konvertierung**: Dokument → PNG-Bilder (300 DPI)
3. **Wortliste**: Prompt 1 extrahiert alle sichtbaren Wörter
4. **Strukturanalyse**: Prompt 2 erstellt JSON-strukturierte Analyse
5. **Validierung**: Vergleich Wortliste ↔ JSON-Inhalt
   - ≥ 95% Deckung → `VERIFIED`
   - < 95% Deckung → `REVIEW_REQUIRED`
6. **Freigabe**: Nach QM-Freigabe → Indexierung

## API-Endpoints

### POST `/api/documents/preview`
Generiert eine Vorschau ohne finale Speicherung.

**Request:**
```
- upload_method: "ocr" oder "visio"
- document_type: Dokumenttyp
- file: Upload-Datei
```

**Response (OCR):**
```json
{
  "upload_method": "ocr",
  "success": true,
  "extracted_text": "...",
  "metadata": {
    "text_length": 5000,
    "estimated_pages": 2,
    "detected_chapters": ["1. Einleitung", "2. Hauptteil"]
  }
}
```

**Response (Visio):**
```json
{
  "upload_method": "visio",
  "success": true,
  "preview_image": "base64...",
  "word_list": ["word1", "word2"],
  "structured_analysis": {...},
  "validation": {
    "status": "VERIFIED",
    "coverage": 96.5,
    "missing_words": []
  }
}
```

### POST `/api/documents/with-file`
Finale Speicherung mit gewählter Upload-Methode.

**Zusätzlicher Parameter:**
- `upload_method`: "ocr" oder "visio" (Standard: "ocr")

## Verwendung im Frontend

1. **Upload-Seite** aufrufen
2. **Datei** auswählen
3. **Upload-Methode** wählen:
   - OCR für Textdokumente
   - Visio für grafische Dokumente
4. **Pflichtfelder** ausfüllen (Titel, Dokumenttyp)
5. **"Vorschau generieren"** klicken
6. **Vorschau prüfen**:
   - Bei OCR: Text-Vorschau kontrollieren
   - Bei Visio: Validierungsstatus prüfen
7. **"Freigeben & Speichern"** für finale Speicherung

## Technische Details

### Visio-Prompts

Die Prompts sind dokumenttyp-spezifisch in `visio_prompts.py` definiert:

- **SOP**: Fokus auf Prozessschritte und Flussdiagramme
- **WORK_INSTRUCTION**: Arbeitsschritte und Sicherheitshinweise
- **PROCEDURE**: Verfahrensschritte und Verantwortlichkeiten
- **FORM**: Formularfelder und Ausfüllhinweise
- **OTHER**: Generische Analyse

### Validierungslogik

Die Visio-Validierung vergleicht:
1. Alle Wörter aus der Wortliste (Prompt 1)
2. Alle Wörter aus der JSON-Analyse (Prompt 2)

Fehlende Wörter werden dokumentiert und dem Benutzer angezeigt.

## Vorteile

- **Flexibilität**: Optimale Verarbeitung je nach Dokumenttyp
- **Transparenz**: Vorschau vor finaler Speicherung
- **Qualitätssicherung**: Validierung bei Visio-Methode
- **Nachvollziehbarkeit**: Speicherung von Prompts und Validierungsstatus

## Wichtige Hinweise

- Die Upload-Methode kann nach der Speicherung nicht mehr geändert werden
- Bei der Visio-Methode wird empfohlen, hochwertige PDFs oder Word-Dokumente zu verwenden
- Die OCR-Methode ist schneller, aber weniger geeignet für grafische Inhalte
- Beide Methoden unterstützen die gleiche RAG-Indexierung nach Freigabe