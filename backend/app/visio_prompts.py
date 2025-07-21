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
Sie sind ein Experte für die Analyse von Qualitätsmanagement-Dokumenten nach ISO 13485 und MDR.

Analysieren Sie das vorliegende QM-Dokument und extrahieren Sie ALLE relevanten Informationen in folgendem JSON-Format:

{
  "document_metadata": {
    "title": "Dokumententitel",
    "document_type": "process | work_instruction | form | norm",
    "version": "Versionsnummer",
    "chapter": "Kapitelnummer",
    "valid_from": "Gültig ab Datum",
    "author": "Autor/Ersteller",
    "approved_by": "Freigegeben von"
  },
  "process_steps": [
    {
      "step_number": 1,
      "label": "Kurzbeschreibung des Schritts",
      "description": "Detaillierte Beschreibung der Aktivität",
      "responsible_department": {
        "short": "Abteilungskürzel (z.B. QM, WE, Service)",
        "long": "Vollständiger Abteilungsname"
      },
      "inputs": ["Eingangsvoraussetzungen"],
      "outputs": ["Ergebnisse/Dokumente"],
      "decision": {
        "is_decision": true,
        "question": "Entscheidungsfrage",
        "yes_action": "Aktion bei Ja",
        "no_action": "Aktion bei Nein"
      },
      "notes": ["Zusätzliche Hinweise oder Anforderungen"]
    }
  ],
  "referenced_documents": [
    {
      "type": "norm | sop | form | external",
      "reference": "Dokumentenreferenz",
      "title": "Dokumententitel"
    }
  ],
  "definitions": [
    {
      "term": "Begriff",
      "definition": "Erklärung"
    }
  ],
  "compliance_requirements": [
    {
      "standard": "ISO 13485 | MDR | andere",
      "section": "Abschnitt/Kapitel",
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

Zusätzliche Anweisung:

Bitte extrahieren Sie **alle sichtbaren Wörter und Zeichen** aus dem Dokument und geben Sie diese als **flache, alphabetisch sortierte Liste** unter dem Feld `all_detected_words` zurück. Beachten Sie:
- Alle Tokens in **Kleinbuchstaben**
- **Keine Duplikate**
- **Satzzeichen und Sonderzeichen dürfen enthalten sein**
- Aufzählungszeichen wie •, → oder - können ignoriert werden
- Reihenfolge im Dokument spielt keine Rolle

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