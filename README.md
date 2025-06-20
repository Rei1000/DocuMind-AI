# KI-QMS - AI-Powered Quality Management System 🏥

> **Version 0.1.0** | Ein intelligentes Qualitätsmanagementsystem für die Medizintechnik mit KI-Unterstützung

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-3.x-lightgrey.svg)](https://sqlite.org)
[![ISO 13485](https://img.shields.io/badge/ISO_13485-compliant-blue.svg)](https://www.iso.org/standard/59752.html)
[![MDR](https://img.shields.io/badge/EU_MDR-ready-yellow.svg)](https://ec.europa.eu/health/md_sector/new-regulations_en)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

## 📋 Inhaltsverzeichnis

- [Überblick](#überblick)
- [Features](#features)
- [Technologie-Stack](#technologie-stack)
- [Installation](#installation)
- [Schnellstart](#schnellstart)
- [API-Dokumentation](#api-dokumentation)
- [Systemarchitektur](#systemarchitektur)
- [Compliance & Standards](#compliance--standards)
- [Verwendung](#verwendung)
- [Entwicklung](#entwicklung)
- [Beitragen](#beitragen)
- [Lizenz](#lizenz)
- [Kontakt](#kontakt)

## 🎯 Überblick

**KI-QMS** ist ein modernes, KI-gestütztes Qualitätsmanagementsystem, das speziell für Medizintechnik-Unternehmen entwickelt wurde. Es kombiniert bewährte QMS-Praktiken mit modernster Technologie, um ISO 13485 und MDR-konforme Dokumentenverwaltung zu ermöglichen.

### 🏢 Zielgruppe

- **Medizintechnik-Unternehmen** (Startups bis Enterprise)
- **QM-Manager und QM-Beauftragte**
- **Externe QM-Beratungsunternehmen**
- **Regulatorische Affairs Teams**
- **Produktentwicklungsteams**

### 🎪 Hauptmerkmale

- **13 Stakeholder-orientierte Interessensgruppen** für granulare Berechtigungen
- **25+ QMS-spezifische Dokumenttypen** (SOPs, Risikoanalysen, Validierungsprotokolle)
- **Intelligente Dokumentenerkennung** mit automatischer Klassifizierung
- **ISO 13485 & MDR-konforme** Workflows und Freigabeprozesse
- **KI-powered Text-Extraktion** für RAG-ready Dokumentenindexierung
- **Equipment-Management** mit automatischer Kalibrierungsüberwachung
- **RESTful API** mit vollständiger OpenAPI-Dokumentation

## ✨ Features

### 🏗️ Kern-Funktionalitäten

#### 📁 **Dokumentenmanagement**
- **25+ Dokumenttypen**: QM_MANUAL, SOP, WORK_INSTRUCTION, RISK_ASSESSMENT, VALIDATION_PROTOCOL, etc.
- **4-stufiger Freigabe-Workflow**: DRAFT → REVIEW → APPROVED → OBSOLETE
- **Versionskontrolle** mit Semantic Versioning
- **Automatische Dokumentennummerierung** (DOC-YYYY-XXX Format)
- **Intelligente Text-Extraktion** aus PDF, DOCX, TXT
- **Duplikat-Erkennung** über SHA-256 Hashing
- **Physische Dateispeicherung** mit Integritätsprüfung

#### 👥 **Stakeholder-Management (13 Gruppen)**
1. **Geschäftsführung** - Strategische Entscheidungen
2. **QM-Management** - Qualitätssicherung und Compliance
3. **Entwicklung** - Produktentwicklung und Design Controls
4. **Produktion** - Herstellungsprozesse
5. **Einkauf** - Lieferantenbewertung
6. **Vertrieb** - Marktanforderungen
7. **Regulatory Affairs** - Zulassungen und Compliance
8. **Klinische Bewertung** - Klinische Daten und Studien
9. **Post-Market Surveillance** - Marktüberwachung
10. **IT/Infrastruktur** - Technische Infrastruktur
11. **Personal/HR** - Mitarbeiterqualifizierung
12. **Externe Auditoren** - Unabhängige Bewertung
13. **Lieferanten** - Externe Dienstleister

#### 🔧 **Equipment-Management**
- **Asset-Tracking** mit eindeutigen Seriennummern
- **Automatische Kalibrierungsplanung** mit Fristen-Überwachung
- **Compliance-Dashboard** für überfällige Kalibrierungen
- **Zertifikats-Management** für Audit-Trail
- **Mehrere Equipment-Kategorien** (Messgeräte, Laborausstattung, Prüfgeräte)

#### 📊 **Normen & Compliance**
- **ISO 13485:2016** - Qualitätsmanagementsysteme für Medizinprodukte
- **EU MDR 2017/745** - Medizinprodukteverordnung
- **ISO 14971** - Risikomanagement für Medizinprodukte
- **IEC 62304** - Software-Lebenszyklusprozesse
- **ISO 10993** - Biologische Beurteilung
- **Erweiterbar** durch Normen-Upload-Funktion

### 🤖 **KI-Features (Roadmap)**
- **Automatische Dokumentklassifizierung**
- **Intelligente Titel-Extraktion** aus Normtexten
- **RAG-basierte Dokumentensuche**
- **Compliance-Gap-Analyse**
- **Automatische Risikobewertung**

## 🛠️ Technologie-Stack

### **Backend**
- **[FastAPI](https://fastapi.tiangolo.com/)** - Moderne, schnelle Web-API
- **[SQLAlchemy](https://sqlalchemy.org/)** - ORM für Datenbank-Operations
- **[Pydantic v2](https://docs.pydantic.dev/)** - Datenvalidierung und Serialisierung
- **[SQLite](https://sqlite.org/)** - Embedded Datenbank (Migration zu PostgreSQL geplant)
- **[Uvicorn](https://uvicorn.org/)** - ASGI Server für Produktion

### **Frontend**
- **[Streamlit](https://streamlit.io/)** - Rapid Prototyping für Web-Interfaces
- **[Pandas](https://pandas.pydata.org/)** - Datenmanipulation und -analyse
- **[Plotly](https://plotly.com/)** - Interaktive Datenvisualisierung

### **Text-Verarbeitung & KI**
- **[PyPDF2](https://pypdf2.readthedocs.io/)** - PDF-Text-Extraktion
- **[python-docx](https://python-docx.readthedocs.io/)** - Word-Dokument-Verarbeitung
- **[openpyxl](https://openpyxl.readthedocs.io/)** - Excel-Dateien-Support
- **[aiofiles](https://github.com/Tinche/aiofiles)** - Asynchrone Dateioperationen

### **Deployment & DevOps**
- **[Docker](https://docker.com/)** - Containerisierung (geplant)
- **[GitHub Actions](https://github.com/features/actions)** - CI/CD Pipeline (geplant)
- **Shell Scripts** - Automatisierte Start/Stop-Prozesse

### **Entwicklung & Testing**
- **[pytest](https://pytest.org/)** - Test-Framework (geplant)
- **[Black](https://black.readthedocs.io/)** - Code-Formatierung (geplant)
- **[mypy](https://mypy.readthedocs.io/)** - Static Type Checking (geplant)

## 🚀 Installation

### Voraussetzungen

- **Python 3.12+** (getestet mit 3.12.4)
- **pip** Package Manager
- **Git** für Repository-Kloning
- **8 GB RAM** empfohlen für größere Dokumentsammlungen

### 1. Repository klonen

```bash
git clone https://github.com/Rei1000/KI-QMS.git
cd KI-QMS
```

### 2. Virtual Environment erstellen

```bash
# Virtual Environment erstellen
python -m venv venv

# Aktivieren (Linux/macOS)
source venv/bin/activate

# Aktivieren (Windows)
venv\Scripts\activate
```

### 3. Dependencies installieren

```bash
# Backend-Dependencies
cd backend
pip install -r requirements.txt
cd ..

# Frontend-Dependencies (automatisch durch Streamlit)
pip install streamlit pandas plotly requests
```

### 4. Datenbank initialisieren

```bash
# Automatische Datenbank-Erstellung beim ersten Start
# Keine manuelle Einrichtung erforderlich
```

## ⚡ Schnellstart

### Komplettes System starten

```bash
# Beide Services automatisch starten
./start-all.sh
```

**Zugriff:**
- 🖥️ **Frontend:** http://localhost:8501
- 🔧 **Backend API:** http://localhost:8000
- 📚 **API Docs:** http://localhost:8000/docs
- ❤️ **Health Check:** http://localhost:8000/health

### Manueller Start (Entwicklung)

```bash
# Terminal 1: Backend starten
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Frontend starten  
cd frontend
streamlit run streamlit_app.py --server.port 8501
```

### System stoppen

```bash
# Alle Services stoppen
./stop-all.sh

# Oder Ctrl+C im jeweiligen Terminal
```

## 📖 API-Dokumentation

### Interaktive API-Dokumentation

Nach dem Start verfügbar unter:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Hauptendpunkte

| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/documents` | GET, POST | Dokumentenverwaltung |
| `/api/documents/with-file` | POST | Dokument mit Datei-Upload |
| `/api/interest-groups` | GET, POST | Stakeholder-Gruppen |
| `/api/users` | GET, POST | Benutzerverwaltung |
| `/api/equipment` | GET, POST | Equipment-Management |
| `/api/calibrations` | GET, POST | Kalibrierungen |
| `/api/norms` | GET, POST | Normen-Management |

### Beispiel: Dokument hochladen

```bash
curl -X POST "http://localhost:8000/api/documents/with-file" \
  -F "file=@document.pdf" \
  -F "document_type=SOP" \
  -F "creator_id=1" \
  -F "title=Neue Arbeitsanweisung"
```

## 🏗️ Systemarchitektur

### Überblick

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
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Datenbankschema

```sql
-- Kern-Entitäten
InterestGroups (13 Stakeholder-Gruppen)
Users (mit Rollen und Berechtigungen)  
UserGroupMemberships (Many-to-Many)
Documents (25+ QMS-Dokumenttypen)
Equipment (Asset-Management)
Calibrations (Kalibrierungsprotokoll)
Norms (Compliance-Standards)

-- Beziehungen
User 1:N Documents (Creator)
Document N:M Norms (Mapping)
Equipment 1:N Calibrations
User 1:N Calibrations (Responsible)
```

### Dateispeicherung

```
backend/uploads/
├── SOP/                    # Standard Operating Procedures
├── QM_MANUAL/             # Qualitätsmanagement-Handbücher  
├── STANDARD_NORM/         # Normen und Standards
├── RISK_ASSESSMENT/       # Risikoanalysen
├── VALIDATION_PROTOCOL/   # Validierungsprotokolle
├── OTHER/                 # Sonstige Dokumente
└── [weitere Typen]/       # Dynamisch nach Bedarf
```

**Dateinamen-Konvention:**
```
YYYYMMDD_HHMMSS_[hash8]_[originalname]
Beispiel: 20250620_143052_a1b2c3d4_ISO_13485_Manual.pdf
```

## 🛡️ Compliance & Standards

### ISO 13485:2016 Compliance

| Kapitel | Anforderung | KI-QMS Feature |
|---------|-------------|----------------|
| 4.2.3 | Dokumentenlenkung | ✅ Versionskontrolle, Freigabe-Workflow |
| 4.2.4 | Aufzeichnungen | ✅ Audit-Trail, Zeitstempel |
| 7.5.1 | Produktionssteuerung | ✅ SOP-Management, Equipment-Tracking |
| 8.2.1 | Kundenzufriedenheit | ✅ Post-Market Surveillance Gruppe |
| 8.5 | Verbesserung | ✅ CAPA-Dokumentation, Analytics |

### EU MDR 2017/745 Ready

- **Technische Dokumentation** (Artikel 10)
- **Qualitätsmanagementsystem** (Artikel 10)
- **Post-Market Surveillance** (Artikel 83-92)
- **EUDAMED Integration** (vorbereitet)

### FDA 21 CFR Part 820 Support

- **Design Controls** (820.30)
- **Document Controls** (820.40)
- **Corrective Actions** (820.100)

## 💡 Verwendung

### Dashboard-Überblick

Das Haupt-Dashboard bietet:
- 📊 **Dokumenten-Metriken** (Anzahl, Typen, Status)
- 🔄 **Workflow-Status** (Pending Reviews, Approvals)
- ⚠️ **Compliance-Alerts** (Überfällige Kalibrierungen)
- 📈 **Trend-Analysen** (Upload-Aktivität, Approval-Zeiten)

### Dokumenten-Upload

1. **Datei auswählen** (PDF, DOCX, TXT, Excel)
2. **Dokumenttyp wählen** (25+ Optionen)
3. **Metadaten eingeben** (Titel, Beschreibung, Kapitel)
4. **Upload & Verarbeitung** (Automatische Text-Extraktion)
5. **Freigabe-Workflow** (DRAFT → REVIEW → APPROVED)

### Equipment-Management

1. **Gerät registrieren** (Name, Seriennummer, Standort)
2. **Kalibrierungsintervall** festlegen
3. **Automatische Erinnerungen** bei fälligen Kalibrierungen
4. **Zertifikate hochladen** für Audit-Trail

### Stakeholder-Integration

Jede der 13 Interessensgruppen hat:
- **Spezifische Berechtigungen** für Dokumente und Funktionen
- **Gruppenkonsistente Workflows** für ihre Aufgaben
- **KI-Funktionalitäten** zugeschnitten auf ihre Bedürfnisse

## 🔧 Entwicklung

### Entwicklungsumgebung einrichten

```bash
# Repository forken und klonen
git clone https://github.com/IhrUsername/KI-QMS.git
cd KI-QMS

# Development Branch erstellen
git checkout -b feature/neue-funktionalität

# Dependencies installieren (siehe Installation)
source venv/bin/activate
cd backend && pip install -r requirements.txt
```

### Code-Struktur

```
KI-QMS/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI Hauptanwendung
│   │   ├── models.py         # SQLAlchemy Datenmodelle
│   │   ├── schemas.py        # Pydantic Schemas
│   │   ├── database.py       # Datenbank-Konfiguration
│   │   └── text_extraction.py # KI-Text-Verarbeitung
│   ├── uploads/              # Dateispeicher
│   ├── requirements.txt      # Python Dependencies
│   └── qms_mvp.db           # SQLite Datenbank
├── frontend/
│   ├── streamlit_app.py     # Haupt-Frontend
│   └── streamlit_app_new.py # Erweiterte Version
├── logs/                    # System-Logs
├── scripts/                 # Hilfsskripte
├── start-all.sh            # System-Starter
├── stop-all.sh             # System-Stopper
└── README.md               # Diese Datei
```

### API-Endpunkt hinzufügen

1. **Model definieren** in `models.py`
2. **Schema erstellen** in `schemas.py`  
3. **Endpunkt implementieren** in `main.py`
4. **Tests schreiben** (geplant)
5. **Dokumentation updaten**

### Frontend-Komponente erstellen

1. **Streamlit-Seite** in `streamlit_app.py` hinzufügen
2. **API-Integration** über `requests`
3. **Benutzer-Interface** mit Streamlit-Komponenten
4. **Fehlerbehandlung** und Validierung

## 🤝 Beitragen

Wir freuen uns über Beiträge! Hier ist, wie Sie mithelfen können:

### Contribution Guidelines

1. **Issues erstellen** für Bugs oder Feature-Requests
2. **Fork** das Repository
3. **Feature Branch** erstellen (`git checkout -b feature/AmazingFeature`)
4. **Commits** mit aussagekräftigen Nachrichten
5. **Pull Request** erstellen

### Code-Standards

- **Python PEP 8** Stil-Guide befolgen
- **Type Hints** für alle Funktionen
- **Docstrings** für Module, Klassen und Funktionen
- **Kommentare** auf Deutsch für Business-Logik
- **Tests** für neue Features (geplant)

### Prioritäre Entwicklungsbereiche

- 🔐 **Authentifizierung & Autorisierung**
- 🐳 **Docker-Containerisierung**
- 🧪 **Test-Suite Entwicklung**
- 🤖 **KI-Features Implementation**
- 📊 **Analytics & Reporting**
- 🌐 **Internationalisierung**

## 📜 Lizenz

Dieses Projekt steht unter der **MIT Lizenz** - siehe [LICENSE](LICENSE) Datei für Details.

## 👨‍💻 Autor & Kontakt

**Reiner Jaeger**
- 📧 Email: [mail@rtjaeger.de](mailto:mail@rtjaeger.de)
- 🐙 GitHub: [@Rei1000](https://github.com/Rei1000)
- 💼 LinkedIn: [Ihr LinkedIn Profil]

### Support & Community

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/Rei1000/KI-QMS/issues)
- 💡 **Feature Requests:** [GitHub Discussions](https://github.com/Rei1000/KI-QMS/discussions)
- ❓ **Fragen:** [GitHub Issues](https://github.com/Rei1000/KI-QMS/issues) mit Label `question`

---

## 📈 Roadmap

### Phase 1 (Aktuell) - MVP ✅
- ✅ Basis-Dokumentenmanagement
- ✅ 13-Stakeholder-System
- ✅ Equipment-Management
- ✅ RESTful API
- ✅ Streamlit Frontend

### Phase 2 (Q2 2024) - KI-Integration 🚧
- 🔄 RAG-basierte Dokumentensuche
- 🔄 Automatische Dokumentklassifizierung
- 🔄 Compliance-Gap-Analyse
- 🔄 PostgreSQL Migration
- 🔄 Docker Deployment

### Phase 3 (Q3 2024) - Enterprise Features 📋
- 📋 Multi-Tenant Architektur
- 📋 LDAP/SSO Integration
- 📋 Advanced Analytics
- 📋 Mobile App
- 📋 Workflow Automation

### Phase 4 (Q4 2024) - Ecosytsem 🌟
- 🌟 EUDAMED Integration
- 🌟 Third-Party APIs
- 🌟 Machine Learning Models
- 🌟 Advanced Reporting
- 🌟 Marketplace Integration

---

⭐ **Gefällt Ihnen KI-QMS?** Geben Sie uns einen Stern auf GitHub! 

📢 **Bleiben Sie auf dem Laufenden:** Watch dieses Repository für Updates und neue Releases.

---

*Entwickelt mit ❤️ für die Medizintechnik-Community* 