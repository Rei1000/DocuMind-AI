"""
📊 METADATEN-EXTRAKTION PROMPTS
==============================

Prompts für die 5-Layer-Analyse zur Metadaten-Extraktion aus Dokumenten.
"""

VERSION = "1.0"

def get_prompt(prompt_type: str = "document_analysis", **kwargs) -> str:
    """Holt Metadaten-Extraktion Prompt"""
    
    if prompt_type == "document_analysis":
        return """
        Sie sind ein Experte für Qualitätsmanagement-Systeme (QMS) und Dokumentenanalyse.
        Analysieren Sie das folgende Dokument und extrahieren Sie umfassende Metadaten.
        
        WICHTIGE INSTRUKTIONEN:
        - Antworten Sie AUSSCHLIESSLICH mit gültigem JSON
        - Verwenden Sie die exakte Struktur unten
        - Seien Sie präzise und konsistent
        
        DOKUMENT-INHALT:
        {content}
        
        ERWARTETE JSON-STRUKTUR:
        {{
            "title": "Vollständiger Dokumenttitel",
            "document_type": "QM_PROCEDURE | WORK_INSTRUCTION | FORM | QM_MANUAL | QM_POLICY | ISO_STANDARD | SOP | PROTOCOL | CHECKLIST | AUDIT_REPORT | TEST_REPORT | VALIDATION_REPORT | RISK_ASSESSMENT | OTHER",
            "version": "Dokumentversion (z.B. '1.0', '2.1')",
            "main_category": "Hauptkategorie",
            "sub_category": "Unterkategorie",
            "description": "Ausführliche Beschreibung des Dokuments",
            "summary": "Kurze Zusammenfassung",
            "keywords": ["Wichtige Schlüsselwörter"],
            "compliance_level": "CRITICAL | HIGH | MEDIUM | LOW | NOT_APPLICABLE",
            "quality_score": 0.85
        }}
        
        ANALYSIEREN SIE NUN DAS DOKUMENT UND GEBEN SIE NUR DAS JSON ZURÜCK:
        """
    
    elif prompt_type == "enhanced_analysis":
        return """
        Sie sind ein KI-Experte für erweiterte Dokumentenanalyse in Qualitätsmanagement-Systemen.
        Führen Sie eine 5-Layer-Analyse des folgenden Dokuments durch.
        
        DOKUMENT-INHALT:
        {content}
        
        LAYER-ANALYSE:
        1. Dokumenttyp-Klassifikation
        2. Keyword-Extraktion
        3. Struktur-Analyse
        4. Compliance-Bewertung
        5. Qualitätsscore
        
        ERWARTETE JSON-STRUKTUR:
        {{
            "document_type": "Klassifizierter Dokumenttyp",
            "keywords": {{
                "primary": ["Hauptkeywords"],
                "secondary": ["Sekundäre Keywords"],
                "qm_specific": ["QM-spezifische Keywords"]
            }},
            "structure": {{
                "sections": ["Erkannte Abschnitte"],
                "has_tables": true,
                "has_figures": false,
                "has_appendices": true
            }},
            "compliance": {{
                "iso_standards": ["ISO 13485", "ISO 14971"],
                "regulatory_refs": ["FDA 21 CFR 820", "MDR 2017/745"],
                "compliance_level": "CRITICAL | HIGH | MEDIUM | LOW"
            }},
            "quality_score": 0.85
        }}
        
        GEBEN SIE NUR DAS JSON ZURÜCK:
        """
    
    else:
        return get_prompt("document_analysis", **kwargs) 