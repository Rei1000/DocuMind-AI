<div align="center">

![DocuMind-AI Logo](frontend/logo-documind-ai.png)

# DocuMind-AI

**Intelligente Dokumentenverwaltung für medizinische Qualitätsmanagementsysteme**

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40.2-red.svg)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-3.x-lightgrey.svg)](https://sqlite.org)
[![ISO 13485](https://img.shields.io/badge/ISO_13485-compliant-blue.svg)](https://www.iso.org/standard/59752.html)
[![MDR](https://img.shields.io/badge/EU_MDR-ready-yellow.svg)](https://ec.europa.eu/health/md_sector/new-regulations_en)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.7.0-orange.svg)](https://github.com/Rei1000/DocuMind-AI/releases)

**Version 3.7.0** | **Multi-Visio Pipeline** | **ISO 13485 & MDR konforme Dokumentenlenkung** | **KI-gestütztes QMS**

[🚀 Quick Start](#-quick-start) • [📋 Features](#-features) • [🧠 Multi-Visio](#-multi-visio-pipeline-5-stufen-ki-analyse) • [🏗️ Architektur](#️-architektur) • [📊 API Docs](#-api-dokumentation)

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
- **🎯 Zentrale Prompt-Verwaltung** mit hierarchischen Templates (Version 3.0)
- **✅ ISO 13485 & MDR-konforme** Workflows und Freigabeprozesse
- **🔍 KI-powered Text-Extraktion** für RAG-ready Dokumentenindexierung
- **⚙️ Equipment-Management** mit automatischer Kalibrierungsüberwachung
- **👥 Erweiterte Benutzerverwaltung** mit dynamischen Abteilungszuordnungen
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
- **🎯 Triple Upload-Methoden** - OCR, Visio & Multi-Visio für optimale Dokumentenverarbeitung
- **🧠 Multi-Visio Pipeline** - 5-stufige KI-Analyse mit Verifikation und Qualitätssicherung
- **📝 Prompt Version 3.0** - Erweiterte Texterfassung für normalen Visio-Workflow

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

#### 👥 **Erweiterte Benutzerverwaltung**
- **Dynamische Abteilungszuordnungen** aus 13 offiziellen Interessensgruppen
- **Mehrfache Abteilungsmitgliedschaften** mit individuellen Approval-Levels
- **Automatische Level-Anzeige** (höchstes Level aus allen Mitgliedschaften)
- **Konsistente Datenquellen** - user_group_memberships als Single Source of Truth
- **Verbesserte UI** - Abteilungen mit Level-Anzeige in Sidebar und Profil
- **Cache-Validierung** für Profile-Seite und Benutzerverwaltung

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
equipment (id, name, serial_number, equipment_type, location, 
          manufacturer, model, purchase_date, calibration_interval,
          last_calibration_date, next_calibration_date, status, 
          responsible_person_id, created_at)

calibrations (id, equipment_id, calibration_date, calibration_type,
             performed_by, certificate_number, calibration_result,
             next_calibration_date, notes, created_at)

-- === WORKFLOWS & TASKS ===
qms_tasks (id, title, description, task_type, priority, status,
          assigned_to_id, interest_group_id, due_date, completed_at,
          created_by_id, created_at)

workflow_templates (id, name, description, steps, interest_group_id,
                   is_active, created_at)
```

### 🧠 Multi-Visio Pipeline (5-Stufen KI-Analyse)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🧠 MULTI-VISIO PIPELINE - 5-STUFEN KI-ANALYSE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 📄 DOKUMENT UPLOAD                                              │
│    ↓                                                            │
│ 🔍 STUFE 1: OCR & TEXT-EXTRAKTION                              │
│    - PyMuPDF für PDF-Verarbeitung                              │
│    - Tesseract OCR für Bild-zu-Text                            │
│    - Strukturierte Text-Ausgabe                                │
│    ↓                                                            │
│ 🎯 STUFE 2: DOKUMENT-KLASSIFIZIERUNG                           │
│    - KI-basierte Typ-Erkennung                                 │
│    - 25+ QMS-Dokumenttypen                                     │
│    - Confidence-Score für Qualität                             │
│    ↓                                                            │
│ 📋 STUFE 3: METADATA-EXTRAKTION                                │
│    - Automatische Feld-Erkennung                               │
│    - Keywords und Tags                                         │
│    - Compliance-Status                                         │
│    ↓                                                            │
│ ✅ STUFE 4: QUALITÄTS-VALIDIERUNG                              │
│    - Cross-Validation mit KI                                   │
│    - Konsistenz-Checks                                         │
│    - Fehler-Erkennung und -Korrektur                           │
│    ↓                                                            │
│ 🎯 STUFE 5: FINAL-OPTIMIERUNG                                  │
│    - Finale Qualitäts-Sicherung                                │
│    - RAG-ready Indexierung                                     │
│    - Audit-Trail für Compliance                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 🤖 AI Engine Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│ 🤖 AI ENGINE v3.5 - MULTI-PROVIDER ARCHITEKTUR                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 📊 PROVIDER-FALLBACK-KETTE:                                    │
│    OpenAI GPT-4o-mini → Gemini Flash → Ollama → Rule-based     │
│                                                                 │
│ 🔧 CORE COMPONENTS:                                             │
│    • AI Engine (Multi-Provider Management)                     │
│    • Multi-Visio Engine (5-Stufen Pipeline)                    │
│    • Word Extraction Engine (LLM + OCR)                        │
│    • Advanced RAG Engine (Qdrant + Hierarchical Chunking)      │
│    • Vision OCR Engine (Enhanced Image Processing)             │
│    • JSON Validation Engine (5-Layer Fallback)                 │
│    • Enhanced Metadata Extractor                               │
│                                                                 │
│ 📈 PERFORMANCE FEATURES:                                        │
│    • Async Processing für bessere Performance                  │
│    • Connection Pooling für API-Calls                          │
│    • Caching für wiederholte Anfragen                          │
│    • Rate Limiting für Provider-Schutz                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Multi-Visio Pipeline (5-Stufen KI-Analyse)

### 🎯 **Stufe 1: OCR & Text-Extraktion**
- **PyMuPDF Integration** für native PDF-Verarbeitung
- **Tesseract OCR** für Bild-zu-Text Konvertierung
- **Strukturierte Text-Ausgabe** mit Format-Erhaltung
- **Multi-Sprach Support** (Deutsch, Englisch, Französisch)

### 🎯 **Stufe 2: Dokument-Klassifizierung**
- **KI-basierte Typ-Erkennung** mit Confidence-Scores
- **25+ QMS-Dokumenttypen** automatisch erkannt
- **Cross-Validation** zwischen verschiedenen AI-Providern
- **Fallback-Mechanismen** für robuste Erkennung

### 🎯 **Stufe 3: Metadata-Extraktion**
- **Automatische Feld-Erkennung** (Titel, Version, Autor, etc.)
- **Keywords und Tags** für bessere Auffindbarkeit
- **Compliance-Status** basierend auf Inhalt
- **Strukturierte Metadaten** für RAG-Indexierung

### 🎯 **Stufe 4: Qualitäts-Validierung**
- **Cross-Validation** zwischen verschiedenen AI-Providern
- **Konsistenz-Checks** für extrahierte Daten
- **Fehler-Erkennung und -Korrektur** automatisch
- **Quality-Scores** für jede Verarbeitungsstufe

### 🎯 **Stufe 5: Final-Optimierung**
- **Finale Qualitäts-Sicherung** vor Speicherung
- **RAG-ready Indexierung** für Vector Database
- **Audit-Trail** für Compliance-Anforderungen
- **Optimierte Metadaten** für beste Performance

---

## 📊 API Dokumentation

### 🔗 **RESTful API Endpoints**

#### 👥 **User Management**
```http
GET    /api/users                    # Benutzer-Liste
POST   /api/users                    # Neuen Benutzer erstellen
GET    /api/users/{user_id}          # Benutzer-Details
PUT    /api/users/{user_id}          # Benutzer aktualisieren
DELETE /api/users/{user_id}          # Benutzer löschen
POST   /api/users/login              # Benutzer-Login
POST   /api/users/logout             # Benutzer-Logout
```

#### 📄 **Document Management**
```http
GET    /api/documents                # Dokumente-Liste
POST   /api/documents                # Dokument hochladen
GET    /api/documents/{doc_id}       # Dokument-Details
PUT    /api/documents/{doc_id}       # Dokument aktualisieren
DELETE /api/documents/{doc_id}       # Dokument löschen
POST   /api/documents/upload         # Multi-Visio Upload
POST   /api/documents/ocr            # OCR-Verarbeitung
```

#### 🤖 **AI Engine**
```http
POST   /api/ai/process-document      # Dokument mit KI verarbeiten
POST   /api/ai/extract-text          # Text-Extraktion
POST   /api/ai/classify-document     # Dokument-Klassifizierung
POST   /api/ai/extract-metadata      # Metadata-Extraktion
GET    /api/ai/providers             # Verfügbare AI-Provider
POST   /api/ai/test-provider         # Provider-Test
```

#### 🔧 **Equipment Management**
```http
GET    /api/equipment                # Equipment-Liste
POST   /api/equipment                # Equipment erstellen
GET    /api/equipment/{equip_id}     # Equipment-Details
PUT    /api/equipment/{equip_id}     # Equipment aktualisieren
GET    /api/calibrations             # Kalibrierungen-Liste
POST   /api/calibrations             # Kalibrierung erstellen
```

### 📖 **OpenAPI Dokumentation**
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## 🛠️ Installation & Setup

### 📋 **Systemanforderungen**
- **Python:** 3.12+
- **RAM:** 4GB+ (8GB empfohlen)
- **Speicher:** 2GB freier Speicherplatz
- **OS:** Windows 10+, macOS 10.15+, Ubuntu 20.04+

### 🔧 **Installation**

#### **Option 1: Automatisches Setup (Empfohlen)**
```bash
# Repository klonen
git clone https://github.com/Rei1000/DocuMind-AI.git
cd DocuMind-AI

# Automatisches Setup und Start
./start-all.sh
```

#### **Option 2: Manuelles Setup**
```bash
# 1. Python Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/macOS
# oder: venv\Scripts\activate  # Windows

# 2. Dependencies installieren
pip install -r backend/requirements.txt

# 3. Datenbank initialisieren
cd backend
python -c "from app.database import create_tables; create_tables()"

# 4. Backend starten
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Frontend starten (neues Terminal)
cd frontend
streamlit run streamlit_app.py --server.port 8501
```

### ⚙️ **Konfiguration**

#### **Environment Variables**
```bash
# .env Datei erstellen
cp env-template.txt .env

# Wichtige Einstellungen:
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./qms_mvp.db
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
UPLOADS_DIR=backend/uploads
LOGS_DIR=logs
```

#### **AI Provider Setup**
```bash
# OpenAI (optional)
export OPENAI_API_KEY="your-openai-api-key"

# Google Gemini (optional)
export GEMINI_API_KEY="your-gemini-api-key"

# Ollama (lokal, kostenlos)
# Installation: https://ollama.ai
ollama pull mistral:7b
```

---

## 🧪 Testing

### 🔍 **Test-Suite ausführen**
```bash
# Alle Tests ausführen
python -m pytest tests/ -v

# Spezifische Test-Kategorien
python -m pytest tests/test_api/ -v
python -m pytest tests/test_ai/ -v
python -m pytest tests/test_database/ -v

# Coverage Report
python -m pytest --cov=app tests/ --cov-report=html
```

### 📊 **Test-Coverage**
- **API Endpoints:** 95%+
- **AI Engine:** 90%+
- **Database Operations:** 98%+
- **Authentication:** 100%+

---

## 🚀 Deployment

### 🐳 **Docker Deployment**
```bash
# Docker Compose Setup
docker-compose up -d

# Services:
# - Frontend: http://localhost:8501
# - Backend: http://localhost:8000
# - Database: SQLite (persistent)
```

### ☁️ **Cloud Deployment**
- **AWS:** EC2 + RDS + S3
- **Azure:** App Service + SQL Database + Blob Storage
- **Google Cloud:** Compute Engine + Cloud SQL + Cloud Storage
- **Heroku:** Container Deployment

---

## 📈 Performance & Monitoring

### ⚡ **Performance-Metriken**
- **API Response Time:** < 200ms (95th percentile)
- **Document Processing:** < 30s für Standard-Dokumente
- **Concurrent Users:** 50+ gleichzeitige Benutzer
- **Database Queries:** < 100ms durchschnittlich

### 📊 **Monitoring**
- **Health Checks:** /api/health
- **Metrics:** /api/metrics
- **Logs:** Strukturierte JSON-Logs
- **Alerts:** Email-Benachrichtigungen bei Fehlern

---

## 🔒 Security

### 🛡️ **Security Features**
- **JWT Authentication** mit Token-Expiration
- **Role-Based Access Control (RBAC)**
- **Password Hashing** mit bcrypt
- **Input Validation** und Sanitization
- **SQL Injection Protection**
- **XSS Protection**
- **CSRF Protection**

### 🔐 **Compliance**
- **ISO 13485:2016** konform
- **EU MDR 2017/745** ready
- **GDPR** compliant
- **Audit Trail** für alle Änderungen
- **Data Encryption** in Transit und at Rest

---

## 🤝 Contributing

### 📝 **Entwicklungs-Workflow**
1. **Fork** das Repository
2. **Feature Branch** erstellen (`git checkout -b feature/amazing-feature`)
3. **Changes** committen (`git commit -m 'Add amazing feature'`)
4. **Branch** pushen (`git push origin feature/amazing-feature`)
5. **Pull Request** erstellen

### 🧪 **Code-Qualität**
- **Type Hints** für alle Funktionen
- **Docstrings** für alle Module und Funktionen
- **Unit Tests** für neue Features
- **Code Coverage** > 90%
- **Linting** mit flake8 und black

---

## 📄 License

Dieses Projekt ist unter der **MIT License** lizenziert - siehe [LICENSE](LICENSE) Datei für Details.

---

## 🆘 Support

### 📞 **Hilfe & Support**
- **Issues:** [GitHub Issues](https://github.com/Rei1000/DocuMind-AI/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Rei1000/DocuMind-AI/discussions)
- **Documentation:** [Wiki](https://github.com/Rei1000/DocuMind-AI/wiki)
- **Email:** support@documind-ai.com

### 📚 **Ressourcen**
- **API Documentation:** http://localhost:8000/docs
- **User Guide:** [docs/user-guide.md](docs/user-guide.md)
- **Developer Guide:** [docs/developer-guide.md](docs/developer-guide.md)
- **Troubleshooting:** [docs/troubleshooting.md](docs/troubleshooting.md)

---

## 🎉 **Danke!**

Vielen Dank für die Nutzung von **DocuMind-AI**! 

**Entwickelt mit ❤️ für die Medizintechnik-Community**

---

<div align="center">

**DocuMind-AI** - *Die Zukunft des Qualitätsmanagements*

[Website](https://documind-ai.com) • [Documentation](https://docs.documind-ai.com) • [Support](https://support.documind-ai.com)

</div>