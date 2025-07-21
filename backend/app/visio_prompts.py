"""
Zentrale Prompt-Verwaltung für Visio-Upload-Methode

Diese Datei enthält die spezialisierten Prompts für die Visio-Verarbeitung
verschiedener Dokumenttypen im KI-QMS System.
"""

from typing import Dict, Tuple

class VisioPromptsManager:
    """Verwaltet die Prompts für die Visio-Dokumentenanalyse"""
    
    def __init__(self):
        self.prompts = self._initialize_prompts()
    
    def _initialize_prompts(self) -> Dict[str, Tuple[str, str]]:
        """
        Initialisiert die Prompts für verschiedene Dokumenttypen.
        Returns: Dict mit document_type als Key und (prompt1, prompt2) als Tuple
        """
        return {
            "SOP": self._get_sop_prompts(),
            "WORK_INSTRUCTION": self._get_work_instruction_prompts(),
            "PROCEDURE": self._get_procedure_prompts(),
            "FORM": self._get_form_prompts(),
            "OTHER": self._get_default_prompts()
        }
    
    def get_prompts(self, document_type: str) -> Tuple[str, str]:
        """
        Holt die Prompts für einen bestimmten Dokumenttyp.
        Falls der Typ nicht definiert ist, werden die Standard-Prompts verwendet.
        
        Args:
            document_type: Der Dokumenttyp
            
        Returns:
            Tuple mit (prompt1_wortliste, prompt2_strukturanalyse)
        """
        return self.prompts.get(document_type, self.prompts["OTHER"])
    
    def _get_sop_prompts(self) -> Tuple[str, str]:
        """Prompts für SOP-Dokumente - Einheitlicher Prompt für Wortliste + Analyse"""
        prompt1 = """
🔧 PROMPT-VERSION: v2.1.0 (2025-07-21) - Ergosana QM-System
📋 ZWECK: Vollständige, auditkonforme JSON-Repräsentation für RAG-System
🎯 COMPLIANCE: ISO 13485, MDR, FDA 21 CFR Part 820

Sie sind ein Experte für die Analyse von Qualitätsmanagement-Dokumenten nach ISO 13485 und MDR.

Analysieren Sie das vorliegende QM-Dokument und extrahieren Sie **alle relevanten Informationen** vollständig und strukturiert gemäß folgendem JSON-Format.

Das Ziel ist es, eine **vollständige, auditkonforme JSON-Repräsentation** des Dokuments zu erzeugen. Diese wird in ein Retrieval-Augmented-Generation (RAG) System überführt und dient als Grundlage für rechtssichere Chat-Antworten im Rahmen von Audits, Normprüfungen und interner Qualitätssicherung.

**WICHTIG:**
- Es dürfen **keine sichtbaren Wörter, Zeichen, Formulierungen, Symbole oder Vorzeichen fehlen** – alles im PNG-Bild vorhandene muss sich **in der JSON-Struktur wiederfinden**, auch Fußnoten, Versionsvermerke, Spaltenüberschriften, etc.
- Wenn ein Element nicht klar identifizierbar ist (z. B. Version, Autor), setzen Sie den Wert auf `"unknown"`.
- Dokumente können verschiedene Layouts haben (z. B. Tabellen, Flussdiagramme, reine Texte) – analysieren Sie **alle Formate zuverlässig**.
- Bei Prozessdarstellungen mit Spalten (z. B. links: Schritt, rechts: Beschreibung), muss die **rechte Spalte als `description`** dem jeweiligen Schritt zugeordnet werden.
- **Abteilungen** wie „QM“, „WE“ (Wareneingang), „Service“, „Vertrieb“ etc. **müssen erkannt** und korrekt im Feld `responsible_department` eingetragen werden.
- Entscheidungen im Prozess (z. B. Ja/Nein-Wege) müssen im Block `"decision"` vollständig erfasst sein.

---

JSON-Antwortformat:

```json
{
  "document_metadata": {
    "title": "Dokumententitel",
    "document_type": "process | work_instruction | form | norm | unknown",
    "version": "Versionsnummer oder 'unknown'",
    "chapter": "Kapitelnummer oder 'unknown'",
    "valid_from": "Gültig ab Datum (z. B. 2023-10-01) oder 'unknown'",
    "author": "Autor/Ersteller oder 'unknown'",
    "approved_by": "Freigegeben von oder 'unknown'"
  },
  "process_steps": [
    {
      "step_number": 1,
      "label": "Kurzbeschreibung des Schritts",
      "description": "Detaillierte Beschreibung der Aktivität, ggf. rechte Spalte aus dem Dokument",
      "responsible_department": {
        "short": "Abteilungskürzel (z. B. QM, WE, Service, Vertrieb)",
        "long": "Vollständiger Abteilungsname oder 'unknown'"
      },
      "inputs": ["Liste aller Eingangsvoraussetzungen oder 'unknown'"],
      "outputs": ["Liste aller erzeugten Ergebnisse/Dokumente oder 'unknown'"],
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
  ]
}
🔚 Geben Sie **nur ein gültiges JSON-Objekt** mit allen Informationen gemäß obigem Format zurück. Keine Kommentare, Erklärungen oder zusätzliche Ausgaben.
"""
        
        # Prompt2 wird nicht mehr benötigt, da alles in Prompt1 enthalten ist
        prompt2 = prompt1  # Verwende denselben Prompt für beide Schritte
        
        return (prompt1, prompt2)
    
    def _get_work_instruction_prompts(self) -> Tuple[str, str]:
        """Prompts für Arbeitsanweisungen"""
        prompt1 = """
Du bist ein OCR-Spezialist. Extrahiere ALLE sichtbaren Wörter aus dieser Arbeitsanweisung.
Beachte besonders:
- Arbeitsschritte und Anweisungen
- Werkzeuge und Materialien
- Sicherheitshinweise
- Qualitätskriterien
- Bilder-Beschriftungen

Gib NUR eine alphabetisch sortierte Wortliste zurück. Ein Wort pro Zeile.
"""
        
        prompt2 = """
Du bist ein Experte für Arbeitsanweisungen. Analysiere dieses Dokument strukturiert:

1. DOKUMENT-INFO:
   - Titel und Nummer
   - Geltungsbereich
   - Version

2. ARBEITSSCHRITTE:
   - Detaillierte Schrittfolge
   - Zeitangaben
   - Benötigte Ressourcen

3. SICHERHEIT:
   - Sicherheitshinweise
   - Persönliche Schutzausrüstung
   - Gefahren

4. QUALITÄT:
   - Prüfkriterien
   - Toleranzen
   - Dokumentation

Antworte als strukturiertes JSON.
"""
        return (prompt1, prompt2)
    
    def _get_procedure_prompts(self) -> Tuple[str, str]:
        """Prompts für Verfahrensdokumente"""
        prompt1 = """
Extrahiere ALLE Wörter aus diesem Verfahrensdokument.
Achte auf:
- Verfahrensbezeichnungen
- Prozessschritte
- Verantwortlichkeiten
- Dokument-Referenzen

Nur alphabetische Wortliste ausgeben.
"""
        
        prompt2 = """
Analysiere dieses Verfahrensdokument und strukturiere:

1. VERFAHRENS-METADATEN
2. ZWECK UND GELTUNGSBEREICH
3. VERANTWORTLICHKEITEN
4. VERFAHRENSSCHRITTE
5. MITGELTENDE DOKUMENTE
6. AUFZEICHNUNGEN

Als JSON ausgeben.
"""
        return (prompt1, prompt2)
    
    def _get_form_prompts(self) -> Tuple[str, str]:
        """Prompts für Formulare"""
        prompt1 = """
Extrahiere alle Wörter aus diesem Formular, inklusive:
- Formularfelder
- Beschriftungen
- Ausfüllhinweise
- Kopf-/Fußzeilen

Alphabetische Wortliste.
"""
        
        prompt2 = """
Analysiere dieses Formular:

1. FORMULAR-IDENTIFIKATION
2. FORMULARFELDER (Name, Typ, Pflichtfeld)
3. AUSFÜLLHINWEISE
4. UNTERSCHRIFTSFELDER
5. VERWENDUNGSZWECK

Als strukturiertes JSON.
"""
        return (prompt1, prompt2)
    
    def _get_default_prompts(self) -> Tuple[str, str]:
        """Standard-Prompts für unbekannte Dokumenttypen"""
        prompt1 = """
Extrahiere ALLE sichtbaren Wörter aus diesem Dokument.
Gib eine alphabetisch sortierte Wortliste aus.
"""
        
        prompt2 = """
Analysiere dieses Dokument und extrahiere:
1. Dokument-Metadaten (Titel, Typ, Version)
2. Hauptinhalt und Struktur
3. Wichtige Informationen
4. Referenzen

Als JSON ausgeben.
"""
        return (prompt1, prompt2)

# Singleton-Instanz
visio_prompts_manager = VisioPromptsManager()