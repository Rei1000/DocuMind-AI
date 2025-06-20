#!/bin/bash

# =============================================================================
# KI-QMS System Stopper v1.0
# =============================================================================
# Stoppt alle KI-QMS Services sauber und führt Cleanup durch
#
# Autor: KI-QMS Team
# Datum: $(date +"%Y-%m-%d")
# =============================================================================

# Farbdefinitionen
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
readonly LOG_DIR="./logs"
readonly PID_DIR="./pids"

# =============================================================================
# LOGGING UND BANNER
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
    
    local color=$WHITE
    case $level in
        "INFO")    color=$BLUE ;;
        "SUCCESS") color=$GREEN ;;
        "WARN")    color=$YELLOW ;;
        "ERROR")   color=$RED ;;
    esac
    
    echo -e "${color}[$timestamp] [$level] [$component] $message${NC}"
    echo "[$timestamp] [$level] [$component] $message" >> "$LOG_DIR/shutdown.log"
}

show_banner() {
    clear
    echo -e "${RED}"
    echo "╔═══════════════════════════════════════════════════════════════════════╗"
    echo "║                        🛑 KI-QMS SYSTEM STOPPER                       ║"
    echo "║                   Graceful Shutdown & Cleanup                        ║"
    echo "║                                                                       ║"
    echo "║  Stoppt alle Services sauber und führt Systembereinigung durch       ║"
    echo "╚═══════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${WHITE}🕐 Shutdown-Zeit: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo ""
}

# =============================================================================
# SERVICE-ERKENNUNG UND STOP
# =============================================================================

check_running_services() {
    # Überprüft welche Services aktuell laufen
    
    log_message "INFO" "SYSTEM" "Prüfe laufende Services..."
    local services_found=0
    
    # Backend prüfen
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_message "INFO" "BACKEND" "Backend läuft auf Port $BACKEND_PORT"
        services_found=$((services_found + 1))
    fi
    
    # Frontend prüfen
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_message "INFO" "FRONTEND" "Frontend läuft auf Port $FRONTEND_PORT"
        services_found=$((services_found + 1))
    fi
    
    # PID-Dateien prüfen
    if [ -f "$PID_DIR/backend.pid" ]; then
        local backend_pid=$(cat "$PID_DIR/backend.pid")
        if kill -0 $backend_pid 2>/dev/null; then
            log_message "INFO" "BACKEND" "Backend-Prozess gefunden (PID: $backend_pid)"
        fi
    fi
    
    if [ -f "$PID_DIR/frontend.pid" ]; then
        local frontend_pid=$(cat "$PID_DIR/frontend.pid")
        if kill -0 $frontend_pid 2>/dev/null; then
            log_message "INFO" "FRONTEND" "Frontend-Prozess gefunden (PID: $frontend_pid)"
        fi
    fi
    
    return $services_found
}

stop_backend() {
    # Stoppt den FastAPI Backend-Server
    # $1: optional "force" für sofortigen Kill
    
    local force_mode=${1:-""}
    log_message "INFO" "BACKEND" "Stoppe Backend-Service..."
    
    local stopped=false
    
    # Versuche über PID-Datei zu stoppen
    if [ -f "$PID_DIR/backend.pid" ]; then
        local backend_pid=$(cat "$PID_DIR/backend.pid")
        if kill -0 $backend_pid 2>/dev/null; then
            if [ "$force_mode" = "force" ]; then
                kill -9 $backend_pid 2>/dev/null
                log_message "WARN" "BACKEND" "Forceful kill durchgeführt (PID: $backend_pid)"
            else
                kill -TERM $backend_pid 2>/dev/null
                log_message "INFO" "BACKEND" "SIGTERM gesendet (PID: $backend_pid)"
                
                # Warte auf graceful shutdown
                for i in {1..10}; do
                    if ! kill -0 $backend_pid 2>/dev/null; then
                        stopped=true
                        break
                    fi
                    sleep 1
                done
                
                # Falls graceful nicht funktioniert, force kill
                if ! $stopped; then
                    kill -9 $backend_pid 2>/dev/null
                    log_message "WARN" "BACKEND" "Graceful shutdown timeout - forceful kill"
                fi
            fi
            stopped=true
        fi
        rm -f "$PID_DIR/backend.pid"
    fi
    
    # Fallback: Stoppe über Port
    local backend_pids=$(lsof -ti:$BACKEND_PORT 2>/dev/null)
    if [ ! -z "$backend_pids" ]; then
        echo "$backend_pids" | xargs kill -TERM 2>/dev/null
        sleep 2
        backend_pids=$(lsof -ti:$BACKEND_PORT 2>/dev/null)
        if [ ! -z "$backend_pids" ]; then
            echo "$backend_pids" | xargs kill -9 2>/dev/null
            log_message "WARN" "BACKEND" "Port-basierter forceful kill"
        fi
        stopped=true
    fi
    
    if $stopped; then
        log_message "SUCCESS" "BACKEND" "Backend gestoppt"
        return 0
    else
        log_message "INFO" "BACKEND" "Kein Backend-Prozess gefunden"
        return 1
    fi
}

stop_frontend() {
    # Stoppt den Streamlit Frontend-Server
    # $1: optional "force" für sofortigen Kill
    
    local force_mode=${1:-""}
    log_message "INFO" "FRONTEND" "Stoppe Frontend-Service..."
    
    local stopped=false
    
    # Versuche über PID-Datei zu stoppen
    if [ -f "$PID_DIR/frontend.pid" ]; then
        local frontend_pid=$(cat "$PID_DIR/frontend.pid")
        if kill -0 $frontend_pid 2>/dev/null; then
            if [ "$force_mode" = "force" ]; then
                kill -9 $frontend_pid 2>/dev/null
                log_message "WARN" "FRONTEND" "Forceful kill durchgeführt (PID: $frontend_pid)"
            else
                kill -TERM $frontend_pid 2>/dev/null
                log_message "INFO" "FRONTEND" "SIGTERM gesendet (PID: $frontend_pid)"
                
                # Warte auf graceful shutdown
                for i in {1..10}; do
                    if ! kill -0 $frontend_pid 2>/dev/null; then
                        stopped=true
                        break
                    fi
                    sleep 1
                done
                
                # Falls graceful nicht funktioniert, force kill
                if ! $stopped; then
                    kill -9 $frontend_pid 2>/dev/null
                    log_message "WARN" "FRONTEND" "Graceful shutdown timeout - forceful kill"
                fi
            fi
            stopped=true
        fi
        rm -f "$PID_DIR/frontend.pid"
    fi
    
    # Fallback: Stoppe über Port
    local frontend_pids=$(lsof -ti:$FRONTEND_PORT 2>/dev/null)
    if [ ! -z "$frontend_pids" ]; then
        echo "$frontend_pids" | xargs kill -TERM 2>/dev/null
        sleep 2
        frontend_pids=$(lsof -ti:$FRONTEND_PORT 2>/dev/null)
        if [ ! -z "$frontend_pids" ]; then
            echo "$frontend_pids" | xargs kill -9 2>/dev/null
            log_message "WARN" "FRONTEND" "Port-basierter forceful kill"
        fi
        stopped=true
    fi
    
    if $stopped; then
        log_message "SUCCESS" "FRONTEND" "Frontend gestoppt"
        return 0
    else
        log_message "INFO" "FRONTEND" "Kein Frontend-Prozess gefunden"
        return 1
    fi
}

# =============================================================================
# CLEANUP FUNKTIONEN
# =============================================================================

cleanup_resources() {
    # Bereinigt temporäre Dateien und Ressourcen
    # $1: optional "deep" für tiefere Bereinigung
    
    local clean_mode=${1:-""}
    log_message "INFO" "SYSTEM" "Bereinige Ressourcen..."
    
    # PID-Dateien entfernen
    if [ -d "$PID_DIR" ]; then
        rm -f "$PID_DIR"/*.pid
        log_message "SUCCESS" "SYSTEM" "PID-Dateien entfernt"
    fi
    
    # Temporäre Dateien entfernen
    rm -f nohup.out
    rm -f ./*.tmp
    
    # Bei tieferer Bereinigung
    if [ "$clean_mode" = "deep" ]; then
        log_message "INFO" "SYSTEM" "Führe tiefe Bereinigung durch..."
        
        # Alte Log-Dateien archivieren
        if [ -d "$LOG_DIR" ]; then
            local archive_dir="$LOG_DIR/archive/$(date +%Y%m%d_%H%M%S)"
            mkdir -p "$archive_dir"
            mv "$LOG_DIR"/*.log "$archive_dir/" 2>/dev/null
            log_message "SUCCESS" "SYSTEM" "Logs archiviert: $archive_dir"
        fi
        
        # Python Cache bereinigen
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
        find . -name "*.pyc" -delete 2>/dev/null
        log_message "SUCCESS" "SYSTEM" "Python Cache bereinigt"
        
        # Streamlit Cache bereinigen
        rm -rf ~/.streamlit 2>/dev/null
    fi
    
    log_message "SUCCESS" "SYSTEM" "Ressourcen-Cleanup abgeschlossen"
}

verify_shutdown() {
    # Verifiziert dass alle Services gestoppt wurden
    
    log_message "INFO" "SYSTEM" "Verifiziere Shutdown..."
    local remaining_services=0
    
    # Port-Checks
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_message "ERROR" "BACKEND" "Backend läuft noch auf Port $BACKEND_PORT"
        remaining_services=$((remaining_services + 1))
    fi
    
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_message "ERROR" "FRONTEND" "Frontend läuft noch auf Port $FRONTEND_PORT"
        remaining_services=$((remaining_services + 1))
    fi
    
    # Prozess-Checks über PID-Dateien
    if [ -f "$PID_DIR/backend.pid" ]; then
        local backend_pid=$(cat "$PID_DIR/backend.pid")
        if kill -0 $backend_pid 2>/dev/null; then
            log_message "ERROR" "BACKEND" "Backend-Prozess läuft noch (PID: $backend_pid)"
            remaining_services=$((remaining_services + 1))
        fi
    fi
    
    if [ -f "$PID_DIR/frontend.pid" ]; then
        local frontend_pid=$(cat "$PID_DIR/frontend.pid")
        if kill -0 $frontend_pid 2>/dev/null; then
            log_message "ERROR" "FRONTEND" "Frontend-Prozess läuft noch (PID: $frontend_pid)"
            remaining_services=$((remaining_services + 1))
        fi
    fi
    
    if [ $remaining_services -eq 0 ]; then
        log_message "SUCCESS" "SYSTEM" "Alle Services erfolgreich gestoppt"
        return 0
    else
        log_message "ERROR" "SYSTEM" "$remaining_services Service(s) laufen noch"
        return 1
    fi
}

# =============================================================================
# ZUSAMMENFASSUNG UND HILFE
# =============================================================================

show_shutdown_summary() {
    # Zeigt Zusammenfassung des Shutdown-Prozesses
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ KI-QMS SYSTEM ERFOLGREICH GESTOPPT ✅${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${WHITE}📊 SHUTDOWN-STATUS:${NC}"
    echo -e "   ✅ Backend gestoppt (Port $BACKEND_PORT frei)"
    echo -e "   ✅ Frontend gestoppt (Port $FRONTEND_PORT frei)"
    echo -e "   ✅ Ressourcen bereinigt"
    echo ""
    echo -e "${WHITE}📁 VERBLEIBENDE DATEIEN:${NC}"
    echo -e "   📋 Logs:     $LOG_DIR/"
    echo -e "   💾 Daten:    backend/qms_mvp.db"
    echo ""
    echo -e "${WHITE}🔧 NÄCHSTE SCHRITTE:${NC}"
    echo -e "   🚀 Neustarten: ./start-all.sh"
    echo -e "   📊 Status:     ./start-all.sh --status"
    echo -e "   📝 Logs:       ls -la $LOG_DIR/"
    echo ""
    echo -e "${CYAN}System ist bereit für Neustart oder Wartung.${NC}"
    echo ""
}

show_help() {
    echo -e "${CYAN}KI-QMS System Stopper - Hilfe${NC}"
    echo ""
    echo -e "${WHITE}VERWENDUNG:${NC}"
    echo "  ./stop-all.sh [OPTIONEN]"
    echo ""
    echo -e "${WHITE}OPTIONEN:${NC}"
    echo "  --help, -h     Zeigt diese Hilfe an"
    echo "  --force, -f    Erzwingt sofortigen Kill (kein graceful shutdown)"
    echo "  --clean, -c    Führt tiefe Bereinigung durch (Archive, Cache)"
    echo "  --status, -s   Zeigt nur Status ohne zu stoppen"
    echo ""
    echo -e "${WHITE}BESCHREIBUNG:${NC}"
    echo "  Stoppt alle KI-QMS Services sauber und führt Cleanup durch."
    echo "  Versucht zuerst graceful shutdown, dann forceful kill falls nötig."
    echo ""
    echo -e "${WHITE}SERVICES:${NC}"
    echo "  Backend:   FastAPI Server auf Port $BACKEND_PORT"
    echo "  Frontend:  Streamlit App auf Port $FRONTEND_PORT"
    echo ""
    echo -e "${WHITE}BEISPIELE:${NC}"
    echo "  ./stop-all.sh              # Normaler Stopp"
    echo "  ./stop-all.sh --force      # Sofortiger Kill"
    echo "  ./stop-all.sh --clean      # Mit tiefem Cleanup"
    echo ""
}

show_status() {
    # Zeigt nur Status ohne zu stoppen
    
    echo -e "${CYAN}KI-QMS Service Status${NC}"
    echo ""
    
    local services_running=0
    
    # Backend Status
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "Backend:  ${GREEN}✅ Läuft${NC} (Port: $BACKEND_PORT)"
        services_running=$((services_running + 1))
    else
        echo -e "Backend:  ${RED}❌ Gestoppt${NC}"
    fi
    
    # Frontend Status
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "Frontend: ${GREEN}✅ Läuft${NC} (Port: $FRONTEND_PORT)"
        services_running=$((services_running + 1))
    else
        echo -e "Frontend: ${RED}❌ Gestoppt${NC}"
    fi
    
    echo ""
    if [ $services_running -gt 0 ]; then
        echo -e "${YELLOW}$services_running Service(s) laufen - verwenden Sie ./stop-all.sh zum Stoppen${NC}"
    else
        echo -e "${GREEN}Keine Services laufen - System ist gestoppt${NC}"
    fi
    echo ""
}

# =============================================================================
# HAUPTFUNKTION
# =============================================================================

main() {
    local force_mode=""
    local clean_mode=""
    
    # Verarbeite Kommandozeilen-Argumente
    case "${1:-}" in
        "--help"|"-h")
            show_help
            exit 0
            ;;
        "--status"|"-s")
            show_status
            exit 0
            ;;
        "--force"|"-f")
            force_mode="force"
            ;;
        "--clean"|"-c")
            clean_mode="deep"
            ;;
        "")
            # Normaler Stop
            ;;
        *)
            echo "Unbekannte Option: $1"
            echo "Verwenden Sie --help für Hilfe"
            exit 1
            ;;
    esac
    
    # Hauptprogramm
    show_banner
    
    # 1. Services prüfen
    check_running_services
    local services_count=$?
    
    if [ $services_count -eq 0 ]; then
        log_message "INFO" "SYSTEM" "Keine laufenden Services gefunden"
        cleanup_resources "$clean_mode"
        echo -e "${GREEN}System ist bereits gestoppt.${NC}"
        exit 0
    fi
    
    # 2. Services stoppen
    stop_backend "$force_mode"
    stop_frontend "$force_mode"
    
    # 3. Cleanup
    cleanup_resources "$clean_mode"
    
    # 4. Verifizierung
    if verify_shutdown; then
        show_shutdown_summary
        exit 0
    else
        log_message "ERROR" "SYSTEM" "Shutdown nicht vollständig - manuelle Überprüfung nötig"
        exit 1
    fi
}

# Script ausführen
main "$@" 