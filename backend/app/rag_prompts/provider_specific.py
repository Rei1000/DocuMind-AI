"""
🔧 PROVIDER-SPEZIFISCHE PROMPTS
==============================

Provider-spezifisch optimierte Prompts für verschiedene AI-Provider.
"""

VERSION = "1.0"

def get_prompt(prompt_type: str = "strict_json", **kwargs) -> str:
    """Holt Provider-spezifischen Prompt"""
    
    if prompt_type == "strict_json":
        return """
        Sie sind ein KI-Assistent für Qualitätsmanagement-Systeme.
        Analysieren Sie das bereitgestellte Dokument und geben Sie eine strikt JSON-formatierte Antwort zurück.
        
        WICHTIG:
        - Antworten Sie AUSSCHLIESSLICH mit gültigem JSON
        - Keine zusätzlichen Erklärungen oder Text
        - Verwenden Sie die exakte Struktur unten
        
        DOKUMENT-INHALT:
        {content}
        
        FRAGE/KONTEXT:
        {question}
        
        ERWARTETE JSON-STRUKTUR:
        {{
            "analysis": "Dokumentenanalyse",
            "key_findings": ["Wichtige Erkenntnisse"],
            "recommendations": ["Empfehlungen"],
            "confidence": 0.85
        }}
        
        GEBEN SIE NUR DAS JSON ZURÜCK:
        """
    
    elif prompt_type == "ollama_optimized":
        return """
        Sie sind ein QMS-Experte. Analysieren Sie das Dokument.
        
        DOKUMENT:
        {content}
        
        Geben Sie eine JSON-Antwort zurück:
        {{
            "title": "Dokumenttitel",
            "type": "Dokumenttyp",
            "summary": "Zusammenfassung"
        }}
        """
    
    else:
        return get_prompt("strict_json", **kwargs) 