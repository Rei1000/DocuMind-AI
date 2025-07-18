#!/usr/bin/env python3
"""
Migration: Fügt Visio-Upload-Felder zur Datenbank hinzu

Neue Felder:
- upload_method: Art des Uploads (ocr/visio)
- validation_status: Validierungsstatus (PENDING/VERIFIED/REVIEW_REQUIRED)
- structured_analysis: JSON-strukturierte Analyse
- processing_state: Verarbeitungszustand für State Machine
- vision_results: Ergebnisse der Vision-API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.database import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_visio_fields():
    """Fügt neue Felder für Visio-Verarbeitung hinzu (SQLite-kompatibel)"""
    
    engine = create_engine(DATABASE_URL)
    
    # SQLite-kompatible ALTER TABLE Statements
    # Hinweis: SQLite unterstützt keine REFERENCES in ALTER TABLE ADD COLUMN
    alter_statements = [
        # Upload-Methode (ocr oder visio)
        """
        ALTER TABLE documents 
        ADD COLUMN upload_method TEXT DEFAULT 'ocr'
        """,
        
        # Validierungsstatus
        """
        ALTER TABLE documents 
        ADD COLUMN validation_status TEXT DEFAULT 'PENDING'
        """,
        
        # Strukturierte Analyse (JSON)
        """
        ALTER TABLE documents 
        ADD COLUMN structured_analysis TEXT
        """,
        
        # Verarbeitungszustand
        """
        ALTER TABLE documents 
        ADD COLUMN processing_state TEXT DEFAULT 'UPLOADED'
        """,
        
        # Vision-API Ergebnisse (JSON)
        """
        ALTER TABLE documents 
        ADD COLUMN vision_results TEXT
        """,
        
        # Verwendete Prompts für Nachvollziehbarkeit
        """
        ALTER TABLE documents 
        ADD COLUMN used_prompts TEXT
        """,
        
        # QM-Freigabe-Zeitstempel (SQLite speichert als TEXT)
        """
        ALTER TABLE documents 
        ADD COLUMN qm_release_at TEXT
        """,
        
        # QM-Freigabe-Benutzer (Foreign Key ohne REFERENCES für SQLite)
        """
        ALTER TABLE documents 
        ADD COLUMN qm_release_by_id INTEGER
        """
    ]
    
    # Prüfe ob es wirklich SQLite ist
    with engine.begin() as conn:
        # SQLite-Version prüfen
        result = conn.execute(text("SELECT sqlite_version()"))
        version = result.scalar()
        logger.info(f"📊 SQLite Version: {version}")
    
    # Führe Migrationen aus
    with engine.begin() as conn:
        # Zuerst prüfen welche Spalten bereits existieren
        result = conn.execute(text("PRAGMA table_info(documents)"))
        existing_columns = {col[1] for col in result.fetchall()}
        logger.info(f"📋 Existierende Spalten: {len(existing_columns)}")
        
        # Neue Spalten identifizieren
        new_columns = [
            'upload_method', 'validation_status', 'structured_analysis',
            'processing_state', 'vision_results', 'used_prompts',
            'qm_release_at', 'qm_release_by_id'
        ]
        
        columns_to_add = [col for col in new_columns if col not in existing_columns]
        
        if not columns_to_add:
            logger.info("✅ Alle Visio-Felder existieren bereits!")
        else:
            logger.info(f"📝 Füge {len(columns_to_add)} neue Spalten hinzu: {columns_to_add}")
        
        # Führe nur notwendige Statements aus
        for i, stmt in enumerate(alter_statements, 1):
            column_name = new_columns[i-1]
            if column_name in columns_to_add:
                try:
                    conn.execute(text(stmt))
                    logger.info(f"✅ Spalte '{column_name}' hinzugefügt")
                except Exception as e:
                    logger.error(f"❌ Fehler bei Spalte '{column_name}': {e}")
                    raise
            else:
                logger.info(f"⏭️ Spalte '{column_name}' übersprungen (existiert bereits)")
    
    logger.info("\n✅ Migration abgeschlossen!")
    
    # Zeige finale Struktur
    with engine.begin() as conn:
        result = conn.execute(text("PRAGMA table_info(documents)"))
        columns = result.fetchall()
        
        logger.info("\n📊 Finale Dokumenten-Tabellen-Struktur:")
        logger.info(f"Spalten gesamt: {len(columns)}")
        
        # Zeige nur die neuen Spalten
        for col in columns:
            if col[1] in new_columns:
                logger.info(f"  ✨ {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'} default: {col[4]}")

def backup_database():
    """Erstellt ein Backup der SQLite-Datenbank vor der Migration"""
    import shutil
    from datetime import datetime
    
    # Finde die SQLite-Datei
    db_path = None
    if "sqlite:///" in DATABASE_URL:
        # Extrahiere Dateipfad aus DATABASE_URL
        db_path = DATABASE_URL.replace("sqlite:///", "")
        if not os.path.isabs(db_path):
            # Relativer Pfad vom backend-Verzeichnis
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_path)
    
    if db_path and os.path.exists(db_path):
        # Erstelle Backup mit Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_{timestamp}"
        
        try:
            shutil.copy2(db_path, backup_path)
            logger.info(f"✅ Backup erstellt: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"❌ Backup fehlgeschlagen: {e}")
            raise
    else:
        logger.warning("⚠️ SQLite-Datei nicht gefunden - kein Backup erstellt")
        return None

if __name__ == "__main__":
    logger.info("🚀 Starte Visio-Felder Migration für SQLite...")
    
    # Erstelle Backup
    backup_path = backup_database()
    
    try:
        # Führe Migration aus
        add_visio_fields()
        logger.info("\n✨ Migration erfolgreich abgeschlossen!")
        logger.info("📝 Die folgenden Features sind jetzt verfügbar:")
        logger.info("  - Visio-Upload mit bildbasierter Dokumentverarbeitung")
        logger.info("  - Schrittweise Verarbeitung mit State Machine")
        logger.info("  - QM-konforme Validierung und Freigabe")
        
    except Exception as e:
        logger.error(f"\n❌ Migration fehlgeschlagen: {e}")
        if backup_path:
            logger.info(f"💾 Backup verfügbar unter: {backup_path}")
        raise