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
        """Prompts für SOP-Dokumente"""
        prompt1 = """
Du bist ein OCR-Spezialist. Extrahiere ALLE sichtbaren Wörter aus diesem SOP-Dokument.
Beachte:
- Kopfzeilen, Fußzeilen, Seitenzahlen
- Titel und Überschriften
- Fließtext und Aufzählungen
- Text in Flussdiagrammen, Formen und Boxen
- Beschriftungen von Pfeilen und Verbindungen
- Legenden und Anmerkungen

Gib NUR eine alphabetisch sortierte Wortliste zurück. Ein Wort pro Zeile.
Keine Duplikate. Keine Erklärungen.
"""
        
        prompt2 = """
Du bist ein QM-Experte für SOP-Analyse. Analysiere dieses SOP-Dokument und extrahiere strukturiert:

1. DOKUMENT-METADATEN:
   - Titel
   - Dokumentennummer
   - Version
   - Gültig ab
   - Ersteller
   - Freigabe durch

2. PROZESSSTRUKTUR:
   - Hauptprozess-Name
   - Prozessschritte (nummeriert)
   - Entscheidungspunkte
   - Verantwortlichkeiten pro Schritt

3. FLUSSDIAGRAMM-ELEMENTE:
   - Start-/End-Punkte
   - Aktivitäten (Rechtecke)
   - Entscheidungen (Rauten)
   - Verbindungen und Reihenfolge

4. REFERENZEN:
   - Verweis auf andere SOPs
   - Normen-Referenzen
   - Formulare und Vorlagen

5. QUALITÄTSKONTROLLE:
   - Prüfpunkte
   - Freigabekriterien
   - Dokumentationspflichten

Antworte im folgenden JSON-Format:
{
  "metadata": {
    "title": "",
    "document_number": "",
    "version": "",
    "valid_from": "",
    "author": "",
    "approved_by": ""
  },
  "process": {
    "name": "",
    "steps": [
      {
        "number": 1,
        "description": "",
        "responsible": "",
        "decision_point": false
      }
    ]
  },
  "flowchart": {
    "start_points": [],
    "end_points": [],
    "activities": [],
    "decisions": [],
    "connections": []
  },
  "references": {
    "sops": [],
    "norms": [],
    "forms": []
  },
  "quality_control": {
    "checkpoints": [],
    "approval_criteria": [],
    "documentation_requirements": []
  }
}
"""
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