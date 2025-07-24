"""
Debug-Utilities für Visio-Prompts

Debug-Routinen und Audit-Trail-Funktionen für die Visio-Prompt-Verwaltung.

VERSION: v2.1.0 (2025-07-02)
ZIEL: Transparenz und Nachverfolgbarkeit für Audit-Konformität
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class VisioPromptDebugger:
    """
    Debug-Klasse für Visio-Prompt-Verwaltung
    
    Features:
    - Audit-Trail für Prompt-Verwendung
    - Debug-Informationen für Troubleshooting
    - Performance-Monitoring
    - Compliance-Logging
    """
    
    def __init__(self):
        """Initialisiert den Debugger"""
        self.usage_log = []
        self.debug_info = {}
        
    def log_prompt_usage(self, document_type: str, prompt_version: str, 
                        timestamp: str = None, user_id: str = None, 
                        session_id: str = None) -> Dict[str, str]:
        """
        Loggt Prompt-Verwendung für Audit-Trail
        
        Args:
            document_type: Der verwendete Dokumenttyp
            prompt_version: Version des verwendeten Prompts
            timestamp: Zeitstempel (optional, wird automatisch gesetzt)
            user_id: Benutzer-ID (optional)
            session_id: Session-ID (optional)
            
        Returns:
            Dict mit Audit-Informationen
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        audit_entry = {
            "document_type": document_type,
            "prompt_version": prompt_version,
            "timestamp": timestamp,
            "user_id": user_id,
            "session_id": session_id,
            "prompt_file": f"{document_type.lower()}_prompt.py",
            "status": "used"
        }
        
        self.usage_log.append(audit_entry)
        logger.info(f"📋 Prompt-Verwendung geloggt: {document_type} v{prompt_version}")
        
        return audit_entry
    
    def get_prompt_debug_info(self, document_type: str) -> Dict[str, str]:
        """
        Gibt Debug-Informationen für einen Prompt zurück
        
        Args:
            document_type: Der Dokumenttyp
            
        Returns:
            Debug-Informationen
        """
        prompt_file = Path(f"backend/app/visio_prompts/{document_type.lower()}_prompt.py")
        
        debug_info = {
            "document_type": document_type,
            "prompt_file": str(prompt_file),
            "file_exists": prompt_file.exists(),
            "file_size": prompt_file.stat().st_size if prompt_file.exists() else 0,
            "last_modified": datetime.fromtimestamp(prompt_file.stat().st_mtime).isoformat() if prompt_file.exists() else "unknown",
            "timestamp": datetime.now().isoformat(),
            "status": "active" if prompt_file.exists() else "missing"
        }
        
        # Versuche Version aus Datei zu extrahieren
        if prompt_file.exists():
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'VERSION_' in content:
                        # Einfache Version-Extraktion
                        lines = content.split('\n')
                        for line in lines:
                            if line.strip().startswith('VERSION_'):
                                version = line.split('=')[1].strip().strip('"\'')
                                debug_info["version"] = version
                                break
                    else:
                        debug_info["version"] = "unknown"
                        
                    debug_info["prompt_length"] = len(content)
            except Exception as e:
                debug_info["error"] = str(e)
                debug_info["version"] = "error"
                debug_info["prompt_length"] = 0
        
        return debug_info
    
    def get_usage_statistics(self) -> Dict[str, any]:
        """
        Gibt Statistiken über Prompt-Verwendung zurück
        
        Returns:
            Dict mit Verwendungsstatistiken
        """
        if not self.usage_log:
            return {"total_usage": 0, "document_types": {}, "recent_usage": []}
        
        # Zähle Verwendung pro Dokumenttyp
        doc_type_counts = {}
        for entry in self.usage_log:
            doc_type = entry["document_type"]
            doc_type_counts[doc_type] = doc_type_counts.get(doc_type, 0) + 1
        
        # Letzte 10 Verwendungen
        recent_usage = self.usage_log[-10:] if len(self.usage_log) > 10 else self.usage_log
        
        return {
            "total_usage": len(self.usage_log),
            "document_types": doc_type_counts,
            "recent_usage": recent_usage,
            "first_usage": self.usage_log[0] if self.usage_log else None,
            "last_usage": self.usage_log[-1] if self.usage_log else None
        }
    
    def export_audit_trail(self, filename: str = None) -> str:
        """
        Exportiert den Audit-Trail in eine JSON-Datei
        
        Args:
            filename: Dateiname (optional)
            
        Returns:
            Pfad zur exportierten Datei
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"visio_prompts_audit_trail_{timestamp}.json"
        
        audit_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_entries": len(self.usage_log),
            "usage_log": self.usage_log,
            "statistics": self.get_usage_statistics()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Audit-Trail exportiert: {filename}")
        return filename
    
    def validate_prompt_files(self) -> Dict[str, bool]:
        """
        Validiert alle Prompt-Dateien auf Vollständigkeit
        
        Returns:
            Dict mit Validierungsergebnissen
        """
        expected_files = [
            "qm_manual_prompt.py", "sop_prompt.py", "work_instruction_prompt.py",
            "form_prompt.py", "user_manual_prompt.py", "service_manual_prompt.py",
            "risk_assessment_prompt.py", "validation_protocol_prompt.py",
            "calibration_procedure_prompt.py", "audit_report_prompt.py",
            "capa_document_prompt.py", "training_material_prompt.py",
            "specification_prompt.py", "standard_norm_prompt.py",
            "regulation_prompt.py", "guidance_document_prompt.py",
            "process_prompt.py", "prompt_test_prompt.py", "other_prompt.py"
        ]
        
        results = {}
        prompt_dir = Path("backend/app/visio_prompts")
        
        for filename in expected_files:
            file_path = prompt_dir / filename
            exists = file_path.exists()
            results[filename] = exists
            
            if not exists:
                logger.warning(f"⚠️ Fehlende Prompt-Datei: {filename}")
            else:
                # Prüfe auf VERSION_ und PROMPT_ Variablen
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        has_version = 'VERSION_' in content
                        has_prompt = 'PROMPT_' in content
                        results[f"{filename}_valid"] = has_version and has_prompt
                        
                        if not has_version or not has_prompt:
                            logger.warning(f"⚠️ Ungültige Prompt-Datei: {filename}")
                except Exception as e:
                    results[f"{filename}_valid"] = False
                    logger.error(f"❌ Fehler beim Lesen von {filename}: {e}")
        
        return results

# Globale Debugger-Instanz
visio_prompt_debugger = VisioPromptDebugger()

# =============================================================================
# 📋 HILFSFUNKTIONEN
# =============================================================================

def log_prompt_usage(document_type: str, prompt_version: str, 
                    timestamp: str = None, user_id: str = None, 
                    session_id: str = None) -> Dict[str, str]:
    """
    Hilfsfunktion: Loggt Prompt-Verwendung
    
    Args:
        document_type: Der verwendete Dokumenttyp
        prompt_version: Version des verwendeten Prompts
        timestamp: Zeitstempel (optional)
        user_id: Benutzer-ID (optional)
        session_id: Session-ID (optional)
        
    Returns:
        Dict mit Audit-Informationen
    """
    return visio_prompt_debugger.log_prompt_usage(
        document_type, prompt_version, timestamp, user_id, session_id
    )

def get_prompt_debug_info(document_type: str) -> Dict[str, str]:
    """
    Hilfsfunktion: Gibt Debug-Informationen zurück
    
    Args:
        document_type: Der Dokumenttyp
        
    Returns:
        Debug-Informationen
    """
    return visio_prompt_debugger.get_prompt_debug_info(document_type)

def get_usage_statistics() -> Dict[str, any]:
    """
    Hilfsfunktion: Gibt Verwendungsstatistiken zurück
    
    Returns:
        Dict mit Verwendungsstatistiken
    """
    return visio_prompt_debugger.get_usage_statistics()

def export_audit_trail(filename: str = None) -> str:
    """
    Hilfsfunktion: Exportiert Audit-Trail
    
    Args:
        filename: Dateiname (optional)
        
    Returns:
        Pfad zur exportierten Datei
    """
    return visio_prompt_debugger.export_audit_trail(filename)

def validate_prompt_files() -> Dict[str, bool]:
    """
    Hilfsfunktion: Validiert alle Prompt-Dateien
    
    Returns:
        Dict mit Validierungsergebnissen
    """
    return visio_prompt_debugger.validate_prompt_files()

# =============================================================================
# 🧪 INITIALISIERUNG & VALIDIERUNG
# =============================================================================

def initialize_debugger():
    """Initialisiert den Debugger beim Start"""
    logger.info("🔄 Initialisiere Visio-Prompt-Debugger...")
    
    # Validiere alle Prompt-Dateien
    validation_results = validate_prompt_files()
    valid_count = sum(1 for k, v in validation_results.items() 
                     if k.endswith('_valid') and v)
    total_count = len([k for k in validation_results.keys() 
                      if k.endswith('_valid')])
    
    if valid_count == total_count:
        logger.info(f"✅ Alle {total_count} Prompt-Dateien erfolgreich validiert")
    else:
        logger.error(f"❌ {total_count - valid_count} von {total_count} Prompt-Dateien haben Probleme")
    
    return validation_results

# Automatische Initialisierung beim Import
if __name__ != "__main__":
    initialize_debugger() 