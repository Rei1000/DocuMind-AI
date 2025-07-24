"""
📋 DOKUMENT-KLASSIFIKATION PROMPTS
==================================

Prompts für automatische Klassifikation von Dokumenttypen.
"""

VERSION = "1.0"

def get_prompt(prompt_type: str = "classify_document", **kwargs) -> str:
    """Holt Dokument-Klassifikation Prompt"""
    return """
    Sie sind ein Experte für Dokument-Klassifikation in Qualitätsmanagement-Systemen.
    Klassifizieren Sie das folgende Dokument.
    
    DOKUMENT-INHALT:
    {content}
    
    ERWARTETE JSON-STRUKTUR:
    {{
        "document_type": "QM_PROCEDURE | WORK_INSTRUCTION | FORM | QM_MANUAL | QM_POLICY | ISO_STANDARD | SOP | PROTOCOL | CHECKLIST | AUDIT_REPORT | TEST_REPORT | VALIDATION_REPORT | RISK_ASSESSMENT | OTHER",
        "confidence": 0.85,
        "reasoning": "Begründung der Klassifikation"
    }}
    
    GEBEN SIE NUR DAS JSON ZURÜCK:
    """ 