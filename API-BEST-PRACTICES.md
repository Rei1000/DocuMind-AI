# KI-QMS API Best Practices & Documentation Standards 🎯

> **Professional API design guidelines and documentation standards for enterprise-grade applications**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.3-blue.svg)](https://swagger.io/specification/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2.5+-red.svg)](https://docs.pydantic.dev/)

## 📋 Inhaltsverzeichnis

- [🎯 API Design Principles](#-api-design-principles)
- [📝 Documentation Standards](#-documentation-standards)
- [🔧 Endpoint Implementation](#-endpoint-implementation)
- [📊 Response Standards](#-response-standards)
- [🛡️ Error Handling](#️-error-handling)
- [🔐 Security Best Practices](#-security-best-practices)
- [⚡ Performance Guidelines](#-performance-guidelines)
- [🧪 Testing Standards](#-testing-standards)

## 🎯 API Design Principles

### RESTful Design

```python
# ✅ GOOD: RESTful resource-based URLs
GET    /api/documents              # List documents
POST   /api/documents              # Create document  
GET    /api/documents/{id}         # Get specific document
PUT    /api/documents/{id}         # Update document
DELETE /api/documents/{id}         # Delete document

# Resource relationships
GET    /api/documents/{id}/versions     # Get document versions
POST   /api/documents/{id}/approve      # Approve document
GET    /api/users/{id}/documents        # Get user's documents

# ❌ BAD: Non-RESTful action-based URLs
POST   /api/createDocument
POST   /api/updateDocument/{id}
GET    /api/getDocumentById/{id}
POST   /api/approveDocument/{id}
```

### HTTP Status Codes

```python
from fastapi import status

# Success responses
HTTP_200_OK                    # GET, PUT successful
HTTP_201_CREATED              # POST successful
HTTP_204_NO_CONTENT           # DELETE successful

# Client error responses  
HTTP_400_BAD_REQUEST          # Invalid request format
HTTP_401_UNAUTHORIZED         # Authentication required
HTTP_403_FORBIDDEN            # Insufficient permissions
HTTP_404_NOT_FOUND           # Resource doesn't exist
HTTP_409_CONFLICT            # Resource conflict (duplicate)
HTTP_422_UNPROCESSABLE_ENTITY # Validation error

# Server error responses
HTTP_500_INTERNAL_SERVER_ERROR # Unexpected server error
HTTP_503_SERVICE_UNAVAILABLE   # Service temporarily down
```

### API Versioning Strategy

```python
# URL versioning (recommended for KI-QMS)
@app.get("/api/v1/documents")
@app.get("/api/v2/documents")  # New version with breaking changes

# Header versioning (alternative)
@app.get("/api/documents")
async def get_documents(
    api_version: str = Header("1.0", alias="API-Version")
):
    if api_version == "2.0":
        return get_documents_v2()
    return get_documents_v1()
```

## 📝 Documentation Standards

### Comprehensive Endpoint Documentation

```python
@app.post(
    "/api/documents/{document_id}/compliance-analysis",
    response_model=ComplianceAnalysisResult,
    status_code=status.HTTP_201_CREATED,
    tags=["Document Analysis"],
    summary="Generate Compliance Analysis Report",
    description="""
    Perform comprehensive compliance analysis for a QMS document against selected standards.
    
    This endpoint analyzes document content against international standards including:
    - ISO 13485:2016 (Medical device quality management)
    - EU MDR 2017/745 (Medical device regulation)  
    - FDA 21 CFR Part 820 (Quality system regulation)
    - ISO 14971:2019 (Risk management for medical devices)
    
    **Analysis Process:**
    1. Document content extraction and preprocessing
    2. Multi-standard compliance checking
    3. Gap analysis and scoring
    4. Actionable recommendations generation
    5. Audit trail creation for regulatory compliance
    
    **Performance:** Typical analysis completes in 2-8 seconds for standard documents.
    
    **Caching:** Results are cached for 1 hour to improve performance for repeated analyses.
    """,
    response_description="Detailed compliance analysis with scores, gaps, and recommendations",
    responses={
        201: {
            "description": "Analysis completed successfully",
            "model": ComplianceAnalysisResult,
            "content": {
                "application/json": {
                    "example": {
                        "document_id": 123,
                        "analysis_id": "ca_789",
                        "overall_score": 87.5,
                        "compliance_by_standard": {
                            "ISO_13485": {"score": 92, "status": "COMPLIANT"},
                            "EU_MDR": {"score": 83, "status": "PARTIALLY_COMPLIANT"}
                        },
                        "gaps": [
                            {
                                "standard": "EU_MDR",
                                "clause": "Annex III, 6.1",
                                "description": "Clinical evidence documentation incomplete",
                                "severity": "HIGH",
                                "recommendation": "Include clinical evaluation report"
                            }
                        ],
                        "generated_at": "2024-12-20T10:30:00Z",
                        "analysis_duration_ms": 3245
                    }
                }
            }
        },
        400: {
            "description": "Invalid request parameters",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_standards": {
                            "summary": "Invalid standards specified",
                            "value": {
                                "detail": "Unknown standard codes: ['INVALID_STD']",
                                "error_code": "INVALID_STANDARDS",
                                "valid_standards": ["ISO_13485", "EU_MDR", "FDA_21_CFR_820"]
                            }
                        },
                        "invalid_depth": {
                            "summary": "Invalid analysis depth",
                            "value": {
                                "detail": "Analysis depth must be one of: BASIC, STANDARD, COMPREHENSIVE",
                                "error_code": "INVALID_ANALYSIS_DEPTH"
                            }
                        }
                    }
                }
            }
        },
        403: {
            "description": "Insufficient permissions",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User lacks 'compliance_analysis' permission",
                        "error_code": "INSUFFICIENT_PERMISSIONS",
                        "required_permission": "compliance_analysis"
                    }
                }
            }
        },
        404: {
            "description": "Document not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Document with ID 123 not found or not accessible",
                        "error_code": "DOCUMENT_NOT_FOUND"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "standards"],
                                "msg": "ensure this list has at least 1 items",
                                "type": "value_error.list.min_items"
                            }
                        ]
                    }
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Analysis rate limit exceeded. Try again in 60 seconds.",
                        "error_code": "RATE_LIMIT_EXCEEDED",
                        "retry_after": 60
                    }
                }
            }
        }
    },
    dependencies=[Depends(require_compliance_permission)]
)
async def analyze_document_compliance(
    document_id: int = Path(
        ..., 
        ge=1, 
        description="Unique identifier of the document to analyze",
        example=123
    ),
    analysis_request: ComplianceAnalysisRequest = Body(
        ...,
        description="Analysis configuration and parameters",
        example={
            "standards": ["ISO_13485", "EU_MDR"],
            "analysis_depth": "STANDARD",
            "include_recommendations": True,
            "priority_threshold": "MEDIUM"
        }
    ),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> ComplianceAnalysisResult:
    """
    Generate comprehensive compliance analysis for a QMS document.
    
    This endpoint performs detailed compliance analysis against international standards
    for medical device quality management. The analysis includes gap identification,
    scoring, and actionable recommendations for compliance improvement.
    
    **Workflow:**
    1. **Validation Phase:**
       - Verify document exists and user has access
       - Validate analysis parameters and standards
       - Check user permissions for compliance analysis
    
    2. **Analysis Phase:**  
       - Extract and preprocess document content
       - Apply multi-standard compliance rules
       - Calculate weighted compliance scores
       - Identify specific compliance gaps
    
    3. **Reporting Phase:**
       - Generate detailed compliance report
       - Create actionable recommendations
       - Log analysis for audit trail
       - Cache results for performance
    
    **Standards Support:**
    - **ISO 13485:2016:** Medical device quality management systems
    - **EU MDR 2017/745:** European medical device regulation
    - **FDA 21 CFR Part 820:** US quality system regulation
    - **ISO 14971:2019:** Risk management for medical devices
    - **IEC 62304:2015:** Medical device software lifecycle
    
    **Analysis Depths:**
    - **BASIC:** Quick compliance check (30-60 seconds)
    - **STANDARD:** Comprehensive analysis (2-5 minutes) 
    - **COMPREHENSIVE:** Deep analysis with AI insights (5-10 minutes)
    
    **Performance Characteristics:**
    - Average processing time: 3-8 seconds for standard documents
    - Memory usage: ~100MB peak for large documents
    - Concurrent analysis limit: 10 per user
    - Results cached for 1 hour (configurable)
    
    **Security & Audit:**
    - All analyses logged for regulatory audit trail
    - User permissions verified before processing
    - Sensitive compliance data access tracked
    - Analysis parameters and results archived
    
    Args:
        document_id: ID of document to analyze (must be > 0)
        analysis_request: Configuration for analysis including:
            - standards: List of standard codes to check against
            - analysis_depth: Depth of analysis (BASIC/STANDARD/COMPREHENSIVE)
            - include_recommendations: Whether to generate recommendations
            - priority_threshold: Minimum priority for gap reporting
        background_tasks: FastAPI background tasks for cleanup
        current_user: Authenticated user (injected dependency)
        db: Async database session (injected dependency)
        
    Returns:
        ComplianceAnalysisResult containing:
            - analysis_id: Unique identifier for this analysis
            - document_id: ID of analyzed document
            - overall_score: Weighted average compliance score (0-100)
            - compliance_by_standard: Per-standard detailed results
            - gaps: List of identified compliance gaps with priorities
            - recommendations: Actionable steps to improve compliance
            - metadata: Analysis timestamp, duration, and parameters
            
    Raises:
        HTTPException:
            - 400: Invalid analysis parameters or standards
            - 403: User lacks compliance_analysis permission
            - 404: Document not found or not accessible
            - 422: Request validation failed
            - 429: Analysis rate limit exceeded
            - 500: Internal analysis error
            
    Example:
        ```python
        import httpx
        
        # Analyze document against ISO 13485 and EU MDR
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"/api/documents/123/compliance-analysis",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "standards": ["ISO_13485", "EU_MDR"],
                    "analysis_depth": "STANDARD",
                    "include_recommendations": True
                }
            )
            
            result = response.json()
            print(f"Overall compliance: {result['overall_score']}%")
            
            for gap in result['gaps']:
                print(f"Gap: {gap['description']} (Priority: {gap['severity']})")
        ```
        
    Note:
        This operation is resource-intensive and subject to rate limiting.
        For batch analysis of multiple documents, use the batch analysis endpoint.
        
        Analysis results are automatically cached to improve performance for
        repeated analyses of the same document with identical parameters.
    """
    # Validate user permissions
    if not has_permission(current_user, "compliance_analysis"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User lacks 'compliance_analysis' permission",
            headers={"X-Error-Code": "INSUFFICIENT_PERMISSIONS"}
        )
    
    # Validate document access
    document = await get_document_with_access_check(
        document_id=document_id,
        user=current_user,
        db=db
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found or not accessible",
            headers={"X-Error-Code": "DOCUMENT_NOT_FOUND"}
        )
    
    try:
        # Check rate limits
        await check_analysis_rate_limit(current_user.id, db)
        
        # Generate analysis
        logger.info(f"Starting compliance analysis for document {document_id} by user {current_user.id}")
        
        analysis_result = await perform_compliance_analysis(
            document=document,
            standards=analysis_request.standards,
            depth=analysis_request.analysis_depth,
            include_recommendations=analysis_request.include_recommendations,
            db=db
        )
        
        # Log for audit trail
        background_tasks.add_task(
            log_compliance_analysis,
            user_id=current_user.id,
            document_id=document_id,
            analysis_id=analysis_result.analysis_id,
            parameters=analysis_request.dict(),
            db=db
        )
        
        logger.info(f"Compliance analysis {analysis_result.analysis_id} completed successfully")
        
        return analysis_result
        
    except RateLimitExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Analysis rate limit exceeded. Try again in {e.retry_after} seconds.",
            headers={
                "X-Error-Code": "RATE_LIMIT_EXCEEDED",
                "Retry-After": str(e.retry_after)
            }
        )
    
    except AnalysisError as e:
        logger.error(f"Compliance analysis failed for document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error during compliance analysis",
            headers={"X-Error-Code": "ANALYSIS_FAILED"}
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in compliance analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error",
            headers={"X-Error-Code": "INTERNAL_ERROR"}
        )
```

### Pydantic Schema Documentation

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum

class ComplianceStatus(str, Enum):
    """Standardized compliance status values."""
    COMPLIANT = "COMPLIANT"
    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"

class AnalysisDepth(str, Enum):
    """Analysis depth levels with different trade-offs."""
    BASIC = "BASIC"           # Quick check, 30-60 seconds
    STANDARD = "STANDARD"     # Comprehensive, 2-5 minutes
    COMPREHENSIVE = "COMPREHENSIVE"  # Deep analysis, 5-10 minutes

class ComplianceGap(BaseModel):
    """
    Represents a specific compliance gap found during analysis.
    
    A gap indicates where the document doesn't meet requirements
    of a specific standard, with contextual information for remediation.
    """
    
    gap_id: str = Field(
        ...,
        description="Unique identifier for this gap",
        example="gap_iso13485_4.2.3_001"
    )
    
    standard: str = Field(
        ...,
        description="Standard code where gap was identified",
        example="ISO_13485"
    )
    
    clause_reference: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Specific clause or section reference",
        example="4.2.3 - Control of documents"
    )
    
    description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Clear description of the compliance gap",
        example="Document lacks required approval signature and date"
    )
    
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        ...,
        description="Priority level for addressing this gap"
    )
    
    impact_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Numerical impact on overall compliance (0-100)",
        example=25.5
    )
    
    current_state: str = Field(
        ...,
        description="What was found in the document",
        example="Document has creation date but no approval signature"
    )
    
    required_state: str = Field(
        ...,
        description="What should be present for compliance",
        example="Document must have both creation date and authorized approval signature"
    )
    
    recommendation: str = Field(
        ...,
        description="Specific action to resolve this gap",
        example="Add approval signature section and obtain signature from QM manager"
    )
    
    effort_estimate: Literal["TRIVIAL", "MINOR", "MODERATE", "MAJOR", "EXTENSIVE"] = Field(
        ...,
        description="Estimated effort to remediate this gap"
    )
    
    regulatory_risk: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        ...,
        description="Risk level for regulatory non-compliance"
    )
    
    class Config:
        """Pydantic configuration for the model."""
        schema_extra = {
            "example": {
                "gap_id": "gap_iso13485_4.2.3_001",
                "standard": "ISO_13485",
                "clause_reference": "4.2.3 - Control of documents",
                "description": "Document lacks required approval signature and date",
                "severity": "HIGH",
                "impact_score": 25.5,
                "current_state": "Document has creation date but no approval signature",
                "required_state": "Document must have both creation date and authorized approval signature",
                "recommendation": "Add approval signature section and obtain signature from QM manager",
                "effort_estimate": "MINOR",
                "regulatory_risk": "MEDIUM"
            }
        }

class StandardAnalysis(BaseModel):
    """
    Analysis results for a specific standard.
    
    Contains detailed compliance information for one standard,
    including score, status, and specific findings.
    """
    
    standard_code: str = Field(
        ...,
        description="Unique code identifying the standard",
        example="ISO_13485"
    )
    
    standard_name: str = Field(
        ...,
        description="Full name of the standard",
        example="ISO 13485:2016 - Medical devices - Quality management systems"
    )
    
    compliance_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Compliance score for this standard (0-100)",
        example=87.5
    )
    
    status: ComplianceStatus = Field(
        ...,
        description="Overall compliance status for this standard"
    )
    
    sections_analyzed: int = Field(
        ...,
        ge=0,
        description="Number of standard sections analyzed",
        example=12
    )
    
    sections_compliant: int = Field(
        ...,
        ge=0,
        description="Number of sections that are compliant",
        example=10
    )
    
    gaps_found: int = Field(
        ...,
        ge=0,
        description="Number of compliance gaps identified",
        example=2
    )
    
    critical_gaps: int = Field(
        ...,
        ge=0,
        description="Number of critical/high priority gaps",
        example=1
    )
    
    analysis_notes: Optional[str] = Field(
        None,
        description="Additional notes about the analysis for this standard",
        example="Strong compliance in documentation control, minor gaps in training records"
    )

class ComplianceAnalysisRequest(BaseModel):
    """
    Request schema for compliance analysis with comprehensive validation.
    
    Defines all parameters needed to perform compliance analysis,
    with validation to ensure reasonable and safe analysis requests.
    """
    
    standards: List[str] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of standard codes to analyze against",
        example=["ISO_13485", "EU_MDR", "FDA_21_CFR_820"]
    )
    
    analysis_depth: AnalysisDepth = Field(
        default=AnalysisDepth.STANDARD,
        description="Depth of analysis to perform"
    )
    
    include_recommendations: bool = Field(
        default=True,
        description="Whether to generate actionable recommendations"
    )
    
    priority_threshold: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        default="MEDIUM",
        description="Minimum priority level for gap reporting"
    )
    
    focus_areas: Optional[List[str]] = Field(
        default=None,
        max_items=20,
        description="Specific areas to focus analysis on",
        example=["document_control", "risk_management", "design_controls"]
    )
    
    exclude_sections: Optional[List[str]] = Field(
        default=None,
        max_items=50,
        description="Standard sections to exclude from analysis",
        example=["7.3.1", "8.2.4"]
    )
    
    @validator('standards')
    def validate_standards(cls, v: List[str]) -> List[str]:
        """Validate that all standards are supported."""
        supported_standards = {
            "ISO_13485", "EU_MDR", "FDA_21_CFR_820", 
            "ISO_14971", "IEC_62304", "ISO_10993"
        }
        
        unsupported = set(v) - supported_standards
        if unsupported:
            raise ValueError(f"Unsupported standards: {unsupported}")
        
        return v
    
    @validator('focus_areas')
    def validate_focus_areas(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate focus areas are recognized."""
        if not v:
            return v
        
        valid_areas = {
            "document_control", "risk_management", "design_controls",
            "purchasing", "production", "installation", "servicing",
            "measurement", "improvement", "management_responsibility"
        }
        
        invalid_areas = set(v) - valid_areas
        if invalid_areas:
            raise ValueError(f"Invalid focus areas: {invalid_areas}")
        
        return v

class ComplianceAnalysisResult(BaseModel):
    """
    Complete compliance analysis results with comprehensive information.
    
    This model represents the full output of compliance analysis,
    designed to provide actionable insights for compliance improvement.
    """
    
    analysis_id: str = Field(
        ...,
        description="Unique identifier for this analysis",
        example="ca_20241220_123456_abc123"
    )
    
    document_id: int = Field(
        ...,
        description="ID of the analyzed document",
        example=123
    )
    
    overall_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Weighted average compliance score across all standards",
        example=87.5
    )
    
    compliance_by_standard: Dict[str, StandardAnalysis] = Field(
        ...,
        description="Detailed analysis results for each standard"
    )
    
    gaps: List[ComplianceGap] = Field(
        ...,
        description="All compliance gaps found during analysis"
    )
    
    total_gaps: int = Field(
        ...,
        ge=0,
        description="Total number of gaps identified"
    )
    
    critical_gaps: int = Field(
        ...,
        ge=0,
        description="Number of critical/high priority gaps"
    )
    
    recommendations: List[str] = Field(
        ...,
        description="Actionable recommendations for compliance improvement"
    )
    
    # Analysis metadata
    generated_at: datetime = Field(
        ...,
        description="Timestamp when analysis was completed"
    )
    
    analysis_duration_ms: int = Field(
        ...,
        ge=0,
        description="Analysis duration in milliseconds",
        example=3245
    )
    
    analysis_depth: AnalysisDepth = Field(
        ...,
        description="Depth of analysis that was performed"
    )
    
    analyzer_version: str = Field(
        ...,
        description="Version of the analysis engine used",
        example="2.0.0"
    )
    
    # Quality metrics
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Confidence level in the analysis results",
        example=94.2
    )
    
    coverage_percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Percentage of standard requirements covered in analysis",
        example=98.5
    )
    
    class Config:
        """Pydantic configuration for enhanced schema generation."""
        schema_extra = {
            "example": {
                "analysis_id": "ca_20241220_123456_abc123",
                "document_id": 123,
                "overall_score": 87.5,
                "compliance_by_standard": {
                    "ISO_13485": {
                        "standard_code": "ISO_13485",
                        "standard_name": "ISO 13485:2016 - Medical devices - Quality management systems",
                        "compliance_score": 92.0,
                        "status": "COMPLIANT",
                        "sections_analyzed": 15,
                        "sections_compliant": 14,
                        "gaps_found": 1,
                        "critical_gaps": 0
                    }
                },
                "gaps": [
                    {
                        "gap_id": "gap_iso13485_4.2.3_001",
                        "standard": "ISO_13485",
                        "clause_reference": "4.2.3",
                        "description": "Document approval signature missing",
                        "severity": "MEDIUM",
                        "impact_score": 15.0,
                        "recommendation": "Add approval signature section"
                    }
                ],
                "total_gaps": 3,
                "critical_gaps": 1,
                "recommendations": [
                    "Implement document approval workflow",
                    "Add version control procedures",
                    "Update training records"
                ],
                "generated_at": "2024-12-20T10:30:00Z",
                "analysis_duration_ms": 3245,
                "analysis_depth": "STANDARD",
                "analyzer_version": "2.0.0",
                "confidence_score": 94.2,
                "coverage_percentage": 98.5
            }
        }
```

## 📊 Response Standards

### Consistent Response Format

```python
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Standardized API response wrapper for all endpoints."""
    
    success: bool = Field(
        ...,
        description="Indicates if the request was successful"
    )
    
    data: Optional[T] = Field(
        None,
        description="Response payload data"
    )
    
    message: Optional[str] = Field(
        None,
        description="Human-readable message about the operation"
    )
    
    error_code: Optional[str] = Field(
        None,
        description="Machine-readable error code for failed requests"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Server timestamp when response was generated"
    )
    
    request_id: Optional[str] = Field(
        None,
        description="Unique identifier for request tracing"
    )
    
    # Pagination metadata for list endpoints
    pagination: Optional[PaginationInfo] = Field(
        None,
        description="Pagination information for list responses"
    )

class PaginationInfo(BaseModel):
    """Pagination metadata for list responses."""
    
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=1000, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")

# Usage in endpoints
@app.get("/api/documents", response_model=APIResponse[List[Document]])
async def get_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> APIResponse[List[Document]]:
    """Get paginated list of documents with standardized response format."""
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get total count
    total = db.query(DocumentModel).count()
    
    # Get documents for current page
    documents = db.query(DocumentModel).offset(offset).limit(page_size).all()
    
    # Calculate pagination info
    total_pages = (total + page_size - 1) // page_size
    pagination = PaginationInfo(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )
    
    return APIResponse(
        success=True,
        data=[Document.from_orm(doc) for doc in documents],
        message=f"Retrieved {len(documents)} documents",
        pagination=pagination,
        timestamp=datetime.utcnow()
    )
```

## 🛡️ Error Handling

### Comprehensive Error Response

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import traceback
import uuid

class DetailedHTTPException(HTTPException):
    """Enhanced HTTPException with additional context."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        context: Optional[dict] = None,
        headers: Optional[dict] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.context = context or {}

class ErrorResponse(BaseModel):
    """Standardized error response format."""
    
    success: bool = Field(False, description="Always false for error responses")
    error: ErrorDetail = Field(..., description="Error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str = Field(..., description="Unique request identifier")

class ErrorDetail(BaseModel):
    """Detailed error information."""
    
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error context")
    field_errors: Optional[List[FieldError]] = Field(None, description="Field-specific validation errors")

class FieldError(BaseModel):
    """Individual field validation error."""
    
    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Validation error message")
    invalid_value: Optional[str] = Field(None, description="The invalid value provided")

# Global exception handlers
@app.exception_handler(DetailedHTTPException)
async def detailed_http_exception_handler(
    request: Request, 
    exc: DetailedHTTPException
) -> JSONResponse:
    """Handle detailed HTTP exceptions with full context."""
    
    request_id = str(uuid.uuid4())
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=exc.error_code,
            message=exc.detail,
            details=exc.context
        ),
        request_id=request_id
    )
    
    # Log error for debugging
    logger.error(
        f"HTTP {exc.status_code} - {exc.error_code}: {exc.detail}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "context": exc.context
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict(),
        headers=exc.headers or {}
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(
    request: Request, 
    exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with field details."""
    
    request_id = str(uuid.uuid4())
    
    field_errors = []
    for error in exc.errors():
        field_errors.append(FieldError(
            field=".".join(str(loc) for loc in error["loc"]),
            message=error["msg"],
            invalid_value=str(error.get("input", ""))
        ))
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            field_errors=field_errors
        ),
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )

# Usage in endpoints
@app.post("/api/documents", response_model=Document)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
) -> Document:
    """Create document with comprehensive error handling."""
    
    try:
        # Check for duplicate document number
        existing = db.query(DocumentModel).filter(
            DocumentModel.document_number == document.document_number
        ).first()
        
        if existing:
            raise DetailedHTTPException(
                status_code=409,
                detail="Document with this number already exists",
                error_code="DUPLICATE_DOCUMENT_NUMBER",
                context={
                    "existing_document_id": existing.id,
                    "conflicting_number": document.document_number
                }
            )
        
        # Create document
        db_document = DocumentModel(**document.dict())
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return Document.from_orm(db_document)
        
    except IntegrityError as e:
        db.rollback()
        
        if "UNIQUE constraint failed" in str(e):
            raise DetailedHTTPException(
                status_code=409,
                detail="Resource already exists",
                error_code="INTEGRITY_CONSTRAINT_VIOLATION",
                context={"database_error": str(e)}
            )
        
        raise DetailedHTTPException(
            status_code=500,
            detail="Database constraint violation",
            error_code="DATABASE_ERROR",
            context={"error": str(e)}
        )
    
    except Exception as e:
        db.rollback()
        
        # Log unexpected errors
        logger.error(f"Unexpected error creating document: {e}", exc_info=True)
        
        raise DetailedHTTPException(
            status_code=500,
            detail="Internal server error",
            error_code="INTERNAL_ERROR",
            context={"error_type": type(e).__name__}
        )
```

---

**KI-QMS API Best Practices v2.0.0** | **Last Updated: 2024-12-20** 