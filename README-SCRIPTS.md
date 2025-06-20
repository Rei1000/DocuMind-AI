# KI-QMS System Scripts 🔧

> **Systemverwaltung und Deployment-Scripts für KI-QMS v0.1.0**

## 🚀 Verfügbare Scripts

### 1. `start-all.sh` - Komplettes System starten ⭐
```bash
./start-all.sh
```

**Features:**
- Startet Backend (FastAPI) + Frontend (Streamlit) automatisch
- Systemvoraussetzungen-Prüfung (Python, pip, Virtual Environment)
- Automatische Dependency-Installation
- Umfassende Health Checks für beide Services
- Intelligente PID-Verwaltung
- Farbige Ausgabe mit Erfolgs-/Fehlermeldungen
- Detaillierte Logging-Funktionen

**System-URLs nach dem Start:**
- 🖥️ **Frontend:** http://localhost:8501
- 🔧 **Backend API:** http://localhost:8000  
- 📚 **API Docs:** http://localhost:8000/docs
- ❤️ **Health Check:** http://localhost:8000/health

### 2. `start-backend.sh` - Nur Backend starten
```bash
./start-backend.sh
```

**Features:**
- Startet nur FastAPI Backend auf Port 8000
- Automatische Virtual Environment Aktivierung
- Development-Modus mit Hot-Reload
- Uvicorn Server mit optimierten Einstellungen

### 3. `stop-all.sh` - Alles stoppen 🛑
```bash
./stop-all.sh
```

**Features:**
- Stoppt alle KI-QMS Services graceful
- Cleanup von PID-Dateien (`pids/`)
- Prozess-Überwachung und Forceful Kill falls nötig
- Aufräumen von temporären Dateien

## 🧪 Development & Testing

### Standard-Workflow für Entwicklung:

**Option 1: Automatisiert (Empfohlen)**
```bash
# Komplettes System starten
./start-all.sh

# Entwickeln und testen...
# http://localhost:8501 für Frontend
# http://localhost:8000/docs für API

# System stoppen
./stop-all.sh
```

**Option 2: Manuell (für Debugging)**
```bash
# Terminal 1: Backend mit Hot-Reload
cd backend
source ../venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Frontend  
cd frontend
streamlit run streamlit_app.py --server.port 8501
```

## 🔧 Fehlerbehebung

### Backend startet nicht:
```bash
# 1. Port-Konflikte prüfen
lsof -i :8000
kill -9 <PID>  # Falls Port belegt

# 2. Virtual Environment prüfen
source venv/bin/activate
which python  # Sollte ./venv/bin/python zeigen

# 3. Dependencies prüfen
cd backend
pip install -r requirements.txt

# 4. Manueller Health Check
curl http://127.0.0.1:8000/health
```

### Frontend startet nicht:
```bash
# 1. Port-Konflikte prüfen
lsof -i :8501
pkill -f streamlit  # Alle Streamlit-Prozesse stoppen

# 2. Streamlit Cache leeren
streamlit cache clear

# 3. Manueller Start mit Debug
cd frontend
streamlit run streamlit_app.py --server.port 8501 --logger.level debug
```

### Virtual Environment Probleme:
```bash
# Virtual Environment neu erstellen
rm -rf venv
python -m venv venv
source venv/bin/activate

# Dependencies neu installieren
pip install --upgrade pip
cd backend && pip install -r requirements.txt
cd ../frontend && pip install streamlit pandas plotly requests
```

### Datenbank-Probleme:
```bash
# Datenbank-Status prüfen
ls -la backend/qms_mvp.db*

# Bei Korruption: Backup verwenden oder neu erstellen
cd backend
rm qms_mvp.db*
python -c "from app.database import create_tables; create_tables()"
```

## 📊 Service-Management

### Service-URLs

| Service | URL | Beschreibung |
|---------|-----|--------------|
| **Frontend** | http://localhost:8501 | Streamlit Web-Interface |
| **Backend API** | http://localhost:8000 | FastAPI REST API |
| **API Dokumentation** | http://localhost:8000/docs | Swagger UI |
| **API Redoc** | http://localhost:8000/redoc | Alternative API-Docs |
| **Health Check** | http://localhost:8000/health | Service-Status |

### Logs & Monitoring

**Log-Dateien:**
```bash
# System-Logs
tail -f logs/startup.log      # System-Start/Stop-Logs
tail -f logs/backend.log      # Backend-Logs (FastAPI/Uvicorn)
tail -f logs/frontend.log     # Frontend-Logs (Streamlit)

# Live-Monitoring beider Services
tail -f logs/backend.log logs/frontend.log
```

**PID-Management:**
```bash
# Aktive Prozesse prüfen
cat pids/backend.pid          # Backend-Prozess-ID
cat pids/frontend.pid         # Frontend-Prozess-ID

# Prozess-Status prüfen
ps aux | grep $(cat pids/backend.pid)
ps aux | grep $(cat pids/frontend.pid)
```

## 🎯 Produktions-Deployment

### Empfohlener Workflow für Produktion:

```bash
# 1. Repository aktualisieren
git pull origin main

# 2. Virtual Environment aktualisieren
source venv/bin/activate
cd backend && pip install -r requirements.txt

# 3. System-Health-Check
./start-all.sh --health-check

# 4. Services starten
./start-all.sh

# 5. Monitoring aktivieren
tail -f logs/backend.log logs/frontend.log
```

### Service-Überwachung:

```bash
# Automatische Restart-Logik (Beispiel mit Cron)
# */5 * * * * cd /path/to/KI-QMS && ./scripts/health-monitor.sh

# Status-Prüfung für Monitoring-Tools
curl -f http://localhost:8000/health || echo "Backend DOWN"
curl -f http://localhost:8501 || echo "Frontend DOWN"
```

## 🔒 Sicherheit & Wartung

### Regelmäßige Wartungsaufgaben:

```bash
# 1. Log-Rotation (wöchentlich)
find logs/ -name "*.log" -size +100M -exec mv {} {}.old \;

# 2. Temporary Files Cleanup
rm -rf backend/__pycache__
rm -rf frontend/__pycache__

# 3. Database Backup
cp backend/qms_mvp.db backend/qms_mvp_backup_$(date +%Y%m%d_%H%M%S).db

# 4. Upload-Ordner bereinigen (optional)
find backend/uploads/ -name "*.tmp" -delete
```

### Sicherheits-Checkliste:

- [ ] **Firewall:** Nur notwendige Ports freigeben (8000, 8501)
- [ ] **SSL/TLS:** HTTPS für Produktionsumgebung konfigurieren  
- [ ] **Authentifizierung:** User-Management implementieren (Roadmap)
- [ ] **Backup:** Regelmäßige DB-Backups einrichten
- [ ] **Monitoring:** Health-Checks und Alerting konfigurieren

## 📝 Entwickler-Notizen

### Frontend-Versionen:
- `streamlit_app.py` - **Hauptversion** (Standard, stabil)
- `streamlit_app_new.py` - Erweiterte Version mit zusätzlichen Features

**Aktuell verwendet:** `streamlit_app.py` (über `start-all.sh`)

### Backend-Konfiguration:
- **Development:** `--reload` aktiviert für Hot-Reload
- **Production:** Optimierte Uvicorn-Settings für Performance
- **Database:** SQLite (Migration zu PostgreSQL in Phase 2)

### API-Integration:
- **Base URL:** `http://127.0.0.1:8000` (OHNE `/api` Suffix!)
- **Timeout:** 30 Sekunden für Upload-Operationen
- **File Upload:** Multipart/form-data mit SHA-256 Hashing

---

## 🆘 Support

**Bei Problemen:**
1. **Logs prüfen:** `tail -f logs/backend.log logs/frontend.log`
2. **Health-Check:** `curl http://localhost:8000/health`
3. **Clean Restart:** `./stop-all.sh && ./start-all.sh`
4. **GitHub Issues:** [Probleme melden](https://github.com/Rei1000/KI-QMS/issues)

**Hilfreiche Befehle:**
```bash
# System-Status kompakt anzeigen
./start-all.sh --status

# Services einzeln neustarten
./stop-all.sh && sleep 2 && ./start-all.sh

# Debug-Modus
export DEBUG=1 && ./start-all.sh
```

---

*📝 Diese Dokumentation bezieht sich auf KI-QMS Version 0.1.0* 