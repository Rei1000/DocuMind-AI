"""
🎯 ENHANCED METADATA EXTRACTOR für KI-QMS - Enterprise Grade v3.1.0
═══════════════════════════════════════════════════════════════════

Fortgeschrittener Metadaten-Extraktor mit:

✅ FEATURES:
- 🎯 Enhanced Schemas mit umfassender Typisierung
- 🔧 Robuster JSON Parser mit 5-Layer Fallback
- 📊 Temperatur=0 für maximale Konsistenz
- 🏷️ QM-spezifische Klassifizierung (25+ Dokumenttypen)
- 📈 Enterprise-Grade Performance-Monitoring
- 🔄 Chunk-Metadaten für Advanced RAG Integration

🎯 INTEGRATION:
- Ersetzt veraltete ai_metadata_extractor.py
- Vollständige Pydantic-Validierung
- Advanced RAG Engine Integration
- Enhanced Prompt Engineering

Author: Enhanced AI Assistant
Version: 3.1.0 - Enterprise Edition
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Enhanced Schemas Import
from schemas_enhanced import (
    EnhancedDocumentMetadata,
    EnhancedChunkMetadata,
    EnhancedMetadataResponse,
    EnhancedMetadataExtractionRequest,
    EnhancedDocumentType,
    EnhancedKeyword,
    KeywordImportance,
    QualityScore,
    ComplianceLevel,
    normalize_document_type,
    create_fallback_metadata
)

# Enhanced Tools Import
from json_parser import (
    EnhancedJSONParser,
    parse_ai_response,
    validate_json_response
)

from prompts_enhanced import (
    build_enhanced_extraction_prompt,
    build_chunking_prompt,
    build_quality_assessment_prompt,
    build_compliance_analysis_prompt,
    build_interest_group_prompt,
    get_prompt_config,
    optimize_prompt_for_model
)

# AI Provider Import
from ai_providers import OpenAI4oMiniProvider, GoogleGeminiProvider

# Setup Logging
logger = logging.getLogger(__name__)

class EnhancedMetadataExtractor:
    """
    🎯 Enterprise-Grade Metadata Extractor
    
    Kombiniert Enhanced Schemas, JSON Parser und optimierte Prompts
    für konsistente und umfassende Metadaten-Extraktion.
    """
    
    def __init__(self, ai_provider: str = "openai"):
        """
        Initialisiert Enhanced Metadata Extractor
        
        Args:
            ai_provider: "openai" oder "gemini"
        """
        self.ai_provider_name = ai_provider
        self.ai_provider = None
        self.json_parser = EnhancedJSONParser()
        self.performance_metrics = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'average_processing_time': 0.0,
            'fallback_uses': 0
        }
        
        # Initialize AI Provider
        self._initialize_ai_provider()
    
    def _initialize_ai_provider(self):
        """Initialisiert AI Provider"""
        try:
            if self.ai_provider_name == "openai":
                self.ai_provider = OpenAI4oMiniProvider()
            elif self.ai_provider_name == "gemini":
                self.ai_provider = GoogleGeminiProvider()
            else:
                logger.warning(f"Unbekannter AI Provider: {self.ai_provider_name}, verwende OpenAI")
                self.ai_provider = OpenAI4oMiniProvider()
                
            logger.info(f"✅ AI Provider initialisiert: {self.ai_provider_name}")
            
        except Exception as e:
            logger.error(f"❌ AI Provider Initialisierung fehlgeschlagen: {e}")
            self.ai_provider = None
    
    async def extract_enhanced_metadata(self, 
                                      content: str,
                                      document_title: Optional[str] = None,
                                      document_type_hint: Optional[str] = None,
                                      include_chunking: bool = True) -> EnhancedMetadataResponse:
        """
        🎯 Hauptfunktion für Enhanced Metadata Extraction
        
        Args:
            content: Dokumentinhalt
            document_title: Optional - Dokumenttitel
            document_type_hint: Optional - Dokumenttyp-Hinweis
            include_chunking: Ob Chunk-Metadaten erstellt werden sollen
            
        Returns:
            EnhancedMetadataResponse: Vollständige Metadaten-Response
        """
        start_time = time.time()
        
        try:
            logger.info(f"🎯 Starte Enhanced Metadata Extraction für Dokument: {document_title or 'Unbekannt'}")
            
            # 1. Document Metadata Extraction
            document_metadata = await self._extract_document_metadata(
                content, document_title, document_type_hint
            )
            
            # 2. Chunk Metadata Extraction (optional)
            chunks_metadata = []
            if include_chunking:
                chunks_metadata = await self._extract_chunks_metadata(
                    content, document_metadata
                )
            
            processing_time = time.time() - start_time
            
            # 3. Performance Metrics Update
            self.performance_metrics['total_extractions'] += 1
            self.performance_metrics['successful_extractions'] += 1
            
            # 4. Create Response
            response = EnhancedMetadataResponse(
                success=True,
                metadata=document_metadata,
                chunks_metadata=chunks_metadata,
                processing_time=processing_time,
                chunks_created=len(chunks_metadata),
                confidence_score=document_metadata.ai_confidence,
                errors=[],
                warnings=[]
            )
            
            logger.info(f"✅ Enhanced Metadata Extraction erfolgreich in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Enhanced Metadata Extraction fehlgeschlagen: {e}")
            
            # Fallback Metadata
            fallback_metadata = create_fallback_metadata(document_title or "Unknown Document")
            
            return EnhancedMetadataResponse(
                success=False,
                metadata=fallback_metadata,
                chunks_metadata=[],
                processing_time=processing_time,
                chunks_created=0,
                confidence_score=0.1,
                errors=[str(e)],
                warnings=["Fallback-Metadaten verwendet"]
            )
    
    async def _extract_document_metadata(self,
                                       content: str,
                                       document_title: Optional[str] = None,
                                       document_type_hint: Optional[str] = None) -> EnhancedDocumentMetadata:
        """Extrahiert Dokumentmetadaten mit Enhanced Prompts"""
        
        if not self.ai_provider:
            logger.error("❌ AI Provider nicht verfügbar")
            return create_fallback_metadata(document_title or "Unknown Document")
        
        try:
            # 1. Build Enhanced Prompt
            prompt = build_enhanced_extraction_prompt(
                content, document_title, document_type_hint
            )
            
            # 2. Optimize for AI Model
            prompt = optimize_prompt_for_model(prompt, self.ai_provider_name)
            
            # 3. AI Request with Temperature=0
            prompt_config = get_prompt_config()
            
            ai_response = await self.ai_provider.generate_response(
                prompt=prompt,
                **prompt_config
            )
            
            # 4. Parse with Enhanced JSON Parser
            metadata = self.json_parser.parse_enhanced_metadata(
                ai_response, 
                document_title or "Unknown Document"
            )
            
            logger.info(f"✅ Dokumentmetadaten extrahiert mit Konfidenz: {metadata.ai_confidence}")
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Dokumentmetadaten-Extraktion fehlgeschlagen: {e}")
            return create_fallback_metadata(document_title or "Unknown Document")
    
    async def _extract_chunks_metadata(self,
                                     content: str,
                                     document_metadata: EnhancedDocumentMetadata) -> List[EnhancedChunkMetadata]:
        """Extrahiert Chunk-Metadaten für Advanced RAG Integration"""
        
        if not self.ai_provider:
            logger.warning("❌ AI Provider nicht verfügbar für Chunk-Metadaten")
            return []
        
        try:
            # 1. Content Chunking (einfache Implementierung)
            chunks = self._create_content_chunks(content)
            
            # 2. Parallel Chunk Analysis
            chunk_tasks = []
            for i, chunk_content in enumerate(chunks):
                task = self._analyze_single_chunk(
                    chunk_content, i, document_metadata
                )
                chunk_tasks.append(task)
            
            # 3. Execute Parallel Analysis
            chunks_metadata = await asyncio.gather(*chunk_tasks, return_exceptions=True)
            
            # 4. Filter successful results
            valid_chunks = []
            for chunk_meta in chunks_metadata:
                if isinstance(chunk_meta, EnhancedChunkMetadata):
                    valid_chunks.append(chunk_meta)
                elif isinstance(chunk_meta, Exception):
                    logger.warning(f"⚠️ Chunk-Analyse fehlgeschlagen: {chunk_meta}")
            
            logger.info(f"✅ {len(valid_chunks)} Chunk-Metadaten erstellt")
            return valid_chunks
            
        except Exception as e:
            logger.error(f"❌ Chunk-Metadaten-Extraktion fehlgeschlagen: {e}")
            return []
    
    async def _analyze_single_chunk(self,
                                  chunk_content: str,
                                  chunk_index: int,
                                  document_metadata: EnhancedDocumentMetadata) -> EnhancedChunkMetadata:
        """Analysiert einzelnen Chunk mit AI"""
        
        try:
            # 1. Build Chunking Prompt
            prompt = build_chunking_prompt(
                chunk_content=chunk_content,
                document_title=document_metadata.title,
                document_type=document_metadata.document_type.value,
                section_title=None  # TODO: Section detection
            )
            
            # 2. AI Analysis
            prompt_config = get_prompt_config()
            ai_response = await self.ai_provider.generate_response(
                prompt=prompt,
                **prompt_config
            )
            
            # 3. Parse Response
            chunk_data = self.json_parser._extract_fields_with_regex(ai_response)
            
            # 4. Create Enhanced Chunk Metadata
            chunk_metadata = EnhancedChunkMetadata(
                document_id=0,  # Will be set later
                chunk_index=chunk_index,
                document_title=document_metadata.title,
                document_type=document_metadata.document_type,
                document_version=document_metadata.version,
                section_title=chunk_data.get('section_title'),
                paragraph_number=chunk_data.get('paragraph_number'),
                word_count=len(chunk_content.split()),
                keywords=[
                    EnhancedKeyword(
                        term=kw.get('term', ''),
                        importance=KeywordImportance(kw.get('importance', 'MEDIUM')),
                        category=kw.get('category', 'general'),
                        confidence=kw.get('confidence', 0.7)
                    ) for kw in chunk_data.get('keywords', [])
                ],
                importance_score=chunk_data.get('importance_score', 0.5),
                interest_groups=chunk_data.get('interest_groups', [])
            )
            
            return chunk_metadata
            
        except Exception as e:
            logger.error(f"❌ Chunk-Analyse fehlgeschlagen für Index {chunk_index}: {e}")
            
            # Fallback Chunk Metadata
            return EnhancedChunkMetadata(
                document_id=0,
                chunk_index=chunk_index,
                document_title=document_metadata.title,
                document_type=document_metadata.document_type,
                document_version=document_metadata.version,
                word_count=len(chunk_content.split()),
                importance_score=0.3,
                ai_methodology="fallback_chunk_analysis"
            )
    
    def _create_content_chunks(self, content: str, chunk_size: int = 1000) -> List[str]:
        """Erstellt Content-Chunks (einfache Implementierung)"""
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk + paragraph) <= chunk_size:
                current_chunk += paragraph + '\n\n'
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + '\n\n'
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Gibt Performance-Metriken zurück"""
        total = self.performance_metrics['total_extractions']
        if total > 0:
            success_rate = self.performance_metrics['successful_extractions'] / total * 100
        else:
            success_rate = 0
        
        return {
            **self.performance_metrics,
            'success_rate': f"{success_rate:.1f}%",
            'ai_provider': self.ai_provider_name,
            'json_parser_metrics': self.json_parser.get_performance_metrics()
        }


# Global Enhanced Metadata Extractor
_enhanced_extractor = None

def get_enhanced_extractor(ai_provider: str = "openai") -> EnhancedMetadataExtractor:
    """Gibt globale Enhanced Metadata Extractor Instanz zurück"""
    global _enhanced_extractor
    if _enhanced_extractor is None:
        _enhanced_extractor = EnhancedMetadataExtractor(ai_provider)
    return _enhanced_extractor


# Convenience Functions
async def extract_enhanced_metadata(content: str,
                                  document_title: Optional[str] = None,
                                  document_type_hint: Optional[str] = None,
                                  ai_provider: str = "openai") -> EnhancedMetadataResponse:
    """
    🎯 Convenience Function für Enhanced Metadata Extraction
    
    Args:
        content: Dokumentinhalt
        document_title: Optional - Dokumenttitel
        document_type_hint: Optional - Dokumenttyp-Hinweis
        ai_provider: AI Provider ("openai" oder "gemini")
        
    Returns:
        EnhancedMetadataResponse: Vollständige Metadaten-Response
    """
    extractor = get_enhanced_extractor(ai_provider)
    return await extractor.extract_enhanced_metadata(
        content, document_title, document_type_hint
    )


async def extract_document_metadata_only(content: str,
                                       document_title: Optional[str] = None,
                                       ai_provider: str = "openai") -> EnhancedDocumentMetadata:
    """
    📊 Extrahiert nur Dokumentmetadaten (ohne Chunks)
    
    Args:
        content: Dokumentinhalt
        document_title: Optional - Dokumenttitel
        ai_provider: AI Provider ("openai" oder "gemini")
        
    Returns:
        EnhancedDocumentMetadata: Dokumentmetadaten
    """
    extractor = get_enhanced_extractor(ai_provider)
    return await extractor._extract_document_metadata(content, document_title)


def validate_enhanced_metadata(metadata: EnhancedDocumentMetadata) -> Dict[str, Any]:
    """
    🔍 Validiert Enhanced Metadata
    
    Args:
        metadata: Zu validierende Metadaten
        
    Returns:
        Dict mit Validierungsergebnissen
    """
    validation_results = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'quality_score': 0.0
    }
    
    try:
        # Basic Validation
        if not metadata.title or len(metadata.title.strip()) < 2:
            validation_results['errors'].append("Titel zu kurz oder leer")
            validation_results['is_valid'] = False
        
        if metadata.ai_confidence < 0.3:
            validation_results['warnings'].append("Niedrige AI-Konfidenz")
        
        if not metadata.primary_keywords:
            validation_results['warnings'].append("Keine primären Keywords gefunden")
        
        # Quality Score Calculation
        quality_factors = [
            metadata.quality_scores.overall,
            metadata.ai_confidence,
            len(metadata.primary_keywords) / 10,  # Normalize to 0-1
            1.0 if metadata.description else 0.0,
            1.0 if metadata.compliance_areas else 0.0
        ]
        
        validation_results['quality_score'] = sum(quality_factors) / len(quality_factors)
        
    except Exception as e:
        validation_results['errors'].append(f"Validierungsfehler: {str(e)}")
        validation_results['is_valid'] = False
    
    return validation_results


# Export wichtiger Funktionen
__all__ = [
    "EnhancedMetadataExtractor",
    "extract_enhanced_metadata",
    "extract_document_metadata_only",
    "validate_enhanced_metadata",
    "get_enhanced_extractor"
]