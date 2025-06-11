#!/bin/bash

# KI-QMS Backend Starter Script - Stabilisierte Version
# Dieses Script startet das Backend automatisch mit der richtigen Umgebung

set -e  # Exit bei Fehlern

echo "🚀 Starte KI-QMS Backend..."

# Zum Projekt-Root navigieren (falls nicht dort)
cd "$(dirname "$0")"

# Funktion: Freien Port finden
find_free_port() {
    local port=$1
    while lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; do
        echo "⚠️  Port $port ist belegt, versuche Port $((port + 1))..."
        port=$((port + 1))
    done
    echo $port
}

# Funktion: Bestehende Backend-Prozesse stoppen
stop_existing_backend() {
    echo "🧹 Stoppe bestehende Backend-Prozesse..."
    pkill -f "uvicorn app.main:app" >/dev/null 2>&1 || true
    pkill -f "python.*app.main" >/dev/null 2>&1 || true
    sleep 2
}

# Prüfen ob venv existiert
if [ ! -d "venv" ]; then
    echo "❌ Virtual Environment nicht gefunden!"
    echo "   Erstelle automatisch..."
    python3 -m venv venv
    echo "✅ Virtual Environment erstellt"
fi

# Virtual Environment aktivieren
echo "📦 Aktiviere Virtual Environment..."
source venv/bin/activate

# Prüfen ob requirements installiert sind
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ requirements.txt nicht gefunden!"
    exit 1
fi

# Dependencies installieren falls nötig
echo "📋 Prüfe Dependencies..."
cd backend
pip install -q -r requirements.txt >/dev/null 2>&1 || {
    echo "⚠️  Installiere fehlende Dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installiert"
}

# Prüfen ob uvicorn verfügbar ist
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "❌ uvicorn nicht verfügbar! Installiere..."
    pip install uvicorn
fi

# Bestehende Prozesse stoppen
stop_existing_backend

# Prüfen ob die Datenbank existiert
if [ ! -f "qms_mvp.db" ]; then
    echo "🗄️  Erstelle Datenbank mit Testdaten..."
    python scripts/init_mvp_db.py
    echo "✅ Datenbank erstellt"
fi

# Freien Port finden
FREE_PORT=$(find_free_port 8000)
if [ "$FREE_PORT" != "8000" ]; then
    echo "📊 Verwende Port $FREE_PORT statt 8000"
else
    echo "📊 Verwende Standard-Port 8000"
fi

# Umgebungsvariablen setzen
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Erfolg anzeigen
echo ""
echo "✅ Backend-Setup abgeschlossen!"
echo "🎉 Starte FastAPI Backend auf http://127.0.0.1:$FREE_PORT"
echo "📚 Swagger Docs: http://127.0.0.1:$FREE_PORT/docs"
echo "🔍 Health Check: http://127.0.0.1:$FREE_PORT/health"
echo ""
echo "Zum Stoppen: Ctrl+C"
echo "============================================"

# Graceful Shutdown Handler
trap 'echo ""; echo "🛑 Stoppe Backend..."; pkill -f "uvicorn app.main:app" >/dev/null 2>&1 || true; echo "✅ Backend gestoppt"; exit 0' SIGINT SIGTERM

# Backend mit verbesserter Konfiguration starten
echo "🚀 Starte Server..."
uvicorn app.main:app \
    --reload \
    --port $FREE_PORT \
    --host 127.0.0.1 \
    --log-level info \
    --access-log 