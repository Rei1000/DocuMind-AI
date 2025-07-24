"""
🤖 MODULARES RAG-PROMPT-SYSTEM für KI-QMS - Enterprise Grade 2024
================================================================

Zentrale Verwaltung aller RAG-Prompts (Text-basierte Analyse) in modularer Struktur.

📋 ZWECK:
- Einheitliche Prompt-Verwaltung für alle RAG-Funktionen
- Modulare Struktur für einfache Wartung
- Versionierung und Debug-Funktionen
- Audit-konforme Logging

Author: KI-QMS System
Version: 1.0 - Modulare RAG-Prompt-Bibliothek
"""

import os
import importlib
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("KI-QMS.RAGPromptManager")

class RAGPromptsManager:
    """Zentrale Verwaltung aller RAG-Prompts (Text-basierte Analyse)"""
    
    def __init__(self):
        self.prompts = {}
        self.versions = {}
        self.load_all_prompts()
    
    def load_all_prompts(self):
        """Lädt alle RAG-Prompt-Module"""
        prompt_modules = [
            "metadata_extraction",
            "rag_chat", 
            "document_classification",
            "compliance_analysis",
            "workflow_automation",
            "hybrid_ai",
            "provider_specific"
        ]
        
        for module_name in prompt_modules:
            try:
                module = importlib.import_module(f".{module_name}", package="app.rag_prompts")
                if hasattr(module, "get_prompt"):
                    self.prompts[module_name] = module.get_prompt
                if hasattr(module, "VERSION"):
                    self.versions[module_name] = module.VERSION
                logger.info(f"✅ RAG-Prompt-Modul geladen: {module_name}")
            except ImportError as e:
                logger.warning(f"⚠️ RAG-Prompt-Modul nicht gefunden: {module_name} - {e}")
    
    def get_prompt_by_module(self, module_name: str, prompt_type: str, **kwargs) -> str:
        """Holt einen RAG-Prompt aus einem spezifischen Modul"""
        if module_name in self.prompts:
            return self.prompts[module_name](prompt_type=prompt_type, **kwargs)
        else:
            logger.error(f"❌ RAG-Prompt-Modul nicht gefunden: {module_name}")
            return self.get_fallback_prompt(prompt_type, **kwargs)
    
    def get_fallback_prompt(self, prompt_type: str, **kwargs) -> str:
        """Fallback-Prompt für unbekannte Typen"""
        return f"""
        Sie sind ein KI-Assistent für Qualitätsmanagement-Systeme.
        Analysieren Sie das bereitgestellte Dokument.
        
        Dokumenttyp: {prompt_type}
        Zusätzliche Parameter: {kwargs}
        
        Bitte geben Sie eine strukturierte Analyse zurück.
        """
    
    def get_available_prompt_types(self) -> Dict[str, str]:
        """Gibt alle verfügbaren RAG-Prompt-Typen zurück"""
        return {k: f"Version {v}" for k, v in self.versions.items()}
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Debug-Informationen für Audit-Trail"""
        return {
            "loaded_modules": list(self.prompts.keys()),
            "versions": self.versions,
            "total_prompts": len(self.prompts),
            "last_updated": datetime.now().isoformat()
        }

# Globale Instanz
rag_prompts_manager = RAGPromptsManager()

# Kompatibilitäts-Funktionen
def get_metadata_prompt(prompt_type: str, **kwargs) -> str:
    """Kompatibilitäts-Funktion für Metadaten-Prompts"""
    return rag_prompts_manager.get_prompt_by_module("metadata_extraction", prompt_type, **kwargs)

def get_rag_prompt(prompt_type: str, **kwargs) -> str:
    """Kompatibilitäts-Funktion für RAG-Prompts"""
    return rag_prompts_manager.get_prompt_by_module("rag_chat", prompt_type, **kwargs)

def get_strict_json_prompt(prompt_type: str, **kwargs) -> str:
    """Kompatibilitäts-Funktion für JSON-Prompts"""
    return rag_prompts_manager.get_prompt_by_module("provider_specific", prompt_type, **kwargs)

def parse_ai_response(response_text: str, **kwargs) -> Dict[str, Any]:
    """Kompatibilitäts-Funktion für AI-Response-Parsing"""
    # Einfache JSON-Parsing-Implementierung
    import json
    try:
        return json.loads(response_text)
    except:
        return {"raw_response": response_text, "parsing_error": True}

def get_prompt_config() -> Dict[str, Any]:
    """Kompatibilitäts-Funktion für Prompt-Konfiguration"""
    return {
        "temperature": 0.0,
        "max_tokens": 4000,
        "model": "gpt-4o-mini",
        "version": "1.0"
    } 