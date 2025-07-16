#!/usr/bin/env python3
"""
🧠 Intelligentes QMS-System Testskript

Testet alle neuen Funktionen:
- ✅ RAG-System für Chat mit Dokumenten
- ✅ Intelligente Workflow-Engine
- ✅ Automatische Task-Generierung
- ✅ Provider-Integration

Ausführung:
    python test_intelligent_qms.py
"""

import asyncio
import json
import requests
import time
from typing import Dict, List

# Konfiguration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"

def print_header(title: str):
    """Druckt einen formatierten Header"""
    print("\n" + "="*60)
    print(f"🧠 {title}")
    print("="*60)

def print_test(test_name: str, success: bool, details: str = ""):
    """Druckt ein Testergebnis"""
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if details:
        print(f"   → {details}")

def test_backend_connection() -> bool:
    """Testet Backend-Verbindung"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_rag_system() -> Dict:
    """Testet das RAG-System"""
    print_header("RAG-SYSTEM TESTS")
    
    results = {"total": 0, "passed": 0}
    
    # Test 1: RAG-Status
    results["total"] += 1
    try:
        response = requests.get(f"{API_BASE_URL}/api/rag/status", timeout=10)
        success = response.status_code == 200
        if success:
            data = response.json()
            available = data.get("rag_system", {}).get("available", False)
            print_test("RAG-Status abrufen", True, f"Verfügbar: {available}")
            if available:
                results["passed"] += 1
        else:
            print_test("RAG-Status abrufen", False, f"HTTP {response.status_code}")
    except Exception as e:
        print_test("RAG-Status abrufen", False, str(e))
    
    # Test 2: Dokumente indexieren
    results["total"] += 1
    try:
        response = requests.post(f"{API_BASE_URL}/api/rag/index-all", timeout=60)
        success = response.status_code == 200
        if success:
            data = response.json()
            indexed = data.get("indexed_documents", 0)
            print_test("Dokumente indexieren", True, f"{indexed} Dokumente indexiert")
            results["passed"] += 1
        else:
            print_test("Dokumente indexieren", False, f"HTTP {response.status_code}")
    except Exception as e:
        print_test("Dokumente indexieren", False, str(e))
    
    # Test 3: Semantische Suche
    results["total"] += 1
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/rag/search",
            params={"query": "Qualitätsmanagement", "max_results": 3},
            timeout=10
        )
        success = response.status_code == 200
        if success:
            data = response.json()
            count = data.get("results_count", 0)
            print_test("Semantische Suche", True, f"{count} Ergebnisse gefunden")
            results["passed"] += 1
        else:
            print_test("Semantische Suche", False, f"HTTP {response.status_code}")
    except Exception as e:
        print_test("Semantische Suche", False, str(e))
    
    # Test 4: RAG-Chat (benötigt Token)
    results["total"] += 1
    try:
        # Login für Token
        login_response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            data={"username": "admin@example.com", "password": "admin123"},
            timeout=5
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            
            # RAG-Chat testen
            response = requests.post(
                f"{API_BASE_URL}/api/rag/chat",
                json={"question": "Was ist Qualitätsmanagement?"},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                if data.get("success"):
                    answer_length = len(data.get("answer", ""))
                    confidence = data.get("confidence_score", 0)
                    print_test("RAG-Chat", True, f"Antwort: {answer_length} Zeichen, Konfidenz: {confidence:.1%}")
                    results["passed"] += 1
                else:
                    print_test("RAG-Chat", False, data.get("error", "Unbekannter Fehler"))
            else:
                print_test("RAG-Chat", False, f"HTTP {response.status_code}")
        else:
            print_test("RAG-Chat", False, "Login fehlgeschlagen")
    except Exception as e:
        print_test("RAG-Chat", False, str(e))
    
    return results

def test_intelligent_workflows() -> Dict:
    """Testet intelligente Workflows"""
    print_header("INTELLIGENTE WORKFLOW TESTS")
    
    results = {"total": 0, "passed": 0}
    
    # Login für Token
    try:
        login_response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            data={"username": "admin@example.com", "password": "admin123"},
            timeout=5
        )
        
        if login_response.status_code != 200:
            print_test("Login für Workflow-Tests", False, "Authentifizierung fehlgeschlagen")
            return results
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
    except Exception as e:
        print_test("Login für Workflow-Tests", False, str(e))
        return results
    
    # Test 1: Workflow-Trigger (Lieferantenproblem)
    results["total"] += 1
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/workflow/trigger-message",
            json={"message": "Bluetooth Modul nicht mehr lieferbar von Supplier XYZ"},
            headers=headers,
            timeout=15
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            if data.get("success") and data.get("workflow_triggered"):
                tasks_created = data.get("tasks_created", 0)
                workflow_name = data.get("workflow_name", "Unbekannt")
                print_test("Workflow-Trigger (Lieferant)", True, f"{workflow_name} - {tasks_created} Tasks erstellt")
                results["passed"] += 1
            else:
                confidence = data.get("confidence", 0)
                print_test("Workflow-Trigger (Lieferant)", False, f"Nicht ausgelöst - Konfidenz: {confidence:.1%}")
        else:
            print_test("Workflow-Trigger (Lieferant)", False, f"HTTP {response.status_code}")
    except Exception as e:
        print_test("Workflow-Trigger (Lieferant)", False, str(e))
    
    # Test 2: Workflow-Trigger (Geräteausfall)  
    results["total"] += 1
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/workflow/trigger-message",
            json={"message": "Lötofen ist defekt und muss repariert werden"},
            headers=headers,
            timeout=15
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            if data.get("success") and data.get("workflow_triggered"):
                tasks_created = data.get("tasks_created", 0)
                workflow_name = data.get("workflow_name", "Unbekannt")
                print_test("Workflow-Trigger (Geräteausfall)", True, f"{workflow_name} - {tasks_created} Tasks erstellt")
                results["passed"] += 1
            else:
                confidence = data.get("confidence", 0)
                print_test("Workflow-Trigger (Geräteausfall)", False, f"Nicht ausgelöst - Konfidenz: {confidence:.1%}")
        else:
            print_test("Workflow-Trigger (Geräteausfall)", False, f"HTTP {response.status_code}")
    except Exception as e:
        print_test("Workflow-Trigger (Geräteausfall)", False, str(e))
    
    # Test 3: Aktive Workflows anzeigen
    results["total"] += 1
    try:
        response = requests.get(f"{API_BASE_URL}/api/workflow/active", timeout=10)
        success = response.status_code == 200
        if success:
            data = response.json()
            if data.get("success"):
                workflows_count = data.get("total_count", 0)
                print_test("Aktive Workflows abrufen", True, f"{workflows_count} aktive Workflows")
                results["passed"] += 1
            else:
                print_test("Aktive Workflows abrufen", False, "API-Fehler")
        else:
            print_test("Aktive Workflows abrufen", False, f"HTTP {response.status_code}")
    except Exception as e:
        print_test("Aktive Workflows abrufen", False, str(e))
    
    # Test 4: Meine Tasks abrufen
    results["total"] += 1
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/tasks/my-tasks", 
            headers=headers,
            timeout=10
        )
        success = response.status_code == 200
        if success:
            data = response.json()
            if data.get("success"):
                tasks_count = data.get("total_count", 0)
                print_test("Meine Tasks abrufen", True, f"{tasks_count} zugewiesene Tasks")
                results["passed"] += 1
            else:
                print_test("Meine Tasks abrufen", False, data.get("error", "Unbekannt"))
        else:
            print_test("Meine Tasks abrufen", False, f"HTTP {response.status_code}")
    except Exception as e:
        print_test("Meine Tasks abrufen", False, str(e))
    
    return results

def test_ai_providers() -> Dict:
    """Testet KI-Provider Integration"""
    print_header("KI-PROVIDER TESTS")
    
    results = {"total": 0, "passed": 0}
    
    # Test 1: Provider-Status
    results["total"] += 1
    try:
        response = requests.get(f"{API_BASE_URL}/api/ai/free-providers-status", timeout=10)
        success = response.status_code == 200
        if success:
            data = response.json()
            provider_status = data.get("provider_status", {})
            available_count = data.get("total_available", 0)
            print_test("Provider-Status", True, f"{available_count} Provider verfügbar")
            results["passed"] += 1
            
            # Details der Provider
            for provider, details in provider_status.items():
                available = details.get("available", False)
                status_emoji = "✅" if available else "❌"
                print(f"   {status_emoji} {provider}: {details.get('status', 'unknown')}")
        else:
            print_test("Provider-Status", False, f"HTTP {response.status_code}")
    except Exception as e:
        print_test("Provider-Status", False, str(e))
    
    # Test 2: Ollama testen (falls verfügbar)
    results["total"] += 1
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/ai/test-provider",
            params={"provider": "ollama", "test_text": "Dies ist ein Testdokument."},
            timeout=20
        )
        success = response.status_code == 200
        if success:
            data = response.json()
            if data.get("success"):
                processing_time = data.get("processing_time_seconds", 0)
                print_test("Ollama Provider", True, f"Verarbeitung: {processing_time:.2f}s")
                results["passed"] += 1
            else:
                print_test("Ollama Provider", False, data.get("error", "Test fehlgeschlagen"))
        else:
            print_test("Ollama Provider", False, f"HTTP {response.status_code}")
    except Exception as e:
        print_test("Ollama Provider", False, str(e))
    
    # Test 3: Google Gemini testen (falls verfügbar)
    results["total"] += 1
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/ai/test-provider",
            params={"provider": "google_gemini", "test_text": "Dies ist ein Testdokument."},
            timeout=15
        )
        success = response.status_code == 200
        if success:
            data = response.json()
            if data.get("success"):
                processing_time = data.get("processing_time_seconds", 0)
                print_test("Google Gemini Provider", True, f"Verarbeitung: {processing_time:.2f}s")
                results["passed"] += 1
            else:
                print_test("Google Gemini Provider", False, data.get("error", "Test fehlgeschlagen"))
        else:
            print_test("Google Gemini Provider", False, f"HTTP {response.status_code}")
    except Exception as e:
        print_test("Google Gemini Provider", False, str(e))
    
    return results

def test_frontend_accessibility() -> Dict:
    """Testet Frontend-Erreichbarkeit"""
    print_header("FRONTEND TESTS")
    
    results = {"total": 1, "passed": 0}
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        success = response.status_code == 200
        if success:
            print_test("Frontend erreichbar", True, f"Streamlit läuft auf {FRONTEND_URL}")
            results["passed"] += 1
        else:
            print_test("Frontend erreichbar", False, f"HTTP {response.status_code}")
    except Exception as e:
        print_test("Frontend erreichbar", False, str(e))
    
    return results

def print_summary(all_results: Dict):
    """Druckt eine Zusammenfassung aller Tests"""
    print_header("TEST-ZUSAMMENFASSUNG")
    
    total_tests = 0
    total_passed = 0
    
    for category, results in all_results.items():
        total_tests += results["total"]
        total_passed += results["passed"]
        
        percentage = (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0
        status = "✅" if percentage == 100 else "⚠️" if percentage >= 50 else "❌"
        
        print(f"{status} {category}: {results['passed']}/{results['total']} ({percentage:.0f}%)")
    
    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print("\n" + "="*60)
    if overall_percentage >= 80:
        print("🎉 SYSTEM BEREIT! Das intelligente QMS läuft erfolgreich!")
    elif overall_percentage >= 50:
        print("⚠️ TEILWEISE BEREIT. Einige Funktionen benötigen Aufmerksamkeit.")
    else:
        print("❌ SYSTEM NICHT BEREIT. Mehrere kritische Probleme gefunden.")
    
    print(f"📊 Gesamt: {total_passed}/{total_tests} Tests bestanden ({overall_percentage:.0f}%)")
    print("="*60)
    
    print("\n🚀 NÄCHSTE SCHRITTE:")
    if overall_percentage >= 80:
        print("1. Frontend öffnen: http://localhost:8501")
        print("2. RAG-Chat testen: 'Was ist Qualitätsmanagement?'") 
        print("3. Workflow auslösen: 'Bluetooth Modul nicht lieferbar'")
        print("4. Tasks prüfen: Meine Tasks Seite")
    else:
        print("1. Backend-Logs prüfen: ./logs/")
        print("2. Dependencies installieren: pip install -r backend/requirements.txt")
        print("3. AI-Provider konfigurieren (siehe FREE-AI-SETUP.md)")
        print("4. Tests wiederholen: python test_intelligent_qms.py")

def main():
    """Hauptfunktion"""
    print("🧠 INTELLIGENTES QMS-SYSTEM - VOLLTEST")
    print("="*60)
    print("Testet RAG-Chat, intelligente Workflows und KI-Provider")
    print("Zeit für einen Kaffee - das dauert ein paar Minuten... ☕")
    
    # Backend-Verbindung prüfen
    if not test_backend_connection():
        print("\n❌ KRITISCHER FEHLER: Backend nicht erreichbar!")
        print("🔧 Backend starten: ./start-backend.sh")
        return
    
    print("✅ Backend ist erreichbar - starte Tests...")
    
    # Alle Tests ausführen
    all_results = {
        "RAG-System": test_rag_system(),
        "Intelligente Workflows": test_intelligent_workflows(),
        "KI-Provider": test_ai_providers(),
        "Frontend": test_frontend_accessibility()
    }
    
    # Zusammenfassung
    print_summary(all_results)

if __name__ == "__main__":
    main() 