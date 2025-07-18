#!/usr/bin/env python3
"""
Migrationsskript: Fügt Visio-Upload-Felder zur documents-Tabelle hinzu

Dieses Skript fügt die notwendigen Felder für die Visio-Verarbeitung hinzu:
- upload_method (ocr/visio)
- processing_state (State Machine Status)
- validation_status 
- structured_analysis (JSON)
- vision_results (JSON)
- used_prompts (JSON)
- qm_release_at
- qm_release_by_id
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from datetime import datetime
import shutil

def backup_database(db_path):
    """Erstellt ein Backup der Datenbank vor der Migration"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"📦 Erstelle Backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    return backup_path

def add_visio_fields():
    """Fügt die Visio-Upload-Felder zur documents-Tabelle hinzu"""
    
    db_path = "qms_mvp.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank {db_path} nicht gefunden!")
        return False
    
    # Backup erstellen
    backup_path = backup_database(db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe existierende Spalten
        cursor.execute("PRAGMA table_info(documents)")
        existing_columns = {col[1] for col in cursor.fetchall()}
        
        print(f"📋 Gefundene Spalten: {len(existing_columns)}")
        
        # Definiere neue Spalten
        new_columns = [
            ("upload_method", "VARCHAR DEFAULT 'ocr'"),
            ("processing_state", "VARCHAR"),
            ("validation_status", "VARCHAR"),
            ("structured_analysis", "TEXT"),
            ("vision_results", "TEXT"),
            ("used_prompts", "TEXT"),
            ("qm_release_at", "DATETIME"),
            ("qm_release_by_id", "INTEGER REFERENCES users(id)")
        ]
        
        # Füge fehlende Spalten hinzu
        added_columns = []
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE documents ADD COLUMN {column_name} {column_def}"
                    cursor.execute(sql)
                    added_columns.append(column_name)
                    print(f"✅ Spalte '{column_name}' hinzugefügt")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"ℹ️ Spalte '{column_name}' existiert bereits")
                    else:
                        raise
            else:
                print(f"ℹ️ Spalte '{column_name}' existiert bereits")
        
        # Setze Default-Werte für existierende Dokumente
        if "upload_method" in added_columns:
            cursor.execute("UPDATE documents SET upload_method = 'ocr' WHERE upload_method IS NULL")
            print("✅ Standard upload_method='ocr' für existierende Dokumente gesetzt")
        
        # Commit der Änderungen
        conn.commit()
        
        # Verifikation
        cursor.execute("PRAGMA table_info(documents)")
        final_columns = {col[1] for col in cursor.fetchall()}
        
        # Prüfe ob alle Spalten vorhanden sind
        all_present = all(col[0] in final_columns for col in new_columns)
        
        if all_present:
            print(f"\n✅ Migration erfolgreich! Alle {len(new_columns)} Visio-Felder sind vorhanden.")
            if added_columns:
                print(f"   Neu hinzugefügt: {', '.join(added_columns)}")
        else:
            print("\n❌ Nicht alle Felder konnten hinzugefügt werden!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Fehler bei der Migration: {e}")
        print(f"💾 Backup verfügbar unter: {backup_path}")
        return False

if __name__ == "__main__":
    print("🚀 Starte Visio-Upload Felder Migration...")
    print("-" * 50)
    
    success = add_visio_fields()
    
    if success:
        print("\n✨ Migration abgeschlossen!")
    else:
        print("\n❌ Migration fehlgeschlagen!")
        sys.exit(1)