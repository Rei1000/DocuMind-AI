"""
📊 COMPLIANCE-ANALYSE PROMPTS
============================

Prompts für Regulatory Affairs und Compliance-Analyse.
"""

VERSION = "1.0"

def get_prompt(prompt_type: str = "compliance_check", **kwargs) -> str:
    """Holt Compliance-Analyse Prompt"""
    return """
    Sie sind ein Experte für Compliance-Analyse in Qualitätsmanagement-Systemen.
    Analysieren Sie das folgende Dokument auf Compliance-Anforderungen.
    
    DOKUMENT-INHALT:
    {content}
    
    ERWARTETE JSON-STRUKTUR:
    {{
        "iso_standards": ["ISO 13485", "ISO 14971"],
        "regulatory_refs": ["FDA 21 CFR 820", "MDR 2017/745"],
        "compliance_level": "CRITICAL | HIGH | MEDIUM | LOW",
        "gaps_identified": ["Identifizierte Compliance-Lücken"]
    }}
    
    GEBEN SIE NUR DAS JSON ZURÜCK:
    """ 