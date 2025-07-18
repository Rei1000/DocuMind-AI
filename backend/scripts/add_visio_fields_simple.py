#!/usr/bin/env python3
"""
Einfache SQLite-Migration für Visio-Upload-Felder
Ohne externe Abhängigkeiten - nur Standard-Python
"""

import sqlite3
import os
import shutil
from datetime import datetime

# Finde die SQLite-Datenbank
def find_database():
    # Mögliche Pfade für die SQLite-Datei
    possible_paths = [
        "../qms_mvp.db",  # Gefundene Datenbank
        "../ki_qms.db",
        "../app/ki_qms.db",
        "../../ki_qms.db",
        "../database.db",
        "../app/database.db",
        "../../database.db"
    ]
    
    for path in possible_paths:
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), path))
        if os.path.exists(abs_path):
            print(f"✅ Datenbank gefunden: {abs_path}")
            return abs_path
    
    # Wenn nicht gefunden, frage nach dem Pfad
    print("❌ SQLite-Datenbank nicht automatisch gefunden.")
    print("Bitte geben Sie den Pfad zur SQLite-Datei an:")
    db_path = input("Pfad: ").strip()
    
    if os.path.exists(db_path):
        return os.path.abspath(db_path)
    else:
        raise FileNotFoundError(f"Datenbank nicht gefunden: {db_path}")

# Erstelle Backup
def create_backup(db_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup erstellt: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Backup fehlgeschlagen: {e}")
        raise

# Hauptfunktion
def migrate():
    print("🚀 SQLite Visio-Upload Migration")
    print("=" * 50)
    
    # Finde Datenbank
    db_path = find_database()
    
    # Erstelle Backup
    backup_path = create_backup(db_path)
    
    # Verbinde zur Datenbank
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Prüfe SQLite-Version
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        print(f"📊 SQLite Version: {version}")
        
        # Hole existierende Spalten
        cursor.execute("PRAGMA table_info(documents)")
        existing_columns = {col[1] for col in cursor.fetchall()}
        print(f"📋 Existierende Spalten: {len(existing_columns)}")
        
        # Neue Spalten definieren
        new_columns = [
            ("upload_method", "TEXT DEFAULT 'ocr'"),
            ("validation_status", "TEXT DEFAULT 'PENDING'"),
            ("structured_analysis", "TEXT"),
            ("processing_state", "TEXT DEFAULT 'UPLOADED'"),
            ("vision_results", "TEXT"),
            ("used_prompts", "TEXT"),
            ("qm_release_at", "TEXT"),
            ("qm_release_by_id", "INTEGER")
        ]
        
        # Füge fehlende Spalten hinzu
        added_count = 0
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE documents ADD COLUMN {column_name} {column_def}"
                    cursor.execute(sql)
                    print(f"✅ Spalte '{column_name}' hinzugefügt")
                    added_count += 1
                except Exception as e:
                    print(f"❌ Fehler bei Spalte '{column_name}': {e}")
                    raise
            else:
                print(f"⏭️  Spalte '{column_name}' existiert bereits")
        
        # Commit der Änderungen
        conn.commit()
        
        # Zeige finale Struktur
        cursor.execute("PRAGMA table_info(documents)")
        final_columns = cursor.fetchall()
        
        print(f"\n✅ Migration abgeschlossen!")
        print(f"📊 {added_count} neue Spalten hinzugefügt")
        print(f"📋 Spalten gesamt: {len(final_columns)}")
        
        # Zeige neue Spalten
        print("\n✨ Neue Visio-Upload-Spalten:")
        for col in final_columns:
            if col[1] in [nc[0] for nc in new_columns]:
                print(f"  - {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"\n❌ Migration fehlgeschlagen: {e}")
        print(f"💾 Backup verfügbar: {backup_path}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        migrate()
        print("\n🎉 Migration erfolgreich abgeschlossen!")
        print("📝 Sie können jetzt Visio-Uploads verwenden:")
        print("  - Upload mit Methode 'Visio' im Frontend")
        print("  - Schrittweise Verarbeitung mit Vorschau")
        print("  - QM-konforme Validierung und Freigabe")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        exit(1)