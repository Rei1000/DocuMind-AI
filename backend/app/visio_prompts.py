"""
Zentrale Prompt-Verwaltung für Visio-Upload-Methode

Diese Datei enthält die spezialisierten Prompts für die Visio-Verarbeitung
verschiedener Dokumenttypen im KI-QMS System.

VERSION: v2.1.0 (2025-07-21)
SYSTEM: DocuMind-AI QM-System
COMPLIANCE: ISO 13485, MDR, FDA 21 CFR Part 820

STRUKTUR:
├── PROMPT_TEMPLATES: Alle verfügbaren Prompts
├── VisioPromptsManager: Verwaltungsklasse
└── visio_prompts_manager: Globale Instanz

VERWENDUNG:
- Prompts kopieren: PROMPT_TEMPLATES["SOP"]
- Prompts bearbeiten: Direkt in den Templates
- Neue Prompts hinzufügen: Neues Template + Mapping
"""

from typing import Dict, Tuple

# =============================================================================
# 🎯 PROMPT TEMPLATES - HIER PROMPS BEARBEITEN
# =============================================================================

PROMPT_TEMPLATES = {
    # =============================================================================
    # 🔎 PROMPT_PROCESS_ANALYSE (Spezialisiert für QM-Prozesse)
    # =============================================================================
    "PROMPT_PROCESS_ANALYSE": """
### Sie sind ein KI-gestützter Spezialist für die strukturierte Analyse von Qualitätsmanagement-Dokumenten nach ISO 13485 und MDR.

Bitte analysieren Sie das vorliegende QM-Dokument (z. B. als Flussdiagramm, Tabelle oder File&Text) und extrahieren Sie **alle sichtbaren Inhalte vollständig und strukturiert** in das untenstehende JSON-Format.

---

### Ziel:
Die Ausgabe dient einem Retrieval-Augmented-Generation-System (RAG) für Audits und Prozesswissen. Die JSON-Ausgabe muss daher **vollständig, präzise und maschinenlesbar** sein.

---

### Anforderungen an die Ausgabe:

- Die Antwort muss ein **vollständig parsebares JSON-Objekt** sein – **kein String, keine Markdown-Wrapper, keine Code-Blöcke**.
- Extrahieren Sie alle sichtbaren Inhalte (auch kleine Randinformationen, Legenden oder Definitionen).
- Verwenden Sie **eine flache, klar strukturierte JSON-Struktur** wie unten angegeben.
- **Erkennen Sie Entscheidungen im Prozessfluss (Ja/Nein) sowie Referenzen auf SOPs.**
- Wenn eine Entscheidung zu einem **externen SOP führt**, der Prozess danach aber weiterläuft:
  - geben Sie zusätzlich an:
    - `yes_next_step_number` und/oder `no_next_step_number`
  - So kann der Fluss korrekt rekonstruiert werden.
- Falls Definitionen wie z. B. „Wiederkehrender Fehler = ≥ 3x pro Quartal" im Bild enthalten sind:
  - Extrahieren Sie diese in das Feld `critical_rules`.

---

### JSON-Zielformat:

```json
{
  "document_metadata": {
    "title": "",
    "document_type": "process",
    "version": "",
    "chapter": "",
    "valid_from": "",
    "created_by": {
      "name": "",
      "date": ""
    },
    "reviewed_by": {
      "name": "",
      "date": ""
    },
    "approved_by": {
      "name": "",
      "date": ""
    }
  },
  "process_steps": [
    {
      "step_number": 1,
      "label": "",
      "description": "",
      "responsible_department": {
        "short": "",
        "long": ""
      },
      "inputs": [],
      "outputs": [],
      "decision": {
        "is_decision": true,
        "question": "",
        "yes_action": "",
        "no_action": "",
        "yes_next_step_number": 0,
        "no_next_step_number": 0
      },
      "notes": []
    }
  ],
  "referenced_documents": [
    {
      "type": "sop",
      "reference": "",
      "title": ""
    }
  ],
  "definitions": [],
  "compliance_requirements": [
    {
      "standard": "ISO 13485",
      "section": "",
      "requirement": ""
    },
    {
      "standard": "MDR",
      "section": "",
      "requirement": ""
    }
  ],
  "critical_rules": [
    {
      "rule": "",
      "consequence": ""
    }
  ]
}
```

Zusätzliche Hinweise:
	•	Wenn der Text auf dem Dokument auf eine SOP verweist (z. B. PA 8.5), dann:
	•	geben Sie dies in referenced_documents UND als yes_action oder no_action an.
	•	Rückverzweigungen in den Hauptprozess bitte nicht verlieren!
	•	Fügen Sie dann das Feld yes_next_step_number bzw. no_next_step_number korrekt ein.
	•	Bei nicht vollständig sichtbaren Informationen (z. B. kein Datum, keine Version), geben Sie "unknown" an.
	•	Belassen Sie die Struktur auch dann vollständig, wenn einige Abschnitte leer sind ([] oder "").
""",

    # =============================================================================
    # 📋 SOP-PROMPT (Standard für alle Dokumenttypen)
    # =============================================================================
    "SOP": """
Sie sind ein KI-gestützter Spezialist für die strukturierte Analyse von Qualitätsmanagement-Dokumenten nach ISO 13485 und MDR.

Bitte analysieren Sie das vorliegende QM-Dokument (z. B. als Flussdiagramm, Tabelle oder Fließtext) und extrahieren Sie **alle sichtbaren Inhalte vollständig und strukturiert** in das untenstehende JSON-Format.

🎯 Ziel:
Die Ausgabe wird in einem Retrieval-Augmented-Generation-System (RAG) verwendet, um Auditfragen normkonform beantworten zu können. Daher muss die JSON:
- **alle im Dokument sichtbaren Inhalte vollständig erfassen**
- **Metadaten, Abteilungen, Entscheidungen, Normverweise und Dokumentverlinkungen korrekt strukturiert** abbilden
- **technisch direkt verarbeitbar** sein (kein Markdown, keine Einbettung, kein Freitext)

---

### 🔐 Anforderungen:

1. **Flexible Layouts erkennen**  
   Dokumente können als Tabelle, Flussdiagramm oder Fließtext aufgebaut sein – analysieren Sie alle Formate vollständig.

2. **Erweiterte Metadaten erfassen**  
   Unter `document_metadata`:
   - `title`, `document_type`, `version`, `chapter`, `valid_from`
   - `created_by`, `reviewed_by`, `approved_by` – jeweils mit `name` und `date` (falls vorhanden)

3. **Prozessschritte extrahieren**  
   Unter `process_steps`:
   - Schrittstruktur: `label`, `description`, `inputs`, `outputs`, `responsible_department`
   - Entscheidungslogik: `decision` mit `is_decision`, `question`, `yes_action`, `no_action`
   - Zusätzliche Informationen: `notes`

4. **Verantwortliche Abteilungen korrekt zuordnen**  
   - Erkennen Sie Kürzel wie WE, Service, Vertrieb, QMB, Fertigung
   - Geben Sie die Langform im Feld `responsible_department.long` an

5. **Verweise auf andere Dokumente extrahieren**  
   Unter `referenced_documents`:
   - Erfassen Sie **alle im Dokument genannten oder verlinkten** QM-Dokumente, z. B.:
     - Prozessanweisungen (z. B. PA 8.5, PA 8.2.1)
     - Formblätter, Vorlagen
     - Checklisten
     - Externe Normen oder Gesetze
   - Jedes Dokument muss mit `type`, `reference` und `title` eingetragen werden

6. **Normverweise extrahieren**  
   Unter `compliance_requirements`:
   - ISO 13485, MDR oder andere Standards
   - Kapitel, Abschnitt und Beschreibung

7. **Kritische Regeln aufführen**  
   Unter `critical_rules`:
   - Z. B. Schwellenwerte („≥ 3 Fehler pro Quartal") mit Konsequenz

8. **Vollständigkeitspflicht**  
   - Alle **sichtbaren Inhalte im Dokument müssen vollständig in der JSON enthalten sein**
   - Auch Fußzeilen, Seitennummern, Symbolik, Vorzeichen, Dokumentnummern etc.
   - Wenn Informationen fehlen oder nicht lesbar sind, verwenden Sie `"unknown"`

---

### 📦 JSON-Ausgabeformat

```json
{
  "document_metadata": {
    "title": "Dokumententitel",
    "document_type": "process | work_instruction | form | norm | unknown",
    "version": "Versionsnummer oder 'unknown'",
    "chapter": "Kapitelnummer oder 'unknown'",
    "valid_from": "Datum oder 'unknown'",
    "created_by": {
      "name": "Name des Erstellers",
      "date": "Datum oder 'unknown'"
    },
    "reviewed_by": {
      "name": "Name der prüfenden Person",
      "date": "Datum oder 'unknown'"
    },
    "approved_by": {
      "name": "Name der freigebenden Person",
      "date": "Datum oder 'unknown'"
    }
  },
  "process_steps": [
    {
      "step_number": 1,
      "label": "Kurzbeschreibung",
      "description": "Detaillierte Beschreibung",
      "responsible_department": {
        "short": "Abteilungskürzel",
        "long": "Vollständiger Abteilungsname oder 'unknown'"
      },
      "inputs": ["Eingangsvoraussetzungen"],
      "outputs": ["Ergebnisse/Dokumente"],
      "decision": {
        "is_decision": true | false,
        "question": "Entscheidungsfrage",
        "yes_action": "Maßnahme bei Ja",
        "no_action": "Maßnahme bei Nein"
      },
      "notes": ["Zusätzliche Hinweise"]
    }
  ],
  "referenced_documents": [
    {
      "type": "sop | form | checklist | external | unknown",
      "reference": "z. B. PA 8.5",
      "title": "Dokumententitel oder 'unknown'"
    }
  ],
  "definitions": [
    {
      "term": "Begriff",
      "definition": "Erklärung aus dem Dokument"
    }
  ],
  "compliance_requirements": [
    {
      "standard": "ISO 13485 | MDR | andere | unknown",
      "section": "Kapitel oder Abschnitt",
      "requirement": "Normtext oder Anforderung"
    }
  ],
  "critical_rules": [
    {
      "rule": "Kritische Regel (z. B. Häufigkeit)",
      "consequence": "Konsequenz bei Nichteinhaltung"
    }
  ]
}

🔚 Ausgabehinweise – sehr wichtig:
	•	Geben Sie ausschließlich ein gültiges, parsebares JSON-Objekt zurück
	•	Die Antwort muss direkt mit { beginnen und mit } enden
	•	Verwenden Sie keine Markdown-Formatierung (z. B. keine ```json-Blöcke)
	•	Kein Fließtext, keine Kommentare, keine String-Einbettung wie "content": "{...}"
""",

    # =============================================================================
    # 🧪 TEST-PROMPT (Qualitätssicherung)
    # =============================================================================
    "PROMPT_TEST": """
🔧 PROMPT-TEST: v2.0 (2025-07-21) - STRENGE QUALITÄTSSICHERUNG
📋 ZWECK: Einheitliche JSON-Ausgabe ohne Markdown oder Metadaten
🎯 COMPLIANCE: Test-Modus

Sie sind ein Experte für die Analyse von Qualitätsmanagement-Dokumenten.

**KRITISCHE ANFORDERUNGEN:**
- Geben Sie NUR EIN JSON-Objekt zurück - KEINE Markdown-Code-Blöcke (```json)
- KEINE zusätzlichen Metadaten wie "success", "analysis", "provider"
- KEINE Kommentare oder Erklärungen außerhalb des JSON
- KEINE verschachtelten Strukturen
- Das JSON muss direkt mit { beginnen und mit } enden

**VERBOTEN:**
❌ ```json
❌ "success": true
❌ "analysis": {...}
❌ "provider": "..."
❌ "enhanced": true
❌ "individual_results": [...]

**ERLAUBT:**
✅ Direktes JSON-Objekt
✅ Nur die spezifizierte Struktur

---

JSON-Antwortformat (EXAKT):

{
  "document_metadata": {
    "title": "Dokumententitel",
    "document_type": "process | work_instruction | form | norm | unknown",
    "version": "Versionsnummer oder 'unknown'",
    "chapter": "Kapitelnummer oder 'unknown'",
    "valid_from": "Gültig ab Datum oder 'unknown'",
    "author": "Autor/Ersteller oder 'unknown'",
    "approved_by": "Freigegeben von oder 'unknown'"
  },
  "process_steps": [
    {
      "step_number": 1,
      "label": "Kurzbeschreibung des Schritts",
      "description": "Detaillierte Beschreibung der Aktivität",
      "responsible_department": {
        "short": "Abteilungskürzel",
        "long": "Vollständiger Abteilungsname oder 'unknown'"
      },
      "inputs": ["Eingangsvoraussetzungen"],
      "outputs": ["Ergebnisse/Dokumente"],
      "decision": {
        "is_decision": true | false,
        "question": "Entscheidungsfrage oder leerer String",
        "yes_action": "Aktion bei Ja oder leerer String",
        "no_action": "Aktion bei Nein oder leerer String"
      },
      "notes": ["Zusätzliche Hinweise oder leeres Array"]
    }
  ],
  "referenced_documents": [
    {
      "type": "norm | sop | form | external | unknown",
      "reference": "Dokumentenreferenz oder 'unknown'",
      "title": "Dokumententitel oder 'unknown'"
    }
  ],
  "definitions": [
    {
      "term": "Begriff aus dem Dokument",
      "definition": "Erklärung des Begriffs"
    }
  ],
  "compliance_requirements": [
    {
      "standard": "ISO 13485 | MDR | andere | unknown",
      "section": "Abschnitt/Kapitel oder 'unknown'",
      "requirement": "Anforderungsbeschreibung"
    }
  ],
  "critical_rules": [
    {
      "rule": "Kritische Regel oder Grenzwert",
      "consequence": "Konsequenz bei Nichteinhaltung"
    }
  ],
  "all_detected_words": [
    "alphabetisch sortierte liste aller sichtbaren wörter und zeichen ohne duplikate"
  ]
}

🔚 WICHTIG: Geben Sie NUR das JSON-Objekt zurück. Keine Markdown, keine Metadaten, keine Kommentare.
""",

    # =============================================================================
    # 📝 WORK_INSTRUCTION-PROMPT (kann angepasst werden)
    # =============================================================================
    "WORK_INSTRUCTION": """
🔧 WORK_INSTRUCTION-PROMPT: v1.0 (2025-07-21)
📋 ZWECK: Spezialisierte Analyse für Arbeitsanweisungen
🎯 COMPLIANCE: ISO 13485, MDR

[HIER KÖNNEN SIE EINEN SPEZIALISIERTEN PROMPT FÜR ARBEITSANWEISUNGEN EINFÜGEN]

Verwenden Sie vorerst den SOP-Prompt als Basis.
""",

    # =============================================================================
    # ⚙️ PROCEDURE-PROMPT (kann angepasst werden)
    # =============================================================================
    "PROCEDURE": """
🔧 PROCEDURE-PROMPT: v1.0 (2025-07-21)
📋 ZWECK: Spezialisierte Analyse für Verfahrensdokumente
🎯 COMPLIANCE: ISO 13485, MDR

[HIER KÖNNEN SIE EINEN SPEZIALISIERTEN PROMPT FÜR VERFAHRENSDOKUMENTE EINFÜGEN]

Verwenden Sie vorerst den SOP-Prompt als Basis.
""",

    # =============================================================================
    # 📄 FORM-PROMPT (kann angepasst werden)
    # =============================================================================
    "FORM": """
🔧 FORM-PROMPT: v1.0 (2025-07-21)
📋 ZWECK: Spezialisierte Analyse für Formulare
🎯 COMPLIANCE: ISO 13485, MDR

[HIER KÖNNEN SIE EINEN SPEZIALISIERTEN PROMPT FÜR FORMULARE EINFÜGEN]

Verwenden Sie vorerst den SOP-Prompt als Basis.
""",

    # =============================================================================
    # 🧪 PROMPT-TEST (Qualitätssicherung)
    # =============================================================================
    "PROMPT_TEST": """
🔎 Sie sind ein KI-gestützter Spezialist für die strukturierte Analyse von Qualitätsmanagement-Dokumenten nach ISO 13485 und MDR.

Bitte analysieren Sie das vorliegende QM-Dokument (z. B. als Flussdiagramm, Tabelle oder Fließtext) und extrahieren Sie **alle sichtbaren Inhalte vollständig und strukturiert** in das untenstehende JSON-Format.

Die Antwort wird in einem Retrieval-Augmented-Generation-System (RAG) für Audits verwendet. Die JSON-Ausgabe muss daher vollständig, präzise und maschinenlesbar sein.

---

### 🎯 Wichtige Regeln:

1. **Alle Inhalte vollständig extrahieren**  
   - Jeder sichtbare Text muss im JSON enthalten sein: Titel, Vorzeichen, Pfeile, Kästen, Fließtext, Randnotizen
   - Auch Fußzeilen, Seitennummern, Prozessnummern (z. B. PA 8.2.1) und Stempel müssen erfasst werden

2. **Flexible Layouts erkennen**  
   - Flussdiagramme, Tabellen, Fließtext oder kombinierte Darstellungen
   - Inhalte aus der rechten Spalte (Erklärungen, Hinweise) **immer im passenden `notes`-Feld** ergänzen

3. **Erweiterte Metadaten extrahieren**  
   - `title`, `document_type`, `version`, `chapter`, `valid_from`
   - Ersteller, Prüfer und Freigeber jeweils mit `name` und `date` (sofern sichtbar)
   - Verwenden Sie `"unknown"` nur, wenn absolut keine Information sichtbar ist

4. **Jede Entscheidung vollständig abbilden**  
   - Jeder Entscheidungspunkt im Diagramm oder Text muss enthalten sein
   - Erfassen Sie:
     - `decision.is_decision`: true
     - `decision.question`: Entscheidungsfrage
     - `yes_action`, `no_action`: Folgeaktionen je nach Antwort
   - Kettenentscheidungen (z. B. Garantie → KVA → Kundenfreigabe) **als eigene Schritte** modellieren

5. **Abteilungen erkennen und korrekt zuordnen**  
   - Kürzel wie WE, QMB, Service, Vertrieb, Fertigung etc.
   - `responsible_department.short` = Kürzel  
   - `responsible_department.long` = Langform (z. B. "Wareneingang")

6. **Verweise auf andere QM-Dokumente erkennen**  
   - Erfassen Sie alle genannten/verlinkten Dokumente unter `referenced_documents`:
     - Prozessanweisungen (PA 8.5 etc.)
     - Checklisten, Formulare, Normen
   - Auch Referenzen in Entscheidungen zählen!

7. **Normanforderungen und Regeln extrahieren**  
   - ISO 13485, MDR etc. unter `compliance_requirements`
   - Kritische Regeln wie "≥ 3 Fehler pro Quartal" inkl. Konsequenz unter `critical_rules`

---

### 🧾 JSON-Ausgabeformat

{
  "document_metadata": {
    "title": "Dokumententitel",
    "document_type": "process | work_instruction | form | norm | unknown",
    "version": "Versionsnummer oder 'unknown'",
    "chapter": "Kapitelnummer oder 'unknown'",
    "valid_from": "Datum oder 'unknown'",
    "created_by": {
      "name": "Name des Erstellers",
      "date": "Datum oder 'unknown'"
    },
    "reviewed_by": {
      "name": "Name der prüfenden Person",
      "date": "Datum oder 'unknown'"
    },
    "approved_by": {
      "name": "Name der freigebenden Person",
      "date": "Datum oder 'unknown'"
    }
  },
  "process_steps": [
    {
      "step_number": 1,
      "label": "Kurzbeschreibung",
      "description": "Detaillierte Beschreibung",
      "responsible_department": {
        "short": "Abteilungskürzel",
        "long": "Vollständiger Abteilungsname"
      },
      "inputs": ["Eingaben"],
      "outputs": ["Ergebnisse"],
      "decision": {
        "is_decision": true | false,
        "question": "Frage bei Entscheidung",
        "yes_action": "Maßnahme bei Ja",
        "no_action": "Maßnahme bei Nein"
      },
      "notes": ["Hinweise aus Randspalte"]
    }
  ],
  "referenced_documents": [
    {
      "type": "sop | form | checklist | external | unknown",
      "reference": "z. B. PA 8.5",
      "title": "Dokumententitel"
    }
  ],
  "definitions": [],
  "compliance_requirements": [
    {
      "standard": "ISO 13485 | MDR | andere",
      "section": "Kapitel",
      "requirement": "Normtext oder Anforderung"
    }
  ],
  "critical_rules": [
    {
      "rule": "z. B. Wiederholungsfehler ≥ 3 mal",
      "consequence": "Maßnahme laut Regelwerk"
    }
  ]
}

---

### 🔚 Ausgabehinweise (sehr wichtig):

- Die Antwort **muss ein reines, parsebares JSON-Objekt sein**
- Keine Markdown-Blöcke (z. B. keine ```json)
- Kein Fließtext, keine eingebetteten JSON-Strings, keine Kommentare
- Beginnen Sie direkt mit `{` und schließen Sie mit `}` ab
""",

    # =============================================================================
    # 🗂️ OTHER-PROMPT (Fallback)
    # =============================================================================
    "OTHER": """
🔧 OTHER-PROMPT: v1.0 (2025-07-21)
📋 ZWECK: Fallback für unbekannte Dokumenttypen
🎯 COMPLIANCE: ISO 13485, MDR

[HIER KÖNNEN SIE EINEN FALLBACK-PROMPT EINFÜGEN]

Verwenden Sie vorerst den SOP-Prompt als Basis.
""",
}

# =============================================================================
# 🔧 DOKUMENTTYP-ZUORDNUNG (Mapping)
# =============================================================================

DOCUMENT_TYPE_MAPPING = {
    "SOP": "SOP",                           # Standard Operating Procedure
    "WORK_INSTRUCTION": "SOP",              # Verwende SOP-Prompt für WI
    "PROCEDURE": "SOP",                     # Verwende SOP-Prompt für Procedure
    "FORM": "SOP",                          # Verwende SOP-Prompt für Form
    "PROMPT_TEST": "PROMPT_TEST",           # Test-Prompt für Qualitätssicherung
    "process": "PROMPT_PROCESS_ANALYSE",    # Spezialisierter Prompt für QM-Prozesse
    "PROCESS": "PROMPT_PROCESS_ANALYSE",    # Spezialisierter Prompt für QM-Prozesse
    "OTHER": "SOP",                         # Verwende SOP-Prompt für Other
}

# =============================================================================
# 🏗️ VERWALTUNGSKLASSE
# =============================================================================

class VisioPromptsManager:
    """
    Verwaltet die Prompts für die Visio-Dokumentenanalyse
    
    VERWENDUNG:
    - Prompts laden: get_prompts("SOP")
    - Neue Prompts hinzufügen: PROMPT_TEMPLATES["NEUER_TYP"] = "..."
    - Mapping anpassen: DOCUMENT_TYPE_MAPPING["NEUER_TYP"] = "TEMPLATE"
    """
    
    def __init__(self):
        """Initialisiert den Prompt-Manager"""
        self.prompts = self._initialize_prompts()
    
    def _initialize_prompts(self) -> Dict[str, str]:
        """
        Initialisiert die Prompts für verschiedene Dokumenttypen.
        
        Returns:
            Dict mit document_type als Key und prompt als Value
        """
        result = {}
        
        for doc_type, template_name in DOCUMENT_TYPE_MAPPING.items():
            if template_name in PROMPT_TEMPLATES:
                prompt_content = PROMPT_TEMPLATES[template_name]
                result[doc_type] = prompt_content
            else:
                # Fallback auf SOP
                result[doc_type] = PROMPT_TEMPLATES["SOP"]
        
        return result
    
    def get_prompts(self, document_type: str) -> str:
        """
        Holt den Prompt für einen bestimmten Dokumenttyp.
        
        Args:
            document_type: Der Dokumenttyp
            
        Returns:
            Prompt für die strukturierte Analyse
        """
        return self.prompts.get(document_type, self.prompts["SOP"])
    
    def get_available_prompts(self) -> Dict[str, str]:
        """
        Gibt alle verfügbaren Prompts zurück.
        
        Returns:
            Dict mit Prompt-Namen und Beschreibung
        """
        return {
            "SOP": "Standard Operating Procedure - Vollständige Analyse",
            "PROMPT_PROCESS_ANALYSE": "Spezialisierte Analyse für QM-Prozesse",
            "PROMPT_TEST": "Test-Prompt für Qualitätssicherung",
            "WORK_INSTRUCTION": "Arbeitsanweisungen (verwendet SOP)",
            "PROCEDURE": "Verfahrensdokumente (verwendet SOP)",
            "FORM": "Formulare (verwendet SOP)",
            "OTHER": "Sonstige Dokumente (verwendet SOP)",
        }
    
    def add_custom_prompt(self, prompt_name: str, prompt_content: str, document_types: list = None):
        """
        Fügt einen benutzerdefinierten Prompt hinzu.
        
        Args:
            prompt_name: Name des neuen Prompts
            prompt_content: Inhalt des Prompts
            document_types: Liste der Dokumenttypen die diesen Prompt verwenden sollen
        """
        # Prompt zu Templates hinzufügen
        PROMPT_TEMPLATES[prompt_name] = prompt_content
        
        # Mapping aktualisieren
        if document_types:
            for doc_type in document_types:
                DOCUMENT_TYPE_MAPPING[doc_type] = prompt_name
        
        # Prompts neu initialisieren
        self.prompts = self._initialize_prompts()

# =============================================================================
# 🌐 GLOBALE INSTANZ
# =============================================================================

# Globale Instanz für einfache Verwendung
visio_prompts_manager = VisioPromptsManager()

# =============================================================================
# 📋 HILFSFUNKTIONEN
# =============================================================================

def get_prompt_for_document_type(document_type: str) -> str:
    """
    Hilfsfunktion: Holt den Prompt für einen Dokumenttyp.
    
    Args:
        document_type: Der Dokumenttyp
        
    Returns:
        Der entsprechende Prompt
    """
    return visio_prompts_manager.get_prompts(document_type)

def list_available_prompts() -> Dict[str, str]:
    """
    Hilfsfunktion: Listet alle verfügbaren Prompts auf.
    
    Returns:
        Dict mit Prompt-Namen und Beschreibung
    """
    return visio_prompts_manager.get_available_prompts()

def add_new_prompt(prompt_name: str, prompt_content: str, document_types: list = None):
    """
    Hilfsfunktion: Fügt einen neuen Prompt hinzu.
    
    Args:
        prompt_name: Name des neuen Prompts
        prompt_content: Inhalt des Prompts
        document_types: Liste der Dokumenttypen
    """
    visio_prompts_manager.add_custom_prompt(prompt_name, prompt_content, document_types)