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

# ===== SESSION STATE =====
def init_session_state():
    """Initialisiert Session State"""
    if "current_user" not in st.session_state:
        st.session_state.current_user = {
            "id": 2,
            "full_name": "Dr. Maria Qualität",
            "email": "maria.qm@company.com",
            "approval_level": 4,
            "organizational_unit": "Qualitätsmanagement"
        }
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "upload"
    
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
    
    # Navigation
    pages = {
        "📤 Upload": "upload",
        "📚 Dokumente": "documents",
        "📊 Dashboard": "dashboard",
        "⚙️ Einstellungen": "settings"
    }
    
    current_page = st.session_state.get("current_page", "upload")
    
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
    
    # Benutzer-Info
    st.sidebar.markdown("---")
    user = st.session_state.current_user
    st.sidebar.markdown(f"""
    **👤 {user['full_name']}**  
    📧 {user['email']}  
    🏷️ Level {user['approval_level']}  
    🏢 {user['organizational_unit']}
    """)

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
                st.markdown(f"**Beschreibung:** {doc.get('content')[:200]}...")
            
            # Aktionen
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"🗑️ Löschen", key=f"delete_{doc['id']}"):
                    if delete_document(doc['id']):
                        st.success("✅ Dokument gelöscht!")
                        st.rerun()
                    else:
                        st.error("❌ Löschen fehlgeschlagen!")

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
    current_page = st.session_state.get("current_page", "upload")
    
    if current_page == "upload":
        render_upload_page()
    elif current_page == "documents":
        render_documents_page()
    elif current_page == "dashboard":
        render_dashboard_page()
    elif current_page == "settings":
        render_settings_page()
    else:
        st.error(f"Unbekannte Seite: {current_page}")

if __name__ == "__main__":
    main()
