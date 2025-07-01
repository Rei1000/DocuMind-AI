#!/bin/bash

# 🆓 KI-QMS Free AI Setup Script
# Automatische Installation und Konfiguration kostenloser KI-Provider

set -e  # Beenden bei Fehlern

echo "🚀 KI-QMS Free AI Setup gestartet..."
echo "========================================="

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Hilfsfunktionen
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Betriebssystem erkennen
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]]; then
    OS="windows"
fi

print_step "Betriebssystem erkannt: $OS"

# 1. .env Datei erstellen
print_step "Erstelle .env Konfigurationsdatei..."

if [ ! -f ".env" ]; then
    cp env-template.txt .env
    print_success ".env Datei aus Vorlage erstellt"
else
    print_warning ".env Datei existiert bereits - wird nicht überschrieben"
fi

# 2. Ollama Installation prüfen/installieren
print_step "Prüfe Ollama Installation..."

if command -v ollama &> /dev/null; then
    print_success "Ollama ist bereits installiert"
else
    print_step "Installiere Ollama..."
    
    if [[ "$OS" == "macos" || "$OS" == "linux" ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
        print_success "Ollama erfolgreich installiert"
    else
        print_warning "Windows erkannt - bitte Ollama manuell von https://ollama.ai/download installieren"
    fi
fi

# 3. Ollama starten
print_step "Starte Ollama Service..."

if [[ "$OS" == "macos" ]]; then
    # macOS: Ollama im Hintergrund starten
    if ! pgrep -x "ollama" > /dev/null; then
        ollama serve > /dev/null 2>&1 &
        sleep 3
        print_success "Ollama Service gestartet"
    else
        print_success "Ollama Service läuft bereits"
    fi
elif [[ "$OS" == "linux" ]]; then
    # Linux: Systemd Service
    if systemctl is-active --quiet ollama; then
        print_success "Ollama Service läuft bereits"
    else
        sudo systemctl start ollama || ollama serve > /dev/null 2>&1 &
        sleep 3
        print_success "Ollama Service gestartet"
    fi
fi

# 4. Mistral Modell herunterladen
print_step "Lade Mistral 7B Modell herunter (kann einige Minuten dauern)..."

if ollama list | grep -q "mistral:7b"; then
    print_success "Mistral 7B ist bereits verfügbar"
else
    print_step "Lade Mistral 7B herunter (~4GB)..."
    ollama pull mistral:7b
    print_success "Mistral 7B erfolgreich heruntergeladen"
fi

# 5. Ollama Test
print_step "Teste Ollama Installation..."

if curl -s http://localhost:11434/api/tags > /dev/null; then
    print_success "Ollama API ist erreichbar"
else
    print_error "Ollama API nicht erreichbar - möglicherweise noch nicht gestartet"
    print_warning "Versuchen Sie: ollama serve"
fi

# 6. Python Dependencies prüfen
print_step "Prüfe Python Dependencies..."

cd backend

if [ -f "requirements.txt" ]; then
    print_step "Installiere/Aktualisiere Python Dependencies..."
    pip install -r requirements.txt
    print_success "Python Dependencies installiert"
fi

# 7. Backend testen
print_step "Teste Backend Start..."

# Kurzer Test-Start des Backends
timeout 10 python -c "
import sys
sys.path.insert(0, '.')
try:
    from app.main import app
    print('✅ Backend import erfolgreich')
except Exception as e:
    print(f'❌ Backend import fehlgeschlagen: {e}')
    sys.exit(1)
" && print_success "Backend kann erfolgreich gestartet werden" || print_error "Backend Startproblem"

cd ..

# 8. Setup-Zusammenfassung
echo ""
echo "========================================="
echo -e "${GREEN}🎉 Free AI Setup abgeschlossen!${NC}"
echo "========================================="
echo ""
echo -e "${BLUE}📋 Nächste Schritte:${NC}"
echo ""
echo "1. 🔧 API Keys eintragen (optional):"
echo "   - Bearbeiten Sie .env und fügen Sie Ihre API-Keys hinzu:"
echo "   - HUGGINGFACE_API_KEY=hf_xxx (kostenlos bei huggingface.co)"
echo "   - GOOGLE_AI_API_KEY=xxx (kostenlos bei aistudio.google.com)"
echo ""
echo "2. 🚀 System starten:"
echo "   cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "3. 🧪 Testen:"
echo "   http://localhost:8000/docs → 'Free AI Analysis' Endpunkte"
echo ""
echo "4. 📖 Dokumentation:"
echo "   FREE-AI-SETUP.md für detaillierte Anweisungen"
echo ""

# 9. Verfügbare Provider Status
print_step "Provider Status:"

if command -v ollama &> /dev/null && curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "   🟢 Ollama: ${GREEN}Verfügbar${NC} (lokal, kostenlos)"
else
    echo -e "   🔴 Ollama: ${RED}Nicht verfügbar${NC}"
fi

echo -e "   🟡 Hugging Face: ${YELLOW}API Key erforderlich${NC}"
echo -e "   🟡 Google Gemini: ${YELLOW}API Key erforderlich${NC}"
echo -e "   🟢 Regel-basiert: ${GREEN}Immer verfügbar${NC}"

echo ""
echo -e "${GREEN}Ihr KI-QMS System ist bereit für kostenlose KI-Analyse! 🎉${NC}"
echo ""

# Optional: Backend direkt starten
read -p "🚀 Backend jetzt starten? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Starte Backend..."
    cd backend
    echo "Backend läuft auf http://localhost:8000"
    echo "Swagger UI: http://localhost:8000/docs"
    echo "Drücken Sie Ctrl+C zum Beenden"
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi 