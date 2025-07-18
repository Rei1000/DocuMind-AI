#!/usr/bin/env python3
"""
Migration: Füge Upload-Methoden-Felder zur documents-Tabelle hinzu

Neue Felder:
- upload_method: Enum('ocr', 'visio') - Standard 'ocr'
- validation_status: String - Validierungsstatus für Visio
- structured_analysis: JSON/Text - Strukturierte Analyse-Daten
- prompt_used: Text - Verwendeter Prompt bei Visio-Methode
- ocr_text_preview: Text - OCR-Text-Vorschau

Autor: KI-QMS System
Datum: 2024
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, Column, String, Text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError
import logging
from datetime import datetime

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Datenbank-URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://qms_user:securepassword123@localhost/qms_db")

def run_migration():
    """Führt die Migration aus, um neue Upload-Methoden-Felder hinzuzufügen"""
    
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.begin() as conn:
            logger.info("🔄 Starte Migration: Upload-Methoden-Felder")
            
            # Prüfe, ob die Felder bereits existieren
            inspector = inspect(engine)
            existing_columns = [col['name'] for col in inspector.get_columns('documents')]
            
            # 1. upload_method hinzufügen (Standard: 'ocr')
            if 'upload_method' not in existing_columns:
                logger.info("➕ Füge upload_method Feld hinzu...")
                conn.execute(text("""
                    ALTER TABLE documents 
                    ADD COLUMN upload_method VARCHAR(10) DEFAULT 'ocr'
                """))
                logger.info("✅ upload_method Feld hinzugefügt")
            else:
                logger.info("⏭️  upload_method existiert bereits")
            
            # 2. validation_status hinzufügen
            if 'validation_status' not in existing_columns:
                logger.info("➕ Füge validation_status Feld hinzu...")
                conn.execute(text("""
                    ALTER TABLE documents 
                    ADD COLUMN validation_status VARCHAR(50)
                """))

                logger.info("✅ validation_status Feld hinzugefügt")
            else:
                logger.info("⏭️  validation_status existiert bereits")
            
            # 3. structured_analysis hinzufügen (JSON als Text)
            if 'structured_analysis' not in existing_columns:
                logger.info("➕ Füge structured_analysis Feld hinzu...")
                conn.execute(text("""
                    ALTER TABLE documents 
                    ADD COLUMN structured_analysis TEXT
                """))

                logger.info("✅ structured_analysis Feld hinzugefügt")
            else:
                logger.info("⏭️  structured_analysis existiert bereits")
            
            # 4. prompt_used hinzufügen
            if 'prompt_used' not in existing_columns:
                logger.info("➕ Füge prompt_used Feld hinzu...")
                conn.execute(text("""
                    ALTER TABLE documents 
                    ADD COLUMN prompt_used TEXT
                """))

                logger.info("✅ prompt_used Feld hinzugefügt")
            else:
                logger.info("⏭️  prompt_used existiert bereits")
            
            # 5. ocr_text_preview hinzufügen
            if 'ocr_text_preview' not in existing_columns:
                logger.info("➕ Füge ocr_text_preview Feld hinzu...")
                conn.execute(text("""
                    ALTER TABLE documents 
                    ADD COLUMN ocr_text_preview TEXT
                """))

                logger.info("✅ ocr_text_preview Feld hinzugefügt")
            else:
                logger.info("⏭️  ocr_text_preview existiert bereits")
            
            # Update existing documents to have 'ocr' as default upload_method
            logger.info("🔄 Aktualisiere bestehende Dokumente...")
            conn.execute(text("""
                UPDATE documents 
                SET upload_method = 'ocr' 
                WHERE upload_method IS NULL
            """))
            
            logger.info("✅ Migration erfolgreich abgeschlossen!")
            
    except (OperationalError, ProgrammingError) as e:
        logger.error(f"❌ Datenbankfehler: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler: {e}")
        raise

if __name__ == "__main__":
    try:
        run_migration()
        logger.info("🎉 Alle Migrationen erfolgreich durchgeführt!")
    except Exception as e:
        logger.error(f"💥 Migration fehlgeschlagen: {e}")
        sys.exit(1)