#!/usr/bin/env python3
"""
Migrationsskript: RAG-System und intelligente Workflow-Tabellen

Fügt die neuen Tabellen für das RAG-System und die intelligente
Workflow-Engine hinzu:
- DocumentIndex: Für Embeddings und semantische Suche
- RAGQuery: Für RAG-Query-Historie
- QMSTask: Für intelligente Workflow-Tasks  
- TaskComment: Für Task-Kommentare
- WorkflowTemplate: Für wiederverwendbare Workflows
- WorkflowExecution: Für Workflow-Ausführungsprotokoll

Ausführung:
    python backend/scripts/add_rag_workflow_tables.py
"""

import sys
import os
from pathlib import Path

# Backend-Pfad hinzufügen
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text
from app.database import get_db, engine
from app.models import Base

def add_rag_workflow_tables():
    """Fügt RAG- und Workflow-Tabellen hinzu"""
    print("🔄 Starte Migration: RAG-System und intelligente Workflows")
    print("📊 Datenbank: qms_mvp.db")
    
    try:
        # Alle Tabellen erstellen (neue werden hinzugefügt, bestehende ignoriert)
        Base.metadata.create_all(bind=engine)
        
        print("✅ Migration erfolgreich abgeschlossen!")
        print("\n📋 Neue Tabellen:")
        
        # Prüfe, welche Tabellen existieren
        with engine.connect() as conn:
            # RAG-Tabellen
            print("🧠 RAG-System:")
            
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM document_indexes"))
                count = result.scalar()
                print(f"  ✅ document_indexes ({count} Einträge)")
            except:
                print("  ❌ document_indexes (nicht erstellt)")
            
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM rag_queries"))
                count = result.scalar()
                print(f"  ✅ rag_queries ({count} Einträge)")
            except:
                print("  ❌ rag_queries (nicht erstellt)")
            
            # Workflow-Tabellen
            print("\n🚀 Intelligente Workflows:")
            
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM qms_tasks"))
                count = result.scalar()
                print(f"  ✅ qms_tasks ({count} Einträge)")
            except:
                print("  ❌ qms_tasks (nicht erstellt)")
            
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM task_comments"))
                count = result.scalar()
                print(f"  ✅ task_comments ({count} Einträge)")
            except:
                print("  ❌ task_comments (nicht erstellt)")
            
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM workflow_templates"))
                count = result.scalar()
                print(f"  ✅ workflow_templates ({count} Einträge)")
            except:
                print("  ❌ workflow_templates (nicht erstellt)")
            
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM workflow_executions"))
                count = result.scalar()
                print(f"  ✅ workflow_executions ({count} Einträge)")
            except:
                print("  ❌ workflow_executions (nicht erstellt)")
        
        print("\n🎉 Das KI-QMS ist jetzt bereit für RAG-Chat und intelligente Workflows!")
        print("\n📋 Nächste Schritte:")
        print("1. Backend neustarten: ./restart_backend.sh")
        print("2. Dokumente indexieren: http://localhost:8501 → RAG-Chat → 'Alle Dokumente indexieren'")
        print("3. Ersten Workflow testen: 'Bluetooth Modul nicht mehr lieferbar'")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    success = add_rag_workflow_tables()
    sys.exit(0 if success else 1) 