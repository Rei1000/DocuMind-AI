"""
🔄 WORKFLOW-AUTOMATION PROMPTS
=============================

Prompts für intelligente Workflow-Erkennung und -Auslösung.
"""

VERSION = "1.0"

def get_prompt(prompt_type: str = "workflow_trigger", **kwargs) -> str:
    """Holt Workflow-Automation Prompt"""
    return """
    Sie sind ein Experte für Workflow-Automation in Qualitätsmanagement-Systemen.
    Analysieren Sie die Nachricht und identifizieren Sie passende Workflows.
    
    NACHRICHT:
    {content}
    
    ERWARTETE JSON-STRUKTUR:
    {{
        "workflow_type": "DOCUMENT_REVIEW | APPROVAL | NOTIFICATION | TASK_ASSIGNMENT",
        "priority": "HIGH | MEDIUM | LOW",
        "assigned_to": ["Zugewiesene Benutzer"],
        "estimated_duration": "Geschätzte Dauer"
    }}
    
    GEBEN SIE NUR DAS JSON ZURÜCK:
    """ 