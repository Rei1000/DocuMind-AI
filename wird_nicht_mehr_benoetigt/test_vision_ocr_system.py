#!/usr/bin/env python3
"""
Test Vision OCR System für KI-QMS
=================================

Testet die neue Vision OCR Engine mit:
- GPT-4o Vision API Integration
- Flussdiagramm-Analyse
- Automatische Prozess-Referenz-Erkennung
- Compliance-Checking

Führt Tests mit dem problematischen PA 8.2.1 Dokument durch.
"""

import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.append('backend')

async def test_vision_ocr_system():
    """Test das Vision OCR System"""
    
    print("🧪 Vision OCR System Test")
    print("=" * 50)
    
    try:
        from app.vision_ocr_engine import VisionOCREngine, extract_text_with_vision
        from app.text_extraction import extract_text_from_file
        
        print("✅ Vision OCR Module erfolgreich importiert")
        
        # Test-Dokument
        test_file = Path("backend/uploads/test_documents/PA 8.2.1 [03] - Behandlung von Reparaturen.docx")
        
        if not test_file.exists():
            print(f"❌ Test-Dokument nicht gefunden: {test_file}")
            return
        
        print(f"📄 Test-Dokument: {test_file.name}")
        print()
        
        # Test 1: Standard Textextraktion
        print("🔍 Test 1: Standard Textextraktion")
        print("-" * 30)
        
        standard_text = extract_text_from_file(test_file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        print(f"📊 Standard-Extraktion: {len(standard_text)} Zeichen")
        print(f"📝 Inhalt: {standard_text[:200]}...")
        print()
        
        # Test 2: Vision OCR Engine
        print("🔍 Test 2: Vision OCR Engine")
        print("-" * 30)
        
        vision_engine = VisionOCREngine()
        
        if not vision_engine.api_key:
            print("⚠️ OpenAI API Key nicht gefunden - Vision OCR Test übersprungen")
            print("💡 Setze OPENAI_API_KEY Environment Variable für vollständigen Test")
            return
        
        # Simuliere Bildextraktion (normalerweise aus Enhanced OCR)
        print("📸 Simuliere Bildextraktion aus Word-Dokument...")
        
        # In echter Anwendung würden hier echte Bilder aus dem Dokument extrahiert
        extracted_images = []  # Placeholder
        
        print(f"📊 {len(extracted_images)} Bilder für Vision-Analyse gefunden")
        
        if extracted_images:
            vision_result = await vision_engine.analyze_document_with_vision(
                test_file, extracted_images
            )
            
            print("🎯 Vision-Analyse Ergebnisse:")
            print(f"   Success: {vision_result['success']}")
            print(f"   Bilder verarbeitet: {vision_result.get('total_images_processed', 0)}")
            print(f"   Prozess-Referenzen: {vision_result.get('process_references_found', [])}")
            print(f"   Compliance-Warnungen: {len(vision_result.get('compliance_warnings', []))}")
            
            if vision_result.get('compliance_warnings'):
                print("\n⚠️ Compliance-Warnungen:")
                for warning in vision_result['compliance_warnings']:
                    print(f"   - {warning['message']}")
        else:
            print("ℹ️ Keine Bilder für Vision-Analyse verfügbar")
        
        print()
        
        # Test 3: Kombinierte Vision + Enhanced OCR
        print("🔍 Test 3: Kombinierte Vision + Enhanced OCR")
        print("-" * 40)
        
        try:
            combined_result = await extract_text_with_vision(test_file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            
            print("🎯 Kombinierte Extraktion Ergebnisse:")
            print(f"   Success: {combined_result['success']}")
            print(f"   Text-Länge: {len(combined_result.get('text', ''))} Zeichen")
            print(f"   Methode: {combined_result.get('methodology', 'unknown')}")
            
            if combined_result.get('process_references'):
                print(f"   📎 Gefundene Referenzen: {combined_result['process_references']}")
            
            if combined_result.get('compliance_warnings'):
                print(f"   ⚠️ Compliance-Warnungen: {len(combined_result['compliance_warnings'])}")
                for warning in combined_result['compliance_warnings']:
                    print(f"      - {warning['message']}")
            
        except Exception as e:
            print(f"❌ Kombinierter Test fehlgeschlagen: {e}")
        
        print()
        
        # Test 4: Prozess-Referenz-Erkennung
        print("🔍 Test 4: Prozess-Referenz-Erkennung")
        print("-" * 35)
        
        test_text = """
        Nach Abschluss der Reparatur muss PA 8.5 durchgeführt werden.
        Siehe auch VA 4.2 für Validierungsverfahren.
        Entspricht ISO 13485 Abschnitt 8.2.1.
        Bei Problemen MDR Artikel 95 beachten.
        """
        
        # Teste auch manuelle Regex  
        import re
        manual_pattern = r'\b(PA|VA|QMA|SOP|WI)\s+\d+(?:\.\d+)*\b'
        manual_matches = re.findall(manual_pattern, test_text, re.IGNORECASE)
        print(f"🔍 Manual Regex Test: {manual_matches}")
        
        full_pattern = r'\b(PA|VA|QMA|SOP|WI)\s+(\d+(?:\.\d+)*)\b'
        full_matches = re.findall(full_pattern, test_text, re.IGNORECASE)
        print(f"🔍 Full Pattern Matches: {full_matches}")
        
        # Bessere Extraktion
        better_references = []
        for match in full_matches:
            reference = f"{match[0]} {match[1]}"
            better_references.append(reference)
        print(f"🔍 Better References: {better_references}")
        
        references = vision_engine._extract_references_regex(test_text)
        print(f"📝 Test-Text: {test_text.strip()}")
        print(f"📎 Gefundene Referenzen: {references}")
        
        # Prüfe Referenzen
        warnings = await vision_engine._check_process_references(references)
        print(f"⚠️ Compliance-Warnungen: {len(warnings)}")
        for warning in warnings:
            print(f"   - {warning['reference']}: {warning['message']}")
        
        print()
        print("🎉 Vision OCR System Test abgeschlossen!")
        
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("💡 Installiere missing dependencies oder prüfe Backend-Setup")
    except Exception as e:
        print(f"❌ Test-Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_vision_ocr_system())