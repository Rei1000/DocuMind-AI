"""
🤖 HYBRID-AI PROMPTS
===================

Prompts für Hybrid-AI-Systeme (lokale + Cloud AI).
"""

VERSION = "1.0"

def get_prompt(prompt_type: str = "hybrid_analysis", **kwargs) -> str:
    """Holt Hybrid-AI Prompt"""
    return """
    Sie sind ein Hybrid-AI-System für Qualitätsmanagement-Systeme.
    Optimieren Sie lokale AI-Ergebnisse durch Cloud-basierte Verbesserung.
    
    LOKALE AI-ERGEBNISSE:
    {content}
    
    ERWARTETE JSON-STRUKTUR:
    {{
        "enhanced_analysis": "Verbesserte Analyse",
        "confidence_improvement": 0.1,
        "additional_insights": ["Zusätzliche Erkenntnisse"],
        "hybrid_method": "local_cloud_enhancement"
    }}
    
    GEBEN SIE NUR DAS JSON ZURÜCK:
    """ 