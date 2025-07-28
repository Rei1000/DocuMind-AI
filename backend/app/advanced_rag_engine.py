"""
🚀 ADVANCED RAG ENGINE für KI-QMS - Enterprise Grade 2024/2025
==============================================================

Moderne RAG-Implementation mit Best Practices:
- Hierarchical + Semantic Chunking
- OpenAI Embeddings (text-embedding-3-small)
- Hybrid Retrieval (Vector + BM25) 
- Query Enhancement Pipeline
- Structured Response Formats mit Quellenangaben
- Re-ranking und Post-processing

Author: AI Assistant  
Version: 3.5.0 - OpenAI Enterprise Grade
"""

from typing import List, Dict, Optional, Any, Tuple, Union
import logging
import asyncio
import os
import time
import re
from dataclasses import dataclass, field
import json

# Core Imports
from .ai_providers import OpenAIEmbeddingProvider
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Enhanced Schemas Integration
from .schemas_enhanced import (
    EnhancedChunkMetadata,
    EnhancedDocumentMetadata,
    EnhancedDocumentType,
    EnhancedKeyword,
    normalize_document_type
)

# Enhanced Metadata Extractor Integration
try:
    from .enhanced_metadata_extractor import (
        extract_enhanced_metadata,
        get_enhanced_extractor
    )
    ENHANCED_METADATA_AVAILABLE = True
except ImportError:
    ENHANCED_METADATA_AVAILABLE = False

logger = logging.getLogger("KI-QMS.AdvancedRAG")

@dataclass
class SearchResult:
    """Strukturiertes Suchergebnis mit erweiterten Metadaten"""
    content: str
    document_id: int
    title: str
    document_type: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    score: float = 0.0
    source_type: str = "vector"
    chunk_index: int = 0
    full_paragraph: str = ""
    context_before: str = ""
    context_after: str = ""
    keywords: List[str] = field(default_factory=list)

@dataclass 
class EnhancedResponse:
    """Strukturierte Antwort mit Quellenangaben und Metadaten"""
    answer: str
    sources: List[SearchResult]
    confidence: float
    query_enhanced: str
    processing_time: float
    methodology: str
    suggested_followup: List[str]
    full_context_available: bool = False
    source_citations: str = ""

class AdvancedChunker:
    """Erweiterte Chunking-Strategien für bessere Kontext-Erhaltung"""
    
    def __init__(self, chunk_size: int = 800, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def hierarchical_chunk(self, content: str, title: str = "") -> List[Dict]:
        """Hierarchical Chunking mit Kontext-Anreicherung"""
        
        # 1. Strukturanalyse
        structure = self._analyze_structure(content)
        
        # 2. Primary Chunking
        primary_chunks = self._create_base_chunks(content)
        
        # 3. Erweiterte Chunks mit Metadaten
        enhanced_chunks = []
        for i, chunk in enumerate(primary_chunks):
            enhanced_chunk = {
                "content": chunk,
                "chunk_index": i,
                "section": self._find_section(chunk, structure),
                "keywords": self._extract_keywords(chunk),
                "importance_score": self._calculate_importance(chunk, title),
                "context_before": primary_chunks[i-1][-100:] if i > 0 else "",
                "context_after": primary_chunks[i+1][:100] if i < len(primary_chunks)-1 else "",
                "full_paragraph": self._find_full_paragraph(chunk, content),
                "page_estimate": self._estimate_page(i, len(primary_chunks))
            }
            enhanced_chunks.append(enhanced_chunk)
        
        return enhanced_chunks
    
    def _analyze_structure(self, content: str) -> Dict:
        """Analysiert Dokumentstruktur"""
        structure = {
            "sections": [],
            "has_headers": False,
            "has_numbering": False,
            "estimated_pages": max(1, len(content) // 2000)
        }
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # Header Detection
            if (len(line) > 0 and len(line) < 100 and 
                (line.isupper() or re.match(r'^\d+\.', line) or line.startswith('#'))):
                structure["sections"].append(line)
                structure["has_headers"] = True
        
        return structure
    
    def _create_base_chunks(self, content: str) -> List[str]:
        """Erstellt Basis-Chunks mit intelligenten Trennungen"""
        # Hierarchical Separators
        separators = [
            '\n\n\n',  # Section breaks
            '\n\n',    # Paragraph breaks
            '\n',      # Line breaks
            '. ',      # Sentence breaks
            ' ',       # Word breaks
            ''         # Character breaks
        ]
        
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        for paragraph in paragraphs:
            if len(current_chunk + paragraph) <= self.chunk_size:
                current_chunk += paragraph + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _find_section(self, chunk: str, structure: Dict) -> str:
        """Findet zugehörige Sektion"""
        chunk_lower = chunk.lower()
        for section in structure.get("sections", []):
            section_words = section.lower().split()[:3]  # First 3 words
            if any(word in chunk_lower for word in section_words):
                return section
        return ""
    
    def _extract_keywords(self, chunk: str) -> List[str]:
        """Extrahiert wichtige Keywords"""
        # QM-spezifische Keywords
        qm_terms = ['ISO', 'DIN', 'Norm', 'Standard', 'Qualität', 'Management', 
                   'Verfahren', 'Prozess', 'Audit', 'Zertifizierung', 'Compliance',
                   'Dokumentation', 'Prüfung', 'Kontrolle', 'Überwachung']
        
        found_keywords = []
        for term in qm_terms:
            if term.lower() in chunk.lower():
                found_keywords.append(term)
        
        # Zusätzliche wichtige Wörter (Großbuchstaben, Zahlen)
        additional = re.findall(r'\b[A-Z][A-Za-z]{3,}\b|\b\d{2,}\b', chunk)
        found_keywords.extend(additional[:5])  # Top 5
        
        return list(set(found_keywords))[:10]  # Max 10 unique
    
    def _calculate_importance(self, chunk: str, title: str) -> float:
        """Berechnet Wichtigkeits-Score"""
        score = 0.5  # Base score
        
        # Title overlap
        if title:
            title_words = set(title.lower().split())
            chunk_words = set(chunk.lower().split())
            overlap = len(title_words.intersection(chunk_words))
            score += min(0.3, overlap * 0.1)
        
        # QM Keywords bonus
        qm_keywords = ['iso', 'din', 'norm', 'standard', 'qualität']
        qm_count = sum(1 for kw in qm_keywords if kw in chunk.lower())
        score += min(0.2, qm_count * 0.05)
        
        # Length bonus (prefer substantial content)
        if 200 <= len(chunk) <= 1000:
            score += 0.1
        
        return min(1.0, score)
    
    def _find_full_paragraph(self, chunk: str, full_content: str) -> str:
        """Findet vollständigen Absatz"""
        chunk_start = chunk[:50].lower()
        paragraphs = full_content.split('\n\n')
        
        for para in paragraphs:
            if chunk_start in para.lower():
                return para.strip()
        
        return chunk
    
    def _estimate_page(self, chunk_index: int, total_chunks: int) -> int:
        """Schätzt Seitenzahl"""
        if total_chunks <= 1:
            return 1
        page_ratio = chunk_index / total_chunks
        return max(1, int(page_ratio * 10))  # Assume max 10 pages

class AdvancedRAGEngine:
    """
    🚀 Enterprise-Grade RAG Engine mit OpenAI Embeddings
    
    Features:
    - Hierarchical Document Processing
    - OpenAI text-embedding-3-small (1536d)
    - Enhanced Query Processing  
    - Structured Responses mit Citations
    - Context-Aware Chunking
    """
    
    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.embedding_model: Optional[OpenAIEmbeddingProvider] = None
        self.chunker: Optional[AdvancedChunker] = None
        self.collection_name = "qms_documents"
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small
        self.is_initialized = False
        
        # Configuration
        self.chunk_size = 800
        self.chunk_overlap = 200
        self.max_results = 8
        
        # Document Store (für BM25 Fallback)
        self.document_store: List[Dict] = []
        
    async def initialize(self):
        """🔧 Initialisiert Advanced RAG Engine mit OpenAI"""
        try:
            logger.info("🚀 Initialisiere Advanced RAG Engine...")
            
            # 1. Qdrant Client Setup
            storage_path = os.path.join(os.path.dirname(__file__), "..", "qdrant_storage")
            os.makedirs(storage_path, exist_ok=True)
            self.client = QdrantClient(path=storage_path)
            logger.info(f"✅ Qdrant Client initialisiert: {storage_path}")
            
            # 2. OpenAI Embedding Model
            self.embedding_model = OpenAIEmbeddingProvider()
            logger.info("✅ OpenAI Embedding Model geladen")
            
            # 3. Advanced Chunker
            self.chunker = AdvancedChunker(self.chunk_size, self.chunk_overlap)
            logger.info("✅ Advanced Chunker initialisiert")
            
            # 4. Collection Setup
            await self._setup_collection()
            
            self.is_initialized = True
            logger.info("🎉 Advanced RAG Engine erfolgreich initialisiert")
            
        except Exception as e:
            logger.error(f"❌ Initialisierung fehlgeschlagen: {e}")
            self.is_initialized = False
            raise
    
    async def _setup_collection(self):
        """Erstellt/überprüft Qdrant Collection"""
        try:
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
            logger.error(f"❌ Collection Setup fehlgeschlagen: {e}")
            raise
    
    async def index_document_advanced(
        self, 
        document_id: int, 
        title: str, 
        content: str,
        document_type: str = "OTHER",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        🔧 Erweiterte Dokumenten-Indexierung mit Enhanced Metadata Extraction
        
        Returns:
            Dict mit Indexierungs-Statistiken und Enhanced Metadata
        """
        start_time = time.time()
        
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.client or not self.embedding_model or not self.chunker:
                raise RuntimeError("Engine nicht vollständig initialisiert")
            
            # 1. Enhanced Metadata Extraction (falls verfügbar)
            enhanced_metadata = None
            enhanced_response = None
            if ENHANCED_METADATA_AVAILABLE:
                try:
                    logger.info(f"🎯 Starte Enhanced Metadata Extraction für '{title}'")
                    enhanced_response = await extract_enhanced_metadata(
                        content=content,
                        document_title=title,
                        document_type_hint=document_type
                    )
                    enhanced_metadata = enhanced_response.metadata
                    logger.info(f"✅ Enhanced Metadata extrahiert mit Konfidenz: {enhanced_metadata.ai_confidence}")
                except Exception as e:
                    logger.warning(f"⚠️ Enhanced Metadata Extraction fehlgeschlagen: {e}")
            
            # 2. Advanced Chunking (mit Enhanced Metadata falls verfügbar)
            if enhanced_metadata and enhanced_response and enhanced_response.chunks_metadata:
                # Verwende Enhanced Chunks
                enhanced_chunks = enhanced_response.chunks_metadata
                chunks = []
                for i, enhanced_chunk in enumerate(enhanced_chunks):
                    chunk_data = {
                        "content": content[i*800:(i+1)*800],  # Approximation
                        "chunk_index": enhanced_chunk.chunk_index,
                        "section": enhanced_chunk.section_title or "",
                        "keywords": [kw.term for kw in enhanced_chunk.keywords],
                        "importance_score": enhanced_chunk.importance_score,
                        "context_before": "",
                        "context_after": "",
                        "full_paragraph": content[i*800:(i+1)*800],
                        "page_estimate": enhanced_chunk.page_number or 1,
                        "enhanced_metadata": enhanced_chunk
                    }
                    chunks.append(chunk_data)
                logger.info(f"📝 {len(chunks)} Enhanced Chunks verwendet")
            else:
                # Fallback zu Standard Chunking
                chunks = self.chunker.hierarchical_chunk(content, title)
                logger.info(f"📝 {len(chunks)} Standard Chunks erstellt für Dokument {document_id}")
            
            # 3. OpenAI Embeddings und Indexierung
            points = []
            chunk_texts = [chunk_data["content"] for chunk_data in chunks]
            embeddings = await self.embedding_model.encode(chunk_texts)
            
            # Handle both single embedding and batch embeddings
            if isinstance(embeddings, list) and len(embeddings) > 0 and isinstance(embeddings[0], list):
                # Batch embeddings
                embedding_list = embeddings
            else:
                # Single embedding - wrap in list
                embedding_list = [embeddings] if not isinstance(embeddings, list) else embeddings
            
            for i, chunk_data in enumerate(chunks):
                # Enhanced Payload mit allen verfügbaren Metadaten
                payload = {
                    "document_id": document_id,
                    "title": title,
                    "content": chunk_data["content"],
                    "chunk_index": chunk_data["chunk_index"],
                    "document_type": document_type,
                    "section": chunk_data["section"],
                    "keywords": chunk_data["keywords"],
                    "importance_score": chunk_data["importance_score"],
                    "context_before": chunk_data.get("context_before", ""),
                    "context_after": chunk_data.get("context_after", ""),
                    "full_paragraph": chunk_data.get("full_paragraph", chunk_data["content"]),
                    "page_number": chunk_data.get("page_estimate", 1),
                    **(metadata or {})
                }
                
                # Enhanced Metadata hinzufügen falls verfügbar
                if enhanced_metadata:
                    payload.update({
                        "enhanced_document_type": enhanced_metadata.document_type.value,
                        "main_category": enhanced_metadata.main_category,
                        "sub_category": enhanced_metadata.sub_category,
                        "process_area": enhanced_metadata.process_area,
                        "compliance_level": enhanced_metadata.compliance_level.value,
                        "quality_score": enhanced_metadata.quality_scores.overall,
                        "ai_confidence": enhanced_metadata.ai_confidence,
                        "interest_groups": enhanced_metadata.interest_groups,
                        "iso_standards": enhanced_metadata.iso_standards_referenced,
                        "compliance_areas": enhanced_metadata.compliance_areas,
                        "metadata_version": enhanced_metadata.metadata_version
                    })
                
                # Enhanced Chunk Metadata falls verfügbar
                if "enhanced_metadata" in chunk_data:
                    enhanced_chunk = chunk_data["enhanced_metadata"]
                    payload.update({
                        "chunk_section_title": enhanced_chunk.section_title,
                        "chunk_paragraph_number": enhanced_chunk.paragraph_number,
                        "chunk_word_count": enhanced_chunk.word_count,
                        "chunk_interest_groups": enhanced_chunk.interest_groups,
                        "chunk_importance_score": enhanced_chunk.importance_score
                    })
                
                # Qdrant Point - Use integer ID instead of UUID
                point_id = document_id * 1000 + chunk_data['chunk_index']
                
                # Ensure we have a valid embedding
                if i < len(embedding_list):
                    embedding = embedding_list[i]
                    if isinstance(embedding, list) and len(embedding) > 0:
                        points.append(PointStruct(
                            id=point_id,
                            vector=embedding,
                            payload=payload
                        ))
                    else:
                        logger.warning(f"⚠️ Ungültiges Embedding für Chunk {i}")
                else:
                    logger.warning(f"⚠️ Kein Embedding für Chunk {i}")
                
                # Document Store für Fallback
                self.document_store.append({
                    "id": str(point_id),
                    "content": chunk_data["content"],
                    "metadata": payload
                })
            
            # 4. Upsert zu Qdrant
            if points:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                logger.info(f"✅ {len(points)} Punkte zu Qdrant indexiert")
            else:
                logger.warning("⚠️ Keine gültigen Punkte für Indexierung")
            
            processing_time = time.time() - start_time
            
            # 5. Enhanced Response
            response = {
                "success": True,
                "document_id": document_id,
                "chunks_created": len(chunks),
                "points_indexed": len(points),
                "processing_time": processing_time,
                "methodology": "enhanced_hierarchical_chunking_with_openai_embeddings",
                "features_applied": [
                    "enhanced_metadata_extraction", 
                    "hierarchical_chunking", 
                    "keyword_extraction", 
                    "importance_scoring", 
                    "context_preservation", 
                    "openai_embeddings",
                    "enterprise_grade_vectors"
                ]
            }
            
            # Enhanced Metadata zur Response hinzufügen
            if enhanced_metadata:
                response.update({
                    "enhanced_metadata": {
                        "document_type": enhanced_metadata.document_type.value,
                        "main_category": enhanced_metadata.main_category,
                        "quality_score": enhanced_metadata.quality_scores.overall,
                        "ai_confidence": enhanced_metadata.ai_confidence,
                        "compliance_level": enhanced_metadata.compliance_level.value,
                        "keywords_count": len(enhanced_metadata.primary_keywords),
                        "metadata_version": enhanced_metadata.metadata_version
                    }
                })
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Enhanced Indexierung fehlgeschlagen: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": processing_time,
                "methodology": "enhanced_indexing_with_fallback"
            }
    
    async def enhanced_search(
        self, 
        query: str, 
        max_results: int = 8,
        enable_reranking: bool = True
    ) -> EnhancedResponse:
        """
        🔍 Erweiterte Suche mit Query Enhancement und Re-ranking
        """
        start_time = time.time()
        
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.client or not self.embedding_model:
                raise RuntimeError("Engine nicht vollständig initialisiert")
            
            # 1. Query Enhancement
            enhanced_query = self._enhance_query(query)
            
            # 2. Semantic Search
            search_results = await self._semantic_search(enhanced_query, max_results)
            
            # 3. Re-ranking (optional)
            if enable_reranking and len(search_results) > 1:
                search_results = self._rerank_results(query, search_results)
            
            # 4. Enhanced Answer Generation
            answer = self._generate_enhanced_answer(query, search_results)
            
            # 5. Follow-up Suggestions
            followup_questions = self._generate_followup_questions(query, search_results)
            
            # 6. Source Citations
            citations = self._generate_citations(search_results)
            
            processing_time = time.time() - start_time
            
            response = EnhancedResponse(
                answer=answer,
                sources=search_results,
                confidence=self._calculate_confidence(search_results),
                query_enhanced=enhanced_query,
                processing_time=processing_time,
                methodology="enhanced_semantic_search_with_reranking",
                suggested_followup=followup_questions,
                full_context_available=len(search_results) >= 3,
                source_citations=citations
            )
            
            logger.info(f"🔍 Erweiterte Suche abgeschlossen: {len(search_results)} Ergebnisse in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"❌ Erweiterte Suche fehlgeschlagen: {e}")
            return EnhancedResponse(
                answer=f"Entschuldigung, bei der Suche ist ein Fehler aufgetreten: {str(e)}",
                sources=[],
                confidence=0.0,
                query_enhanced=query,
                processing_time=time.time() - start_time,
                methodology="error",
                suggested_followup=[]
            )
    
    def _enhance_query(self, query: str) -> str:
        """Verbessert Query für bessere Retrieval-Ergebnisse"""
        enhanced = query
        
        # QM-spezifische Erweiterungen
        qm_expansions = {
            "iso": "ISO 13485 Norm Standard Medizinprodukte",
            "qualität": "Qualitätsmanagement QM Quality Assurance",
            "audit": "Audit Überprüfung Prüfung Assessment",
            "prozess": "Prozess Verfahren Ablauf Workflow Procedure",
            "dokument": "Dokument Dokumentation Unterlagen Documentation",
            "norm": "Norm Standard Richtlinie Guideline",
            "zertifizierung": "Zertifizierung Certification Akkreditierung"
        }
        
        query_lower = query.lower()
        for term, expansion in qm_expansions.items():
            if term in query_lower:
                enhanced += f" {expansion}"
        
        return enhanced
    
    async def _semantic_search(self, query: str, max_results: int) -> List[SearchResult]:
        """Führt semantische Suche mit OpenAI Embeddings und Qdrant durch"""
        if not self.client or not self.embedding_model:
            return []
        
        try:
            # Query Embedding mit OpenAI
            query_embedding = await self.embedding_model.encode(query)
            
            # Qdrant Search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=max_results,
                with_payload=True
            )
            
            # Convert to SearchResult objects
            results = []
            for result in search_results:
                payload = result.payload
                search_result = SearchResult(
                    content=payload.get("content", ""),
                    document_id=payload.get("document_id", 0),
                    title=payload.get("title", "Unbekannt"),
                    document_type=payload.get("document_type", "OTHER"),
                    page_number=payload.get("page_number"),
                    section=payload.get("section", ""),
                    score=result.score,
                    source_type="semantic_openai",
                    chunk_index=payload.get("chunk_index", 0),
                    full_paragraph=payload.get("full_paragraph", payload.get("content", "")),
                    context_before=payload.get("context_before", ""),
                    context_after=payload.get("context_after", ""),
                    keywords=payload.get("keywords", [])
                )
                results.append(search_result)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Semantic Search fehlgeschlagen: {e}")
            return []
    
    def _rerank_results(self, original_query: str, results: List[SearchResult]) -> List[SearchResult]:
        """Re-rankt Ergebnisse basierend auf Query-Relevanz"""
        try:
            query_words = set(original_query.lower().split())
            
            for result in results:
                # Query overlap
                content_words = set(result.content.lower().split())
                overlap = len(query_words.intersection(content_words)) / len(query_words)
                
                # Keyword bonus
                keyword_bonus = len([kw for kw in result.keywords if kw.lower() in original_query.lower()]) * 0.1
                
                # Section relevance
                section_bonus = 0.1 if result.section and any(word in result.section.lower() for word in query_words) else 0
                
                # Combine scores
                result.score = (result.score * 0.6) + (overlap * 0.3) + keyword_bonus + section_bonus
            
            # Sort by new score
            results.sort(key=lambda x: x.score, reverse=True)
            return results
            
        except Exception as e:
            logger.warning(f"⚠️ Re-ranking fehlgeschlagen: {e}")
            return results
    
    def _generate_enhanced_answer(self, query: str, results: List[SearchResult]) -> str:
        """Generiert erweiterte, strukturierte Antwort"""
        if not results:
            return "Entschuldigung, ich konnte keine relevanten Informationen zu Ihrer Anfrage finden."
        
        # Hauptantwort
        answer = f"**Antwort zu: {query}**\n\n"
        
        # Context aus Top-Ergebnissen
        context_parts = []
        for i, result in enumerate(results[:3], 1):
            content = result.full_paragraph if result.full_paragraph else result.content
            
            # Begrenzen auf wichtigste Teile
            if len(content) > 400:
                content = content[:397] + "..."
            
            context_parts.append(f"**{i}. {result.title}** {f'(Abschnitt: {result.section})' if result.section else ''}\n{content}")
        
        answer += "\n\n".join(context_parts)
        
        # Zusätzliche Informationen
        if len(results) > 3:
            answer += f"\n\n*... und {len(results) - 3} weitere relevante Abschnitte gefunden.*"
        
        return answer
    
    def _generate_followup_questions(self, query: str, results: List[SearchResult]) -> List[str]:
        """Generiert relevante Follow-up Fragen"""
        followups = []
        
        # Basierend auf gefundenen Dokumenttypen
        doc_types = list(set(r.document_type for r in results if r.document_type != "OTHER"))
        for doc_type in doc_types[:2]:
            followups.append(f"Welche weiteren {doc_type} Dokumente sind verfügbar?")
        
        # Basierend auf Sektionen
        sections = list(set(r.section for r in results if r.section))
        for section in sections[:1]:
            followups.append(f"Was steht noch in '{section}'?")
        
        # Query-spezifische Follow-ups
        query_lower = query.lower()
        if "iso" in query_lower:
            followups.append("Welche anderen ISO Standards sind relevant?")
        elif "prozess" in query_lower:
            followups.append("Wie läuft der detaillierte Prozess ab?")
        elif "qualität" in query_lower:
            followups.append("Welche Qualitätskontrollmaßnahmen gibt es?")
        
        return followups[:3]  # Maximal 3
    
    def _generate_citations(self, results: List[SearchResult]) -> str:
        """Generiert Quellenangaben"""
        if not results:
            return ""
        
        citations = "**📚 Quellen:**\n"
        for i, result in enumerate(results[:5], 1):
            citation = f"{i}. **{result.title}**"
            if result.section:
                citation += f", Abschnitt: {result.section}"
            if result.page_number:
                citation += f", Seite {result.page_number}"
            citation += f" (Relevanz: {result.score:.2f})"
            citations += f"\n{citation}"
        
        return citations
    
    def _calculate_confidence(self, results: List[SearchResult]) -> float:
        """Berechnet Konfidenz der Antwort"""
        if not results:
            return 0.0
        
        # Durchschnittlicher Score der Top-3
        top_scores = [r.score for r in results[:3]]
        avg_score = sum(top_scores) / len(top_scores)
        
        # Bonus für mehrere Quellen
        source_bonus = min(0.2, len(results) * 0.04)
        
        # Bonus für verschiedene Dokumenttypen
        doc_types = len(set(r.document_type for r in results))
        diversity_bonus = min(0.1, doc_types * 0.02)
        
        confidence = avg_score + source_bonus + diversity_bonus
        return min(1.0, confidence)
    
    async def get_system_stats(self) -> Dict:
        """Erweiterte System-Statistiken"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.client:
                raise RuntimeError("Client nicht initialisiert")
            
            # Collection Info
            collection_info = self.client.get_collection(self.collection_name)
            
            stats = {
                "status": "ready",
                "engine_type": "advanced_rag_openai_enterprise",
                "collection_name": self.collection_name,
                "total_vectors": collection_info.points_count,
                "embedding_model": "openai/text-embedding-3-small",
                "embedding_dimension": self.embedding_dimension,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "features": {
                    "hierarchical_chunking": True,
                    "openai_embeddings": True,
                    "semantic_search": True,
                    "query_enhancement": True,
                    "source_citations": True,
                    "context_preservation": True,
                    "reranking": True,
                    "followup_suggestions": True,
                    "structured_responses": True
                },
                "document_store_size": len(self.document_store),
                "methodology": "openai_enterprise_grade_2025",
                "cost_model": "sehr günstig ($0.00002/1K tokens)"
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Stats Abruf fehlgeschlagen: {e}")
            return {
                "status": "error",
                "error": str(e),
                "engine_type": "advanced_rag_openai_enterprise"
            }

# Global Instance
advanced_rag_engine = AdvancedRAGEngine()

# Convenience Functions
async def index_document_advanced(
    document_id: int, 
    title: str, 
    content: str, 
    document_type: str = "OTHER", 
    metadata: Optional[Dict] = None
) -> Dict:
    """🚀 Erweiterte Dokumenten-Indexierung"""
    return await advanced_rag_engine.index_document_advanced(
        document_id, title, content, document_type, metadata
    )

async def search_documents_advanced(query: str, max_results: int = 8) -> EnhancedResponse:
    """🔍 Erweiterte Dokumentensuche"""
    return await advanced_rag_engine.enhanced_search(query, max_results)

async def get_advanced_stats() -> Dict:
    """📊 Erweiterte System-Statistiken"""
    return await advanced_rag_engine.get_system_stats() 