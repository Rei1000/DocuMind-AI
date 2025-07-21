"""
AI-Enhanced Upload Endpoints für KI-QMS
Separate Datei für AI-Features zur besseren Modularität.
"""

from fastapi import HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime
import logging

from .database import get_db
from .auth import get_current_active_user
from .models import User as UserModel
from .text_extraction import extract_text_from_file
from .ai_metadata_extractor import extract_document_metadata

logger = logging.getLogger("KI-QMS.AIEndpoints")

# Import RAG Engine
try:
    from .qdrant_rag_engine import qdrant_rag_engine
    RAG_AVAILABLE = True
except Exception as e:
    logger.warning(f"Qdrant RAG Engine nicht verfügbar: {e}")
    RAG_AVAILABLE = False

async def extract_metadata_endpoint(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Extrahiert Metadaten aus einem Dokument mit AI (ohne Upload)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")
    
    try:
        # Temporäre Datei erstellen
        file_content = await file.read()
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        safe_filename = file.filename or "unknown_file"
        temp_file_path = temp_dir / f"temp_{safe_filename}"
        
        with open(temp_file_path, "wb") as buffer:
            buffer.write(file_content)
        
        logger.info(f"Temporäre Datei erstellt: {temp_file_path}")
        
        # Text extrahieren
        extracted_text = ""
        try:
            extracted_text = extract_text_from_file(str(temp_file_path), file.content_type or "application/octet-stream")
            logger.info(f"Text extrahiert: {len(extracted_text)} Zeichen")
        except Exception as e:
            logger.warning(f"Text-Extraktion fehlgeschlagen: {e}")
            # Cleanup
            try:
                temp_file_path.unlink()
            except Exception:
                pass
            raise HTTPException(status_code=400, detail=f"Text-Extraktion fehlgeschlagen: {e}")
        
        # AI-Metadaten extrahieren
        if extracted_text:
            logger.info("🤖 Starte AI-Metadaten-Extraktion...")
            try:
                ai_metadata = await extract_document_metadata(extracted_text, file.filename)
                logger.info(f"✅ AI-Metadaten extrahiert: {ai_metadata.get('processing_status')}")
            except Exception as e:
                logger.warning(f"AI-Metadaten-Extraktion fehlgeschlagen: {e}")
                ai_metadata = {
                    "title": file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename,
                    "description": f"Automatische Analyse fehlgeschlagen: {e}",
                    "document_type": "OTHER",
                    "processing_status": "error",
                    "error": str(e)
                }
        else:
            ai_metadata = {
                "title": file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename,
                "description": "Kein Text zur Analyse verfügbar.",
                "document_type": "OTHER",
                "processing_status": "no_text"
            }
        
        # Temporäre Datei löschen
        try:
            temp_file_path.unlink()
        except Exception:
            pass
        
        return {
            "success": True,
            "filename": file.filename,
            "file_size": len(file_content),
            "extracted_text_length": len(extracted_text),
            "ai_metadata": ai_metadata
        }
        
    except Exception as e:
        logger.error(f"Metadaten-Extraktion fehlgeschlagen: {e}")
        # Cleanup
        try:
            if 'temp_file_path' in locals():
                temp_file_path.unlink()
        except Exception:
            pass
        
        raise HTTPException(status_code=500, detail=f"Metadaten-Extraktion fehlgeschlagen: {e}")


# ENTFERNT: Veraltete upload_document_with_ai Funktion - wird durch /api/documents/with-file ersetzt


async def chat_with_documents_endpoint(
    request: dict,
    current_user: UserModel = Depends(get_current_active_user)
):
    """Chat mit Dokumenten über Qdrant RAG"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")
    
    if not RAG_AVAILABLE:
        raise HTTPException(status_code=503, detail="RAG Engine nicht verfügbar")
    
    try:
        question = request.get("question", "")
        max_docs = request.get("max_docs", 3)
        
        if not question.strip():
            raise HTTPException(status_code=400, detail="Frage darf nicht leer sein")
        
        logger.info(f"💬 Chat-Anfrage von {current_user.email}: {question}")
        
        # Chat mit Qdrant RAG Engine
        chat_result = await qdrant_rag_engine.chat_with_documents(question, max_docs)
        
        return {
            "success": chat_result.get("success", False),
            "question": question,
            "answer": chat_result.get("answer", "Keine Antwort generiert"),
            "sources": chat_result.get("sources", []),
            "context_used": chat_result.get("context_used", 0),
            "user": current_user.email
        }
        
    except Exception as e:
        logger.error(f"Chat fehlgeschlagen: {e}")
        raise HTTPException(status_code=500, detail=f"Chat fehlgeschlagen: {e}")


async def get_rag_stats(current_user=None):
    """RAG System Statistiken"""
    try:
        if RAG_AVAILABLE:
            stats = await qdrant_rag_engine.get_system_stats()
            
            # Echte Dokumentenanzahl aus SQL-Database
            from .database import get_db
            from .models import Document as DocumentModel
            db = next(get_db())
            real_document_count = db.query(DocumentModel).count()
            db.close()
            
            # Strukturiere die Antwort für das Frontend
            return {
                "success": True,
                "status": stats.get("status", "unknown"),
                "total_documents": real_document_count,  # Echte SQL-Dokumente
                "total_chunks": stats.get("document_count", 0),  # Qdrant-Chunks
                "collection_name": stats.get("collection", "qms_documents"),
                "engine_info": {
                    "type": stats.get("engine", "qdrant"),
                    "embedding_model": stats.get("embedding_model", "all-MiniLM-L6-v2"),
                    "embedding_dimension": stats.get("embedding_dimension", 384)
                }
            }
        else:
            return {
                "success": False,
                "status": "unavailable",
                "total_documents": 0,
                "collection_name": "none",
                "error": "RAG Engine nicht verfügbar"
            }
    except Exception as e:
        logger.error(f"RAG Stats fehler: {e}")
        return {
            "success": False,
            "status": "error",
            "total_documents": 0,
            "collection_name": "error",
            "error": str(e)
        } 