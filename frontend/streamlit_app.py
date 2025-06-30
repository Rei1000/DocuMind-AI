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
REQUEST_TIMEOUT = 30
MAX_FILE_SIZE_MB = 50

# ===== LOGGING SETUP =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== STREAMLIT CONFIG =====
st.set_page_config(
    page_title="KI-QMS Dokumentenverwaltung",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CSS STYLING =====
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f1aeb5;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #cce7ff;
        border: 1px solid #99d6ff;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .upload-area {
        border: 2px dashed #ccc;
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    
    .doc-card {
        border: 1px solid #ddd;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: white;
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

def get_document_types() -> List[str]:
    """Lädt verfügbare Dokumenttypen"""
    def _get_types():
        response = requests.get(f"{API_BASE_URL}/api/documents/types", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return []
    
    result = safe_api_call(_get_types)
    return result if result else ["OTHER", "QM_MANUAL", "SOP", "STANDARD_NORM", "WORK_INSTRUCTION"]

def upload_document_with_file(
    file_data, 
    document_type: str = "OTHER", 
    creator_id: int = 2, 
    title: Optional[str] = None,
    version: str = "1.0",
    content: Optional[str] = None,
    remarks: Optional[str] = None,
    chapter_numbers: Optional[str] = None
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
            "version": version
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
        response = requests.get(f"{API_BASE_URL}/api/users?limit=100", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
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
    <div class="main-header">
        <h1>🏥 KI-QMS Dokumentenverwaltung</h1>
        <p style="font-size: 1.2em; margin: 0;">ISO 13485 & MDR konforme Dokumentenlenkung</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Rendert die Sidebar mit Navigation und Status"""
    st.sidebar.title("🏥 KI-QMS Navigation")
    
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
        </div>
        """, unsafe_allow_html=True)
        
        # Reset after showing
        if st.button("🔄 Neuen Upload starten"):
            st.session_state.upload_success = None
            st.rerun()
        return
    
    # Upload Form
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
            # Dokumenttyp - verfügbare Typen laden
            doc_types = get_document_types()
            doc_type_options = {
                "OTHER": "🗂️ Sonstige",
                "QM_MANUAL": "📖 QM-Handbuch", 
                "SOP": "📋 SOP",
                "STANDARD_NORM": "⚖️ Norm/Standard (ISO, DIN, EN)",
                "WORK_INSTRUCTION": "📝 Arbeitsanweisung",
                "FORM": "📄 Formular",
                "SPECIFICATION": "📐 Spezifikation",
                "PROCEDURE": "🔄 Verfahren",
                "POLICY": "📜 Richtlinie"
            }
            
            # Nur verfügbare Typen anzeigen
            available_options = {k: v for k, v in doc_type_options.items() if k in doc_types}
            if not available_options:
                available_options = {"OTHER": "🗂️ Sonstige"}
            
            document_type = st.selectbox(
                "Dokumenttyp",
                options=list(available_options.keys()),
                format_func=lambda x: available_options[x],
                index=0,
                help="Der Dokumenttyp wird automatisch gesetzt falls nicht ausgewählt"
            )
            
            version = st.text_input("Version", value="1.0", help="Standardwert: 1.0")
        
        with col2:
            title = st.text_input(
                "Titel (optional)", 
                help="Wird automatisch aus dem Dokumentinhalt extrahiert falls leer"
            )
            
            content = st.text_area(
                "Beschreibung (optional)", 
                help="Wird automatisch aus dem Dokumentinhalt extrahiert falls leer"
            )
        
        # Erweiterte Optionen
        with st.expander("🔧 Erweiterte Optionen"):
            remarks = st.text_area("Bemerkungen (optional)")
            chapter_numbers = st.text_input(
                "Relevante Kapitel (optional)", 
                help="z.B. 4.2.3, 7.5.1"
            )
        
        # Submit Button
        submit_button = st.form_submit_button(
            "🚀 Dokument hochladen", 
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            if not uploaded_file:
                st.error("❌ Bitte wählen Sie eine Datei aus!")
                return
            
            with st.spinner("📤 Upload läuft..."):
                try:
                    # Upload durchführen
                    result = upload_document_with_file(
                        file_data=uploaded_file,
                        document_type=document_type,
                        creator_id=st.session_state.current_user["id"],
                        title=title,
                        version=version,
                        content=content,
                        remarks=remarks,
                        chapter_numbers=chapter_numbers
                    )
                    
                    if result:
                        st.session_state.upload_success = result
                        st.success("✅ Upload erfolgreich!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Upload fehlgeschlagen!")
                        
                except ValueError as e:
                    # Duplikat-Fehler speziell behandeln
                    if "DUPLIKAT" in str(e):
                        error_msg = str(e).replace("DUPLIKAT:", "").strip()
                        st.markdown(f"""
                        <div class="warning-box">
                            <h4>⚠️ Dokument-Duplikat erkannt!</h4>
                            <p>{error_msg}</p>
                            <p><strong>Lösungsvorschläge:</strong></p>
                            <ul>
                                <li>Verwenden Sie einen anderen Titel</li>
                                <li>Laden Sie eine andere Datei hoch</li>
                                <li>Prüfen Sie die bestehenden Dokumente in der Dokumentenverwaltung</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"❌ Validierungsfehler: {e}")
                        
                except Exception as e:
                    st.error(f"❌ Upload-Fehler: {e}")
                    logger.error(f"Upload Exception: {e}")

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
                **Erstellt:** {doc.get('created_at', 'N/A')[:10] if doc.get('created_at') else 'N/A'}  
                **Ersteller:** {doc.get('creator_id', 'N/A')}  
                **Dateigröße:** {doc.get('file_size', 'N/A')} Bytes  
                **MIME-Type:** {doc.get('mime_type', 'N/A')}
                """)
            
            if doc.get('content'):
                content = doc.get('content') or ""
                st.markdown(f"**Beschreibung:** {content[:200]}...")
            
            # Aktionen
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"🗑️ Löschen", key=f"delete_{doc['id']}"):
                    if delete_document(doc['id']):
                        st.success("✅ Dokument gelöscht!")
                        st.rerun()
                    else:
                        st.error("❌ Löschen fehlgeschlagen!")

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
    is_qm_user = "quality_management" in user.get("groups", [])
    
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
                    st.write(f"**Freigegeben:** {doc.get('approved_at', 'N/A')[:16]}")
                    
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
                # 13 Interessengruppen als Abteilungsoptionen
                organizational_unit = st.selectbox(
                    "Abteilung",
                    [
                        "System Administration",  # Für QMS Admin
                        "Team/Eingangsmodul", 
                        "Qualitätsmanagement", 
                        "Entwicklung", 
                        "Einkauf", 
                        "Produktion", 
                        "HR/Schulung", 
                        "Dokumentation", 
                        "Service/Support", 
                        "Vertrieb", 
                        "Regulatory Affairs", 
                        "IT-Abteilung", 
                        "Externe Auditoren", 
                        "Lieferanten"
                    ]
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
                        st.write(f"**Erstellt:** {user.get('created_at', 'N/A')[:10]}")
                    
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
                                available_groups = [
                                    {"id": 1, "name": "Team/Eingangsmodul"},
                                    {"id": 2, "name": "Qualitätsmanagement"},
                                    {"id": 3, "name": "Entwicklung"},
                                    {"id": 4, "name": "Einkauf"},
                                    {"id": 5, "name": "Produktion"},
                                    {"id": 6, "name": "HR/Schulung"},
                                    {"id": 7, "name": "Dokumentation"},
                                    {"id": 8, "name": "Service/Support"},
                                    {"id": 9, "name": "Vertrieb"},
                                    {"id": 10, "name": "Regulatory Affairs"},
                                    {"id": 11, "name": "IT-Abteilung"},
                                    {"id": 12, "name": "Externe Auditoren"},
                                    {"id": 13, "name": "Lieferanten"}
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
                                            
                                            col_confirm, col_abort = st.columns(2)
                                            
                                            with col_confirm:
                                                if st.button(f"🗑️ ENDGÜLTIG LÖSCHEN", key=f"final_delete_{user['id']}", type="primary"):
                                                    if admin_password:
                                                        if delete_user_permanently(user['id'], admin_password, st.session_state.auth_token):
                                                            st.success(f"User {user['full_name']} permanent gelöscht!")
                                                            st.rerun()
                                            
                                            with col_abort:
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

# ===== MAIN APP =====
def main():
    """Hauptfunktion der App"""
    init_session_state()
    render_header()
    render_sidebar()
    
    # Page Routing
    current_page = st.session_state.get("current_page", "workflow")
    
    if current_page == "workflow":
        render_workflow_page()
    elif current_page == "upload":
        render_upload_page()
    elif current_page == "documents":
        render_documents_page()
    elif current_page == "users":
        render_users_page()
    elif current_page == "dashboard":
        render_dashboard_page()
    elif current_page == "profile":
        render_profile_page()
    elif current_page == "settings":
        render_settings_page()
    else:
        st.error(f"Unbekannte Seite: {current_page}")

if __name__ == "__main__":
    main()
