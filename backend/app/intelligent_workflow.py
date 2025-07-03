"""
🧠 Intelligente Workflow-Engine - DAS IST DER GAME CHANGER!

Auto-Magic QMS Workflows:
"Bluetooth Modul nicht lieferbar" → Automatisch:
- 📋 Entwicklung: Ersatzmodul Task
- 🛒 Einkauf: Lieferant Task + Audit
- 🏭 Produktion: Arbeitsanweisung Update
- 🔧 Service: Serviceanleitung Update
- 📖 Dokumentation: Bedienungsanleitung
- 👥 HR: Schulung organisieren

Features:
- 🎯 KI-basierte Intent-Erkennung
- 🔄 Automatische Task-Generierung
- 👥 Intelligente Rollenverteilung
- 📋 SOP-basierte Entscheidungen
- 🚨 Compliance-Monitoring
- 🤖 Vollautomatisches Routing

Autoren: KI-QMS Team  
Version: 1.0.0
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import re

from .models import User, InterestGroup, QMSTask, TaskStatus, DocumentType
from .ai_providers import GoogleGeminiProvider
# Advanced RAG Engine - direkt verwenden
try:
    from .advanced_rag_engine import advanced_rag_engine as rag_engine
    RAG_AVAILABLE = True
    print("✅ Intelligent Workflow: Advanced RAG Engine geladen")
except Exception as e:
    print(f"⚠️  Intelligent Workflow: Advanced RAG Engine nicht verfügbar: {str(e)}")
    RAG_AVAILABLE = False
    
    # Mock RAG Engine für Workflow
    class MockRAGEngine:
        async def enhanced_search(self, query, max_results=5):
            return {"results": [], "answer": "RAG Engine nicht verfügbar"}
        async def index_document_advanced(self, *args, **kwargs):
            return {"status": "skipped"}
    
    rag_engine = MockRAGEngine()

logger = logging.getLogger(__name__)

class WorkflowTriggerType(str, Enum):
    """Workflow-Trigger Typen"""
    SUPPLIER_ISSUE = "supplier_issue"           # "Lieferant Problem"
    COMPONENT_CHANGE = "component_change"       # "Bauteil Änderung"  
    EQUIPMENT_FAILURE = "equipment_failure"     # "Gerät Ausfall"
    COMPLIANCE_GAP = "compliance_gap"           # "Compliance Lücke"
    CUSTOMER_COMPLAINT = "customer_complaint"   # "Kunden Beschwerde"
    AUDIT_FINDING = "audit_finding"             # "Audit Befund"
    PROCESS_IMPROVEMENT = "process_improvement" # "Prozess Verbesserung"
    DOCUMENT_UPDATE = "document_update"         # "Dokument Update"
    TRAINING_NEED = "training_need"             # "Schulungsbedarf"
    RISK_IDENTIFIED = "risk_identified"         # "Risiko identifiziert"

@dataclass
class WorkflowAction:
    """Eine Workflow-Aktion"""
    interest_group: str
    action_type: str
    title: str
    description: str
    priority: str
    due_days: int
    required_documents: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    approval_needed: bool = False

@dataclass
class WorkflowTemplate:
    """Workflow-Template für bestimmte Szenarien"""
    trigger_type: WorkflowTriggerType
    name: str
    description: str
    actions: List[WorkflowAction]
    estimated_duration: int  # Tage
    compliance_relevant: bool = True

@dataclass
class TriggeredWorkflow:
    """Ein ausgelöster Workflow"""
    id: str
    trigger_type: WorkflowTriggerType
    template_name: str
    context: Dict[str, Any]
    created_at: datetime
    created_by: int
    actions: List[WorkflowAction]
    generated_tasks: List[int] = field(default_factory=list)
    status: str = "active"

class IntelligentWorkflowEngine:
    """🧠 Intelligente Workflow-Engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm_provider = GoogleGeminiProvider()
        self.active_workflows: Dict[str, TriggeredWorkflow] = {}
        
        # Workflow-Templates laden
        self.templates = self._load_workflow_templates()
        
    def _load_workflow_templates(self) -> Dict[WorkflowTriggerType, List[WorkflowTemplate]]:
        """Lädt vordefinierte Workflow-Templates"""
        
        templates = {
            WorkflowTriggerType.SUPPLIER_ISSUE: [
                WorkflowTemplate(
                    trigger_type=WorkflowTriggerType.SUPPLIER_ISSUE,
                    name="Lieferanten-Krise Management",
                    description="Kompletter Workflow bei Lieferantenproblemen",
                    estimated_duration=30,
                    actions=[
                        WorkflowAction(
                            interest_group="Entwicklung",
                            action_type="evaluation",
                            title="Ersatzkomponente identifizieren und evaluieren",
                            description="Alternative Komponenten recherchieren, technische Spezifikationen prüfen, Kompatibilität bewerten",
                            priority="HIGH",
                            due_days=5,
                            required_documents=["Anforderungsspezifikation", "Testprotokoll"],
                            approval_needed=True
                        ),
                        WorkflowAction(
                            interest_group="Einkauf",
                            action_type="sourcing",
                            title="Ersatzlieferant identifizieren",
                            description="Neue Lieferanten recherchieren, Angebote einholen, Preisvergleich durchführen",
                            priority="HIGH", 
                            due_days=7,
                            required_documents=["Lieferantenbewertung", "Angebotsvergleich"]
                        ),
                        WorkflowAction(
                            interest_group="Einkauf",
                            action_type="audit",
                            title="Lieferantenaudit durchführen",
                            description="Qualitätssystem des neuen Lieferanten prüfen, Audit-Bericht erstellen",
                            priority="HIGH",
                            due_days=14,
                            required_documents=["Audit-Checkliste", "Audit-Bericht", "Lieferantenfreigabe"],
                            prerequisites=["Ersatzlieferant identifiziert"]
                        ),
                        WorkflowAction(
                            interest_group="Produktion",
                            action_type="documentation", 
                            title="Arbeitsanweisungen aktualisieren",
                            description="Fertigungsanweisungen für neue Komponente anpassen, Prüfvorgaben updaten",
                            priority="MEDIUM",
                            due_days=10,
                            required_documents=["Arbeitsanweisung", "Prüfanweisung"],
                            prerequisites=["Ersatzkomponente approved"]
                        ),
                        WorkflowAction(
                            interest_group="Service",
                            action_type="documentation",
                            title="Serviceanleitung aktualisieren", 
                            description="Service-Dokumentation für neue Komponente erstellen, Fehlerbehebung anpassen",
                            priority="MEDIUM",
                            due_days=12,
                            required_documents=["Serviceanleitung", "Ersatzteilkatalog"]
                        ),
                        WorkflowAction(
                            interest_group="Dokumentation",
                            action_type="documentation",
                            title="Bedienungsanleitung überarbeiten",
                            description="Bedienungsanleitung an neue Komponente anpassen, technische Daten updaten",
                            priority="MEDIUM", 
                            due_days=15,
                            required_documents=["Bedienungsanleitung", "Technische Dokumentation"]
                        ),
                        WorkflowAction(
                            interest_group="HR",
                            action_type="training",
                            title="Mitarbeiterschulung organisieren",
                            description="Schulung zu neuer Komponente für alle betroffenen Bereiche organisieren",
                            priority="MEDIUM",
                            due_days=20,
                            required_documents=["Schulungsplan", "Schulungsnachweis"]
                        ),
                        WorkflowAction(
                            interest_group="Management",
                            action_type="approval",
                            title="Änderung final freigeben",
                            description="Finale Freigabe der Komponentenänderung nach Abschluss aller Maßnahmen",
                            priority="HIGH",
                            due_days=25,
                            required_documents=["Änderungsantrag", "Freigabebescheinigung"],
                            prerequisites=["Alle anderen Tasks abgeschlossen"],
                            approval_needed=True
                        )
                    ]
                )
            ],
            
            WorkflowTriggerType.EQUIPMENT_FAILURE: [
                WorkflowTemplate(
                    trigger_type=WorkflowTriggerType.EQUIPMENT_FAILURE,
                    name="Geräteausfall Management",
                    description="Workflow bei kritischen Geräteausfällen",
                    estimated_duration=14,
                    actions=[
                        WorkflowAction(
                            interest_group="Technik",
                            action_type="assessment",
                            title="Geräteausfall analysieren",
                            description="Ursachenanalyse durchführen, Reparaturmöglichkeiten prüfen",
                            priority="CRITICAL",
                            due_days=1,
                            required_documents=["Fehlerbericht", "Diagnoseprotokoll"]
                        ),
                        WorkflowAction(
                            interest_group="Einkauf", 
                            action_type="sourcing",
                            title="Ersatzgerät oder Reparaturservice organisieren",
                            description="Reparaturdienstleister oder Ersatzgerät beschaffen",
                            priority="CRITICAL",
                            due_days=3,
                            required_documents=["Bestellung", "Liefertermin"]
                        ),
                        WorkflowAction(
                            interest_group="Produktion",
                            action_type="planning", 
                            title="Produktionsplanung anpassen",
                            description="Alternative Produktionsrouten planen, Kapazitäten umverteilen",
                            priority="HIGH",
                            due_days=2,
                            required_documents=["Produktionsplan", "Kapazitätsplanung"]
                        ),
                        WorkflowAction(
                            interest_group="QMB",
                            action_type="documentation",
                            title="Qualitätsauswirkungen bewerten",
                            description="Auswirkungen auf Produktqualität bewerten, CAPA einleiten",
                            priority="HIGH", 
                            due_days=5,
                            required_documents=["Qualitätsbewertung", "CAPA-Plan"]
                        )
                    ]
                )
            ],
            
            WorkflowTriggerType.CUSTOMER_COMPLAINT: [
                WorkflowTemplate(
                    trigger_type=WorkflowTriggerType.CUSTOMER_COMPLAINT,
                    name="Kundenbeschwerden Management", 
                    description="Vollständiger 8D-Prozess bei Kundenbeschwerden",
                    estimated_duration=21,
                    actions=[
                        WorkflowAction(
                            interest_group="QMB",
                            action_type="analysis",
                            title="Beschwerde analysieren und bewerten",
                            description="Erstbewertung der Beschwerde, Schweregrad bestimmen, 8D-Team zusammenstellen",
                            priority="CRITICAL",
                            due_days=1,
                            required_documents=["Beschwerdebericht", "8D-Report"]
                        ),
                        WorkflowAction(
                            interest_group="Entwicklung",
                            action_type="investigation",
                            title="Ursachenanalyse durchführen",
                            description="Root-Cause-Analysis, technische Untersuchung, Fehlerquelle identifizieren",
                            priority="HIGH",
                            due_days=7, 
                            required_documents=["Ursachenanalyse", "Testbericht"]
                        ),
                        WorkflowAction(
                            interest_group="Produktion",
                            action_type="correction",
                            title="Sofortmaßnahmen umsetzen",
                            description="Sofortige Korrekturmaßnahmen in der Produktion implementieren",
                            priority="HIGH",
                            due_days=3,
                            required_documents=["Korrekturmaßnahmen", "Umsetzungsnachweis"]
                        ),
                        WorkflowAction(
                            interest_group="Service",
                            action_type="customer_care",
                            title="Kundenbetreuung und Kommunikation",
                            description="Kunde über Maßnahmen informieren, Kulanz prüfen, Beziehung pflegen",
                            priority="HIGH",
                            due_days=5,
                            required_documents=["Kundenkommunikation", "Kulanzentscheidung"]
                        )
                    ]
                )
            ]
        }
        
        return templates
    
    async def analyze_trigger_intent(self, message: str, context: Dict[str, Any] = None) -> Tuple[WorkflowTriggerType, float, Dict[str, Any]]:
        """
        Analysiert Benutzer-Input und identifiziert Workflow-Trigger
        
        Args:
            message: Benutzer-Nachricht
            context: Zusätzlicher Kontext
            
        Returns:
            Tuple[WorkflowTriggerType, confidence, extracted_context]
        """
        if not await self.llm_provider.is_available():
            # Fallback: Rule-based Intent Recognition
            return self._rule_based_intent_analysis(message)
        
        try:
            # KI-basierte Intent-Erkennung
            prompt = f"""
Analysiere diese Nachricht und identifiziere den QMS-Workflow-Trigger:

NACHRICHT: "{message}"

VERFÜGBARE TRIGGER-TYPEN:
- SUPPLIER_ISSUE: Lieferantenprobleme (z.B. "Bluetooth Modul nicht lieferbar")
- COMPONENT_CHANGE: Bauteil-Änderungen (z.B. "CPU muss getauscht werden")
- EQUIPMENT_FAILURE: Geräteausfälle (z.B. "Lötofen ist defekt")
- COMPLIANCE_GAP: Compliance-Lücken (z.B. "ISO 13485 Anforderung fehlt")
- CUSTOMER_COMPLAINT: Kundenbeschwerden (z.B. "Kunde beschwert sich über Fehler")
- AUDIT_FINDING: Audit-Befunde (z.B. "Internes Audit fand Abweichung")
- PROCESS_IMPROVEMENT: Prozessverbesserungen
- DOCUMENT_UPDATE: Dokument-Updates
- TRAINING_NEED: Schulungsbedarf
- RISK_IDENTIFIED: Identifizierte Risiken

Antworte NUR mit JSON:
{{
    "trigger_type": "TRIGGER_TYPE",
    "confidence": 0.95,
    "extracted_context": {{
        "component": "Bluetooth Modul",
        "supplier": "Acme Corp",
        "urgency": "high",
        "affected_products": ["Produkt A", "Produkt B"]
    }}
}}
"""
            
            result = await self.llm_provider.analyze_document(prompt, "INTENT_ANALYSIS")
            ai_response = result.get("ai_summary", "{}")
            
            # JSON parsen
            try:
                parsed = json.loads(ai_response)
                trigger_type = WorkflowTriggerType(parsed["trigger_type"].lower())
                confidence = float(parsed["confidence"])
                extracted_context = parsed.get("extracted_context", {})
                
                return trigger_type, confidence, extracted_context
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                self.logger.warning(f"KI-Intent-Parsing fehlgeschlagen: {e}")
                return self._rule_based_intent_analysis(message)
                
        except Exception as e:
            self.logger.error(f"KI-Intent-Analyse fehlgeschlagen: {e}")
            return self._rule_based_intent_analysis(message)
    
    def _rule_based_intent_analysis(self, message: str) -> Tuple[WorkflowTriggerType, float, Dict[str, Any]]:
        """Fallback: Regelbasierte Intent-Erkennung"""
        message_lower = message.lower()
        
        # Keywords für verschiedene Trigger
        trigger_keywords = {
            WorkflowTriggerType.SUPPLIER_ISSUE: [
                "lieferant", "nicht lieferbar", "ausverkauft", "lieferstopp", 
                "supplier", "nicht verfügbar", "modul nicht", "bauteil nicht"
            ],
            WorkflowTriggerType.EQUIPMENT_FAILURE: [
                "defekt", "kaputt", "ausfall", "funktioniert nicht", "gerät", 
                "maschine", "anlage", "störung", "fehler"
            ],
            WorkflowTriggerType.CUSTOMER_COMPLAINT: [
                "beschwerde", "reklamation", "kunde unzufrieden", "customer complaint",
                "kunde beschwert", "problem mit produkt"
            ],
            WorkflowTriggerType.COMPONENT_CHANGE: [
                "ändern", "ersetzen", "tauschen", "wechseln", "komponente", 
                "bauteil", "change", "update"
            ]
        }
        
        # Score für jeden Trigger berechnen
        scores = {}
        for trigger, keywords in trigger_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                scores[trigger] = score / len(keywords)
        
        if scores:
            best_trigger = max(scores, key=scores.get)
            confidence = min(0.8, scores[best_trigger] * 2)  # Max 80% für rule-based
            
            # Einfache Kontext-Extraktion
            context = {"source": "rule_based", "keywords_matched": scores[best_trigger]}
            
            return best_trigger, confidence, context
        
        # Default: Allgemeiner Trigger
        return WorkflowTriggerType.PROCESS_IMPROVEMENT, 0.3, {"source": "default"}
    
    async def trigger_workflow(self, 
                             trigger_type: WorkflowTriggerType, 
                             context: Dict[str, Any],
                             user_id: int,
                             db) -> TriggeredWorkflow:
        """
        Löst einen Workflow aus - DER MAGIC MOMENT!
        
        Args:
            trigger_type: Art des Triggers
            context: Kontext-Informationen
            user_id: ID des auslösenden Benutzers
            db: Datenbank-Session
            
        Returns:
            TriggeredWorkflow: Der ausgelöste Workflow
        """
        # Template für Trigger finden
        templates = self.templates.get(trigger_type, [])
        if not templates:
            raise ValueError(f"Kein Template für Trigger {trigger_type} gefunden")
        
        # Erstes Template verwenden (später: intelligente Auswahl)
        template = templates[0]
        
        # Workflow-ID generieren
        workflow_id = f"wf_{trigger_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Workflow erstellen
        workflow = TriggeredWorkflow(
            id=workflow_id,
            trigger_type=trigger_type,
            template_name=template.name,
            context=context,
            created_at=datetime.utcnow(),
            created_by=user_id,
            actions=template.actions.copy()
        )
        
        # Tasks in Datenbank erstellen
        created_tasks = await self._create_workflow_tasks(workflow, template, db)
        workflow.generated_tasks = [task.id for task in created_tasks]
        
        # Workflow speichern
        self.active_workflows[workflow_id] = workflow
        
        self.logger.info(f"🚀 Workflow '{template.name}' ausgelöst: {len(created_tasks)} Tasks erstellt")
        
        return workflow
    
    async def _create_workflow_tasks(self, workflow: TriggeredWorkflow, template: WorkflowTemplate, db) -> List[QMSTask]:
        """Erstellt alle Tasks für einen Workflow"""
        from sqlalchemy.orm import Session
        
        created_tasks = []
        
        try:
            for action in template.actions:
                # Interesse Group finden
                interest_group = db.query(InterestGroup).filter(
                    InterestGroup.name.ilike(f"%{action.interest_group}%")
                ).first()
                
                if not interest_group:
                    self.logger.warning(f"Interest Group '{action.interest_group}' nicht gefunden")
                    continue
                
                # Due Date berechnen
                due_date = datetime.utcnow() + timedelta(days=action.due_days)
                
                # Task erstellen
                task = QMSTask(
                    title=action.title,
                    description=action.description,
                    status=TaskStatus.OPEN,
                    priority=action.priority,
                    assigned_group_id=interest_group.id,
                    created_by=workflow.created_by,
                    due_date=due_date,
                    workflow_id=workflow.id,
                    workflow_context=json.dumps(workflow.context),
                    required_documents=json.dumps(action.required_documents),
                    prerequisites=json.dumps(action.prerequisites),
                    approval_needed=action.approval_needed
                )
                
                db.add(task)
                created_tasks.append(task)
            
            db.commit()
            
            # IDs nach Commit verfügbar
            for task in created_tasks:
                db.refresh(task)
            
            return created_tasks
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Task-Erstellung fehlgeschlagen: {e}")
            raise
    
    async def process_message_trigger(self, message: str, user_id: int, db) -> Dict[str, Any]:
        """
        Verarbeitet eine Nachricht und löst ggf. Workflows aus
        
        Args:
            message: Benutzer-Nachricht
            user_id: ID des Benutzers
            db: Datenbank-Session
            
        Returns:
            Dict: Ergebnis der Verarbeitung
        """
        try:
            # 1. Intent analysieren
            trigger_type, confidence, context = await self.analyze_trigger_intent(message)
            
            # 2. Schwellwert prüfen
            if confidence < 0.5:
                return {
                    "workflow_triggered": False,
                    "message": "Nachricht erkannt, aber kein eindeutiger Workflow-Trigger identifiziert",
                    "confidence": confidence,
                    "detected_intent": trigger_type.value
                }
            
            # 3. Workflow auslösen
            workflow = await self.trigger_workflow(trigger_type, context, user_id, db)
            
            return {
                "workflow_triggered": True,
                "workflow_id": workflow.id,
                "workflow_name": workflow.template_name,
                "tasks_created": len(workflow.generated_tasks),
                "estimated_duration": self.templates[trigger_type][0].estimated_duration,
                "message": f"Workflow '{workflow.template_name}' automatisch ausgelöst! {len(workflow.generated_tasks)} Aufgaben erstellt.",
                "confidence": confidence
            }
            
        except Exception as e:
            self.logger.error(f"Message-Trigger-Verarbeitung fehlgeschlagen: {e}")
            return {
                "workflow_triggered": False,
                "error": str(e),
                "message": "Fehler bei der Workflow-Auslösung"
            }
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Status eines Workflows abrufen"""
        if workflow_id not in self.active_workflows:
            return None
        
        workflow = self.active_workflows[workflow_id]
        
        return {
            "id": workflow.id,
            "trigger_type": workflow.trigger_type.value,
            "template_name": workflow.template_name,
            "created_at": workflow.created_at.isoformat(),
            "status": workflow.status,
            "total_tasks": len(workflow.generated_tasks),
            "context": workflow.context
        }
    
    async def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Alle aktiven Workflows abrufen"""
        return [
            await self.get_workflow_status(wf_id) 
            for wf_id in self.active_workflows.keys()
        ]

# Globale Engine-Instanz
intelligent_workflow_engine = IntelligentWorkflowEngine() 