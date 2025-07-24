"""
Qdrant-basierte RAG Engine für KI-QMS
Ersetzt ChromaDB um NumPy 2.0 Konflikte zu vermeiden.
Nutzt OpenAI Embeddings für Enterprise-Grade Suche.

Features:
- Persistent Qdrant Storage
- OpenAI text-embedding-3-small
- Robuste Vektor-Suche
- Dokumenten-Indexierung
- Chat-Interface
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from .ai_providers import OpenAIEmbeddingProvider
import logging
import asyncio
from typing import List, Dict, Optional, Any
import hashlib
import uuid
from pathlib import Path
import time

logger = logging.getLogger("KI-QMS.QdrantRAG")

class QdrantRAGEngine:
    def __init__(self):
        """Initialisiert Qdrant RAG Engine mit OpenAI Embeddings"""
        self.client = None
        self.embedding_model = None
        self.collection_name = "qms_documents"
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small
        self.is_initialized = False
        
    async def initialize(self):
        """Initialisiert Qdrant Client und OpenAI Embedding Model"""
        try:
            # Qdrant Client (PERSISTENT für Production-ready Storage)
            import os
            storage_path = os.path.join(os.path.dirname(__file__), "..", "qdrant_storage")
            os.makedirs(storage_path, exist_ok=True)
            
            self.client = QdrantClient(path=storage_path)
            logger.info(f"✅ Qdrant Client (persistent) initialisiert: {storage_path}")
            
            # OpenAI Embedding Model laden
            self.embedding_model = OpenAIEmbeddingProvider()
            logger.info("✅ OpenAI Embedding Model geladen")
            
            # Collection erstellen
            await self._create_collection()
            
            self.is_initialized = True
            logger.info("🎉 Qdrant RAG Engine erfolgreich initialisiert")
            
        except Exception as e:
            logger.error(f"❌ Qdrant RAG Engine Initialisierung fehlgeschlagen: {e}")
            self.is_initialized = False
    
    async def _create_collection(self):
        """Erstellt Qdrant Collection für Dokumente"""
        try:
            # Prüfe ob Collection bereits existiert
            collections = self.client.get_collections()
            collection_exists = any(c.name == self.collection_name for c in collections.collections)
            
            if not collection_exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Collection '{self.collection_name}' erstellt")
            else:
                logger.info(f"ℹ️ Collection '{self.collection_name}' bereits vorhanden")
                
        except Exception as e:
            logger.error(f"❌ Collection Erstellung fehlgeschlagen: {e}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generiert OpenAI Embeddings für Texte"""
        if not self.embedding_model:
            raise RuntimeError("Embedding Model nicht initialisiert")
        
        embeddings = await self.embedding_model.encode(texts)
        return embeddings
    
    async def index_document(self, document_id: int, title: str, content: str, 
                           document_type: str = "OTHER", metadata: Dict = None) -> bool:
        """Indexiert ein Dokument in Qdrant mit OpenAI Embeddings"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Text in Chunks aufteilen (für große Dokumente)
            chunks = self._split_text(content, max_length=500)
            
            # OpenAI Embeddings für alle Chunks generieren
            embeddings = await self.generate_embeddings(chunks)
            
            points = []
            for i, chunk in enumerate(chunks):
                # Punkt-ID generieren (UUID-Format für Qdrant)
                point_id = str(uuid.uuid4())
                
                # Metadaten
                payload = {
                    "document_id": document_id,
                    "title": title,
                    "content_chunk": chunk,
                    "chunk_index": i,
                    "document_type": document_type,
                    "full_content": content[:1000],  # Ersten 1000 Zeichen
                    **(metadata or {})
                }
                
                points.append(PointStruct(
                    id=point_id,
                    vector=embeddings[i],
                    payload=payload
                ))
            
            # Punkte in Qdrant speichern
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"✅ Dokument {document_id} mit {len(chunks)} Chunks indexiert (OpenAI Embeddings)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Indexierung fehlgeschlagen für Dokument {document_id}: {e}")
            return False
    
    def _split_text(self, text: str, max_length: int = 500) -> List[str]:
        """Teilt Text in Chunks auf"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]
    
    async def search_documents(self, query: str, max_results: int = 5) -> List[Dict]:
        """Sucht ähnliche Dokumente zu einer Anfrage mit OpenAI Embeddings"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Query Embedding mit OpenAI generieren
            query_embedding = await self.embedding_model.encode(query)
            
            # Qdrant Suche
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=max_results,
                with_payload=True
            )
            
            # Ergebnisse formatieren
            results = []
            for result in search_results:
                results.append({
                    "document_id": result.payload.get("document_id"),
                    "title": result.payload.get("title", "Unbekannt"),
                    "content_snippet": result.payload.get("content_chunk", "")[:200],
                    "score": result.score,
                    "document_type": result.payload.get("document_type", "OTHER"),
                    "embedding_model": "openai/text-embedding-3-small"
                })
            
            logger.info(f"🔍 OpenAI Suche '{query}' ergab {len(results)} Ergebnisse")
            return results
            
        except Exception as e:
            logger.error(f"❌ Suche fehlgeschlagen: {e}")
            return []
    
    async def chat_with_documents(self, question: str, context_docs: int = 3, enable_debug: bool = False) -> Dict:
        """Chat mit Dokumenten-Kontext mit Debug-Tracking"""
        start_time = time.time()
        
        # Debug-Tracking initialisieren
        debug_info = {
            "prompt_type": "qdrant_rag_chat",
            "prompt_source": "QdrantRAGEngine.chat_with_documents", 
            "ai_model": "gemini-1.5-flash",
            "temperature": 0.0,  # Für konsistente Antworten
            "context_limit": context_docs,
            "search_method": "qdrant_vector_similarity",
            "embedding_model": "openai/text-embedding-3-small",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "processing_steps": []
        } if enable_debug else None
        
        try:
            if debug_info:
                debug_info["processing_steps"].append("1. Starting Qdrant document search...")
            
            # Relevante Dokumente finden
            relevant_docs = await self.search_documents(question, max_results=context_docs)
            
            if debug_info:
                debug_info["processing_steps"].append(f"2. Found {len(relevant_docs)} relevant documents")
                debug_info["search_results_count"] = len(relevant_docs)
            
            if not relevant_docs:
                processing_time = time.time() - start_time
                return {
                    "answer": "Keine relevanten Dokumente gefunden.",
                    "sources": [],
                    "success": True,
                    "confidence": 0.0,
                    "processing_time": processing_time,
                    "debug_info": debug_info
                }
            
            if debug_info:
                debug_info["processing_steps"].append("3. Building context from documents...")
            
            # Kontext zusammenstellen
            context_chunks = []
            for doc in relevant_docs:
                context_chunks.append(f"**{doc['title']}**: {doc['content_snippet']}")
            
            context = "\n\n".join(context_chunks)
            
            if debug_info:
                debug_info["context_length"] = len(context)
                debug_info["content_types_found"] = list(set(doc.get('document_type', 'unknown') for doc in relevant_docs))
            
            # Verwende neue strikte JSON-Prompts aus prompts.py
            try:
                from .rag_prompts import get_strict_json_prompt
                
                if debug_info:
                    debug_info["processing_steps"].append("4. Using centralized JSON prompt system...")
                    debug_info["prompt_type"] = "strict_json_qms_analysis"
                    debug_info["prompt_source"] = "prompts.py.get_strict_json_prompt"
                
                # Hole strikten JSON-Prompt
                prompt_config = get_strict_json_prompt(
                    "qms_analysis",
                    context=context,
                    question=question
                )
                
                prompt = prompt_config["prompt"]
                
                if debug_info:
                    debug_info["prompt_length"] = len(prompt)
                    debug_info["temperature"] = prompt_config.get("temperature", 0.0)
                    debug_info["json_schema"] = prompt_config.get("expected_schema", "QMSResponseSchema")
                    debug_info["full_prompt"] = prompt if enable_debug else "[Hidden - enable debug for full prompt]"
                
            except ImportError:
                # Fallback auf Legacy-Prompt
                if debug_info:
                    debug_info["processing_steps"].append("4. Fallback to legacy prompt (prompts.py not available)")
                    debug_info["prompt_type"] = "legacy_qdrant_chat"
                
                prompt = f"""Du bist ein QMS-Experte. Beantworte die Frage basierend auf dem bereitgestellten Kontext.

KONTEXT:
{context}

FRAGE: {question}

Gib eine präzise, fachlich korrekte Antwort."""

                if debug_info:
                    debug_info["prompt_length"] = len(prompt)
                    debug_info["full_prompt"] = prompt if enable_debug else "[Hidden - enable debug for full prompt]"
            
            if debug_info:
                debug_info["processing_steps"].append("5. Generating AI response...")
            
            # Erweiterte Antwort mit strukturiertem JSON
            if hasattr(self, 'ai_model') and self.ai_model:
                try:
                    # Verwende Google Gemini mit temperature=0 für konsistente Antworten
                    generation_config = {
                        "temperature": 0.0,
                        "top_p": 1.0,
                        "top_k": 1,
                        "max_output_tokens": 2048,
                    }
                    
                    ai_response = self.ai_model.generate_content(
                        prompt,
                        generation_config=generation_config
                    )
                    
                    answer_text = ai_response.text
                    
                    if debug_info:
                        debug_info["ai_response_length"] = len(answer_text)
                        debug_info["ai_provider_used"] = "google_gemini"
                        debug_info["generation_config"] = generation_config
                    
                except Exception as ai_error:
                    if debug_info:
                        debug_info["ai_error"] = str(ai_error)
                        debug_info["ai_provider_used"] = "fallback"
                    
                    answer_text = f"Basierend auf {len(relevant_docs)} relevanten Dokumenten:\n\n{context}"
            else:
                if debug_info:
                    debug_info["ai_provider_used"] = "fallback_no_model"
                
                answer_text = f"Basierend auf {len(relevant_docs)} relevanten Dokumenten:\n\n{context}"
            
            # Konfidenz basierend auf durchschnittlicher Score
            avg_confidence = sum(doc['score'] for doc in relevant_docs) / len(relevant_docs)
            processing_time = time.time() - start_time
            
            if debug_info:
                debug_info["processing_steps"].append(f"6. Completed in {processing_time:.2f}s")
                debug_info["confidence_calculation"] = {
                    "method": "average_similarity_score",
                    "individual_scores": [doc['score'] for doc in relevant_docs],
                    "final_confidence": avg_confidence
                }
            
            # Frontend-kompatible Sources-Struktur
            sources = []
            for doc in relevant_docs:
                sources.append({
                    "metadata": {
                        "title": doc["title"],
                        "document_type": doc["document_type"],
                        "filename": f"Dokument_{doc['document_id']}.pdf",
                        "document_id": doc["document_id"]
                    },
                    "content": doc["content_snippet"],
                    "score": doc["score"],
                    "file": doc["title"],
                    "content_type": doc.get("document_type", "document"),
                    "similarity": doc["score"]
                })
            
            return {
                "answer": answer_text,
                "sources": sources,
                "success": True,
                "confidence": avg_confidence,
                "processing_time": processing_time,
                "context_used": len(relevant_docs),
                "debug_info": debug_info
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            if debug_info:
                debug_info["error"] = str(e)
                debug_info["processing_steps"].append(f"ERROR: {str(e)}")
            
            return {
                "answer": f"Fehler bei der Antwortgenerierung: {str(e)}",
                "sources": [],
                "success": False,
                "confidence": 0.0,
                "processing_time": processing_time,
                "debug_info": debug_info
            }
    
    async def get_system_stats(self) -> Dict:
        """System-Statistiken mit OpenAI Integration"""
        try:
            if not self.is_initialized:
                return {"status": "not_initialized", "document_count": 0}
            
            # Collection Info
            collection_info = self.client.get_collection(self.collection_name)
            
            return {
                "status": "ready",
                "engine": "qdrant_openai",
                "document_count": collection_info.points_count,
                "embedding_model": "openai/text-embedding-3-small",
                "embedding_dimension": self.embedding_dimension,
                "collection": self.collection_name,
                "cost_model": "sehr günstig ($0.00002/1K tokens)",
                "features": ["persistent_storage", "openai_embeddings", "enterprise_grade"]
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Global Instance
qdrant_rag_engine = QdrantRAGEngine()

# Async Wrapper Funktionen für Kompatibilität
async def index_all_documents():
    """Placeholder für Bulk-Indexierung"""
    stats = await qdrant_rag_engine.get_system_stats()
    return {
        "success": True,
        "message": f"Qdrant RAG Engine bereit. {stats.get('document_count', 0)} Dokumente indexiert.",
        "stats": stats
    }

# Legacy Kompatibilität
async def search_documents_semantic(query: str, max_results: int = 5):
    """Legacy-kompatible Suche"""
    results = await qdrant_rag_engine.search_documents(query, max_results)
    return {
        "success": True,
        "results": results,
        "query": query
    } 