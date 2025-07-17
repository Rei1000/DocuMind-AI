#!/usr/bin/env python3
"""
🎯 Document-to-Image Vision System Test

Testet die revolutionäre Lösung für komplexe QM-Dokumente:
1. Document → High-Quality Images (300 DPI)
2. GPT-4o Vision API → Comprehensive Analysis
3. >1000 Zeichen Extraktion Ziel

Speziell optimiert für PA 8.2.1 und ähnliche Flussdiagramm-Dokumente.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_document_vision_comprehensive():
    """Test Document Vision Engine mit verschiedenen Dokumenten"""
    
    print("🎯 DOCUMENT-TO-IMAGE VISION SYSTEM TEST")
    print("=" * 70)
    print()
    
    # Test-Dokumente
    test_documents = [
        "uploads/PA 8.2.1 [03] - Behandlung von Reparaturen.docx",
        "backend/uploads/test_documents/PA 8.2.1 [03] - Behandlung von Reparaturen.docx",
        "backend/uploads/PA 8.2.2-1 [00a] - Behandlung von Reklamationen.pdf"
    ]
    
    # Finde verfügbares Test-Dokument
    test_file = None
    for doc_path in test_documents:
        if Path(doc_path).exists():
            test_file = doc_path
            break
    
    if not test_file:
        print("❌ Kein Test-Dokument gefunden!")
        print("Getestete Pfade:")
        for path in test_documents:
            print(f"   - {path}")
        return False
    
    print(f"📄 Test-Dokument: {test_file}")
    print()
    
    # Run async test
    return asyncio.run(test_document_vision_async(test_file))

async def test_document_vision_async(file_path: str):
    """Async Test der Document Vision Engine"""
    
    try:
        # Import Document Vision Engine
        from app.document_vision_engine import extract_text_with_document_vision
        
        print("🔄 Starte Document-to-Image Vision OCR...")
        print("=" * 50)
        print()
        
        # 1. Document Vision OCR
        result = await extract_text_with_document_vision(file_path)
        
        print("📊 ERGEBNISSE:")
        print("=" * 50)
        print(f"✅ Erfolgreich: {result['success']}")
        print(f"📄 Methode: {result['method']}")
        print(f"🖼️ Bilder verarbeitet: {result.get('images_processed', 0)}")
        print(f"📋 Seiten analysiert: {result.get('pages_analyzed', 0)}")
        print(f"📝 Zeichen extrahiert: {result.get('total_characters', 0)}")
        print()
        
        # 2. Success Metrics
        if 'success_metrics' in result:
            metrics = result['success_metrics']
            print("📈 SUCCESS METRICS:")
            print(f"🎯 Ziel: {metrics['target_characters']} Zeichen")
            print(f"✅ Erreicht: {metrics['achieved_characters']} Zeichen")
            print(f"📊 Erfolgsrate: {metrics['success_rate']:.1f}%")
            print(f"🏆 Qualitätsscore: {metrics['quality_score']:.1f}/100")
            print()
        
        # 3. Process References
        refs = result.get('process_references', [])
        if refs:
            print(f"📎 PROZESS-REFERENZEN ({len(refs)}):")
            for ref in refs[:10]:  # Erste 10
                print(f"   - {ref}")
            if len(refs) > 10:
                print(f"   ... und {len(refs) - 10} weitere")
            print()
        
        # 4. Text Sample
        text = result.get('extracted_text', '')
        if text:
            print("📝 TEXT-EXTRAKTION (Erste 500 Zeichen):")
            print("-" * 50)
            print(text[:500])
            if len(text) > 500:
                print(f"\n... [+{len(text) - 500} weitere Zeichen]")
            print()
        
        # 5. Detailed Vision Results
        vision_results = result.get('vision_results', [])
        if vision_results:
            print(f"🔍 VISION API DETAILS ({len(vision_results)} Bilder):")
            for i, vision_result in enumerate(vision_results):
                print(f"   Bild {i+1}:")
                print(f"   - Erfolg: {vision_result.get('success', False)}")
                print(f"   - Zeichen: {len(vision_result.get('extracted_text', ''))}")
                print(f"   - Referenzen: {len(vision_result.get('process_references', []))}")
            print()
        
        # 6. Quality Assessment
        chars = result.get('total_characters', 0)
        print("🎯 QUALITÄTSBEWERTUNG:")
        print("-" * 50)
        
        if chars >= 1000:
            print(f"🎉 EXZELLENT: {chars} Zeichen (Ziel erreicht!)")
        elif chars >= 500:
            print(f"✅ GUT: {chars} Zeichen (50% des Ziels)")
        elif chars >= 100:
            print(f"⚠️ MÄSSIG: {chars} Zeichen (Verbesserung nötig)")
        else:
            print(f"❌ UNZUREICHEND: {chars} Zeichen (Grundlegendes Problem)")
        
        # 7. Recommendations
        print()
        print("💡 EMPFEHLUNGEN:")
        if not result['success']:
            print("   - System-Dependencies prüfen (LibreOffice, PyMuPDF)")
            print("   - OpenAI API Key validieren")
            print("   - Dokumentformat überprüfen")
        elif chars < 1000:
            print("   - Vision-Prompts für spezifische Dokumente optimieren")
            print("   - DPI-Auflösung erhöhen (aktuell: 300 DPI)")
            print("   - Multi-Page Verarbeitung verbessern")
        else:
            print("   - ✅ System funktioniert optimal!")
            print("   - Für Produktiveinsatz bereit")
        
        return result['success'] and chars >= 1000
        
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("💡 Lösung: Document Vision Engine Module überprüfen")
        return False
    
    except Exception as e:
        print(f"❌ Test-Fehler: {e}")
        print(f"💡 Details: {type(e).__name__}")
        return False

def print_system_info():
    """System-Informationen anzeigen"""
    print("🔧 SYSTEM-INFORMATIONEN:")
    print("-" * 30)
    
    # Python Version
    print(f"🐍 Python: {sys.version}")
    
    # Dependencies
    dependencies = [
        ("PyMuPDF", "fitz"),
        ("OpenAI", "openai"),
        ("Pillow", "PIL"),
        ("LibreOffice", None)  # Command-line tool
    ]
    
    for name, module in dependencies:
        if module:
            try:
                __import__(module)
                print(f"✅ {name}: Verfügbar")
            except ImportError:
                print(f"❌ {name}: Nicht verfügbar")
        else:
            # LibreOffice check
            import subprocess
            try:
                result = subprocess.run(['libreoffice', '--version'], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ {name}: Verfügbar")
                else:
                    print(f"❌ {name}: Nicht verfügbar")
            except:
                print(f"❌ {name}: Nicht verfügbar")
    
    # Environment
    openai_key = os.getenv('OPENAI_API_KEY')
    print(f"🔑 OpenAI API Key: {'✅ Gesetzt' if openai_key else '❌ Fehlt'}")
    print()

def main():
    """Hauptfunktion"""
    print("🎯 DOCUMENT-TO-IMAGE VISION SYSTEM")
    print("Revolutionäre Lösung für komplexe QM-Dokumente")
    print("=" * 70)
    print()
    
    # System Check
    print_system_info()
    
    # Run Test
    success = test_document_vision_comprehensive()
    
    print()
    print("=" * 70)
    if success:
        print("🎉 TEST ERFOLGREICH: Document Vision System funktioniert!")
        print("🚀 Bereit für PA 8.2.1 und komplexe Flussdiagramme")
    else:
        print("❌ TEST FEHLGESCHLAGEN: Verbesserungen erforderlich")
        print("🔧 Siehe Empfehlungen oben für Lösungsansätze")
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 