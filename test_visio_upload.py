#!/usr/bin/env python3
"""
Test-Skript für Visio-Upload-Funktionalität

Dieses Skript testet die komplette Visio-Upload-Pipeline:
1. Login
2. Upload eines Dokuments mit upload_method="visio"
3. Schrittweise Verarbeitung
4. Status-Abfragen
"""

import requests
import time
import json
from pathlib import Path

# API-Konfiguration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
UPLOAD_URL = f"{BASE_URL}/api/upload"

# Test-Credentials
TEST_USER = "admin@qms.local"
TEST_PASSWORD = "admin123"

def login():
    """Login und Token abrufen"""
    print("🔐 Login als admin@qms.local...")
    
    response = requests.post(
        LOGIN_URL,
        data={
            "username": TEST_USER,
            "password": TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login erfolgreich!")
        return token
    else:
        print(f"❌ Login fehlgeschlagen: {response.status_code}")
        print(response.text)
        return None

def upload_visio_document(token, file_path):
    """Dokument mit Visio-Methode hochladen"""
    print(f"\n📤 Lade Dokument hoch: {file_path}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, "application/pdf")}
        data = {
            "title": "Test QM-Prozess",
            "document_type": "process",
            "upload_method": "visio"  # Wichtig: Visio-Upload!
        }
        
        response = requests.post(
            UPLOAD_URL,
            headers=headers,
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        doc_id = response.json()["id"]
        print(f"✅ Upload erfolgreich! Dokument-ID: {doc_id}")
        return doc_id
    else:
        print(f"❌ Upload fehlgeschlagen: {response.status_code}")
        print(response.text)
        return None

def process_visio_step(token, doc_id, step_name, endpoint):
    """Einzelnen Visio-Verarbeitungsschritt ausführen"""
    print(f"\n🔄 Führe {step_name} aus...")
    
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/documents/{doc_id}/visio-step/{endpoint}"
    
    response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {step_name} erfolgreich!")
        if "message" in result:
            print(f"   {result['message']}")
        return True
    else:
        print(f"❌ {step_name} fehlgeschlagen: {response.status_code}")
        print(response.text)
        return False

def check_visio_status(token, doc_id):
    """Visio-Verarbeitungsstatus abrufen"""
    print(f"\n📊 Prüfe Visio-Status...")
    
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/documents/{doc_id}/visio-status"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        status = response.json()
        print(f"✅ Status abgerufen:")
        print(f"   - Processing State: {status['processing_state']}")
        print(f"   - Validation Status: {status['validation_status']}")
        print(f"   - Word Count: {status.get('word_count', 0)}")
        print(f"   - Coverage: {status.get('validation_coverage', 0)}%")
        return status
    else:
        print(f"❌ Status-Abruf fehlgeschlagen: {response.status_code}")
        return None

def main():
    """Haupttest-Funktion"""
    print("🚀 Starte Visio-Upload-Test")
    print("=" * 50)
    
    # 1. Login
    token = login()
    if not token:
        return
    
    # 2. Upload
    test_file = "test_qm_process.pdf"
    if not Path(test_file).exists():
        print(f"❌ Test-Datei {test_file} nicht gefunden!")
        return
    
    doc_id = upload_visio_document(token, test_file)
    if not doc_id:
        return
    
    # 3. Schrittweise Verarbeitung
    steps = [
        ("PNG-Generierung", "generate-png"),
        ("Wort-Extraktion", "extract-words"),
        ("Strukturanalyse", "analyze-structure"),
        ("Validierung", "validate")
    ]
    
    for step_name, endpoint in steps:
        success = process_visio_step(token, doc_id, step_name, endpoint)
        if not success:
            print("⚠️ Verarbeitung abgebrochen")
            break
        time.sleep(1)  # Kurze Pause zwischen Schritten
    
    # 4. Finaler Status
    final_status = check_visio_status(token, doc_id)
    
    if final_status and final_status["processing_state"] == "VALIDATED":
        print(f"\n✨ Visio-Verarbeitung erfolgreich abgeschlossen!")
        print(f"📄 Dokument {doc_id} ist bereit für QM-Freigabe")
    
    print("\n" + "=" * 50)
    print("Test abgeschlossen!")

if __name__ == "__main__":
    main()