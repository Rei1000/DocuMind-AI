#!/usr/bin/env python3
"""
Migrations-Skript: Norm-spezifische Felder zur documents Tabelle hinzufügen

Dieses Skript erweitert die documents Tabelle um die neuen Felder:
- compliance_status: Compliance-Status für Normen
- priority: Priorität (HOCH, MITTEL, NIEDRIG)
- scope: Anwendungsbereich/Relevanz

Autor: KI-QMS Team
Datum: 2025-06-18
"""

import sys
import os

# Aktuelles Verzeichnis zum Python-Pfad hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, SessionLocal
import logging

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Führt die Migration aus"""
    
    db = SessionLocal()
    try:
        logger.info("🚀 Starte Norm-Felder Migration (SQLite)...")
        
        # Erst prüfen welche Spalten bereits existieren
        logger.info("🔍 Prüfe existierende Spalten...")
        existing_columns = []
        try:
            result = db.execute(text("PRAGMA table_info(documents);"))
            columns = result.fetchall()
            existing_columns = [col[1] for col in columns]  # col[1] ist der column_name
            logger.info(f"   Existierende Spalten: {existing_columns}")
        except Exception as e:
            logger.error(f"   ❌ Fehler beim Prüfen der Spalten: {str(e)}")
            return False
        
        # Nur fehlende Spalten hinzufügen
        new_columns = [
            ("compliance_status", "ALTER TABLE documents ADD COLUMN compliance_status VARCHAR(50);"),
            ("priority", "ALTER TABLE documents ADD COLUMN priority VARCHAR(20);"),
            ("scope", "ALTER TABLE documents ADD COLUMN scope TEXT;")
        ]
        
        for col_name, query in new_columns:
            if col_name not in existing_columns:
                logger.info(f"   ➕ Füge Spalte '{col_name}' hinzu...")
                try:
                    db.execute(text(query))
                    db.commit()
                    logger.info(f"   ✅ Spalte '{col_name}' erfolgreich hinzugefügt")
                except Exception as e:
                    logger.error(f"   ❌ Fehler beim Hinzufügen von '{col_name}': {str(e)}")
                    db.rollback()
                    return False
            else:
                logger.info(f"   ⏭️ Spalte '{col_name}' existiert bereits")
        
        logger.info("✅ Norm-Felder Migration abgeschlossen!")
        
        # Finale Prüfung aller Spalten
        logger.info("🔍 Finale Spalten-Prüfung...")
        result = db.execute(text("PRAGMA table_info(documents);"))
        columns = result.fetchall()
        
        norm_columns = [col for col in columns if col[1] in ['compliance_status', 'priority', 'scope']]
        logger.info(f"   Gefundene neue Norm-Spalten: {len(norm_columns)}")
        for col in norm_columns:
            logger.info(f"   - {col[1]}: {col[2]} (not null: {col[3]})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration fehlgeschlagen: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("KI-QMS - Norm-Felder Migration")
    logger.info("=" * 60)
    
    success = run_migration()
    
    if success:
        logger.info("🎉 Migration erfolgreich abgeschlossen!")
        sys.exit(0)
    else:
        logger.error("💥 Migration fehlgeschlagen!")
        sys.exit(1) 