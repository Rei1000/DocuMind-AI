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
│ 🏢 AKTIVE INTERESSENGRUPPEN (13)                                 │
├─────────────────────────────────────────────────────────────────┤
│ 1.  Einkauf (procurement)               - Lieferantenbewertung   │
│ 2.  Qualitätsmanagement (quality_mgmt)  - QM-Überwachung       │
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
│  User Interface │    │   RESTful API   │    │  Data Persistence│
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