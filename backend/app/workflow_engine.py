"""
KI-QMS Workflow Engine - Automatische Aufgabenteilung

Dieses Modul implementiert die automatische Verteilung von Dokumenten
an die entsprechenden Interessengruppen basierend auf Dokumenttyp
und definierten Geschäftsregeln.

KRITISCH: Dies ist das fehlende Bindeglied zwischen Dokumenten-Upload
und Interessengruppen-Benachrichtigungen!

Funktionalitäten:
- Automatisches Routing basierend auf Dokumenttyp
- Freigabe-Ketten-Generierung (Approval Chains)
- Task-Assignment für Interessengruppen
- Eskalations-Management bei überfälligen Tasks
- Integration mit Email-Benachrichtigungssystem

Autoren: KI-QMS Entwicklungsteam
Version: 1.0.0 (Phase 1)
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from .models import (
    Document, DocumentType, DocumentStatus,
    InterestGroup, User, UserGroupMembership
)

logger = logging.getLogger(__name__)

# ===== WORKFLOW DATENSTRUKTUREN =====

@dataclass
class ApprovalStep:
    """Einzelner Schritt in einer Freigabe-Kette"""
    group_code: str
    group_name: str
    step_order: int
    is_required: bool = True
    approval_level_required: int = 2  # 1=Standard, 2=Teamleiter, 3=Abteilungsleiter, 4=QM-Manager
    estimated_duration_hours: int = 24
    
@dataclass
class WorkflowTask:
    """Aufgabe für eine Interessengruppe"""
    document_id: int
    group_code: str
    task_type: str  # "review", "approve", "notify"
    priority: str   # "low", "medium", "high", "critical"
    due_date: datetime
    assigned_at: datetime
    status: str = "pending"  # "pending", "in_progress", "completed", "overdue"
    assigned_user_id: Optional[int] = None
    completion_comment: Optional[str] = None

class TaskType(Enum):
    """Typen von Workflow-Aufgaben"""
    REVIEW = "review"           # Fachliche Prüfung
    APPROVE = "approve"         # Offizielle Freigabe
    NOTIFY = "notify"           # Information erhalten
    VALIDATE = "validate"       # Technische Validierung
    IMPLEMENT = "implement"     # Umsetzung/Integration

class Priority(Enum):
    """Prioritätsstufen für Tasks"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

# ===== WORKFLOW-REGELN DEFINITION =====

WORKFLOW_RULES: Dict[DocumentType, Dict] = {
    # === KERN-QM-DOKUMENTE ===
    DocumentType.QM_MANUAL: {
        "required_groups": ["development", "quality_management"],
        "approval_sequence": [
            ApprovalStep("development", "Entwicklung", 1, True, 3, 48),
            ApprovalStep("quality_management", "Qualitätsmanagement", 2, True, 4, 24)
        ],
        "notification_groups": ["quality_management", "documentation", "regulatory"],
        "priority": Priority.CRITICAL,
        "estimated_completion_days": 7
    },
    
    DocumentType.SOP: {
        "required_groups": ["production", "quality_management"],
        "approval_sequence": [
            ApprovalStep("production", "Produktion", 1, True, 2, 24),
            ApprovalStep("quality_management", "Qualitätsmanagement", 2, True, 3, 24)
        ],
        "notification_groups": ["hr_training", "production", "service_support"],
        "priority": Priority.HIGH,
        "estimated_completion_days": 5
    },
    
    DocumentType.WORK_INSTRUCTION: {
        "required_groups": ["production", "hr_training"],
        "approval_sequence": [
            ApprovalStep("production", "Produktion", 1, True, 2, 24),
            ApprovalStep("hr_training", "HR/Schulung", 2, True, 2, 24)
        ],
        "notification_groups": ["production", "quality_management"],
        "priority": Priority.MEDIUM,
        "estimated_completion_days": 3
    },
    
    # === ANALYSE & VALIDIERUNG ===
    DocumentType.RISK_ASSESSMENT: {
        "required_groups": ["development", "regulatory", "quality_management"],
        "approval_sequence": [
            ApprovalStep("development", "Entwicklung", 1, True, 3, 48),
            ApprovalStep("regulatory", "Regulatory Affairs", 2, True, 3, 48),
            ApprovalStep("quality_management", "Qualitätsmanagement", 3, True, 4, 24)
        ],
        "notification_groups": ["quality_management", "regulatory", "development"],
        "priority": Priority.CRITICAL,
        "estimated_completion_days": 10
    },
    
    DocumentType.VALIDATION_PROTOCOL: {
        "required_groups": ["development", "quality_management", "production"],
        "approval_sequence": [
            ApprovalStep("development", "Entwicklung", 1, True, 3, 48),
            ApprovalStep("production", "Produktion", 2, True, 2, 24),
            ApprovalStep("quality_management", "Qualitätsmanagement", 3, True, 3, 24)
        ],
        "notification_groups": ["it_department", "regulatory"],
        "priority": Priority.HIGH,
        "estimated_completion_days": 7
    },
    
    DocumentType.CALIBRATION_PROCEDURE: {
        "required_groups": ["production", "quality_management"],
        "approval_sequence": [
            ApprovalStep("production", "Produktion", 1, True, 2, 24),
            ApprovalStep("quality_management", "Qualitätsmanagement", 2, True, 3, 24)
        ],
        "notification_groups": ["production", "service_support"],
        "priority": Priority.MEDIUM,
        "estimated_completion_days": 3
    },
    
    # === TRAINING & DOKUMENTATION ===
    DocumentType.USER_MANUAL: {
        "required_groups": ["documentation", "service_support"],
        "approval_sequence": [
            ApprovalStep("documentation", "Dokumentation", 1, True, 2, 48),
            ApprovalStep("service_support", "Service/Support", 2, True, 2, 24)
        ],
        "notification_groups": ["sales", "service_support", "hr_training"],
        "priority": Priority.MEDIUM,
        "estimated_completion_days": 5
    },
    
    DocumentType.TRAINING_MATERIAL: {
        "required_groups": ["hr_training", "quality_management"],
        "approval_sequence": [
            ApprovalStep("hr_training", "HR/Schulung", 1, True, 2, 48),
            ApprovalStep("quality_management", "Qualitätsmanagement", 2, True, 3, 24)
        ],
        "notification_groups": ["hr_training", "production", "service_support"],
        "priority": Priority.MEDIUM,
        "estimated_completion_days": 4
    },
    
    # === COMPLIANCE & STANDARDS ===
    DocumentType.STANDARD_NORM: {
        "required_groups": ["regulatory", "quality_management"],
        "approval_sequence": [
            ApprovalStep("regulatory", "Regulatory Affairs", 1, True, 3, 72),
            ApprovalStep("quality_management", "Qualitätsmanagement", 2, True, 4, 24)
        ],
        "notification_groups": ["development", "production", "regulatory"],
        "priority": Priority.HIGH,
        "estimated_completion_days": 7
    },
    
    DocumentType.AUDIT_REPORT: {
        "required_groups": ["quality_management", "external_auditors"],
        "approval_sequence": [
            ApprovalStep("external_auditors", "Externe Auditoren", 1, True, 3, 48),
            ApprovalStep("quality_management", "Qualitätsmanagement", 2, True, 4, 24)
        ],
        "notification_groups": ["quality_management", "regulatory", "development"],
        "priority": Priority.HIGH,
        "estimated_completion_days": 5
    },
    
    # === DEFAULT FÜR ANDERE TYPEN ===
    DocumentType.OTHER: {
        "required_groups": ["quality_management"],
        "approval_sequence": [
            ApprovalStep("quality_management", "Qualitätsmanagement", 1, True, 3, 48)
        ],
        "notification_groups": ["quality_management"],
        "priority": Priority.MEDIUM,
        "estimated_completion_days": 3
    }
}

# ===== WORKFLOW ENGINE KLASSE =====

class WorkflowEngine:
    """
    Zentrale Engine für automatisches Dokumenten-Routing und Task-Management.
    
    Funktionalitäten:
    - Routing von Dokumenten zu passenden Interessengruppen
    - Generierung von Freigabe-Ketten (Approval Chains)
    - Task-Erstellung und -Verwaltung
    - Benachrichtigungs-Trigger
    - Eskalations-Management
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.WorkflowEngine")
        
    def route_document(self, document: Document) -> List[str]:
        """
        Bestimmt welche Interessengruppen bei einem Dokumenttyp aktiv werden.
        
        Args:
            document: Das zu routende Dokument
            
        Returns:
            Liste von Interessengruppen-Codes die benachrichtigt werden sollen
        """
        doc_type = document.document_type
        
        if doc_type not in WORKFLOW_RULES:
            self.logger.warning(f"Kein Workflow für Dokumenttyp {doc_type}, verwende DEFAULT")
            doc_type = DocumentType.OTHER
            
        rules = WORKFLOW_RULES[doc_type]
        
        # Kombiniere alle beteiligten Gruppen
        all_groups = set()
        all_groups.update(rules.get("required_groups", []))
        all_groups.update(rules.get("notification_groups", []))
        
        self.logger.info(
            f"Dokument {document.id} ({doc_type}) → Gruppen: {list(all_groups)}"
        )
        
        return list(all_groups)
    
    def create_approval_chain(self, document: Document) -> List[ApprovalStep]:
        """
        Erstellt die Freigabe-Kette für ein Dokument.
        
        Args:
            document: Das Dokument für das die Freigabe-Kette erstellt wird
            
        Returns:
            Liste von ApprovalStep-Objekten in der korrekten Reihenfolge
        """
        doc_type = document.document_type
        
        if doc_type not in WORKFLOW_RULES:
            doc_type = DocumentType.OTHER
            
        rules = WORKFLOW_RULES[doc_type]
        approval_sequence = rules.get("approval_sequence", [])
        
        self.logger.info(
            f"Freigabe-Kette für Dokument {document.id}: "
            f"{[step.group_code for step in approval_sequence]}"
        )
        
        return approval_sequence
    
    def create_workflow_tasks(self, document: Document) -> List[WorkflowTask]:
        """
        Erstellt Workflow-Tasks für alle beteiligten Interessengruppen.
        
        Args:
            document: Das Dokument für das Tasks erstellt werden
            
        Returns:
            Liste von WorkflowTask-Objekten
        """
        doc_type = document.document_type
        if doc_type not in WORKFLOW_RULES:
            doc_type = DocumentType.OTHER
            
        rules = WORKFLOW_RULES[doc_type]
        approval_steps = rules.get("approval_sequence", [])
        notification_groups = rules.get("notification_groups", [])
        priority = rules.get("priority", Priority.MEDIUM)
        
        tasks = []
        now = datetime.utcnow()
        
        # Tasks für Freigabe-Kette erstellen
        for step in approval_steps:
            due_date = now + timedelta(hours=step.estimated_duration_hours)
            
            task = WorkflowTask(
                document_id=document.id,
                group_code=step.group_code,
                task_type=TaskType.APPROVE.value,
                priority=priority.value,
                due_date=due_date,
                assigned_at=now
            )
            tasks.append(task)
            
        # Tasks für Benachrichtigungsgruppen erstellen
        for group_code in notification_groups:
            # Keine doppelten Tasks für Gruppen die schon in Approval-Chain sind
            if not any(task.group_code == group_code for task in tasks):
                task = WorkflowTask(
                    document_id=document.id,
                    group_code=group_code,
                    task_type=TaskType.NOTIFY.value,
                    priority=Priority.LOW.value,
                    due_date=now + timedelta(hours=24),
                    assigned_at=now
                )
                tasks.append(task)
        
        self.logger.info(f"Erstellt {len(tasks)} Tasks für Dokument {document.id}")
        return tasks
    
    def get_next_approval_step(self, document: Document) -> Optional[ApprovalStep]:
        """
        Bestimmt den nächsten erforderlichen Freigabe-Schritt.
        
        Args:
            document: Das Dokument
            
        Returns:
            Nächster ApprovalStep oder None wenn keine Freigabe erforderlich
        """
        approval_chain = self.create_approval_chain(document)
        
        # TODO: Hier müsste geprüft werden welche Schritte bereits abgeschlossen sind
        # Das erfordert eine Erweiterung des Document-Models um approval_history
        
        # Für jetzt: Ersten Schritt zurückgeben wenn Status DRAFT
        if document.status == DocumentStatus.DRAFT and approval_chain:
            return approval_chain[0]
            
        return None
    
    def check_approval_requirements(self, document: Document) -> Dict[str, any]:
        """
        Prüft ob alle erforderlichen Freigaben vorhanden sind.
        
        Args:
            document: Das zu prüfende Dokument
            
        Returns:
            Dictionary mit Approval-Status und fehlenden Freigaben
        """
        approval_chain = self.create_approval_chain(document)
        
        # TODO: Implementierung erfordert approval_history in Document-Model
        
        result = {
            "all_approvals_complete": False,
            "required_approvals": len(approval_chain),
            "completed_approvals": 0,
            "missing_approvals": [step.group_code for step in approval_chain],
            "can_be_approved": document.status in [DocumentStatus.DRAFT, DocumentStatus.REVIEWED]
        }
        
        return result
    
    def get_workflow_summary(self, document: Document) -> Dict[str, any]:
        """
        Erstellt eine Zusammenfassung des Workflow-Status für ein Dokument.
        
        Args:
            document: Das Dokument
            
        Returns:
            Dictionary mit vollständiger Workflow-Information
        """
        doc_type = document.document_type
        if doc_type not in WORKFLOW_RULES:
            doc_type = DocumentType.OTHER
            
        rules = WORKFLOW_RULES[doc_type]
        approval_chain = self.create_approval_chain(document)
        next_step = self.get_next_approval_step(document)
        approval_status = self.check_approval_requirements(document)
        
        summary = {
            "document_id": document.id,
            "document_type": doc_type.value,
            "current_status": document.status.value,
            "workflow_rules": {
                "priority": rules.get("priority", Priority.MEDIUM).value,
                "estimated_completion_days": rules.get("estimated_completion_days", 3),
                "required_groups": rules.get("required_groups", []),
                "notification_groups": rules.get("notification_groups", [])
            },
            "approval_chain": [
                {
                    "step_order": step.step_order,
                    "group_code": step.group_code,
                    "group_name": step.group_name,
                    "is_required": step.is_required,
                    "approval_level_required": step.approval_level_required,
                    "estimated_duration_hours": step.estimated_duration_hours
                }
                for step in approval_chain
            ],
            "next_approval_step": {
                "group_code": next_step.group_code,
                "group_name": next_step.group_name,
                "approval_level_required": next_step.approval_level_required
            } if next_step else None,
            "approval_status": approval_status
        }
        
        return summary

# ===== HELPER FUNCTIONS =====

def get_workflow_engine() -> WorkflowEngine:
    """Factory function für WorkflowEngine Instanz"""
    return WorkflowEngine()

def get_document_priority(document_type: DocumentType) -> Priority:
    """Bestimmt die Priorität eines Dokumenttyps"""
    rules = WORKFLOW_RULES.get(document_type, WORKFLOW_RULES[DocumentType.OTHER])
    return rules.get("priority", Priority.MEDIUM)

def get_estimated_completion_time(document_type: DocumentType) -> int:
    """Geschätzte Bearbeitungszeit in Tagen für einen Dokumenttyp"""
    rules = WORKFLOW_RULES.get(document_type, WORKFLOW_RULES[DocumentType.OTHER])
    return rules.get("estimated_completion_days", 3)

def validate_workflow_rules() -> bool:
    """
    Validiert die Konsistenz der Workflow-Regeln.
    
    Returns:
        True wenn alle Regeln valide sind
    """
    logger = logging.getLogger(f"{__name__}.validate_workflow_rules")
    
    for doc_type, rules in WORKFLOW_RULES.items():
        try:
            # Prüfe erforderliche Felder
            assert "required_groups" in rules
            assert "approval_sequence" in rules
            assert "notification_groups" in rules
            
            # Prüfe Approval Sequence
            approval_sequence = rules["approval_sequence"]
            assert isinstance(approval_sequence, list)
            
            for i, step in enumerate(approval_sequence):
                assert isinstance(step, ApprovalStep)
                assert step.step_order == i + 1
                
            logger.debug(f"Workflow-Regeln für {doc_type} sind valide")
            
        except Exception as e:
            logger.error(f"Ungültige Workflow-Regeln für {doc_type}: {e}")
            return False
    
    logger.info("Alle Workflow-Regeln sind valide")
    return True

# ===== INITIALISIERUNG =====

# Validiere Workflow-Regeln beim Import
if not validate_workflow_rules():
    raise ValueError("Ungültige Workflow-Regeln konfiguriert!") 