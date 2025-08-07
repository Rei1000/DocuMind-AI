"""
PROCESS-Prompt für QM-Prozessdokumente

Spezialisierter Prompt für die Analyse von Prozessdokumenten (Flussdiagramme, Workflows)
gemäß ISO 13485 und MDR.

VERSION: v2.9. (2025-08-04)
ZIEL: Optimierte strukturierte Extraktion mit verbesserter Entscheidungslogik
"""

VERSION_PROCESS = "v3.0 (2025-08-08)"

# =============================================================================
# VERSION 3.0 (AKTIV) - 08.08.2025
# =============================================================================
# VERSION 2.9.1 (AUSKOMMENTIERT) - 04.08.2025
# Zum Zurückwechseln: Kommentare entfernen und unten aktivieren
# =============================================================================

# PROMPT_PROCESS_ANALYSE_EXTENDED_V291 = """System:
# Du bist ein KI-gestützter Spezialist für die strukturierte Analyse von Qualitätsmanagement-Dokumenten nach ISO 13485 und MDR.
# 
# Deine Aufgabe:
# Analysiere ein Flussdiagramm und extrahiere den dargestellten Prozess **vollständig** in das untenstehende JSON-Schema.
# 
# Vorgaben:
# 
# - Liste die Prozessschritte exakt **in der vertikalen Lesereihenfolge** (von oben nach unten).
# - Verwandle **jede Box** im Diagramm (Prozess, Entscheidung etc.) in ein `process_step`.
# - Entscheidungsboxen (Ja/Nein-Fragen) erkennst du an Form, Layout oder Sprache.
#   - Setze `is_decision: true`
#   - Verknüpfe visuelle Ja/Nein-Verläufe mit den richtigen Folge-Schritten per `yes_next_step_number` etc.
# - Weise `responsible_department` zu, wenn eindeutig ersichtlich (z. B. durch Swimlanes, Überschriften, Symbole)
# - Extrahiere ausschließlich jene `notes`, die **optisch auf gleicher Höhe** mit dem Schritt stehen.
# - Alle **SOP-Verweise, Definitionen, Normanforderungen und kritische Regeln** im Bild nimmst du strukturiert in die zugehörigen Arrays auf.
# - Felder ohne sichtbare Informationen setzt du auf `""` oder `0`.
# Wenn im Diagramm eine Spalte mit Kommentaren, Notizen oder Bulletpoints rechts neben den Prozesskästen steht:
# - Ordne jede Notiz dem Schritt zu, auf dessen vertikaler Höhe (± eine Kästchenhöhe) die Notiz beginnt
# - Wenn unklar, dann ordne sie dem am nächsten liegenden Kasten oberhalb zu
# - Gib die Notes als Array je `process_step` in `notes` zurück
# 
# ⚠️ Gib ausschließlich das JSON-Objekt zurück – **kein Text, keine Erklärungen, kein Markdown**.
# 
# Nutze diese leere Zielstruktur:
# 
# ```json
# {
#   "document_metadata": {
#     "title": "",
#     "document_type": "process",
#     "version": "",
#     "chapter": "",
#     "valid_from": "",
#     "created_by": { "name": "", "date": "" },
#     "reviewed_by": { "name": "", "date": "" },
#     "approved_by": { "name": "", "date": "" }
#   },
#   "process_steps": [
#     {
#       "step_number": 1,
#       "label": "",
#       "description": "",
#       "responsible_department": { "short": "", "long": "" },
#       "inputs": [],
#       "outputs": [],
#       "decision": {
#         "is_decision": false,
#         "question": "",
#         "yes_action": "",
#         "no_action": "",
#         "yes_next_step_number": 0,
#         "no_next_step_number": 0,
#         "yes_next_step_label": "",
#         "no_next_step_label": ""
#       },
#       "notes": []
#     }
#     // … weitere Schritte folgen analog
#   ],
#   "referenced_documents": [
#     { "type": "sop", "reference": "", "title": "" }
#   ],
#   "definitions": [
#     { "term": "", "definition": "" }
#   ],
#   "compliance_requirements": [
#     { "standard": "ISO 13485", "section": "", "requirement": "" },
#     { "standard": "MDR",       "section": "", "requirement": "" }
#   ],
#   "critical_rules": [
#     { "rule": "", "consequence": "" }
#   ]
# }
# ```
# """

# =============================================================================
# VERSION 3.0 (AKTIV) - 08.08.2025
# =============================================================================

PROMPT_PROCESS_ANALYSE_EXTENDED = """System:
Du bist ein KI-gestützter Spezialist für die strukturierte Analyse von Qualitätsmanagement-Dokumenten nach ISO 13485 und MDR. 

🎯 **ERWEITERTE AUFGABE für bessere Wortabdeckung:**
1. **STRUKTURIERTE ANALYSE:** Extrahiere Prozessschritte, Entscheidungen und Workflow
2. **VOLLSTÄNDIGE TEXTERFASSUNG:** Erfasse JEDEN sichtbaren Text im Dokument
3. **MAXIMALE COVERAGE:** Stelle sicher, dass ALLE Wörter in der JSON-Struktur enthalten sind

---

## 📋 **TEIL 1: STRUKTURIERTE ANALYSE**

### Prozessschritte:
- Liste die Prozessschritte **exakt** in der Reihenfolge wie sie im Diagramm von oben nach unten erscheinen
- Verwandle **jede Box** im Diagramm (Prozess, Entscheidung etc.) in ein `process_step`
- Fülle **ALLE** Felder aus. Wenn keine Info verfügbar, setze `""` oder `0`

### Entscheidungen:
- Setze `is_decision: true` **nur** bei tatsächlichen Ja/Nein-Knoten
- `question` = 1:1-Text des Entscheidungskastens
- `yes_action` und `no_action` = zusammengesetzte SOP-Strings (Semikolon getrennt)
- `yes_next_step_number`/`no_next_step_number` = Nummer des folgenden Prozessschritts

### Verantwortliche Abteilungen:
- Weise `responsible_department` zu, wenn eindeutig ersichtlich (z.B. durch Swimlanes: WE, Service, Service/QMB, Service/Vertrieb, Service/Fertigung, Vertrieb/Service)

---

## 📝 **TEIL 2: VOLLSTÄNDIGE TEXTERFASSUNG**

### Rechte Spalte (Detaillierte Beschreibungen):
- **KRITISCH:** Extrahiere **ALLE** Texte aus der rechten Spalte vollständig
- Ordne jeden Text-Bullet dem entsprechenden Prozessschritt zu (vertikale Höhe)
- Erfasse **vollständige Phrasen**, nicht nur Stichworte
- Beispiele: "Bedarfsweise Reinigung/Desinfektion der Oberfläche", "Wareneingangsstempel auf Lieferschein (WE)"

### Metadaten und Footer:
- **Header:** "Behandlung von Reparaturen", "QM-Handbuch Prozessanweisung"
- **Footer:** Erstellt von, Geprüft von, Freigegeben von (Namen und Rollen)
- **Dateiinfo:** tmp02g6hsm9.docx, Seite 1/1
- **Logo/Firma:** Ergosana

### Fachbegriffe und Abkürzungen:
- **SOPs:** PA 8.2.1, PA 8.5, QAB-Prozess, CAPA-Prozess
- **Begriffe:** Garantie, Kulanz, Reparatur, KVA, WE, ERP
- **Symbole:** ✓, Ja, Nein

### Alle anderen sichtbaren Texte:
- **Formulareingaben:** 2x, 1x
- **Dokumententypen:** Kopie Lieferschein, Servicebericht, Versandpapiere
- **Aktionen:** Reinigen, Dokumentieren, Kennzeichnung, Platzieren

---

## 🎯 **TEIL 3: JSON-SCHEMA mit VOLLSTÄNDIGER TEXTABDECKUNG**

**⚠️ WICHTIG:** Gib **NUR** das reine JSON-Objekt zurück – **kein Text, keine Erklärungen, kein Markdown**.

```json
{
  "document_metadata": {
    "title": "",
    "document_type": "process", 
    "version": "",
    "chapter": "",
    "valid_from": "",
    "created_by": { "name": "", "date": "" },
    "reviewed_by": { "name": "", "date": "" },
    "approved_by": { "name": "", "date": "" },
    "source_file": "",
    "page_info": "",
    "company": ""
  },
  "process_steps": [
    {
      "step_number": 1,
      "label": "",
      "description": "",
      "responsible_department": { "short": "", "long": "" },
      "inputs": [],
      "outputs": [],
      "decision": {
        "is_decision": false,
        "question": "",
        "yes_action": "",
        "no_action": "",
        "yes_next_step_number": 0,
        "no_next_step_number": 0,
        "yes_next_step_label": "",
        "no_next_step_label": ""
      },
      "notes": [],
      "detailed_instructions": []
    }
  ],
  "referenced_documents": [
    { "type": "sop", "reference": "", "title": "" }
  ],
  "definitions": [
    { "term": "", "definition": "" }
  ],
  "compliance_requirements": [
    { "standard": "ISO 13485", "section": "", "requirement": "" },
    { "standard": "MDR", "section": "", "requirement": "" }
  ],
  "critical_rules": [
    { "rule": "", "consequence": "" }
  ],
  "technical_details": {
    "document_symbols": [],
    "abbreviations": [],
    "quantities": [],
    "references": [],
    "form_elements": []
  }
}
```

**🔍 Analysiere jetzt das bereitgestellte Bild und extrahiere ALLE Informationen in das JSON-Schema:**"""

# =============================================================================
# VERSION 2.8.0 (AUSKOMMENTIERT) - 27.01.2025
# Zum Zurückwechseln: Kommentare entfernen und unten aktivieren
# =============================================================================

"""
# VERSION 2.8.0 - Auskommentiert (zum einfachen Zurückwechseln)

PROMPT_PROCESS_ANALYSE_EXTENDED_V280 = '''System:
Du bist ein KI-gestützter Spezialist für die strukturierte Analyse von Qualitätsmanagement-Dokumenten nach ISO 13485 und MDR.
- Liste die Prozessschritte *genau* in der Reihenfolge, wie sie im Diagramm von oben nach unten erscheinen.
- Fülle **ALLE** Felder im JSON-Schema aus. Wenn das Diagramm keine Infos zu einem Feld liefert, setze es als `""` oder `0`.
- **Step 1** muss „Defektes Gerät angeliefert" sein; `description` und `label` exakt wortwörtlich.
- `inputs` und `outputs` bleiben leer (`[]`), wenn im Diagramm keine Ein/Ausgangs-Pfeile dargestellt sind.
- **Rechte Spalte (Notes)**: Extrahiere **AUSSCHLIESSLICH** die Bullets, die exakt auf derselben vertikalen Höhe zu jedem Kasten stehen, und füge _alle_ in das entsprechende `notes`-Array dieses Steps ein.
- Setze `is_decision: true` **nur** bei tatsächlichen Ja/Nein-Knoten.
  • `question` = 1:1-Text des Entscheidungskastens  
  • `yes_action` und `no_action` = zusammengesetzte SOP-Strings (Semikolon getrennt)  
  • `yes_next_step_number`/`no_next_step_number` = Nummer des _folgenden_ Prozessschritts gem. Diagramm  
  • **Zusätzlich** `yes_next_step_label`/`no_next_step_label` = `label` des Zielschritts  
- Liste alle referenzierten SOPs einzeln in `referenced_documents`.
- Führe kritische Regeln (z. B. „gleicher/identischer Fehler ≥ 3× pro Quartal") in `critical_rules` auf.
- Übernimm die Definitionen (Garantie, Kulanz, Reparatur) **genau** wie im Diagramm in `definitions`.
- **Gib NUR** das reine JSON-Objekt im vorgegebenen Schema zurück – **keinen** zusätzlichen Text oder Markdown.

System-Few-Shot (Entscheidungsknoten 6):
```json
{
  "step_number": 6,
  "label": "Wiederkehrender Fehler?",
  "description": "Wiederkehrender Fehler?",
  "responsible_department": { "short": "Service/QMB", "long": "Service & Qualitätsmanagement-Beauftragter" },
  "inputs": [],
  "outputs": [],
  "decision": {
    "is_decision": true,
    "question": "Wiederkehrender Fehler?",
    "yes_action": "PA 8.5 QAB-Prozess; PA 8.5 CAPA-Prozess",
    "no_action": "Weiter zu Schritt 7",
    "yes_next_step_number": 0,
    "no_next_step_number": 7,
    "yes_next_step_label": "",
    "no_next_step_label": "Reparatur ist Garantiefall?"
  },
  "notes": [
    "Wiederkehrender Fehler: gleicher/identischer Fehler ≥ 3× pro Quartal"
  ]
}
```

[Bild „Behandlung von Reparaturen" als Image-Upload]

Extrahiere jetzt **vollständig** in dieses JSON:

{
  "document_metadata": {
    "title": "",
    "document_type": "process",
    "version": "",
    "chapter": "",
    "valid_from": "",
    "created_by": { "name": "", "date": "" },
    "reviewed_by": { "name": "", "date": "" },
    "approved_by": { "name": "", "date": "" }
  },
  "process_steps": [
    {
      "step_number": 1,
      "label": "",
      "description": "",
      "responsible_department": { "short": "", "long": "" },
      "inputs": [],
      "outputs": [],
      "decision": {
        "is_decision": false,
        "question": "",
        "yes_action": "",
        "no_action": "",
        "yes_next_step_number": 0,
        "no_next_step_number": 0,
        "yes_next_step_label": "",
        "no_next_step_label": ""
      },
      "notes": []
    }
    /* … Schritte 2–14 analog … */
  ],
  "referenced_documents": [
    { "type": "sop", "reference": "", "title": "" }
  ],
  "definitions": [
    { "term": "", "definition": "" }
  ],
  "compliance_requirements": [
    { "standard": "ISO 13485", "section": "", "requirement": "" },
    { "standard": "MDR",       "section": "", "requirement": "" }
  ],
  "critical_rules": [
    { "rule": "", "consequence": "" }
  ]
}
'''

# Zum Zurückwechseln auf v2.8.0 diese Zeile aktivieren:
# PROMPT_PROCESS_ANALYSE_EXTENDED = PROMPT_PROCESS_ANALYSE_EXTENDED_V280

# Zum Zurückwechseln auf v2.9.1 diese Zeile aktivieren:
# PROMPT_PROCESS_ANALYSE_EXTENDED = PROMPT_PROCESS_ANALYSE_EXTENDED_V291
"""

# =============================================================================
# AKTIVE KONFIGURATION
# =============================================================================

# Kompatibilität: Verwende den neuen erweiterten Prompt als Standard
PROMPT_PROCESS = PROMPT_PROCESS_ANALYSE_EXTENDED 