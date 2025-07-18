"""
Visio-spezifische Prompts für Bildanalyse von QM-Dokumenten

Diese Prompts werden für die zweistufige Visio-Verarbeitung verwendet:
1. visio_words: Extraktion aller Wörter und Zeichen
2. visio_analysis: Strukturierte semantische Analyse
"""

from typing import Dict, Optional
import json

# Visio-Prompt-Templates nach Dokumenttyp
VISIO_PROMPTS = {
    # Standard-Prompts für alle Dokumenttypen
    "default": {
        "visio_words": """
Du bist ein präziser OCR-Spezialist für Qualitätsmanagement-Dokumente.

AUFGABE:
Extrahiere ALLE lesbaren Wörter, Zahlen und Zeichen aus diesem Bild.
Das Bild zeigt ein QM-Dokument (möglicherweise mit Flussdiagrammen, Tabellen, Formularen).

WICHTIG:
- Extrahiere JEDEN sichtbaren Text, egal wie klein
- Behalte die originale Schreibweise bei
- Trenne Wörter mit Leerzeichen
- Ignoriere rein dekorative Elemente
- Bei Flussdiagrammen: Extrahiere Text aus ALLEN Boxen und Verbindungen
- Bei Tabellen: Extrahiere ALLE Zellen-Inhalte
- Bei Formularen: Extrahiere Feldnamen UND ausgefüllte Werte

FORMAT:
Gib alle Wörter als einfache, durch Leerzeichen getrennte Liste aus.
Keine JSON-Struktur, keine Formatierung, nur die Wörter.

Beispiel-Output:
Prozess Start Eingangsprüfung Dokument vollständig Ja Nein Rückgabe Freigabe QM-001 Version 2.0
""",
        
        "visio_analysis": """
Du bist ein Experte für die Analyse von QM-Dokumenten in der Medizintechnik.

AUFGABE:
Analysiere dieses Bild eines QM-Dokuments und erstelle eine strukturierte JSON-Analyse.

ANALYSE-STRUKTUR:
{
    "document_info": {
        "title": "Haupttitel des Dokuments",
        "document_number": "Dokumentennummer falls vorhanden",
        "version": "Versionsnummer",
        "type": "Art des Dokuments (SOP, Arbeitsanweisung, Formular, etc.)",
        "date": "Datum falls vorhanden"
    },
    "content_structure": {
        "main_sections": ["Liste der Hauptabschnitte"],
        "process_steps": ["Falls Prozess: Liste der Schritte"],
        "decision_points": ["Falls vorhanden: Entscheidungspunkte"],
        "responsibilities": ["Genannte Verantwortlichkeiten/Rollen"]
    },
    "compliance_references": {
        "iso_standards": ["Referenzierte ISO-Normen"],
        "regulations": ["MDR, FDA, etc."],
        "internal_references": ["Interne Dokument-Referenzen"]
    },
    "quality_indicators": {
        "contains_flowchart": true/false,
        "contains_forms": true/false,
        "contains_tables": true/false,
        "validation_requirements": ["Erkannte Validierungsanforderungen"],
        "critical_control_points": ["Kritische Kontrollpunkte"]
    },
    "extracted_data": {
        "key_terms": ["Wichtige Fachbegriffe"],
        "measurements": ["Messgrößen/Toleranzen"],
        "abbreviations": {"Abk": "Bedeutung"},
        "form_fields": ["Bei Formularen: Feldnamen"]
    }
}

WICHTIG:
- Strukturiere die Informationen logisch
- Extrahiere ALLE relevanten QM-Informationen
- Erkenne Prozessflüsse und deren Logik
- Identifiziere Compliance-relevante Aspekte
- Bei Unsicherheit: Beste Schätzung mit Hinweis

Antworte NUR mit dem JSON-Objekt, keine zusätzlichen Erklärungen.
"""
    },
    
    # Spezifische Prompts für SOPs
    "SOP": {
        "visio_words": """
Du bist ein OCR-Spezialist für Standard Operating Procedures (SOPs).

FOKUS bei SOP-Dokumenten:
- Prozesstitel und SOP-Nummer
- Alle Prozessschritte
- Verantwortlichkeiten (QM, QS, Produktion, etc.)
- Entscheidungspunkte (Ja/Nein-Verzweigungen)
- Referenzen zu anderen SOPs oder Formularen
- Versionsnummer und Freigabedatum
- Gültigkeitsbereich

Extrahiere ALLE Wörter aus Flussdiagrammen, Textboxen und Verbindungslinien.
Gib sie als einfache, durch Leerzeichen getrennte Liste aus.
""",
        
        "visio_analysis": """
Du bist ein SOP-Analyse-Experte für Medizinprodukte-QMS.

Analysiere diese SOP und strukturiere sie gemäß ISO 13485:

{
    "sop_header": {
        "title": "SOP-Titel",
        "sop_number": "SOP-XXX",
        "version": "X.X",
        "effective_date": "TT.MM.JJJJ",
        "author": "Ersteller",
        "approved_by": "Freigeber"
    },
    "process_flow": {
        "start_condition": "Auslöser/Startbedingung",
        "process_steps": [
            {
                "step_number": 1,
                "action": "Beschreibung",
                "responsible": "Verantwortliche Rolle",
                "decision": "Ja/Nein wenn Entscheidung"
            }
        ],
        "end_condition": "Prozessende/Output"
    },
    "references": {
        "related_sops": ["SOP-XXX"],
        "forms": ["F-XXX"],
        "work_instructions": ["AA-XXX"],
        "standards": ["ISO 13485:2016 Kapitel X.X"]
    },
    "critical_aspects": {
        "quality_gates": ["Qualitätskontrollpunkte"],
        "documentation_requirements": ["Zu dokumentierende Schritte"],
        "training_requirements": ["Schulungsanforderungen"]
    }
}

Antworte NUR mit dem JSON-Objekt.
"""
    },
    
    # Spezifische Prompts für Arbeitsanweisungen
    "WORK_INSTRUCTION": {
        "visio_words": """
Du bist ein OCR-Spezialist für Arbeitsanweisungen in der Medizintechnik.

FOKUS bei Arbeitsanweisungen:
- Titel und AA-Nummer
- Detaillierte Arbeitsschritte
- Werkzeuge/Materialien
- Sicherheitshinweise
- Qualitätsprüfpunkte
- Bilder/Diagramm-Beschriftungen
- Toleranzen und Messgrößen

Extrahiere ALLE sichtbaren Texte, auch aus:
- Bildunterschriften
- Tabellen mit Parametern
- Checklisten
- Warnhinweisen

Output: Alle Wörter durch Leerzeichen getrennt.
""",
        
        "visio_analysis": """
Du bist ein Experte für technische Arbeitsanweisungen nach ISO 13485.

Strukturiere diese Arbeitsanweisung:

{
    "instruction_header": {
        "title": "Titel der Arbeitsanweisung",
        "document_number": "AA-XXX",
        "version": "X.X",
        "product_scope": "Betroffene Produkte/Prozesse"
    },
    "work_steps": [
        {
            "step": 1,
            "action": "Detaillierte Anweisung",
            "tools_required": ["Benötigte Werkzeuge"],
            "materials": ["Benötigte Materialien"],
            "safety_notes": ["Sicherheitshinweise"],
            "quality_check": "Prüfpunkt falls vorhanden"
        }
    ],
    "technical_details": {
        "parameters": [
            {"name": "Parameter", "value": "Wert", "tolerance": "±X"}
        ],
        "measurements": ["Messgrößen"],
        "settings": ["Maschineneinstellungen"]
    },
    "quality_requirements": {
        "inspection_points": ["Prüfpunkte"],
        "acceptance_criteria": ["Akzeptanzkriterien"],
        "documentation": ["Zu dokumentierende Werte"]
    },
    "references": {
        "drawings": ["Zeichnungsnummern"],
        "specifications": ["Spezifikationen"],
        "sops": ["Übergeordnete SOPs"]
    }
}

Antworte NUR mit dem JSON-Objekt.
"""
    },
    
    # Spezifische Prompts für Formulare
    "FORM": {
        "visio_words": """
Du bist ein OCR-Spezialist für QM-Formulare.

FOKUS bei Formularen:
- Formularname und F-Nummer
- ALLE Feldbezeichnungen
- Vorausgefüllte Werte
- Checkboxen-Beschriftungen
- Tabellenkopfzeilen
- Fußnoten und Hinweise
- Unterschriftsfelder

Extrahiere wirklich JEDEN Text, auch:
- Kleine Hinweistexte
- Versionsnummern
- Datumsfelder
- Abteilungsbezeichnungen

Output: Alle Wörter durch Leerzeichen getrennt.
""",
        
        "visio_analysis": """
Du bist ein Formular-Analyse-Experte für QMS.

Analysiere dieses QM-Formular:

{
    "form_identification": {
        "form_name": "Formularname",
        "form_number": "F-XXX",
        "version": "X.X",
        "purpose": "Zweck des Formulars"
    },
    "form_structure": {
        "sections": [
            {
                "section_name": "Abschnittsname",
                "fields": [
                    {
                        "field_name": "Feldbezeichnung",
                        "field_type": "text/checkbox/date/signature",
                        "required": true/false,
                        "prefilled_value": "Falls vorhanden"
                    }
                ]
            }
        ],
        "tables": [
            {
                "table_name": "Tabellenname",
                "columns": ["Spalte1", "Spalte2"],
                "row_count": X
            }
        ]
    },
    "workflow_integration": {
        "used_in_processes": ["SOP-XXX"],
        "approval_fields": ["Unterschriftsfelder"],
        "distribution": ["Verteilerliste"]
    },
    "compliance_features": {
        "traceability_fields": ["Chargen-Nr", "Serien-Nr"],
        "mandatory_fields": ["Pflichtfelder"],
        "validation_rules": ["Erkannte Validierungsregeln"]
    }
}

Antworte NUR mit dem JSON-Objekt.
"""
    }
}

def get_visio_prompt(document_type: str, prompt_type: str) -> str:
    """
    Holt den passenden Visio-Prompt basierend auf Dokumenttyp
    
    Args:
        document_type: Der Dokumenttyp (SOP, WORK_INSTRUCTION, FORM, etc.)
        prompt_type: "visio_words" oder "visio_analysis"
    
    Returns:
        Der entsprechende Prompt-String
    """
    # Normalisiere Dokumenttyp
    doc_type_upper = document_type.upper()
    
    # Prüfe ob spezifischer Prompt existiert
    if doc_type_upper in VISIO_PROMPTS and prompt_type in VISIO_PROMPTS[doc_type_upper]:
        return VISIO_PROMPTS[doc_type_upper][prompt_type]
    
    # Fallback zu Default-Prompt
    if prompt_type in VISIO_PROMPTS["default"]:
        return VISIO_PROMPTS["default"][prompt_type]
    
    # Fehler wenn Prompt-Typ unbekannt
    raise ValueError(f"Unbekannter Prompt-Typ: {prompt_type}")

def get_available_visio_prompts() -> Dict[str, list]:
    """
    Gibt alle verfügbaren Visio-Prompts zurück
    
    Returns:
        Dictionary mit Dokumenttypen und verfügbaren Prompt-Typen
    """
    available = {}
    for doc_type, prompts in VISIO_PROMPTS.items():
        available[doc_type] = list(prompts.keys())
    return available

def validate_visio_json_response(response: str, expected_structure: str = "visio_analysis") -> Dict:
    """
    Validiert und parsed die JSON-Antwort von der Vision-API
    
    Args:
        response: Die Antwort der Vision-API
        expected_structure: Erwartete Struktur ("visio_analysis")
    
    Returns:
        Geparste und validierte JSON-Struktur
    
    Raises:
        ValueError: Bei ungültiger JSON oder fehlender Struktur
    """
    try:
        # Parse JSON
        data = json.loads(response)
        
        # Basis-Validierung für visio_analysis
        if expected_structure == "visio_analysis":
            required_keys = ["document_info", "content_structure", "compliance_references", 
                           "quality_indicators", "extracted_data"]
            
            # Prüfe ob Hauptschlüssel vorhanden
            missing_keys = [key for key in required_keys if key not in data]
            if missing_keys:
                # Erstelle fehlende Strukturen mit Defaults
                for key in missing_keys:
                    if key == "document_info":
                        data[key] = {"title": "Unbekannt", "type": "OTHER"}
                    elif key == "content_structure":
                        data[key] = {"main_sections": []}
                    elif key == "compliance_references":
                        data[key] = {"iso_standards": [], "regulations": []}
                    elif key == "quality_indicators":
                        data[key] = {"contains_flowchart": False}
                    elif key == "extracted_data":
                        data[key] = {"key_terms": []}
        
        return data
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Ungültige JSON-Antwort: {str(e)}")
    except Exception as e:
        raise ValueError(f"Fehler bei JSON-Validierung: {str(e)}")