"""
KI-Provider für lokale und kostenlose Modelle
Enhanced mit OpenAI 4o mini Support
"""
import requests
import json
import os
from typing import Dict, Any, Optional, List
import logging
import asyncio
import openai

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
                timeout=120  # Erhöhtes Timeout für lokale Modelle
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_analysis_result(result.get("response", ""))
            else:
                logger.error(f"Ollama API Fehler: {response.status_code}")
                raise Exception(f"Ollama API Fehler: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Ollama Analyse Fehler: {e}")
            raise Exception(f"Ollama Analyse Fehler: {e}")
    
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
    
    async def simple_prompt(self, prompt: str) -> Dict[str, Any]:
        """Einfacher Prompt für AI Test Interface"""
        try:
            payload = {
                "model": "mistral:7b",
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120  # Erhöhtes Timeout für lokale Modelle
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", "Keine Antwort erhalten"),
                    "model": "mistral:7b",
                    "provider": "ollama"
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "provider": "ollama"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ollama Verbindungsfehler: {str(e)}",
                "provider": "ollama"
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


class OpenAI4oMiniProvider:
    """OpenAI 4o-mini Provider - Schnell und günstig für Produktionseinsatz"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        self.model = "gpt-4o-mini"
        self.embedding_model = "text-embedding-3-small"
    
    async def analyze_document(self, content: str, document_type: str = "unknown") -> Dict[str, Any]:
        """Analysiert Dokument mit OpenAI 4o-mini"""
        try:
            if not self.api_key:
                logger.error("❌ OpenAI API Key fehlt - 🚨 KEIN FALLBACK für Auditierbarkeit!")
                raise Exception("OpenAI API Key nicht konfiguriert")
            
            prompt = f"""
            Analysiere dieses QMS-Dokument und gib eine strukturierte Antwort in folgendem JSON-Format:

            {{
                "document_type": "DETECTED_TYPE",
                "main_topics": ["topic1", "topic2", "topic3"],
                "language": "de/en",
                "quality_score": 8.5,
                "compliance_relevant": true,
                "ai_summary": "Detaillierte Zusammenfassung...",
                "norm_references": ["ISO 13485", "MDR"],
                "compliance_keywords": ["GMP", "Validation", "Risk Management"]
            }}

            Dokumenttyp-Optionen: PROCEDURE, WORK_INSTRUCTION, FORM, POLICY, MANUAL, SPECIFICATION, 
            RISK_ASSESSMENT, AUDIT_REPORT, TRAINING_MATERIAL, CERTIFICATE, NORM_STANDARD, OTHER

            Dokument-Inhalt:
            {content[:2000]}...
            """
            
            # Neue OpenAI API v1.x
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Du bist ein QMS-Experte für ISO 13485 und EU MDR. Analysiere Dokumente präzise und strukturiert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            # Parse JSON response
            import json
            try:
                result = json.loads(response.choices[0].message.content)
                result['provider'] = 'openai_4o_mini'
                result['cost'] = 'sehr günstig ($0.00015/1K tokens)'
                return result
            except json.JSONDecodeError:
                # Fallback if not valid JSON
                return {
                    "document_type": document_type,
                    "main_topics": ["OpenAI Analyse"],
                    "language": "de",
                    "quality_score": 8.5,
                    "compliance_relevant": True,
                    "ai_summary": response.choices[0].message.content,
                    "provider": "openai_4o_mini",
                    "cost": "sehr günstig"
                }
                
        except Exception as e:
            logger.error(f"OpenAI 4o-mini Fehler: {e}")
            raise Exception(f"OpenAI 4o-mini Fehler: {e}")
    
    async def simple_prompt(self, prompt: str) -> Dict[str, Any]:
        """Einfacher Prompt für AI Test Interface"""
        try:
            if not self.api_key:
                return {"ai_summary": "OpenAI API Key nicht verfügbar", "response": "API Key fehlt"}
            
            # Neue OpenAI API v1.x
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            return {
                "ai_summary": ai_response,
                "response": ai_response,
                "provider": "openai_4o_mini"
            }
            
        except Exception as e:
            logger.error(f"OpenAI simple_prompt Fehler: {e}")
            return {"ai_summary": f"OpenAI Fehler: {str(e)}", "response": f"Fehler: {str(e)}"}

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generiert OpenAI Embeddings"""
        try:
            if not self.api_key:
                raise ValueError("OpenAI API Key fehlt")
            
            # Neue OpenAI API v1.x
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.info(f"✅ OpenAI Embeddings generiert: {len(embeddings)} Texte")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ OpenAI Embedding Fehler: {e}")
            raise
    
    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback ohne API"""
        return {
            "document_type": "Standard",
            "main_topics": ["Dokument", "Analyse"],
            "language": "de",
            "quality_score": 7,
            "compliance_relevant": True,
            "ai_summary": "Basis-Analyse durchgeführt (OpenAI API nicht verfügbar)",
            "provider": "openai_fallback",
            "cost": "kostenlos"
        }


class OpenAIEmbeddingProvider:
    """Spezialisierter OpenAI Embedding Provider für RAG"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        self.model = "text-embedding-3-small"  # Günstig und sehr gut
        self.dimension = 1536  # Dimension für text-embedding-3-small
    
    async def encode(self, texts: List[str] | str) -> List[List[float]] | List[float]:
        """Encodes text(s) to embeddings - kompatibel mit SentenceTransformer API"""
        try:
            if not self.api_key:
                raise ValueError("OpenAI API Key fehlt")
            
            # Handle single string
            if isinstance(texts, str):
                texts = [texts]
                single_text = True
            else:
                single_text = False
            
            response = await openai.Embedding.acreate(
                model=self.model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            if single_text:
                return embeddings[0]
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ OpenAI Embedding encode Fehler: {e}")
            raise
    
    def encode_sync(self, texts: List[str] | str) -> List[List[float]] | List[float]:
        """Synchrone Version von encode"""
        try:
            if not self.api_key:
                raise ValueError("OpenAI API Key fehlt")
            
            # Handle single string
            if isinstance(texts, str):
                texts = [texts]
                single_text = True
            else:
                single_text = False
            
            response = openai.Embedding.create(
                model=self.model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            if single_text:
                return embeddings[0]
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ OpenAI Embedding encode_sync Fehler: {e}")
            raise


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
        logger.info(f"🔍 Gemini API Key verfügbar: {bool(self.api_key)}")
        if not self.api_key:
            logger.error("❌ Gemini API Key fehlt - 🚨 KEIN FALLBACK für Auditierbarkeit!")
            raise Exception("Google Gemini API Key nicht konfiguriert")
            
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
            
            logger.info(f"🔍 Gemini Response Status: {response.status_code}")
            logger.info(f"🔍 Gemini Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and result["candidates"]:
                    text_response = result["candidates"][0]["content"]["parts"][0]["text"]
                    return self._parse_gemini_response(text_response, content)
                else:
                    logger.error("Keine Antwort von Gemini erhalten - 🚨 KEIN FALLBACK für Auditierbarkeit!")
                    raise Exception("Google Gemini API lieferte keine Antwort")
            else:
                logger.error(f"Gemini API Fehler: {response.status_code} - {response.text}")
                raise Exception(f"Google Gemini API Fehler: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Google Gemini Fehler: {e}")
            raise Exception(f"Google Gemini Fehler: {e}")
    
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
                "provider": "gemini",
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
                "provider": "gemini",
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


class HuggingFaceProvider:
    """Deprecated: Ersetze durch OpenAI4oMiniProvider"""
    
    def __init__(self, api_key: Optional[str] = None):
        logger.warning("⚠️ HuggingFaceProvider ist deprecated. Verwende OpenAI4oMiniProvider.")
        self.fallback_provider = OpenAI4oMiniProvider(api_key)
    
    async def analyze_document(self, content: str, document_type: str = "unknown") -> Dict[str, Any]:
        """Leitet an OpenAI weiter"""
        return await self.fallback_provider.analyze_document(content, document_type) 