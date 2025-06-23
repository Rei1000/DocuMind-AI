#!/usr/bin/env python3
"""
Update User Group Memberships Table Migration Script
===================================================

Fügt fehlende Spalten zur user_group_memberships Tabelle hinzu:
- approval_level: INT (für granulare Freigabe-Level)

Hintergrund:
Das Backend-Modell UserGroupMembershipModel erwartet diese Spalten,
aber sie fehlen in der aktuellen Datenbank-Struktur.
"""

import sqlite3
import shutil
from datetime import datetime
import os
import sys

# Füge das Backend-Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def backup_database(db_path: str) -> str:
    """Erstellt ein Backup der Datenbank"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{db_path.replace('.db', '')}.backup_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup erstellt: {os.path.basename(backup_path)}")
    return backup_path

def column_exists(cursor, table_name: str, column_name: str) -> bool:
    """Prüft ob eine Spalte existiert"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns

def update_user_group_memberships():
    """Hauptfunktion für die Migration"""
    print("🚀 User Group Memberships Migration")
    print("=" * 50)
    
    # Datenbankpfad
    db_path = os.path.join(os.path.dirname(__file__), '..', 'qms_mvp.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    # Backup erstellen
    backup_path = backup_database(db_path)
    
    try:
        # Datenbankverbindung
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. approval_level Spalte hinzufügen
        if not column_exists(cursor, 'user_group_memberships', 'approval_level'):
            print("📝 Füge approval_level Spalte hinzu...")
            cursor.execute("""
                ALTER TABLE user_group_memberships 
                ADD COLUMN approval_level INTEGER DEFAULT 1
            """)
            print("✅ approval_level Spalte hinzugefügt")
        else:
            print("⏭️  Spalte existiert bereits: approval_level")
        
        # Migration erfolgreich
        conn.commit()
        print("\n📊 Migration erfolgreich!")
        
        # Statistiken anzeigen
        cursor.execute("SELECT COUNT(*) FROM user_group_memberships")
        total_memberships = cursor.fetchone()[0]
        print(f"   📊 {total_memberships} Gruppen-Zugehörigkeiten aktualisiert")
        
        cursor.execute("""
            SELECT ugm.approval_level, COUNT(*) 
            FROM user_group_memberships ugm 
            GROUP BY ugm.approval_level
        """)
        level_stats = cursor.fetchall()
        for level, count in level_stats:
            print(f"   • Level {level}: {count} Zugehörigkeiten")
        
        conn.close()
        
        print("\n🎉 Migration erfolgreich abgeschlossen!")
        print("📝 Neue Features verfügbar:")
        print("   • Granulare Freigabe-Level in Interessensgruppen")
        print("   • Verbesserte Workflow-Kontrolle")
        print("   • DSGVO-konforme Benutzerprofil-Anzeige")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Migration: {e}")
        print(f"🔄 Stelle Backup wieder her: {backup_path}")
        
        # Backup wiederherstellen
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, db_path)
            print("✅ Backup wiederhergestellt")
        
        return False

if __name__ == "__main__":
    success = update_user_group_memberships()
    sys.exit(0 if success else 1) 