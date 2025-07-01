#!/usr/bin/env python3
"""
Script to index existing uploaded files into the database.
Scans the uploads/ directory and creates database entries for all found files.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine
from app.models import Document, DocumentType, DocumentStatus
from sqlalchemy.orm import Session

def get_document_type_from_path(file_path):
    """Determine document type from file path."""
    path_parts = str(file_path).split(os.sep)
    
    if 'SOP' in path_parts:
        return DocumentType.SOP
    elif 'WORK_INSTRUCTION' in path_parts:
        return DocumentType.WORK_INSTRUCTION
    elif 'STANDARD_NORM' in path_parts:
        return DocumentType.STANDARD_NORM
    elif 'OTHER' in path_parts:
        return DocumentType.OTHER
    else:
        return DocumentType.OTHER

def extract_title_from_filename(filename):
    """Extract a readable title from filename."""
    # Remove extension
    title = Path(filename).stem
    
    # Replace underscores with spaces
    title = title.replace('_', ' ')
    
    # Limit length
    if len(title) > 100:
        title = title[:97] + "..."
    
    return title

def index_uploads_directory():
    """Scan uploads directory and add files to database."""
    uploads_path = Path(__file__).parent.parent / "uploads"
    
    if not uploads_path.exists():
        print("❌ Uploads-Verzeichnis nicht gefunden!")
        return
    
    db = SessionLocal()
    try:
        indexed_count = 0
        skipped_count = 0
        
        print(f"🔍 Scanne Verzeichnis: {uploads_path}")
        
        # Walk through all files in uploads directory
        for file_path in uploads_path.rglob("*"):
            if file_path.is_file():
                
                # Check if file already exists in database
                relative_path = str(file_path.relative_to(uploads_path.parent))
                existing = db.query(Document).filter(Document.file_path == relative_path).first()
                
                if existing:
                    print(f"⏭️  Überspringe (bereits indexiert): {file_path.name}")
                    skipped_count += 1
                    continue
                
                # Create database entry
                document_type = get_document_type_from_path(file_path)
                title = extract_title_from_filename(file_path.name)
                
                doc = Document(
                    title=title,
                    document_type=document_type,
                    document_number=f"AUTO_{file_path.stem}_{int(datetime.now().timestamp())}",  # Auto-generated number
                    file_path=relative_path,
                    creator_id=1,  # Default to user ID 1 (admin)
                    created_at=datetime.now(),
                    status=DocumentStatus.APPROVED  # Set to APPROVED so they show up
                )
                
                db.add(doc)
                
                print(f"✅ Indexiert: {title} ({document_type})")
                indexed_count += 1
        
        # Commit all changes
        db.commit()
        
        print(f"\n🎉 Indexierung abgeschlossen!")
        print(f"✅ {indexed_count} Dateien neu indexiert")
        print(f"⏭️  {skipped_count} Dateien übersprungen (bereits vorhanden)")
        
        # Show total count
        total_docs = db.query(Document).count()
        print(f"📊 Gesamt Dokumente in DB: {total_docs}")
        
    except Exception as e:
        print(f"❌ Fehler bei Indexierung: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starte Indexierung der Upload-Dateien...")
    index_uploads_directory() 