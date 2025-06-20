# KI-QMS Deployment Guide 🚀

> **Anleitung zur professionellen Installation und Konfiguration**

## 📋 Umgebungsvariablen

### Setup der .env Datei

Erstellen Sie eine `.env` Datei im Root-Verzeichnis mit folgenden Variablen:

```bash
# Beispiel .env Datei für KI-QMS

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_URL=sqlite:///./qms_mvp.db

# =============================================================================
# API CONFIGURATION  
# =============================================================================
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=true
SECRET_KEY=your-super-secret-key-change-this-in-production
CORS_ORIGINS=http://localhost:8501,http://127.0.0.1:8501

# =============================================================================
# FRONTEND CONFIGURATION
# =============================================================================
FRONTEND_HOST=127.0.0.1
FRONTEND_PORT=8501
API_BASE_URL=http://127.0.0.1:8000

# =============================================================================
# FILE UPLOAD CONFIGURATION
# =============================================================================
UPLOAD_DIR=uploads
MAX_FILE_SIZE=52428800
ALLOWED_MIME_TYPES=application/pdf,application/msword,text/plain

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL=INFO
LOG_DIR=logs
```

## 🐳 Docker Deployment (Roadmap)

Für produktive Umgebungen wird Docker-Support entwickelt:

```yaml
# docker-compose.yml (in Entwicklung)
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/ki_qms
    depends_on:
      - db
  
  frontend:
    build: ./frontend  
    ports:
      - "8501:8501"
    depends_on:
      - backend
      
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ki_qms
      POSTGRES_USER: ki_qms_user
      POSTGRES_PASSWORD: secure_password
```

## 🔧 Produktions-Konfiguration

### PostgreSQL Setup (Phase 2)

```bash
# PostgreSQL Installation
sudo apt install postgresql postgresql-contrib

# Datenbank erstellen
sudo -u postgres createdb ki_qms
sudo -u postgres createuser ki_qms_user

# .env anpassen
DATABASE_URL=postgresql://ki_qms_user:password@localhost:5432/ki_qms
```

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/ki-qms
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Systemd Services

```ini
# /etc/systemd/system/ki-qms-backend.service
[Unit]
Description=KI-QMS FastAPI Backend
After=network.target

[Service]
Type=simple
User=ki-qms
WorkingDirectory=/opt/ki-qms
Environment=PATH=/opt/ki-qms/venv/bin
ExecStart=/opt/ki-qms/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔐 Sicherheits-Checkliste

### Entwicklung
- [ ] `.env` Datei nie ins Git committen
- [ ] Standard-Passwörter ändern
- [ ] Debug-Modus in Produktion deaktivieren

### Produktion
- [ ] HTTPS mit SSL-Zertifikaten
- [ ] Starke SECRET_KEY generieren
- [ ] Database-Zugangsdaten sichern
- [ ] Firewall konfigurieren (nur Port 80/443)
- [ ] Regelmäßige Backups einrichten
- [ ] Log-Monitoring implementieren

## 📊 Monitoring

### Health Checks
```bash
# Backend Health
curl http://localhost:8000/health

# Frontend Health  
curl http://localhost:8501

# Database Connection
python -c "from backend.app.database import engine; engine.connect()"
```

### Log-Monitoring
```bash
# System-Logs
journalctl -u ki-qms-backend -f
journalctl -u ki-qms-frontend -f

# Application-Logs
tail -f logs/backend.log
tail -f logs/frontend.log
```

## 🔄 Updates & Wartung

### Update-Prozess
```bash
# 1. Code aktualisieren
git pull origin main

# 2. Dependencies updaten
source venv/bin/activate
pip install -r backend/requirements.txt

# 3. Database Migration (falls nötig)
# python backend/scripts/migrate_db.py

# 4. Services neustarten
./stop-all.sh
./start-all.sh
```

### Backup-Strategie
```bash
# Database Backup
cp backend/qms_mvp.db backups/qms_mvp_$(date +%Y%m%d_%H%M%S).db

# Upload-Ordner Backup
tar -czf backups/uploads_$(date +%Y%m%d).tar.gz backend/uploads/

# Automatisches Backup (Cron)
# 0 2 * * * cd /opt/ki-qms && ./scripts/backup.sh
```

---

*Für detaillierte Installation siehe [README.md](README.md)* 