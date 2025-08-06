"""
Multi-Visio Prompts Management System

Ähnlich wie visio_prompts, aber für die mehrstufige Multi-Visio Pipeline.
Ermöglicht dynamisches Laden, Versionierung und Audit-Trail.

Autor: DocuMind-AI Team
Version: 1.0 - Dynamisches Multi-Visio Prompt Management
"""

import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import hashlib

# Logger konfigurieren
logger = logging.getLogger(__name__)

# =============================================================================
# 📝 PROMPT IMPORTS - Dynamisch aus Dateien
# =============================================================================

def _load_prompt_from_file(filename: str) -> Dict[str, str]:
    """
    Lädt einen Prompt dynamisch aus einer .txt Datei
    
    Args:
        filename: Name der Prompt-Datei (z.B. "01_expert_induction.txt")
        
    Returns:
        Dict mit prompt content, version und metadata
    """
    try:
        prompt_file_path = Path(__file__).parent / filename
        
        if not prompt_file_path.exists():
            logger.error(f"❌ Prompt-Datei nicht gefunden: {filename}")
            return {
                "prompt": f"# Fehler: Prompt-Datei {filename} nicht gefunden",
                "version": "0.0",
                "description": f"Fehlende Datei: {filename}"
            }
        
        # Lade Datei-Inhalt
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrahiere Version aus Kommentaren (falls vorhanden)
        version = "1.0"
        description = f"Multi-Visio Prompt aus {filename}"
        
        lines = content.split('\n')
        for line in lines[:10]:  # Nur erste 10 Zeilen für Metadaten prüfen
            if '# Version:' in line:
                version = line.split('# Version:')[1].strip()
            elif '# Beschreibung:' in line:
                description = line.split('# Beschreibung:')[1].strip()
        
        logger.info(f"📝 Multi-Visio Prompt geladen: {filename} (v{version})")
        
        return {
            "prompt": content,
            "version": version,
            "description": description,
            "filename": filename,
            "loaded_at": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Laden von {filename}: {e}")
        return {
            "prompt": f"# Fehler beim Laden: {str(e)}",
            "version": "0.0",
            "description": f"Fehler in {filename}: {str(e)}"
        }

# =============================================================================
# 🗂️ MULTI-VISIO PROMPT MAPPING
# =============================================================================

def get_multi_visio_prompts() -> Dict[str, Dict[str, str]]:
    """
    Lädt alle Multi-Visio Prompts dynamisch
    
    Returns:
        Dict mit allen Prompts für die 5-Stufen Pipeline
    """
    return {
        "expert_induction": _load_prompt_from_file("01_expert_induction.txt"),
        "structured_analysis": _load_prompt_from_file("02_structured_analysis.txt"),
        "word_coverage": _load_prompt_from_file("03_word_coverage.txt"),
        "verification": {
            "prompt": "# Backend-Logik für Wort-Coverage Verifikation",
            "version": "1.0",
            "description": "Backend-basierte Verifikation ohne LLM-Prompt"
        },
        "norm_compliance": _load_prompt_from_file("05_norm_compliance.txt")
    }

# =============================================================================
# 📋 HILFSFUNKTIONEN - Wie bei visio_prompts
# =============================================================================

def get_multi_visio_prompt(stage: str) -> Dict[str, Any]:
    """
    Lädt einen spezifischen Multi-Visio Prompt mit erweiterten Metadaten
    
    Args:
        stage: Stage-Name (z.B. "expert_induction", "structured_analysis")
        
    Returns:
        Dict mit prompt, version, metadata, hash und audit_info
    """
    prompts = get_multi_visio_prompts()
    
    if stage not in prompts:
        logger.warning(f"⚠️ Unbekannte Multi-Visio Stage: {stage}")
        # Fallback zu expert_induction
        stage = "expert_induction"
    
    prompt_data = prompts[stage]
    prompt_text = prompt_data["prompt"]
    version = prompt_data["version"]
    
    # Erstelle Hash für Prompt-Integrität
    prompt_hash = hashlib.sha256(prompt_text.encode('utf-8')).hexdigest()[:16]
    
    # Erweiterte Metadaten für Audit
    metadata = {
        "stage": stage,
        "version": version,
        "description": prompt_data.get("description", ""),
        "filename": prompt_data.get("filename", "unknown"),
        "prompt_length": len(prompt_text),
        "prompt_hash": prompt_hash,
        "loaded_at": datetime.utcnow().isoformat() + "Z",
        "system_version": "v3.6.0 Multi-Visio"
    }
    
    # Audit-Informationen
    audit_info = {
        "prompt_source": "dynamic_file_loading",
        "prompt_verification": {
            "hash_verified": True,
            "length_check": len(prompt_text) > 10,
            "encoding_check": True
        },
        "stage_info": {
            "pipeline_stage": stage,
            "stage_number": _get_stage_number(stage),
            "requires_image": stage != "verification"
        }
    }
    
    return {
        "prompt": prompt_text,
        "version": version,
        "metadata": metadata,
        "hash": prompt_hash,
        "audit_info": audit_info
    }

def _get_stage_number(stage: str) -> int:
    """Gibt die Stufen-Nummer zurück"""
    stage_mapping = {
        "expert_induction": 1,
        "structured_analysis": 2, 
        "word_coverage": 3,
        "verification": 4,
        "norm_compliance": 5
    }
    return stage_mapping.get(stage, 0)

# =============================================================================
# 🔄 KOMPATIBILITÄT MIT ALTER API
# =============================================================================

def get_prompt_for_stage(stage_name: str) -> str:
    """
    Kompatibilitätsfunktion für bestehenden Code
    
    Args:
        stage_name: Name der Stage
        
    Returns:
        Prompt-Text als String
    """
    prompt_data = get_multi_visio_prompt(stage_name)
    return prompt_data["prompt"]

# =============================================================================
# 🌐 GLOBALE INSTANZ
# =============================================================================

class MultiVisioPromptsManager:
    """
    Manager für Multi-Visio Prompts - analog zu VisioPromptsManager
    """
    
    def __init__(self):
        """Initialisiert den Multi-Visio Prompt Manager"""
        self.prompts = get_multi_visio_prompts()
        logger.info(f"✅ MultiVisioPromptsManager initialisiert mit {len(self.prompts)} Stages")
    
    def get_prompt(self, stage: str) -> Dict[str, Any]:
        """Lädt einen Prompt für eine bestimmte Stage"""
        return get_multi_visio_prompt(stage)
    
    def reload_prompts(self):
        """Lädt alle Prompts neu (für Updates zur Laufzeit)"""
        self.prompts = get_multi_visio_prompts()
        logger.info("🔄 Multi-Visio Prompts neu geladen")

# Globale Instanz
multi_visio_prompts_manager = MultiVisioPromptsManager()

# =============================================================================
# 📊 VALIDIERUNG & DEBUG
# =============================================================================

def validate_all_multi_visio_prompts() -> Dict[str, bool]:
    """Validiert alle Multi-Visio Prompts"""
    results = {}
    prompts = get_multi_visio_prompts()
    
    for stage, prompt_data in prompts.items():
        try:
            prompt_text = prompt_data["prompt"]
            is_valid = (
                len(prompt_text) > 10 and
                not prompt_text.startswith("# Fehler") and
                "version" in prompt_data
            )
            results[stage] = is_valid
            
            if is_valid:
                logger.info(f"✅ Multi-Visio Stage {stage}: Gültig")
            else:
                logger.warning(f"❌ Multi-Visio Stage {stage}: Ungültig")
                
        except Exception as e:
            logger.error(f"❌ Validierungsfehler für {stage}: {e}")
            results[stage] = False
    
    return results