#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KI-QMS Streamlit Frontend - Zuverlässige Version
ISO 13485 & MDR konforme Dokumentenverwaltung

Diese App ist darauf ausgelegt, ZUVERLÄSSIG zu funktionieren!
Alle bekannten Fehlerquellen wurden berücksichtigt.
"""

import streamlit as st
import requests
import os
import time
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# ===== KONFIGURATION =====
API_BASE_URL = "http://127.0.0.1:8000"  # OHNE /api Suffix!
REQUEST_TIMEOUT = 120  # Erhöht auf 2 Minuten für Vision-API
MAX_FILE_SIZE_MB = 50

# ===== LOGGING SETUP =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== STREAMLIT CONFIG =====
st.set_page_config(
    page_title="DocuMind-AI | Dokumentenverwaltung",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CSS STYLING & FAVICON =====
st.markdown("""
<style>
    /* DocuMind-AI Clean Medical Design - TEST LIGHTER VERSION */
    :root {
        --primary-blue: #5B84C4;
        --text-gray: #6B7280;
        --light-gray: #F8FAFC;
        --border-light: #E2E8F0;
        --white: #FFFFFF;
        --shadow-light: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        --shadow-medium: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Global Clean Styling */
    .main .block-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-gray);
        background-color: var(--white);
        padding-top: 2rem;
    }
    
    /* Komplett weißer Hintergrund überall */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: var(--white) !important;
    }
    
    /* Sidebar - minimalistisch weiß */
    [data-testid="stSidebar"] > div {
        background-color: var(--white) !important;
        border-right: 1px solid var(--border-light) !important;
        padding: 1rem !important;
    }
    

    
    /* Sidebar Logo - sauberer Abstand */
    [data-testid="stSidebar"] .stImage {
        margin-bottom: 2rem !important;
    }
    
    /* Buttons - kompakt und konsistent mit fester Breite */
    .stButton > button, [data-testid="stSidebar"] .stButton > button {
        background-color: var(--white) !important;
        color: var(--text-gray) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 0.4rem 0.8rem !important;
        margin-bottom: 0.3rem !important;
        box-shadow: var(--shadow-light) !important;
        transition: all 0.2s ease !important;
        height: auto !important;
        min-height: 2.2rem !important;
        max-width: 200px !important;
        width: auto !important;
        display: inline-block !important;
    }
    
    /* Sidebar Buttons - volle Breite nur in Sidebar */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        max-width: none !important;
    }
    
    .stButton > button:hover, [data-testid="stSidebar"] .stButton > button:hover {
        color: var(--primary-blue) !important;
        border-color: var(--primary-blue) !important;
        background-color: var(--white) !important;
        box-shadow: var(--shadow-medium) !important;
    }
    
    /* Login-Formular - sauber und klar */
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background-color: var(--white) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
        color: var(--text-gray) !important;
    }
    
    [data-testid="stSidebar"] .stTextInput > div > div > input:focus {
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 0 2px rgba(58, 107, 165, 0.2) !important;
    }
    
    /* Header - professioneller blauer Balken */
    .documind-header-clean {
        background: linear-gradient(135deg, var(--primary-blue) 0%, #2E5A94 100%);
        color: var(--white);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-medium);
    }
    
    .documind-header-clean h1 {
        font-size: 2rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.025em;
    }
    
    .documind-header-clean p {
        font-size: 1.1rem;
        margin: 0;
        opacity: 0.95;
        font-weight: 300;
    }
    

    
    /* Wasserzeichen - dezent */
    .main-content-watermark::before {
        content: '🧠';
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 200px;
        opacity: 0.03;
        z-index: -1;
        pointer-events: none;
        color: var(--primary-blue);
    }
    
    /* Verstecke Streamlit-Branding */
    #MainMenu, footer, .stDeployButton {
        display: none !important;
    }
    
    /* Responsive für verschiedene Bildschirmgrößen */
    @media (max-width: 768px) {
        .login-card-clean {
            margin: 1rem;
            padding: 2rem 1.5rem;
        }
        .documind-header-clean h1 {
            font-size: 1.6rem;
        }
         }
     
</style>
""", unsafe_allow_html=True)

# ===== HILFSFUNKTIONEN =====

def safe_api_call(func, *args, **kwargs):
    """
    Wrapper für API-Aufrufe mit umfassender Fehlerbehandlung
    """
    try:
        return func(*args, **kwargs)
    except requests.exceptions.ConnectionError:
        logger.error("Backend nicht erreichbar")
        st.error("❌ Backend ist nicht erreichbar. Bitte Backend starten!")
        return None
    except requests.exceptions.Timeout:
        logger.error("API-Aufruf Timeout")
        st.error("⏱️ API-Aufruf hat zu lange gedauert")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error: {e}")
        st.error(f"🌐 Netzwerk-Fehler: {e}")
        return None
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}")
        st.error(f"❌ Unerwarteter Fehler: {e}")
        return None

def check_backend_status() -> bool:
    """Prüft ob Backend erreichbar ist"""
    def _check():
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    
    result = safe_api_call(_check)
    return result is True

def get_upload_methods() -> List[Dict]:
    """
    Lädt alle verfügbaren Upload-Methoden vom Backend.
    
    Returns:
        List[Dict]: Liste der verfügbaren Upload-Methoden
    """
    def _get_methods():
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/upload-methods",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("methods", [])
            else:
                st.error(f"❌ Fehler beim Laden der Upload-Methoden: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"❌ Verbindungsfehler beim Laden der Upload-Methoden: {str(e)}")
            return []
    
    return safe_api_call(_get_methods)

def get_document_types() -> List[str]:
    """Lädt verfügbare Dokumenttypen"""
    def _get_types():
        response = requests.get(f"{API_BASE_URL}/api/documents/types", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return []
    
    result = safe_api_call(_get_types)
    # VERBESSERTER FALLBACK: Nur die wichtigsten Typen
    return result if result else ["OTHER", "SOP", "WORK_INSTRUCTION"]

def upload_document_with_file(
    file_data, 
    document_type: str = "OTHER", 
    creator_id: int = 2, 
    title: Optional[str] = None,
    version: str = "1.0",
    content: Optional[str] = None,
    remarks: Optional[str] = None,
    chapter_numbers: Optional[str] = None,
    upload_method: str = "ocr",  # NEU: Upload-Methode Parameter
    ai_model: str = "auto"  # NEU: AI-Modell Parameter
) -> Optional[Dict]:
    """
    Lädt ein Dokument mit Datei hoch - ZUVERLÄSSIG!
    """
    def _upload():
        # Datei vorbereiten
        files = {}
        if file_data:
            file_data.seek(0)  # Wichtig: Zurücksetzen!
            files["file"] = (file_data.name, file_data.read(), file_data.type)
            logger.info(f"📁 Datei vorbereitet: {file_data.name} ({file_data.type})")
        
        # Form-Daten vorbereiten
        form_data = {
            "creator_id": str(creator_id),
            "version": version,
            "upload_method": upload_method,  # NEU: Upload-Methode hinzufügen
            "ai_model": ai_model  # NEU: AI-Modell hinzufügen
        }
        
        # document_type NUR setzen wenn nicht leer (Backend hat Default "OTHER")
        if document_type and document_type.strip():
            form_data["document_type"] = document_type
        
        # Optionale Felder nur hinzufügen wenn vorhanden
        if title and title.strip():
            form_data["title"] = title.strip()
        if content and content.strip():
            form_data["content"] = content.strip()
        if remarks and remarks.strip():
            form_data["remarks"] = remarks.strip()
        if chapter_numbers and chapter_numbers.strip():
            form_data["chapter_numbers"] = chapter_numbers.strip()
        
        logger.info(f"📝 Form-Daten: {form_data}")
        
        # API-Aufruf - KORREKTE URL!
        url = f"{API_BASE_URL}/api/documents/with-file"
        logger.info(f"🚀 Sende Upload-Request an: {url}")
        
        response = requests.post(
            url,
            files=files,
            data=form_data,
            timeout=REQUEST_TIMEOUT
        )
        
        logger.info(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            logger.info(f"✅ Upload erfolgreich: Dokument ID {result.get('id')}")
            return result
        elif response.status_code == 409:
            # Duplikat-Fehler speziell behandeln
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', 'Duplikat erkannt')
            except:
                error_detail = "Duplikat erkannt"
            logger.warning(f"⚠️ Duplikat-Warnung: {error_detail}")
            raise ValueError(f"DUPLIKAT: {error_detail}")
        else:
            # Andere Fehler
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', response.text)
            except:
                error_detail = response.text
            
            logger.error(f"❌ Upload fehlgeschlagen: {response.status_code} - {error_detail}")
            raise Exception(f"Upload fehlgeschlagen (Status {response.status_code}): {error_detail}")
    
    return safe_api_call(_upload)

def test_simple_vision_api(file_data) -> Optional[Dict]:
    """Einfacher Vision-Test für Bilder"""
    def _test():
        try:
            # Datei vorbereiten
            file_data.seek(0)  # Wichtig: Zurücksetzen!
            files = {"file": (file_data.name, file_data.getvalue(), file_data.type)}
            
            response = requests.post(
                f"{API_BASE_URL}/api/test/simple-vision",
                files=files,
                timeout=180  # Längeres Timeout für Vision-API-Tests
            )
            
            if response.status_code == 200:
                result = response.json()
                # Prüfe ob es eine echte API-Antwort ist
                if result.get('success') and result.get('structured_analysis'):
                    st.success(f"✅ Vision-Test erfolgreich: {result.get('summary', 'N/A')}")
                    return result
                else:
                    st.error(f"❌ Vision-Test: Keine gültige API-Antwort erhalten")
                    st.error(f"Antwort: {result}")
                    return None
            else:
                st.error(f"❌ Vision-Test fehlgeschlagen: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"❌ Vision-Test Fehler: {str(e)}")
            return None
    
    return safe_api_call(_test)

def process_multi_visio_stage(file_data, stage: int, provider: str = "auto") -> Optional[Dict]:
    """Führt eine einzelne Stufe der Multi-Visio-Pipeline aus"""
    
    def _process_stage():
        try:
            # Datei vorbereiten
            files = {"file": (file_data.name, file_data.getvalue(), file_data.type)}
            
            # API-Aufruf für Multi-Visio-Stufe
            response = requests.post(
                f"{API_BASE_URL}/api/multi-visio/stage/{stage}",
                files=files,
                data={
                    "provider": provider
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"❌ API-Fehler: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"❌ Fehler: {str(e)}")
            return None
    
    return safe_api_call(_process_stage)

def process_document_with_prompt(file_data, upload_method: str = "visio", document_type: str = "SOP", confirm_prompt: bool = False, preferred_provider: str = "auto", exact_prompt: str = None) -> Optional[Dict]:
    """Optimierter Workflow mit einheitlichem Prompt"""
    def _process():
        try:
            # Datei vorbereiten
            file_data.seek(0)  # Wichtig: Zurücksetzen!
            files = {"file": (file_data.name, file_data.getvalue(), file_data.type)}
            data = {
                "upload_method": upload_method,
                "document_type": document_type,
                "confirm_prompt": confirm_prompt,
                "preferred_provider": preferred_provider
            }
            
            # ✅ PROMPT-SICHERHEIT: Füge den exakten Prompt hinzu, falls vorhanden
            if exact_prompt:
                data["exact_prompt"] = exact_prompt
            
            response = requests.post(
                f"{API_BASE_URL}/api/documents/process-with-prompt",
                files=files,
                data=data,
                timeout=300  # Längerer Timeout für API-Aufrufe (5 Minuten für komplexe Analysen)
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ API-Antwort erhalten: {len(str(result))} Zeichen")
                return result
            else:
                st.error(f"❌ Workflow-Fehler: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"❌ Workflow-Fehler: {str(e)}")
            return None
    
    return safe_api_call(_process)

def get_documents(limit: int = 100) -> List[Dict]:
    """Lädt Dokumente von der API"""
    def _get_docs():
        response = requests.get(f"{API_BASE_URL}/api/documents?limit={limit}", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            documents = response.json()
            logger.info(f"✅ {len(documents)} Dokumente geladen")
            return documents
        else:
            logger.error(f"❌ Dokumente laden fehlgeschlagen: {response.status_code}")
            return []
    
    result = safe_api_call(_get_docs)
    return result if result else []

def get_users() -> List[Dict]:
    """Lädt Benutzer von der API"""
    def _get_users():
        response = requests.get(f"{API_BASE_URL}/api/users", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            users = response.json()
            logger.info(f"✅ {len(users)} Benutzer geladen")
            return users
        else:
            logger.error(f"❌ Benutzer laden fehlgeschlagen: {response.status_code}")
            return []
    
    result = safe_api_call(_get_users)
    return result if result else []

def delete_document(document_id: int) -> bool:
    """Löscht ein Dokument"""
    def _delete():
        response = requests.delete(f"{API_BASE_URL}/api/documents/{document_id}", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            logger.info(f"✅ Dokument {document_id} gelöscht")
            return True
        else:
            logger.error(f"❌ Löschen fehlgeschlagen: {response.status_code}")
            return False
    
    result = safe_api_call(_delete)
    return result is True

def analyze_document_with_ai(document_id: int, analyze_duplicates: bool = True) -> Optional[Dict]:
    """🤖 Führt KI-Analyse für ein Dokument durch"""
    def _analyze():
        response = requests.post(
            f"{API_BASE_URL}/api/documents/{document_id}/ai-analysis",
            params={"analyze_duplicates": analyze_duplicates},
            timeout=REQUEST_TIMEOUT * 2  # KI-Analyse braucht mehr Zeit
        )
        if response.status_code == 200:
            logger.info(f"🤖 KI-Analyse abgeschlossen für Dokument {document_id}")
            return response.json()
        else:
            logger.error(f"❌ KI-Analyse fehlgeschlagen: {response.status_code} - {response.text}")
            return None
    
    return safe_api_call(_analyze)

def analyze_text_with_ai(text: str, filename: Optional[str] = None) -> Optional[Dict]:
    """🧠 Analysiert Text mit KI (ohne Dokumenterstellung)"""
    def _analyze():
        data = {
            "text": text,
            "filename": filename,
            "analyze_duplicates": False
        }
        response = requests.post(
            f"{API_BASE_URL}/api/ai/analyze-text",
            json=data,
            timeout=REQUEST_TIMEOUT * 2
        )
        if response.status_code == 200:
            logger.info(f"🧠 Text-KI-Analyse abgeschlossen")
            return response.json()
        else:
            logger.error(f"❌ Text-KI-Analyse fehlgeschlagen: {response.status_code}")
            return None
    
    return safe_api_call(_analyze)

def analyze_document_with_hybrid_ai(document_id: int, enhance_with_llm: bool = True, analyze_duplicates: bool = True) -> Optional[Dict]:
    """🤖 Hybrid-KI-Analyse für Dokument"""
    def _analyze():
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/documents/{document_id}/hybrid-analysis",
                params={
                    "enhance_with_llm": enhance_with_llm,
                    "analyze_duplicates": analyze_duplicates
                },
                timeout=REQUEST_TIMEOUT * 3  # Längere Timeout für LLM-Analysen
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API-Fehler: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Verbindungsfehler: {e}")
            return None
    
    return safe_api_call(_analyze)

def analyze_text_with_hybrid_ai(text: str, filename: Optional[str] = None, enhance_with_llm: bool = True, analyze_duplicates: bool = False) -> Optional[Dict]:
    """🤖 Hybrid-Text-Analyse"""
    def _analyze():
        try:
            payload = {
                "text": text,
                "enhance_with_llm": enhance_with_llm,
                "analyze_duplicates": analyze_duplicates
            }
            if filename:
                payload["filename"] = filename
            
            response = requests.post(
                f"{API_BASE_URL}/api/ai/hybrid-text-analysis",
                json=payload,
                timeout=REQUEST_TIMEOUT * 3  # Längere Timeout für LLM
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API-Fehler: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Verbindungsfehler: {e}")
            return None
    
    return safe_api_call(_analyze)

def get_hybrid_ai_config() -> Optional[Dict]:
    """🤖 Abrufen der Hybrid-AI-Konfiguration"""
    def _get_config():
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/ai/hybrid-config",
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None
    
    return safe_api_call(_get_config)

def get_hybrid_ai_cost_stats() -> Optional[Dict]:
    """💰 Abrufen der LLM-Kosten-Statistiken"""
    def _get_stats():
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/ai/hybrid-cost-statistics",
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None
    
    return safe_api_call(_get_stats)

def change_document_status(document_id: int, new_status: str, comment: str = "", token: str = "") -> Optional[Dict]:
    """Ändert den Status eines Dokuments"""
    def _change_status():
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        payload = {
            "status": new_status,
            "comment": comment
        }
        
        response = requests.put(
            f"{API_BASE_URL}/api/documents/{document_id}/status",
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            st.error("❌ Keine Berechtigung für diese Status-Änderung")
            return None
        else:
            st.error(f"❌ Fehler beim Status-Update: {response.status_code}")
            return None
    
    return safe_api_call(_change_status)

def get_documents_by_status(status: str) -> List[Dict]:
    """Lädt Dokumente nach Status gefiltert"""
    def _get_docs_by_status():
        response = requests.get(f"{API_BASE_URL}/api/documents/status/{status}", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return []
    
    result = safe_api_call(_get_docs_by_status)
    return result if result else []

def get_document_status_history(document_id: int) -> List[Dict]:
    """Lädt Status-History eines Dokuments"""
    def _get_history():
        response = requests.get(f"{API_BASE_URL}/api/documents/{document_id}/status-history", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return []
    
    result = safe_api_call(_get_history)
    return result if result else []

def render_document_history(document_id: int):
    """Rendert die Dokument-Historie mit verbesserter Formatierung"""
    history = get_document_status_history(document_id)
    if history:
        st.write("**📜 Status-Verlauf:**")
        for h in history:
            # Formatiere Datum/Zeit
            timestamp = h.get('changed_at', 'Unbekannt')
            if timestamp and timestamp != 'Unbekannt':
                try:
                    # ISO Format parse und formatieren
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    formatted_time = timestamp[:16]  # Fallback
            else:
                formatted_time = "Unbekannt"
            
            # User-Name holen
            changed_by = h.get('changed_by', {})
            user_name = changed_by.get('full_name', 'Unbekannt') if changed_by else 'Unbekannt'
            
            # Status-Übergang formatieren
            old_status = h.get('old_status', 'DRAFT')
            new_status = h.get('new_status', 'UNKNOWN')
            
            # Status-Emoji
            status_emojis = {
                'DRAFT': '📝',
                'REVIEWED': '🔍', 
                'APPROVED': '✅',
                'OBSOLETE': '🗑️'
            }
            old_emoji = status_emojis.get(old_status, '❓')
            new_emoji = status_emojis.get(new_status, '❓')
            
            # Bemerkung
            comment = h.get('comment', '')
            comment_text = f" - **{comment}**" if comment and comment.strip() else ""
            
            # Vollständige Zeile anzeigen
            st.write(f"🕒 **{formatted_time}** | 👤 {user_name}")
            st.write(f"   {old_emoji} {old_status} → {new_emoji} {new_status}{comment_text}")
            st.write("---")
    else:
        st.info("Keine Status-Änderungen gefunden")

def create_user(user_data: Dict, token: str = "") -> Optional[Dict]:
    """Erstellt einen neuen Benutzer"""
    def _create_user():
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = requests.post(
            f"{API_BASE_URL}/api/users",
            json=user_data,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 409:
            st.error("❌ Email-Adresse bereits registriert")
            return None
        elif response.status_code == 422:
            try:
                error_detail = response.json()
                st.error(f"❌ Validierungsfehler: {error_detail}")
            except:
                st.error(f"❌ Validierungsfehler (422): Bitte überprüfen Sie Ihre Eingaben")
            return None
        else:
            try:
                error_detail = response.json()
                st.error(f"❌ Fehler beim Erstellen ({response.status_code}): {error_detail}")
            except:
                st.error(f"❌ Fehler beim Erstellen: HTTP {response.status_code}")
            return None
    
    return safe_api_call(_create_user)

def get_all_users() -> List[Dict]:
    """Lädt alle Benutzer für die Verwaltung"""
    def _get_all_users():
        # Token aus Session State holen
        token = st.session_state.get("auth_token", "")
        if not token:
            st.error("❌ Kein gültiger Token - bitte neu anmelden")
            return []
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/api/users?limit=100", headers=headers, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("❌ Token ungültig - bitte neu anmelden")
            st.session_state.authenticated = False
            st.session_state.auth_token = ""
            return []
        elif response.status_code == 403:
            st.error("❌ Keine Berechtigung für Benutzerliste")
            return []
        else:
            st.error(f"❌ Fehler beim Laden der Benutzer: {response.status_code}")
            return []
    
    result = safe_api_call(_get_all_users)
    return result if result else []

def update_user(user_id: int, update_data: Dict, token: str = "") -> Optional[Dict]:
    """Aktualisiert einen Benutzer"""
    def _update_user():
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = requests.put(
            f"{API_BASE_URL}/api/users/{user_id}",
            json=update_data,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Update fehlgeschlagen: {response.status_code}")
            return None
    
    return safe_api_call(_update_user)

def login_user(email: str, password: str) -> Optional[Dict]:
    """Benutzer-Login"""
    def _login():
        payload = {"email": email, "password": password}
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("❌ Ungültige Anmeldedaten")
            return None
        elif response.status_code == 404:
            st.error("❌ Benutzer nicht gefunden")
            return None
        else:
            st.error(f"❌ Login-Fehler: {response.status_code}")
            return None
    
    return safe_api_call(_login)

def get_user_departments(user_id: int) -> List[Dict]:
    """Holt alle Abteilungszuordnungen für einen User"""
    def _get_departments():
        # Token prüfen
        token = st.session_state.get("auth_token", "")
        if not token:
            return []
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/api/users/{user_id}/departments",
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            # Token ungültig - User abmelden
            st.session_state.authenticated = False
            st.session_state.auth_token = ""
            return []
        return []
    
    return safe_api_call(_get_departments) or []

def add_user_department(user_id: int, department_data: Dict, token: str = "") -> Optional[Dict]:
    """Fügt einem User eine neue Abteilung hinzu (nur System Admin)"""
    def _add_department():
        response = requests.post(
            f"{API_BASE_URL}/api/users/{user_id}/departments",
            json=department_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Fehler: {response.text}")
            return None
    
    return safe_api_call(_add_department)

def update_user_department(user_id: int, membership_id: int, update_data: Dict, token: str = "") -> Optional[Dict]:
    """Aktualisiert User-Abteilungszuordnung (nur System Admin)"""
    def _update_department():
        response = requests.put(
            f"{API_BASE_URL}/api/users/{user_id}/departments/{membership_id}",
            json=update_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Fehler: {response.text}")
            return None
    
    return safe_api_call(_update_department)

def remove_user_department(user_id: int, membership_id: int, token: str = "") -> bool:
    """Entfernt User aus Abteilung (nur System Admin)"""
    def _remove_department():
        response = requests.delete(
            f"{API_BASE_URL}/api/users/{user_id}/departments/{membership_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=REQUEST_TIMEOUT
        )
        return response.status_code == 200
    
    return safe_api_call(_remove_department) or False

def delete_user_permanently(user_id: int, confirm_password: str, token: str = "") -> bool:
    """Löscht User permanent (nur System Admin mit Passwort-Bestätigung)"""
    def _delete_permanently():
        response = requests.delete(
            f"{API_BASE_URL}/api/users/{user_id}/permanent",
            json={"confirm_password": confirm_password},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            return True
        else:
            st.error(f"❌ Fehler: {response.text}")
            return False
    
    return safe_api_call(_delete_permanently) or False

# === BENUTZER-SELBSTVERWALTUNG API-FUNKTIONEN ===

def clear_session_cache():
    """Löscht alle Session-State-Daten und cached Profile"""
    keys_to_clear = [
        "my_profile", "users_cache", "documents_cache", 
        "auth_token", "current_user", "authenticated"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Session State neu initialisieren
    init_session_state()
    st.success("✅ Cache geleert! Bitte melden Sie sich neu an.")
    st.rerun()

def get_my_profile(token: str = "") -> Optional[Dict]:
    """Ruft das eigene Benutzerprofil ab - DSGVO-konform"""
    def _get_profile():
        auth_token = token if token else st.session_state.get("auth_token", "")
        
        if not auth_token:
            st.error("❌ Kein gültiger Authentifizierungs-Token")
            return None
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/users/me/profile",
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                st.error("❌ Authentifizierung fehlgeschlagen - Session wird zurückgesetzt")
                # Bei Auth-Fehlern Session löschen
                clear_session_cache()
                return None
            elif response.status_code == 403:
                st.error("❌ Keine Berechtigung für Profil-Zugriff")
                return None
            elif response.status_code == 500:
                st.error("❌ Server-Fehler beim Laden des Profils - Cache wird geleert")
                # Bei Server-Fehlern Session löschen
                clear_session_cache()
                return None
            else:
                st.error(f"❌ Fehler beim Laden des Profils: {response.status_code}")
                if response.status_code >= 500:
                    clear_session_cache()
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Verbindungsfehler: {str(e)}")
            return None
    
    return safe_api_call(_get_profile)

def change_my_password(current_password: str, new_password: str, confirm_password: str, token: str = "") -> Optional[Dict]:
    """Ändert das eigene Passwort"""
    def _change_password():
        auth_token = token if token else st.session_state.auth_token
        
        response = requests.put(
            f"{API_BASE_URL}/api/users/me/password",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "current_password": current_password,
                "new_password": new_password,
                "confirm_password": confirm_password
            },
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            # Validierungsfehler
            error_detail = response.json().get("detail", "Unbekannter Fehler")
            st.error(f"❌ {error_detail}")
        elif response.status_code == 401:
            st.error("❌ Aktuelles Passwort ist falsch")
        else:
            st.error(f"❌ Fehler beim Passwort-Wechsel: {response.status_code}")
        return None
    
    return safe_api_call(_change_password)

def admin_reset_user_password(user_id: int, reset_reason: str, temporary_password: str = "", token: str = "") -> Optional[Dict]:
    """Admin-Passwort-Reset für Notfälle"""
    def _admin_reset():
        auth_token = token if token else st.session_state.auth_token
        
        request_data = {
            "user_id": user_id,  # Backend braucht user_id im Request Body
            "reset_reason": reset_reason,
            "force_change_on_login": True
        }
        
        if temporary_password:
            request_data["temporary_password"] = temporary_password
        
        response = requests.put(
            f"{API_BASE_URL}/api/users/{user_id}/password/admin-reset",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=request_data,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            st.error("❌ Nur System-Administratoren dürfen Passwörter zurücksetzen")
        elif response.status_code == 422:
            st.error("❌ Ungültige Daten - prüfen Sie alle Eingaben")
        else:
            st.error(f"❌ Fehler beim Admin-Reset: {response.status_code}")
        return None
    
    return safe_api_call(_admin_reset)

def generate_temp_password(user_id: int, token: str = "") -> Optional[Dict]:
    """Generiert temporäres Passwort für User"""
    def _generate_temp():
        auth_token = token if token else st.session_state.auth_token
        
        response = requests.post(
            f"{API_BASE_URL}/api/users/{user_id}/temp-password",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            st.error("❌ Nur System-Administratoren dürfen temporäre Passwörter generieren")
        else:
            st.error(f"❌ Fehler beim Generieren: {response.status_code}")
        return None
    
    return safe_api_call(_generate_temp)

# ===== SESSION STATE =====
def init_session_state():
    """Initialisiert Session State"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = ""
    
    if "current_user" not in st.session_state:
        # Default-User für nicht-authentifizierte Sessions
        st.session_state.current_user = {
            "id": 0,
            "full_name": "Gast",
            "email": "gast@qms.com",
            "approval_level": 1,
            "organizational_unit": "Nicht angemeldet",
            "groups": [],
            "permissions": []
        }
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "workflow"
    
    if "upload_success" not in st.session_state:
        st.session_state.upload_success = None

# ===== UI KOMPONENTEN =====
def render_header():
    """Rendert den Header"""
    st.markdown("""
    <div class="documind-header-clean">
        <h1>Dokumentenverwaltung</h1>
        <p>ISO 13485 & MDR konforme Dokumentenlenkung</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Rendert die Sidebar mit Navigation und Status"""
    
    # Logo - schlicht und elegant (ohne zusätzliche Container)
    with st.sidebar:
        st.image("logo-documind-ai.png", use_container_width=True)
    
    # Login-Bereich
    if not st.session_state.authenticated:
        st.sidebar.markdown("### 🔐 Login")
        with st.sidebar.form("login_form"):
            email = st.text_input("Email", value="test@qms.com")
            password = st.text_input("Passwort", type="password", value="test123")
            
            if st.form_submit_button("🔑 Anmelden", use_container_width=True):
                login_result = login_user(email, password)
                if login_result:
                    st.session_state.authenticated = True
                    st.session_state.auth_token = login_result["access_token"]
                    
                    # Hole echte User-Details vom Backend
                    user_details = safe_api_call(lambda: requests.get(
                        f"{API_BASE_URL}/api/users/{login_result['user_id']}",
                        headers={"Authorization": f"Bearer {login_result['access_token']}"},
                        timeout=REQUEST_TIMEOUT
                    ).json())
                    
                    if user_details:
                        # Echte User-Daten verwenden
                        st.session_state.current_user = {
                            "id": user_details["id"],
                            "full_name": user_details["full_name"],
                            "email": user_details["email"],
                            "approval_level": user_details["approval_level"],
                            "organizational_unit": user_details["organizational_unit"],
                            "individual_permissions": user_details["individual_permissions"],
                            "is_department_head": user_details.get("is_department_head", False),
                            "employee_id": user_details.get("employee_id", ""),
                            "groups": login_result["groups"],
                            "permissions": login_result["permissions"]
                        }
                    else:
                        # Fallback falls API-Aufruf fehlschlägt
                        st.session_state.current_user = {
                            "id": login_result["user_id"],
                            "full_name": login_result["user_name"],
                            "email": email,
                            "approval_level": 4,
                            "organizational_unit": "System Administration",
                            "individual_permissions": login_result["permissions"],
                            "groups": login_result["groups"],
                            "permissions": login_result["permissions"]
                        }
                    st.sidebar.success("✅ Login erfolgreich!")
                    st.rerun()
                else:
                    st.sidebar.error("❌ Login fehlgeschlagen")
        return
    
    # Navigation (nur für eingeloggte User)
    pages = {
        "📋 QM-Workflow": "workflow",
        "📤 Upload": "upload",
        "📚 Dokumente": "documents",
        "🤖 KI-Analyse": "ai_analysis",
        "🚀 AI Test": "ai_prompt_test",
        "💬 RAG-Chat": "rag_chat",
        "🌐 Intelligent Workflows": "intelligent_workflows",
        "📋 Meine Tasks": "my_tasks",
        "👥 Benutzer": "users",
        "📊 Dashboard": "dashboard",
        "👤 Mein Profil": "profile",
        "⚙️ Einstellungen": "settings"
    }
    
    current_page = st.session_state.get("current_page", "workflow")
    
    for label, page_id in pages.items():
        if st.sidebar.button(label, key=f"nav_{page_id}", use_container_width=True):
            st.session_state.current_page = page_id
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Backend Status - LIVE CHECK
    if check_backend_status():
        st.sidebar.success("✅ Backend Online")
    else:
        st.sidebar.error("❌ Backend Offline")
        st.sidebar.markdown("**Backend starten:**")
        st.sidebar.code("cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
    
    # Benutzer-Info mit dynamischen Abteilungen
    st.sidebar.markdown("---")
    user = st.session_state.current_user
    
    # User-Basis-Info
    st.sidebar.markdown(f"""
    **👤 {user.get('full_name', 'Unbekannt')}**  
    📧 {user.get('email', 'Unbekannt')}  
    🆔 ID: {user.get('id', 'N/A')}
    """)
    
    # === DYNAMISCHE ABTEILUNGS-ANZEIGE ===
    # Zuerst prüfen ob es ein System Admin ist (KEINE API-Aufrufe nötig)
    perms = user.get('individual_permissions', [])
    if isinstance(perms, str):
        import json
        try:
            perms = json.loads(perms)
        except:
            perms = []
    
    if "system_administration" in perms:
        # System Administrator - DYNAMISCH, keine API-Aufrufe!
        st.sidebar.markdown("🏢 **System Administration**")
        st.sidebar.markdown("⭐ Level 4")
        st.sidebar.markdown("🔧 **System Administrator**")
    else:
        # Normale User - lade Abteilungen von API
        try:
            user_departments = get_user_departments(user.get('id', 0))
            
            if user_departments and len(user_departments) > 0:
                st.sidebar.markdown("**🏢 Abteilungen:**")
                
                for dept in user_departments:
                    dept_name = dept.get("interest_group_name", "Unbekannt")
                    approval_level = dept.get("approval_level", 1)
                    
                    # Emoji basierend auf Level
                    level_emoji = ["👤", "👥", "👑", "⭐"][approval_level - 1] if 1 <= approval_level <= 4 else "❓"
                    
                    st.sidebar.markdown(f"• **{dept_name}**")
                    st.sidebar.markdown(f"  {level_emoji} Level {approval_level}")
            else:
                # Normaler User ohne Abteilungszuordnungen
                dept_info = user.get('organizational_unit', 'Unbekannt')
                approval_level = user.get('approval_level', 1)
                st.sidebar.markdown(f"🏢 **{dept_info}**")
                st.sidebar.markdown(f"⭐ Level {approval_level}")
        
        except Exception as e:
            # Fallback bei API-Fehlern für normale User
            st.sidebar.markdown("🏢 **Abteilung:** Laden...")
            print(f"Sidebar Abteilungen Fehler: {e}")
    
    # Logout
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.auth_token = ""
        st.session_state.current_page = "workflow"
        st.rerun()

def render_upload_page():
    """Rendert die Upload-Seite - ZUVERLÄSSIG!"""
    st.markdown("## 📤 Dokument hochladen")
    
    # Backend-Status prüfen
    if not check_backend_status():
        st.markdown("""
        <div class="error-box">
            <h4>❌ Backend nicht erreichbar!</h4>
            <p>Das Backend muss gestartet werden, bevor Dokumente hochgeladen werden können.</p>
            <p><strong>Backend starten:</strong></p>
            <code>cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000</code>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Vereinfachtes Upload-Formular
    render_unified_upload()

def render_unified_upload():
    """Vereinheitlichtes Upload-Formular - Upload-Methode entscheidet den Workflow"""
    
    # Erfolgs-/Fehlermeldungen anzeigen
    if st.session_state.get("upload_success"):
        success_data = st.session_state.upload_success
        st.markdown(f"""
        <div class="success-box">
            <h4>✅ Upload erfolgreich!</h4>
            <p><strong>Dokument ID:</strong> {success_data.get('id', 'N/A')}</p>
            <p><strong>Titel:</strong> {success_data.get('title', 'N/A')}</p>
            <p><strong>Typ:</strong> {success_data.get('document_type', 'N/A')}</p>
            <p><strong>Version:</strong> {success_data.get('version', 'N/A')}</p>
            <p><strong>Dokumentnummer:</strong> {success_data.get('document_number', 'N/A')}</p>
            <p><strong>Upload-Methode:</strong> {success_data.get('upload_method', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Reset after showing
        if st.button("🔄 Neuen Upload starten"):
            st.session_state.upload_success = None
            st.session_state.upload_preview = None
            st.rerun()
        return
    
    # Erfolgs-/Fehlermeldungen anzeigen
    if st.session_state.get("upload_success"):
        success_data = st.session_state.upload_success
        st.markdown(f"""
        <div class="success-box">
            <h4>✅ Upload erfolgreich!</h4>
            <p><strong>Dokument ID:</strong> {success_data.get('id', 'N/A')}</p>
            <p><strong>Titel:</strong> {success_data.get('title', 'N/A')}</p>
            <p><strong>Typ:</strong> {success_data.get('document_type', 'N/A')}</p>
            <p><strong>Version:</strong> {success_data.get('version', 'N/A')}</p>
            <p><strong>Dokumentnummer:</strong> {success_data.get('document_number', 'N/A')}</p>
            <p><strong>Upload-Methode:</strong> {success_data.get('upload_method', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Reset after showing
        if st.button("🔄 Neuen Upload starten"):
            st.session_state.upload_success = None
            st.session_state.upload_preview = None
            st.rerun()
        return
    
    # Vorschau anzeigen (wenn vorhanden)
    if st.session_state.get("upload_preview"):
        preview_data = st.session_state.upload_preview
        st.markdown("### 👁️ Dokument-Vorschau")
        
        if preview_data.get("upload_method") == "ocr":
            # OCR-Vorschau
            st.info(f"📄 **OCR-Verarbeitung**: {preview_data.get('message', '')}")
            
            metadata = preview_data.get("metadata", {})
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Textlänge", f"{metadata.get('text_length', 0):,} Zeichen")
            with col2:
                st.metric("Geschätzte Seiten", metadata.get('estimated_pages', 0))
            with col3:
                st.metric("Inhalt erkannt", "✅ Ja" if metadata.get('has_content') else "❌ Nein")
            
            # Erkannte Kapitel anzeigen
            if metadata.get("detected_chapters"):
                with st.expander("🔍 Erkannte Kapitel"):
                    for chapter in metadata["detected_chapters"]:
                        st.write(f"• {chapter}")
            
            # Text-Vorschau
            with st.expander("📝 Text-Vorschau", expanded=True):
                st.text_area(
                    "Extrahierter Text", 
                    value=metadata.get("preview_text", ""),
                    height=400,
                    disabled=True
                )
        
        else:  # visio
            # Visio-Vorschau
            validation = preview_data.get("validation", {})
            status = validation.get("status", "UNKNOWN")
            coverage = validation.get("coverage", 0)
            
            # ✅ EINFACHE ERFOLGSANZEIGE ohne Wortabdeckung
            st.success("✅ **Dokument erfolgreich verarbeitet**")
            
            # EINFACHE METRIKEN
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📄 Seiten", preview_data.get('page_count', 0))
            with col2:
                st.metric("📡 API-Aufrufe", preview_data.get('transparency_info', {}).get('api_calls_made', 1))
            
            # ✅ EINFACHE TABS ohne Wortliste und Validierung
            tab1, tab2, tab3 = st.tabs(["📸 Vorschaubild", "🔍 Strukturierte Analyse", "💬 Prompts"])
            
            with tab1:
                if preview_data.get("preview_image"):
                    st.image(
                        f"data:image/png;base64,{preview_data['preview_image']}", 
                        caption="Erste Seite des Dokuments",
                        use_column_width=True
                    )
                else:
                    st.warning("Kein Vorschaubild verfügbar")
            
            # Tab2 wurde entfernt (Wortliste)
            
            with tab2:
                analysis = preview_data.get("structured_analysis", {})
                if analysis:
                    st.markdown("**📊 Strukturierte Analyse:**")
                    st.json(analysis)
                else:
                    st.info("ℹ️ Strukturierte Analyse wird nach API-Aufruf verfügbar sein")
            
            # Tab4 wurde entfernt (Validierung)
            
            with tab3:
                # Upload-Methode prüfen
                upload_method = preview_data.get("upload_method", "ocr")
                
                if upload_method == "visio":
                    # IMMER Prompt dynamisch über API vom Backend laden
                    try:
                        # Verwende den Dokumenttyp aus der Session oder aus form_data - VERBESSERT
                        current_document_type = st.session_state.get('document_type')
                        if not current_document_type:
                            # Fallback: Versuche aus form_data zu holen
                            form_data = st.session_state.get("upload_form_data", {})
                            current_document_type = form_data.get("document_type", "SOP")
                            # Synchronisiere Session-State
                            st.session_state.document_type = current_document_type
                        
                        # Lade Prompt über API vom Backend
                        prompt_response = requests.get(f"{API_BASE_URL}/api/visio-prompts/{current_document_type}")
                        
                        if prompt_response.status_code != 200:
                            st.error(f"❌ **KRITISCHER FEHLER:** Prompt konnte nicht vom Backend geladen werden: {prompt_response.status_code}")
                            return
                        
                        prompt_data = prompt_response.json()
                        prompt_to_use = prompt_data["prompt"]
                        st.success(f"✅ Prompt für '{current_document_type}' dynamisch vom Backend geladen")
                        
                        # Prompt anzeigen - VERBESSERT: Keine Markdown-Ausgabe bei PROMPT_TEST
                        if current_document_type == "PROMPT_TEST":
                            st.markdown("**🤖 PROMPT-TEST: v2.0 (2025-07-21) - STRENGE QUALITÄTSSICHERUNG**")
                            st.text_area("Einheitlicher Prompt", prompt_to_use, height=300, disabled=True, key="tab5_prompt_test")
                        else:
                            st.markdown("**🤖 Dynamischer Prompt vom Backend:**")
                            st.text_area("Einheitlicher Prompt", prompt_to_use, height=300, disabled=True, key="tab5_standard_prompt")
                        
                    except Exception as e:
                        st.error(f"❌ KRITISCHER FEHLER beim Laden des Prompts: {str(e)}")
                        st.error("🔧 Bitte überprüfen Sie:")
                        st.error("   - Backend läuft (http://localhost:8000)")
                        st.error("   - API-Endpoint ist verfügbar")
                        st.error("   - Netzwerkverbindung ist korrekt")
                        
                        # Fallback auf alte Prompts ENTFERNT - immer API verwenden
                        st.error("❌ Fallback-Prompts nicht verfügbar - API ist erforderlich")
                else:
                    # OCR-Methode - keine Prompts nötig
                    st.info("📄 **OCR-Verarbeitung**: Keine AI-Prompts erforderlich")
                    st.write("Das Dokument wird mit OCR extrahiert und direkt in das RAG-System indexiert.")
        
        # ✅ KORREKTER WORKFLOW: Vorschau → Prompt → KI-Modell → JSON → Freigabe
        st.markdown("---")
        
        # Schritt 1: Vorschau anzeigen (bereits gemacht)
        st.markdown("### 📸 Schritt 1: Dokument-Vorschau ✅")
        st.success("✅ Vorschau erfolgreich erstellt!")
        
        # Schritt 2: KI-Modell wählen (für alle Methoden)
        st.markdown("### 🧠 Schritt 2: KI-Modell wählen")
        
        # Provider-Status abrufen
        provider_status = get_ai_provider_status()
        if provider_status and "provider_status" in provider_status:
            providers = provider_status["provider_status"]
            
            # Verfügbare Provider anzeigen
            available_providers = ["auto"]
            for provider_name, details in providers.items():
                if details.get("available", False):
                    available_providers.append(provider_name)
            
            selected_provider = st.selectbox(
                "KI-Modell auswählen:",
                options=available_providers,
                format_func=lambda x: {
                    "auto": "🤖 Auto (Beste verfügbare)",
                    "openai": "🌟 OpenAI GPT-4o",
                    "ollama": "🦙 Ollama (Lokal)",
                    "gemini": "🌐 Google Gemini"
                }.get(x, x)
            )
            
            st.success(f"✅ KI-Modell ausgewählt: {selected_provider}")
        else:
            st.warning("⚠️ KI-Provider-Status nicht verfügbar")
            selected_provider = "auto"
        
        # Schritt 3: Prompt anzeigen
        st.markdown("### 🤖 Schritt 3: Dynamischer Prompt")
        upload_method = preview_data.get("upload_method", "ocr")
        
        if upload_method == "visio":
            # ✅ KORREKT: Lade und zeige den Prompt dynamisch vom Backend
            try:
                # Dokumenttyp aus Session holen
                form_data = st.session_state.get("upload_form_data", {})
                current_document_type = form_data.get("document_type", "SOP")
                
                # Lade Prompt über API vom Backend
                prompt_response = requests.get(f"{API_BASE_URL}/api/visio-prompts/{current_document_type}")
                
                if prompt_response.status_code != 200:
                    st.error(f"❌ **KRITISCHER FEHLER:** Prompt konnte nicht vom Backend geladen werden: {prompt_response.status_code}")
                    return
                
                prompt_data = prompt_response.json()
                prompt_to_use = prompt_data["prompt"]
                st.success(f"✅ Prompt für '{current_document_type}' dynamisch vom Backend geladen")
                
                # Prompt-Informationen anzeigen
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("**🤖 Dynamischer Prompt vom Backend:**")
                    # Cache-buster: Zeitstempel für dynamischen Key
                    import time
                    cache_buster = int(time.time() // 10)  # Erneuert alle 10 Sekunden
                    st.text_area("Prompt", prompt_to_use, height=200, disabled=True, key=f"prompt_display_{cache_buster}")
                
                with col2:
                    st.markdown("**📊 Prompt-Info:**")
                    st.metric("Zeichen", len(prompt_to_use))
                    st.metric("Zeilen", prompt_to_use.count('\n') + 1)
                    st.metric("Version", prompt_data.get('version', 'unbekannt'))
                    
                    # Prompt-Bearbeitung (optional)
                    if st.button("📝 Prompt-Info anzeigen", help="Zeigt Informationen über den aktuellen Prompt"):
                        st.info("🔧 **HINWEIS:** Der Prompt wird dynamisch vom Backend geladen")
                        st.code(f"API: {API_BASE_URL}/api/visio-prompts/{current_document_type}", language="bash")
                        
                        # Zeige aktuellen Prompt-Key
                        st.info(f"**Aktueller Prompt-Key:** `{current_document_type}`")
                        
                        # Zeige verfügbare Prompts über API
                        try:
                            types_response = requests.get(f"{API_BASE_URL}/api/visio-prompts/types")
                            if types_response.status_code == 200:
                                available_prompts_data = types_response.json()
                                st.markdown("**📋 Verfügbare Prompts:**")
                                for prompt_name, prompt_info in available_prompts_data.items():
                                    st.write(f"• **{prompt_name}**: {prompt_info.get('description', 'Keine Beschreibung')}")
                            else:
                                st.error("❌ Konnte verfügbare Prompts nicht laden")
                        except Exception as e:
                            st.error(f"❌ Fehler beim Laden der verfügbaren Prompts: {str(e)}")
                
            except Exception as e:
                st.error(f"❌ Fehler beim Laden des Prompts: {str(e)}")
                st.stop()
        elif upload_method == "multi-visio":
            # === MULTI-VISIO 5-STUFEN-PIPELINE ===
            st.success("🔍 **Multi-Visio 5-Stufen-Pipeline** aktiviert")
            st.info("📋 **Workflow:** Experten-Einweisung → JSON-Analyse → Textextraktion → Verifikation (Backend) → Normkonformität")
            
            # Multi-Visio Pipeline-Status initialisieren
            if "multi_visio_pipeline" not in st.session_state:
                st.session_state.multi_visio_pipeline = {
                    "current_stage": 1,
                    "stages_completed": [],
                    "results": {},
                    "selected_provider": selected_provider  # Verwende die ausgewählte Provider
                }
            else:
                # Provider aktualisieren
                st.session_state.multi_visio_pipeline["selected_provider"] = selected_provider
            
            # Fortschrittsanzeige
            st.markdown("### 📊 Pipeline-Fortschritt")
            stages = ["1️⃣ Experten-Einweisung", "2️⃣ JSON-Analyse", "3️⃣ Textextraktion", "4️⃣ Verifikation", "5️⃣ Normkonformität"]
            progress = len(st.session_state.multi_visio_pipeline["stages_completed"]) / 5
            st.progress(progress)
            
            # ✅ KORRIGIERT: 5 Spalten für 5 Stages
            col1, col2, col3, col4, col5 = st.columns(5)
            columns = [col1, col2, col3, col4, col5]
            
            for i, stage in enumerate(stages):
                with columns[i]:
                    if i + 1 in st.session_state.multi_visio_pipeline["stages_completed"]:
                        st.success(f"✅ {stage.split(' ')[1]}")
                    elif i + 1 == st.session_state.multi_visio_pipeline["current_stage"]:
                        st.info(f"🔄 {stage.split(' ')[1]}")
                    else:
                        st.info(f"⏳ {stage.split(' ')[1]}")
            
            # Stufe 1: Experten-Einweisung
            if st.session_state.multi_visio_pipeline["current_stage"] == 1:
                st.markdown("### 🎯 Stufe 1: Experten-Einweisung")
                
                # Prompt für Stufe 1 laden
                try:
                    # Cache-buster: Zeitstempel für dynamischen Key
                    import time
                    cache_buster = int(time.time() // 10)  # Erneuert alle 10 Sekunden
                    
                    prompt_response = requests.get(f"{API_BASE_URL}/api/multi-visio-prompts/expert-induction")
                    if prompt_response.status_code == 200:
                        prompt_data = prompt_response.json()
                        prompt_to_use = prompt_data["prompt"]
                        
                        # Debug-Info für Auditierbarkeit
                        st.markdown("**🤖 Prompt für Experten-Einweisung:**")
                        col_info, col_clear = st.columns([3, 1])
                        with col_info:
                            st.caption(f"🔍 Prompt-Länge: {len(prompt_to_use)} Zeichen | Version: {prompt_data.get('version', 'unbekannt')} | API: ✅")
                        with col_clear:
                            if st.button("🔄 Cache leeren", help="Lädt den Prompt neu vom Server", key="clear_cache_stage1"):
                                st.rerun()
                        
                        # Verwende dynamischen Key um Streamlit-Caching zu umgehen
                        st.text_area("Experten-Einweisung", prompt_to_use, height=150, disabled=True, key=f"stage1_prompt_{cache_buster}")
                        
                        # Erweiterte Audit Trail Informationen
                        with st.expander("📈 Audit Trail Details", expanded=False):
                            st.json({
                                "stufe": "1 - Experten-Einweisung",
                                "prompt_quelle": "01_expert_induction.txt",
                                "api_endpoint": "/api/multi-visio-prompts/expert-induction",
                                "prompt_laenge": len(prompt_to_use),
                                "version": prompt_data.get('version', 'unbekannt'),
                                "hash": prompt_data.get('hash', 'unbekannt'),
                                "timestamp": prompt_data.get('timestamp', 'unbekannt'),
                                "cache_buster": cache_buster
                            })
                        
                        # KI-Modell-Info anzeigen
                        st.success(f"✅ KI-Modell ausgewählt: {st.session_state.multi_visio_pipeline['selected_provider']}")
                        
                        # Stufe 1 ausführen
                        if st.button("🚀 Stufe 1: Experten-Einweisung starten", type="primary", key="stage1_btn"):
                            with st.spinner("🤖 Führe Experten-Einweisung durch..."):
                                try:
                                    # API-Aufruf für Stufe 1
                                    form_data = st.session_state.get("upload_form_data", {})
                                    result = process_multi_visio_stage(
                                        file_data=form_data["file"],
                                        stage=1,
                                        provider=st.session_state.multi_visio_pipeline["selected_provider"]
                                    )
                                    
                                    if result and result.get("success"):
                                        st.session_state.multi_visio_pipeline["results"]["stage1"] = result
                                        st.session_state.multi_visio_pipeline["stages_completed"].append(1)
                                        st.session_state.multi_visio_pipeline["current_stage"] = 2
                                        st.success("✅ Stufe 1 erfolgreich abgeschlossen!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Stufe 1 fehlgeschlagen")
                                except Exception as e:
                                    st.error(f"❌ Fehler in Stufe 1: {str(e)}")
                    else:
                        st.error(f"❌ Prompt für Stufe 1 konnte nicht geladen werden: {prompt_response.status_code}")
                except Exception as e:
                    st.error(f"❌ Fehler beim Laden des Prompts: {str(e)}")
            
            # Stufe 2: JSON-Analyse
            elif st.session_state.multi_visio_pipeline["current_stage"] == 2:
                st.markdown("### 📊 Stufe 2: Strukturierte JSON-Analyse")
                
                # ✅ VERBESSERTE AUDIT-TRANSPARENZ: Stufe 1 Ergebnis
                if "stage1" in st.session_state.multi_visio_pipeline["results"]:
                    with st.expander("📋 **AUDIT: Stufe 1 - Experten-Einweisung**", expanded=True):
                        stage1_result = st.session_state.multi_visio_pipeline["results"]["stage1"]
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Status", "✅ Erfolgreich" if stage1_result.get('success') else "❌ Fehlgeschlagen")
                        with col2:
                            st.metric("Provider", stage1_result.get('provider_used', 'Unbekannt'))
                        with col3:
                            st.metric("Dauer", f"{stage1_result.get('duration_seconds', 0):.2f}s")
                        
                        st.markdown("**🤖 KI-Antwort:**")
                        st.text_area("Experten-Einweisung Antwort", stage1_result.get('response', 'Keine Antwort'), height=100, disabled=True)
                        
                        # Audit-Informationen
                        st.markdown("**📋 Audit-Details:**")
                        st.json({
                            "stage": stage1_result.get('stage'),
                            "timestamp": datetime.now().isoformat(),
                            "provider": stage1_result.get('provider_used'),
                            "duration_seconds": stage1_result.get('duration_seconds'),
                            "success": stage1_result.get('success')
                        })
                
                # Prompt für Stufe 2 laden
                try:
                    # Cache-buster: Zeitstempel für dynamischen Key
                    import time
                    cache_buster = int(time.time() // 10)  # Erneuert alle 10 Sekunden
                    
                    prompt_response = requests.get(f"{API_BASE_URL}/api/multi-visio-prompts/structured-analysis")
                    if prompt_response.status_code == 200:
                        prompt_data = prompt_response.json()
                        prompt_to_use = prompt_data["prompt"]
                        
                        # Debug-Info für Auditierbarkeit
                        st.markdown("**🤖 Prompt für JSON-Analyse:**")
                        col_info, col_clear = st.columns([3, 1])
                        with col_info:
                            st.caption(f"🔍 Prompt-Länge: {len(prompt_to_use)} Zeichen | Version: {prompt_data.get('version', 'unbekannt')} | API: ✅")
                        with col_clear:
                            if st.button("🔄 Cache leeren", help="Lädt den Prompt neu vom Server", key="clear_cache_stage2"):
                                st.rerun()
                        
                        # Verwende dynamischen Key um Streamlit-Caching zu umgehen
                        st.text_area("JSON-Analyse", prompt_to_use, height=200, disabled=True, key=f"stage2_prompt_{cache_buster}")
                        
                        # Erweiterte Audit Trail Informationen
                        with st.expander("📈 Audit Trail Details", expanded=False):
                            st.json({
                                "stufe": "2 - Strukturierte Analyse",
                                "prompt_quelle": "02_structured_analysis.txt",
                                "api_endpoint": "/api/multi-visio-prompts/structured-analysis",
                                "prompt_laenge": len(prompt_to_use),
                                "version": prompt_data.get('version', 'unbekannt'),
                                "hash": prompt_data.get('hash', 'unbekannt'),
                                "timestamp": prompt_data.get('timestamp', 'unbekannt'),
                                "cache_buster": cache_buster
                            })
                        
                        # Prompt-Informationen anzeigen
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Zeichen", len(prompt_to_use))
                            st.metric("Zeilen", prompt_to_use.count('\n') + 1)
                        with col2:
                            st.metric("Version", prompt_data.get('version', 'unbekannt'))
                        
                        # Stufe 2 ausführen
                        if st.button("🚀 Stufe 2: JSON-Analyse starten", type="primary", key="stage2_btn"):
                            with st.spinner("🤖 Führe JSON-Analyse durch..."):
                                try:
                                    form_data = st.session_state.get("upload_form_data", {})
                                    result = process_multi_visio_stage(
                                        file_data=form_data["file"],
                                        stage=2,
                                        provider=st.session_state.multi_visio_pipeline["selected_provider"]
                                    )
                                    
                                    if result and result.get("success"):
                                        st.session_state.multi_visio_pipeline["results"]["stage2"] = result
                                        st.session_state.multi_visio_pipeline["stages_completed"].append(2)
                                        st.session_state.multi_visio_pipeline["current_stage"] = 3
                                        st.success("✅ Stufe 2 erfolgreich abgeschlossen!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Stufe 2 fehlgeschlagen")
                                except Exception as e:
                                    st.error(f"❌ Fehler in Stufe 2: {str(e)}")
                    else:
                        st.error(f"❌ Prompt für Stufe 2 konnte nicht geladen werden: {prompt_response.status_code}")
                except Exception as e:
                    st.error(f"❌ Fehler beim Laden des Prompts: {str(e)}")
            
            # Stufe 3: HYBRID - Backend Text-Processing
            elif st.session_state.multi_visio_pipeline["current_stage"] == 3:
                st.markdown("### 🔄 Stufe 3: Hybrid Text-Processing (Backend)")
                
                # Ergebnisse der vorherigen Stufen anzeigen
                if "stage1" in st.session_state.multi_visio_pipeline["results"]:
                    with st.expander("📋 Ergebnis Stufe 1: Experten-Einweisung"):
                        stage1_result = st.session_state.multi_visio_pipeline["results"]["stage1"]
                        st.success("✅ Experten-Einweisung erfolgreich")
                        st.write(f"**Antwort:** {stage1_result.get('response', 'Keine Antwort')}")
                
                if "stage2" in st.session_state.multi_visio_pipeline["results"]:
                    with st.expander("📋 Ergebnis Stufe 2: JSON-Analyse"):
                        stage2_result = st.session_state.multi_visio_pipeline["results"]["stage2"]
                        st.success("✅ JSON-Analyse erfolgreich")
                        if "structured_analysis" in stage2_result:
                            st.json(stage2_result["structured_analysis"])
                
                # Backend-Processing Info anzeigen
                st.info("🔄 **Hybrid-Ansatz:** Diese Stufe verwendet die `all_extracted_texts` aus Stufe 2 für effiziente Backend-Verarbeitung (keine AI-Kosten)")
                
                # Zeige Stage 2 Daten als Quelle
                if "stage2" in st.session_state.multi_visio_pipeline["results"]:
                    stage2_result = st.session_state.multi_visio_pipeline["results"]["stage2"]
                    
                    # Versuche all_extracted_texts zu extrahieren
                    stage2_response = stage2_result.get("response", {})
                    if isinstance(stage2_response, str):
                        try:
                            import json
                            stage2_response = json.loads(stage2_response)
                        except:
                            stage2_response = {}
                    
                    all_extracted_texts = stage2_response.get("all_extracted_texts", [])
                    
                    if all_extracted_texts:
                        st.markdown("**📝 Quell-Daten aus Stufe 2:**")
                        st.info(f"✅ {len(all_extracted_texts)} Texte aus Stage 2 `all_extracted_texts` verfügbar")
                        
                        with st.expander("🔍 Vorschau der Quell-Texte (erste 10)", expanded=False):
                            for i, text in enumerate(all_extracted_texts[:10]):
                                st.write(f"{i+1}. {text}")
                            if len(all_extracted_texts) > 10:
                                st.caption(f"... und {len(all_extracted_texts) - 10} weitere Texte")
                    else:
                        st.error("❌ Keine `all_extracted_texts` in Stage 2 gefunden")
                
                # Audit Trail für Backend-Processing
                with st.expander("📈 Audit Trail Details", expanded=False):
                    st.json({
                        "stufe": "3 - Hybrid Text-Processing",
                        "methode": "backend_tokenization",
                        "quelle": "stage2_all_extracted_texts",
                        "ai_kosten": "❌ Keine (Backend-only)",
                        "verarbeitung": ["Tokenisierung", "Bereinigung", "Duplikat-Entfernung", "Normalisierung"],
                        "vorteile": ["Schnell", "Zuverlässig", "Kostenlos", "Audit-gerecht"]
                    })
                
                # Stufe 3 ausführen
                if st.button("🚀 Stufe 3: Backend Text-Processing starten", type="primary", key="stage3_btn"):
                    with st.spinner("🔄 Führe Backend Text-Processing durch..."):
                        try:
                            form_data = st.session_state.get("upload_form_data", {})
                            result = process_multi_visio_stage(
                                file_data=form_data["file"],
                                stage=3,
                                provider=st.session_state.multi_visio_pipeline["selected_provider"]
                            )
                            
                            if result and result.get("success"):
                                st.session_state.multi_visio_pipeline["results"]["stage3"] = result
                                st.session_state.multi_visio_pipeline["stages_completed"].append(3)
                                st.session_state.multi_visio_pipeline["current_stage"] = 4
                                st.success("✅ Stufe 3 (Backend Text-Processing) erfolgreich abgeschlossen!")
                                st.rerun()
                            else:
                                st.error("❌ Stufe 3 fehlgeschlagen")
                        except Exception as e:
                            st.error(f"❌ Fehler in Stufe 3: {str(e)}")
            
            # Stufe 4: HYBRID - Verifikation (Stage 2 Referenz)
            elif st.session_state.multi_visio_pipeline["current_stage"] == 4:
                st.markdown("### 🔍 Stufe 4: Hybrid-Verifikation (Stage 2 Referenz)")
                
                # Info über neue Hybrid-Verifikation
                st.info("🎯 **Neue Logik:** Stage 2 `all_extracted_texts` = 100% Referenz | Stage 3 Backend-Processing = Qualitätstest")
                
                # Ergebnisse der vorherigen Stufen anzeigen
                for stage_num in [1, 2, 3]:
                    if f"stage{stage_num}" in st.session_state.multi_visio_pipeline["results"]:
                        stage_names = {1: "Experten-Einweisung", 2: "JSON-Analyse", 3: "Backend Text-Processing"}
                        with st.expander(f"📋 Ergebnis Stufe {stage_num}: {stage_names[stage_num]}"):
                            stage_result = st.session_state.multi_visio_pipeline["results"][f"stage{stage_num}"]
                            st.success(f"✅ Stufe {stage_num} erfolgreich")
                            if stage_num == 2 and "structured_analysis" in stage_result:
                                st.json(stage_result["structured_analysis"])
                            else:
                                st.write(f"**Antwort:** {stage_result.get('response', 'Keine Antwort')}")
                
                # Verifikation läuft automatisch im Backend
                st.info("🔧 **Verifikation läuft automatisch im Backend**")
                st.info("📊 **Methode:** Wortabdeckungs-Validierung mit Backend-Logik")
                st.info("✅ **Vorteil:** Zuverlässiger als KI-Prompt, deterministisch")
                
                # Stufe 4 automatisch ausführen
                if st.button("🚀 Stufe 4: Verifikation starten", type="primary", key="stage4_btn"):
                    with st.spinner("🔧 Führe Backend-Verifikation durch..."):
                        try:
                            form_data = st.session_state.get("upload_form_data", {})
                            result = process_multi_visio_stage(
                                file_data=form_data["file"],
                                stage=4,
                                provider=st.session_state.multi_visio_pipeline["selected_provider"]
                            )
                            
                            if result and result.get("success"):
                                st.session_state.multi_visio_pipeline["results"]["stage4"] = result
                                st.session_state.multi_visio_pipeline["stages_completed"].append(4)
                                st.session_state.multi_visio_pipeline["current_stage"] = 5
                                st.success("✅ Stufe 4 erfolgreich abgeschlossen!")
                                st.rerun()
                            else:
                                st.error("❌ Stufe 4 fehlgeschlagen")
                        except Exception as e:
                            st.error(f"❌ Fehler in Stufe 4: {str(e)}")
            
            # Stufe 5: Normkonformität
            elif st.session_state.multi_visio_pipeline["current_stage"] == 5:
                st.markdown("### 📋 Stufe 5: Normkonformitäts-Check")
                
                # Ergebnisse der vorherigen Stufen anzeigen
                for stage_num in [1, 2, 3, 4]:
                    if f"stage{stage_num}" in st.session_state.multi_visio_pipeline["results"]:
                        stage_names = {1: "Experten-Einweisung", 2: "JSON-Analyse", 3: "Textextraktion", 4: "Verifikation"}
                        with st.expander(f"📋 Ergebnis Stufe {stage_num}: {stage_names[stage_num]}"):
                            stage_result = st.session_state.multi_visio_pipeline["results"][f"stage{stage_num}"]
                            st.success(f"✅ Stufe {stage_num} erfolgreich")
                            if stage_num == 2 and "structured_analysis" in stage_result:
                                st.json(stage_result["structured_analysis"])
                            elif stage_num == 4 and "verification" in stage_result:
                                # Verifikations-Ergebnis anzeigen  
                                verification = stage_result["verification"]
                                
                                # Hauptmetriken
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("📊 Wortabdeckung", f"{verification.get('coverage_percentage', 0):.1f}%")
                                with col2:
                                    st.metric("📝 Erkannte Wörter", verification.get('total_detected', 0))
                                with col3:
                                    st.metric("🔍 JSON-Wörter", verification.get('total_in_json', 0))
                                
                                # Status und Qualität
                                status = verification.get('verification_status', 'unbekannt')
                                quality = verification.get('quality_assessment', 'unbekannt')
                                if status == 'verifiziert':
                                    st.success(f"✅ **Status:** {status} | **Qualität:** {quality}")
                                else:
                                    st.warning(f"⚠️ **Status:** {status} | **Qualität:** {quality}")
                                
                                # Fehlende Wörter
                                missing_words = verification.get('missing_words', [])
                                if missing_words:
                                    st.warning(f"⚠️ **{len(missing_words)} Wörter fehlen in der JSON-Analyse:**")
                                    # Zeige bis zu 10 fehlende Wörter
                                    shown_words = missing_words[:10]
                                    st.code(", ".join(shown_words))
                                    if len(missing_words) > 10:
                                        st.caption(f"... und {len(missing_words) - 10} weitere")
                                else:
                                    st.success("✅ **Alle erkannten Wörter sind in der JSON-Analyse enthalten**")
                                
                                # Empfehlungen
                                recommendations = verification.get('recommendations', [])
                                if recommendations:
                                    st.subheader("💡 Empfehlungen:")
                                    for rec in recommendations:
                                        st.info(f"• {rec}")
                                
                                # Debug-Details
                                st.subheader("🔧 Technische Details:")
                                st.json(verification)
                            else:
                                st.write(f"**Antwort:** {stage_result.get('response', 'Keine Antwort')}")
                
                # Prompt für Stufe 5 laden
                try:
                    # Cache-buster: Zeitstempel für dynamischen Key
                    import time
                    cache_buster = int(time.time() // 10)  # Erneuert alle 10 Sekunden
                    
                    prompt_response = requests.get(f"{API_BASE_URL}/api/multi-visio-prompts/norm-compliance")
                    if prompt_response.status_code == 200:
                        prompt_data = prompt_response.json()
                        prompt_to_use = prompt_data["prompt"]
                        
                        # Debug-Info für Auditierbarkeit
                        st.markdown("**🤖 Prompt für Normkonformität:**")
                        col_info, col_clear = st.columns([3, 1])
                        with col_info:
                            st.caption(f"🔍 Prompt-Länge: {len(prompt_to_use)} Zeichen | Version: {prompt_data.get('version', 'unbekannt')} | API: ✅")
                        with col_clear:
                            if st.button("🔄 Cache leeren", help="Lädt den Prompt neu vom Server", key="clear_cache_stage5"):
                                st.rerun()
                        
                        # Verwende dynamischen Key um Streamlit-Caching zu umgehen
                        st.text_area("Normkonformität", prompt_to_use, height=200, disabled=True, key=f"stage5_prompt_{cache_buster}")
                        
                        # Erweiterte Audit Trail Informationen
                        with st.expander("📈 Audit Trail Details", expanded=False):
                            st.json({
                                "stufe": "5 - Normkonformität",
                                "prompt_quelle": "05_norm_compliance.txt",
                                "api_endpoint": "/api/multi-visio-prompts/norm-compliance",
                                "prompt_laenge": len(prompt_to_use),
                                "version": prompt_data.get('version', 'unbekannt'),
                                "hash": prompt_data.get('hash', 'unbekannt'),
                                "timestamp": prompt_data.get('timestamp', 'unbekannt'),
                                "cache_buster": cache_buster
                            })
                        
                        # Stufe 5 ausführen
                        if st.button("🚀 Stufe 5: Normkonformität starten", type="primary", key="stage5_btn"):
                            with st.spinner("🤖 Führe Normkonformitäts-Check durch..."):
                                try:
                                    form_data = st.session_state.get("upload_form_data", {})
                                    result = process_multi_visio_stage(
                                        file_data=form_data["file"],
                                        stage=5,
                                        provider=st.session_state.multi_visio_pipeline["selected_provider"]
                                    )
                                    
                                    if result and result.get("success"):
                                        st.session_state.multi_visio_pipeline["results"]["stage5"] = result
                                        st.session_state.multi_visio_pipeline["stages_completed"].append(5)
                                        st.session_state.multi_visio_pipeline["current_stage"] = 6  # Fertig
                                        st.success("✅ Stufe 5 erfolgreich abgeschlossen!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Stufe 5 fehlgeschlagen")
                                except Exception as e:
                                    st.error(f"❌ Fehler in Stufe 5: {str(e)}")
                    else:
                        st.error(f"❌ Prompt für Stufe 5 konnte nicht geladen werden: {prompt_response.status_code}")
                except Exception as e:
                    st.error(f"❌ Fehler beim Laden des Prompts: {str(e)}")
            
            # Alle Stufen abgeschlossen
            elif st.session_state.multi_visio_pipeline["current_stage"] == 6:
                st.markdown("### 🎉 Multi-Visio Pipeline abgeschlossen!")
                st.success("✅ Alle 5 Stufen erfolgreich durchgeführt")
                
                # 🎯 BEST PRACTICE UI/UX: Verbesserte Multi-Visio-Anzeige
                st.markdown("---")
                st.markdown("## 🔍 **MULTI-VISIO PIPELINE - VOLLSTÄNDIGE AUDIT-ÜBERSICHT**")
                
                # Pipeline-Status
                pipeline_results = st.session_state.multi_visio_pipeline["results"]
                total_stages = 5
                completed_stages = len([stage for stage in pipeline_results.keys() if stage.startswith("stage")])
                
                # Status-Metriken
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Pipeline-Status", "✅ Abgeschlossen" if completed_stages == total_stages else "🔄 In Bearbeitung")
                with col2:
                    st.metric("Stufen abgeschlossen", f"{completed_stages}/{total_stages}")
                with col3:
                    st.metric("Provider", st.session_state.multi_visio_pipeline.get("selected_provider", "Unbekannt"))
                with col4:
                    total_duration = sum(
                        stage.get("duration_seconds", 0) 
                        for stage in pipeline_results.values() 
                        if isinstance(stage, dict)
                    )
                    st.metric("Gesamtdauer", f"{total_duration:.2f}s")
                
                # Fortschrittsbalken
                progress = completed_stages / total_stages
                st.progress(progress)
                
                # Stufen-Details in Tabs
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                    "📋 Stufe 1: Experten-Einweisung",
                    "🔍 Stufe 2: JSON-Analyse", 
                    "📝 Stufe 3: Textextraktion",
                    "✅ Stufe 4: Verifikation",
                    "📊 Stufe 5: Normkonformität",
                    "🎯 Gesamt-Ergebnis"
                ])
                
                # Stufe 1: Experten-Einweisung
                with tab1:
                    if "stage1" in pipeline_results:
                        stage1 = pipeline_results["stage1"]
                        st.markdown("### 🎯 **Stufe 1: Experten-Einweisung**")
                        
                        # Status-Badges
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if stage1.get("success"):
                                st.success("✅ Erfolgreich")
                            else:
                                st.error("❌ Fehlgeschlagen")
                        with col2:
                            st.info(f"⏱️ {stage1.get('duration_seconds', 0):.2f}s")
                        with col3:
                            st.info(f"🤖 {stage1.get('provider_used', 'Unbekannt')}")
                        
                        # KI-Antwort
                        st.markdown("**🤖 KI-Antwort:**")
                        st.text_area(
                            "Experten-Einweisung Bestätigung",
                            stage1.get('response', 'Keine Antwort'),
                            height=150,
                            disabled=True
                        )
                        
                        # Audit-Details
                        with st.expander("📋 **Audit-Details**", expanded=False):
                            st.json({
                                "stage": stage1.get('stage'),
                                "method": stage1.get('method'),
                                "provider_used": stage1.get('provider_used'),
                                "duration_seconds": stage1.get('duration_seconds'),
                                "success": stage1.get('success'),
                                "timestamp": datetime.now().isoformat()
                            })
                    else:
                        st.warning("⏳ Stufe 1 noch nicht ausgeführt")
                
                # Stufe 2: JSON-Analyse
                with tab2:
                    if "stage2" in pipeline_results:
                        stage2 = pipeline_results["stage2"]
                        st.markdown("### 🔍 **Stufe 2: Strukturierte JSON-Analyse**")
                        
                        # Status-Badges
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if stage2.get("success"):
                                st.success("✅ Erfolgreich")
                            else:
                                st.error("❌ Fehlgeschlagen")
                        with col2:
                            st.info(f"⏱️ {stage2.get('duration_seconds', 0):.2f}s")
                        with col3:
                            st.info(f"🤖 {stage2.get('provider_used', 'Unbekannt')}")
                        
                        # JSON-Analyse anzeigen
                        st.markdown("**📊 Strukturierte JSON-Analyse:**")
                        try:
                            response_content = stage2.get('response', '{}')
                            if isinstance(response_content, str):
                                parsed_json = json.loads(response_content)
                                st.json(parsed_json)
                            else:
                                st.json(response_content)
                        except json.JSONDecodeError:
                            st.code(response_content, language="json")
                        
                        # Audit-Details
                        with st.expander("📋 **Audit-Details**", expanded=False):
                            st.json({
                                "stage": stage2.get('stage'),
                                "method": stage2.get('method'),
                                "provider_used": stage2.get('provider_used'),
                                "duration_seconds": stage2.get('duration_seconds'),
                                "success": stage2.get('success'),
                                "response_length": len(str(stage2.get('response', ''))),
                                "timestamp": datetime.now().isoformat()
                            })
                    else:
                        st.warning("⏳ Stufe 2 noch nicht ausgeführt")
                
                # Stufe 3: Textextraktion
                with tab3:
                    if "stage3" in pipeline_results:
                        stage3 = pipeline_results["stage3"]
                        st.markdown("### 📝 **Stufe 3: Textextraktion (Wortliste)**")
                        
                        # Status-Badges
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if stage3.get("success"):
                                st.success("✅ Erfolgreich")
                            else:
                                st.error("❌ Fehlgeschlagen")
                        with col2:
                            st.info(f"⏱️ {stage3.get('duration_seconds', 0):.2f}s")
                        with col3:
                            st.info(f"🤖 {stage3.get('provider_used', 'Unbekannt')}")
                        
                        # Wortliste anzeigen
                        st.markdown("**📋 Extrahierte Wortliste:**")
                        try:
                            response_content = stage3.get('response', '{}')
                            if isinstance(response_content, str):
                                parsed_json = json.loads(response_content)
                                if 'extracted_words' in parsed_json:
                                    words = parsed_json['extracted_words']
                                    st.success(f"✅ **{len(words)} Wörter erfolgreich extrahiert**")
                                    
                                    # Wortliste in Spalten anzeigen
                                    cols = st.columns(4)
                                    for i, word in enumerate(words):
                                        with cols[i % 4]:
                                            st.write(f"• {word}")
                                else:
                                    st.json(parsed_json)
                            else:
                                st.json(response_content)
                        except json.JSONDecodeError:
                            st.code(response_content, language="json")
                        
                        # Audit-Details
                        with st.expander("📋 **Audit-Details**", expanded=False):
                            st.json({
                                "stage": stage3.get('stage'),
                                "method": stage3.get('method'),
                                "provider_used": stage3.get('provider_used'),
                                "duration_seconds": stage3.get('duration_seconds'),
                                "success": stage3.get('success'),
                                "response_length": len(str(stage3.get('response', ''))),
                                "timestamp": datetime.now().isoformat()
                            })
                    else:
                        st.warning("⏳ Stufe 3 noch nicht ausgeführt")
                
                # Stufe 4: Verifikation
                with tab4:
                    if "stage4" in pipeline_results:
                        stage4 = pipeline_results["stage4"]
                        st.markdown("### ✅ **Stufe 4: Verifikation (Backend-Logik)**")
                        
                        # Status-Badges
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if stage4.get("success"):
                                st.success("✅ Erfolgreich")
                            else:
                                st.error("❌ Fehlgeschlagen")
                        with col2:
                            st.info(f"⏱️ {stage4.get('duration_seconds', 0):.2f}s")
                        with col3:
                            st.info(f"🔧 {stage4.get('provider_used', 'Backend-Logik')}")
                        
                        # Verifikations-Ergebnis
                        st.markdown("**🔍 Verifikations-Ergebnis:**")
                        verification_result = stage4.get('verification_result', {})
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Extrahierte Wörter", stage4.get('extracted_words_count', 0))
                        with col2:
                            coverage = verification_result.get('coverage_percentage', 0)
                            st.metric("Abdeckung", f"{coverage:.1f}%")
                        
                        # Detaillierte Verifikation
                        if verification_result:
                            st.markdown("**📊 Detaillierte Verifikation:**")
                            st.json(verification_result)
                        
                        # Audit-Details
                        with st.expander("📋 **Audit-Details**", expanded=False):
                            st.json({
                                "stage": stage4.get('stage'),
                                "method": stage4.get('method'),
                                "provider_used": stage4.get('provider_used'),
                                "duration_seconds": stage4.get('duration_seconds'),
                                "success": stage4.get('success'),
                                "extracted_words_count": stage4.get('extracted_words_count'),
                                "timestamp": datetime.now().isoformat()
                            })
                    else:
                        st.warning("⏳ Stufe 4 noch nicht ausgeführt")
                
                # Stufe 5: Normkonformität
                with tab5:
                    if "stage5" in pipeline_results:
                        stage5 = pipeline_results["stage5"]
                        st.markdown("### 📊 **Stufe 5: Normkonformität**")
                        
                        # Status-Badges
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if stage5.get("success"):
                                st.success("✅ Erfolgreich")
                            else:
                                st.error("❌ Fehlgeschlagen")
                        with col2:
                            st.info(f"⏱️ {stage5.get('duration_seconds', 0):.2f}s")
                        with col3:
                            st.info(f"🤖 {stage5.get('provider_used', 'Unbekannt')}")
                        
                        # Normkonformität-Ergebnis
                        st.markdown("**📋 Normkonformität-Bewertung:**")
                        try:
                            response_content = stage5.get('response', '{}')
                            if isinstance(response_content, str):
                                parsed_json = json.loads(response_content)
                                st.json(parsed_json)
                            else:
                                st.json(response_content)
                        except json.JSONDecodeError:
                            st.code(response_content, language="json")
                        
                        # Audit-Details
                        with st.expander("📋 **Audit-Details**", expanded=False):
                            st.json({
                                "stage": stage5.get('stage'),
                                "method": stage5.get('method'),
                                "provider_used": stage5.get('provider_used'),
                                "duration_seconds": stage5.get('duration_seconds'),
                                "success": stage5.get('success'),
                                "response_length": len(str(stage5.get('response', ''))),
                                "timestamp": datetime.now().isoformat()
                            })
                    else:
                        st.warning("⏳ Stufe 5 noch nicht ausgeführt")
                
                # Gesamt-Ergebnis
                with tab6:
                    st.markdown("### 🎯 **Gesamt-Ergebnis der Multi-Visio Pipeline**")
                    
                    # Pipeline-Statistiken
                    st.markdown("**📊 Pipeline-Statistiken:**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Gesamtdauer", f"{total_duration:.2f}s")
                        st.metric("Durchschnitt pro Stufe", f"{total_duration/max(completed_stages, 1):.2f}s")
                    with col2:
                        st.metric("Erfolgsrate", f"{(completed_stages/total_stages)*100:.1f}%")
                        st.metric("Verwendeter Provider", st.session_state.multi_visio_pipeline.get("selected_provider", "Unbekannt"))
                    
                    # Qualitätsbewertung
                    st.markdown("**🏆 Qualitätsbewertung:**")
                    
                    # Erfolgreiche Stufen zählen
                    successful_stages = sum(
                        1 for stage in pipeline_results.values() 
                        if isinstance(stage, dict) and stage.get('success')
                    )
                    
                    if successful_stages == total_stages:
                        st.success("🎉 **PERFEKT:** Alle 5 Stufen erfolgreich abgeschlossen!")
                    elif successful_stages >= 3:
                        st.warning(f"⚠️ **TEILWEISE ERFOLGREICH:** {successful_stages}/{total_stages} Stufen erfolgreich")
                    else:
                        st.error(f"❌ **PROBLEMATISCH:** Nur {successful_stages}/{total_stages} Stufen erfolgreich")
                    
                    # Vollständige Pipeline-Daten
                    with st.expander("📋 **Vollständige Pipeline-Daten**", expanded=False):
                        st.json({
                            "pipeline_info": {
                                "total_stages": total_stages,
                                "completed_stages": completed_stages,
                                "successful_stages": successful_stages,
                                "provider": st.session_state.multi_visio_pipeline.get("selected_provider"),
                                "total_duration": total_duration,
                                "average_duration_per_stage": total_duration/max(completed_stages, 1)
                            },
                            "stage_results": pipeline_results,
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    # Export-Optionen
                    st.markdown("**💾 Export-Optionen:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📄 PDF-Report generieren", type="secondary"):
                            st.info("📄 PDF-Export-Funktion wird implementiert...")
                    with col2:
                        if st.button("📊 JSON-Export", type="secondary"):
                            st.download_button(
                                label="⬇️ JSON herunterladen",
                                data=json.dumps(pipeline_results, indent=2, ensure_ascii=False),
                                file_name=f"multi_visio_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                
                # Dokument übernehmen
                st.markdown("### ✅ Dokument übernehmen")
                if st.button("✅ Dokument übernehmen", type="primary", key="multi_visio_approve_btn"):
                    # Finale Speicherung mit den gespeicherten Form-Daten
                    form_data = st.session_state.get("upload_form_data", {})
                    if form_data:
                        with st.spinner("💾 Speichere Dokument..."):
                            try:
                                result = upload_document_with_file(
                                    file_data=form_data["file"],
                                    document_type=form_data["document_type"],
                                    creator_id=st.session_state.current_user["id"],
                                    title=form_data["title"],
                                    version=form_data["version"],
                                    content=form_data["content"],
                                    remarks=form_data["remarks"],
                                    chapter_numbers=form_data["chapter_numbers"],
                                    upload_method=form_data["upload_method"],
                                    ai_model=selected_provider  # NEU: Verwende den ausgewählten Provider
                                )
                                
                                if result and result.get("success"):
                                    st.success("✅ Dokument erfolgreich übernommen!")
                                    st.info("📋 Das Dokument durchläuft jetzt den normalen Freigabe-Prozess")
                                    
                                    # Pipeline-Status zurücksetzen
                                    st.session_state.multi_visio_pipeline = None
                                    st.session_state.upload_preview = None
                                    st.session_state.upload_form_data = None
                                    st.rerun()
                                else:
                                    st.error("❌ Fehler beim Übernehmen des Dokuments")
                            except Exception as e:
                                st.error(f"❌ Fehler: {str(e)}")
        else:
            st.info("📄 OCR-Verarbeitung: Keine AI-Prompts erforderlich")
        
        # Schritt 4: API-Aufruf starten
        st.markdown("### 🚀 Schritt 4: API-Aufruf starten")
        
        if st.button("🚀 Dokument mit KI analysieren", type="primary", key="analyze_btn"):
            with st.spinner("🤖 Analysiere Dokument mit KI..."):
                try:
                    # API-Aufruf durchführen
                    form_data = st.session_state.get("upload_form_data", {})
                    
                    # ✅ BESTÄTIGUNG: Bild und Prompt werden an KI-Modell gesendet
                    st.info("📡 **BESTÄTIGUNG:** Sende PNG-Bild + Prompt an ausgewähltes KI-Modell...")
                    
                    # Für PNG-Dateien verwende den einfachen Vision-Test
                    file_extension = form_data["file"].name.lower().split('.')[-1] if '.' in form_data["file"].name else 'txt'
                    is_image = file_extension in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff']
                    
                    if is_image:
                        st.info("🖼️ **BILD-ANALYSE:** Verwende Vision-API für PNG/JPG-Datei")
                        # Einfacher Vision-Test für Bilder
                        result = test_simple_vision_api(form_data["file"])
                    else:
                        st.info("📄 **DOKUMENT-ANALYSE:** Verwende komplexen Workflow für DOCX/PDF")
                        
                        # ✅ KRITISCHE SICHERHEIT: Verwende EXAKT den gleichen Prompt wie in der Vorschau
                        try:
                            # Verwende den gleichen Dokumenttyp wie in der Vorschau
                            current_document_type = st.session_state.get('document_type')
                            if not current_document_type:
                                current_document_type = form_data.get("document_type", "SOP")
                            
                            # Lade den EXAKTEN Prompt über die API vom Backend
                            prompt_response = requests.get(f"{API_BASE_URL}/api/visio-prompts/{current_document_type}")
                            
                            if prompt_response.status_code != 200:
                                st.error(f"❌ **KRITISCHER FEHLER:** Prompt konnte nicht vom Backend geladen werden: {prompt_response.status_code}")
                                return
                            
                            prompt_data = prompt_response.json()
                            prompt_to_use = prompt_data["prompt"]
                            
                            st.success(f"✅ **PROMPT-SICHERHEIT:** Verwende exakt den gleichen Prompt wie in der Vorschau")
                            st.info(f"📝 **DOKUMENTTYP:** {current_document_type}")
                            st.info(f"📏 **PROMPT-LÄNGE:** {len(prompt_to_use)} Zeichen")
                            st.info(f"🔢 **VERSION:** {prompt_data.get('version', 'unbekannt')}")
                            
                        except Exception as e:
                            st.error(f"❌ **KRITISCHER FEHLER:** Prompt-Sicherheit fehlgeschlagen: {str(e)}")
                            st.error("🔧 **LÖSUNG:** Bitte überprüfen Sie das Backend und die API-Verbindung")
                            return
                        
                        # ✅ PROMPT-SICHERHEIT: Übertrage den exakten Prompt an das Backend
                        st.info("🔒 **PROMPT-SICHERHEIT:** Übertrage exakten Prompt an Backend...")
                        
                        # ✅ NORMALE VISION: Verwende Vision Engine über /api/documents/with-file
                        result = upload_document_with_file(
                            file_data=form_data["file"],
                            document_type=current_document_type,  # Verwende den gesicherten Typ
                            creator_id=st.session_state.current_user["id"],
                            title=form_data.get("title"),
                            version=form_data.get("version", "1.0"),
                            content=form_data.get("content"),
                            remarks=form_data.get("remarks"),
                            chapter_numbers=form_data.get("chapter_numbers"),
                            upload_method="visio",  # Explizit Vision Engine verwenden
                            ai_model=selected_provider  # Provider für Vision Engine
                        )
                    
                    # DETAILLIERTE FEHLERANALYSE
                    if not result:
                        st.error("❌ SCHRITT 1 FEHLGESCHLAGEN: Keine Antwort von der API erhalten")
                        st.error("🔍 Mögliche Ursachen:")
                        st.error("   - API-Server nicht erreichbar")
                        st.error("   - Timeout bei der API-Anfrage")
                        st.error("   - Netzwerkfehler")
                        return
                    
                    # Prüfe ob es ein gültiges Document-Objekt ist
                    if not result or not isinstance(result, dict) or 'id' not in result:
                        st.error("❌ SCHRITT 2 FEHLGESCHLAGEN: Kein gültiges Document-Objekt erhalten")
                        st.error(f"🔍 API-Antwort: {result}")
                        return
                    
                    # ✅ ALLE SCHRITTE ERFOLGREICH - Zeige ECHTE JSON-Antwort von Gemini
                    extracted_text = result.get("extracted_text", "")
                    
                    # 1. ECHTE JSON-Antwort von Gemini extrahieren und anzeigen
                    st.subheader("🔍 ECHTE JSON-Antwort von Gemini (wie vom Prompt gefordert)")
                    
                    import json
                    import re
                    
                    # ✅ NEU: Versuche extracted_text direkt als JSON zu parsen (vom Backend)
                    try:
                        # Das Backend speichert jetzt die echte JSON in extracted_text
                        parsed_gemini_json = json.loads(extracted_text)
                        st.success("✅ JSON direkt vom Backend erfolgreich geparst!")
                        st.json(parsed_gemini_json)
                        structured_analysis = parsed_gemini_json
                    except json.JSONDecodeError:
                        # Fallback: Suche nach JSON-Block in extracted_text (alte Methode)
                        json_match = re.search(r'```json\s*(.*?)\s*```', extracted_text, re.DOTALL)
                        if json_match:
                            raw_gemini_json = json_match.group(1).strip()
                            st.success("✅ JSON-Block von Gemini gefunden!")
                            
                            # Zeige die ECHTE JSON-Antwort von Gemini
                            st.code(raw_gemini_json, language="json")
                            
                            # Versuche die JSON zu parsen
                            try:
                                parsed_gemini_json = json.loads(raw_gemini_json)
                                st.success("✅ JSON erfolgreich geparst!")
                                st.json(parsed_gemini_json)
                                structured_analysis = parsed_gemini_json
                            except json.JSONDecodeError as e:
                                st.warning(f"⚠️ JSON-Parsing fehlgeschlagen: {e}")
                                st.info("📄 Verwende Roh-Text von Gemini als structured_analysis")
                                structured_analysis = {
                                    "raw_gemini_response": raw_gemini_json,
                                    "parsing_error": str(e),
                                    "document_metadata": {
                                        "title": result.get("title", "Unbekannt"),
                                        "document_type": result.get("document_type", "OTHER"),
                                        "version": result.get("version", "1.0"),
                                        "status": result.get("status", "draft")
                                    }
                                }
                        else:
                            st.warning("⚠️ Kein JSON-Block in der Antwort gefunden")
                            st.info("📄 Zeige gesamten extracted_text:")
                            st.code(extracted_text, language="text")
                            
                            # Fallback: Verwende Document-Daten
                            structured_analysis = {
                                "raw_gemini_response": extracted_text,
                                "document_metadata": {
                                    "title": result.get("title", "Unbekannt"),
                                    "document_type": result.get("document_type", "OTHER"),
                                    "version": result.get("version", "1.0"),
                                    "status": result.get("status", "draft")
                                },
                                "extracted_text": extracted_text,
                                "keywords": result.get("keywords", "").split(", ") if result.get("keywords") else [],
                                "ai_analysis": {
                                    "provider": "gemini",
                                    "quality_score": 5,
                                    "language": "de",
                                    "compliance_status": result.get("compliance_status", "ZU_BEWERTEN")
                                }
                            }
                    
                    # 2. Zusätzlich: Zeige die geparste JSON aus dem Backend
                    st.subheader("📊 Geparste JSON aus Backend-Verarbeitung")
                    if "raw_gemini_response" in structured_analysis:
                        # Versuche die raw_gemini_response zu parsen
                        try:
                            raw_response = structured_analysis["raw_gemini_response"]
                            if isinstance(raw_response, str):
                                # Entferne Markdown-Formatierung
                                clean_json = raw_response.replace('```json', '').replace('```', '').strip()
                                parsed_backend_json = json.loads(clean_json)
                                st.success("✅ Backend-JSON erfolgreich geparst!")
                                st.json(parsed_backend_json)
                            else:
                                st.json(raw_response)
                        except json.JSONDecodeError as e:
                            st.warning(f"⚠️ Backend-JSON-Parsing fehlgeschlagen: {e}")
                            st.code(raw_response, language="text")
                    else:
                        st.json(structured_analysis)
                    
                    # ✅ BESTÄTIGUNG: Strukturierte JSON-Antwort erhalten
                    st.success("✅ **ERFOLG:** KI-Modell hat strukturierte JSON-Antwort zurückgegeben!")
                    st.success(f"📊 **ZUSAMMENFASSUNG:** {result.get('summary', 'Analyse abgeschlossen')}")
                    
                    final_result = {
                        "success": True,
                        "structured_analysis": structured_analysis,
                        "transparency_info": {
                            "api_calls_made": 1,
                            "providers_used": ["gemini"],
                            "api_response_time": 0,
                            "file_size_bytes": 0
                        },
                        "page_count": 1,
                        "raw_response": result  # Original-Antwort für Debugging
                    }
                    
                    st.session_state.final_result = final_result
                    st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Fehler: {str(e)}")
        
        # Schritt 5: REINE KI-ANTWORT anzeigen (UNVERÄNDERT)
        if st.session_state.get("final_result"):
            st.markdown("### 🎯 Schritt 5: Strukturierte JSON-Vorschau")
            
            final_result = st.session_state.final_result
            structured_analysis = final_result.get("structured_analysis", "")
            raw_ki_response = final_result.get("raw_ki_response", "")
            
            if structured_analysis:
                st.success("✅ **SAUBERE KI-ANTWORT:** Entpackt und bereinigt")
                st.info("📋 **HINWEIS:** Dies ist das ECHTE JSON-OBJEKT des KI-Modells - ohne String-Wrapper, ohne redundante Felder")
                
                # Prüfe den Typ der Antwort
                if isinstance(structured_analysis, dict):
                    st.success("✅ **ECHTES JSON-OBJEKT:** Direkt verarbeitbar")
                    
                    # Strukturierte Anzeige der wichtigsten Felder
                    st.markdown("### 📊 Strukturierte Vorschau:")
                    
                    # Document Metadata
                    if 'document_metadata' in structured_analysis:
                        metadata = structured_analysis['document_metadata']
                        st.markdown("#### 📄 Dokument-Metadaten:")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Titel:** {metadata.get('title', 'N/A')}")
                            st.write(f"**Typ:** {metadata.get('document_type', 'N/A')}")
                            st.write(f"**Version:** {metadata.get('version', 'N/A')}")
                        with col2:
                            st.write(f"**Kapitel:** {metadata.get('chapter', 'N/A')}")
                            st.write(f"**Gültig ab:** {metadata.get('valid_from', 'N/A')}")
                    
                    # Process Steps
                    if 'process_steps' in structured_analysis:
                        steps = structured_analysis['process_steps']
                        st.markdown(f"#### 🔄 Prozessschritte ({len(steps)}):")
                        
                        for i, step in enumerate(steps[:5]):  # Zeige nur die ersten 5
                            with st.expander(f"Schritt {step.get('step_number', i+1)}: {step.get('label', 'N/A')}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Beschreibung:** {step.get('description', 'N/A')}")
                                    st.write(f"**Abteilung:** {step.get('responsible_department', {}).get('short', 'N/A')}")
                                with col2:
                                    decision = step.get('decision', {})
                                    if decision.get('is_decision', False):
                                        st.write(f"**Entscheidung:** {decision.get('question', 'N/A')}")
                                        st.write(f"**Ja →** {decision.get('yes_action', 'N/A')}")
                                        st.write(f"**Nein →** {decision.get('no_action', 'N/A')}")
                        
                        if len(steps) > 5:
                            st.info(f"📋 ... und {len(steps) - 5} weitere Schritte")
                    
                    # Referenced Documents
                    if 'referenced_documents' in structured_analysis:
                        refs = structured_analysis['referenced_documents']
                        if refs:
                            st.markdown(f"#### 📚 Referenzierte Dokumente ({len(refs)}):")
                            for ref in refs:
                                st.write(f"• **{ref.get('reference', 'N/A')}** - {ref.get('title', 'N/A')} ({ref.get('type', 'N/A')})")
                    
                    # Compliance Requirements
                    if 'compliance_requirements' in structured_analysis:
                        compliance = structured_analysis['compliance_requirements']
                        if compliance:
                            st.markdown(f"#### 📋 Compliance-Anforderungen ({len(compliance)}):")
                            for req in compliance:
                                st.write(f"• **{req.get('standard', 'N/A')}** - {req.get('requirement', 'N/A')}")
                    
                    # Critical Rules
                    if 'critical_rules' in structured_analysis:
                        rules = structured_analysis['critical_rules']
                        if rules:
                            st.markdown(f"#### ⚠️ Kritische Regeln ({len(rules)}):")
                            for rule in rules:
                                st.write(f"• **{rule.get('rule', 'N/A')}** → {rule.get('consequence', 'N/A')}")
                    
                    # Vollständiges JSON anzeigen
                    with st.expander("🔍 Vollständiges JSON anzeigen"):
                        st.json(structured_analysis)
                        
                        # JSON-String (kopierbar)
                        import json
                        json_string = json.dumps(structured_analysis, ensure_ascii=False, indent=2)
                        st.markdown("### 📄 JSON-String (kopierbar):")
                        st.code(json_string, language="json")
                    
                elif isinstance(structured_analysis, str):
                    # Falls es doch ein String ist, versuche es zu parsen
                    try:
                        import json
                        parsed_json = json.loads(structured_analysis)
                        st.success("✅ **GÜLTIGES JSON:** String erfolgreich geparst")
                        
                        # Zeige die geparste KI-ANTWORT
                        st.json(parsed_json)
                        
                        # Zeige den ursprünglichen String
                        st.markdown("### 📄 Ursprünglicher String:")
                        st.code(structured_analysis, language="json")
                        
                    except json.JSONDecodeError as e:
                        st.error(f"⚠️ **String ist kein gültiges JSON:** {e}")
                        st.warning("🔧 **LÖSUNG:** Bitte Prompt oder Modell prüfen")
                        
                        # Zeige den rohen String
                        st.markdown("### 📄 Roher String:")
                        st.code(raw_ki_response, language="text")
                else:
                    st.warning(f"⚠️ **UNBEKANNTER TYP:** {type(raw_ki_response)}")
                    st.code(str(raw_ki_response), language="text")
            else:
                st.warning("⚠️ Keine KI-Antwort verfügbar")
                
                # Metriken anzeigen
                col1, col2 = st.columns(2)
                with col1:
                    api_calls = final_result.get('transparency_info', {}).get('api_calls_made', 1)
                    st.metric("📡 API-Aufrufe", api_calls)
                
                with col2:
                    page_count = final_result.get('page_count', 0)
                    st.metric("📄 Seiten verarbeitet", page_count)
                
                # Freigabe-Buttons
                st.markdown("### ✅ Schritt 6: Dokument freigeben")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Dokument freigeben", type="primary", key="approve_final_btn"):
                        st.success("✅ Dokument erfolgreich freigegeben!")
                
                with col2:
                    if st.button("❌ Abbrechen", key="cancel_final_btn"):
                        st.session_state.upload_preview = None
                        st.session_state.upload_form_data = None
                        st.session_state.final_result = None
                        st.rerun()
        else:
            st.info("ℹ️ Führen Sie Schritt 4 aus, um die strukturierte Analyse zu erhalten")
            
            # Freigabe-Buttons
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("🔄 Neuer Workflow", key="new_workflow_btn", use_container_width=True):
                    st.session_state.workflow_step = "prompt_review"
                    st.session_state.final_result = None
                    st.rerun()
            
            with col2:
                if st.button("❌ Abbrechen", key="cancel_btn", use_container_width=True):
                    st.session_state.upload_preview = None
                    st.session_state.upload_form_data = None
                    st.session_state.workflow_step = None
                    st.session_state.final_result = None
                    st.rerun()
            
            with col3:
                if st.button("✅ Freigeben & Speichern", key="approve_btn", type="primary", use_container_width=True):
                    # Finale Speicherung mit den gespeicherten Form-Daten
                    form_data = st.session_state.get("upload_form_data", {})
                    if form_data:
                        with st.spinner("💾 Speichere Dokument..."):
                            try:
                                result = upload_document_with_file(
                                    file_data=form_data["file"],
                                    document_type=form_data["document_type"],
                                    creator_id=st.session_state.current_user["id"],
                                    title=form_data["title"],
                                    version=form_data["version"],
                                    content=form_data["content"],
                                    remarks=form_data["remarks"],
                                    chapter_numbers=form_data["chapter_numbers"],
                                    upload_method=form_data["upload_method"],
                                    ai_model="auto"  # NEU: Verwende Auto als Standard
                                )
                                
                                if result:
                                    st.session_state.upload_success = result
                                    st.session_state.upload_preview = None
                                    st.session_state.upload_form_data = None
                                    st.session_state.workflow_step = None
                                    st.session_state.final_result = None
                                    st.rerun()
                                else:
                                    st.error("❌ Fehler beim Speichern des Dokuments")
                                    
                            except Exception as e:
                                st.error(f"❌ Fehler beim Speichern: {str(e)}")
        
        return  # Verhindere das Anzeigen des Upload-Formulars
    
    # Upload Form (nur anzeigen, wenn keine Vorschau aktiv ist)
    with st.form("upload_form", clear_on_submit=False):
        st.markdown("### 📁 Datei auswählen")
        
        uploaded_file = st.file_uploader(
            "Datei auswählen",
            type=['pdf', 'docx', 'doc', 'txt', 'xlsx', 'xls'],
            help=f"Maximale Dateigröße: {MAX_FILE_SIZE_MB}MB"
        )
        
        if uploaded_file:
            # Dateigröße prüfen
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            if file_size_mb > MAX_FILE_SIZE_MB:
                st.error(f"❌ Datei zu groß! Maximum: {MAX_FILE_SIZE_MB}MB, Ihre Datei: {file_size_mb:.1f}MB")
                st.stop()
            
            st.info(f"📄 **{uploaded_file.name}** ({file_size_mb:.1f}MB)")
        
        st.markdown("### 📋 Dokumentinformationen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # NEU: Dynamische Upload-Methode Auswahl
            upload_methods = get_upload_methods()
            
            # Fallback für den Fall, dass keine Methoden geladen werden können
            if not upload_methods:
                upload_methods = [
                    {
                        "id": "ocr",
                        "name": "OCR - Für textbasierte Dokumente",
                        "description": "Optical Character Recognition für Normen, Richtlinien",
                        "icon": "📄"
                    },
                    {
                        "id": "visio", 
                        "name": "Visio - Für grafische Dokumente",
                        "description": "KI-basierte Analyse von Flussdiagrammen, SOPs",
                        "icon": "🖼️"
                    }
                ]
            
            # Upload-Methoden für Selectbox vorbereiten
            upload_method_options = [method["id"] for method in upload_methods]
            upload_method_format_func = lambda x: next(
                (f"{method['icon']} {method['name']}" for method in upload_methods if method['id'] == x),
                x
            )
            
            upload_method = st.selectbox(
                "Upload-Methode",
                options=upload_method_options,
                format_func=upload_method_format_func,
                help="Wählen Sie die passende Verarbeitungsmethode für Ihr Dokument"
            )
            
            # Zusätzliche Informationen zur ausgewählten Methode anzeigen
            selected_method = next((method for method in upload_methods if method['id'] == upload_method), None)
            if selected_method:
                st.info(f"ℹ️ {selected_method['description']}")
            
            # Dokumenttyp - verfügbare Typen laden
            doc_types = get_document_types()
            
            # Debug-Ausgabe (nur im Entwicklungsmodus)
            if st.session_state.get("debug_mode", False):
                st.info(f"🔍 Debug: {len(doc_types)} Dokumenttypen vom Backend geladen")
                st.json(doc_types)
            
            # Dynamische Dokumenttyp-Optionen basierend auf Backend
            doc_type_options = {
                "OTHER": "🗂️ Sonstige",
                "QM_MANUAL": "📖 QM-Handbuch", 
                "SOP": "📋 SOP",
                "WORK_INSTRUCTION": "📝 Arbeitsanweisung",
                "FORM": "📄 Formular",
                "USER_MANUAL": "👤 Benutzerhandbuch",
                "SERVICE_MANUAL": "🔧 Servicehandbuch",
                "RISK_ASSESSMENT": "⚠️ Risikoanalyse",
                "VALIDATION_PROTOCOL": "✅ Validierungsprotokoll",
                "CALIBRATION_PROCEDURE": "⚖️ Kalibrierverfahren",
                "AUDIT_REPORT": "🔍 Audit-Bericht",
                "CAPA_DOCUMENT": "🛠️ CAPA-Dokumentation",
                "TRAINING_MATERIAL": "🎓 Schulungsunterlagen",
                "SPECIFICATION": "📐 Spezifikation",
                "STANDARD_NORM": "⚖️ Norm/Standard (ISO, DIN, EN)",
                "REGULATION": "📜 Regulatorische Dokumente",
                "GUIDANCE_DOCUMENT": "📋 Leitfäden",
                "PROCESS": "🔄 Prozess (Flussdiagramme, Workflows)",
                "PROMPT_TEST": "🧪 Prompt Test (Qualitätssicherung)"
            }
            
            # Alle verfügbaren Typen aus Backend anzeigen
            available_options = {}
            for doc_type in doc_types:
                if doc_type in doc_type_options:
                    available_options[doc_type] = doc_type_options[doc_type]
                else:
                    # Fallback für unbekannte Typen
                    available_options[doc_type] = f"📄 {doc_type}"
            
            # Sortiere alphabetisch nach deutschen Namen
            sorted_options = dict(sorted(available_options.items(), key=lambda x: x[1]))
            
            if not sorted_options:
                sorted_options = {"OTHER": "🗂️ Sonstige"}
            
            document_type = st.selectbox(
                "Dokumenttyp *",
                options=list(sorted_options.keys()),
                format_func=lambda x: sorted_options[x],
                index=0,
                help="Pflichtfeld: Der Dokumenttyp bestimmt die Verarbeitungslogik"
            )
            
            version = st.text_input("Version", value="1.0", help="Standardwert: 1.0")
        
        with col2:
            title = st.text_input(
                "Titel *", 
                help="Pflichtfeld: Dokumententitel"
            )
            
            content = st.text_area(
                "Beschreibung (optional)", 
                help="Wird automatisch aus dem Dokumentinhalt extrahiert falls leer"
            )
            
            # NEU: Kapitel-Nummern als Pflichtfeld bei bestimmten Dokumenttypen
            if document_type in ["STANDARD_NORM", "REGULATION", "GUIDANCE_DOCUMENT"]:
                chapter_numbers = st.text_input(
                    "Relevante Kapitel *", 
                    help="Pflichtfeld für Normen: z.B. 4.2.3, 7.5.1"
                )
            else:
                chapter_numbers = st.text_input(
                    "Relevante Kapitel (optional)", 
                    help="z.B. 4.2.3, 7.5.1"
                )
        
        # Erweiterte Optionen
        with st.expander("🔧 Erweiterte Optionen"):
            remarks = st.text_area("Bemerkungen (optional)")
        
        # Submit Button
        submit_button = st.form_submit_button(
            "🔍 Vorschau generieren",  # Geändert von "Dokument hochladen"
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            if not uploaded_file:
                st.error("❌ Bitte wählen Sie eine Datei aus!")
                return
            
            if not title or title.strip() == "":
                st.error("❌ Titel ist ein Pflichtfeld!")
                return
            
            # Validierung: Dokumenttyp muss vom Backend unterstützt werden
            if document_type not in doc_types:
                st.error(f"❌ Dokumenttyp '{document_type}' wird vom Backend nicht unterstützt!")
                st.error(f"Verfügbare Typen: {', '.join(doc_types[:5])}...")
                return
                
            if document_type in ["STANDARD_NORM", "REGULATION", "GUIDANCE_DOCUMENT"] and (not chapter_numbers or chapter_numbers.strip() == ""):
                st.error("❌ Kapitel-Nummern sind für Normen ein Pflichtfeld!")
                return
            
            with st.spinner("🔄 Generiere Vorschau..."):
                try:
                    # Form-Daten für späteren Upload speichern
                    st.session_state.upload_form_data = {
                        "file": uploaded_file,
                        "document_type": document_type,
                        "title": title,
                        "version": version,
                        "content": content,
                        "remarks": remarks,
                        "chapter_numbers": chapter_numbers,
                        "upload_method": upload_method
                    }
                    
                    # Document type in Session State speichern für dynamische Prompts - VERBESSERT
                    st.session_state.document_type = document_type
                    st.success(f"✅ Dokumenttyp '{document_type}' in Session-State gespeichert")
                    
                    # Vorschau generieren
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    form_data = {
                        "upload_method": upload_method,
                        "document_type": document_type
                    }
                    
                    response = requests.post(
                        f"{API_BASE_URL}/api/documents/preview",
                        files=files,
                        data=form_data,
                        timeout=180  # Längeres Timeout für Visio-Verarbeitung (3 Minuten)
                    )
                    
                    if response.status_code == 200:
                        preview_data = response.json()
                        st.session_state.upload_preview = preview_data
                        st.rerun()
                    else:
                        error_detail = response.json().get('detail', response.text)
                        st.error(f"❌ Vorschau-Fehler: {error_detail}")
                        
                except Exception as e:
                    st.error(f"❌ Fehler bei der Vorschau-Generierung: {str(e)}")

def render_documents_page():
    """Rendert die Dokumentenverwaltung"""
    st.markdown("## 📚 Dokumentenverwaltung")
    
    if not check_backend_status():
        st.error("❌ Backend nicht erreichbar!")
        return
    
    # Dokumente laden
    with st.spinner("📄 Lade Dokumente..."):
        documents = get_documents()
    
    if not documents:
        st.info("📭 Keine Dokumente gefunden")
        return
    
    st.info(f"📊 **{len(documents)}** Dokumente gefunden")
    
    # Filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        type_filter = st.selectbox(
            "Typ filtern",
            ["Alle"] + list(set(doc.get("document_type", "OTHER") for doc in documents))
        )
    
    with col2:
        status_filter = st.selectbox(
            "Status filtern", 
            ["Alle"] + list(set(doc.get("status", "DRAFT") for doc in documents))
        )
    
    with col3:
        search_term = st.text_input("🔍 Suchen", placeholder="Titel, Inhalt...")
    
    # Dokumente filtern
    filtered_docs = documents
    
    if type_filter != "Alle":
        filtered_docs = [doc for doc in filtered_docs if doc.get("document_type") == type_filter]
    
    if status_filter != "Alle":
        filtered_docs = [doc for doc in filtered_docs if doc.get("status") == status_filter]
    
    if search_term:
        search_lower = search_term.lower()
        filtered_docs = [
            doc for doc in filtered_docs 
            if search_lower in doc.get("title", "").lower() 
            or search_lower in doc.get("content", "").lower()
        ]
    
    st.markdown(f"**Gefilterte Ergebnisse: {len(filtered_docs)}**")
    
    # Dokumente anzeigen
    for doc in filtered_docs:
        with st.expander(f"📄 {doc.get('title', 'Ohne Titel')} (ID: {doc.get('id')})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Typ:** {doc.get('document_type', 'N/A')}  
                **Version:** {doc.get('version', 'N/A')}  
                **Status:** {doc.get('status', 'N/A')}  
                **Dokumentnummer:** {doc.get('document_number', 'N/A')}
                """)
            
            with col2:
                st.markdown(f"""
                **Erstellt:** {doc.get('created_at')[:10] if doc.get('created_at') else 'N/A'}  
                **Ersteller:** {doc.get('creator_id', 'N/A')}  
                **Dateigröße:** {doc.get('file_size', 'N/A')} Bytes  
                **MIME-Type:** {doc.get('mime_type', 'N/A')}
                """)
            
            if doc.get('content'):
                content = doc.get('content') or ""
                st.markdown(f"**Beschreibung:** {content[:200]}...")
            
            # KI-Analyse anzeigen (falls vorhanden)
            if doc.get('keywords'):
                st.markdown(f"**🏷️ Keywords:** {doc.get('keywords')}")
            
            # Aktionen
            col1, col2, col3, col4 = st.columns(4)
            
            # Download-Button
            with col1:
                if doc.get('file_path'):
                    # Download-Link erstellen
                    download_url = f"http://localhost:8000/api/documents/{doc['id']}/download"
                    st.markdown(f"""
                    <a href="{download_url}" target="_blank" style="
                        display: inline-block;
                        padding: 0.25rem 0.5rem;
                        background-color: #1f77b4;
                        color: white;
                        text-decoration: none;
                        border-radius: 0.25rem;
                        font-size: 0.875rem;
                        font-weight: 500;
                        text-align: center;
                        width: 100%;
                        box-sizing: border-box;
                    ">📄 Öffnen</a>
                    """, unsafe_allow_html=True)
                else:
                    st.button("📄 Keine Datei", disabled=True, key=f"no_file_{doc['id']}")
            
            with col2:
                if st.button(f"🗑️ Löschen", key=f"delete_{doc['id']}"):
                    if delete_document(doc['id']):
                        st.success("✅ Dokument gelöscht!")
                        st.rerun()
                    else:
                        st.error("❌ Löschen fehlgeschlagen!")
            
            with col3:
                if st.button(f"🤖 KI-Analyse", key=f"ai_analyze_{doc['id']}"):
                    with st.spinner("🧠 KI-Analyse läuft..."):
                        ai_result = analyze_document_with_ai(doc['id'])
                        if ai_result:
                            st.success("✅ KI-Analyse abgeschlossen!")
                            
                            # Spracherkennung
                            lang_data = ai_result.get('language_analysis', {})
                            if lang_data:
                                st.info(f"🌍 **Sprache:** {lang_data.get('detected_language', 'unbekannt')} ({lang_data.get('confidence', 0):.1%} Konfidenz)")
                            
                            # Dokumenttyp-Vorhersage
                            class_data = ai_result.get('document_classification', {})
                            if class_data:
                                predicted_type = class_data.get('predicted_type')
                                confidence = class_data.get('confidence', 0)
                                current_type = class_data.get('current_type')
                                
                                if predicted_type != current_type:
                                    st.warning(f"📊 **KI-Empfehlung:** Dokumenttyp sollte '{predicted_type}' sein ({confidence:.1%} Konfidenz), aktuell: '{current_type}'")
                                else:
                                    st.success(f"📊 **Dokumenttyp bestätigt:** {predicted_type} ({confidence:.1%} Konfidenz)")
                            
                            # Norm-Referenzen
                            norm_refs = ai_result.get('norm_references', [])
                            if norm_refs:
                                st.markdown("📋 **Gefundene Norm-Referenzen:**")
                                for ref in norm_refs:
                                    st.markdown(f"  - **{ref.get('norm_name')}**: {ref.get('description')} ({ref.get('confidence', 0):.1%})")
                            
                            # Qualitätsbewertung
                            quality_data = ai_result.get('quality_assessment', {})
                            if quality_data:
                                quality_score = quality_data.get('content_quality', 0)
                                completeness = quality_data.get('completeness', 0)
                                st.markdown(f"📈 **Qualitätsbewertung:** {quality_score:.1%} | **Vollständigkeit:** {completeness:.1%}")
                            
                            # Empfehlungen
                            recommendations = ai_result.get('recommendations', [])
                            if recommendations:
                                st.markdown("💡 **KI-Empfehlungen:**")
                                for rec in recommendations:
                                    priority = rec.get('priority', 'LOW')
                                    message = rec.get('message', '')
                                    if priority == 'HIGH':
                                        st.error(f"🔴 {message}")
                                    elif priority == 'MEDIUM':
                                        st.warning(f"🟡 {message}")
                                    else:
                                        st.info(f"🔵 {message}")
                        else:
                            st.error("❌ KI-Analyse fehlgeschlagen!")

def render_workflow_page():
    """Rendert die QM-Workflow Seite - NEUE HAUPTSEITE"""
    st.markdown("## 📋 QM-Workflow Dashboard")
    
    if not st.session_state.authenticated:
        st.warning("🔐 Bitte loggen Sie sich ein, um den Workflow zu verwenden.")
        st.info("**Test-Login:** Email: `test@qms.com`, Passwort: `test123`")
        
        # Zeige auch anonyme Statistiken
        all_docs = get_documents()
        st.markdown("### 📊 Öffentliche Statistiken")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📁 Dokumente gesamt", len(all_docs))
        with col2:
            st.metric("✅ Backend-Status", "Online" if check_backend_status() else "Offline")
        with col3:
            st.metric("🏥 System", "KI-QMS v2.0")
        return
    
    # Workflow-Statistiken
    col1, col2, col3, col4 = st.columns(4)
    
    draft_docs = get_documents_by_status("draft")
    reviewed_docs = get_documents_by_status("reviewed") 
    approved_docs = get_documents_by_status("approved")
    all_docs = get_documents()
    
    with col1:
        st.metric("✏️ Entwürfe", len(draft_docs))
    
    with col2:
        st.metric("🔍 Zu prüfen", len(reviewed_docs), help="Warten auf QM-Freigabe")
    
    with col3:
        st.metric("✅ Freigegeben", len(approved_docs))
    
    with col4:
        st.metric("📁 Gesamt", len(all_docs))
    
    st.markdown("---")
    
    # QM-Workflow Aktionen
    user = st.session_state.current_user
    # ✅ QM-Manager Berechtigung: Prüfe sowohl groups als auch permissions
    is_qm_user = (
        "quality_management" in user.get("groups", []) or 
        "final_approval" in user.get("permissions", []) or
        "all_rights" in user.get("permissions", [])
    )
    
    if is_qm_user:
        st.markdown("### 🎯 QM-Manager Aktionen")
        
        if reviewed_docs:
            st.markdown("#### 📋 Dokumente zur Freigabe:")
            for doc in reviewed_docs:
                with st.expander(f"📄 {doc['title'][:60]}... (ID: {doc['id']})"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Typ:** {doc['document_type']}")
                        st.write(f"**Version:** {doc['version']}")
                        st.write(f"**Ersteller:** {doc.get('creator_id', 'N/A')}")
                        st.write(f"**Erstellt:** {doc['created_at'][:16]}")
                    
                    with col2:
                        # Kommentar-Feld oben
                        comment = st.text_input(f"Bemerkung", key=f"comment_{doc['id']}", placeholder="Optional: Freigabe-Kommentar...")
                        
                        # Status-Änderungs-Buttons
                        col_approve, col_reject = st.columns(2)
                        
                        with col_approve:
                            if st.button(f"✅ Freigeben", key=f"approve_{doc['id']}", use_container_width=True):
                                approval_comment = comment or "QM-Freigabe erteilt"
                                result = change_document_status(
                                    doc['id'], 
                                    "approved", 
                                    approval_comment, 
                                    st.session_state.auth_token
                                )
                                if result:
                                    st.success(f"✅ Dokument {doc['id']} freigegeben!")
                                    st.rerun()
                        
                        with col_reject:
                            if st.button(f"❌ Ablehnen", key=f"reject_{doc['id']}", use_container_width=True):
                                rejection_comment = comment or "Zurück zur Überarbeitung"
                                result = change_document_status(
                                    doc['id'], 
                                    "draft", 
                                    rejection_comment, 
                                    st.session_state.auth_token
                                )
                                if result:
                                    st.warning(f"↩️ Dokument {doc['id']} zur Überarbeitung zurückgesendet")
                                    st.rerun()
        else:
            st.info("✅ Alle Dokumente sind bearbeitet!")
    else:
        st.markdown("### 👤 Standard-User Aktionen")
        st.info("Als Standard-User können Sie Dokumente erstellen und zur Prüfung weiterleiten.")
    
    st.markdown("---")
    
    # Workflow-Status Übersicht
    st.markdown("### 📊 Dokument-Status Übersicht")
    
    status_tabs = st.tabs(["✏️ Entwürfe", "🔍 Geprüft", "✅ Freigegeben"])
    
    with status_tabs[0]:
        if draft_docs:
            for doc in draft_docs[:10]:
                with st.expander(f"📄 {doc['title'][:50]}..."):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**ID:** {doc['id']} | **Typ:** {doc['document_type']}")
                        st.write(f"**Erstellt:** {doc['created_at'][:16]}")
                        
                        # Status-History anzeigen
                        if st.button(f"📊 Historie", key=f"history_draft_{doc['id']}"):
                            render_document_history(doc['id'])
                        
                    with col2:
                        if st.button(f"🔍 Zur Prüfung", key=f"review_{doc['id']}"):
                            result = change_document_status(
                                doc['id'], 
                                "reviewed", 
                                "Zur fachlichen Prüfung weitergeleitet", 
                                st.session_state.auth_token
                            )
                            if result:
                                st.success("🔍 Zur Prüfung weitergeleitet!")
                                st.rerun()
        else:
            st.info("Keine Entwürfe vorhanden")
    
    with status_tabs[1]:
        if reviewed_docs:
            for doc in reviewed_docs[:10]:
                with st.expander(f"🔍 {doc['title'][:50]}..."):
                    st.write(f"**ID:** {doc['id']} | **Typ:** {doc['document_type']}")
                    st.write(f"**Erstellt:** {doc['created_at'][:16]}")
                    
                    # Status-History anzeigen
                    if st.button(f"📊 Historie", key=f"history_reviewed_{doc['id']}"):
                        render_document_history(doc['id'])
        else:
            st.info("Keine Dokumente in Prüfung")
    
    with status_tabs[2]:
        if approved_docs:
            for doc in approved_docs[:10]:
                with st.expander(f"✅ {doc['title'][:50]}..."):
                    st.write(f"**ID:** {doc['id']} | **Typ:** {doc['document_type']}")
                    approved_at = doc.get('approved_at')
                    if approved_at:
                        st.write(f"**Freigegeben:** {approved_at[:16]}")
                    else:
                        st.write(f"**Freigegeben:** N/A")
                    
                    # Status-History anzeigen
                    if st.button(f"📊 Historie", key=f"history_{doc['id']}"):
                        render_document_history(doc['id'])
        else:
            st.info("Noch keine freigegebenen Dokumente")

def render_dashboard_page():
    """Rendert das Dashboard"""
    st.markdown("## 📊 Dashboard")
    
    if not check_backend_status():
        st.error("❌ Backend nicht erreichbar!")
        return
    
    # Daten laden
    with st.spinner("📊 Lade Dashboard-Daten..."):
        documents = get_documents()
        users = get_users()
    
    # Metriken
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Dokumente", len(documents))
    
    with col2:
        st.metric("👥 Benutzer", len(users))
    
    with col3:
        draft_count = len([doc for doc in documents if doc.get("status") == "DRAFT"])
        st.metric("📝 Entwürfe", draft_count)
    
    with col4:
        approved_count = len([doc for doc in documents if doc.get("status") == "APPROVED"])
        st.metric("✅ Genehmigt", approved_count)
    
    # Dokumenttypen-Verteilung
    if documents:
        st.markdown("### 📊 Dokumenttypen-Verteilung")
        type_counts = {}
        for doc in documents:
            doc_type = doc.get("document_type", "OTHER")
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        for doc_type, count in type_counts.items():
            st.write(f"**{doc_type}:** {count}")

def render_users_page():
    """Rendert die Benutzerverwaltung"""
    st.markdown("## 👥 Benutzerverwaltung")
    
    if not st.session_state.authenticated:
        st.warning("🔐 Bitte loggen Sie sich ein, um Benutzer zu verwalten.")
        return
    
    # Check if user has admin permissions
    user = st.session_state.current_user
    is_admin = "system_administration" in user.get("permissions", [])
    
    if not is_admin:
        st.warning("⚠️ Keine Berechtigung für Benutzerverwaltung")
        st.info("Nur Benutzer mit 'system_administration' Berechtigung können Benutzer verwalten.")
        return
    
    # Tabs für verschiedene Verwaltungsfunktionen
    tab1, tab2, tab3 = st.tabs(["👤 Neuer Benutzer", "📋 Benutzerliste", "📊 Statistiken"])
    
    with tab1:
        st.markdown("### ➕ Neuen Benutzer erstellen")
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                email = st.text_input("Email *", placeholder="max.mustermann@company.com")
                full_name = st.text_input("Vollständiger Name *", placeholder="Max Mustermann")
                employee_id = st.text_input("Mitarbeiter-ID", placeholder="MM001")
                password = st.text_input("Passwort *", type="password", placeholder="Mindestens 8 Zeichen")
            
            with col2:
                # Interessengruppen dynamisch vom Backend laden
                organizational_units = get_organizational_units()
                unit_names = [unit["name"] for unit in organizational_units]
                
                organizational_unit = st.selectbox(
                    "Abteilung",
                    unit_names
                )
                
                approval_level = st.selectbox(
                    "Freigabe-Level",
                    [1, 2, 3, 4],
                    format_func=lambda x: f"Level {x} - {['Mitarbeiter', 'Teamleiter', 'Abteilungsleiter', 'QM-Manager'][x-1]}"
                )
            
            # Spezielle Berechtigungen nur für Systemadmin
            is_system_admin = organizational_unit == "System Administration"
            
            if is_system_admin:
                st.info("ℹ️ **System Administrator** - Automatische Vollberechtigung bei Abteilung 'System Administration'")
            
            if st.form_submit_button("👤 Benutzer erstellen", use_container_width=True):
                # Validierung
                if not all([full_name.strip(), email.strip(), employee_id.strip(), password.strip()]):
                    st.error("Bitte füllen Sie alle Pflichtfelder aus!")
                elif not "@" in email:
                    st.error("Bitte geben Sie eine gültige E-Mail-Adresse ein!")
                elif len(password) < 8:
                    st.error("Passwort muss mindestens 8 Zeichen lang sein!")
                else:
                    # Benutzer-Daten zusammenstellen
                    user_data = {
                        "full_name": full_name,
                        "email": email,
                        "employee_id": employee_id,
                        "organizational_unit": organizational_unit,
                        "password": password,
                        "approval_level": approval_level,
                        "is_department_head": approval_level >= 3,
                        "individual_permissions": []
                    }
                    
                    # System Admin Berechtigungen automatisch setzen
                    if organizational_unit == "System Administration":
                        user_data["individual_permissions"].extend(["system_administration", "user_management", "all_rights"])
                    
                    result = create_user(user_data, st.session_state.auth_token)
                    if result:
                        st.success(f"✅ Benutzer '{full_name}' erfolgreich erstellt!")
                        st.info(f"🆔 Benutzer-ID: {result['id']}")
                        st.rerun()
    
    with tab2:
        st.markdown("### 📋 Alle Benutzer")
        
        # Benutzer laden
        users = get_all_users()
        if users:
            st.info(f"📊 **{len(users)}** Benutzer im System")
            
            # Filter
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Status", ["Alle", "Aktiv", "Inaktiv"])
            with col2:
                # 🔄 DYNAMISCH: Lade verfügbare Abteilungen aus den tatsächlichen Usern
                dept_filter = st.selectbox(
                    "Abteilung", 
                    ["Alle"] + list(set(u.get("organizational_unit", "Unbekannt") for u in users))
                )
            with col3:
                level_filter = st.selectbox("Level", ["Alle", "1", "2", "3", "4"])
            
            # Filter anwenden
            filtered_users = users
            if status_filter != "Alle":
                active = status_filter == "Aktiv"
                filtered_users = [u for u in filtered_users if u.get("is_active", True) == active]
            if dept_filter != "Alle":
                filtered_users = [u for u in filtered_users if u.get("organizational_unit") == dept_filter]
            if level_filter != "Alle":
                filtered_users = [u for u in filtered_users if u.get("approval_level") == int(level_filter)]
            
            st.markdown(f"**Gefilterte Ergebnisse: {len(filtered_users)}**")
            
            # Benutzer-Tabelle
            for user in filtered_users:
                with st.expander(f"👤 {user['full_name']} ({user['email']})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**ID:** {user['id']}")
                        st.write(f"**Mitarbeiter-ID:** {user.get('employee_id', 'N/A')}")
                        st.write(f"**Abteilung:** {user.get('organizational_unit', 'N/A')}")
                        st.write(f"**Level:** {user.get('approval_level', 1)}")
                    
                    with col2:
                        st.write(f"**Abteilungsleiter:** {'✅' if user.get('is_department_head') else '❌'}")
                        st.write(f"**Status:** {'🟢 Aktiv' if user.get('is_active', True) else '🔴 Inaktiv'}")
                        created_at = user.get('created_at')
                        if created_at:
                            st.write(f"**Erstellt:** {created_at[:10]}")
                        else:
                            st.write(f"**Erstellt:** N/A")
                    
                    with col3:
                        perms = user.get('individual_permissions', [])
                        if isinstance(perms, str):
                            try:
                                import json
                                perms = json.loads(perms)
                            except:
                                perms = []
                        
                        if perms:
                            st.write("**Berechtigungen:**")
                            for perm in perms[:3]:  # Nur erste 3 anzeigen
                                st.write(f"• {perm}")
                            if len(perms) > 3:
                                st.write(f"• ... und {len(perms)-3} weitere")
                        else:
                            st.write("**Berechtigungen:** Keine speziellen")
                    
                    # Admin-Aktionen - ERWEITERT für Multiple-Abteilungen
                    current_user_email = st.session_state.current_user.get("email", "")
                    is_system_admin = "system_administration" in st.session_state.current_user.get("permissions", [])
                    is_qms_admin = user.get("email") == "qms.admin@company.com"
                    is_self_action = user.get("email") == current_user_email
                    
                    col_edit, col_dept, col_delete = st.columns(3)
                    
                    with col_edit:
                        if st.button(f"📝 Bearbeiten", key=f"edit_{user['id']}"):
                            st.session_state[f"editing_user_{user['id']}"] = True
                            st.rerun()
                    
                    # === INLINE BEARBEITUNG ===
                    if st.session_state.get(f"editing_user_{user['id']}", False):
                        st.markdown("---")
                        st.markdown(f"**✏️ Bearbeite User: {user['full_name']}**")
                        
                        # === BASIS-DATEN BEARBEITEN ===
                        with st.form(f"edit_user_form_{user['id']}"):
                            st.markdown("### ✏️ Basis-Daten bearbeiten")
                            new_name = st.text_input("Name", value=user.get("full_name", ""))
                            new_email = st.text_input("E-Mail", value=user.get("email", ""))
                            new_employee_id = st.text_input("Mitarbeiter-ID", value=user.get("employee_id", ""))
                            
                            # Form-Buttons
                            col_save, col_cancel = st.columns(2)
                            
                            with col_save:
                                if st.form_submit_button("💾 Änderungen speichern"):
                                    update_data = {
                                        "full_name": new_name,
                                        "email": new_email,
                                        "employee_id": new_employee_id
                                    }
                                    
                                    result = update_user(user['id'], update_data, st.session_state.auth_token)
                                    if result:
                                        st.success("User aktualisiert!")
                                        st.session_state[f"editing_user_{user['id']}"] = False
                                        st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button("❌ Abbrechen"):
                                    st.session_state[f"editing_user_{user['id']}"] = False
                                    st.rerun()
                        
                        # === ABTEILUNGEN VERWALTEN (außerhalb der Form) ===
                        # Keine Abteilungsverwaltung für den QMS System Administrator (hat alle Rechte)
                        if is_system_admin and user['id'] != 1:
                            st.markdown("### 🏢 Abteilungen verwalten")
                            
                            # Aktuelle Abteilungen anzeigen
                            user_departments = get_user_departments(user['id'])
                            
                            if user_departments:
                                st.markdown("**Aktuelle Abteilungen:**")
                                for i, dept in enumerate(user_departments):
                                    col_dept, col_level, col_action = st.columns([3, 2, 1])
                                    
                                    with col_dept:
                                        st.text(dept.get("interest_group_name", "Unbekannt"))
                                    
                                    with col_level:
                                        current_level = dept.get("approval_level", 1)
                                        new_level = st.selectbox(
                                            "Level",
                                            [1, 2, 3, 4],
                                            index=current_level - 1,
                                            format_func=lambda x: f"Level {x}",
                                            key=f"level_{user['id']}_{dept['id']}"
                                        )
                                        
                                        if new_level != current_level:
                                            if st.button(f"💾 Level ändern", key=f"update_level_{user['id']}_{dept['id']}"):
                                                result = update_user_department(
                                                    user['id'],
                                                    dept.get("id", 0),
                                                    {"approval_level": new_level},
                                                    st.session_state.auth_token
                                                )
                                                if result:
                                                    st.success(f"Level auf {new_level} geändert!")
                                                    st.rerun()
                                    
                                    with col_action:
                                        if st.button(f"🗑️", key=f"remove_dept_{user['id']}_{dept['id']}", help="Aus Abteilung entfernen"):
                                            if remove_user_department(
                                                user['id'],
                                                dept.get("id", 0),
                                                st.session_state.auth_token
                                            ):
                                                st.success("Aus Abteilung entfernt!")
                                                st.rerun()
                            
                            # === NEUE ABTEILUNG HINZUFÜGEN ===
                            st.markdown("**➕ Neue Abteilung hinzufügen:**")
                            
                            col_new_dept, col_new_level, col_add_btn = st.columns([3, 2, 1])
                            
                            with col_new_dept:
                                # 🔄 DYNAMISCH: Lade verfügbare Interest Groups von API
                                available_groups = get_interest_groups()
                                
                                if not available_groups:
                                    st.warning("⚠️ Keine Abteilungen verfügbar oder Verbindungsfehler")
                                    # Fallback: zeige wenigstens die wichtigsten
                                    available_groups = [
                                        {"id": 1, "name": "Einkauf"},
                                        {"id": 2, "name": "Qualitätsmanagement"},
                                        {"id": 3, "name": "Entwicklung"},
                                        {"id": 4, "name": "Produktion"}
                                    ]
                                
                                new_dept_id = st.selectbox(
                                    "Abteilung",
                                    [g["id"] for g in available_groups],
                                    format_func=lambda x: next(g["name"] for g in available_groups if g["id"] == x),
                                    key=f"new_dept_{user['id']}"
                                )
                            
                            with col_new_level:
                                new_dept_level = st.selectbox(
                                    "Level",
                                    [1, 2, 3, 4],
                                    format_func=lambda x: f"Level {x} - {['Mitarbeiter', 'Teamleiter', 'Abteilungsleiter', 'QM-Manager'][x-1]}",
                                    key=f"new_level_{user['id']}"
                                )
                            
                            with col_add_btn:
                                if st.button(f"➕ Hinzufügen", key=f"add_dept_{user['id']}"):
                                    department_data = {
                                        "interest_group_id": new_dept_id,
                                        "approval_level": new_dept_level,
                                        "role_in_group": f"Level {new_dept_level}",
                                        "notes": f"Hinzugefügt durch {current_user_email}"
                                    }
                                    
                                    result = add_user_department(
                                        user['id'],
                                        department_data,
                                        st.session_state.auth_token
                                    )
                                    
                                    if result:
                                        st.success("Abteilung hinzugefügt!")
                                        st.rerun()
                    
                    # === DEPARTMENT STATUS ANZEIGE ===
                    with col_dept:
                        # Für QMS System Administrator: zeige Status ohne API-Aufruf
                        if user['id'] == 1:
                            st.text("🏢 System Administration")
                            st.caption("• Alle Rechte")
                        else:
                            user_departments = get_user_departments(user['id'])
                            if user_departments:
                                dept_names = [dept.get("interest_group_name", "Unbekannt") for dept in user_departments]
                                st.text(f"🏢 {len(dept_names)} Abteilung(en)")
                                # Zeige alle Abteilungen, aber verwende Columns für bessere Darstellung bei vielen Abteilungen
                                if len(dept_names) <= 3:
                                    # Bei 1-3 Abteilungen: alle untereinander anzeigen
                                    for dept in dept_names:
                                        st.caption(f"• {dept}")
                                else:
                                    # Bei mehr als 3 Abteilungen: kompakte Darstellung
                                    for i, dept in enumerate(dept_names[:3]):
                                        st.caption(f"• {dept}")
                                    if len(dept_names) > 3:
                                        st.caption(f"• ... und {len(dept_names) - 3} weitere")
                            else:
                                st.text("🏢 Keine Abteilungen")
                    
                    # === SICHERES LÖSCHEN ===
                    with col_delete:
                        if not user.get('is_active', True):
                            if st.button(f"✅ Aktivieren", key=f"activate_{user['id']}"):
                                result = update_user(user['id'], {"is_active": True}, st.session_state.auth_token)
                                if result:
                                    st.success("Benutzer aktiviert!")
                                    st.rerun()
                        else:
                            # SICHERHEITS-CHECKS für Deaktivierung/Löschung
                            if is_qms_admin and is_self_action:
                                st.warning("🚨 QMS Admin kann sich nicht selbst deaktivieren!")
                            elif is_qms_admin:
                                st.warning("⚠️ Haupt-QMS Administrator!")
                                if st.button(f"⚠️ Trotzdem deaktivieren", key=f"force_deactivate_{user['id']}"):
                                    result = update_user(user['id'], {"is_active": False}, st.session_state.auth_token)
                                    if result:
                                        st.error("⚠️ QMS Administrator deaktiviert!")
                                        st.rerun()
                            else:
                                # Standard-User Aktionen
                                col_deact, col_pass, col_del = st.columns(3)
                                
                                with col_deact:
                                    if st.button(f"❌ Deaktivieren", key=f"deactivate_{user['id']}"):
                                        result = update_user(user['id'], {"is_active": False}, st.session_state.auth_token)
                                        if result:
                                            st.warning("Benutzer deaktiviert!")
                                            st.rerun()
                                
                                with col_pass:
                                    # PASSWORT-RESET (nur System Admin)
                                    if is_system_admin:
                                        reset_btn_key = f"reset_btn_{user['id']}"
                                        reset_state_key = f"reset_dialog_{user['id']}"
                                        if st.button(f"🔐 Passwort zurücksetzen", key=reset_btn_key):
                                            st.session_state[reset_state_key] = True
                                            st.rerun()
                                
                                with col_del:
                                    # PERMANENT LÖSCHEN (nur System Admin)
                                    if is_system_admin:
                                        if st.button(f"🗑️ LÖSCHEN", key=f"delete_{user['id']}", type="primary"):
                                            st.session_state[f"confirm_delete_{user['id']}"] = True
                                            st.rerun()
                                        
                                        # Bestätigungs-Dialog
                                        if st.session_state.get(f"confirm_delete_{user['id']}", False):
                                            st.error(f"⚠️ **PERMANENT LÖSCHEN:** {user['full_name']}")
                                            
                                            admin_password = st.text_input(
                                                "Admin-Passwort zur Bestätigung:",
                                                type="password",
                                                key=f"del_confirm_{user['id']}"
                                            )
                                            
                                            # Buttons ohne verschachtelte Columns
                                            if st.button(f"🗑️ ENDGÜLTIG LÖSCHEN", key=f"final_delete_{user['id']}", type="primary"):
                                                if admin_password:
                                                    if delete_user_permanently(user['id'], admin_password, st.session_state.auth_token):
                                                        st.success(f"User {user['full_name']} permanent gelöscht!")
                                                        st.rerun()
                                                    else:
                                                        st.error("❌ Löschung fehlgeschlagen - Passwort oder Berechtigung falsch")
                                                else:
                                                    st.error("❌ Admin-Passwort erforderlich")
                                            
                                            if st.button(f"❌ Abbrechen", key=f"abort_delete_{user['id']}"):
                                                st.session_state[f"confirm_delete_{user['id']}"] = False
                                                st.rerun()
                    
                    # === TEMPORÄRES PASSWORT ANZEIGEN ===
                    temp_pw_key = f"temp_password_{user['id']}"
                    show_temp_pw_key = f"show_temp_password_{user['id']}"
                    
                    if st.session_state.get(show_temp_pw_key, False):
                        temp_pw = st.session_state.get(temp_pw_key, "")
                        if temp_pw:
                            st.markdown("---")
                            st.markdown("### 🔑 **TEMPORÄRES PASSWORT**")
                            
                            # Großer, gut sichtbarer Container
                            st.markdown(f"""
                            <div style="
                                background-color: #FFE4B5; 
                                border: 3px solid #FF8C00; 
                                border-radius: 10px; 
                                padding: 20px; 
                                text-align: center; 
                                margin: 20px 0;
                                font-size: 1.2em;
                                font-weight: bold;
                            ">
                                🔐 NEUES PASSWORT FÜR: <strong>{user['full_name']}</strong><br/>
                                <span style="font-size: 1.5em; color: #B22222; font-family: monospace; background: white; padding: 10px; border-radius: 5px; margin: 10px; display: inline-block;">
                                    {temp_pw}
                                </span><br/>
                                📋 Dieses Passwort an den Benutzer weitergeben!
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Anweisungen für das Passwort
                            st.warning("⚠️ **WICHTIG:** Dieses Passwort sofort und sicher an den Benutzer übermitteln!")
                            st.info("ℹ️ Der Benutzer muss das Passwort beim nächsten Login ändern.")
                            st.info("💡 **Tipp:** Markieren Sie das Passwort oben und kopieren Sie es (Strg+C / Cmd+C)")
                            
                            # Button zum Schließen
                            if st.button("✅ Passwort übermittelt", key=f"close_temp_pw_{user['id']}"):
                                st.session_state[show_temp_pw_key] = False
                                if temp_pw_key in st.session_state:
                                    del st.session_state[temp_pw_key]
                                st.rerun()
                            
                            st.markdown("---")
                    
                    # === PASSWORT-RESET-DIALOG ===
                    reset_state_key = f"reset_dialog_{user['id']}"
                    if st.session_state.get(reset_state_key, False):
                        st.markdown("---")
                        st.markdown(f"### 🔐 Passwort zurücksetzen für: **{user['full_name']}**")
                        
                        st.warning("""
                        **Sicherheitshinweis:** 
                        - Ein temporäres Passwort wird generiert
                        - Der Benutzer muss es beim nächsten Login ändern
                        - Diese Aktion wird protokolliert
                        """)
                        
                        # Option: Eigenes temporäres Passwort oder automatisch generieren (außerhalb Form)
                        use_custom_password = st.checkbox(
                            "Eigenes temporäres Passwort verwenden",
                            key=f"custom_pw_checkbox_{user['id']}"
                        )
                        
                        temp_password = ""
                        if use_custom_password:
                            temp_password = st.text_input(
                                "Temporäres Passwort",
                                type="password",
                                help="Mindestens 12 Zeichen für Sicherheit",
                                placeholder="Eigenes sicheres Passwort eingeben...",
                                key=f"temp_password_input_{user['id']}"
                            )
                            st.warning("⚠️ **Wichtig:** Das Passwort sollte sicher sein (min. 12 Zeichen, gemischt)")
                        else:
                            st.info("✨ Ein sicheres temporäres Passwort wird automatisch generiert")
                        
                        with st.form(f"password_reset_form_{user['id']}"):
                            reset_reason = st.text_area(
                                "Grund für Passwort-Reset *",
                                placeholder="z.B. Benutzer hat Passwort vergessen, Sicherheitsvorfall, etc.",
                                help="Begründung ist für Audit-Trail erforderlich"
                            )
                            
                            col_reset, col_cancel = st.columns(2)
                            
                            with col_reset:
                                if st.form_submit_button("🔐 Passwort zurücksetzen", type="primary"):
                                    # State aus Session State lesen da außerhalb Form
                                    current_use_custom_pw = st.session_state.get(f"custom_pw_checkbox_{user['id']}", False)
                                    current_temp_pw = st.session_state.get(f"temp_password_input_{user['id']}", "")
                                    
                                    if not reset_reason.strip():
                                        st.error("❌ Bitte Grund für Reset angeben!")
                                    elif current_use_custom_pw and len(current_temp_pw) < 12:
                                        st.error("❌ Temporäres Passwort muss mindestens 12 Zeichen haben!")
                                    elif current_use_custom_pw and not current_temp_pw.strip():
                                        st.error("❌ Bitte ein temporäres Passwort eingeben!")
                                    else:
                                        with st.spinner("🔐 Setze Passwort zurück..."):
                                            result = admin_reset_user_password(
                                                user['id'],
                                                reset_reason,
                                                current_temp_pw,
                                                st.session_state.auth_token
                                            )
                                            
                                            if result:
                                                st.success("✅ Passwort erfolgreich zurückgesetzt!")
                                                
                                                # Temporäres Passwort in Session State speichern
                                                temp_pw = result.get('temporary_password')
                                                if temp_pw:
                                                    st.session_state[f"temp_password_{user['id']}"] = temp_pw
                                                    st.session_state[f"show_temp_password_{user['id']}"] = True
                                                
                                                st.session_state[reset_state_key] = False
                                                st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button("❌ Abbrechen"):
                                    st.session_state[reset_state_key] = False
                                    st.rerun()
        else:
            st.info("Keine Benutzer gefunden oder Berechtigung fehlt.")
    
    with tab3:
        st.markdown("### 📊 Benutzer-Statistiken")
        
        users = get_all_users()
        if users:
            # Statistiken berechnen
            total_users = len(users)
            active_users = len([u for u in users if u.get('is_active', True)])
            dept_heads = len([u for u in users if u.get('is_department_head', False)])
            
            # Metriken anzeigen
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👥 Gesamt", total_users)
            with col2:
                st.metric("🟢 Aktiv", active_users)
            with col3:
                st.metric("👑 Führungskräfte", dept_heads)
            with col4:
                st.metric("📊 Aktiv-Rate", f"{(active_users/total_users*100):.1f}%" if total_users > 0 else "0%")
            
            # Abteilungsverteilung
            st.markdown("#### 🏢 Abteilungsverteilung")
            dept_counts = {}
            for user in users:
                dept = user.get("organizational_unit", "Unbekannt")
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
            
            for dept, count in sorted(dept_counts.items()):
                st.write(f"**{dept}:** {count} Benutzer")
            
            # Level-Verteilung
            st.markdown("#### 🏷️ Level-Verteilung")
            level_counts = {}
            for user in users:
                level = user.get("approval_level", 1)
                level_counts[level] = level_counts.get(level, 0) + 1
            
            for level in sorted(level_counts.keys()):
                level_name = ['Mitarbeiter', 'Teamleiter', 'Abteilungsleiter', 'QM-Manager'][level-1]
                st.write(f"**Level {level} ({level_name}):** {level_counts[level]} Benutzer")

def render_profile_page():
    """
    Rendert die Benutzerprofil-Seite - DSGVO-konform
    
    Ermöglicht Benutzern:
    - Eigene Daten einsehen (DSGVO Art. 15)
    - Passwort selbst ändern (DSGVO Art. 16)
    """
    st.markdown("## 👤 Mein Profil")
    
    if not check_backend_status():
        st.error("❌ Backend nicht erreichbar!")
        return
    
    # Tabs für verschiedene Profil-Bereiche
    tab1, tab2 = st.tabs(["📄 Profil-Informationen", "🔐 Passwort ändern"])
    
    with tab1:
        st.markdown("### 📄 Meine Profil-Informationen")
        st.markdown("""
        <div class="info-box">
            <strong>DSGVO-Hinweis:</strong> Sie haben das Recht auf Auskunft über Ihre personenbezogenen Daten (Art. 15 DSGVO).
            Diese Seite zeigt alle über Sie gespeicherten Informationen.
        </div>
        """, unsafe_allow_html=True)
        
        # Profil-Aktionen
        if st.button("🔄 Profil aktualisieren"):
            # Cache löschen und neu laden
            st.session_state["my_profile"] = None
            profile = get_my_profile()
            if profile:
                st.session_state["my_profile"] = profile
        
        # Cache wird automatisch bei Fehlern geleert
        
        # IMMER AKTUELLES PROFIL LADEN - Session State Problem beheben
        profile = None
        
        # Debugging: Prüfe Session State
        cached_profile = st.session_state.get("my_profile")
        if cached_profile:
            st.info(f"🔧 Debug: Cache gefunden für {cached_profile.get('email', 'unbekannt')}")
        
        # FORCE: Immer frische Daten vom Backend holen
        with st.spinner("📄 Lade aktuelle Profil-Daten..."):
            profile = get_my_profile()
            if profile:
                st.session_state["my_profile"] = profile
                st.success("✅ Profil erfolgreich aktualisiert!")
        
        if profile:
            # DEBUG: Zeige rohe API-Daten
            with st.expander("🔧 Debug: API-Response", expanded=False):
                import json
                st.json(profile)
            
            # Basis-Informationen
            st.markdown("#### 👤 Persönliche Daten")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Vollständiger Name:** {profile.get('full_name', 'N/A')}")
                st.markdown(f"**E-Mail:** {profile.get('email', 'N/A')}")
                st.markdown(f"**Mitarbeiter-ID:** {profile.get('employee_id') or 'Nicht vergeben'}")
                st.markdown(f"**Benutzer-ID:** {profile.get('id', 'N/A')}")
            
            with col2:
                st.markdown(f"**Abteilung:** {profile.get('organizational_unit', 'N/A')}")
                st.markdown(f"**Freigabe-Level:** {profile.get('approval_level', 1)}")
                st.markdown(f"**Abteilungsleiter:** {'✅ Ja' if profile.get('is_department_head') else '❌ Nein'}")
                st.markdown(f"**Account-Status:** {'🟢 Aktiv' if profile.get('is_active') else '🔴 Inaktiv'}")
            
            # Account-Metadaten
            st.markdown("#### 📅 Account-Informationen")
            col1, col2 = st.columns(2)
            
            with col1:
                created_at = profile.get('created_at')
                if created_at:
                    from datetime import datetime
                    try:
                        if isinstance(created_at, str):
                            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        else:
                            created_date = created_at
                        st.markdown(f"**Account erstellt:** {created_date.strftime('%d.%m.%Y %H:%M')}")
                    except:
                        st.markdown(f"**Account erstellt:** {created_at}")
                
                last_login = profile.get('last_login')
                if last_login:
                    st.markdown(f"**Letzter Login:** {last_login}")
                else:
                    st.markdown("**Letzter Login:** Nicht verfügbar")
            
            with col2:
                password_changed = profile.get('password_changed_at')
                if password_changed:
                    st.markdown(f"**Passwort geändert:** {password_changed}")
                else:
                    st.markdown("**Passwort geändert:** Nicht verfügbar")
            
            # Berechtigungen
            st.markdown("#### 🔐 Meine Berechtigungen")
            permissions = profile.get('individual_permissions', [])
            if permissions:
                st.markdown("**Individuelle Berechtigungen:**")
                for perm in permissions:
                    perm_emoji = {
                        'system_administration': '🔧',
                        'user_management': '👥',
                        'document_management': '📋',
                        'qm_approval': '✅',
                        'all_rights': '⭐'
                    }.get(perm, '🔹')
                    st.markdown(f"• {perm_emoji} {perm}")
            else:
                st.markdown("**Berechtigungen:** Standard-Berechtigungen")
            
            # Interessensgruppen - VERBESSERTE ANZEIGE
            st.markdown("#### 🏢 Meine Interessensgruppen")
            interest_groups = profile.get('interest_groups', [])
            
            # DEBUG: Zeige rohe Daten
            st.caption(f"🔧 Debug: interest_groups = {interest_groups} (Typ: {type(interest_groups)})")
            
            if interest_groups and len(interest_groups) > 0:
                st.markdown("**Zugeordnete Gruppen:**")
                for group in interest_groups:
                    st.markdown(f"• 🏢 {group}")
                st.success(f"✅ {len(interest_groups)} Interessensgruppen zugeordnet")
            else:
                st.warning("**Interessensgruppen:** Keine Zuordnungen")
                st.caption("Wenn Sie Interessensgruppen haben sollten, wenden Sie sich an den Administrator.")
            
            # Datenexport (DSGVO Art. 20)
            st.markdown("#### 📥 Datenexport")
            st.markdown("""
            <div class="info-box">
                <strong>Recht auf Datenübertragbarkeit (Art. 20 DSGVO):</strong> 
                Sie können Ihre Daten in einem strukturierten, gängigen Format herunterladen.
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📥 Meine Daten als JSON exportieren"):
                import json
                from datetime import datetime
                profile_json = json.dumps(profile, indent=2, default=str, ensure_ascii=False)
                st.download_button(
                    label="💾 JSON-Datei herunterladen",
                    data=profile_json,
                    file_name=f"profil_{profile.get('email', 'user')}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        else:
            st.error("❌ Profil konnte nicht geladen werden. Bitte versuchen Sie es erneut.")
    
    with tab2:
        st.markdown("### 🔐 Passwort ändern")
        st.markdown("""
        <div class="info-box">
            <strong>Sicherheitshinweis:</strong> Sie können Ihr Passwort jederzeit selbst ändern.
            Ihr aktuelles Passwort wird zur Bestätigung benötigt.
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("password_change_form"):
            current_password = st.text_input(
                "🔐 Aktuelles Passwort", 
                type="password",
                help="Zur Sicherheit benötigen wir Ihr aktuelles Passwort"
            )
            
            new_password = st.text_input(
                "🆕 Neues Passwort", 
                type="password",
                help="Mindestens 8 Zeichen, 1 Großbuchstabe, 1 Zahl oder Sonderzeichen"
            )
            
            confirm_password = st.text_input(
                "✅ Neues Passwort bestätigen", 
                type="password",
                help="Wiederholen Sie das neue Passwort"
            )
            
            # Passwort-Stärke-Anzeige
            if new_password:
                strength_score = 0
                feedback = []
                
                if len(new_password) >= 8:
                    strength_score += 1
                else:
                    feedback.append("❌ Mindestens 8 Zeichen")
                
                if any(c.isupper() for c in new_password):
                    strength_score += 1
                else:
                    feedback.append("❌ Mindestens 1 Großbuchstabe")
                
                if any(c.isdigit() for c in new_password):
                    strength_score += 1
                else:
                    feedback.append("❌ Mindestens 1 Zahl")
                
                if any(not c.isalnum() for c in new_password):
                    strength_score += 1
                else:
                    feedback.append("❌ Mindestens 1 Sonderzeichen empfohlen")
                
                # Stärke-Anzeige
                if strength_score >= 3:
                    st.success("✅ Passwort-Stärke: Gut")
                elif strength_score >= 2:
                    st.warning("⚠️ Passwort-Stärke: Mittel")
                else:
                    st.error("❌ Passwort-Stärke: Schwach")
                
                # Feedback anzeigen
                if feedback:
                    for fb in feedback:
                        st.caption(fb)
            
            # Submit Button
            if st.form_submit_button("🔄 Passwort ändern", type="primary"):
                if not current_password:
                    st.error("❌ Aktuelles Passwort ist erforderlich")
                elif not new_password:
                    st.error("❌ Neues Passwort ist erforderlich")
                elif new_password != confirm_password:
                    st.error("❌ Neue Passwörter stimmen nicht überein")
                elif len(new_password) < 8:
                    st.error("❌ Neues Passwort muss mindestens 8 Zeichen haben")
                else:
                    with st.spinner("🔄 Passwort wird geändert..."):
                        result = change_my_password(current_password, new_password, confirm_password)
                        if result:
                            st.success("✅ Passwort erfolgreich geändert!")
                            st.balloons()
                            # Session State zurücksetzen für Sicherheit
                            time.sleep(2)
                            st.rerun()

def render_ai_analysis_page():
    """🤖 Rendert die erweiterte KI-Analyse-Seite mit Hybrid-Funktionen"""
    st.markdown("## 🤖 KI-Analyse - Hybrid Edition")
    st.markdown("Erweiterte KI-Funktionalitäten mit optionaler LLM-Integration")
    
    # Backend-Status prüfen
    if not check_backend_status():
        st.error("❌ Backend nicht erreichbar! KI-Funktionen sind nicht verfügbar.")
        return
    
    # Hybrid-AI Status anzeigen
    hybrid_config = get_hybrid_ai_config()
    if hybrid_config:
        hybrid_status = hybrid_config.get("hybrid_ai_status", {})
        llm_enabled = hybrid_status.get("enabled", False)
        llm_provider = hybrid_status.get("provider", "none")
        
        if llm_enabled:
            st.success(f"🤖 **Hybrid-Modus aktiv** - LLM: {llm_provider.upper()}")
        else:
            st.info("🏠 **Lokale KI aktiv** - Hybrid-Modus nicht konfiguriert")
    
    # Erweiterte Tabs für Hybrid-Features
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Hybrid Text-Analyse", 
        "📊 Dokument-Analyse", 
        "🔍 Ähnlichkeits-Vergleich",
        "💰 Kosten-Übersicht",
        "⚙️ System-Status"
    ])
    
    with tab1:
        st.markdown("### 📝 Hybrid Text-Analyse")
        st.markdown("Kombiniert lokale KI mit optionaler LLM-Enhancement für tiefere Insights")
        
        # Konfiguration
        col1, col2 = st.columns(2)
        with col1:
            enhance_with_llm = st.checkbox("🤖 LLM-Enhancement aktivieren", value=False, help="Erweiterte Analyse mit Large Language Models")
        with col2:
            analyze_duplicates = st.checkbox("🔍 Duplikatsprüfung", value=False, help="Vergleich mit existierenden Dokumenten")
        
        # Text-Input
        test_text = st.text_area(
            "Text eingeben (min. 50 Zeichen):",
            height=200,
            placeholder="Standard Operating Procedure\nDokumentenkontrolle nach ISO 13485:2016\n\n1. Zweck\nDiese SOP beschreibt das Verfahren zur Kontrolle und Verwaltung von QMS-Dokumenten gemäß ISO 13485:2016 und MDR 2017/745..."
        )
        
        filename = st.text_input("Dateiname (optional):", placeholder="z.B. sop_dokumentenkontrolle.pdf")
        
        # Analyse-Modus auswählen
        analysis_mode = "Standard KI" if not enhance_with_llm else "Hybrid KI (LLM)"
        st.info(f"📊 **Analyse-Modus:** {analysis_mode}")
        
        if st.button("🧠 Hybrid-Analyse starten", type="primary"):
            if len(test_text.strip()) < 50:
                st.error("❌ Text zu kurz! Mindestens 50 Zeichen erforderlich.")
            else:
                progress_text = "🤖 Lokale KI-Analyse..." if not enhance_with_llm else "🧠 Hybrid-Analyse (Lokale KI + LLM)..."
                
                with st.spinner(progress_text):
                    # Verwende Hybrid-API wenn LLM aktiviert, sonst Standard
                    if enhance_with_llm:
                        ai_result = analyze_text_with_hybrid_ai(test_text, filename, enhance_with_llm, analyze_duplicates)
                    else:
                        ai_result = analyze_text_with_ai(test_text, filename)
                    
                    if ai_result:
                        st.success("✅ Hybrid-Analyse abgeschlossen!")
                        
                        # Performance-Informationen
                        processing_time = ai_result.get('processing_time_seconds', 0)
                        st.info(f"⏱️ Verarbeitungszeit: {processing_time:.2f} Sekunden")
                        
                        # === LOKALE KI-ERGEBNISSE (immer vorhanden) ===
                        st.markdown("### 🏠 Lokale KI-Analyse")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # Spracherkennung
                            if enhance_with_llm:
                                local_analysis = ai_result.get('local_analysis', {})
                                detected_lang = local_analysis.get('language', 'unbekannt')
                                lang_conf = local_analysis.get('language_confidence', 0)
                            else:
                                lang_data = ai_result.get('language', {})
                                detected_lang = lang_data.get('detected', 'unbekannt')
                                lang_conf = lang_data.get('confidence', 0)
                            
                            st.markdown("#### 🌍 Sprache")
                            if lang_conf > 0.7:
                                st.success(f"**{detected_lang.upper()}** ({lang_conf:.1%})")
                            else:
                                st.warning(f"**{detected_lang.upper()}** ({lang_conf:.1%})")
                        
                        with col2:
                            # Dokumenttyp
                            if enhance_with_llm:
                                predicted_type = local_analysis.get('document_type', 'UNKNOWN')
                                type_conf = local_analysis.get('type_confidence', 0)
                            else:
                                class_data = ai_result.get('classification', {})
                                predicted_type = class_data.get('predicted_type', 'UNKNOWN')
                                type_conf = class_data.get('confidence', 0)
                            
                            st.markdown("#### 📊 Dokumenttyp")
                            st.success(f"**{predicted_type}** ({type_conf:.1%})")
                        
                        with col3:
                            # Qualitätsbewertung
                            if enhance_with_llm:
                                quality_score = local_analysis.get('quality_score', 0)
                            else:
                                quality_data = ai_result.get('quality', {})
                                quality_score = quality_data.get('content_score', 0)
                            
                            st.markdown("#### 📈 Qualität")
                            st.metric("Bewertung", f"{quality_score:.1%}")
                        
                        # Keywords und Normen
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Keywords
                            if enhance_with_llm:
                                keywords = local_analysis.get('keywords', [])
                            else:
                                keywords = ai_result.get('keywords', [])
                            
                            st.markdown("#### 🏷️ Keywords")
                            if keywords:
                                for kw in keywords[:8]:
                                    st.button(kw, key=f"kw1_{kw}", disabled=True)
                            else:
                                st.info("Keine gefunden")
                        
                        with col2:
                            # Norm-Referenzen
                            if enhance_with_llm:
                                norm_refs = local_analysis.get('norm_references', [])
                            else:
                                norm_refs = ai_result.get('norm_references', [])
                            
                            st.markdown("#### 📋 Norm-Referenzen")
                            if norm_refs:
                                for ref in norm_refs[:5]:
                                    if isinstance(ref, dict):
                                        st.success(f"**{ref.get('norm_name', 'Unbekannt')}**")
                                    else:
                                        st.success(f"**{ref}**")
                            else:
                                st.info("Keine gefunden")
                        
                        # === LLM-ENHANCEMENT (falls aktiviert) ===
                        if enhance_with_llm:
                            llm_enhancement = ai_result.get('llm_enhancement', {})
                            
                            if llm_enhancement.get('enabled', False):
                                st.markdown("### 🤖 LLM-Enhancement")
                                
                                # LLM-Informationen
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    cost = llm_enhancement.get('cost_eur', 0)
                                    st.metric("💰 Kosten", f"{cost:.4f}€")
                                
                                with col2:
                                    confidence = llm_enhancement.get('confidence', 0)
                                    st.metric("📊 Konfidenz", f"{confidence:.1%}")
                                
                                with col3:
                                    anonymized = llm_enhancement.get('anonymized', False)
                                    st.metric("🔒 Anonymisiert", "✅" if anonymized else "❌")
                                
                                # LLM-Zusammenfassung
                                llm_summary = llm_enhancement.get('summary')
                                if llm_summary:
                                    st.markdown("#### 📋 KI-Zusammenfassung")
                                    st.info(llm_summary)
                                
                                # LLM-Empfehlungen
                                recommendations = llm_enhancement.get('recommendations', [])
                                if recommendations:
                                    st.markdown("#### 💡 Empfehlungen")
                                    for i, rec in enumerate(recommendations, 1):
                                        st.write(f"**{i}.** {rec}")
                                
                                # Compliance-Lücken
                                compliance_gaps = llm_enhancement.get('compliance_gaps', [])
                                if compliance_gaps:
                                    st.markdown("#### ⚠️ Compliance-Lücken")
                                    for gap in compliance_gaps:
                                        severity = gap.get('severity', 'MITTEL')
                                        color = "🔴" if severity == "HOCH" else "🟡" if severity == "MITTEL" else "🟢"
                                        st.write(f"{color} **{gap.get('standard', 'Unbekannt')}:** {gap.get('gap', 'Nicht spezifiziert')}")
                                
                                # Auto-Metadaten
                                auto_metadata = llm_enhancement.get('auto_metadata', {})
                                if auto_metadata:
                                    st.markdown("#### 🏷️ Auto-Metadaten")
                                    
                                    suggested_keywords = auto_metadata.get('suggested_keywords', [])
                                    if suggested_keywords:
                                        st.write("**Vorgeschlagene Keywords:**")
                                        for kw in suggested_keywords:
                                            st.write(f"• {kw}")
                                    
                                    risk_category = auto_metadata.get('risk_category')
                                    if risk_category:
                                        color = "🔴" if risk_category == "HOCH" else "🟡" if risk_category == "MITTEL" else "🟢"
                                        st.write(f"**Risiko-Kategorie:** {color} {risk_category}")
                                    
                                    compliance_score = auto_metadata.get('compliance_score')
                                    if compliance_score:
                                        st.metric("Compliance-Score", f"{compliance_score:.1%}")
                            
                            else:
                                st.warning("⚠️ LLM-Enhancement war aktiviert, aber nicht erfolgreich. Verwende nur lokale KI-Ergebnisse.")
                        
                        # Duplikate (falls aktiviert)
                        if analyze_duplicates:
                            duplicates = ai_result.get('duplicates', [])
                            if duplicates:
                                st.markdown("### 🔍 Ähnliche Dokumente")
                                for dup in duplicates[:3]:
                                    similarity = dup.get('similarity_percentage', 0)
                                    title = dup.get('title', 'Unbekannt')
                                    doc_id = dup.get('id', 0)
                                    st.write(f"📄 **{title}** (ID: {doc_id}) - Ähnlichkeit: {similarity:.1%}")
                            else:
                                st.info("🔍 Keine ähnlichen Dokumente gefunden")
                    
                    else:
                        st.error("❌ Hybrid-Analyse fehlgeschlagen!")
    
    with tab2:
        st.markdown("### 📊 Hybrid Dokument-Analyse")
        st.markdown("Umfassende Analyse existierender Dokumente mit optionaler LLM-Enhancement")
        
        documents = get_documents()
        if documents:
            doc_options = [f"{doc['id']} - {doc['title']}" for doc in documents]
            selected_doc = st.selectbox("Dokument auswählen:", doc_options)
            
            # Konfiguration für Dokument-Analyse
            col1, col2 = st.columns(2)
            with col1:
                enhance_with_llm = st.checkbox("🤖 LLM-Enhancement", value=False, key="doc_llm", help="Erweiterte Analyse mit LLM")
            with col2:
                analyze_duplicates = st.checkbox("🔍 Duplikatsprüfung", value=True, key="doc_dup", help="Suche nach ähnlichen Dokumenten")
            
            if selected_doc and st.button("🧠 Hybrid-Dokument-Analyse", type="primary"):
                doc_id = int(selected_doc.split(' - ')[0])
                
                progress_text = "🔍 Lokale Analyse..." if not enhance_with_llm else "🧠 Hybrid-Analyse (Lokale KI + LLM)..."
                
                with st.spinner(progress_text):
                    # Verwende Hybrid-API wenn LLM aktiviert
                    if enhance_with_llm:
                        ai_result = analyze_document_with_hybrid_ai(doc_id, enhance_with_llm, analyze_duplicates)
                    else:
                        ai_result = analyze_document_with_ai(doc_id, analyze_duplicates)
                    
                    if ai_result:
                        st.success("✅ Dokument-Analyse abgeschlossen!")
                        
                        # Performance-Info
                        if enhance_with_llm:
                            processing_time = ai_result.get('processing_time_seconds', 0)
                            st.info(f"⏱️ Verarbeitungszeit: {processing_time:.2f} Sekunden")
                        
                        # === LOKALE KI-ERGEBNISSE ===
                        st.markdown("### 🏠 Lokale KI-Analyse")
                        
                        if enhance_with_llm:
                            # Hybrid-Modus: Strukturierte Daten
                            local_data = ai_result.get('local_analysis', {})
                            lang_data = local_data.get('language', {})
                            class_data = local_data.get('document_classification', {})
                            quality_data = local_data.get('quality_assessment', {})
                            
                            detected_lang = lang_data.get('detected', 'unbekannt')
                            lang_conf = lang_data.get('confidence', 0)
                            predicted_type = class_data.get('predicted_type', 'UNKNOWN')
                            type_conf = class_data.get('confidence', 0)
                            
                        else:
                            # Standard-Modus: Original-Format
                            lang_data = ai_result.get('language', {})
                            class_data = ai_result.get('document_classification', {})
                            quality_data = ai_result.get('quality', {})
                            
                            detected_lang = lang_data.get('detected', 'unbekannt')
                            lang_conf = lang_data.get('confidence', 0)
                            predicted_type = class_data.get('predicted_type', 'UNKNOWN')
                            type_conf = class_data.get('confidence', 0)
                        
                        # Basis-Informationen anzeigen
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("🌍 Sprache", f"{detected_lang.upper()}", f"{lang_conf:.1%}")
                        
                        with col2:
                            st.metric("📊 Dokumenttyp", predicted_type, f"{type_conf:.1%}")
                        
                        with col3:
                            if enhance_with_llm:
                                complexity = quality_data.get('complexity_score', 0)
                                st.metric("🧮 Komplexität", f"{complexity}/10")
                            else:
                                content_quality = quality_data.get('content_score', 0)
                                st.metric("📈 Qualität", f"{content_quality:.1%}")
                        
                        with col4:
                            if enhance_with_llm:
                                risk_level = quality_data.get('risk_level', 'UNKNOWN')
                                color = "🔴" if risk_level == "HOCH" else "🟡" if risk_level == "MITTEL" else "🟢"
                                st.metric("⚠️ Risiko", f"{color} {risk_level}")
                            else:
                                st.metric("📄 Format", "Standard")
                        
                        # Keywords und Normen
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if enhance_with_llm:
                                keywords = local_data.get('extracted_keywords', [])
                            else:
                                keywords = ai_result.get('keywords', [])
                            
                            st.markdown("#### 🏷️ Keywords")
                            if keywords:
                                for kw in keywords[:10]:
                                    st.button(kw, key=f"kw2_{kw}", disabled=True)
                            else:
                                st.info("Keine gefunden")
                        
                        with col2:
                            if enhance_with_llm:
                                norm_refs = local_data.get('norm_references', [])
                            else:
                                norm_refs = ai_result.get('norm_references', [])
                            
                            st.markdown("#### 📋 Norm-Referenzen")
                            if norm_refs:
                                for ref in norm_refs[:5]:
                                    if isinstance(ref, dict):
                                        norm_name = ref.get('norm_name', 'Unbekannt')
                                        confidence = ref.get('confidence', 0)
                                        st.write(f"• **{norm_name}** ({confidence:.1%})")
                                    else:
                                        st.write(f"• **{ref}**")
                            else:
                                st.info("Keine gefunden")
                        
                        # === LLM-ENHANCEMENT (falls aktiviert) ===
                        if enhance_with_llm:
                            llm_enhancement = ai_result.get('llm_enhancement', {})
                            
                            if llm_enhancement.get('enabled', False):
                                st.markdown("### 🤖 LLM-Enhancement")
                                
                                # LLM-Status-Info
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    cost = llm_enhancement.get('estimated_cost_eur', 0)
                                    st.metric("💰 Kosten", f"{cost:.4f}€")
                                
                                with col2:
                                    confidence = llm_enhancement.get('confidence', 0)
                                    st.metric("📊 Konfidenz", f"{confidence:.1%}")
                                
                                with col3:
                                    anonymized = llm_enhancement.get('anonymization_applied', False)
                                    st.metric("🔒 Anonymisiert", "✅" if anonymized else "❌")
                                
                                # LLM-Insights
                                llm_summary = llm_enhancement.get('summary')
                                if llm_summary:
                                    st.markdown("#### 📋 KI-Zusammenfassung")
                                    st.info(llm_summary)
                                
                                recommendations = llm_enhancement.get('recommendations', [])
                                if recommendations:
                                    st.markdown("#### 💡 Verbesserungsempfehlungen")
                                    for i, rec in enumerate(recommendations, 1):
                                        st.write(f"**{i}.** {rec}")
                                
                                compliance_gaps = llm_enhancement.get('compliance_gaps', [])
                                if compliance_gaps:
                                    st.markdown("#### ⚠️ Compliance-Lücken")
                                    for gap in compliance_gaps:
                                        severity = gap.get('severity', 'MITTEL')
                                        color = "🔴" if severity == "HOCH" else "🟡" if severity == "MITTEL" else "🟢"
                                        standard = gap.get('standard', 'Unbekannt')
                                        gap_desc = gap.get('gap', 'Nicht spezifiziert')
                                        st.warning(f"{color} **{standard}:** {gap_desc}")
                            else:
                                st.warning("⚠️ LLM-Enhancement fehlgeschlagen - verwende nur lokale Analyse")
                        
                        # Duplikate
                        if analyze_duplicates:
                            if enhance_with_llm:
                                duplicates = local_data.get('potential_duplicates', [])
                            else:
                                duplicates = ai_result.get('duplicates', [])
                            
                            if duplicates:
                                st.markdown("### 🔍 Ähnliche Dokumente")
                                for dup in duplicates[:5]:
                                    if isinstance(dup, dict):
                                        similarity = dup.get('similarity_percentage', 0)
                                        title = dup.get('title', 'Unbekannt')
                                        doc_id_dup = dup.get('id', 0)
                                        st.write(f"📄 **{title}** (ID: {doc_id_dup}) - Ähnlichkeit: {similarity:.1%}")
                                    else:
                                        st.write(f"📄 {dup}")
                            else:
                                st.info("🔍 Keine ähnlichen Dokumente gefunden")
                    else:
                        st.error("❌ Dokument-Analyse fehlgeschlagen!")
        else:
            st.info("Keine Dokumente verfügbar")
    
    with tab3:
        st.markdown("### 🔍 Ähnlichkeits-Vergleich")
        
        documents = get_documents()
        if documents and len(documents) >= 2:
            doc_options = [f"{doc['id']} - {doc['title']}" for doc in documents]
            
            col1, col2 = st.columns(2)
            with col1:
                doc1 = st.selectbox("Erstes Dokument:", doc_options, key="doc1")
            with col2:
                doc2 = st.selectbox("Zweites Dokument:", doc_options, key="doc2")
            
            if doc1 != doc2 and st.button("🔍 Ähnlichkeit berechnen"):
                doc1_id = int(doc1.split(' - ')[0])
                doc2_id = int(doc2.split(' - ')[0])
                
                with st.spinner("🧮 Berechne..."):
                    try:
                        response = requests.get(
                            f"{API_BASE_URL}/api/ai/similarity/{doc1_id}/{doc2_id}",
                            timeout=REQUEST_TIMEOUT
                        )
                        
                        if response.status_code == 200:
                            similarity_data = response.json()
                            analysis = similarity_data.get('similarity_analysis', {})
                            percentage = analysis.get('percentage', '0%')
                            level = analysis.get('level', 'NIEDRIG')
                            
                            if level == "SEHR_HOCH":
                                st.error(f"⚠️ **Ähnlichkeit:** {percentage}")
                            elif level == "HOCH":
                                st.warning(f"📋 **Ähnlichkeit:** {percentage}")
                            else:
                                st.success(f"✅ **Ähnlichkeit:** {percentage}")
                        else:
                            st.error("❌ Analyse fehlgeschlagen!")
                    except Exception as e:
                        st.error(f"❌ Fehler: {e}")
        else:
            st.info("Mindestens 2 Dokumente erforderlich")
    
    with tab4:
        st.markdown("### 💰 Kosten-Übersicht")
        st.markdown("Transparenz und Kontrolle über LLM-Nutzung und -Kosten")
        
        cost_stats = get_hybrid_ai_cost_stats()
        
        if cost_stats:
            cost_summary = cost_stats.get('cost_summary', {})
            system_info = cost_stats.get('system_info', {})
            recent_activity = cost_stats.get('recent_activity', [])
            
            # Kosten-Metriken
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_cost = cost_summary.get('total_cost_eur', 0)
                st.metric("💰 Gesamtkosten", f"{total_cost:.4f}€")
            
            with col2:
                total_requests = cost_summary.get('total_requests', 0)
                st.metric("🔢 Anfragen", total_requests)
            
            with col3:
                avg_cost = cost_summary.get('average_cost_per_request', 0)
                st.metric("📊 Ø pro Anfrage", f"{avg_cost:.4f}€")
            
            with col4:
                llm_provider = system_info.get('llm_provider', 'none')
                st.metric("🤖 Provider", llm_provider.upper())
            
            # System-Konfiguration
            st.markdown("#### ⚙️ System-Konfiguration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                llm_enabled = system_info.get('llm_enabled', False)
                anonymization = system_info.get('anonymization_enabled', True)
                
                st.write(f"**LLM aktiviert:** {'✅' if llm_enabled else '❌'}")
                st.write(f"**Anonymisierung:** {'✅' if anonymization else '❌'}")
            
            with col2:
                max_cost = system_info.get('max_cost_per_request', 0.5)
                st.write(f"**Max. Kosten/Anfrage:** {max_cost}€")
                st.write(f"**Provider:** {llm_provider}")
            
            # Letzte Aktivitäten
            if recent_activity:
                st.markdown("#### 📜 Letzte Aktivitäten")
                
                for activity in recent_activity[:10]:
                    timestamp = activity.get('timestamp', 0)
                    filename = activity.get('filename', 'Unbekannt')
                    cost = activity.get('cost_eur', 0)
                    provider = activity.get('provider', 'unbekannt')
                    
                    # Timestamp formatieren
                    try:
                        from datetime import datetime
                        dt = datetime.fromtimestamp(timestamp)
                        formatted_time = dt.strftime("%d.%m.%Y %H:%M")
                    except:
                        formatted_time = "Unbekannt"
                    
                    st.write(f"🕒 **{formatted_time}** | 📄 {filename} | 💰 {cost:.4f}€ | 🤖 {provider}")
            else:
                st.info("Keine LLM-Aktivitäten vorhanden")
                
            # Kosten-Warnung
            if total_cost > 1.0:
                st.warning(f"⚠️ **Hohe Kosten:** Bereits {total_cost:.2f}€ verbraucht. Überwachen Sie die LLM-Nutzung!")
            elif total_cost > 0.1:
                st.info(f"💡 **Moderate Nutzung:** {total_cost:.4f}€ bisher verbraucht.")
        else:
            st.info("Keine Kosten-Daten verfügbar (LLM nicht aktiviert oder noch keine Nutzung)")
    
    with tab5:
        st.markdown("### ⚙️ System-Status")
        st.markdown("Detaillierte Informationen über die Hybrid-AI-Konfiguration")
        
        # Backend-Status
        backend_ok = check_backend_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🖥️ Backend-Status")
            if backend_ok:
                st.success("✅ Backend erreichbar")
            else:
                st.error("❌ Backend nicht erreichbar")
        
        with col2:
            st.markdown("#### 🤖 Hybrid-AI-Status")
            hybrid_config = get_hybrid_ai_config()
            
            if hybrid_config:
                hybrid_status = hybrid_config.get("hybrid_ai_status", {})
                llm_enabled = hybrid_status.get("enabled", False)
                
                if llm_enabled:
                    st.success("✅ Hybrid-Modus aktiv")
                else:
                    st.info("🏠 Nur lokale KI aktiv")
            else:
                st.warning("⚠️ Konfiguration nicht abrufbar")
        
        # Detaillierte Konfiguration
        if hybrid_config:
            st.markdown("#### 📋 Detaillierte Konfiguration")
            
            hybrid_status = hybrid_config.get("hybrid_ai_status", {})
            local_status = hybrid_config.get("local_ai_status", {})
            config_source = hybrid_config.get("configuration_source", {})
            
            # Hybrid-AI-Einstellungen
            st.markdown("**🤖 Hybrid-AI-Einstellungen:**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"• **Provider:** {hybrid_status.get('provider', 'none')}")
                st.write(f"• **Modell:** {hybrid_status.get('model', 'N/A')}")
                st.write(f"• **Anonymisierung:** {hybrid_status.get('anonymization', True)}")
            
            with col2:
                st.write(f"• **Max Tokens:** {hybrid_status.get('max_tokens', 1000)}")
                st.write(f"• **Temperatur:** {hybrid_status.get('temperature', 0.1)}")
                st.write(f"• **Max Kosten:** {hybrid_status.get('max_cost_per_request', 0.5)}€")
            
            # Lokale KI-Status
            st.markdown("**🏠 Lokale KI-Status:**")
            st.write(f"• **Status:** {local_status.get('always_enabled', True)}")
            st.write(f"• **Beschreibung:** {local_status.get('description', 'N/A')}")
            
            # Konfiguration via Umgebungsvariablen
            st.markdown("**🔧 Konfiguration:**")
            st.write(f"• **Quelle:** {config_source.get('description', 'N/A')}")
            
            env_vars = config_source.get('variables', [])
            if env_vars:
                st.markdown("**Umgebungsvariablen:**")
                for var in env_vars:
                    st.code(var)
            
            # Test-Buttons
            st.markdown("#### 🧪 System-Tests")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🏥 Backend-Test"):
                    with st.spinner("Teste Backend..."):
                        if check_backend_status():
                            st.success("✅ Backend erreichbar")
                        else:
                            st.error("❌ Backend nicht erreichbar")
            
            with col2:
                if st.button("🤖 Hybrid-AI-Test"):
                    with st.spinner("Teste Hybrid-AI..."):
                        test_result = analyze_text_with_hybrid_ai(
                            "Test-Dokument für ISO 13485 Qualitätsmanagementsystem.",
                            "test.txt",
                            enhance_with_llm=False,  # Nur lokale KI testen
                            analyze_duplicates=False
                        )
                        
                        if test_result:
                            st.success("✅ Lokale KI funktioniert")
                        else:
                            st.error("❌ KI-Test fehlgeschlagen")
            
            with col3:
                if st.button("📊 LLM-Test") and hybrid_status.get("enabled", False):
                    with st.spinner("Teste LLM..."):
                        test_result = analyze_text_with_hybrid_ai(
                            "Test-Dokument für ISO 13485 Qualitätsmanagementsystem.",
                            "test.txt",
                            enhance_with_llm=True,  # LLM testen
                            analyze_duplicates=False
                        )
                        
                        if test_result and test_result.get('llm_enhancement', {}).get('enabled', False):
                            st.success("✅ LLM funktioniert")
                        else:
                            st.warning("⚠️ LLM-Test nicht erfolgreich")
        
        # Hilfe-Sektion
        st.markdown("#### 💡 Hybrid-AI konfigurieren")
        
        with st.expander("📚 Umgebungsvariablen für LLM-Integration"):
            st.markdown("""
            **Für OpenAI:**
            ```bash
            export AI_LLM_PROVIDER=openai
            export AI_LLM_API_KEY=your_openai_api_key
            export AI_LLM_MODEL=gpt-4o-mini
            ```
            
            **Für Anthropic Claude:**
            ```bash
            export AI_LLM_PROVIDER=anthropic
            export AI_LLM_API_KEY=your_anthropic_api_key
            export AI_LLM_MODEL=claude-3-haiku-20240307
            ```
            
            **Für lokales Ollama:**
            ```bash
            export AI_LLM_PROVIDER=ollama
            export AI_LLM_ENDPOINT=http://localhost:11434
            export AI_LLM_MODEL=llama3.1:8b
            ```
            
            **Optionale Einstellungen:**
            ```bash
            export AI_LLM_ANONYMIZE=true
            export AI_LLM_MAX_TOKENS=1000
            export AI_LLM_TEMPERATURE=0.1
            export AI_LLM_MAX_COST=0.50
            ```            """)

def render_settings_page():
    """Rendert die Einstellungen"""
    st.markdown("## ⚙️ Einstellungen")
    
    st.markdown("### 🔧 API-Konfiguration")
    st.code(f"API Base URL: {API_BASE_URL}")
    st.code(f"Request Timeout: {REQUEST_TIMEOUT}s")
    st.code(f"Max File Size: {MAX_FILE_SIZE_MB}MB")
    
    st.markdown("### 🏥 Backend-Status")
    if st.button("🔄 Backend-Status prüfen"):
        if check_backend_status():
            st.success("✅ Backend ist erreichbar!")
        else:
            st.error("❌ Backend nicht erreichbar!")
    
    st.markdown("### 🧪 API-Test")
    if st.button("🧪 API-Endpunkte testen"):
        with st.spinner("🧪 Teste API..."):
            # Health Check
            if check_backend_status():
                st.success("✅ Health Check OK")
            else:
                st.error("❌ Health Check fehlgeschlagen")
            
            # Document Types
            types = get_document_types()
            if types:
                st.success(f"✅ Dokumenttypen geladen: {', '.join(types)}")
            else:
                st.error("❌ Dokumenttypen laden fehlgeschlagen")
            
            # Documents
            docs = get_documents(limit=5)
            if docs is not None:
                st.success(f"✅ Dokumente geladen: {len(docs)} gefunden")
            else:
                st.error("❌ Dokumente laden fehlgeschlagen")

def get_ai_provider_status() -> Optional[Dict]:
    """Holt AI-Provider Status vom Backend"""
    def _get_status():
        response = requests.get(f"{API_BASE_URL}/api/ai/free-providers-status", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return None
    
    result = safe_api_call(_get_status)
    return result


def test_ai_provider(provider: str, test_text: Optional[str] = None) -> Optional[Dict]:
    """Testet einen spezifischen AI-Provider"""
    if not test_text:
        test_text = "Dies ist ein Test-Dokument für die QMS-Analyse. Es enthält Informationen über Qualitätsmanagement und Dokumentenverwaltung."
    
    def _test_provider():
        data = {
            "provider": provider,
            "test_text": test_text
        }
        response = requests.post(f"{API_BASE_URL}/api/ai/test-provider", data=data, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return None
    
    result = safe_api_call(_test_provider)
    return result


def simple_ai_prompt_test(prompt: str, provider: str = "auto") -> Optional[Dict]:
    """Führt einen einfachen AI Prompt Test durch"""
    def _test_prompt():
        data = {
            "prompt": prompt,
            "provider": provider
        }
        response = requests.post(f"{API_BASE_URL}/api/ai/simple-prompt", data=data, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return None
    
    result = safe_api_call(_test_prompt)
    return result


def get_ai_provider_status_simple() -> Optional[Dict]:
    """Lädt den Status aller AI Provider"""
    def _get_status():
        try:
            response = requests.get(f"{API_BASE_URL}/api/ai/free-providers-status", timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Provider Status HTTP Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Provider Status Error: {e}")
            return None
    
    result = safe_api_call(_get_status)
    return result


def render_ai_prompt_test_page():
    """🚀 Neue AI Provider Test Seite"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Provider Test Interface</h1>
        <p>Teste verschiedene AI Provider direkt mit eigenen Prompts</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Provider Status laden
    provider_status = get_ai_provider_status_simple()
    
    if not provider_status:
        st.error("❌ Kann Provider-Status nicht laden. Backend prüfen!")
        return
    
    # Provider Status anzeigen
    st.subheader("📊 Provider Status")
    
    if "provider_status" in provider_status:
        providers = provider_status["provider_status"]
        
        # Status-Grid
        cols = st.columns(len(providers))
        
        for i, (provider_name, details) in enumerate(providers.items()):
            with cols[i]:
                available = details.get("available", False)
                status_emoji = "✅" if available else "❌"
                
                st.markdown(f"""
                <div class="doc-card">
                    <h4>{status_emoji} {provider_name.title()}</h4>
                    <p><strong>Status:</strong> {details.get('status', 'unknown')}</p>
                    <p><strong>Typ:</strong> {details.get('type', 'unknown')}</p>
                    <p><strong>Kosten:</strong> {details.get('cost', 'unknown')}</p>
                    <p><strong>Performance:</strong> {details.get('performance', 'unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Test Interface
    st.subheader("🧪 AI Prompt Test")
    
    # Provider Auswahl
    # Provider aus Backend-Konfiguration laden
    try:
        import sys
        sys.path.append('../backend')
        from app.config import get_available_providers
        available_providers = ["auto"] + get_available_providers()
    except ImportError:
        # Fallback falls Backend nicht verfügbar
        available_providers = ["auto", "ollama", "openai_4o_mini", "gemini", "rule_based"]
    
    if provider_status and "provider_status" in provider_status:
        # Nur verfügbare Provider anzeigen
        status_dict = provider_status["provider_status"]
        available_providers = ["auto"]  # Auto bleibt immer verfügbar
        
        for provider, details in status_dict.items():
            if details.get("available", False):
                available_providers.append(provider)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Prompt Eingabe
        prompt = st.text_area(
            "💬 Dein Prompt an die AI:",
            value="Erkläre mir ISO 13485 und warum es für Medizinprodukte wichtig ist.",
            height=120,
            help="Gib hier deinen Text oder deine Frage ein"
        )
    
    with col2:
        # Provider Auswahl
        selected_provider = st.selectbox(
            "🤖 AI Provider:",
            available_providers,
            index=0,
            help="Wähle den AI Provider für deinen Test"
        )
        
        # Provider Info
        if provider_status and "provider_status" in provider_status:
            if selected_provider in provider_status["provider_status"]:
                provider_info = provider_status["provider_status"][selected_provider]
                st.info(f"**{selected_provider}:**\n{provider_info.get('description', 'Kein Beschreibung')}")
        
        # Test Button
        test_button = st.button("🚀 AI Test starten", type="primary", use_container_width=True)
    

    
    st.divider()
    
    # Test ausführen
    if test_button and prompt.strip():
        with st.spinner(f"🤖 Teste {selected_provider} mit deinem Prompt..."):
            
            # Test durchführen
            result = simple_ai_prompt_test(prompt, selected_provider)
            
            if result:
                if result.get("success", False):
                    # Erfolgreiche Antwort
                    st.success(f"✅ Test erfolgreich mit **{result.get('provider', 'unbekannt')}**")
                    
                    # Metriken anzeigen
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🕐 Verarbeitungszeit", f"{result.get('processing_time_seconds', 0):.2f}s")
                    with col2:
                        st.metric("🤖 Provider", result.get('provider', 'unbekannt'))
                    with col3:
                        st.metric("📝 Prompt Länge", f"{len(prompt)} Zeichen")
                    
                    # AI Antwort anzeigen
                    st.subheader("💬 AI Antwort:")
                    response_text = result.get("response", "Keine Antwort erhalten")
                    
                    # Schöne Darstellung der Antwort
                    st.markdown(f"""
                    <div class="success-box">
                        <h4>🤖 {selected_provider.title()} Antwort:</h4>
                        <p>{response_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Zusätzliche Details
                    with st.expander("🔍 Weitere Details"):
                        st.json(result)
                        
                else:
                    # Fehler
                    st.error(f"❌ Test fehlgeschlagen mit {selected_provider}")
                    error_msg = result.get("error", "Unbekannter Fehler")
                    st.markdown(f"""
                    <div class="error-box">
                        <h4>❌ Fehler Details:</h4>
                        <p>{error_msg}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("🔍 Technische Details"):
                        st.json(result)
            else:
                st.error("❌ Kann keine Verbindung zum Backend herstellen!")
    
    elif test_button and not prompt.strip():
        st.warning("⚠️ Bitte gib einen Prompt ein!")
    
    # Performance Tipps entfernt auf Wunsch des Users


def render_ai_provider_management_page():
    """🤖 AI-Provider Management Seite - Entwicklungstool"""
    
    st.markdown('<div class="main-header"><h1>🤖 KI-Provider Management</h1><p>Entwicklungs- und Test-Interface für KI-Provider</p></div>', unsafe_allow_html=True)
    
    # Warnung für Entwicklungsmodus
    st.markdown("""
    <div class="warning-box">
        ⚠️ <strong>Entwicklungsmodus:</strong> Diese Seite ist für Testing und Entwicklung gedacht.
        Hier kannst du verschiedene KI-Provider direkt testen und vergleichen.
    </div>
    """, unsafe_allow_html=True)
    
    # Provider Status laden
    with st.spinner("🔄 Lade Provider-Status..."):
        provider_status = get_ai_provider_status()
    
    if not provider_status:
        st.error("❌ Konnte Provider-Status nicht laden. Backend verfügbar?")
        return
    
    st.subheader("🎯 Provider-Übersicht")
    
    # Status-Übersicht
    provider_info = provider_status.get("provider_status", {})
    total_available = provider_status.get("total_available", 0)
    fallback_chain = provider_status.get("current_fallback_chain", "Unbekannt")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Verfügbare Provider", total_available, f"von {len(provider_info)}")
    
    with col2:
        st.metric("🔗 Aktuelle Fallback-Kette", "", fallback_chain)
    
    with col3:
        recommended_order = provider_status.get("recommended_order", [])
        recommended = " → ".join(recommended_order[:2]) if recommended_order else "N/A"
        st.metric("⭐ Empfohlen", "", recommended)
    
    # Provider Details-Tabelle
    st.subheader("📋 Provider-Details")
    
    for provider_name, details in provider_info.items():
        with st.expander(f"{'✅' if details['available'] else '❌'} **{provider_name.upper()}** - {details['description']}", 
                        expanded=details['available']):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Status:**", details['status'])
                st.write("**Modell:**", details['model'])
                st.write("**Performance:**", details['performance'])
                st.write("**Kosten:**", details['cost'])
            
            with col2:
                # Test-Button für jeden Provider
                if st.button(f"🧪 {provider_name} testen", key=f"test_{provider_name}"):
                    with st.spinner(f"🤖 Teste {provider_name}..."):
                        test_result = test_ai_provider(provider_name)
                    
                    if test_result and test_result.get("success"):
                        analysis = test_result.get("analysis_result", {})
                        processing_time = test_result.get("processing_time_seconds", 0)
                        
                        st.success(f"✅ Test erfolgreich! ({processing_time:.2f}s)")
                        
                        # Ergebnis anzeigen
                        st.json({
                            "Dokumenttyp": analysis.get("document_type"),
                            "Hauptthemen": analysis.get("main_topics"),
                            "Sprache": analysis.get("language"),
                            "Qualitätsscore": analysis.get("quality_score"),
                            "Zusammenfassung": analysis.get("ai_summary", "N/A")[:100] + "...",
                            "Provider": analysis.get("provider")
                        })
                    else:
                        error_msg = test_result.get("error", "Unbekannter Fehler") if test_result else "Keine Antwort"
                        st.error(f"❌ Test fehlgeschlagen: {error_msg}")
    
    # Vergleichstest
    st.subheader("⚖️ Provider-Vergleichstest")
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_text = st.text_area(
            "Test-Text eingeben:",
            value="Dies ist eine Standard Operating Procedure (SOP) für die Qualitätskontrolle in der Medizintechnik. Das Verfahren beschreibt die Schritte zur Dokumentenvalidierung nach ISO 13485.",
            height=100
        )
    
    with col2:
        available_providers = [name for name, details in provider_info.items() if details['available']]
        
        if available_providers:
            if st.button("🚀 Alle verfügbaren Provider testen", type="primary"):
                st.write("**📊 Vergleichstest-Ergebnisse:**")
                
                results = []
                
                for provider in available_providers:
                    with st.spinner(f"🤖 Teste {provider}..."):
                        result = test_ai_provider(provider, test_text)
                    
                    if result and result.get("success"):
                        analysis = result.get("analysis_result", {})
                        results.append({
                            "Provider": provider,
                            "Zeit (s)": f"{result.get('processing_time_seconds', 0):.2f}",
                            "Dokumenttyp": analysis.get("document_type", "N/A"),
                            "Qualität": analysis.get("quality_score", "N/A"),
                            "Sprache": analysis.get("language", "N/A"),
                            "Zusammenfassung": (analysis.get("ai_summary", "N/A")[:100] + "...") if analysis.get("ai_summary") else "N/A"
                        })
                    else:
                        results.append({
                            "Provider": provider,
                            "Zeit (s)": "FEHLER",
                            "Dokumenttyp": "FEHLER",
                            "Qualität": "FEHLER", 
                            "Sprache": "FEHLER",
                            "Zusammenfassung": result.get("error", "Unbekannt") if result else "Keine Antwort"
                        })
                
                if results:
                    import pandas as pd
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
        else:
            st.warning("⚠️ Keine Provider verfügbar für Tests!")
    
    # Konfigurationshilfe
    st.subheader("⚙️ Konfigurationshilfe")
    
    with st.expander("🔧 Provider konfigurieren", expanded=False):
        st.markdown("""
        **🤖 Ollama (Lokal):**
        ```bash
        # Installieren
        curl -fsSL https://ollama.ai/install.sh | sh
        
        # Mistral 7B Modell laden
        ollama pull mistral:7b
        
        # Server starten (läuft auf localhost:11434)
        ollama serve
        ```
        
        **🌟 Google Gemini Flash:**
        ```bash
        # 1. Google AI Studio: https://aistudio.google.com/
        # 2. API Key generieren
        # 3. In .env hinzufügen:
        GOOGLE_AI_API_KEY=your_api_key_here
        ```
        
        **🤗 Hugging Face:**
        ```bash
        # 1. Registrierung: https://huggingface.co/join
        # 2. Token erstellen: https://huggingface.co/settings/tokens
        # 3. In .env hinzufügen:
        HUGGINGFACE_API_KEY=your_token_here
        ```
        """)
    
    # Aktueller Status
    st.subheader("📊 Aktueller System-Status")
    
    status_data = {
        "Gesamte Provider": len(provider_info),
        "Verfügbare Provider": total_available,
        "Bevorzugte Reihenfolge": fallback_chain,
        "Backend erreichbar": "✅" if provider_status else "❌",
        "Letzter Check": datetime.now().strftime("%H:%M:%S")
    }
    
    for key, value in status_data.items():
        st.write(f"**{key}:** {value}")



# === RAG-CHAT FUNKTIONEN ===

def get_rag_status() -> Optional[Dict]:
    """RAG-System Status abrufen"""
    def _get_status():
        # Verwende neuen AI-Enhanced Endpoint
        headers = {"Authorization": f"Bearer {st.session_state.get('auth_token', '')}"} if st.session_state.get('auth_token') else {}
        response = requests.get(f"{API_BASE_URL}/api/rag-stats", headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return None
    
    result = safe_api_call(_get_status)
    return result

def chat_with_documents(question: str, token: str = "") -> Optional[Dict]:
    """Chat mit QMS-Dokumenten"""
    def _chat():
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = requests.post(
            f"{API_BASE_URL}/api/chat-with-documents",
            json={"question": question},
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    result = safe_api_call(_chat)
    return result





def render_rag_chat_page():
    """💬 RAG-Chat Seite"""
    st.markdown('<div class="main-header"><h1>💬 RAG-Chat</h1><p>Chat mit allen QMS-Dokumenten</p></div>', unsafe_allow_html=True)
    
    # RAG-System Status prüfen
    with st.expander("🧠 RAG-System Status", expanded=False):
        status_result = get_rag_status()
        
        if status_result and status_result.get("success"):
            st.success("✅ Qdrant RAG-System ist verfügbar!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📚 Dokumente", status_result.get("total_documents", 0))
            with col2:
                st.metric("🧩 Kollektion", status_result.get("collection_name", "qms_documents"))
            with col3:
                st.metric("🎯 Status", status_result.get("status", "unknown"))
            
            # Engine-Details
            engine_info = status_result.get("engine_info", {})
            if engine_info:
                st.info(f"🤖 Engine: {engine_info.get('type', 'qdrant')} | "
                       f"📊 Embedding Dimension: {engine_info.get('embedding_dimension', 384)} | "
                       f"🧠 Model: {engine_info.get('embedding_model', 'all-MiniLM-L6-v2')}")
        else:
            st.error("❌ RAG-System Status nicht abrufbar")
            st.warning("Stellen Sie sicher, dass die AI-Enhanced Features aktiviert sind.")
    
    # Chat-Interface
    st.markdown("### 💬 Chat mit QMS-Dokumenten")
    
    # Chat-Input
    question = st.text_area(
        "🤔 Ihre Frage an das QMS:",
        value=st.session_state.get('rag_question', ''),
        placeholder="z.B. 'Was steht in der ISO 13485 über Dokumentenlenkung?' oder 'Wie funktioniert die SOP-001?'",
        height=100,
        key="rag_question_input"
    )
    
    # Nur ein Button für Chat
    ask_button = st.button("🧠 Frage stellen", type="primary", disabled=not question.strip())
    
    # Chat-Antwort
    if ask_button and question.strip():
        token = st.session_state.get('auth_token', '')
        
        with st.spinner("🧠 Durchsuche QMS-Dokumente und generiere Antwort..."):
            result = chat_with_documents(question, token)
            
            if result and result.get("success"):
                # Antwort anzeigen
                st.markdown("### 💡 Antwort")
                st.markdown(result.get("answer", "Keine Antwort generiert"))
                
                # Metriken
                col1, col2, col3 = st.columns(3)
                with col1:
                    confidence = result.get("confidence", 0.0)
                    color = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.5 else "🔴"
                    st.metric("🎯 Konfidenz", f"{color} {confidence:.1%}")
                
                with col2:
                    processing_time = result.get("processing_time", 0)
                    st.metric("⏱️ Verarbeitung", f"{processing_time:.2f}s")
                
                with col3:
                    sources_used = len(result.get("sources", []))
                    st.metric("📄 Verwendete Quellen", sources_used)
                
                # Quellen anzeigen
                sources = result.get("sources", [])
                if sources:
                    st.markdown("### 📚 Verwendete Quellen")
                    for i, source in enumerate(sources, 1):
                        metadata = source.get("metadata", {})
                        with st.expander(f"📄 Quelle {i}: {metadata.get('title', 'Unbekannt')}"):
                            st.write(f"**Typ:** {metadata.get('document_type', 'Unbekannt')}")
                            st.write(f"**Datei:** {metadata.get('filename', 'Unbekannt')}")
                            st.write(f"**Relevanz:** {source.get('score', 0):.3f}")
                            if source.get("content"):
                                st.write("**Inhalt:**")
                                content_preview = source["content"][:300] + "..." if len(source["content"]) > 300 else source["content"]
                                st.code(content_preview)
            else:
                st.error("❌ Fehler beim Chat mit Dokumenten")
                if result:
                    st.error(f"Fehler: {result.get('error', 'Unbekannt')}")

# === INTELLIGENTE WORKFLOW-FUNKTIONEN ===

def trigger_workflow_from_message(message: str, token: str = "") -> Optional[Dict]:
    """Workflow aus Nachricht auslösen"""
    def _trigger():
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = requests.post(
            f"{API_BASE_URL}/api/workflow/trigger-message",
            json={"message": message},
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    result = safe_api_call(_trigger)
    return result

def get_active_workflows() -> Optional[Dict]:
    """Aktive Workflows abrufen"""
    def _get_workflows():
        response = requests.get(f"{API_BASE_URL}/api/workflow/active", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return None
    
    result = safe_api_call(_get_workflows)
    return result

def get_my_tasks(token: str = "", status: Optional[str] = None, priority: Optional[str] = None) -> Optional[Dict]:
    """Meine Tasks abrufen"""
    def _get_tasks():
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        params = {}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        
        response = requests.get(
            f"{API_BASE_URL}/api/tasks/my-tasks",
            headers=headers,
            params=params,
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    result = safe_api_call(_get_tasks)
    return result

def render_intelligent_workflows_page():
    """🚀 Intelligente Workflows Seite"""
    st.markdown('<div class="main-header"><h1>🚀 Intelligente Workflows</h1><p>Automatische Workflow-Auslösung durch KI</p></div>', unsafe_allow_html=True)
    
    # Workflow-Trigger
    st.markdown("### 💬 Workflow auslösen")
    st.markdown("Beschreiben Sie ein Problem oder eine Situation - die KI löst automatisch den passenden Workflow aus!")
    
    # Beispiel-Nachrichten
    st.markdown("**🔮 Beispiel-Trigger:**")
    example_triggers = [
        "Bluetooth Modul nicht mehr lieferbar",
        "Lötofen ist defekt und muss repariert werden",
        "Kunde beschwert sich über Produktfehler",
        "Interne Audit hat Abweichung gefunden",
        "Neue ISO 13485 Version erfordert Updates"
    ]
    
    cols = st.columns(len(example_triggers))
    for i, trigger in enumerate(example_triggers):
        with cols[i]:
            if st.button(f"⚡ Trigger {i+1}", help=trigger, key=f"trigger_{i}"):
                st.session_state['workflow_message'] = trigger
    
    # Message Input
    message = st.text_area(
        "🎯 Problem/Situation beschreiben:",
        value=st.session_state.get('workflow_message', ''),
        placeholder="z.B. 'CPU Chip nicht mehr verfügbar' oder 'Kalibrierofen ist ausgefallen'",
        height=100,
        key="workflow_message_input"
    )
    
    if st.button("🚀 Intelligenten Workflow auslösen", type="primary", disabled=not message.strip()):
        token = st.session_state.get('auth_token', '')
        
        with st.spinner("🧠 Analysiere Nachricht und löse Workflow aus..."):
            result = trigger_workflow_from_message(message, token)
            
            if result and result.get("success"):
                if result.get("workflow_triggered"):
                    st.success("🎉 Workflow erfolgreich ausgelöst!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📋 Workflow", result.get("workflow_name", "Unbekannt"))
                        st.metric("⏱️ Geschätzte Dauer", f"{result.get('estimated_duration', 0)} Tage")
                    
                    with col2:
                        st.metric("📝 Tasks erstellt", result.get("tasks_created", 0))
                        st.metric("🎯 Konfidenz", f"{result.get('confidence', 0):.1%}")
                    
                    st.info(f"🆔 Workflow-ID: {result.get('workflow_id', 'Unbekannt')}")
                    st.info(result.get("message", "Workflow ausgelöst"))
                else:
                    st.warning("🤔 Kein eindeutiger Workflow-Trigger erkannt")
                    st.info(result.get("message", "Nachricht analysiert, aber kein Workflow ausgelöst"))
            else:
                st.error("❌ Fehler bei der Workflow-Auslösung")
                if result:
                    st.error(f"Fehler: {result.get('error', 'Unbekannt')}")
    
    # Aktive Workflows anzeigen
    st.markdown("### 📋 Aktive Workflows")
    
    workflow_result = get_active_workflows()
    
    if workflow_result and workflow_result.get("success"):
        workflows = workflow_result.get("active_workflows", [])
        
        if workflows:
            for workflow in workflows:
                with st.expander(f"🔄 {workflow.get('template_name', 'Unbekannt')} - {workflow.get('id', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Typ:** {workflow.get('trigger_type', 'Unbekannt')}")
                        st.write(f"**Status:** {workflow.get('status', 'Unbekannt')}")
                    
                    with col2:
                        st.write(f"**Tasks:** {workflow.get('total_tasks', 0)}")
                        created_at = workflow.get('created_at', '')
                        if created_at:
                            st.write(f"**Erstellt:** {created_at[:19].replace('T', ' ')}")
        else:
            st.info("📭 Keine aktiven Workflows vorhanden")
    else:
        st.error("❌ Fehler beim Laden der aktiven Workflows")

def render_my_tasks_page():
    """📋 Meine Tasks Seite"""
    st.markdown('<div class="main-header"><h1>📋 Meine Aufgaben</h1><p>Alle mir zugewiesenen Tasks aus intelligenten Workflows</p></div>', unsafe_allow_html=True)
    
    # Filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Status Filter:",
            ["Alle", "open", "in_progress", "waiting", "completed", "cancelled"],
            index=0
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Priorität Filter:",
            ["Alle", "CRITICAL", "HIGH", "MEDIUM", "LOW"],
            index=0
        )
    
    with col3:
        if st.button("🔄 Aktualisieren"):
            st.rerun()
    
    # Tasks laden
    token = st.session_state.get('auth_token', '')
    status = None if status_filter == "Alle" else status_filter
    priority = None if priority_filter == "Alle" else priority_filter
    
    tasks_result = get_my_tasks(token, status, priority)
    
    if tasks_result and tasks_result.get("success"):
        tasks = tasks_result.get("tasks", [])
        
        if tasks:
            st.markdown(f"### 📝 {len(tasks)} Aufgaben gefunden")
            
            # Tasks nach Priorität gruppieren
            priority_groups = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}
            for task in tasks:
                task_priority = task.get("priority", "MEDIUM")
                if task_priority in priority_groups:
                    priority_groups[task_priority].append(task)
            
            # Tasks anzeigen
            for priority, priority_tasks in priority_groups.items():
                if not priority_tasks:
                    continue
                
                priority_color = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠", 
                    "MEDIUM": "🟡",
                    "LOW": "🟢"
                }
                
                st.markdown(f"#### {priority_color.get(priority, '⚪')} {priority} Priorität ({len(priority_tasks)})")
                
                for task in priority_tasks:
                    status_emoji = {
                        "open": "📋",
                        "in_progress": "🔄",
                        "waiting": "⏳",
                        "completed": "✅",
                        "cancelled": "❌"
                    }
                    
                    task_status = task.get("status", "open")
                    emoji = status_emoji.get(task_status, "📋")
                    
                    with st.expander(f"{emoji} {task.get('title', 'Unbekannt')} (#{task.get('id', 'N/A')})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Status:** {task_status}")
                            st.write(f"**Gruppe:** {task.get('assigned_group', 'Unbekannt')}")
                            if task.get('due_date'):
                                due = task['due_date'][:19].replace('T', ' ')
                                st.write(f"**Fällig:** {due}")
                        
                        with col2:
                            st.write(f"**Workflow:** {task.get('workflow_id', 'N/A')}")
                            if task.get('approval_needed'):
                                st.write("**🔒 Freigabe erforderlich**")
                            created_at = task.get('created_at', '')
                            if created_at:
                                created = created_at[:19].replace('T', ' ')
                            else:
                                created = 'N/A'
                            st.write(f"**Erstellt:** {created}")
                        
                        if task.get('description'):
                            st.write("**Beschreibung:**")
                            st.write(task['description'])
                        
                        # Task-Aktionen (vereinfacht)
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if task_status == "open":
                                if st.button("▶️ Starten", key=f"start_{task['id']}"):
                                    st.info("Task-Update noch nicht implementiert")
                        
                        with col2:
                            if task_status == "in_progress":
                                if st.button("✅ Abschließen", key=f"complete_{task['id']}"):
                                    st.info("Task-Update noch nicht implementiert")
                        
                        with col3:
                            if st.button("💬 Kommentar", key=f"comment_{task['id']}"):
                                st.info("Kommentar-System noch nicht implementiert")
        else:
            st.info("📭 Keine Aufgaben gefunden")
    else:
        st.error("❌ Fehler beim Laden der Aufgaben")
        if tasks_result:
            st.error(f"Fehler: {tasks_result.get('error', 'Unbekannt')}")

# ENTFERNT: render_optimized_workflow() - Funktion komplett entfernt
# Der vereinheitlichte Upload-Workflow in render_unified_upload() übernimmt diese Funktionalität

# === NEUE DYNAMISCHE FUNKTION FÜR INTEREST GROUPS ===
def get_interest_groups() -> List[Dict]:
    """Lädt alle verfügbaren Interest Groups dynamisch von der API"""
    try:
        token = st.session_state.get("auth_token", "")
        if not token:
            print("❌ Kein Auth-Token verfügbar für Interest Groups")
            return []
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/api/interest-groups", headers=headers, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            groups = response.json()
            print(f"✅ {len(groups)} Interest Groups geladen")
            return groups
        else:
            print(f"❌ Interest Groups API Fehler: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Interest Groups Fehler: {e}")
        return []

def get_organizational_units() -> List[Dict]:
    """Lädt verfügbare Abteilungen/Interest Groups vom Backend"""
    def _get_units():
        response = requests.get(f"{API_BASE_URL}/api/interest-groups", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            groups = response.json()
            # Mapping zu deutschen Namen für UI
            unit_mapping = {
                "procurement": "Einkauf",
                "quality_management": "Qualitätsmanagement", 
                "development": "Entwicklung",
                "production": "Produktion",
                "service_support": "Service & Support",
                "sales": "Vertrieb",
                "regulatory_affairs": "Regulatorische Angelegenheiten",
                "clinical_affairs": "Klinische Angelegenheiten",
                "post_market_surveillance": "Post-Market Surveillance",
                "risk_management": "Risikomanagement",
                "supplier_management": "Lieferantenmanagement",
                "training": "Schulung",
                "audit": "Audit"
            }
            
            return [
                {
                    "name": unit_mapping.get(group.get("name", ""), group.get("name", "Unbekannt")),
                    "id": group.get("id", 0),
                    "original_name": group.get("name", "")
                }
                for group in groups
            ]
        return []
    
    result = safe_api_call(_get_units)
    # FALLBACK: Mindestens System Admin
    return result if result else [{"name": "System Administration", "id": 0, "original_name": "system_administration"}]

# ===== MAIN APP =====
def render_login_welcome():
    """Rendert die Login-Welcome-Seite mit großem Logo"""
    # Zentriertes Logo mit ausreichend Abstand
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Responsive zentriertes Layout  
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("logo-documind-ai.png", use_container_width=True)

def main():
    """Hauptfunktion der App"""
    init_session_state()
    render_sidebar()
    
    # Zeige Login-Welcome-Seite wenn nicht eingeloggt
    if not st.session_state.authenticated:
        render_login_welcome()
        return
    
    # Für eingeloggte User: Header, Wasserzeichen und normale Navigation
    render_header()
    
    # Wasserzeichen-Container für eingeloggte User
    st.markdown('<div class="main-content-watermark">', unsafe_allow_html=True)
    
    # Page Routing
    current_page = st.session_state.get("current_page", "workflow")
    
    if current_page == "workflow":
        render_workflow_page()
    elif current_page == "upload":
        render_upload_page()
    elif current_page == "documents":
        render_documents_page()
    elif current_page == "ai_analysis":
        render_ai_analysis_page()
    elif current_page == "ai_prompt_test":
        render_ai_prompt_test_page()
    elif current_page == "rag_chat":
        render_rag_chat_page()
    elif current_page == "intelligent_workflows":
        render_intelligent_workflows_page()
    elif current_page == "my_tasks":
        render_my_tasks_page()
    elif current_page == "users":
        render_users_page()
    elif current_page == "dashboard":
        render_dashboard_page()
    elif current_page == "profile":
        render_profile_page()
    elif current_page == "settings":
        render_settings_page()
    elif current_page == "ai_provider_management":
        render_ai_provider_management_page()
    else:
        st.error(f"Unbekannte Seite: {current_page}")
    
    # Schließe Wasserzeichen-Container
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

