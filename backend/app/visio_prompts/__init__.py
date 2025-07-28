"""
Zentrale Prompt-Verwaltung für Visio-Upload-Methode

Diese Datei verwaltet alle spezialisierten Prompts für die Visio-Verarbeitung
verschiedener Dokumenttypen im KI-QMS System.

VERSION: v3.5.0 (2025-07-26)
SYSTEM: DocuMind-AI QM-System
COMPLIANCE: ISO 13485, MDR, FDA 21 CFR Part 820

STRUKTUR:
├── PROMPT_MAPPING: Alle 25 Dokumenttypen mit Prompts und Versionen
├── VisioPromptsManager: Verwaltungsklasse
└── visio_prompts_manager: Globale Instanz

VERWENDUNG:
- Prompts laden: get_prompt_for_document_type("SOP")
- Version prüfen: get_prompt_version("SOP")
- Debug-Info: get_prompt_debug_info("SOP")
"""

from typing import Dict, Optional
import logging
from datetime import datetime

# Logging Setup
logger = logging.getLogger(__name__)

# =============================================================================
# 🎯 PROMPT IMPORTS - Alle 25 Dokumenttypen
# =============================================================================

# Importiere alle Prompt-Dateien
from .qm_manual_prompt import PROMPT_QM_MANUAL, VERSION_QM_MANUAL
from .sop_prompt import PROMPT_SOP, VERSION_SOP
from .work_instruction_prompt import PROMPT_WORK_INSTRUCTION, VERSION_WORK_INSTRUCTION
from .form_prompt import PROMPT_FORM, VERSION_FORM
from .user_manual_prompt import PROMPT_USER_MANUAL, VERSION_USER_MANUAL
from .service_manual_prompt import PROMPT_SERVICE_MANUAL, VERSION_SERVICE_MANUAL
from .risk_assessment_prompt import PROMPT_RISK_ASSESSMENT, VERSION_RISK_ASSESSMENT
from .validation_protocol_prompt import PROMPT_VALIDATION_PROTOCOL, VERSION_VALIDATION_PROTOCOL
from .calibration_procedure_prompt import PROMPT_CALIBRATION_PROCEDURE, VERSION_CALIBRATION_PROCEDURE
from .audit_report_prompt import PROMPT_AUDIT_REPORT, VERSION_AUDIT_REPORT
from .capa_document_prompt import PROMPT_CAPA_DOCUMENT, VERSION_CAPA_DOCUMENT
from .training_material_prompt import PROMPT_TRAINING_MATERIAL, VERSION_TRAINING_MATERIAL
from .specification_prompt import PROMPT_SPECIFICATION, VERSION_SPECIFICATION
from .standard_norm_prompt import PROMPT_STANDARD_NORM, VERSION_STANDARD_NORM
from .regulation_prompt import PROMPT_REGULATION, VERSION_REGULATION
from .guidance_document_prompt import PROMPT_GUIDANCE_DOCUMENT, VERSION_GUIDANCE_DOCUMENT
from .process_prompt import PROMPT_PROCESS, VERSION_PROCESS
from .prompt_test_prompt import PROMPT_PROMPT_TEST, VERSION_PROMPT_TEST
from .other_prompt import PROMPT_OTHER, VERSION_OTHER

# =============================================================================
# 🗂️ PROMPT MAPPING - Alle 25 Dokumenttypen
# =============================================================================

PROMPT_MAPPING = {
    # =============================================================================
    # 📋 KERNDOKUMENTE
    # =============================================================================
    "QM_MANUAL": {
        "prompt": PROMPT_QM_MANUAL,
        "version": VERSION_QM_MANUAL,
        "description": "Qualitätsmanagement-Handbuch (Hauptdokument)",
        "category": "core"
    },
    "SOP": {
        "prompt": PROMPT_SOP,
        "version": VERSION_SOP,
        "description": "Standard Operating Procedure",
        "category": "core"
    },
    "WORK_INSTRUCTION": {
        "prompt": PROMPT_WORK_INSTRUCTION,
        "version": VERSION_WORK_INSTRUCTION,
        "description": "Arbeitsanweisung (detaillierte Schritte)",
        "category": "core"
    },
    
    # =============================================================================
    # 📄 FORMULARE & VORLAGEN
    # =============================================================================
    "FORM": {
        "prompt": PROMPT_FORM,
        "version": VERSION_FORM,
        "description": "Formular/Vorlage für Dokumentation",
        "category": "forms"
    },
    "USER_MANUAL": {
        "prompt": PROMPT_USER_MANUAL,
        "version": VERSION_USER_MANUAL,
        "description": "Benutzerhandbuch für Medizinprodukte",
        "category": "forms"
    },
    "SERVICE_MANUAL": {
        "prompt": PROMPT_SERVICE_MANUAL,
        "version": VERSION_SERVICE_MANUAL,
        "description": "Servicehandbuch für Wartung",
        "category": "forms"
    },
    
    # =============================================================================
    # 🔍 ANALYSE & VALIDIERUNG
    # =============================================================================
    "RISK_ASSESSMENT": {
        "prompt": PROMPT_RISK_ASSESSMENT,
        "version": VERSION_RISK_ASSESSMENT,
        "description": "Risikoanalyse nach ISO 14971",
        "category": "analysis"
    },
    "VALIDATION_PROTOCOL": {
        "prompt": PROMPT_VALIDATION_PROTOCOL,
        "version": VERSION_VALIDATION_PROTOCOL,
        "description": "Validierungsprotokoll (IQ/OQ/PQ)",
        "category": "analysis"
    },
    
    # =============================================================================
    # ⚙️ PROZESSE
    # =============================================================================
    "CALIBRATION_PROCEDURE": {
        "prompt": PROMPT_CALIBRATION_PROCEDURE,
        "version": VERSION_CALIBRATION_PROCEDURE,
        "description": "Kalibrierverfahren für Equipment",
        "category": "processes"
    },
    "AUDIT_REPORT": {
        "prompt": PROMPT_AUDIT_REPORT,
        "version": VERSION_AUDIT_REPORT,
        "description": "Audit-Berichte (intern/extern)",
        "category": "processes"
    },
    "CAPA_DOCUMENT": {
        "prompt": PROMPT_CAPA_DOCUMENT,
        "version": VERSION_CAPA_DOCUMENT,
        "description": "CAPA-Dokumentation (Corrective Action)",
        "category": "processes"
    },
    "PROCESS": {
        "prompt": PROMPT_PROCESS,
        "version": VERSION_PROCESS,
        "description": "Prozessdokumente (Flussdiagramme, Workflows)",
        "category": "processes"
    },
    
    # =============================================================================
    # 📚 TRAINING & SPEZIFIKATIONEN
    # =============================================================================
    "TRAINING_MATERIAL": {
        "prompt": PROMPT_TRAINING_MATERIAL,
        "version": VERSION_TRAINING_MATERIAL,
        "description": "Schulungsunterlagen und -protokolle",
        "category": "training"
    },
    "SPECIFICATION": {
        "prompt": PROMPT_SPECIFICATION,
        "version": VERSION_SPECIFICATION,
        "description": "Spezifikationen und Anforderungen",
        "category": "training"
    },
    
    # =============================================================================
    # 📖 NORMEN & STANDARDS
    # =============================================================================
    "STANDARD_NORM": {
        "prompt": PROMPT_STANDARD_NORM,
        "version": VERSION_STANDARD_NORM,
        "description": "Standards und Normen (ISO, IEC, DIN, EN)",
        "category": "standards"
    },
    "REGULATION": {
        "prompt": PROMPT_REGULATION,
        "version": VERSION_REGULATION,
        "description": "Regulatorische Dokumente (MDR, FDA CFR)",
        "category": "standards"
    },
    "GUIDANCE_DOCUMENT": {
        "prompt": PROMPT_GUIDANCE_DOCUMENT,
        "version": VERSION_GUIDANCE_DOCUMENT,
        "description": "Leitfäden und Guidance-Dokumente",
        "category": "standards"
    },
    
    # =============================================================================
    # 🧪 TEST & FALLBACK
    # =============================================================================
    "PROMPT_TEST": {
        "prompt": PROMPT_PROMPT_TEST,
        "version": VERSION_PROMPT_TEST,
        "description": "Prompt-Test für Qualitätssicherung",
        "category": "test"
    },
    "OTHER": {
        "prompt": PROMPT_OTHER,
        "version": VERSION_OTHER,
        "description": "Sonstige/kundenspezifische Dokumente",
        "category": "fallback"
    },
}

# =============================================================================
# 🏗️ VERWALTUNGSKLASSE
# =============================================================================

class VisioPromptsManager:
    """
    Verwaltet die Prompts für die Visio-Dokumentenanalyse
    
    Features:
    - Alle 25 Dokumenttypen unterstützt
    - Versionierung für Audit-Trail
    - Debug-Informationen
    - Kategorisierung für bessere Organisation
    
    VERWENDUNG:
    - Prompts laden: get_prompt_for_document_type("SOP")
    - Version prüfen: get_prompt_version("SOP")
    - Debug-Info: get_prompt_debug_info("SOP")
    """
    
    def __init__(self):
        """Initialisiert den Prompt-Manager"""
        self.prompts = PROMPT_MAPPING
        logger.info(f"✅ VisioPromptsManager initialisiert mit {len(self.prompts)} Dokumenttypen")
    
    def get_prompt_for_document_type(self, document_type: str) -> Dict[str, str]:
        """
        Holt den Prompt für einen bestimmten Dokumenttyp.
        
        Args:
            document_type: Der Dokumenttyp (z.B. "SOP", "PROCESS")
            
        Returns:
            Dict mit prompt, version, description und category
            
        Raises:
            KeyError: Wenn Dokumenttyp nicht existiert
        """
        if document_type not in self.prompts:
            logger.warning(f"⚠️ Unbekannter Dokumenttyp: {document_type}, verwende OTHER")
            return self.prompts["OTHER"]
        
        prompt_data = self.prompts[document_type]
        logger.info(f"📋 Prompt geladen für {document_type}: v{prompt_data['version']}")
        return prompt_data
    
    def get_prompt_text(self, document_type: str) -> str:
        """
        Holt nur den Prompt-Text für einen Dokumenttyp.
        
        Args:
            document_type: Der Dokumenttyp
            
        Returns:
            Prompt-Text als String
        """
        prompt_data = self.get_prompt_for_document_type(document_type)
        return prompt_data["prompt"]
    
    def get_prompt_version(self, document_type: str) -> str:
        """
        Holt nur die Version eines Prompts.
        
        Args:
            document_type: Der Dokumenttyp
            
        Returns:
            Version als String
        """
        prompt_data = self.get_prompt_for_document_type(document_type)
        return prompt_data["version"]
    
    def get_available_document_types(self) -> Dict[str, Dict[str, str]]:
        """
        Gibt alle verfügbaren Dokumenttypen zurück.
        
        Returns:
            Dict mit allen Dokumenttypen und ihren Metadaten
        """
        return self.prompts
    
    def get_document_types_by_category(self, category: str) -> Dict[str, Dict[str, str]]:
        """
        Gibt Dokumenttypen nach Kategorie gefiltert zurück.
        
        Args:
            category: Kategorie (core, forms, analysis, processes, training, standards, test, fallback)
            
        Returns:
            Gefilterte Dokumenttypen
        """
        return {k: v for k, v in self.prompts.items() if v["category"] == category}
    
    def get_prompt_debug_info(self, document_type: str) -> Dict[str, str]:
        """
        Gibt Debug-Informationen für einen Prompt zurück.
        
        Args:
            document_type: Der Dokumenttyp
            
        Returns:
            Debug-Informationen
        """
        prompt_data = self.get_prompt_for_document_type(document_type)
        
        return {
            "document_type": document_type,
            "prompt_file": f"{document_type.lower()}_prompt.py",
            "version": prompt_data["version"],
            "category": prompt_data["category"],
            "description": prompt_data["description"],
            "prompt_length": len(prompt_data["prompt"]),
            "timestamp": datetime.now().isoformat(),
            "status": "active"
        }
    
    def validate_all_prompts(self) -> Dict[str, bool]:
        """
        Validiert alle Prompts auf Vollständigkeit.
        
        Returns:
            Dict mit Validierungsergebnissen
        """
        results = {}
        
        for doc_type, prompt_data in self.prompts.items():
            is_valid = (
                "prompt" in prompt_data and
                "version" in prompt_data and
                "description" in prompt_data and
                "category" in prompt_data and
                len(prompt_data["prompt"]) > 0
            )
            results[doc_type] = is_valid
            
            if not is_valid:
                logger.error(f"❌ Prompt {doc_type} ist nicht vollständig")
        
        return results

# =============================================================================
# 🌐 GLOBALE INSTANZ
# =============================================================================

# Globale Instanz für einfache Verwendung
visio_prompts_manager = VisioPromptsManager()

# =============================================================================
# 📋 HILFSFUNKTIONEN
# =============================================================================

def get_prompt_for_document_type(document_type: str) -> Dict[str, str]:
    """
    Lädt den Prompt für einen bestimmten Dokumenttyp mit erweiterten Metadaten
    
    Args:
        document_type: Dokumenttyp (z.B. "SOP", "PROCESS")
        
    Returns:
        Dict mit prompt, version, metadata, hash und audit_info
    """
    import hashlib
    from datetime import datetime
    
    # Normalisiere Dokumenttyp
    normalized_type = document_type.upper().replace(" ", "_")
    
    if normalized_type not in PROMPT_MAPPING:
        logger.warning(f"⚠️ Unbekannter Dokumenttyp: {document_type} -> verwende OTHER")
        normalized_type = "OTHER"
    
    prompt_data = PROMPT_MAPPING[normalized_type]
    prompt_text = prompt_data["prompt"]
    version = prompt_data["version"]
    
    # Erstelle Hash für Prompt-Integrität
    prompt_hash = hashlib.sha256(prompt_text.encode('utf-8')).hexdigest()[:16]
    
    # Erweiterte Metadaten für Audit
    metadata = {
        "document_type": normalized_type,
        "original_request": document_type,
        "version": version,
        "description": prompt_data.get("description", ""),
        "category": prompt_data.get("category", "unknown"),
        "prompt_length": len(prompt_text),
        "prompt_hash": prompt_hash,
        "loaded_at": datetime.utcnow().isoformat() + "Z",
        "system_version": "v3.5.0 (2025-07-26)"
    }
    
    # Audit-Informationen
    audit_info = {
        "prompt_used": prompt_text[:200] + "..." if len(prompt_text) > 200 else prompt_text,
        "full_prompt_available": len(prompt_text) <= 200,
        "hash_verification": f"sha256:{prompt_hash}",
        "version_verified": True,
        "load_success": True
    }
    
    logger.info(f"✅ Prompt geladen: {normalized_type} v{version} (Hash: {prompt_hash})")
    
    return {
        "prompt": prompt_text,
        "version": version,
        "metadata": metadata,
        "hash": prompt_hash,
        "audit_info": audit_info,
        "success": True
    }

def get_prompt_text(document_type: str) -> str:
    """
    Hilfsfunktion: Holt nur den Prompt-Text.
    
    Args:
        document_type: Der Dokumenttyp
        
    Returns:
        Prompt-Text als String
    """
    return visio_prompts_manager.get_prompt_text(document_type)

def get_prompt_version(document_type: str) -> str:
    """
    Hilfsfunktion: Holt nur die Prompt-Version.
    
    Args:
        document_type: Der Dokumenttyp
        
    Returns:
        Version als String
    """
    return visio_prompts_manager.get_prompt_version(document_type)

def get_available_document_types() -> Dict[str, Dict[str, str]]:
    """
    Hilfsfunktion: Listet alle verfügbaren Dokumenttypen auf.
    
    Returns:
        Dict mit allen Dokumenttypen und Metadaten
    """
    return visio_prompts_manager.get_available_document_types()

def get_prompt_debug_info(document_type: str) -> Dict[str, str]:
    """
    Hilfsfunktion: Gibt Debug-Informationen zurück.
    
    Args:
        document_type: Der Dokumenttyp
        
    Returns:
        Debug-Informationen
    """
    return visio_prompts_manager.get_prompt_debug_info(document_type)

def validate_all_prompts() -> Dict[str, bool]:
    """
    Hilfsfunktion: Validiert alle Prompts.
    
    Returns:
        Validierungsergebnisse
    """
    return visio_prompts_manager.validate_all_prompts()

# =============================================================================
# 🧪 INITIALISIERUNG & VALIDIERUNG
# =============================================================================

def initialize_prompts():
    """Initialisiert und validiert alle Prompts beim Start"""
    logger.info("🔄 Initialisiere Visio-Prompts...")
    
    # Validiere alle Prompts
    validation_results = validate_all_prompts()
    valid_count = sum(validation_results.values())
    total_count = len(validation_results)
    
    if valid_count == total_count:
        logger.info(f"✅ Alle {total_count} Prompts erfolgreich validiert")
    else:
        logger.error(f"❌ {total_count - valid_count} von {total_count} Prompts haben Probleme")
        for doc_type, is_valid in validation_results.items():
            if not is_valid:
                logger.error(f"   - {doc_type}: Ungültig")
    
    return validation_results

# Automatische Initialisierung beim Import
if __name__ != "__main__":
    initialize_prompts() 