"""
Zentrale Konfiguration für DocuMind-AI QMS System

Diese Datei verwaltet alle konfigurierbaren Parameter des Systems,
um hardcodierte Werte zu vermeiden und Flexibilität zu gewährleisten.

Version: 1.0.0
Autor: DocuMind-AI Team
"""

import os
from pathlib import Path
from typing import List, Dict

# =============================================================================
# 🔧 SYSTEM-PFADE
# =============================================================================

def get_uploads_dir() -> Path:
    """
    Gibt das Upload-Verzeichnis zurück.
    
    Priorität:
    1. Umgebungsvariable UPLOADS_DIR
    2. Relative Pfad 'backend/uploads' (Standard)
    """
    uploads_dir = os.getenv('UPLOADS_DIR', 'backend/uploads')
    return Path(uploads_dir)

def get_prompts_dir() -> Path:
    """
    Gibt das Prompt-Verzeichnis zurück.
    
    Priorität:
    1. Umgebungsvariable PROMPTS_DIR
    2. Relative Pfad zum multi_visio_prompts Ordner (Standard)
    """
    prompts_dir = os.getenv('PROMPTS_DIR')
    if prompts_dir:
        return Path(prompts_dir)
    
    # Standard: Relativ zur aktuellen Datei
    return Path(__file__).parent / "multi_visio_prompts"

def get_logs_dir() -> Path:
    """
    Gibt das Log-Verzeichnis zurück.
    
    Priorität:
    1. Umgebungsvariable LOGS_DIR
    2. Relative Pfad 'logs' (Standard)
    """
    logs_dir = os.getenv('LOGS_DIR', 'logs')
    return Path(logs_dir)

# =============================================================================
# 🤖 AI-PROVIDER KONFIGURATION
# =============================================================================

# Standard AI-Provider (Reihenfolge = Priorität)
DEFAULT_PROVIDER_CHAIN = [
    "openai_4o_mini",
    "gemini",
    "ollama", 
    "rule_based"
]

def get_available_providers() -> List[str]:
    """
    Gibt verfügbare AI-Provider zurück.
    
    Priorität:
    1. Umgebungsvariable AI_PROVIDERS (kommasepariert)
    2. DEFAULT_PROVIDER_CHAIN
    """
    env_providers = os.getenv('AI_PROVIDERS')
    if env_providers:
        return [p.strip() for p in env_providers.split(',')]
    
    return DEFAULT_PROVIDER_CHAIN.copy()

def get_default_provider() -> str:
    """
    Gibt den Standard-Provider zurück.
    
    Priorität:
    1. Umgebungsvariable DEFAULT_AI_PROVIDER
    2. Erster Provider aus der verfügbaren Liste
    """
    default_provider = os.getenv('DEFAULT_AI_PROVIDER')
    if default_provider:
        return default_provider
    
    available = get_available_providers()
    return available[0] if available else "openai_4o_mini"

def get_provider_fallback_chain(preferred_provider: str = None) -> List[str]:
    """
    Gibt die Provider-Fallback-Kette zurück.
    
    Args:
        preferred_provider: Gewünschter Provider (wird an erste Stelle gesetzt)
    
    Returns:
        Liste der Provider in Fallback-Reihenfolge
    """
    available = get_available_providers()
    
    if preferred_provider and preferred_provider in available:
        # Setze gewünschten Provider an erste Stelle
        chain = [preferred_provider]
        chain.extend([p for p in available if p != preferred_provider])
        return chain
    
    return available

# Provider-spezifische Konfiguration
PROVIDER_CONFIG = {
    "openai_4o_mini": {
        "display_name": "🤖 OpenAI 4o-mini",
        "supports_vision": True,
        "max_tokens": 16384,  # Maximum für bessere Analyse-Qualität
        "temperature": 0.0
    },
    "gemini": {
        "display_name": "🌐 Google Gemini",
        "supports_vision": True,
        "max_tokens": 32768,  # Maximum für komplexe Multi-Visio Analyse
        "temperature": 0.0
    },
    "ollama": {
        "display_name": "🦙 Ollama (Local)",
        "supports_vision": False,
        "max_tokens": 8192,  # Erhöht für längere Texte
        "temperature": 0.0
    },
    "rule_based": {
        "display_name": "📋 Rule-based",
        "supports_vision": False,
        "max_tokens": None,  # Kein Limit für regelbasierte Logik
        "temperature": 0.0
    }
}

def get_provider_config(provider_name: str) -> Dict:
    """
    Gibt die Konfiguration für einen Provider zurück.
    
    Args:
        provider_name: Name des Providers
        
    Returns:
        Provider-Konfiguration oder Standard-Werte
    """
    return PROVIDER_CONFIG.get(provider_name, {
        "display_name": f"🔧 {provider_name}",
        "supports_vision": False,
        "max_tokens": 2048,
        "temperature": 0.0
    })

# =============================================================================
# 📊 QUALITÄTSSCHWELLEN
# =============================================================================

# Standard-Qualitätsschwellen (können später dokumenttyp-spezifisch werden)
QUALITY_THRESHOLDS = {
    "high_quality": float(os.getenv('QUALITY_THRESHOLD_HIGH', '95.0')),
    "medium_quality": float(os.getenv('QUALITY_THRESHOLD_MEDIUM', '85.0')),
    "low_quality": float(os.getenv('QUALITY_THRESHOLD_LOW', '70.0'))
}

def get_quality_threshold(level: str) -> float:
    """
    Gibt Qualitätsschwelle für ein Level zurück.
    
    Args:
        level: "high_quality", "medium_quality", "low_quality"
        
    Returns:
        Schwellenwert in Prozent
    """
    return QUALITY_THRESHOLDS.get(level, 80.0)

# =============================================================================
# 🔧 MULTI-VISIO KONFIGURATION
# =============================================================================

# Prompt-Datei-Mapping (konfigurierbar)
MULTI_VISIO_PROMPT_FILES = {
    "expert-induction": "01_expert_induction.txt",
    "structured-analysis": "02_structured_analysis.txt", 
    "word-coverage": "03_word_coverage.txt",
    "norm-compliance": "05_norm_compliance.txt"
}

def get_prompt_filename(prompt_type: str) -> str:
    """
    Gibt Dateiname für einen Prompt-Typ zurück.
    
    Args:
        prompt_type: Typ des Prompts
        
    Returns:
        Dateiname oder Standard-Schema
    """
    # Versuche aus Umgebungsvariable
    env_var = f"PROMPT_FILE_{prompt_type.upper().replace('-', '_')}"
    env_filename = os.getenv(env_var)
    if env_filename:
        return env_filename
    
    # Standard-Mapping
    return MULTI_VISIO_PROMPT_FILES.get(prompt_type, f"{prompt_type}.txt")

# =============================================================================
# 🌍 UMGEBUNGS-HILFSFUNKTIONEN
# =============================================================================

def is_development() -> bool:
    """Prüft ob wir im Entwicklungsmodus sind."""
    return os.getenv('ENVIRONMENT', 'development').lower() == 'development'

def is_production() -> bool:
    """Prüft ob wir im Produktionsmodus sind."""
    return os.getenv('ENVIRONMENT', 'development').lower() == 'production'

def get_debug_level() -> str:
    """Gibt Debug-Level zurück."""
    return os.getenv('DEBUG_LEVEL', 'INFO')

# =============================================================================
# 📋 KONFIGURATION VALIDIERUNG
# =============================================================================

def validate_config() -> Dict[str, any]:
    """
    Validiert die aktuelle Konfiguration.
    
    Returns:
        Dictionary mit Validierungsergebnissen
    """
    validation = {
        "valid": True,
        "warnings": [],
        "errors": []
    }
    
    # Prüfe Upload-Verzeichnis
    uploads_dir = get_uploads_dir()
    if not uploads_dir.exists():
        validation["warnings"].append(f"Upload-Verzeichnis existiert nicht: {uploads_dir}")
    
    # Prüfe Prompt-Verzeichnis
    prompts_dir = get_prompts_dir()
    if not prompts_dir.exists():
        validation["errors"].append(f"Prompt-Verzeichnis existiert nicht: {prompts_dir}")
        validation["valid"] = False
    
    # Prüfe Provider-Verfügbarkeit
    available_providers = get_available_providers()
    if not available_providers:
        validation["errors"].append("Keine AI-Provider konfiguriert")
        validation["valid"] = False
    
    return validation

# =============================================================================
# 📄 KONFIGURATION FÜR DEBUGGING
# =============================================================================

def get_config_summary() -> Dict[str, any]:
    """
    Gibt eine Zusammenfassung der aktuellen Konfiguration zurück.
    Nützlich für Debugging und Logs.
    """
    return {
        "system_paths": {
            "uploads_dir": str(get_uploads_dir()),
            "prompts_dir": str(get_prompts_dir()),
            "logs_dir": str(get_logs_dir())
        },
        "ai_providers": {
            "available": get_available_providers(),
            "default": get_default_provider(),
            "fallback_chain": get_provider_fallback_chain()
        },
        "quality_thresholds": QUALITY_THRESHOLDS,
        "environment": {
            "is_development": is_development(),
            "is_production": is_production(),
            "debug_level": get_debug_level()
        },
        "validation": validate_config()
    }