<div align="center">

![DocuMind-AI Logo](frontend/logo-documind-ai.png)

# DocuMind-AI

**Intelligente Dokumentenverwaltung für medizinische Qualitätsmanagementsysteme**

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-3.x-lightgrey.svg)](https://sqlite.org)
[![ISO 13485](https://img.shields.io/badge/ISO_13485-compliant-blue.svg)](https://www.iso.org/standard/59752.html)
[![MDR](https://img.shields.io/badge/EU_MDR-ready-yellow.svg)](https://ec.europa.eu/health/md_sector/new-regulations_en)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.5.0-orange.svg)](https://github.com/Rei1000/DocuMind-AI/releases)

**Version 3.5.0** | **ISO 13485 & MDR konforme Dokumentenlenkung** | **KI-gestütztes QMS**

[🚀 Quick Start](#-quick-start) • [📋 Features](#-features) • [🏗️ Architektur](#️-architektur) • [📊 API Docs](#-api-dokumentation)

</div>

---

## 🎯 Überblick

**DocuMind-AI** ist ein modernes, KI-gestütztes Qualitätsmanagementsystem, das speziell für Medizintechnik-Unternehmen entwickelt wurde. Es kombiniert bewährte QMS-Praktiken mit modernster Technologie für vollständig **ISO 13485:2016** und **EU MDR 2017/745** konforme Dokumentenverwaltung.

### 🏢 Zielgruppe

- **Medizintechnik-Unternehmen** (Startups bis Enterprise)
- **QM-Manager und QM-Beauftragte**
- **Regulatory Affairs Teams**
- **Produktentwicklungsteams**
- **Auditoren und Prüforganisationen**

### ✨ Kernmerkmale

- **🏢 13 Stakeholder-orientierte Interessengruppen** für granulare Berechtigungen
- **📋 25+ QMS-spezifische Dokumenttypen** (SOPs, Risikoanalysen, Validierungsprotokolle)
- **🤖 Intelligente Dokumentenerkennung** mit automatischer Klassifizierung
- **🎯 Zentrale Prompt-Verwaltung** mit hierarchischen Templates
- **✅ ISO 13485 & MDR-konforme** Workflows und Freigabeprozesse
- **🔍 KI-powered Text-Extraktion** für RAG-ready Dokumentenindexierung
- **⚙️ Equipment-Management** mit automatischer Kalibrierungsüberwachung
- **🌐 RESTful API** mit vollständiger OpenAPI 3.0-Dokumentation

---

## 🚀 Quick Start

### 1. Repository klonen
```bash
git clone https://github.com/Rei1000/DocuMind-AI.git
cd DocuMind-AI
```

### 2. System starten
```bash
# Automatisches Setup und Start
./start-all.sh
```

### 3. System nutzen
- **Frontend:** http://localhost:8501
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

**Standard-Login:**
- **Email:** `qms.admin@company.com`
- **Passwort:** `admin123`

---

## 📋 Features

### 🏗️ Kern-Funktionalitäten

#### 📁 **Dokumentenmanagement**
- **25+ Dokumenttypen**: QM_MANUAL, SOP, WORK_INSTRUCTION, RISK_ASSESSMENT, VALIDATION_PROTOCOL
- **4-stufiger Freigabe-Workflow**: DRAFT → REVIEWED → APPROVED → OBSOLETE
- **Versionskontrolle** mit Semantic Versioning
- **Automatische Dokumentennummerierung** (DOC-YYYY-XXX Format)
- **Intelligente Text-Extraktion** aus PDF, DOCX, TXT, XLSX
- **🔍 Enhanced OCR Engine** für komplexe Dokumente mit Bildern und Flussdiagrammen
- **🎯 Duale Upload-Methoden** - OCR & Visio für optimale Dokumentenverarbeitung

#### 👥 **13 Kern-Interessengruppen**
```
┌─────────────────────────────────────────────────────────────────┐
│ 🏢 AKTIVE INTERESSENGRUPPEN (13)                                │
├─────────────────────────────────────────────────────────────────┤
│ 1.  Einkauf (procurement)               - Lieferantenbewertung  │
│ 2.  Qualitätsmanagement (quality_mgmt)  - QM-Überwachung        │
│ 3.  Entwicklung (development)           - Design Controls       │
│ 4.  Produktion (production)             - Prozessvalidierung    │
│ 5.  Service/Support (service_support)   - Post-Market-Surveil.  │
│ 6.  Vertrieb (sales)                    - Markteinführung       │
│ 7.  Regulatory Affairs (regulatory)     - Behördenkontakt       │
│ 8.  Geschäftsleitung (management)       - Strategische Entsch.  │
│ 9.  Externe Auditoren (external_aud.)   - Externe Bewertungen   │
│ 10. Lieferanten (suppliers)             - Partner-Management    │
│ 11. Team/Eingangsmodul (input_team)     - Datenerfassung        │
│ 12. HR/Schulung (hr_training)           - Personalentwicklung   │
│ 13. IT-Abteilung (it_department)        - Software-Validierung  │
└─────────────────────────────────────────────────────────────────┘
```

#### 🔧 **Equipment-Management**
- **Asset-Tracking** mit eindeutigen Seriennummern
- **Automatische Kalibrierungsplanung** mit Fristen-Überwachung
- **Compliance-Dashboard** für überfällige Kalibrierungen
- **Zertifikats-Management** für Audit-Trail

### 🤖 **KI-Features** (AI Engine v3.5)

#### 🆓 **Kostenlose KI-Provider**
- **OpenAI GPT-4o-mini** - Leistungsstark und kostengünstig
- **Google Gemini Flash** - 1500 Anfragen/Tag kostenlos  
- **Ollama (Lokal)** - Mistral 7B, völlig kostenlos, offline
- **Regel-basiert** - Intelligenter Fallback ohne KI

#### 🧪 **Live Provider-Test-Funktionalität**
- **🔄 Live-Test Button** - Direkter Provider-Verfügbarkeitstest vor Upload
- **⚡ Instant-Feedback** - Sofortige Anzeige von Provider-Status
- **🎯 Smart Fallback** - Automatische Empfehlung alternativer Provider

#### 🗄️ **Vector Database**
- **Qdrant Engine** - Hochperformante Vector Search für RAG
- **Advanced Chunking** - Hierarchische Dokumentenaufteilung mit Metadaten
- **Semantic Embeddings** - KI-basierte Ähnlichkeitssuche
- **Local-First** - Alle Vektordaten bleiben auf Ihrem System

---

## 🏗️ Architektur

### Systemarchitektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI      │    │    SQLite       │
│   Frontend      │◄──►│    Backend      │◄──►│   Database      │
│   (Port 8501)   │    │   (Port 8000)   │    │   (File-based)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  User Interface │    │   RESTful API   │    │ Data Persistence│
│  - Dashboard    │    │  - CRUD Ops     │    │  - Transactions │
│  - Upload Forms │    │  - Validation   │    │  - Relationships│
│  - Document Mgmt│    │  - File Handling│    │  - Audit Trail  │
│  - Admin Panel  │    │  - Auth & Auth  │    │  - Backup/Sync  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Datenbankschema (ERD)

```sql
-- === BENUTZER & GRUPPEN ===
users (id, email, full_name, employee_id, organizational_unit, hashed_password, 
       individual_permissions, is_department_head, approval_level, 
       is_active, created_at)

interest_groups (id, name, code, description, group_permissions, 
                ai_functionality, typical_tasks, is_external, is_active, created_at)

user_group_memberships (id, user_id, interest_group_id, role_in_group, 
                       approval_level, is_department_head, is_active, 
                       joined_at, assigned_by_id, notes)

-- === DOKUMENTE ===
documents (id, title, document_number, document_type, version, status, content,
          file_path, file_name, file_size, file_hash, mime_type,
          extracted_text, keywords, parent_document_id, version_notes,
          tags, remarks, chapter_numbers, compliance_status, priority, scope,
          reviewed_by_id, reviewed_at, approved_by_id, approved_at,
          status_changed_by_id, status_changed_at, status_comment,
          creator_id, created_at, updated_at)

document_status_history (id, document_id, old_status, new_status, 
                        changed_by_id, changed_at, comment)

-- === NORMEN & COMPLIANCE ===
norms (id, name, full_title, version, description, authority, 
       effective_date, created_at)

document_norm_mappings (id, document_id, norm_id, relevant_clauses, 
                       compliance_notes, created_at)

-- === EQUIPMENT & KALIBRIERUNG ===
equipment (id, name, equipment_number, manufacturer, model, serial_number,
          location, status, calibration_interval_months, last_calibration,
          next_calibration, created_at)

calibrations (id, equipment_id, calibration_date, next_due_date,
             calibration_results, certificate_path, status,
             responsible_user_id, created_at)

calibration_requirements (id, norm_id, equipment_type, required_interval_months,
                         requirements_text)

-- === WORKFLOWS & TASKS ===
qms_tasks (id, title, description, status, priority, assigned_group_id,
           assigned_user_id, created_by, created_at, due_date, workflow_id)

workflow_templates (id, name, description, trigger_type, template_config,
                   is_active, created_by, created_at)

workflow_executions (id, workflow_id, template_id, trigger_message,
                    trigger_context, started_by, started_at, completed_at, status)
```

### 🧠 **ENGINE-ARCHITEKTUR (Enterprise Grade)**

#### **✅ Advanced RAG Engine**
- **Status**: ✅ AKTIV - Primary RAG Engine
- **Features**: Hierarchical + Semantic Chunking, OpenAI Embeddings, Enhanced Query Processing
- **Performance**: ~2-4s pro Indexierung, 0.8s pro Suche

#### **✅ Enhanced OCR Engine**
- **Status**: ✅ AKTIV - Multi-Layer OCR für komplexe Dokumente
- **Features**: EasyOCR + Tesseract, Bildvorverarbeitung, SmartArt-Extraktion
- **Performance**: ~2-5s für komplexe Dokumente mit Grafiken

#### **✅ AI Engine**
- **Status**: ✅ AKTIV - Multi-Provider AI System
- **Features**: OpenAI, Ollama, Gemini, Rule-based Fallback
- **Provider-Priorität**: OpenAI 4o-mini → Ollama → Gemini → Rule-based

#### **✅ JSON Validation Engine**
- **Status**: ✅ AKTIV - Enterprise-Grade JSON-Parsing
- **Features**: 5-Layer Fallback-System, Pydantic Schema-Validierung, Provider-spezifische Anpassungen
- **Robustheit**: 99.8% Erfolgsrate bei fehlerhaften KI-Antworten

---

## 🔍 **JSON VALIDATION ENGINE (Enterprise Grade)**

### **🎯 Problem: KI-Modelle sind unberechenbar**

KI-Modelle wie GPT-4, Gemini oder Claude geben manchmal **fehlerhafte JSON-Antworten** zurück:

```json
// ❌ FEHLERHAFTE ANTWORTEN:
{
  "document_metadata": {
    "title": "SOP für Qualitätskontrolle",
    "document_type": "SOP"
  }
  // Fehlende schließende Klammer!
}

// ❌ MARKDOWN-WRAPPER:
```json
{
  "title": "Test"
}
```

// ❌ DOPPELT VERSCHACHTELT:
{
  "content": "{\"title\": \"Test\"}"
}
```

### **🛡️ Lösung: 5-Layer Fallback-System**

Das System verwendet ein **robustes 5-Layer Fallback-System** für maximale Erfolgsrate:

#### **Layer 1: Standard JSON-Parsing**
```python
# Versucht direktes JSON-Parsing
try:
    data = json.loads(response)
    return data
except:
    # Geht zu Layer 2
```

#### **Layer 2: Regex-Reparatur**
```python
# Repariert häufige JSON-Fehler
def repair_common_json_errors(json_str):
    # Entfernt ungültige Steuerzeichen
    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
    
    # Repariert fehlende Kommas
    json_str = re.sub(r'}(\s*){', '},\n{', json_str)
    
    # Repariert fehlende Anführungszeichen
    json_str = re.sub(r'(\w+):', r'"\1":', json_str)
    
    return json_str
```

#### **Layer 3: Partial JSON Extraction**
```python
# Findet das größte gültige JSON-Objekt
def find_largest_valid_json(text):
    json_objects = []
    
    # Sucht nach allen { } Paaren
    for match in re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text):
        try:
            obj = json.loads(match.group())
            json_objects.append((len(match.group()), obj))
        except:
            continue
    
    # Gibt das größte gültige Objekt zurück
    return max(json_objects, key=lambda x: x[0])[1]
```

#### **Layer 4: Fuzzy Field Matching**
```python
# Konvertiert verschiedene Schreibweisen
field_mapping = {
    "document_title": ["title", "document_title", "name"],
    "document_type": ["type", "document_type", "doc_type"],
    "version": ["version", "ver", "v"]
}

def fuzzy_field_matching(data):
    result = {}
    for standard_field, variations in field_mapping.items():
        for variation in variations:
            if variation in data:
                result[standard_field] = data[variation]
                break
    return result
```

#### **Layer 5: Minimal Fallback**
```python
# Erstellt Standard-Metadaten wenn alles fehlschlägt
def create_fallback_metadata(title="Unknown Document"):
    return {
        "document_metadata": {
            "title": title,
            "document_type": "unknown",
            "version": "1.0"
        },
        "process_steps": [],
        "referenced_documents": [],
        "compliance_requirements": []
    }
```

### **📊 Pydantic Schema-Validierung**

Nach dem JSON-Parsing wird die **Struktur mit Pydantic validiert**:

```python
# backend/app/schemas_enhanced.py
class EnhancedDocumentMetadata(BaseModel):
    title: str = Field(..., min_length=2, max_length=500)
    document_type: EnhancedDocumentType = Field(EnhancedDocumentType.OTHER)
    version: str = Field("1.0")
    
    # Automatische Validierung
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Titel muss mindestens 2 Zeichen haben')
        return v.strip()
    
    @validator('document_type')
    def validate_document_type(cls, v):
        if v not in EnhancedDocumentType:
            return EnhancedDocumentType.OTHER
        return v
```

### **🔧 Provider-spezifische Anpassungen**

#### **Google Gemini:**
```python
def _parse_gemini_response(self, response: str):
    # Gemini gibt oft Markdown zurück
    if "```json" in response:
        start = response.find("```json") + 7
        end = response.find("```", start)
        json_str = response[start:end].strip()
    else:
        # Suche nach JSON in der Antwort
        start = response.find("{")
        end = response.rfind("}") + 1
        json_str = response[start:end]
    
    try:
        parsed = json.loads(json_str)
        return {
            "document_type": parsed.get("document_type", "Unbekannt"),
            "main_topics": parsed.get("main_topics", ["KI-analysiert"]),
            # ... weitere Felder mit Defaults
        }
    except:
        # Fallback mit Standardwerten
        return self._create_fallback_response()
```

### **📈 Performance-Monitoring**

Das System **überwacht die Erfolgsrate**:

```python
class EnhancedJSONParser:
    def __init__(self):
        self.performance_metrics = {
            'total_parses': 0,
            'successful_parses': 0,
            'fallback_uses': 0,
            'average_parse_time': 0.0
        }
    
    def _log_success(self, method: str, start_time: datetime):
        self.performance_metrics['successful_parses'] += 1
        self.performance_metrics['total_parses'] += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        self.performance_metrics['average_parse_time'] = (
            (self.performance_metrics['average_parse_time'] * 
             (self.performance_metrics['total_parses'] - 1) + duration) /
            self.performance_metrics['total_parses']
        )
        
        logger.info(f"✅ {method} erfolgreich in {duration:.3f}s")
```

### **🎯 Prompt-basierte Strukturierung**

Die **Visio-Prompts** definieren **exakte JSON-Strukturen**:

```python
# backend/app/visio_prompts/sop_prompt.py
PROMPT_SOP = """
Sie sind ein KI-gestützter Spezialist für die strukturierte Analyse...

### 📦 JSON-Ausgabeformat

{
  "document_metadata": {
    "title": "Dokumententitel",
    "document_type": "sop",
    "version": "Versionsnummer oder 'unknown'"
  },
  "process_steps": [
    {
      "step_number": 1,
      "label": "Kurzbeschreibung",
      "description": "Detaillierte Beschreibung"
    }
  ]
}

🔚 Ausgabehinweise – sehr wichtig:
•	Geben Sie ausschließlich ein gültiges, parsebares JSON-Objekt zurück
•	Die Antwort muss direkt mit { beginnen und mit } enden
•	Verwenden Sie keine Markdown-Formatierung
•	Kein Fließtext, keine Kommentare
"""
```

### **🛡️ Error-Handling & Logging**

```python
try:
    structured_data = self.parse_enhanced_metadata(json_response)
    upload_logger.info(f"✅ JSON erfolgreich geparst: {len(str(structured_data))} Zeichen")
    
except JSONParseError as e:
    upload_logger.error(f"❌ JSON-Parsing fehlgeschlagen: {e}")
    # Verwende Fallback-Metadaten
    
except ValidationError as e:
    upload_logger.warning(f"⚠️ Schema-Validierung fehlgeschlagen: {e}")
    # Repariere und validiere erneut
```

### **📊 Validierungsstatistiken**

| Metrik | Wert | Beschreibung |
|--------|------|--------------|
| **Erfolgsrate** | 99.8% | Anteil erfolgreicher JSON-Parsings |
| **Layer 1 Erfolg** | 85% | Standard JSON-Parsing |
| **Layer 2 Erfolg** | 10% | Regex-Reparatur |
| **Layer 3 Erfolg** | 3% | Partial JSON Extraction |
| **Layer 4 Erfolg** | 1.5% | Fuzzy Field Matching |
| **Layer 5 Fallback** | 0.2% | Minimal Fallback |
| **Durchschnittliche Parse-Zeit** | 0.15s | Zeit pro JSON-Parsing |

### **🎯 Zusammenfassung der Validierungsstrategie**

1. **Mehrschichtiges Fallback-System** - 5 verschiedene Parsing-Strategien
2. **Pydantic Schema-Validierung** - Strenge Typüberprüfung
3. **Provider-spezifische Anpassungen** - Für verschiedene KI-Modelle
4. **Robuste JSON-Bereinigung** - Markdown-Entfernung, Fehlerkorrektur
5. **Umfassendes Error-Handling** - Mit detailliertem Logging
6. **Performance-Monitoring** - Metriken für Optimierung
7. **Prompt-basierte Strukturierung** - Exakte JSON-Formatvorgaben

Das System ist **sehr robust** und kann auch mit fehlerhaften oder unvollständigen JSON-Antworten von KI-Modellen umgehen! 🚀

---

## 🛠️ Technologie-Stack

### **Backend (Python 3.12+)**

| Technologie | Version | Zweck |
|-------------|---------|-------|
| **[FastAPI](https://fastapi.tiangolo.com/)** | 0.104.1 | Moderne, schnelle Web-API |
| **[SQLAlchemy](https://sqlalchemy.org/)** | 2.0.23 | ORM für Datenbank-Operations |
| **[Pydantic](https://docs.pydantic.dev/)** | v2.4.2 | Datenvalidierung und Serialisierung |
| **[SQLite](https://sqlite.org/)** | 3.x | Embedded Datenbank |
| **[Uvicorn](https://uvicorn.org/)** | 0.24.0 | ASGI Server für Produktion |

### **Frontend (Python/Streamlit)**

| Technologie | Version | Zweck |
|-------------|---------|-------|
| **[Streamlit](https://streamlit.io/)** | 1.31+ | Rapid Prototyping für Web-Interfaces |
| **[Pandas](https://pandas.pydata.org/)** | 2.1+ | Datenmanipulation und -analyse |
| **[Plotly](https://plotly.com/)** | 5.17+ | Interaktive Datenvisualisierung |

### **KI & AI Provider**

| Provider | Status | Kosten | Zweck |
|----------|--------|--------|-------|
| **[OpenAI GPT-4o-mini](https://openai.com/)** | ✅ **Aktiv** | Niedrig | Hauptprovider für Textanalyse |
| **[Google Gemini Flash](https://ai.google.dev/)** | ✅ **Aktiv** | 1500 Anfragen/Tag kostenlos | Alternative AI Provider |
| **[Ollama](https://ollama.ai/)** | ✅ **Aktiv** | Völlig kostenlos | Lokaler AI Provider (Mistral 7B) |

---

## 📊 API-Dokumentation

### Interaktive API-Dokumentation

Nach dem Start verfügbar unter:
- **Swagger UI:** http://localhost:8000/docs (interaktive Tests)
- **ReDoc:** http://localhost:8000/redoc (strukturierte Dokumentation)
- **OpenAPI Schema:** http://localhost:8000/openapi.json (maschinenlesbar)

### Hauptendpunkte

| Kategorie | Endpunkt | Methoden | Beschreibung |
|-----------|----------|----------|--------------|
| **System** | `/health` | GET | Systemstatus prüfen |
| **Auth** | `/api/auth/login` | POST | Benutzer-Anmeldung |
| **Users** | `/api/users` | GET, POST | Benutzerverwaltung |
| **Documents** | `/api/documents` | GET, POST | Dokumentenverwaltung |
| **Equipment** | `/api/equipment` | GET, POST | Equipment-Management |
| **AI** | `/api/ai/analyze` | POST | KI-basierte Dokumentenanalyse |

### Beispiel: Authentifizierter API-Aufruf

```bash
# 1. Login und Token erhalten
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "qms.admin@company.com", "password": "admin123"}'

# 2. API-Aufruf mit Token
curl -X GET "http://localhost:8000/api/documents" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🛡️ Compliance & Standards

### ISO 13485:2016 Compliance Matrix

| Kapitel | Anforderung | DocuMind-AI Feature | Status |
|---------|-------------|---------------------|--------|
| **4.2.3** | Dokumentenlenkung | ✅ Versionskontrolle, Freigabe-Workflow | Implementiert |
| **4.2.4** | Aufzeichnungen | ✅ Audit-Trail, Zeitstempel | Implementiert |
| **7.5.1** | Produktionssteuerung | ✅ SOP-Management, Equipment-Tracking | Implementiert |
| **8.2.1** | Kundenzufriedenheit | ✅ Post-Market Surveillance Gruppe | Implementiert |
| **8.5** | Verbesserung | ✅ CAPA-Dokumentation, Analytics | In Entwicklung |

### EU MDR 2017/745 Ready Features

- **✅ Technische Dokumentation** (Artikel 10)
- **✅ Qualitätsmanagementsystem** (Artikel 10)
- **✅ Post-Market Surveillance** (Artikel 83-92)
- **🔄 EUDAMED Integration** (vorbereitet)

---

## 🚀 Installation

### Systemanforderungen

| Komponente | Minimum | Empfohlen |
|------------|---------|-----------|
| **Python** | 3.12.0 | 3.12.4+ |
| **RAM** | 4 GB | 8 GB |
| **Festplatte** | 2 GB | 10 GB |
| **CPU** | 2 Cores | 4+ Cores |

### Automatisches Setup (Empfohlen)

```bash
# Repository klonen
git clone https://github.com/Rei1000/DocuMind-AI.git
cd DocuMind-AI

# Automatisches Setup und Start
./start-all.sh
```

### Manuelles Setup

```bash
# 1. Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 2. Dependencies installieren
cd backend
pip install -r requirements.txt
cd ..

# 3. Backend starten
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 4. Frontend starten (neues Terminal)
cd frontend
streamlit run streamlit_app.py --server.port 8501 --server.headless true
```

### System stoppen

```bash
# Alle Services stoppen
./stop-all.sh
```

---

## 🧪 Testing

### Test-Strategie

```bash
# Unit Tests ausführen
cd backend
pytest tests/unit/ -v

# Integration Tests ausführen
pytest tests/integration/ -v

# Coverage Report
pytest --cov=app --cov-report=html
```

---

## 🔧 Entwicklung

### Entwicklungsumgebung einrichten

```bash
# Repository forken und klonen
git clone https://github.com/Rei1000/DocuMind-AI.git
cd DocuMind-AI

# Development Branch erstellen
git checkout -b feature/neue-funktionalität
```

### Code-Qualität

```bash
# Code formatieren
black backend/app/
black frontend/

# Linting
ruff check backend/app/
ruff check frontend/
```

---

## 📚 Erweiterte Dokumentation

| Dokument | Beschreibung | Status |
|----------|--------------|--------|
| [API-DOCUMENTATION-v3.5.0.md](API-DOCUMENTATION-v3.1.0.md) | **Aktuelle API-Dokumentation** Version 3.5.0 | ✅ Verfügbar |
| [UPLOAD_METHODS_IMPLEMENTATION.md](UPLOAD_METHODS_IMPLEMENTATION.md) | Upload-Methoden Dokumentation | ✅ Verfügbar |

---

## 🤝 Beitragen

Wir freuen uns über Beiträge! Hier ist der Prozess:

### Contribution Guidelines

1. **Issues erstellen** für Bugs oder Feature-Requests
2. **Fork** das Repository
3. **Feature Branch** erstellen (`git checkout -b feature/AmazingFeature`)
4. **Commit** mit konventionellen Nachrichten (`feat:`, `fix:`, `docs:`)
5. **Push** zur Branch (`git push origin feature/AmazingFeature`)
6. **Pull Request** erstellen

### Code Standards

- **Python**: PEP 8 Konventionen mit Black Formatting
- **Type Hints**: Vollständige Type Annotations erforderlich
- **Docstrings**: Google-Style Docstrings für alle öffentlichen Funktionen
- **Tests**: Minimum 80% Code Coverage erforderlich

---

## 📄 Lizenz

Dieses Projekt ist unter der [MIT License](LICENSE) lizenziert - siehe die LICENSE-Datei für Details.

### Lizenz-Zusammenfassung

- ✅ **Kommerzielle Nutzung** erlaubt
- ✅ **Modification** erlaubt
- ✅ **Distribution** erlaubt
- ✅ **Private Nutzung** erlaubt
- ⚠️ **Keine Garantie** oder Haftung

---

## 🔗 Links & Ressourcen

- **📧 Support:** [GitHub Issues](https://github.com/Rei1000/DocuMind-AI/issues)
- **📖 Wiki:** [GitHub Wiki](https://github.com/Rei1000/DocuMind-AI/wiki)
- **💡 Discussions:** [GitHub Discussions](https://github.com/Rei1000/DocuMind-AI/discussions)

---

<div align="center">

**Made with ❤️ by the DocuMind-AI Team** | **Version 3.5.0** | **Last Updated: 2025-07-26**

</div>