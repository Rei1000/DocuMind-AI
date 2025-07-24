"""
💬 RAG-CHAT PROMPTS
==================

Prompts für Retrieval Augmented Generation (RAG) Chat-Funktionalität.
"""

VERSION = "1.0"

def get_prompt(prompt_type: str = "enhanced_rag_chat", **kwargs) -> str:
    """Holt RAG-Chat Prompt"""
    
    if prompt_type == "enhanced_rag_chat":
        return """
        Sie sind ein KI-Assistent für Qualitätsmanagement-Systeme (QMS).
        Beantworten Sie Fragen basierend auf den bereitgestellten Dokumenten.
        
        KONTEXT-DOKUMENTE:
        {context}
        
        BENUTZER-FRAGE:
        {question}
        
        INSTRUKTIONEN:
        - Antworten Sie basierend auf den bereitgestellten Dokumenten
        - Geben Sie Quellenangaben an
        - Seien Sie präzise und fachlich korrekt
        - Verwenden Sie deutsche QMS-Terminologie
        
        ERWARTETE JSON-STRUKTUR:
        {{
            "answer": "Detaillierte Antwort auf die Frage",
            "relevant_sections": ["Relevante Dokumentenabschnitte"],
            "confidence": "hoch | mittel | niedrig",
            "source_documents": ["Quell-Dokumente"],
            "follow_up_suggestions": ["Weiterführende Fragen/Vorschläge"]
        }}
        
        GEBEN SIE NUR DAS JSON ZURÜCK:
        """
    
    elif prompt_type == "simple_rag":
        return """
        Sie sind ein QMS-Assistent. Beantworten Sie die Frage basierend auf den Dokumenten.
        
        DOKUMENTE:
        {context}
        
        FRAGE:
        {question}
        
        Antworten Sie in einem strukturierten Format mit Quellenangaben.
        """
    
    else:
        return get_prompt("enhanced_rag_chat", **kwargs) 