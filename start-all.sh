#!/bin/bash

# =============================================================================
# KI-QMS System Starter v1.0
# =============================================================================
# Automatisierter Start des KI-QMS (AI-powered Quality Management System)
# für Medizinprodukte mit ISO 13485, MDR und FDA 21 CFR Part 820 Compliance
#
# Autor: KI-QMS Team
# Datum: $(date +"%Y-%m-%d")
# =============================================================================

# Farbdefinitionen für bessere Terminal-Ausgabe
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly PURPLE='\033[0;35m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m' # No Color

# System-Konfiguration
readonly BACKEND_PORT=8000
readonly FRONTEND_PORT=8501
readonly VENV_PATH="./venv"
readonly BACKEND_PATH="./backend"
readonly FRONTEND_PATH="./frontend"
readonly LOG_DIR="./logs"
readonly PID_DIR="./pids"

# Erstelle notwendige Verzeichnisse
mkdir -p "$LOG_DIR" "$PID_DIR"

# =============================================================================
# LOGGING FUNKTIONEN
# =============================================================================

log_message() {
    # Strukturierte Log-Nachrichten mit Zeitstempel
    # $1: Log-Level (INFO, WARN, ERROR, SUCCESS)
    # $2: Komponente (SYSTEM, BACKEND, FRONTEND)
    # $3: Nachricht
    
    local level=$1
    local component=$2
    local message=$3
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Farbe basierend auf Log-Level
    local color=$WHITE
    case $level in
        "INFO")    color=$BLUE ;;
        "SUCCESS") color=$GREEN ;;
        "WARN")    color=$YELLOW ;;
        "ERROR")   color=$RED ;;
    esac
    
    # Console-Ausgabe
    echo -e "${color}[$timestamp] [$level] [$component] $message${NC}"
    
    # Log-Datei
    echo "[$timestamp] [$level] [$component] $message" >> "$LOG_DIR/startup.log"
}

# =============================================================================
# BANNER UND SYSTEM-INFO
# =============================================================================

show_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════════════╗"
    echo "║                        🏥 KI-QMS SYSTEM STARTER                       ║"
    echo "║                    AI-powered Quality Management                      ║"
    echo "║                                                                       ║"
    echo "║  📋 ISO 13485 Compliant   🇪🇺 MDR Ready   🇺🇸 FDA 21 CFR Part 820  ║"
    echo "║                                                                       ║"
    echo "║  🔧 Backend: FastAPI      🖥️  Frontend: Streamlit                   ║"
    echo "║  📊 13 Stakeholder Groups 📁 25+ Document Types                      ║"
    echo "╚═══════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${WHITE}🕐 Startzeitpunkt: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${WHITE}📍 Arbeitsverzeichnis: $(pwd)${NC}"
    echo -e "${WHITE}🖥️  System: $(uname -s) $(uname -r)${NC}"
    echo ""
}

# =============================================================================
# STOP-FUNKTIONEN (Integriert vor dem Start)
# =============================================================================

stop_existing_services() {
    # Stoppt alle laufenden KI-QMS Services vor dem Neustart
    
    log_message "INFO" "SYSTEM" "Stoppe bestehende Services..."
    local services_stopped=0
    
    # Backend stoppen (Port 8000)
    local backend_pids=$(lsof -ti:$BACKEND_PORT 2>/dev/null)
    if [ ! -z "$backend_pids" ]; then
        log_message "INFO" "BACKEND" "Stoppe Backend auf Port $BACKEND_PORT..."
        echo "$backend_pids" | xargs kill -TERM 2>/dev/null
        sleep 2
        
        # Forceful kill falls nötig
        backend_pids=$(lsof -ti:$BACKEND_PORT 2>/dev/null)
        if [ ! -z "$backend_pids" ]; then
            echo "$backend_pids" | xargs kill -9 2>/dev/null
            log_message "WARN" "BACKEND" "Forceful kill durchgeführt"
        fi
        services_stopped=$((services_stopped + 1))
    fi
    
    # Frontend stoppen (Port 8501)
    local frontend_pids=$(lsof -ti:$FRONTEND_PORT 2>/dev/null)
    if [ ! -z "$frontend_pids" ]; then
        log_message "INFO" "FRONTEND" "Stoppe Frontend auf Port $FRONTEND_PORT..."
        echo "$frontend_pids" | xargs kill -TERM 2>/dev/null
        sleep 2
        
        # Forceful kill falls nötig
        frontend_pids=$(lsof -ti:$FRONTEND_PORT 2>/dev/null)
        if [ ! -z "$frontend_pids" ]; then
            echo "$frontend_pids" | xargs kill -9 2>/dev/null
            log_message "WARN" "FRONTEND" "Forceful kill durchgeführt"
        fi
        services_stopped=$((services_stopped + 1))
    fi
    
    # Cleanup PID-Dateien
    rm -f "$PID_DIR"/*.pid
    
    if [ $services_stopped -gt 0 ]; then
        log_message "SUCCESS" "SYSTEM" "$services_stopped Service(s) gestoppt"
        sleep 1
    else
        log_message "INFO" "SYSTEM" "Keine laufenden Services gefunden"
    fi
}

# =============================================================================
# SYSTEM-PRÜFUNGEN
# =============================================================================

check_system_requirements() {
    # Überprüft alle Systemvoraussetzungen
    
    log_message "INFO" "SYSTEM" "Prüfe Systemvoraussetzungen..."
    local errors=0
    
    # Python-Version prüfen
    if ! command -v python3 &> /dev/null; then
        log_message "ERROR" "SYSTEM" "Python3 nicht gefunden!"
        errors=$((errors + 1))
    else
        local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_message "SUCCESS" "SYSTEM" "Python $python_version gefunden"
        
        # Mindestversion 3.8 prüfen
        if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)"; then
            log_message "ERROR" "SYSTEM" "Python 3.8+ erforderlich, gefunden: $python_version"
            errors=$((errors + 1))
        fi
    fi
    
    # Pip prüfen
    if ! command -v pip3 &> /dev/null; then
        log_message "ERROR" "SYSTEM" "pip3 nicht gefunden!"
        errors=$((errors + 1))
    else
        log_message "SUCCESS" "SYSTEM" "pip3 verfügbar"
    fi
    
    # Projektstruktur prüfen
    local required_dirs=("backend" "frontend" "backend/app")
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            log_message "ERROR" "SYSTEM" "Verzeichnis '$dir' nicht gefunden!"
            errors=$((errors + 1))
        fi
    done
    
    # Wichtige Dateien prüfen
    local required_files=("backend/requirements.txt" "backend/app/main.py" "frontend/streamlit_app.py")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_message "ERROR" "SYSTEM" "Datei '$file' nicht gefunden!"
            errors=$((errors + 1))
        fi
    done
    
    if [ $errors -eq 0 ]; then
        log_message "SUCCESS" "SYSTEM" "Alle Systemvoraussetzungen erfüllt"
        return 0
    else
        log_message "ERROR" "SYSTEM" "$errors Fehler gefunden - Abbruch"
        return 1
    fi
}

check_port_availability() {
    # Prüft ob die benötigten Ports verfügbar sind
    # $1: Port-Nummer
    # $2: Service-Name
    
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_message "WARN" "SYSTEM" "Port $port ($service_name) ist belegt"
        return 1
    else
        log_message "SUCCESS" "SYSTEM" "Port $port ($service_name) verfügbar"
        return 0
    fi
}

# =============================================================================
# VIRTUAL ENVIRONMENT SETUP
# =============================================================================

setup_virtual_environment() {
    # Erstellt und konfiguriert das Virtual Environment
    
    log_message "INFO" "SYSTEM" "Virtual Environment Setup..."
    
    # Virtual Environment erstellen falls nicht vorhanden
    if [ ! -d "$VENV_PATH" ]; then
        log_message "INFO" "SYSTEM" "Erstelle Virtual Environment..."
        python3 -m venv "$VENV_PATH"
        if [ $? -ne 0 ]; then
            log_message "ERROR" "SYSTEM" "Virtual Environment konnte nicht erstellt werden"
            return 1
        fi
        log_message "SUCCESS" "SYSTEM" "Virtual Environment erstellt"
    else
        log_message "INFO" "SYSTEM" "Virtual Environment bereits vorhanden"
    fi
    
    # Virtual Environment aktivieren
    source "$VENV_PATH/bin/activate"
    if [ $? -ne 0 ]; then
        log_message "ERROR" "SYSTEM" "Virtual Environment konnte nicht aktiviert werden"
        return 1
    fi
    log_message "SUCCESS" "SYSTEM" "Virtual Environment aktiviert"
    
    # Pip upgraden
    log_message "INFO" "SYSTEM" "Upgrade pip..."
    pip install --upgrade pip --quiet
    
    # Backend Dependencies installieren
    log_message "INFO" "BACKEND" "Installiere Backend-Dependencies..."
    cd "$BACKEND_PATH"
    pip install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        log_message "ERROR" "BACKEND" "Backend-Dependencies konnten nicht installiert werden"
        cd ..
        return 1
    fi
    cd ..
    log_message "SUCCESS" "BACKEND" "Backend-Dependencies installiert"
    
    # Frontend Dependencies (Streamlit bereits in requirements.txt falls nötig)
    log_message "INFO" "FRONTEND" "Prüfe Frontend-Dependencies..."
    pip show streamlit >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        log_message "INFO" "FRONTEND" "Installiere Streamlit..."
        pip install streamlit --quiet
    fi
    log_message "SUCCESS" "FRONTEND" "Frontend-Dependencies verfügbar"
    
    return 0
}

# =============================================================================
# SERVICE-START FUNKTIONEN
# =============================================================================

start_backend() {
    # Startet den FastAPI Backend-Server
    
    log_message "INFO" "BACKEND" "Starte FastAPI Backend..."
    
    cd "$BACKEND_PATH"
    
    # Backend im Hintergrund starten
    nohup python -m uvicorn app.main:app --reload --port $BACKEND_PORT --host 127.0.0.1 \
        > "../$LOG_DIR/backend.log" 2>&1 &
    
    local backend_pid=$!
    echo $backend_pid > "../$PID_DIR/backend.pid"
    
    cd ..
    
    # Kurz warten und prüfen ob der Prozess läuft
    sleep 3
    if kill -0 $backend_pid 2>/dev/null; then
        log_message "SUCCESS" "BACKEND" "Backend gestartet (PID: $backend_pid)"
        return 0
    else
        log_message "ERROR" "BACKEND" "Backend konnte nicht gestartet werden"
        return 1
    fi
}

start_frontend() {
    # Startet den Streamlit Frontend-Server
    
    log_message "INFO" "FRONTEND" "Starte Streamlit Frontend..."
    
    cd "$FRONTEND_PATH"
    
    # Frontend im Hintergrund starten (Standard Frontend für Upload-Tests)
    nohup streamlit run streamlit_app.py --server.port $FRONTEND_PORT \
        --server.headless true --server.runOnSave true \
        > "../$LOG_DIR/frontend.log" 2>&1 &
    
    local frontend_pid=$!
    echo $frontend_pid > "../$PID_DIR/frontend.pid"
    
    cd ..
    
    # Kurz warten und prüfen ob der Prozess läuft
    sleep 3
    if kill -0 $frontend_pid 2>/dev/null; then
        log_message "SUCCESS" "FRONTEND" "Frontend gestartet (PID: $frontend_pid)"
        return 0
    else
        log_message "ERROR" "FRONTEND" "Frontend konnte nicht gestartet werden"
        return 1
    fi
}

# =============================================================================
# HEALTH CHECKS
# =============================================================================

wait_for_services() {
    # Wartet bis beide Services verfügbar sind
    
    log_message "INFO" "SYSTEM" "Warte auf Service-Verfügbarkeit..."
    
    # Backend Health Check
    log_message "INFO" "BACKEND" "Health Check..."
    local backend_ready=false
    for i in {1..30}; do
        if curl -s http://127.0.0.1:$BACKEND_PORT/health >/dev/null 2>&1; then
            backend_ready=true
            break
        fi
        sleep 1
    done
    
    if [ "$backend_ready" = true ]; then
        log_message "SUCCESS" "BACKEND" "Backend ist bereit"
    else
        log_message "ERROR" "BACKEND" "Backend Health Check fehlgeschlagen"
        return 1
    fi
    
    # Frontend Health Check
    log_message "INFO" "FRONTEND" "Health Check..."
    local frontend_ready=false
    for i in {1..20}; do
        if curl -s http://127.0.0.1:$FRONTEND_PORT >/dev/null 2>&1; then
            frontend_ready=true
            break
        fi
        sleep 1
    done
    
    if [ "$frontend_ready" = true ]; then
        log_message "SUCCESS" "FRONTEND" "Frontend ist bereit"
    else
        log_message "ERROR" "FRONTEND" "Frontend Health Check fehlgeschlagen"
        return 1
    fi
    
    return 0
}

# =============================================================================
# ZUSAMMENFASSUNG UND HILFE
# =============================================================================

show_startup_summary() {
    # Zeigt eine Zusammenfassung des erfolgreichen Starts
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}🎉 KI-QMS SYSTEM ERFOLGREICH GESTARTET! 🎉${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${WHITE}📊 SYSTEM-STATUS:${NC}"
    echo -e "   ✅ Backend:  http://127.0.0.1:$BACKEND_PORT"
    echo -e "   ✅ Frontend: http://127.0.0.1:$FRONTEND_PORT"
    echo -e "   ✅ API Docs: http://127.0.0.1:$BACKEND_PORT/docs"
    echo ""
    echo -e "${WHITE}📁 WICHTIGE PFADE:${NC}"
    echo -e "   📋 Logs:     $LOG_DIR/"
    echo -e "   🔧 PIDs:     $PID_DIR/"
    echo ""
    echo -e "${WHITE}🔧 NÜTZLICHE BEFEHLE:${NC}"
    echo -e "   🛑 Stoppen:   ./stop-all.sh"
    echo -e "   📊 Status:    ./start-all.sh --status"
    echo -e "   📝 Logs:      tail -f $LOG_DIR/backend.log"
    echo -e "   📝 Logs:      tail -f $LOG_DIR/frontend.log"
    echo ""
    echo -e "${YELLOW}Zum Stoppen: Ctrl+C oder ./stop-all.sh${NC}"
    echo ""
}

show_help() {
    echo -e "${CYAN}KI-QMS System Starter - Hilfe${NC}"
    echo ""
    echo -e "${WHITE}VERWENDUNG:${NC}"
    echo "  ./start-all.sh [OPTIONEN]"
    echo ""
    echo -e "${WHITE}OPTIONEN:${NC}"
    echo "  --help, -h     Zeigt diese Hilfe an"
    echo "  --check, -c    Führt nur System-Checks durch"
    echo "  --status, -s   Zeigt Status der Services"
    echo "  --stop         Stoppt alle Services"
    echo "  --logs         Zeigt Live-Logs"
    echo ""
    echo -e "${WHITE}BESCHREIBUNG:${NC}"
    echo "  Startet das komplette KI-QMS System mit Backend und Frontend."
    echo "  Das Script führt automatisch alle notwendigen Checks durch,"
    echo "  stoppt bestehende Services und startet alles neu."
    echo ""
    echo -e "${WHITE}SERVICES:${NC}"
    echo "  Backend:   FastAPI Server auf Port $BACKEND_PORT"
    echo "  Frontend:  Streamlit App auf Port $FRONTEND_PORT"
    echo ""
    echo -e "${WHITE}DATEIEN:${NC}"
    echo "  Logs:      $LOG_DIR/"
    echo "  PID-Files: $PID_DIR/"
    echo ""
}

check_service_status() {
    # Prüft und zeigt den Status aller Services
    
    echo -e "${CYAN}KI-QMS Service Status${NC}"
    echo ""
    
    # Backend Status
    if [ -f "$PID_DIR/backend.pid" ]; then
        local backend_pid=$(cat "$PID_DIR/backend.pid")
        if kill -0 $backend_pid 2>/dev/null; then
            echo -e "Backend:  ${GREEN}✅ Läuft${NC} (PID: $backend_pid, Port: $BACKEND_PORT)"
        else
            echo -e "Backend:  ${RED}❌ Gestoppt${NC} (Stale PID: $backend_pid)"
        fi
    else
        echo -e "Backend:  ${RED}❌ Nicht gestartet${NC}"
    fi
    
    # Frontend Status
    if [ -f "$PID_DIR/frontend.pid" ]; then
        local frontend_pid=$(cat "$PID_DIR/frontend.pid")
        if kill -0 $frontend_pid 2>/dev/null; then
            echo -e "Frontend: ${GREEN}✅ Läuft${NC} (PID: $frontend_pid, Port: $FRONTEND_PORT)"
        else
            echo -e "Frontend: ${RED}❌ Gestoppt${NC} (Stale PID: $frontend_pid)"
        fi
    else
        echo -e "Frontend: ${RED}❌ Nicht gestartet${NC}"
    fi
    
    echo ""
}

show_logs() {
    # Zeigt Live-Logs beider Services
    
    echo -e "${CYAN}KI-QMS Live Logs (Ctrl+C zum Beenden)${NC}"
    echo ""
    
    if [ -f "$LOG_DIR/backend.log" ] && [ -f "$LOG_DIR/frontend.log" ]; then
        tail -f "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log"
    elif [ -f "$LOG_DIR/backend.log" ]; then
        tail -f "$LOG_DIR/backend.log"
    elif [ -f "$LOG_DIR/frontend.log" ]; then
        tail -f "$LOG_DIR/frontend.log"
    else
        echo "Keine Log-Dateien gefunden."
    fi
}

# =============================================================================
# HAUPTFUNKTION
# =============================================================================

main() {
    # Verarbeite Kommandozeilen-Argumente
    case "${1:-}" in
        "--help"|"-h")
            show_help
            exit 0
            ;;
        "--check"|"-c")
            show_banner
            check_system_requirements
            exit $?
            ;;
        "--status"|"-s")
            check_service_status
            exit 0
            ;;
        "--stop")
            stop_existing_services
            exit 0
            ;;
        "--logs")
            show_logs
            exit 0
            ;;
        "")
            # Normaler Start
            ;;
        *)
            echo "Unbekannte Option: $1"
            echo "Verwenden Sie --help für Hilfe"
            exit 1
            ;;
    esac
    
    # Hauptprogramm
    show_banner
    
    # 1. System-Checks
    if ! check_system_requirements; then
        exit 1
    fi
    
    # 2. Bestehende Services stoppen
    stop_existing_services
    
    # 3. Virtual Environment einrichten
    if ! setup_virtual_environment; then
        exit 1
    fi
    
    # 4. Services starten
    if ! start_backend; then
        log_message "ERROR" "SYSTEM" "Backend-Start fehlgeschlagen"
        exit 1
    fi
    
    if ! start_frontend; then
        log_message "ERROR" "SYSTEM" "Frontend-Start fehlgeschlagen"
        exit 1
    fi
    
    # 5. Health Checks
    if ! wait_for_services; then
        log_message "ERROR" "SYSTEM" "Service Health Checks fehlgeschlagen"
        exit 1
    fi
    
    # 6. Erfolgreiche Zusammenfassung
    show_startup_summary
    
    # 7. Warten auf Ctrl+C
    log_message "INFO" "SYSTEM" "System läuft. Drücken Sie Ctrl+C zum Beenden..."
    
    # Signal Handler für graceful shutdown
    trap 'log_message "INFO" "SYSTEM" "Shutdown angefordert..."; stop_existing_services; exit 0' SIGINT SIGTERM
    
    # Endlos warten
    while true; do
        sleep 1
    done
}

# Script ausführen
main "$@" 