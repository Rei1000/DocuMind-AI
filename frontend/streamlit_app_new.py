"""
KI-QMS Streamlit Frontend - Vollständig neu entwickelt

ISO 13485 und MDR konforme Dokumentenverwaltung mit rollenbasierter Berechtigung.
Komplett neues Frontend mit korrekten API-Aufrufen und modernem Design.

Autor: KI-QMS Team
Version: 3.0.0 - Komplett neu entwickelt
"""

import streamlit as st
import requests
import pandas as pd
import json
import os
import time
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import traceback

# ===== STREAMLIT PAGE CONFIG =====
st.set_page_config(
    page_title="🏥 KI-QMS | Dokumentenverwaltung",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM CSS FÜR MODERNES QMS DESIGN =====
def load_custom_css():
    st.markdown("""
    <style>
    /* Hauptdesign - Modern und professionell */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
    }
    
    .upload-zone {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 3px dashed #2a5298;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        border-color: #1e3c72;
        transform: translateY(-2px);
    }
    
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(40, 167, 69, 0.2);
    }
    
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(220, 53, 69, 0.2);
    }
    
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(23, 162, 184, 0.2);
    }
    
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #dee2e6;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    
    /* Status Badges */
    .status-draft { 
        background: #6c757d; color: white; 
        padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;
        display: inline-block; margin: 0.2rem;
    }
    .status-review { 
        background: #ffc107; color: black; 
        padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;
        display: inline-block; margin: 0.2rem;
    }
    .status-approved { 
        background: #28a745; color: white; 
        padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;
        display: inline-block; margin: 0.2rem;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: bold;
        border: none;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# ===== LOGGING =====
def setup_logging():
    """Konfiguriert strukturiertes Logging für das Frontend."""
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger("ki_qms_frontend_new")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        file_handler = logging.FileHandler(
            f"logs/ki_qms_frontend_new_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

# ===== KONFIGURATION =====
API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 30

# Dokumenttyp-Mapping für die UI
DOCUMENT_TYPE_MAPPING = {
    "QM_MANUAL": "📋 QM-Handbuch",
    "SOP": "📝 Standard Operating Procedure", 
    "WORK_INSTRUCTION": "🔧 Arbeitsanweisung",
    "FORM": "📄 Formular/Vorlage",
    "USER_MANUAL": "📖 Benutzerhandbuch",
    "SERVICE_MANUAL": "🔧 Servicehandbuch",
    "RISK_ASSESSMENT": "⚠️ Risikoanalyse",
    "VALIDATION_PROTOCOL": "✅ Validierungsprotokoll",
    "CALIBRATION_PROCEDURE": "📏 Kalibrierverfahren",
    "AUDIT_REPORT": "🔍 Audit-Bericht",
    "CAPA_DOCUMENT": "🔄 CAPA-Dokumentation",
    "TRAINING_MATERIAL": "🎓 Schulungsunterlagen",
    "SPECIFICATION": "📊 Spezifikation",
    "STANDARD_NORM": "🔖 Norm/Standard (ISO, DIN, EN)",
    "REGULATION": "⚖️ Verordnung/Richtlinie (MDR, FDA)",
    "GUIDANCE_DOCUMENT": "🧭 Leitfaden/Guidance",
    "OTHER": "📁 Sonstige Dokumente"
}

# ===== API FUNKTIONEN =====
def check_backend_status() -> bool:
    """Prüft ob das Backend erreichbar ist."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.ok
    except:
        return False

def get_document_types() -> List[str]:
    """Lädt verfügbare Dokumenttypen von der API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents/types", timeout=REQUEST_TIMEOUT)
        if response.ok:
            types = response.json()
            logger.info(f"✅ Loaded {len(types)} document types from API")
            return types
        else:
            logger.error(f"❌ Failed to load document types: {response.status_code}")
            return list(DOCUMENT_TYPE_MAPPING.keys())  # Fallback
    except Exception as e:
        logger.error(f"❌ Exception loading document types: {str(e)}")
        return list(DOCUMENT_TYPE_MAPPING.keys())  # Fallback

def get_users() -> List[Dict]:
    """Lädt alle Benutzer von der API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/users", timeout=REQUEST_TIMEOUT)
        if response.ok:
            users = response.json()
            logger.info(f"✅ Loaded {len(users)} users from API")
            return users
        else:
            logger.error(f"❌ Failed to load users: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"❌ Exception loading users: {str(e)}")
        return []

def get_documents(limit: int = 50) -> List[Dict]:
    """Lädt Dokumente von der API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents?limit={limit}", timeout=REQUEST_TIMEOUT)
        if response.ok:
            documents = response.json()
            logger.info(f"✅ Loaded {len(documents)} documents from API")
            return documents
        else:
            logger.error(f"❌ Failed to load documents: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"❌ Exception loading documents: {str(e)}")
        return []

def upload_document_with_file(
    file_data,
    title: str = None,
    document_type: str = "OTHER",
    creator_id: int = 2,
    version: str = "1.0",
    content: str = None,
    remarks: str = None,
    chapter_numbers: str = None
) -> Optional[Dict]:
    """
    Lädt ein Dokument mit Datei über die API hoch.
    
    Args:
        file_data: Streamlit UploadedFile object
        title: Dokumenttitel (optional - wird automatisch generiert)
        document_type: Dokumenttyp
        creator_id: ID des Erstellers
        version: Version
        content: Beschreibung
        remarks: Bemerkungen
        chapter_numbers: Kapitelnummern
        
    Returns:
        API Response oder None bei Fehlern
    """
    try:
        # Multipart Form Data vorbereiten
        files = {}
        if file_data:
            file_data.seek(0)  # Reset file pointer
            files["file"] = (file_data.name, file_data.read(), file_data.type)
        
        form_data = {
            "creator_id": str(creator_id),
            "document_type": document_type,
            "version": version
        }
        
        # Optionale Felder nur hinzufügen wenn vorhanden
        if title:
            form_data["title"] = title
        if content:
            form_data["content"] = content
        if remarks:
            form_data["remarks"] = remarks
        if chapter_numbers:
            form_data["chapter_numbers"] = chapter_numbers
        
        logger.info(f"🚀 Uploading document: {file_data.name if file_data else 'No file'}")
        logger.info(f"📝 Form data: {form_data}")
        
        response = requests.post(
            f"{API_BASE_URL}/api/documents/with-file",
            files=files,
            data=form_data,
            timeout=REQUEST_TIMEOUT
        )
        
        logger.info(f"📡 Response status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            logger.info(f"✅ Successfully uploaded document: ID {result.get('id')}")
            return result
        else:
            error_text = response.text
            logger.error(f"❌ Upload failed: {response.status_code} - {error_text}")
            
            # Parse error message for better display
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', error_text)
            except:
                error_detail = error_text
                
            raise Exception(f"Status {response.status_code}: {error_detail}")
            
    except Exception as e:
        logger.error(f"❌ Upload exception: {str(e)}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        raise e

def delete_document(document_id: int) -> bool:
    """Löscht ein Dokument."""
    try:
        response = requests.delete(f"{API_BASE_URL}/api/documents/{document_id}", timeout=REQUEST_TIMEOUT)
        if response.ok:
            logger.info(f"✅ Successfully deleted document ID: {document_id}")
            return True
        else:
            logger.error(f"❌ Failed to delete document {document_id}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Exception deleting document {document_id}: {str(e)}")
        return False

# ===== SESSION STATE =====
def init_session_state():
    """Initialisiert Streamlit Session State."""
    if "current_user" not in st.session_state:
        # Default: QM-Benutzer
        st.session_state.current_user = {
            "id": 2,
            "full_name": "Dr. Maria Qualität",
            "email": "maria.qm@company.com",
            "approval_level": 4,
            "organizational_unit": "Qualitätsmanagement"
        }
        logger.info(f"🔐 Initialized session with user: {st.session_state.current_user['full_name']}")
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "upload"
    
    if "upload_success" not in st.session_state:
        st.session_state.upload_success = False

# ===== UI KOMPONENTEN =====
def render_header():
    """Rendert den Hauptheader der Anwendung."""
    st.markdown("""
    <div class="main-header">
        <h1>🏥 KI-QMS Dokumentenverwaltung</h1>
        <p style="font-size: 1.2em; margin: 0;">ISO 13485 & MDR konforme Dokumentenlenkung</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Rendert die Sidebar mit Navigation."""
    st.sidebar.title("🏥 KI-QMS Navigation")
    
    # Navigation
    pages = {
        "📤 Upload": "upload",
        "📚 Dokumente": "management", 
        "📊 Dashboard": "dashboard",
        "⚙️ Einstellungen": "settings"
    }
    
    current_page = st.session_state.get("current_page", "upload")
    
    for label, page_id in pages.items():
        if st.sidebar.button(
            label, 
            key=f"nav_{page_id}", 
            use_container_width=True,
            type="primary" if page_id == current_page else "secondary"
        ):
            st.session_state.current_page = page_id
            st.session_state.upload_success = False  # Reset upload success
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Backend Status
    if check_backend_status():
        st.sidebar.success("✅ Backend Online")
    else:
        st.sidebar.error("❌ Backend Offline")
    
    # Benutzerinformationen
    st.sidebar.markdown("---")
    user = st.session_state.current_user
    st.sidebar.markdown(f"""
    **👤 {user['full_name']}**  
    📧 {user['email']}  
    🏷️ Level {user['approval_level']}  
    🏢 {user['organizational_unit']}
    """)
    
    if st.sidebar.button("🚪 Abmelden", key="logout", use_container_width=True):
        st.session_state.current_user = None
        st.session_state.current_page = "upload"
        st.rerun()

def render_upload_page():
    """Rendert die Upload-Seite mit korrekten API-Aufrufen."""
    
    st.markdown("## 📤 Dokument hochladen")
    
    # Info-Box über Features
    st.markdown("""
    <div class="info-box">
        <h4>🤖 Intelligente Upload-Features</h4>
        <ul>
            <li><strong>Automatische Titel-Extraktion:</strong> Titel wird aus Norm-Nummern und Dokumentinhalt extrahiert</li>
            <li><strong>Smart-Beschreibung:</strong> Relevante Inhalte werden automatisch als Beschreibung verwendet</li>
            <li><strong>QMS-Keywords:</strong> Erkennt medizinprodukte-spezifische Begriffe</li>
            <li><strong>Duplikat-Erkennung:</strong> Verhindert doppelte Uploads</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Reset success state bei neuer Seite
    if 'just_loaded' not in st.session_state:
        st.session_state.upload_success = False
        st.session_state.just_loaded = True
    
    # Upload Form
    with st.form("document_upload_form_new", clear_on_submit=True):
        
        # Datei-Upload
        st.markdown("### 📁 Datei auswählen")
        uploaded_file = st.file_uploader(
            "Datei hochladen",
            type=['pdf', 'doc', 'docx', 'md', 'txt', 'xls', 'xlsx'],
            help="Unterstützte Formate: PDF, DOC, DOCX, MD, TXT, XLS, XLSX (max. 50MB)",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            file_size_mb = len(uploaded_file.getvalue()) / 1024 / 1024
            st.success(f"📁 **{uploaded_file.name}** ausgewählt ({file_size_mb:.1f} MB)")
        
        st.markdown("---")
        
        # Dokument-Konfiguration
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Dokumenttyp")
            doc_types = get_document_types()
            if doc_types:
                selected_type = st.selectbox(
                    "Dokumenttyp",
                    options=doc_types,
                    format_func=lambda x: DOCUMENT_TYPE_MAPPING.get(x, x),
                    index=doc_types.index("STANDARD_NORM") if "STANDARD_NORM" in doc_types else 0,
                    label_visibility="collapsed"
                )
            else:
                st.error("❌ Kann Dokumenttypen nicht laden")
                return
        
        with col2:
            st.markdown("### 🔢 Version")
            version = st.text_input(
                "Version",
                value="1.0",
                help="z.B. 1.0, 1.1, 2.0",
                label_visibility="collapsed"
            )
        
        # Optionale Felder
        st.markdown("### 📝 Optionale Informationen")
        st.caption("Alle Felder können leer gelassen werden - sie werden automatisch aus dem Dokumentinhalt extrahiert")
        
        title = st.text_input(
            "📝 Titel des Dokuments (optional)",
            placeholder="Wird automatisch aus Dokumentinhalt extrahiert...",
            help="Wird automatisch aus dem Dokumentinhalt extrahiert wenn leer gelassen"
        )
        
        content = st.text_area(
            "📄 Beschreibung (optional)",
            placeholder="Wird automatisch aus Dokumentinhalt extrahiert...",
            height=100,
            help="Wird automatisch aus dem Dokumentinhalt extrahiert wenn leer gelassen"
        )
        
        col3, col4 = st.columns(2)
        
        with col3:
            chapter_numbers = st.text_input(
                "📖 Relevante Kapitel (optional)",
                placeholder="z.B. 4.2.3, 7.5.1",
                help="Für Normen: Welche Kapitel sind relevant?"
            )
        
        with col4:
            remarks = st.text_input(
                "💬 Bemerkungen (optional)",
                placeholder="Zusätzliche Hinweise...",
                help="QM-Manager Hinweise oder Bemerkungen"
            )
        
        # Upload Button
        st.markdown("---")
        submit_button = st.form_submit_button(
            "🚀 Dokument hochladen",
            type="primary",
            use_container_width=True
        )
        
        if submit_button:
            if not uploaded_file:
                st.error("❌ Bitte wählen Sie eine Datei aus")
                return
            
            # Upload verarbeiten
            with st.spinner("📤 Dokument wird hochgeladen..."):
                try:
                    result = upload_document_with_file(
                        file_data=uploaded_file,
                        title=title if title.strip() else None,
                        document_type=selected_type,
                        creator_id=st.session_state.current_user["id"],
                        version=version,
                        content=content if content.strip() else None,
                        remarks=remarks if remarks.strip() else None,
                        chapter_numbers=chapter_numbers if chapter_numbers.strip() else None
                    )
                    
                    if result:
                        st.session_state.upload_success = True
                        st.session_state.upload_result = result
                        st.session_state.just_loaded = False
                        st.rerun()
                        
                except Exception as e:
                    error_msg = str(e)
                    
                    st.markdown(f"""
                    <div class="error-box">
                        <h4>❌ Upload fehlgeschlagen</h4>
                        <p><strong>Fehler:</strong> {error_msg}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Spezielle Behandlung für bekannte Fehler
                    if "409" in error_msg or "Duplikat" in error_msg:
                        st.warning("""
                        🔍 **Mögliche Ursachen:**
                        - Ein Dokument mit gleichem Titel existiert bereits
                        - Die gleiche Datei wurde bereits hochgeladen
                        - Identischer Dateiinhalt gefunden
                        
                        **Lösungsvorschläge:**
                        - Prüfen Sie die bestehenden Dokumente
                        - Verwenden Sie einen anderen Titel
                        - Laden Sie eine andere Datei hoch
                        """)
                    
                    elif "400" in error_msg:
                        st.info("""
                        💡 **Eingabe prüfen:**
                        - Ist der Dokumenttyp korrekt gewählt?
                        - Ist die Datei in einem unterstützten Format?
                        - Sind alle Pflichtfelder ausgefüllt?
                        """)
                    
                    logger.error(f"❌ Upload error in UI: {error_msg}")
    
    # Erfolgsanzeige (außerhalb des Forms)
    if st.session_state.get('upload_success', False) and 'upload_result' in st.session_state:
        result = st.session_state.upload_result
        
        st.markdown("""
        <div class="success-box">
            <h3>🎉 Upload erfolgreich!</h3>
            <p>Das Dokument wurde erfolgreich hochgeladen und verarbeitet.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Ergebnisse anzeigen
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📄 Dokument Details")
            st.info(f"""
            **ID:** {result['id']}  
            **Titel:** {result['title']}  
            **Typ:** {DOCUMENT_TYPE_MAPPING.get(result['document_type'], result['document_type'])}  
            **Version:** {result['version']}  
            **Status:** {result['status'].upper()}  
            **Dokumentnummer:** {result.get('document_number', 'N/A')}
            """)
        
        with col2:
            if result.get('file_name'):
                file_size_mb = round(result.get('file_size', 0) / 1024 / 1024, 2)
                st.markdown("#### 📁 Datei Details")
                st.info(f"""
                **Name:** {result['file_name']}  
                **Größe:** {file_size_mb} MB  
                **Typ:** {result.get('mime_type', 'N/A')}  
                **Hash:** {result.get('file_hash', 'N/A')[:12]}...
                """)
        
        # Text-Extraktion anzeigen
        if result.get('extracted_text') and len(result['extracted_text']) > 20:
            with st.expander("📖 Extrahierter Text (Vorschau)"):
                extracted_text = result['extracted_text']
                if len(extracted_text) > 500:
                    st.text(extracted_text[:500] + "...")
                    st.caption(f"Text gekürzt. Vollständig: {len(extracted_text)} Zeichen")
                else:
                    st.text(extracted_text)
        
        # Action Buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📚 Zu Dokumenten", type="primary", use_container_width=True):
                st.session_state.current_page = "management"
                st.session_state.upload_success = False
                st.rerun()
        
        with col2:
            if st.button("🔄 Neues Dokument", type="secondary", use_container_width=True):
                st.session_state.upload_success = False
                del st.session_state.upload_result
                st.rerun()
        
        with col3:
            if st.button("📊 Dashboard", type="secondary", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.session_state.upload_success = False
                st.rerun()

def render_management_page():
    """Rendert die Dokumentenverwaltungsseite."""
    st.markdown("## 📚 Dokumentenverwaltung")
    
    # Dokumente laden
    with st.spinner("📄 Lade Dokumente..."):
        documents = get_documents(100)
    
    if not documents:
        st.warning("📭 Keine Dokumente gefunden oder Backend nicht erreichbar")
        return
    
    st.success(f"📊 {len(documents)} Dokumente gefunden")
    
    # Filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        doc_types = get_document_types()
        type_filter = st.selectbox(
            "🏷️ Nach Typ filtern",
            options=["Alle"] + doc_types,
            format_func=lambda x: "Alle Typen" if x == "Alle" else DOCUMENT_TYPE_MAPPING.get(x, x)
        )
    
    with col2:
        status_filter = st.selectbox(
            "📊 Nach Status filtern",
            options=["Alle", "draft", "review", "approved", "obsolete"],
            format_func=lambda x: {
                "Alle": "Alle Status",
                "draft": "🔄 Entwurf",
                "review": "👀 Prüfung", 
                "approved": "✅ Freigegeben",
                "obsolete": "📁 Veraltet"
            }.get(x, x)
        )
    
    with col3:
        search_term = st.text_input("🔍 Suche", placeholder="Titel, Inhalt...")
    
    # Dokumente filtern
    filtered_docs = documents
    
    if type_filter != "Alle":
        filtered_docs = [d for d in filtered_docs if d.get('document_type') == type_filter]
    
    if status_filter != "Alle":
        filtered_docs = [d for d in filtered_docs if d.get('status') == status_filter]
    
    if search_term:
        search_lower = search_term.lower()
        filtered_docs = [d for d in filtered_docs if 
                        search_lower in d.get('title', '').lower() or 
                        search_lower in d.get('content', '').lower()]
    
    st.markdown(f"**📊 {len(filtered_docs)} von {len(documents)} Dokumenten**")
    
    # Dokumente anzeigen
    for doc in filtered_docs:
        with st.expander(f"📄 {doc.get('title', 'Ohne Titel')} (ID: {doc.get('id')})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                **🏷️ Typ:** {DOCUMENT_TYPE_MAPPING.get(doc.get('document_type'), doc.get('document_type'))}  
                **🔢 Version:** {doc.get('version', 'N/A')}  
                **📊 Status:** {doc.get('status', 'N/A').upper()}  
                **📅 Erstellt:** {doc.get('created_at', 'N/A')[:10] if doc.get('created_at') else 'N/A'}  
                **👤 Ersteller:** {doc.get('creator', {}).get('full_name', 'N/A')}
                """)
                
                if doc.get('content'):
                    st.markdown(f"**📝 Beschreibung:** {doc['content'][:200]}...")
                
                if doc.get('file_name'):
                    file_size_mb = round(doc.get('file_size', 0) / 1024 / 1024, 2) if doc.get('file_size') else 0
                    st.markdown(f"**📁 Datei:** {doc['file_name']} ({file_size_mb} MB)")
            
            with col2:
                if st.button(f"🗑️ Löschen", key=f"delete_{doc['id']}", type="secondary"):
                    if delete_document(doc['id']):
                        st.success("✅ Dokument gelöscht")
                        st.rerun()
                    else:
                        st.error("❌ Fehler beim Löschen")

def render_dashboard_page():
    """Rendert das Dashboard."""
    st.markdown("## 📊 KI-QMS Dashboard")
    
    # Statistiken laden
    with st.spinner("📊 Lade Dashboard-Daten..."):
        documents = get_documents(100)
        users = get_users()
    
    # Metriken
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📄 Gesamt Dokumente</h3>
            <h2 style="color: #2a5298;">{}</h2>
        </div>
        """.format(len(documents)), unsafe_allow_html=True)
    
    with col2:
        draft_count = len([d for d in documents if d.get('status') == 'draft'])
        st.markdown("""
        <div class="metric-card">
            <h3>🔄 Entwürfe</h3>
            <h2 style="color: #ffc107;">{}</h2>
        </div>
        """.format(draft_count), unsafe_allow_html=True)
    
    with col3:
        approved_count = len([d for d in documents if d.get('status') == 'approved'])
        st.markdown("""
        <div class="metric-card">
            <h3>✅ Freigegeben</h3>
            <h2 style="color: #28a745;">{}</h2>
        </div>
        """.format(approved_count), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>👥 Benutzer</h3>
            <h2 style="color: #17a2b8;">{}</h2>
        </div>
        """.format(len(users)), unsafe_allow_html=True)
    
    # Dokumenttyp-Verteilung
    if documents:
        st.markdown("### 📊 Dokumenttyp-Verteilung")
        
        type_counts = {}
        for doc in documents:
            doc_type = doc.get('document_type', 'OTHER')
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        # Als Tabelle anzeigen
        type_data = []
        for doc_type, count in type_counts.items():
            type_data.append({
                "Dokumenttyp": DOCUMENT_TYPE_MAPPING.get(doc_type, doc_type),
                "Anzahl": count,
                "Anteil": f"{count/len(documents)*100:.1f}%"
            })
        
        df = pd.DataFrame(type_data)
        st.dataframe(df, use_container_width=True)
    
    # Letzte Aktivitäten
    st.markdown("### 🕒 Letzte Aktivitäten")
    
    # Sortiere Dokumente nach Erstellungsdatum
    recent_docs = sorted(documents, 
                        key=lambda x: x.get('created_at', ''), 
                        reverse=True)[:10]
    
    for doc in recent_docs:
        created_at = doc.get('created_at', '')
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                time_str = dt.strftime("%d.%m.%Y %H:%M")
            except:
                time_str = created_at[:16]
        else:
            time_str = "Unbekannt"
        
        status_emoji = {
            'draft': '🔄',
            'review': '👀', 
            'approved': '✅',
            'obsolete': '📁'
        }.get(doc.get('status'), '📄')
        
        st.markdown(f"""
        {status_emoji} **{doc.get('title', 'Ohne Titel')}**  
        {DOCUMENT_TYPE_MAPPING.get(doc.get('document_type'), doc.get('document_type'))} | {time_str}
        """)

def render_settings_page():
    """Rendert die Einstellungsseite."""
    st.markdown("## ⚙️ Einstellungen")
    
    # System-Status
    st.markdown("### 🔧 System-Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if check_backend_status():
            st.success("✅ Backend erreichbar")
        else:
            st.error("❌ Backend nicht erreichbar")
        
        st.info(f"📡 **API URL:** {API_BASE_URL}")
        st.info(f"⏱️ **Timeout:** {REQUEST_TIMEOUT}s")
    
    with col2:
        # Test API-Endpunkte
        st.markdown("#### 🧪 API-Tests")
        
        if st.button("Test Dokumenttypen", use_container_width=True):
            try:
                types = get_document_types()
                st.success(f"✅ {len(types)} Dokumenttypen geladen")
            except Exception as e:
                st.error(f"❌ Fehler: {str(e)}")
        
        if st.button("Test Benutzer", use_container_width=True):
            try:
                users = get_users()
                st.success(f"✅ {len(users)} Benutzer geladen")
            except Exception as e:
                st.error(f"❌ Fehler: {str(e)}")
        
        if st.button("Test Dokumente", use_container_width=True):
            try:
                docs = get_documents(5)
                st.success(f"✅ {len(docs)} Dokumente geladen")
            except Exception as e:
                st.error(f"❌ Fehler: {str(e)}")
    
    st.markdown("---")
    
    # Benutzer-Einstellungen
    st.markdown("### 👤 Benutzer-Einstellungen")
    
    user = st.session_state.current_user
    st.json(user)
    
    st.markdown("---")
    
    # Debug-Informationen
    st.markdown("### 🐛 Debug-Informationen")
    
    with st.expander("Session State"):
        st.json(dict(st.session_state))
    
    with st.expander("System-Info"):
        st.write({
            "Python Version": "3.8+",
            "Streamlit Version": st.__version__,
            "Current Time": datetime.now().isoformat(),
            "Upload Success": st.session_state.get('upload_success', False)
        })

# ===== MAIN APPLICATION =====
def main():
    """Hauptfunktion der Anwendung."""
    
    # CSS laden
    load_custom_css()
    
    # Session State initialisieren
    init_session_state()
    
    # Header rendern
    render_header()
    
    # Sidebar rendern
    render_sidebar()
    
    # Aktuelle Seite rendern
    current_page = st.session_state.get("current_page", "upload")
    
    if current_page == "upload":
        render_upload_page()
    elif current_page == "management":
        render_management_page()
    elif current_page == "dashboard":
        render_dashboard_page()
    elif current_page == "settings":
        render_settings_page()
    else:
        st.error(f"❌ Unbekannte Seite: {current_page}")

if __name__ == "__main__":
    main() 