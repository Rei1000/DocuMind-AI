#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 COMPREHENSIVE VISION SYSTEM TEST - Enhanced Compliance Edition
Test Document-to-Image Vision OCR with Intelligent Compliance Analysis

Target: Multiple QM Documents Analysis with >1000 characters + Compliance Validation
"""
import os
import sys
import asyncio
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

async def test_enhanced_compliance_vision():
    """🎯 Test enhanced vision system with compliance validation"""
    
    print("🔥 ENHANCED COMPLIANCE VISION SYSTEM TEST")
    print("=" * 80)
    
    try:
        from app.document_vision_engine import extract_text_with_document_vision
        
        # Test files - verschiedene QM-Dokumenttypen
        test_files = [
            "backend/uploads/test_documents/PA 8.2.1 [03] - Behandlung von Reparaturen.docx",
            "backend/uploads/test_documents/FB 4.2 [04] - Änderungsantrag.docx", 
            "backend/uploads/test_documents/PA 7.3 [00] 260816 - Entwicklung, Produktionsunterlagen.docx",
            "backend/uploads/test_documents/PA 7.6 [00] 070616 - Prüfmittelüberwachung.docx",
            "backend/uploads/test_documents/Kapitel 8 [02] 170718 - Messung, Analyse, Verbesserung.docx",
            "uploads/PA 8.2.1 [03] - Behandlung von Reparaturen.docx"  # Backup location
        ]
        
        print(f"📋 Teste {len(test_files)} verschiedene QM-Dokumente...")
        print()
        
        total_success = 0
        total_files = 0
        results_summary = []
        
        for file_path in test_files:
            if not os.path.exists(file_path):
                print(f"⚠️ Datei nicht gefunden: {file_path}")
                continue
                
            total_files += 1
            file_name = os.path.basename(file_path)
            
            print(f"🔍 TESTE: {file_name}")
            print("-" * 60)
            
            try:
                # Enhanced Vision OCR Test
                result = await extract_text_with_document_vision(file_path)
                
                # Analyse der Ergebnisse
                if result and result.get("success"):
                    characters = result.get("total_characters", 0)
                    references = result.get("process_references", [])
                    compliance = result.get("compliance_analysis", {})
                    
                    success_rate = result.get("success_metrics", {}).get("success_rate", 0)
                    quality_score = result.get("success_metrics", {}).get("quality_score", 0)
                    
                    print(f"✅ ERFOLG: {characters} Zeichen extrahiert")
                    print(f"📊 Success Rate: {success_rate:.1f}%")
                    print(f"⭐ Quality Score: {quality_score}/100")
                    print(f"🔗 Process References: {len(references)}")
                    
                    if references:
                        print(f"   → {', '.join(references)}")
                    
                    # Compliance Analysis
                    if compliance:
                        compliance_score = compliance.get("compliance_score", 0)
                        missing_docs = compliance.get("missing_documents", [])
                        recommendations = compliance.get("recommendations", [])
                        
                        print(f"⚖️ Compliance Score: {compliance_score}/100")
                        if missing_docs:
                            print(f"⚠️ Fehlende Dokumente: {', '.join(missing_docs)}")
                        if recommendations:
                            print(f"💡 Empfehlungen: {len(recommendations)} verfügbar")
                    
                    # Workflow Readiness
                    workflow_ready = compliance.get("workflow_ready", False)
                    print(f"🚀 Workflow Ready: {'JA' if workflow_ready else 'NEIN'}")
                    
                    if characters >= 1000:
                        total_success += 1
                        print(f"🎉 TARGET ERREICHT: >1000 Zeichen!")
                    else:
                        print(f"📈 Fortschritt: {characters}/1000 Zeichen ({(characters/1000)*100:.1f}%)")
                    
                    results_summary.append({
                        "file": file_name,
                        "success": True,
                        "characters": characters,
                        "references": len(references),
                        "compliance_score": compliance.get("compliance_score", 0),
                        "workflow_ready": workflow_ready
                    })
                    
                else:
                    print("❌ FEHLER: Vision OCR fehlgeschlagen")
                    print(f"   Grund: {result.get('error', 'Unbekannter Fehler')}")
                    results_summary.append({
                        "file": file_name,
                        "success": False,
                        "error": result.get("error", "Vision OCR Error")
                    })
                
            except Exception as e:
                print(f"❌ EXCEPTION: {str(e)}")
                results_summary.append({
                    "file": file_name,
                    "success": False,
                    "error": str(e)
                })
            
            print()
            
            # Rate limit friendly delay between documents
            if total_files < len([f for f in test_files if os.path.exists(f)]):
                print("⏳ Kurze Pause zur Rate-Limit-Vermeidung...")
                await asyncio.sleep(15)  # 15 second delay between documents
        
        # Zusammenfassung
        print("=" * 80)
        print("📊 ENHANCED COMPLIANCE VISION TEST - ZUSAMMENFASSUNG")
        print("=" * 80)
        print(f"📋 Getestete Dateien: {total_files}")
        print(f"✅ Erfolgreich (>1000 Zeichen): {total_success}")
        print(f"📈 Erfolgsquote: {(total_success/total_files)*100:.1f}%" if total_files > 0 else "📈 Erfolgsquote: 0%")
        print()
        
        # Detaillierte Ergebnisse
        for result in results_summary:
            if result["success"]:
                print(f"✅ {result['file']}")
                print(f"   📊 {result['characters']} Zeichen | {result['references']} Referenzen")
                print(f"   ⚖️ Compliance: {result['compliance_score']}/100 | Workflow: {'✅' if result['workflow_ready'] else '❌'}")
            else:
                print(f"❌ {result['file']}: {result['error']}")
            print()
        
        # Finale Bewertung
        if total_success == total_files and total_files > 0:
            print("🎉 ALLE TESTS ERFOLGREICH!")
            print("🚀 Enhanced Compliance Vision System ist PRODUKTIONSBEREIT!")
        elif total_success > 0:
            print(f"🎯 TEILWEISE ERFOLGREICH: {total_success}/{total_files}")
            print("🔧 System benötigt weitere Optimierung")
        else:
            print("❌ Enhanced Vision System Test FAILED!")
            print("🔧 System benötigt Debugging")
        
    except Exception as e:
        print(f"❌ KRITISCHER FEHLER: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🏥 KI-QMS Enhanced Compliance Vision System")
    print("🎯 Document Analysis with Intelligent Compliance Validation")
    print()
    
    asyncio.run(test_enhanced_compliance_vision()) 