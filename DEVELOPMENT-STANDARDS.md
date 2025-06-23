# 🔧 Development Standards - KI-QMS

**Version:** 2.0.0  
**Letzte Aktualisierung:** Dezember 2024  
**Status:** ✅ Production Ready  

## 📋 Inhaltsverzeichnis

1. [🧭 Code-Qualitäts-Standards](#-code-qualitäts-standards)
2. [📝 Dokumentations-Standards](#-dokumentations-standards)
3. [🔒 Sicherheits-Guidelines](#-sicherheits-guidelines)
4. [🧪 Testing-Standards](#-testing-standards)
5. [🚀 Performance-Best-Practices](#-performance-best-practices)
6. [🔄 Git-Workflow](#-git-workflow)
7. [🛠️ Development-Tools](#️-development-tools)
8. [📊 Code-Review-Prozess](#-code-review-prozess)

---

## 🧭 Code-Qualitäts-Standards

### **PEP 8 Compliance**
Alle Python-Code muss den [PEP 8](https://peps.python.org/pep-0008/) Standards entsprechen.

```python
# ✅ Korrekt
def calculate_document_score(
    document: Document, 
    interest_groups: List[str], 
    approval_level: int = 1
) -> float:
    """Berechnet den QM-Score für ein Dokument."""
    pass

# ❌ Falsch
def calculateDocumentScore(document,interest_groups,approval_level=1):
    pass
```

### **Type Hints - Vollständige Typisierung**
**PFLICHT:** Alle Funktionen, Methoden und Variablen müssen Type Hints haben.

```python
from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel

# ✅ Vollständige Type Hints
async def process_document_workflow(
    document_id: int,
    user: User,
    db: AsyncSession,
    approval_chain: List[str]
) -> WorkflowResult:
    """Verarbeitet einen Dokumenten-Workflow asynchron."""
    result: WorkflowResult = await workflow_engine.process(
        document_id=document_id,
        approver_groups=approval_chain,
        initiator=user
    )
    return result

# Pydantic Schemas mit strikter Typisierung
class DocumentCreateRequest(BaseModel):
    title: str
    content: str
    document_type: DocumentType
    interest_groups: List[str]
    priority: Priority = Priority.MEDIUM
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True
        validate_assignment = True
```

### **Error Handling - Strukturierte Ausnahmebehandlung**

```python
from app.exceptions import (
    DocumentNotFoundError,
    InsufficientPermissionsError,
    ValidationError
)

# ✅ Strukturierte Error Handling
async def update_document_status(
    document_id: int, 
    new_status: DocumentStatus,
    user: User,
    db: AsyncSession
) -> Document:
    """Aktualisiert den Dokumentenstatus mit vollständiger Validierung."""
    try:
        # Dokument validieren
        document = await get_document_by_id(db, document_id)
        if not document:
            raise DocumentNotFoundError(
                f"Dokument {document_id} nicht gefunden",
                document_id=document_id
            )
        
        # Berechtigung prüfen
        if not await user_has_approval_rights(user, document):
            raise InsufficientPermissionsError(
                f"User {user.email} hat keine Berechtigung für Dokument {document_id}",
                user_id=user.id,
                document_id=document_id,
                required_level=document.required_approval_level
            )
        
        # Status-Transition validieren
        if not is_valid_status_transition(document.status, new_status):
            raise ValidationError(
                f"Ungültige Status-Transition: {document.status} → {new_status}",
                current_status=document.status,
                target_status=new_status
            )
        
        # Update durchführen
        document.status = new_status
        document.updated_at = datetime.utcnow()
        document.updated_by_id = user.id
        
        await db.commit()
        await db.refresh(document)
        
        # Workflow-Engine benachrichtigen
        await workflow_engine.notify_status_change(document, user)
        
        return document
        
    except (DocumentNotFoundError, InsufficientPermissionsError, ValidationError):
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Unerwarteter Fehler bei Dokument-Update: {e}", exc_info=True)
        raise InternalServerError(f"Dokument-Update fehlgeschlagen: {str(e)}")
```

---

## 📝 Dokumentations-Standards

### **Google-Style Docstrings**
**PFLICHT:** Alle Funktionen und Klassen benötigen umfassende Docstrings.

```python
def analyze_document_compliance(
    document: Document,
    standards: List[ComplianceStandard],
    strict_mode: bool = True
) -> ComplianceReport:
    """Analysiert ein Dokument auf Compliance-Konformität.
    
    Führt eine umfassende Analyse des Dokuments gegen die angegebenen
    Compliance-Standards durch. Berücksichtigt ISO 13485, EU MDR und
    FDA 21 CFR Part 820 Anforderungen.
    
    Args:
        document: Das zu analysierende QM-Dokument
        standards: Liste der anzuwendenden Compliance-Standards
        strict_mode: Wenn True, werden strengere Validierungsregeln angewendet
                    Defaults to True für Produktionsumgebung
    
    Returns:
        ComplianceReport: Detaillierter Bericht mit:
            - compliance_score: Numerischer Score (0.0-1.0)
            - violations: Liste aller gefundenen Verstöße
            - recommendations: Verbesserungsvorschläge
            - standard_coverage: Abdeckung pro Standard
    
    Raises:
        DocumentNotFoundError: Wenn das Dokument nicht existiert
        InvalidStandardError: Wenn ein unbekannter Standard übergeben wird
        ValidationError: Bei fehlerhaften Eingabeparametern
    
    Example:
        >>> document = await get_document(1)
        >>> standards = [ISO_13485, EU_MDR]
        >>> report = analyze_document_compliance(document, standards)
        >>> print(f"Score: {report.compliance_score:.2%}")
        Score: 87.50%
    
    Note:
        Diese Funktion ist CPU-intensiv für große Dokumente.
        Für Batch-Verarbeitung verwenden Sie analyze_documents_batch().
    """
    pass

class WorkflowEngine:
    """Intelligente Workflow-Engine für QM-Dokumenten-Freigaben.
    
    Die WorkflowEngine automatisiert den kompletten Freigabeprozess für
    QM-Dokumente basierend auf Dokumenttyp, Interessengruppen und
    Compliance-Anforderungen.
    
    Attributes:
        interest_groups: Dict der 13 konfigurierten Interessengruppen
        approval_chains: Vordefinierte Freigabeketten nach Dokumenttyp
        notification_service: Service für E-Mail/System-Benachrichtigungen
        audit_logger: Logger für Compliance-Audit-Trail
    
    Example:
        >>> engine = WorkflowEngine()
        >>> result = await engine.start_approval_process(document, user)
        >>> print(f"Workflow gestartet: {result.workflow_id}")
    """
    
    async def start_approval_process(
        self,
        document: Document,
        initiator: User
    ) -> WorkflowResult:
        """Startet den automatischen Freigabeprozess für ein Dokument.
        
        Args:
            document: Das freizugebende Dokument
            initiator: User der den Freigabeprozess startet
        
        Returns:
            WorkflowResult: Ergebnis mit Workflow-ID und nächsten Schritten
        
        Raises:
            InsufficientPermissionsError: User darf Workflow nicht starten
            InvalidDocumentStateError: Dokument ist nicht freigabebereit
        """
        pass
```

### **Code-Kommentare**

```python
# ✅ Gute Kommentare - erklären WARUM, nicht WAS
class DocumentProcessor:
    def __init__(self):
        # Cache für häufig verwendete Regex-Pattern um Performance zu verbessern
        # bei großen Dokumenten (>10MB) bis zu 60% Geschwindigkeitssteigerung
        self._regex_cache: Dict[str, re.Pattern] = {}
        
        # Maximale Dateigröße für In-Memory-Verarbeitung
        # Größere Dateien werden gestreamt um Memory-Probleme zu vermeiden
        self.max_memory_size = 50 * 1024 * 1024  # 50MB
    
    def extract_text(self, file_path: str) -> str:
        """Extrahiert Text aus verschiedenen Dateiformaten."""
        # PDF-Extraktion mit PyPDF2 ist für einfache PDFs ausreichend
        # Für komplexe PDFs mit Bildern/Tabellen würde pdfplumber bessere Ergebnisse liefern
        # aber deutlich mehr Abhängigkeiten und Ressourcen benötigen
        if file_path.endswith('.pdf'):
            return self._extract_pdf_text(file_path)
```

---

## 🔒 Sicherheits-Guidelines

### **Input-Validierung und Sanitization**

```python
from pydantic import validator, ValidationError
import bleach
import re

class DocumentUploadRequest(BaseModel):
    title: str
    content: str
    file_type: str
    
    @validator('title')
    def validate_title(cls, v):
        """Validiert und sanitized Dokumenttitel."""
        # HTML/Script-Tags entfernen
        clean_title = bleach.clean(v, tags=[], strip=True)
        
        # Länge prüfen
        if len(clean_title) < 3:
            raise ValueError('Titel muss mindestens 3 Zeichen lang sein')
        if len(clean_title) > 200:
            raise ValueError('Titel darf maximal 200 Zeichen lang sein')
        
        # Gefährliche Zeichen entfernen
        safe_title = re.sub(r'[<>"/\\|?*]', '', clean_title)
        
        return safe_title.strip()
    
    @validator('file_type')
    def validate_file_type(cls, v):
        """Strenge Validierung erlaubter Dateitypen."""
        allowed_types = {
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'text/markdown'
        }
        
        if v not in allowed_types:
            raise ValueError(f'Dateityp {v} ist nicht erlaubt')
        
        return v

# File Upload Security
async def validate_uploaded_file(file: UploadFile) -> None:
    """Umfassende Sicherheitsprüfung für Upload-Dateien."""
    
    # Dateigröße prüfen
    if file.size > 100 * 1024 * 1024:  # 100MB
        raise ValidationError("Datei zu groß (max. 100MB)")
    
    # Magic Number Validation (echte Dateityp-Prüfung)
    file_signature = await file.read(4)
    await file.seek(0)  # Reset file pointer
    
    pdf_signatures = [b'%PDF']
    docx_signatures = [b'PK\x03\x04']  # ZIP-based formats
    
    is_valid_file = any(
        file_signature.startswith(sig) 
        for sig in pdf_signatures + docx_signatures
    )
    
    if not is_valid_file:
        raise ValidationError("Ungültiger Dateityp (Magic Number Check)")
    
    # Virus-Scan würde hier implementiert werden
    # await virus_scanner.scan_file(file)
```

### **Authentication & Authorization**

```python
from functools import wraps
from app.auth import get_current_user, verify_permissions

def require_permission(permission: str, resource_type: str = None):
    """Decorator für rollenbasierte Zugriffskontrolle."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Current user aus Token extrahieren
            user = await get_current_user(kwargs.get('token'))
            
            # Permission prüfen
            if not await verify_permissions(user, permission, resource_type):
                raise InsufficientPermissionsError(
                    f"User {user.email} hat keine {permission} Berechtigung",
                    required_permission=permission,
                    user_id=user.id
                )
            
            # User in kwargs einfügen für nachgelagerte Funktionen
            kwargs['current_user'] = user
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@require_permission('document:approve', 'qm_document')
async def approve_document(document_id: int, current_user: User) -> Document:
    """Nur Users mit document:approve Permission können aufrufen."""
    pass
```

---

## 🧪 Testing-Standards

### **Minimum Test Coverage: 80%**
**Kritische Pfade: 90%+ Coverage erforderlich**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.models import Document, User, DocumentStatus
from app.services import DocumentService
from app.exceptions import DocumentNotFoundError

class TestDocumentService:
    """Comprehensive test suite für DocumentService."""
    
    @pytest.fixture
    async def mock_db(self):
        """Mock database session."""
        db = AsyncMock()
        yield db
    
    @pytest.fixture
    def sample_user(self):
        """Standard test user."""
        return User(
            id=1,
            email="test@company.com",
            full_name="Test User",
            is_active=True
        )
    
    @pytest.fixture
    def sample_document(self):
        """Standard test document."""
        return Document(
            id=1,
            title="Test QM-Handbuch",
            content="Test content",
            document_type=DocumentType.QM_MANUAL,
            status=DocumentStatus.DRAFT,
            created_by_id=1
        )
    
    # Unit Tests
    async def test_get_document_success(self, mock_db, sample_document):
        """Test successful document retrieval."""
        # Arrange
        mock_db.execute.return_value.scalar_one_or_none.return_value = sample_document
        service = DocumentService(mock_db)
        
        # Act
        result = await service.get_document(1)
        
        # Assert
        assert result == sample_document
        assert result.id == 1
        assert result.title == "Test QM-Handbuch"
    
    async def test_get_document_not_found(self, mock_db):
        """Test document not found scenario."""
        # Arrange
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        service = DocumentService(mock_db)
        
        # Act & Assert
        with pytest.raises(DocumentNotFoundError) as exc_info:
            await service.get_document(999)
        
        assert exc_info.value.document_id == 999
        assert "nicht gefunden" in str(exc_info.value)
    
    # Integration Tests
    @pytest.mark.integration
    async def test_document_workflow_integration(self, test_db, sample_user):
        """Integration test für kompletten Dokumenten-Workflow."""
        # Test erstellt echte DB-Verbindung und testet End-to-End
        service = DocumentService(test_db)
        
        # 1. Dokument erstellen
        doc_data = DocumentCreateRequest(
            title="Integration Test Doc",
            content="Test content",
            document_type=DocumentType.SOP
        )
        document = await service.create_document(doc_data, sample_user)
        
        # 2. Status ändern
        updated_doc = await service.update_status(
            document.id, 
            DocumentStatus.REVIEWED, 
            sample_user
        )
        
        # 3. Validierung
        assert updated_doc.status == DocumentStatus.REVIEWED
        assert updated_doc.updated_by_id == sample_user.id
    
    # Performance Tests
    @pytest.mark.performance
    async def test_bulk_document_processing_performance(self, test_db):
        """Performance test für Bulk-Operationen."""
        import time
        
        service = DocumentService(test_db)
        documents = []
        
        # 1000 Dokumente erstellen und messen
        start_time = time.time()
        
        for i in range(1000):
            doc = await service.create_document(
                DocumentCreateRequest(
                    title=f"Perf Test Doc {i}",
                    content="Test content",
                    document_type=DocumentType.OTHER
                ),
                sample_user
            )
            documents.append(doc)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Performance-Anforderung: < 10 Sekunden für 1000 Dokumente
        assert processing_time < 10.0, f"Bulk processing zu langsam: {processing_time}s"
        assert len(documents) == 1000

# Mocking Best Practices
class TestWorkflowEngine:
    """Tests mit umfassendem Mocking."""
    
    @pytest.fixture
    def mock_notification_service(self):
        """Mock für NotificationService."""
        mock = AsyncMock()
        mock.send_approval_notification.return_value = True
        mock.send_status_update.return_value = True
        return mock
    
    async def test_workflow_with_mocked_dependencies(
        self, 
        mock_db, 
        mock_notification_service,
        sample_document,
        sample_user
    ):
        """Test mit vollständig gemockten Abhängigkeiten."""
        # Workflow Engine mit Mocks initialisieren
        engine = WorkflowEngine(
            db=mock_db,
            notification_service=mock_notification_service
        )
        
        # Mock DB responses
        mock_db.execute.return_value.scalar_one_or_none.return_value = sample_document
        
        # Test ausführen
        result = await engine.start_approval_process(sample_document, sample_user)
        
        # Assertions
        assert result.success is True
        mock_notification_service.send_approval_notification.assert_called_once()
```

### **Test-Konfiguration**

```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow running tests

# conftest.py - Shared Test Configuration
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.database import get_database

@pytest.fixture(scope="session")
def event_loop():
    """Event loop für async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///test.db")
    
    # Tabellen erstellen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Session für Test
    async with AsyncSession(engine) as session:
        yield session
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

---

## 🚀 Performance-Best-Practices

### **Async/Await Patterns**

```python
# ✅ Richtige Async-Implementierung
async def process_multiple_documents(
    document_ids: List[int],
    db: AsyncSession
) -> List[ProcessingResult]:
    """Verarbeitet mehrere Dokumente parallel."""
    
    # Parallele Verarbeitung mit asyncio.gather
    tasks = [
        process_single_document(doc_id, db) 
        for doc_id in document_ids
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Fehlerbehandlung für einzelne Tasks
    successful_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Fehler bei Dokument {document_ids[i]}: {result}")
        else:
            successful_results.append(result)
    
    return successful_results

# Database Connection Pooling
async def get_documents_optimized(
    db: AsyncSession,
    limit: int = 100,
    offset: int = 0
) -> List[Document]:
    """Optimierte Datenbankabfrage mit Eager Loading."""
    
    # Eager Loading um N+1 Queries zu vermeiden
    query = (
        select(Document)
        .options(
            selectinload(Document.created_by),
            selectinload(Document.interest_groups),
            selectinload(Document.approvals)
        )
        .limit(limit)
        .offset(offset)
    )
    
    result = await db.execute(query)
    return result.scalars().all()
```

### **Caching-Strategien**

```python
from functools import lru_cache
import redis.asyncio as redis
import json
from typing import Optional

class CacheService:
    """Intelligenter Cache-Service für Performance-Optimierung."""
    
    def __init__(self):
        self.redis_client = redis.from_url("redis://localhost:6379")
    
    @lru_cache(maxsize=1000)
    def get_interest_groups_cached(self) -> List[InterestGroup]:
        """In-Memory Cache für statische Interessengruppen."""
        # Diese Daten ändern sich selten, daher LRU-Cache ideal
        return self._load_interest_groups_from_db()
    
    async def get_document_cache(self, document_id: int) -> Optional[Document]:
        """Redis Cache für häufig abgerufene Dokumente."""
        cache_key = f"document:{document_id}"
        
        # Cache lookup
        cached_data = await self.redis_client.get(cache_key)
        if cached_data:
            # Cache hit
            data = json.loads(cached_data)
            return Document.parse_obj(data)
        
        return None
    
    async def set_document_cache(
        self, 
        document: Document, 
        ttl: int = 3600
    ) -> None:
        """Setzt Dokument in Redis Cache mit TTL."""
        cache_key = f"document:{document.id}"
        
        # Nur cacheable Dokumente speichern (keine DRAFT-Status)
        if document.status != DocumentStatus.DRAFT:
            await self.redis_client.setex(
                cache_key,
                ttl,
                document.json()
            )
```

### **Database-Optimierung**

```python
# Optimierte Queries mit SQLAlchemy
async def get_user_dashboard_data(
    user_id: int, 
    db: AsyncSession
) -> DashboardData:
    """Optimierte Dashboard-Datenabfrage mit einem Query."""
    
    # Einzelner komplexer Query statt mehrere kleine
    query = text("""
        SELECT 
            COUNT(CASE WHEN d.status = 'DRAFT' THEN 1 END) as draft_count,
            COUNT(CASE WHEN d.status = 'REVIEWED' THEN 1 END) as reviewed_count,
            COUNT(CASE WHEN d.status = 'APPROVED' THEN 1 END) as approved_count,
            COUNT(CASE WHEN d.created_at > NOW() - INTERVAL '7 days' THEN 1 END) as recent_count
        FROM documents d
        JOIN user_group_memberships ugm ON ugm.user_id = :user_id
        JOIN document_interest_groups dig ON dig.document_id = d.id 
                                          AND dig.interest_group_id = ugm.interest_group_id
        WHERE ugm.is_active = true
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    row = result.fetchone()
    
    return DashboardData(
        draft_documents=row.draft_count,
        reviewed_documents=row.reviewed_count,
        approved_documents=row.approved_count,
        recent_documents=row.recent_count
    )

# Connection Pool Configuration
engine = create_async_engine(
    DATABASE_URL,
    # Pool-Einstellungen für Production
    pool_size=20,              # 20 permanente Verbindungen
    max_overflow=30,           # +30 bei Bedarf
    pool_pre_ping=True,        # Verbindung vor Nutzung testen
    pool_recycle=3600,         # Verbindungen nach 1h erneuern
    echo=False                 # SQL-Logging in Production aus
)
```

---

## 🔄 Git-Workflow

### **Branch-Naming-Konventionen**

```bash
# Feature Branches
feature/qms-document-approval-chain
feature/user-role-management
feature/iso-13485-compliance-check

# Bugfix Branches
bugfix/login-session-timeout
bugfix/document-upload-validation

# Hotfix Branches (Production)
hotfix/security-vulnerability-fix
hotfix/critical-db-connection-leak

# Release Branches
release/v2.1.0
release/v2.1.1-hotfix
```

### **Commit-Message-Standard (Conventional Commits)**

```bash
# Format: <type>(<scope>): <description>

# Examples
feat(auth): implement JWT refresh token mechanism
fix(upload): resolve file size validation for large PDFs
docs(api): update OpenAPI schema for user endpoints
test(workflow): add integration tests for approval chain
perf(db): optimize document query with eager loading
refactor(models): extract common base model functionality
security(auth): fix potential SQL injection in user search

# Breaking Changes
feat(api)!: redesign document status API with new enum values

BREAKING CHANGE: Document status values changed from strings to enum.
Migration required for existing installations.
```

### **Pre-Commit Hooks Configuration**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, backend/app, -f, json, -o, security-report.json]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest tests/ -v --tb=short
        language: system
        types: [python]
        pass_filenames: false
```

---

## 🛠️ Development-Tools

### **IDE-Konfiguration (VS Code)**

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests",
        "-v",
        "--tb=short"
    ],
    "files.associations": {
        "*.md": "markdown"
    },
    "sqltools.connections": [
        {
            "name": "KI-QMS Development",
            "driver": "SQLite",
            "database": "./backend/qms_mvp.db"
        }
    ]
}

// .vscode/extensions.json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "charliermarsh.ruff",
        "ms-python.mypy-type-checker",
        "ms-vscode.vscode-json",
        "ms-python.pytest",
        "mtxr.sqltools",
        "mtxr.sqltools-driver-sqlite"
    ]
}
```

### **Development Environment Setup**

```bash
# .env.development
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite+aiosqlite:///./qms_mvp.db
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Test Environment
TESTING=True
TEST_DATABASE_URL=sqlite+aiosqlite:///./test.db

# Performance Monitoring
ENABLE_PROFILING=True
PROFILE_OUTPUT_DIR=./performance_reports/
```

---

## 📊 Code-Review-Prozess

### **Review-Checklist**

#### **🔍 Code-Qualität**
- [ ] **Type Hints:** Vollständige Typisierung vorhanden?
- [ ] **Docstrings:** Google-Style Dokumentation für alle öffentlichen Funktionen?
- [ ] **Error Handling:** Strukturierte Ausnahmebehandlung implementiert?
- [ ] **PEP 8:** Code-Style-Konformität geprüft?
- [ ] **Complexity:** Funktionen haben max. 15 Zeilen Code?

#### **🔒 Sicherheit**
- [ ] **Input Validation:** Alle User-Eingaben validiert?
- [ ] **SQL Injection:** Parametrisierte Queries verwendet?
- [ ] **XSS Prevention:** HTML-Sanitization implementiert?
- [ ] **File Upload:** Sichere Upload-Validierung vorhanden?
- [ ] **Secrets:** Keine Hardcoded-Credentials im Code?

#### **🧪 Testing**
- [ ] **Unit Tests:** Neue Funktionalität getestet?
- [ ] **Test Coverage:** Mindestens 80% Coverage erreicht?
- [ ] **Edge Cases:** Grenzfälle abgedeckt?
- [ ] **Integration Tests:** API-Endpoints getestet?
- [ ] **Error Scenarios:** Fehlerbehandlung getestet?

#### **🚀 Performance**
- [ ] **Database Queries:** N+1 Queries vermieden?
- [ ] **Async/Await:** Async-Pattern korrekt implementiert?
- [ ] **Caching:** Sinnvolle Cache-Strategien eingesetzt?
- [ ] **Memory Usage:** Keine Memory-Leaks bei großen Dateien?

#### **📝 Dokumentation**
- [ ] **API Documentation:** OpenAPI Schema aktualisiert?
- [ ] **README:** Breaking Changes dokumentiert?
- [ ] **Migration Guide:** Bei Schema-Änderungen erstellt?
- [ ] **Compliance:** QM-relevante Änderungen dokumentiert?

### **Review-Approval-Prozess**

```bash
# 1. Feature Branch erstellen
git checkout -b feature/new-compliance-check

# 2. Entwicklung mit Tests
# ... Code schreiben ...
pytest tests/ --cov=app --cov-fail-under=80

# 3. Pre-commit hooks ausführen
pre-commit run --all-files

# 4. Pull Request erstellen
# Template automatisch mit Checklist

# 5. Review-Anforderungen:
# - Mindestens 2 Approvals für kritische Features
# - 1 Approval für Bugfixes
# - Security-Review für alle Auth/Permission-Änderungen

# 6. CI/CD Pipeline muss grün sein
# - Alle Tests bestanden
# - Security Scan bestanden
# - Performance Benchmarks OK

# 7. Merge nach Approval
git checkout main
git merge --no-ff feature/new-compliance-check
```

---

## ⚡ Quick Reference

### **Daily Development Workflow**

```bash
# 1. Aktueller Stand
git pull origin main
pip install -r requirements-dev.txt

# 2. Branch erstellen
git checkout -b feature/your-feature-name

# 3. Development starten
cd backend
python -m uvicorn app.main:app --reload

# 4. Tests während Entwicklung
pytest tests/test_your_module.py -v

# 5. Code Quality Check
black app/
ruff check app/
mypy app/

# 6. Vollständige Test-Suite
pytest tests/ --cov=app --cov-report=html

# 7. Commit mit Conventional Commits
git commit -m "feat(module): add new functionality"

# 8. Push und PR erstellen
git push origin feature/your-feature-name
```

### **Debugging-Commands**

```bash
# API Testing
curl -X GET "http://localhost:8000/docs"  # Swagger UI
curl -X GET "http://localhost:8000/health"  # Health Check

# Database Debugging
sqlite3 backend/qms_mvp.db
.tables
.schema documents

# Performance Profiling
python -m cProfile -o profile.stats your_script.py
snakeviz profile.stats  # Visualisierung
```

---

**Letzte Aktualisierung:** Dezember 2024  
**Version:** 2.0.0  
**Verantwortlich:** KI-QMS Development Team  

Für Fragen oder Verbesserungsvorschläge: [GitHub Issues](https://github.com/your-org/ki-qms/issues) 