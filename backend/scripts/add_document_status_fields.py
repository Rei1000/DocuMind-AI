#!/usr/bin/env python3
"""
Database Migration: Document Status Workflow Fields
===================================================

Fügt die neuen Felder für das Document Status Workflow System hinzu:
1. Document Model: status_changed_by_id, status_changed_at, status_comment
2. DocumentStatusHistory Tabelle für Audit-Trail

Sicherheit: Erstellt Backup vor Migration
"""

import sys
import os
import shutil
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine
from app.models import Base
import sqlite3

def create_backup():
    """Erstellt Backup der aktuellen Datenbank"""
    db_path = Path("qms_mvp.db")
    if db_path.exists():
        backup_path = db_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup erstellt: {backup_path}")
        return backup_path
    return None

def add_document_status_fields():
    """Fügt neue Status-Felder zur documents Tabelle hinzu"""
    conn = sqlite3.connect("qms_mvp.db")
    cursor = conn.cursor()
    
    try:
        # Prüfe welche Felder bereits existieren
        cursor.execute("PRAGMA table_info(documents)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        new_columns = [
            ("status_changed_by_id", "INTEGER"),
            ("status_changed_at", "DATETIME"),
            ("status_comment", "TEXT")
        ]
        
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                print(f"📝 Füge Spalte hinzu: {column_name}")
                cursor.execute(f"ALTER TABLE documents ADD COLUMN {column_name} {column_def}")
            else:
                print(f"⏭️  Spalte existiert bereits: {column_name}")
        
        conn.commit()
        print("✅ Document Status-Felder hinzugefügt")
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Fehler beim Hinzufügen der Document-Felder: {e}")
    finally:
        conn.close()

def create_status_history_table():
    """Erstellt DocumentStatusHistory Tabelle"""
    conn = sqlite3.connect("qms_mvp.db")
    cursor = conn.cursor()
    
    try:
        # Prüfe ob Tabelle bereits existiert
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='document_status_history'")
        if cursor.fetchone():
            print("⏭️  DocumentStatusHistory Tabelle existiert bereits")
            return
        
        # Tabelle erstellen
        create_table_sql = """
        CREATE TABLE document_status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL REFERENCES documents(id),
            old_status VARCHAR(20),
            new_status VARCHAR(20) NOT NULL,
            changed_by_id INTEGER NOT NULL REFERENCES users(id),
            changed_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            comment TEXT
        )
        """
        
        cursor.execute(create_table_sql)
        
        # Indices erstellen für Performance
        cursor.execute("CREATE INDEX idx_document_status_history_document_id ON document_status_history(document_id)")
        cursor.execute("CREATE INDEX idx_document_status_history_changed_at ON document_status_history(changed_at)")
        
        conn.commit()
        print("✅ DocumentStatusHistory Tabelle erstellt")
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Fehler beim Erstellen der Status-History-Tabelle: {e}")
    finally:
        conn.close()

def update_document_status_enum():
    """Aktualisiert bestehende 'review' Status zu 'reviewed'"""
    conn = sqlite3.connect("qms_mvp.db")
    cursor = conn.cursor()
    
    try:
        # Prüfe aktuelle Status-Werte
        cursor.execute("SELECT DISTINCT status FROM documents WHERE status IS NOT NULL")
        current_statuses = [row[0] for row in cursor.fetchall()]
        print(f"🔍 Aktuelle Status-Werte: {current_statuses}")
        
        # Update 'review' zu 'reviewed' falls vorhanden
        if 'review' in current_statuses:
            cursor.execute("UPDATE documents SET status = 'reviewed' WHERE status = 'review'")
            updated_count = cursor.rowcount
            print(f"📝 {updated_count} Dokument(e) von 'review' zu 'reviewed' aktualisiert")
        
        conn.commit()
        print("✅ Status-Enum aktualisiert")
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Fehler beim Aktualisieren der Status-Enum: {e}")
    finally:
        conn.close()

def initialize_status_fields():
    """Initialisiert neue Status-Felder mit Default-Werten"""
    conn = sqlite3.connect("qms_mvp.db")
    cursor = conn.cursor()
    
    try:
        # Setze status_changed_at auf created_at wo NULL
        cursor.execute("""
            UPDATE documents 
            SET status_changed_at = created_at 
            WHERE status_changed_at IS NULL
        """)
        
        # Setze status_changed_by_id auf creator_id wo NULL
        cursor.execute("""
            UPDATE documents 
            SET status_changed_by_id = creator_id 
            WHERE status_changed_by_id IS NULL AND creator_id IS NOT NULL
        """)
        
        updated_count = cursor.rowcount
        conn.commit()
        print(f"✅ {updated_count} Dokument(e) mit Default-Status-Werten initialisiert")
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Fehler beim Initialisieren der Status-Felder: {e}")
    finally:
        conn.close()

def verify_migration():
    """Verifiziert die Migration"""
    conn = sqlite3.connect("qms_mvp.db")
    cursor = conn.cursor()
    
    try:
        # Prüfe Document-Felder
        cursor.execute("PRAGMA table_info(documents)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_fields = ["status_changed_by_id", "status_changed_at", "status_comment"]
        missing_fields = [f for f in required_fields if f not in columns]
        
        if missing_fields:
            print(f"❌ Fehlende Document-Felder: {missing_fields}")
            return False
        
        # Prüfe Status-History Tabelle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='document_status_history'")
        if not cursor.fetchone():
            print("❌ DocumentStatusHistory Tabelle fehlt")
            return False
        
        # Prüfe Dokument-Count
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents WHERE status_changed_by_id IS NOT NULL")
        initialized_count = cursor.fetchone()[0]
        
        print(f"📊 Migration erfolgreich!")
        print(f"   📁 {doc_count} Dokumente total")
        print(f"   ✅ {initialized_count} Dokumente mit Status-Tracking")
        
        return True
        
    except Exception as e:
        print(f"❌ Verifikation fehlgeschlagen: {e}")
        return False
    finally:
        conn.close()

def main():
    print("🚀 Document Status Workflow Migration")
    print("=" * 50)
    
    try:
        # 1. Backup erstellen
        backup_path = create_backup()
        
        # 2. Document Status-Felder hinzufügen
        add_document_status_fields()
        
        # 3. Status-History Tabelle erstellen
        create_status_history_table()
        
        # 4. Status-Enum aktualisieren
        update_document_status_enum()
        
        # 5. Status-Felder initialisieren
        initialize_status_fields()
        
        # 6. Migration verifizieren
        if verify_migration():
            print("\n🎉 Migration erfolgreich abgeschlossen!")
            print("📝 Neue Features verfügbar:")
            print("   • PUT /api/documents/{id}/status - Status ändern")
            print("   • GET /api/documents/{id}/status-history - Audit-Trail")
            print("   • GET /api/documents/status/{status} - Status-Filter")
        else:
            print("\n❌ Migration fehlgeschlagen - prüfe Logs")
            if backup_path:
                print(f"💾 Restore mit: cp {backup_path} qms_mvp.db")
            
    except Exception as e:
        print(f"\n💥 Migration ERROR: {e}")
        if backup_path:
            print(f"💾 Restore mit: cp {backup_path} qms_mvp.db")
        sys.exit(1)

if __name__ == "__main__":
    main() 