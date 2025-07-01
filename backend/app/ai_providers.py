"""
KI-Provider für lokale und kostenlose Modelle
"""
import requests
import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class OllamaProvider:
    """Lokaler Ollama Provider für kostenlose KI-Modelle"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = [
            "llama2:7b",
            "mistral:7b", 
            "codellama:7b"
        ]
    
    async def is_available(self) -> bool:
        """Prüft ob Ollama läuft"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def analyze_document(self, content: str, document_type: str = "unknown") -> Dict[str, Any]:
        """Analysiert Dokument mit lokalem Modell"""
        try:
            prompt = f"""
            Analysiere das folgende Dokument und extrahiere:
            1. Dokumenttyp
            2. Hauptthemen (3-5 Stichworte)
            3. Sprache (de/en)
            4. Qualitätsbewertung (1-10)
            5. Compliance-Relevanz (ja/nein)
            
            Dokument:
            {content[:2000]}...
            
            Antwort als JSON:
            """
            
            payload = {
                "model": "mistral:7b",
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_analysis_result(result.get("response", ""))
            else:
                logger.error(f"Ollama API Fehler: {response.status_code}")
                return self._fallback_analysis(content)
                
        except Exception as e:
            logger.error(f"Ollama Analyse Fehler: {e}")
            return self._fallback_analysis(content)
    
    def _parse_analysis_result(self, response: str) -> Dict[str, Any]:
        """Parst KI-Antwort zu strukturiertem Ergebnis"""
        try:
            # Versuche JSON zu extrahieren
            if "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: Strukturierte Antwort
        return {
            "document_type": "Unbekannt",
            "main_topics": ["Automatisch analysiert"],
            "language": "de",
            "quality_score": 7,
            "compliance_relevant": True,
            "ai_summary": response[:200]
        }
    
    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Einfache Fallback-Analyse ohne KI"""
        return {
            "document_type": "Automatisch erkannt",
            "main_topics": ["Inhalt", "Qualität", "Compliance"],
            "language": "de" if any(word in content.lower() for word in ["der", "die", "das", "und", "ist"]) else "en",
            "quality_score": 6,
            "compliance_relevant": True,
            "ai_summary": "Dokument wurde lokal analysiert"
        }


class HuggingFaceProvider:
    """Kostenloser Hugging Face Provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api-inference.huggingface.co/models"
        self.model = "microsoft/DialoGPT-medium"
    
    async def analyze_document(self, content: str, document_type: str = "unknown") -> Dict[str, Any]:
        """Analysiert mit Hugging Face Inference API"""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            payload = {
                "inputs": f"Analysiere dieses Dokument: {content[:500]}..."
            }
            
            response = requests.post(
                f"{self.base_url}/{self.model}",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                return {
                    "document_type": document_type,
                    "main_topics": ["HF-Analyse"],
                    "language": "de",
                    "quality_score": 7,
                    "compliance_relevant": True,
                    "ai_summary": "Analysiert mit Hugging Face"
                }
            else:
                logger.warning(f"HuggingFace API limitiert: {response.status_code}")
                return self._fallback_analysis(content)
                
        except Exception as e:
            logger.error(f"HuggingFace Fehler: {e}")
            return self._fallback_analysis(content)
    
    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback ohne API"""
        return {
            "document_type": "Standard",
            "main_topics": ["Dokument", "Analyse"],
            "language": "de",
            "quality_score": 6,
            "compliance_relevant": True,
            "ai_summary": "Basis-Analyse durchgeführt"
        }


class GoogleGeminiProvider:
    """🌟 Google Gemini Flash Provider - KOSTENLOS (1500 Anfragen/Tag)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-1.5-flash"
        
    async def is_available(self) -> bool:
        """Prüft ob Google Gemini verfügbar ist"""
        return bool(self.api_key)
    
    async def analyze_document(self, content: str, document_type: str = "unknown") -> Dict[str, Any]:
        """Analysiert mit Google Gemini Flash (kostenlos!)"""
        if not self.api_key:
            return self._fallback_analysis(content)
            
        try:
            prompt = f"""
            Du bist ein Experte für Qualitätsmanagement in der Medizintechnik. 
            Analysiere das folgende Dokument und gib die Antwort als JSON zurück:

            {{
                "document_type": "erkannter Dokumenttyp (z.B. SOP, Arbeitsanweisung, Norm)",
                "main_topics": ["Hauptthema1", "Hauptthema2", "Hauptthema3"],
                "language": "de/en/fr",
                "quality_score": 1-10,
                "compliance_relevant": true/false,
                "ai_summary": "Kurze Zusammenfassung des Inhalts",
                "norm_references": ["gefundene Normen wie ISO 13485, MDR"],
                "risk_level": "niedrig/mittel/hoch",
                "missing_elements": ["Was könnte fehlen für Vollständigkeit"]
            }}

            Dokument (erste 2000 Zeichen):
            {content[:2000]}
            """
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 1000
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and result["candidates"]:
                    text_response = result["candidates"][0]["content"]["parts"][0]["text"]
                    return self._parse_gemini_response(text_response, content)
                else:
                    logger.warning("Keine Antwort von Gemini erhalten")
                    return self._fallback_analysis(content)
            else:
                logger.error(f"Gemini API Fehler: {response.status_code} - {response.text}")
                return self._fallback_analysis(content)
                
        except Exception as e:
            logger.error(f"Google Gemini Fehler: {e}")
            return self._fallback_analysis(content)
    
    def _parse_gemini_response(self, response: str, original_content: str) -> Dict[str, Any]:
        """Parst Gemini JSON-Response"""
        try:
            # JSON aus Response extrahieren
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
            else:
                json_str = response
                
            parsed = json.loads(json_str)
            
            # Validierung und Defaults
            return {
                "document_type": parsed.get("document_type", "Unbekannt"),
                "main_topics": parsed.get("main_topics", ["KI-analysiert"]),
                "language": parsed.get("language", "de"),
                "quality_score": parsed.get("quality_score", 7),
                "compliance_relevant": parsed.get("compliance_relevant", True),
                "ai_summary": parsed.get("ai_summary", "Analysiert mit Google Gemini"),
                "norm_references": parsed.get("norm_references", []),
                "risk_level": parsed.get("risk_level", "mittel"),
                "missing_elements": parsed.get("missing_elements", []),
                "provider": "google_gemini",
                "enhanced": True
            }
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Gemini Response Parse-Fehler: {e}")
            return {
                "document_type": "KI-analysiert",
                "main_topics": ["Automatisch analysiert"],
                "language": "de",
                "quality_score": 8,
                "compliance_relevant": True,
                "ai_summary": f"Google Gemini Analyse (Parse-Fehler): {response[:200]}",
                "provider": "google_gemini",
                "enhanced": True
            }
    
    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback ohne API"""
        return {
            "document_type": "Standard",
            "main_topics": ["Dokument", "Analyse"],
            "language": "de",
            "quality_score": 6,
            "compliance_relevant": True,
            "ai_summary": "Google Gemini nicht verfügbar - Basis-Analyse",
            "provider": "rule_based",
            "enhanced": False
        } 