"""
🎯 Document-to-Image Vision Engine für KI-QMS

Die ultimative Lösung für komplexe QM-Dokumente:
Document → High-Quality Images → GPT-4o Vision → >1000 Zeichen Text

Workflow:
1. PDF/DOCX → 300 DPI PNG Images  
2. GPT-4o Vision API → Structured Analysis
3. Comprehensive Text Extraction
4. Process Reference Detection

Optimiert für: PA 8.2.1 Behandlung von Reparaturen
"""

import base64
import json
import logging
import tempfile
import subprocess
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import time

# Document Processing
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# OpenAI Vision
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger("KI-QMS.DocumentVision")

class DocumentVisionEngine:
    """🎯 Advanced Document → Image → Vision OCR → Compliance Analysis"""
    
    def __init__(self):
        # OpenAI Vision setup
        self.client = None
        self.model = "gpt-4o-mini"  # Vision model with availability
        
        # Initialize compliance validator
        self.compliance_validator = ComplianceValidator()
        
        # Check dependencies
        self.pymupdf_available = PYMUPDF_AVAILABLE
        self.libreoffice_available = self._check_libreoffice()
        
        # Initialize OpenAI client
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
                logger.info("✅ OpenAI Vision API initialisiert")
            else:
                logger.warning("⚠️ OPENAI_API_KEY nicht gefunden")
        except Exception as e:
            logger.error(f"❌ OpenAI Vision API Fehler: {e}")
        
        logger.info(f"🎯 Document Vision Engine initialized")
        logger.info(f"📚 PyMuPDF: {'✅' if self.pymupdf_available else '❌'}")
        logger.info(f"📄 LibreOffice: {'✅' if self.libreoffice_available else '❌'}")
        logger.info(f"🤖 OpenAI Vision: {'✅' if self.client else '❌'}")

    def _check_libreoffice(self) -> bool:
        """Check if LibreOffice is available"""
        libreoffice_paths = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS
            "/usr/bin/libreoffice",  # Linux
            "C:\\Program Files\\LibreOffice\\program\\soffice.exe"   # Windows
        ]
        
        for path in libreoffice_paths:
            if Path(path).exists():
                self.libreoffice_path = path
                logger.info(f"✅ LibreOffice gefunden: {path}")
                return True
        
        logger.warning("⚠️ LibreOffice nicht gefunden - Word-Konvertierung nicht verfügbar")
        return False

    async def extract_text_with_document_vision(self, file_path: str) -> Dict[str, Any]:
        """
        🎯 MAIN FUNCTION: Document → Vision OCR → Comprehensive Text
        
        Args:
            file_path: Path to document (PDF, DOCX)
            
        Returns:
            Comprehensive analysis with >1000 characters goal
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "extracted_text": "",
                "method": "file_not_found"
            }
        
        logger.info(f"🎯 Starting Document Vision OCR for: {file_path_obj.name}")
        
        try:
            # 1. Convert Document to High-Quality Images
            images = await self.convert_document_to_images(file_path_obj)
            
            if not images:
                return {
                    "success": False,
                    "error": "No images extracted from document",
                    "extracted_text": "",
                    "method": "no_images"
                }
            
            # 2. Analyze each image with Vision API
            vision_results = []
            combined_text = ""
            process_references = []
            
            for i, img_bytes in enumerate(images):
                logger.info(f"🔍 Analyzing image {i+1}/{len(images)} with Vision API...")
                
                result = await self._analyze_image_with_vision(
                    img_bytes, f"Page {i+1} of {file_path_obj.name}"
                )
                
                if result['success']:
                    vision_results.append(result)
                    combined_text += result['extracted_text'] + "\n\n"
                    process_references.extend(result.get('process_references', []))
            
            # 3. Perform Compliance Analysis on combined results
            logger.info("🔍 Starting comprehensive compliance analysis...")
            
            # Merge all vision results for comprehensive analysis
            merged_vision_data = self._merge_vision_results(vision_results)
            
            # Validate compliance
            compliance_result = await self.compliance_validator.validate_compliance(merged_vision_data)
            
            # 4. Create comprehensive result with compliance intelligence
            final_result = {
                "success": len(vision_results) > 0,
                "extracted_text": combined_text.strip(),
                "method": "document_to_image_vision_with_compliance",
                "images_processed": len(images),
                "pages_analyzed": len(vision_results),
                "process_references": list(set(process_references)),
                "vision_results": vision_results,
                "total_characters": len(combined_text.strip()),
                "file_name": file_path_obj.name,
                
                # Enhanced Compliance Analysis
                "compliance_analysis": compliance_result,
                "structured_data": merged_vision_data,
                
                # Success Metrics
                "success_metrics": {
                    "target_characters": 1000,
                    "achieved_characters": len(combined_text.strip()),
                    "success_rate": min(100, (len(combined_text.strip()) / 1000) * 100),
                    "quality_score": self._calculate_quality_score(combined_text, process_references),
                    "compliance_score": compliance_result.get("compliance_score", 0)
                },
                
                # Actionable Intelligence
                "actionable_insights": {
                    "missing_documents": compliance_result.get("missing_documents", []),
                    "compliance_warnings": compliance_result.get("warnings", []),
                    "recommendations": compliance_result.get("recommendations", []),
                    "workflow_readiness": compliance_result.get("overall_compliance", False)
                }
            }
            
            # Success logging
            chars = final_result["total_characters"]
            if chars > 1000:
                logger.info(f"🎉 SUCCESS: {chars} characters extracted (Target: >1000)!")
            else:
                logger.warning(f"⚠️ Below target: {chars} characters (Target: 1000)")
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Document Vision OCR failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "extracted_text": "",
                "method": "exception",
                "total_characters": 0
            }

    async def convert_document_to_images(self, file_path: Path, dpi: int = 300) -> List[bytes]:
        """Convert document to high-quality images"""
        file_ext = file_path.suffix.lower()
        
        logger.info(f"🔄 Converting {file_ext} → Images (DPI: {dpi})")
        
        if file_ext == '.pdf':
            return await self._pdf_to_images(file_path, dpi)
        elif file_ext in ['.docx', '.doc']:
            return await self._word_to_images(file_path, dpi)
        else:
            logger.error(f"❌ Unsupported format: {file_ext}")
            return []

    async def _pdf_to_images(self, file_path: Path, dpi: int = 300) -> List[bytes]:
        """PDF → PNG with PyMuPDF"""
        if not self.pymupdf_available:
            logger.error("❌ PyMuPDF not available")
            return []
        
        try:
            doc = fitz.open(file_path)
            images = []
            
            logger.info(f"📄 PDF: {len(doc)} pages found")
            max_pages = min(len(doc), 5)  # Limit for performance
            
            for page_num in range(max_pages):
                page = doc.load_page(page_num)
                
                # High-quality rendering
                zoom = dpi / 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img_data = pix.tobytes("png")
                
                images.append(img_data)
                logger.info(f"✅ Page {page_num + 1}: {len(img_data):,} bytes")
                pix = None  # Memory cleanup
            
            doc.close()
            logger.info(f"🎉 PDF→PNG completed: {len(images)} images")
            return images
            
        except Exception as e:
            logger.error(f"❌ PDF conversion failed: {e}")
            return []

    async def _word_to_images(self, file_path: Path, dpi: int = 300) -> List[bytes]:
        """Word → Images via LibreOffice"""
        if not self.libreoffice_available:
            logger.error("❌ LibreOffice not available")
            return []
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 1. Word → PDF
                logger.info("🔄 Step 1: Word → PDF (LibreOffice)")
                pdf_path = await self._convert_word_to_pdf(file_path, temp_path)
                
                if not pdf_path or not pdf_path.exists():
                    logger.error("❌ Word → PDF conversion failed")
                    return []
                
                # 2. PDF → Images
                logger.info("🔄 Step 2: PDF → Images")
                images = await self._pdf_to_images(pdf_path, dpi)
                
                logger.info(f"🎉 Word→Images completed: {len(images)} images")
                return images
                
        except Exception as e:
            logger.error(f"❌ Word conversion failed: {e}")
            return []

    async def _convert_word_to_pdf(self, word_path: Path, output_dir: Path) -> Optional[Path]:
        """Convert Word to PDF using LibreOffice"""
        try:
            # Use the detected LibreOffice path
            libreoffice_cmd = getattr(self, 'libreoffice_path', '/Applications/LibreOffice.app/Contents/MacOS/soffice')
            
            cmd = [
                libreoffice_cmd, '--headless', '--convert-to', 'pdf',
                '--outdir', str(output_dir), str(word_path)
            ]
            
            logger.info(f"🔄 LibreOffice Konvertierung: {' '.join(cmd[:3])}...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                pdf_files = list(output_dir.glob("*.pdf"))
                if pdf_files:
                    pdf_path = pdf_files[0]
                    logger.info(f"✅ Word→PDF erfolgreich: {pdf_path.name} ({pdf_path.stat().st_size:,} bytes)")
                    return pdf_path
                else:
                    logger.error("❌ Keine PDF-Datei nach Konvertierung gefunden")
            else:
                logger.error(f"❌ LibreOffice Fehler (Code {result.returncode}): {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("❌ LibreOffice Timeout (120s)")
        except Exception as e:
            logger.error(f"❌ LibreOffice Exception: {e}")
        
        return None

    async def _analyze_image_with_vision(self, image_bytes: bytes, context: str) -> Dict[str, Any]:
        """Analyze image with GPT-4o Vision API with intelligent rate limiting"""
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI client not available",
                "extracted_text": ""
            }
        
        max_retries = 3
        base_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                prompt = self._create_vision_prompt(context)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_b64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }],
                    max_tokens=2000,
                    temperature=0.1
                )
                
                response_text = response.choices[0].message.content or ""
                
                # Try to parse JSON, fallback to text
                try:
                    parsed = json.loads(response_text)
                    parsed["success"] = True
                    parsed["context"] = context
                    return parsed
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "extracted_text": response_text,
                        "context": context,
                        "process_references": self._extract_references(response_text)
                    }
                    
            except Exception as e:
                error_str = str(e)
                logger.error(f"❌ Vision API error: {e}")
                
                # Check if it's a rate limit error
                if "rate_limit_exceeded" in error_str.lower() or "429" in error_str:
                    if attempt < max_retries - 1:  # Don't wait on last attempt
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"⏳ Rate limit hit, waiting {delay}s before retry {attempt + 1}/{max_retries}...")
                        await asyncio.sleep(delay)
                        continue
                
                # For other errors or last attempt, return error
                return {
                    "success": False,
                    "error": str(e),
                    "extracted_text": ""
                }
        
        # If we get here, all retries failed
        return {
            "success": False,
            "error": f"Failed after {max_retries} attempts due to rate limits",
            "extracted_text": ""
        }

    def _create_vision_prompt(self, context: str) -> str:
        """Create optimized vision prompt for intelligent QM compliance analysis"""
        return f"""
Analyze this QM document/flowchart image with COMPREHENSIVE COMPLIANCE FOCUS.
GOAL: Extract >1000 characters + complete compliance structure.

🎯 CRITICAL ANALYSIS AREAS:

1. DOCUMENT IDENTIFICATION
   - Complete title, version, revision
   - Document type (PA, VA, SOP, WI, Form, etc.)
   - Scope and purpose

2. PROCESS FLOW ANALYSIS
   - Sequential process steps with exact order
   - Decision points (Ja/Nein, conditional paths)
   - Start/End points clearly identified
   - Parallel processes and loops

3. REFERENCE EXTRACTION (Critical for Compliance!)
   - Process references: PA x.x, VA x.x, QMA x.x, SOP x.x
   - Form references: Formblatt xyz, Checkliste abc
   - Standard references: ISO 13485, MDR, FDA CFR Part 820
   - External documents: Arbeitsanweisungen, Verfahren
   - Software/ERP references

4. RESPONSIBILITY MATRIX
   - Role assignments per process step
   - Department responsibilities
   - Approval authorities
   - Review requirements

5. COMPLIANCE REQUIREMENTS
   - Quality control points
   - Documentation requirements
   - Verification steps
   - Validation criteria
   - Risk assessment triggers

6. WORKFLOW CONNECTIONS
   - Input documents required
   - Output documents generated
   - Interface to other processes
   - Escalation procedures

Return STRUCTURED JSON with COMPLIANCE INTELLIGENCE:
{{
    "document_info": {{
        "title": "Complete document title",
        "document_id": "PA 8.2.1 etc.",
        "version": "version info",
        "document_type": "Process Instruction|Work Instruction|SOP|Form|etc.",
        "scope": "what this document covers"
    }},
    "extracted_text": "COMPLETE text extraction (>1000 chars target)",
    "process_flow": {{
        "start_condition": "trigger for this process",
        "main_steps": [
            {{"step": 1, "action": "action description", "responsible": "role", "decision": false}},
            {{"step": 2, "action": "decision point", "responsible": "role", "decision": true, "yes_path": "action", "no_path": "action"}}
        ],
        "end_conditions": ["completion criteria"]
    }},
    "referenced_documents": {{
        "process_instructions": ["PA 8.5", "PA 8.2.2"],
        "work_instructions": ["VA 2.1", "WI 001"],
        "forms_checklists": ["Formblatt X", "Checkliste Y"],
        "sops": ["SOP 123"],
        "standards": ["ISO 13485", "MDR", "FDA CFR"],
        "external_docs": ["ERP System", "Database X"]
    }},
    "responsibility_matrix": {{
        "primary_responsible": "main role",
        "involved_roles": {{"WE": "specific tasks", "Service": "tasks", "QMB": "tasks"}},
        "approval_required": "role for approval",
        "review_cycle": "review requirements"
    }},
    "compliance_checkpoints": {{
        "quality_gates": ["gate1", "gate2"],
        "documentation_required": ["doc1", "doc2"],
        "verification_steps": ["verify1", "verify2"],
        "capa_triggers": ["condition1", "condition2"]
    }},
    "workflow_interfaces": {{
        "input_from": ["source process/document"],
        "output_to": ["destination process/document"],
        "parallel_processes": ["concurrent processes"],
        "escalation_to": ["escalation path"]
    }},
    "estimated_characters": number,
    "compliance_confidence": "percentage of confidence in analysis",
    "missing_references_risk": ["potentially missing documents to check"]
}}

Context: {context}

EXTRACT EVERYTHING - focus on creating a complete compliance map that enables:
- Automatic reference validation
- Missing document detection  
- Process compliance verification
- Intelligent workflow routing
- Norm conformity checking

Be extremely detailed and systematic!
"""

    def _extract_references(self, text: str) -> List[str]:
        """Extract process references from text"""
        patterns = [
            r'\b(PA|VA|QMA|SOP|WI)\s+(\d+(?:\.\d+)*)\b',
            r'\b(ISO|DIN|EN|IEC)\s+(\d+(?:\.\d+)*)\b',
            r'\b(MDR|IVDR|FDA|CFR)\b'
        ]
        
        references = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    references.append(' '.join(match))
                else:
                    references.append(match)
        
        return list(set(references))

    def _calculate_quality_score(self, text: str, references: List[str]) -> float:
        """Calculate extraction quality score"""
        score = 0
        
        # Text length score (0-50 points)
        length_score = min(50, len(text) / 20)
        score += length_score
        
        # Reference score (0-25 points)
        ref_score = min(25, len(references) * 5)
        score += ref_score
        
        # Content quality indicators (0-25 points)
        quality_indicators = [
            'behandlung', 'reparatur', 'prozess', 'verantwortlich',
            'qualität', 'dokumentation', 'prüfung', 'capa'
        ]
        content_score = sum(5 for indicator in quality_indicators 
                          if indicator.lower() in text.lower())
        score += min(25, content_score)
        
        return min(100, score)
    
    def _merge_vision_results(self, vision_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple page results into comprehensive document analysis"""
        
        merged = {
            "document_info": {},
            "extracted_text": "",
            "process_flow": {"main_steps": [], "start_condition": "", "end_conditions": []},
            "referenced_documents": {
                "process_instructions": [],
                "work_instructions": [],
                "forms_checklists": [],
                "sops": [],
                "standards": [],
                "external_docs": []
            },
            "responsibility_matrix": {},
            "compliance_checkpoints": {},
            "workflow_interfaces": {}
        }
        
        # Merge data from all pages
        for result in vision_results:
            if result.get("success"):
                # Try to parse JSON first
                try:
                    if isinstance(result.get("extracted_text", ""), str):
                        parsed = json.loads(result["extracted_text"])
                    else:
                        parsed = result
                        
                    # Merge document info (first page takes precedence)
                    if not merged["document_info"] and parsed.get("document_info"):
                        merged["document_info"] = parsed["document_info"]
                    
                    # Accumulate text
                    if parsed.get("extracted_text"):
                        merged["extracted_text"] += parsed["extracted_text"] + "\n"
                    
                    # Merge referenced documents
                    ref_docs = parsed.get("referenced_documents", {})
                    for category, refs in ref_docs.items():
                        if category in merged["referenced_documents"] and refs:
                            merged["referenced_documents"][category].extend(refs)
                    
                    # Merge process flow
                    if parsed.get("process_flow", {}).get("main_steps"):
                        merged["process_flow"]["main_steps"].extend(parsed["process_flow"]["main_steps"])
                    
                    # Merge other sections
                    for section in ["responsibility_matrix", "compliance_checkpoints", "workflow_interfaces"]:
                        if parsed.get(section):
                            merged[section].update(parsed[section])
                            
                except (json.JSONDecodeError, KeyError):
                    # Fallback to simple text extraction
                    text = result.get("extracted_text", "")
                    merged["extracted_text"] += text + "\n"
                    
                    # Extract references from raw text
                    refs = self._extract_references(text)
                    merged["referenced_documents"]["process_instructions"].extend(refs)
        
        # Remove duplicates
        for category in merged["referenced_documents"]:
            merged["referenced_documents"][category] = list(set(merged["referenced_documents"][category]))
        
        return merged

class ComplianceValidator:
    """🔍 Automatic compliance validation for referenced documents"""
    
    def __init__(self):
        self.known_documents = {
            # Process Instructions
            "PA 8.5": {"exists": True, "title": "QAB-Prozess/CAPA-Prozess", "type": "process_instruction"},
            "PA 8.2.1": {"exists": True, "title": "Behandlung von Reklamationen", "type": "process_instruction"},
            "PA 8.2.2": {"exists": False, "title": "Unknown", "type": "process_instruction"},
            
            # Work Instructions  
            "VA 2.1": {"exists": False, "title": "Unknown", "type": "work_instruction"},
            
            # Standards
            "ISO 13485": {"exists": True, "title": "Medical devices — Quality management systems", "type": "standard"},
            "MDR": {"exists": True, "title": "Medical Device Regulation", "type": "regulation"},
            "FDA CFR Part 820": {"exists": True, "title": "Quality System Regulation", "type": "regulation"}
        }
        
        self.required_forms = {
            "Kostenvoranschlag": {"exists": True, "template": "KVA-001"},
            "Reparaturerfassung": {"exists": True, "template": "REP-001"},
            "Wareneingang": {"exists": True, "template": "WE-001"}
        }
    
    async def validate_compliance(self, vision_result: Dict[str, Any]) -> Dict[str, Any]:
        """🔍 Validate all references in vision result for compliance"""
        
        validation_result = {
            "overall_compliance": True,
            "compliance_score": 100,
            "warnings": [],
            "errors": [],
            "validated_references": {},
            "missing_documents": [],
            "recommendations": []
        }
        
        # Extract referenced documents from vision result
        referenced_docs = vision_result.get("referenced_documents", {})
        
        # Validate each category
        await self._validate_process_instructions(referenced_docs.get("process_instructions", []), validation_result)
        await self._validate_work_instructions(referenced_docs.get("work_instructions", []), validation_result)
        await self._validate_forms(referenced_docs.get("forms_checklists", []), validation_result)
        await self._validate_standards(referenced_docs.get("standards", []), validation_result)
        
        # Calculate final compliance score
        validation_result["compliance_score"] = self._calculate_compliance_score(validation_result)
        validation_result["overall_compliance"] = validation_result["compliance_score"] >= 80
        
        # Generate recommendations
        validation_result["recommendations"] = self._generate_recommendations(validation_result)
        
        return validation_result
    
    async def _validate_process_instructions(self, references: List[str], result: Dict[str, Any]):
        """Validate PA references"""
        for ref in references:
            if ref in self.known_documents:
                doc_info = self.known_documents[ref]
                if doc_info["exists"]:
                    result["validated_references"][ref] = {
                        "status": "exists",
                        "title": doc_info["title"],
                        "type": doc_info["type"]
                    }
                else:
                    result["missing_documents"].append(ref)
                    result["errors"].append(f"❌ Referenced process instruction {ref} does not exist in system")
            else:
                result["missing_documents"].append(ref)
                result["warnings"].append(f"⚠️ Unknown process instruction {ref} - needs verification")
    
    async def _validate_work_instructions(self, references: List[str], result: Dict[str, Any]):
        """Validate VA/WI references"""
        for ref in references:
            if ref in self.known_documents:
                doc_info = self.known_documents[ref]
                if doc_info["exists"]:
                    result["validated_references"][ref] = {
                        "status": "exists", 
                        "title": doc_info["title"],
                        "type": doc_info["type"]
                    }
                else:
                    result["missing_documents"].append(ref)
                    result["errors"].append(f"❌ Referenced work instruction {ref} missing")
            else:
                result["warnings"].append(f"⚠️ Work instruction {ref} not found in document registry")
    
    async def _validate_forms(self, references: List[str], result: Dict[str, Any]):
        """Validate form/checklist references"""
        for ref in references:
            # Check for form keywords
            form_found = False
            for form_name, form_info in self.required_forms.items():
                if form_name.lower() in ref.lower():
                    if form_info["exists"]:
                        result["validated_references"][ref] = {
                            "status": "exists",
                            "template": form_info["template"],
                            "type": "form"
                        }
                        form_found = True
                    else:
                        result["missing_documents"].append(ref)
                        result["errors"].append(f"❌ Required form template {ref} missing")
                        form_found = True
                    break
            
            if not form_found:
                result["warnings"].append(f"⚠️ Form/checklist {ref} needs template verification")
    
    async def _validate_standards(self, references: List[str], result: Dict[str, Any]):
        """Validate standard/regulation references"""
        for ref in references:
            if ref in self.known_documents:
                doc_info = self.known_documents[ref]
                result["validated_references"][ref] = {
                    "status": "standard",
                    "title": doc_info["title"],
                    "type": doc_info["type"]
                }
            else:
                result["warnings"].append(f"⚠️ Standard {ref} should be verified for current version")
    
    def _calculate_compliance_score(self, result: Dict[str, Any]) -> float:
        """Calculate overall compliance score"""
        total_refs = len(result["validated_references"]) + len(result["missing_documents"])
        if total_refs == 0:
            return 100
        
        error_penalty = len(result["errors"]) * 20
        warning_penalty = len(result["warnings"]) * 5
        missing_penalty = len(result["missing_documents"]) * 15
        
        score = 100 - error_penalty - warning_penalty - missing_penalty
        return max(0, score)
    
    def _generate_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if result["missing_documents"]:
            recommendations.append(f"🔧 Create missing documents: {', '.join(result['missing_documents'])}")
        
        if len(result["errors"]) > 0:
            recommendations.append("🚨 Fix critical compliance errors before process approval")
        
        if result["compliance_score"] < 90:
            recommendations.append("📋 Consider compliance review with QM team")
        
        if len(result["warnings"]) > 2:
            recommendations.append("🔍 Schedule document verification audit")
        
        return recommendations

# Main export function
async def extract_text_with_document_vision(file_path: str) -> Dict[str, Any]:
    """
    🎯 Main function for document vision OCR
    
    Args:
        file_path: Path to document
        
    Returns:
        Comprehensive text extraction result
    """
    engine = DocumentVisionEngine()
    return await engine.extract_text_with_document_vision(file_path) 