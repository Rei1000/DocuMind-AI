# 📡 KI-QMS API DOCUMENTATION - Version 3.1.0

> **Stand:** 2. Juli 2025 | **Status:** ✅ Produktionsbereit  
> **Backend:** FastAPI | **Vector DB:** Qdrant | **AI-Providers:** OpenAI, Gemini, Ollama

---

## 🚀 **ÜBERBLICK**

Die KI-QMS API bietet eine vollständige REST-Schnittstelle für das intelligente Qualitätsmanagementsystem. Version 3.1.0 bringt fortschrittliche RAG-Funktionen, Multi-Provider AI-Support und Enterprise-Grade-Features.

### **🔗 Basis-URLs**
- **Backend:** `http://localhost:8000`  
- **API Docs:** `http://localhost:8000/docs`
- **Redoc:** `http://localhost:8000/redoc`

---

## 🏗️ **SYSTEM ARCHITEKTUR - v3.1.0**

### **🤖 AI-Provider System**
```
┌─ OpenAI GPT-4o-mini ────┐
├─ Google Gemini Flash ───┤  ──→ ai_engine.py ──→ Unified AI Interface
├─ Ollama (Mistral 7B) ───┤
└─ Regel-basiert ─────────┘
```

### **🧠 Advanced RAG Engine**
```
┌─ Qdrant Vector DB ──────┐
├─ Hierarchical Chunking ─┤  ──→ advanced_rag_engine.py ──→ Enterprise RAG
├─ OpenAI Embeddings ─────┤
└─ LangChain Integration ─┘
```

### **📊 Fallback Strategy**
```
Advanced RAG ──(fallback)──→ Qdrant RAG ──(fallback)──→ Rule-based
```

---

## 🔑 **AUTHENTICATION**

### **Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@ki-qms.de",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_info": {
    "id": 1,
    "email": "admin@ki-qms.de",
    "full_name": "QMS Administrator",
    "approval_level": 5,
    "is_qms_admin": true
  }
}
```

### **Authorization Header**
```http
Authorization: Bearer {access_token}
```

---

## 📄 **DOKUMENT-MANAGEMENT**

### **🔄 Intelligenter Upload mit Advanced AI**
```http
POST /api/documents/with-file
Content-Type: multipart/form-data
Authorization: Bearer {token}

title: "ISO 13485 Implementierung"
document_type: "QM_MANUAL"  
creator_id: 1
version: "1.0"
ai_model: "openai_4o_mini"  # OpenAI, Gemini, Ollama
enable_debug: "false"
file: {binary_data}
```

**Response - Vollständiger AI-Upload:**
```json
{
  "id": 123,
  "title": "ISO 13485 Implementierung v2.1 - Medizinprodukte QM",
  "document_type": "QM_MANUAL",
  "status": "DRAFT",
  "ai_analysis": {
    "document_type": "QM_MANUAL",
    "type_confidence": 95.7,
    "detected_language": "de",
    "language_confidence": 89.3,
    "norm_references": ["ISO 13485:2016", "MDR 2017/745"],
    "compliance_keywords": ["Qualitätsmanagementsystem", "Risikoanalyse"]
  },
  "rag_indexing": {
    "success": true,
    "chunks_created": 24,
    "processing_time": 2.3,
    "methodology": "hierarchical_chunking_with_enhancement"
  },
  "file_path": "/documents/uploads/iso_13485_impl_v21.pdf",
  "created_at": "2025-07-02T14:30:00Z"
}
```

### **📋 Dokumente abrufen**
```http
GET /api/documents?limit=20&document_type=QM_MANUAL&status=APPROVED
Authorization: Bearer {token}
```

### **🔍 Dokument-Suche**
```http
GET /api/documents/search/{query}
Authorization: Bearer {token}
```

---

## 🧠 **ADVANCED RAG SYSTEM**

### **💬 Intelligenter Chat mit Dokumenten**
```http
POST /api/rag/chat
Content-Type: application/json
Authorization: Bearer {token}

{
  "query": "Wie implementiere ich ISO 13485 Risikoanalyse?",
  "max_results": 5,
  "include_sources": true
}
```

**Response:**
```json
{
  "success": true,
  "query": "Wie implementiere ich ISO 13485 Risikoanalyse?",
  "answer": "Für die ISO 13485 Risikoanalyse sind folgende Schritte erforderlich:\n\n1. **Risiko-Identifikation**: Systematische Erfassung aller potentiellen Gefährdungen...",
  "confidence": 0.94,
  "processing_time": 1.87,
  "sources": [
    {
      "document_id": 123,
      "document_title": "ISO 13485 Implementierung v2.1",
      "chunk_content": "Die Risikoanalyse nach ISO 14971 ist ein zentraler Bestandteil...",
      "relevance_score": 0.95,
      "page_reference": "Seite 12-15"
    }
  ],
  "methodology": "advanced_rag_with_hierarchy"
}
```

### **🔍 Semantische Dokumenten-Suche**
```http
GET /api/rag/search?query=Reklamationsbehandlung&max_results=10
Authorization: Bearer {token}
```

### **📊 RAG System Status**
```http
GET /api/rag/status
```

**Response:**
```json
{
  "system_status": "OPERATIONAL",
  "vector_db": "Qdrant",
  "embedding_model": "OpenAI text-embedding-3-small",
  "total_documents": 127,
  "total_chunks": 3456,
  "collections": {
    "qms_documents": {
      "documents": 127,
      "vectors": 3456,
      "last_updated": "2025-07-02T14:30:00Z"
    }
  },
  "performance": {
    "avg_query_time": 0.23,
    "uptime": "99.97%"
  }
}
```

---

## 🤖 **AI-PROVIDER SYSTEM**

### **🧪 Provider-Tests**
```http
POST /api/ai/test-provider
Content-Type: application/json

{
  "provider": "openai_4o_mini",
  "test_text": "Erkläre mir ISO 13485 und warum es für Medizinprodukte wichtig ist."
}
```

**Response:**
```json
{
  "provider": "openai_4o_mini",
  "status": "SUCCESS",
  "response_time": 1.24,
  "response_text": "ISO 13485 ist ein internationaler Standard für Qualitätsmanagementsysteme von Medizinprodukten...",
  "cost_estimate": 0.0003,
  "model_info": {
    "model": "gpt-4o-mini",
    "max_tokens": 4096,
    "temperature": 0.1
  }
}
```

### **📊 Provider-Status abrufen**
```http
GET /api/ai/free-providers-status
```

**Response:**
```json
{
  "providers": {
    "openai_4o_mini": {
      "available": true,
      "status": "OPERATIONAL",
      "last_test": "2025-07-02T14:25:00Z",
      "avg_response_time": 1.2,
      "cost_per_1k_tokens": 0.00015,
      "rate_limit": "60/min"
    },
    "google_gemini": {
      "available": true, 
      "status": "OPERATIONAL",
      "daily_quota_used": 340,
      "daily_quota_limit": 1500,
      "free_tier": true
    },
    "ollama_mistral": {
      "available": true,
      "status": "OPERATIONAL", 
      "local_model": true,
      "model_size": "7B",
      "avg_response_time": 15.3
    }
  },
  "recommended": "openai_4o_mini",
  "fallback_strategy": ["openai_4o_mini", "google_gemini", "ollama_mistral", "rule_based"]
}
```

### **⚙️ Provider Details**
```http
GET /api/ai-providers/details
```

---

## 📈 **WORKFLOW & TASK MANAGEMENT**

### **🔄 Intelligente Workflows**
```http
POST /api/workflow/trigger-message
Content-Type: application/json
Authorization: Bearer {token}

{
  "message": "Neues ISO 13485 Dokument erfordert Freigabe-Workflow",
  "context": {
    "document_id": 123,
    "priority": "high"
  }
}
```

### **📋 Meine Aufgaben**
```http
GET /api/tasks/my-tasks?status=PENDING&priority=high
Authorization: Bearer {token}
```

---

## 🔧 **SYSTEM-ENDPUNKTE**

### **💊 Health Check**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "3.1.0",
  "timestamp": "2025-07-02T14:30:00Z",
  "database": "connected",
  "vector_db": "operational",
  "ai_providers": {
    "openai": "available",
    "gemini": "available", 
    "ollama": "available"
  },
  "uptime": 86400
}
```

### **📊 System-Informationen**
```http
GET /
```

---

## 🚨 **ERROR HANDLING**

### **Standard Error Response:**
```json
{
  "detail": "Dokument nicht gefunden",
  "status_code": 404,
  "timestamp": "2025-07-02T14:30:00Z",
  "path": "/api/documents/999",
  "request_id": "req_123abc"
}
```

### **Häufige HTTP Status Codes:**
- `200` - Success
- `201` - Created  
- `400` - Bad Request (Validation Error)
- `401` - Unauthorized (Token fehlt/ungültig)
- `403` - Forbidden (Keine Berechtigung)
- `404` - Not Found
- `422` - Unprocessable Entity (Validation Failed)
- `500` - Internal Server Error

---

## 🔒 **SECURITY & COMPLIANCE**

### **🛡️ Sicherheits-Features:**
- JWT-Token Authentication
- Role-based Access Control (RBAC)
- QMS Admin & Approval Level System
- API Rate Limiting
- Input Validation & Sanitization

### **📋 Compliance:**
- ISO 13485 konform
- GDPR/DSGVO Ready
- FDA 21 CFR Part 820 kompatibel
- MDR 2017/745 aligned

---

## 🚀 **VERSION 3.1.0 FEATURES**

### **🆕 Neue Features:**
- ✅ **Advanced RAG Engine** mit Hierarchical Chunking
- ✅ **Multi-Provider AI** (OpenAI, Gemini, Ollama)  
- ✅ **Qdrant Vector Database** Integration
- ✅ **Zentrale Prompt-Verwaltung**
- ✅ **Enhanced Document Upload** mit AI-Analyse
- ✅ **Intelligent Workflow Engine**
- ✅ **Real-time Provider Status**

### **🔄 Migrated:**
- ❌ HuggingFace → ✅ OpenAI GPT-4o-mini
- ❌ ChromaDB → ✅ Qdrant Vector DB
- ❌ Basic RAG → ✅ Advanced RAG Engine

### **⚠️ Deprecated (but still available):**
- Legacy RAG endpoints (`/api/rag/upload-document`, `/api/rag/chat-enhanced`)
- Hybrid AI endpoints (`/api/ai/hybrid-*`)

---

## 📚 **WEITERE RESSOURCEN**

- 📖 [OpenAPI Schema](http://localhost:8000/openapi.json)
- 🔍 [Interactive API Docs](http://localhost:8000/docs)  
- 📘 [ReDoc Documentation](http://localhost:8000/redoc)
- 🚀 [Advanced RAG Engine Analysis](./ADVANCED-RAG-ENGINE-ANALYSIS.md)
- 🔧 [Development Standards](./DEVELOPMENT-STANDARDS.md)

---

*📅 Letzte Aktualisierung: 2. Juli 2025 | Version 3.1.0* 