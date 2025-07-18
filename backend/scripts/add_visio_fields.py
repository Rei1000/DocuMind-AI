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
    """Fügt neue Felder für Visio-Verarbeitung hinzu"""
    
    engine = create_engine(DATABASE_URL)
    
    # SQL-Befehle für neue Spalten
    alter_statements = [
        # Upload-Methode (ocr oder visio)
        """
        ALTER TABLE documents 
        ADD COLUMN upload_method VARCHAR(20) DEFAULT 'ocr'
        """,
        
        # Validierungsstatus
        """
        ALTER TABLE documents 
        ADD COLUMN validation_status VARCHAR(50) DEFAULT 'PENDING'
        """,
        
        # Strukturierte Analyse (JSON)
        """
        ALTER TABLE documents 
        ADD COLUMN structured_analysis TEXT
        """,
        
        # Verarbeitungszustand
        """
        ALTER TABLE documents 
        ADD COLUMN processing_state VARCHAR(50) DEFAULT 'UPLOADED'
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
        
        # QM-Freigabe-Zeitstempel
        """
        ALTER TABLE documents 
        ADD COLUMN qm_release_at TIMESTAMP
        """,
        
        # QM-Freigabe-Benutzer
        """
        ALTER TABLE documents 
        ADD COLUMN qm_release_by_id INTEGER REFERENCES users(id)
        """
    ]
    
    with engine.begin() as conn:
        for i, stmt in enumerate(alter_statements, 1):
            try:
                conn.execute(text(stmt))
                logger.info(f"✅ Statement {i}/8 erfolgreich ausgeführt")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info(f"ℹ️ Statement {i}/8: Spalte existiert bereits")
                else:
                    logger.error(f"❌ Statement {i}/8 fehlgeschlagen: {e}")
                    raise
    
    logger.info("✅ Migration abgeschlossen!")
    
    # Zeige aktuelle Struktur
    with engine.begin() as conn:
        result = conn.execute(text("PRAGMA table_info(documents)"))
        columns = result.fetchall()
        
        logger.info("\n📊 Aktuelle Dokumenten-Tabellen-Struktur:")
        for col in columns:
            logger.info(f"  - {col[1]} ({col[2]})")

if __name__ == "__main__":
    logger.info("🚀 Starte Visio-Felder Migration...")
    add_visio_fields()