"""
🤖 KI-QMS Hybrid AI Engine v1.0
Erweitert die bestehende lokale AI Engine um optionale LLM-Funktionalitäten

HYBRID-ANSATZ:
- Nutzt die bewährte lokale AI Engine als Basis (DSGVO-konform, schnell, kostenlos)
- Erweitert optional um LLM-basierte Analysen (konfigurierbar)
- Anonymisierung für LLM-Verarbeitung
- Kosten-Transparenz und Performance-Monitoring

FEATURES:
- 🏠 Lokale KI als Standard (bestehende ai_engine.py)
- 🌐 Optionale LLM-Integration (OpenAI, Anthropic, Ollama, Azure)
- 🔒 Automatische Daten-Anonymisierung
- 💰 Kosten-Tracking und -Optimierung
- ⚡ Performance-Monitoring
- 🛡️ Graceful Degradation bei LLM-Ausfällen
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from .ai_engine import ai_engine, AIAnalysisResult

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    """Unterstützte LLM-Provider für Hybrid-Ansatz"""
    NONE = "none"  # Nur lokale KI
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL_OLLAMA = "ollama"
    AZURE_OPENAI = "azure_openai"

@dataclass
class LLMConfig:
    """Konfiguration für LLM-Provider"""
    provider: LLMProvider = LLMProvider.NONE
    api_key: Optional[str] = None
    model: Optional[str] = None
    endpoint: Optional[str] = None
    anonymize_data: bool = True
    max_tokens: int = 1000
    temperature: float = 0.1
    max_cost_per_request: float = 0.50  # Euro
    
@dataclass
class HybridAnalysisResult:
    """Erweiterte Analyse-Ergebnisse mit LLM-Enhancement"""
    # Basis: Lokale KI-Ergebnisse (immer vorhanden)
    local_analysis: AIAnalysisResult
    
    # LLM-Enhanced Ergebnisse (optional)
    llm_enhanced: bool = False
    llm_summary: Optional[str] = None
    llm_recommendations: List[str] = None
    llm_compliance_gaps: List[Dict[str, str]] = None
    llm_auto_metadata: Optional[Dict[str, Union[str, float, List[str]]]] = None
    
    # Performance & Kosten
    enhancement_confidence: float = 0.0
    estimated_cost_eur: float = 0.0
    processing_time_seconds: float = 0.0
    anonymization_applied: bool = False

class HybridAIEngine:
    """
    🧠 Hybrid AI Engine - Erweitert lokale KI um optionale LLM-Funktionen
    
    Arbeitsweise:
    1. Nutzt immer die lokale AI Engine als Basis
    2. Erweitert optional um LLM-basierte Analysen
    3. Behält alle bestehenden Funktionen bei
    4. Graceful Degradation bei LLM-Problemen
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """
        Initialisiert Hybrid AI Engine
        
        Args:
            llm_config: LLM-Konfiguration (optional, Standard: nur lokale KI)
        """
        self.logger = logging.getLogger(__name__)
        
        # LLM-Konfiguration
        self.llm_config = llm_config or self._load_config_from_env()
        self.llm_enabled = self.llm_config.provider != LLMProvider.NONE
        
        # LLM-Client
        self.llm_client = None
        self._cost_tracking = []
        
        # LLM initialisieren (falls konfiguriert)
        if self.llm_enabled:
            self._init_llm_client()
        
        self.logger.info(f"🤖 Hybrid AI Engine initialisiert - LLM: {'✅' if self.llm_enabled else '❌'} ({self.llm_config.provider.value})")

    def _load_config_from_env(self) -> LLMConfig:
        """Lädt LLM-Konfiguration aus Umgebungsvariablen"""
        provider = LLMProvider(os.getenv("AI_LLM_PROVIDER", "none"))
        
        return LLMConfig(
            provider=provider,
            api_key=os.getenv("AI_LLM_API_KEY"),
            model=os.getenv("AI_LLM_MODEL"),
            endpoint=os.getenv("AI_LLM_ENDPOINT"),
            anonymize_data=os.getenv("AI_LLM_ANONYMIZE", "true").lower() == "true",
            max_tokens=int(os.getenv("AI_LLM_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("AI_LLM_TEMPERATURE", "0.1")),
            max_cost_per_request=float(os.getenv("AI_LLM_MAX_COST", "0.50"))
        )

    def _init_llm_client(self):
        """Initialisiert LLM-Client basierend auf Provider"""
        try:
            if self.llm_config.provider == LLMProvider.OPENAI:
                self._init_openai_client()
            elif self.llm_config.provider == LLMProvider.ANTHROPIC:
                self._init_anthropic_client()
            elif self.llm_config.provider == LLMProvider.LOCAL_OLLAMA:
                self._init_ollama_client()
            elif self.llm_config.provider == LLMProvider.AZURE_OPENAI:
                self._init_azure_openai_client()
                
            self.logger.info(f"🔌 LLM-Client initialisiert: {self.llm_config.provider.value}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ LLM-Client Initialisierung fehlgeschlagen: {e}")
            self.logger.info("🏠 Fallback: Nur lokale KI wird verwendet")
            self.llm_enabled = False
            self.llm_client = None

    def _init_openai_client(self):
        """Initialisiert OpenAI Client"""
        try:
            import openai
            self.llm_client = openai.OpenAI(
                api_key=self.llm_config.api_key or os.getenv("OPENAI_API_KEY")
            )
            self.llm_config.model = self.llm_config.model or "gpt-4o-mini"
        except ImportError:
            raise ImportError("OpenAI-Library nicht installiert. Verwende: pip install openai")

    def _init_anthropic_client(self):
        """Initialisiert Anthropic Claude Client"""
        try:
            import anthropic
            self.llm_client = anthropic.Anthropic(
                api_key=self.llm_config.api_key or os.getenv("ANTHROPIC_API_KEY")
            )
            self.llm_config.model = self.llm_config.model or "claude-3-haiku-20240307"
        except ImportError:
            raise ImportError("Anthropic-Library nicht installiert. Verwende: pip install anthropic")

    def _init_ollama_client(self):
        """Initialisiert lokalen Ollama Client"""
        try:
            import requests
            endpoint = self.llm_config.endpoint or "http://localhost:11434"
            response = requests.get(f"{endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                self.llm_client = "ollama"
                self.llm_config.model = self.llm_config.model or "llama3.1:8b"
            else:
                raise ConnectionError("Ollama Server nicht erreichbar")
        except Exception as e:
            raise ConnectionError(f"Ollama-Verbindung fehlgeschlagen: {e}")

    def _init_azure_openai_client(self):
        """Initialisiert Azure OpenAI Client"""
        try:
            import openai
            self.llm_client = openai.AzureOpenAI(
                api_key=self.llm_config.api_key or os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=self.llm_config.endpoint or os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version="2024-02-01"
            )
            self.llm_config.model = self.llm_config.model or "gpt-4o-mini"
        except ImportError:
            raise ImportError("OpenAI-Library für Azure benötigt")

    def comprehensive_hybrid_analysis(self, text: str, filename: str = "", 
                                    existing_documents: List[Dict] = None,
                                    enhance_with_llm: bool = True) -> HybridAnalysisResult:
        """
        🧠 Führt umfassende Hybrid-Analyse durch
        
        Workflow:
        1. Lokale KI-Analyse (immer)
        2. Optionale LLM-Enhancement (falls aktiviert und gewünscht)
        3. Ergebnis-Kombination mit Kosten-Tracking
        
        Args:
            text: Dokumenttext
            filename: Dateiname
            existing_documents: Existierende Dokumente für Duplikatsprüfung
            enhance_with_llm: LLM-Enhancement aktivieren (falls verfügbar)
            
        Returns:
            HybridAnalysisResult: Kombinierte Analyseergebnisse
        """
        start_time = time.time()
        
        self.logger.info(f"🧠 Starte Hybrid-Analyse: {filename}")
        
        # 1. LOKALE KI-ANALYSE (Basis, immer ausführen)
        local_result = ai_engine.comprehensive_analysis(text, filename, existing_documents)
        
        # 2. LLM-ENHANCEMENT (optional)
        llm_enhanced = False
        llm_summary = None
        llm_recommendations = []
        llm_compliance_gaps = []
        llm_auto_metadata = {}
        enhancement_confidence = 0.0
        estimated_cost = 0.0
        anonymization_applied = False
        
        if enhance_with_llm and self.llm_enabled and self.llm_client:
            try:
                self.logger.info("🤖 Starte LLM-Enhancement...")
                
                # Text anonymisieren (falls aktiviert)
                analysis_text = text
                if self.llm_config.anonymize_data:
                    analysis_text = self._anonymize_text(text)
                    anonymization_applied = True
                
                # LLM-Analyse durchführen
                llm_results = self._perform_llm_analysis(analysis_text, local_result, filename)
                
                if llm_results:
                    llm_enhanced = True
                    llm_summary = llm_results.get("summary")
                    llm_recommendations = llm_results.get("recommendations", [])
                    llm_compliance_gaps = llm_results.get("compliance_gaps", [])
                    llm_auto_metadata = llm_results.get("auto_metadata", {})
                    enhancement_confidence = llm_results.get("confidence", 0.8)
                    estimated_cost = llm_results.get("estimated_cost", 0.01)
                    
                    # Kosten-Tracking
                    self._cost_tracking.append({
                        "timestamp": time.time(),
                        "filename": filename,
                        "cost_eur": estimated_cost,
                        "provider": self.llm_config.provider.value
                    })
                    
                    self.logger.info(f"✅ LLM-Enhancement erfolgreich (Kosten: ~{estimated_cost:.3f}€)")
                
            except Exception as e:
                self.logger.warning(f"⚠️ LLM-Enhancement fehlgeschlagen: {e}")
                self.logger.info("🏠 Fallback: Verwende nur lokale KI-Ergebnisse")
        
        processing_time = time.time() - start_time
        
        return HybridAnalysisResult(
            local_analysis=local_result,
            llm_enhanced=llm_enhanced,
            llm_summary=llm_summary,
            llm_recommendations=llm_recommendations,
            llm_compliance_gaps=llm_compliance_gaps,
            llm_auto_metadata=llm_auto_metadata,
            enhancement_confidence=enhancement_confidence,
            estimated_cost_eur=estimated_cost,
            processing_time_seconds=processing_time,
            anonymization_applied=anonymization_applied
        )

    def _anonymize_text(self, text: str) -> str:
        """
        Anonymisiert sensible Daten für sichere LLM-Verarbeitung
        
        Args:
            text: Original-Text
            
        Returns:
            str: Anonymisierter Text
        """
        import re
        
        anonymized = text
        
        # E-Mail-Adressen
        anonymized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[E-MAIL]', anonymized)
        
        # Telefonnummern (verschiedene Formate)
        phone_patterns = [
            r'(\+?\d{1,3}[-.\s]?)?\(?\d{3,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,6}',
            r'\b\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,6}\b'
        ]
        for pattern in phone_patterns:
            anonymized = re.sub(pattern, '[TELEFON]', anonymized)
        
        # Firmennamen (häufige Muster)
        company_patterns = [
            r'\b[A-Z][a-z]+ (GmbH|AG|Ltd|Inc|Corp|Corporation|SE|KG)\b',
            r'\b[A-Z][a-z]+ & [A-Z][a-z]+ (GmbH|AG|Ltd|Inc)\b'
        ]
        for pattern in company_patterns:
            anonymized = re.sub(pattern, '[FIRMA]', anonymized)
        
        # Personen-Namen (einfache Heuristik)
        anonymized = re.sub(r'\b[A-Z][a-z]{2,} [A-Z][a-z]{2,}\b', '[PERSON]', anonymized)
        
        # IP-Adressen
        anonymized = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP-ADRESSE]', anonymized)
        
        # URLs (außer Standards-URLs)
        anonymized = re.sub(r'https?://(?!iso|din|en|iec)[^\s]+', '[URL]', anonymized)
        
        return anonymized

    def _perform_llm_analysis(self, text: str, local_result: AIAnalysisResult, filename: str) -> Optional[Dict]:
        """
        Führt LLM-basierte Analyse durch
        
        Args:
            text: (Anonymisierter) Text
            local_result: Lokale KI-Ergebnisse
            filename: Dateiname
            
        Returns:
            Optional[Dict]: LLM-Analyseergebnisse oder None bei Fehler
        """
        if not self.llm_client:
            return None
            
        # Prompts erstellen
        system_prompt = self._create_qms_analysis_prompt()
        user_prompt = self._create_user_analysis_prompt(text, local_result, filename)
        
        try:
            if self.llm_config.provider == LLMProvider.OPENAI:
                return self._query_openai(system_prompt, user_prompt)
            elif self.llm_config.provider == LLMProvider.ANTHROPIC:
                return self._query_anthropic(system_prompt, user_prompt)
            elif self.llm_config.provider == LLMProvider.LOCAL_OLLAMA:
                return self._query_ollama(system_prompt, user_prompt)
            elif self.llm_config.provider == LLMProvider.AZURE_OPENAI:
                return self._query_azure_openai(system_prompt, user_prompt)
        except Exception as e:
            self.logger.error(f"❌ LLM-Abfrage fehlgeschlagen: {e}")
            return None

    def _create_qms_analysis_prompt(self) -> str:
        """Erstellt System-Prompt für QMS-Analyse"""
        return """Du bist ein Experte für Qualitätsmanagementsysteme in der Medizintechnik.

AUFGABE:
- Analysiere QMS-Dokumente gemäß ISO 13485, MDR, FDA-Standards
- Identifiziere Compliance-Lücken und Verbesserungsmöglichkeiten  
- Generiere automatische Metadaten und Zusammenfassungen
- Gib strukturierte, umsetzbare Empfehlungen

AUSGABE NUR IM JSON-FORMAT:
{
  "summary": "Kurze präzise Zusammenfassung (2-3 Sätze)",
  "recommendations": [
    "Konkrete Empfehlung 1",
    "Konkrete Empfehlung 2",
    "Konkrete Empfehlung 3"
  ],
  "compliance_gaps": [
    {
      "standard": "ISO 13485:2016",
      "gap": "Spezifische Lücke",
      "severity": "HOCH|MITTEL|NIEDRIG"
    }
  ],
  "auto_metadata": {
    "suggested_keywords": ["keyword1", "keyword2", "keyword3"],
    "risk_category": "HOCH|MITTEL|NIEDRIG", 
    "compliance_score": 0.85,
    "suggested_reviewers": ["QM-Manager", "Regulatory Affairs"]
  },
  "confidence": 0.9,
  "estimated_cost": 0.02
}

WICHTIG: Nur valides JSON zurückgeben, keine Markdown oder Erklärungen."""

    def _create_user_analysis_prompt(self, text: str, local_result: AIAnalysisResult, filename: str) -> str:
        """Erstellt User-Prompt mit Dokumentdaten"""
        
        # Text kürzen für Token-Effizienz
        max_text_length = 2500  # Konservativ für Kosten-Optimierung
        analysis_text = text[:max_text_length]
        if len(text) > max_text_length:
            analysis_text += "\n[...Text aus Kostengründen gekürzt...]"
            
        return f"""DOKUMENT-ANALYSE:

DATEINAME: {filename}

LOKALE KI-ERGEBNISSE (als Basis):
- Dokumenttyp: {local_result.document_type} (Konfidenz: {local_result.type_confidence:.1%})
- Sprache: {local_result.detected_language.value}
- Komplexität: {local_result.complexity_score}/10
- Risiko: {local_result.risk_level}
- Keywords: {', '.join(local_result.extracted_keywords[:8])}
- Normen: {', '.join([ref['norm_name'] for ref in local_result.norm_references[:3]])}

DOKUMENTINHALT:
{analysis_text}

Erweitere die lokale Analyse um QMS-spezifische Erkenntnisse und strukturierte Empfehlungen."""

    def _query_openai(self, system_prompt: str, user_prompt: str) -> Optional[Dict]:
        """OpenAI API-Abfrage mit Kosten-Kontrolle"""
        try:
            response = self.llm_client.chat.completions.create(
                model=self.llm_config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.llm_config.max_tokens,
                temperature=self.llm_config.temperature,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Kosten berechnen (OpenAI GPT-4o-mini Preise)
            input_cost = (response.usage.prompt_tokens / 1000) * 0.00015  # $0.15 per 1M tokens
            output_cost = (response.usage.completion_tokens / 1000) * 0.0006  # $0.60 per 1M tokens
            total_cost_usd = input_cost + output_cost
            estimated_cost_eur = total_cost_usd * 0.92  # Grobe USD->EUR Umrechnung
            
            result["estimated_cost"] = estimated_cost_eur
            
            # Kosten-Limit prüfen
            if estimated_cost_eur > self.llm_config.max_cost_per_request:
                self.logger.warning(f"⚠️ LLM-Kosten überschritten: {estimated_cost_eur:.3f}€ > {self.llm_config.max_cost_per_request}€")
            
            return result
            
        except Exception as e:
            self.logger.error(f"OpenAI-Fehler: {e}")
            return None

    def _query_anthropic(self, system_prompt: str, user_prompt: str) -> Optional[Dict]:
        """Anthropic Claude API-Abfrage"""
        try:
            response = self.llm_client.messages.create(
                model=self.llm_config.model,
                max_tokens=self.llm_config.max_tokens,
                temperature=self.llm_config.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            result = json.loads(response.content[0].text)
            
            # Kosten berechnen (Claude Haiku Preise)
            input_cost = (response.usage.input_tokens / 1000) * 0.00025  # $0.25 per 1M tokens
            output_cost = (response.usage.output_tokens / 1000) * 0.00125  # $1.25 per 1M tokens
            total_cost_usd = input_cost + output_cost
            estimated_cost_eur = total_cost_usd * 0.92
            
            result["estimated_cost"] = estimated_cost_eur
            
            return result
            
        except Exception as e:
            self.logger.error(f"Anthropic-Fehler: {e}")
            return None

    def _query_ollama(self, system_prompt: str, user_prompt: str) -> Optional[Dict]:
        """Lokale Ollama-Abfrage (kostenlos)"""
        try:
            import requests
            
            endpoint = self.llm_config.endpoint or "http://localhost:11434"
            
            payload = {
                "model": self.llm_config.model,
                "prompt": f"{system_prompt}\n\n{user_prompt}",
                "stream": False,
                "options": {
                    "temperature": self.llm_config.temperature,
                    "num_predict": self.llm_config.max_tokens
                }
            }
            
            response = requests.post(f"{endpoint}/api/generate", json=payload, timeout=60)
            response.raise_for_status()
            
            # Versuche JSON zu parsen aus der Antwort
            response_text = response.json().get("response", "")
            
            # Extrahiere JSON aus der Antwort (falls vorhanden)
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback: Strukturiere Antwort manuell
                result = {
                    "summary": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "recommendations": [],
                    "compliance_gaps": [],
                    "auto_metadata": {},
                    "confidence": 0.6
                }
            
            result["estimated_cost"] = 0.0  # Lokale Ausführung
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ollama-Fehler: {e}")
            return None

    def _query_azure_openai(self, system_prompt: str, user_prompt: str) -> Optional[Dict]:
        """Azure OpenAI-Abfrage (gleiche API wie OpenAI)"""
        return self._query_openai(system_prompt, user_prompt)

    def get_cost_statistics(self) -> Dict[str, Union[float, int, List[Dict]]]:
        """
        Gibt Kosten-Statistiken zurück
        
        Returns:
            Dict: Kosten-Übersicht und -Verlauf
        """
        if not self._cost_tracking:
            return {
                "total_cost_eur": 0.0,
                "request_count": 0,
                "average_cost_per_request": 0.0,
                "recent_requests": []
            }
        
        total_cost = sum(entry["cost_eur"] for entry in self._cost_tracking)
        request_count = len(self._cost_tracking)
        avg_cost = total_cost / request_count if request_count > 0 else 0.0
        
        return {
            "total_cost_eur": round(total_cost, 4),
            "request_count": request_count,
            "average_cost_per_request": round(avg_cost, 4),
            "recent_requests": self._cost_tracking[-10:]  # Letzte 10 Anfragen
        }

# Globale Hybrid-Instanz
hybrid_ai_engine = HybridAIEngine()
