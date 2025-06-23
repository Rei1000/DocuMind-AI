#!/usr/bin/env python3
"""
KI-QMS Master Interest Groups Definition

Diese Datei definiert die DEFINITIVEN 13 Interessengruppen für das KI-QMS System.
Alle anderen Scripts und Module MÜSSEN diese Definition verwenden.

WICHTIG: Diese Gruppen sind strategisch für Workflow-Automatisierung optimiert!

QMS-SYSTEM-ADMINISTRATOR KONZEPT:
=================================
Es gibt einen wichtigen Unterschied zwischen:

1. IT-ABTEILUNG (Interessengruppe):
   - Code: "it_department" 
   - Teil des QMS-Stakeholder-Systems
   - Aufgaben: Software-Validierung, IT-QM-Prozesse, System-Dokumentation
   - KEINE system_administration Rechte!

2. QMS-SYSTEM-ADMINISTRATOR (separate Rolle):
   - Nicht Teil der 13 Interessengruppen
   - Technische System-Administration
   - Berechtigungen: system_administration, user_management, backup_management
   - Unabhängig von fachlichen QM-Prozessen
   - Wird über individual_permissions vergeben

Diese Trennung gewährleistet ISO 13485 Compliance durch klare Rollentrennung!

Autoren: KI-QMS Entwicklungsteam
Version: 1.2.0 (IT-Administrator Trennung implementiert)
"""

import json

# === DEFINITIVE 13 INTERESSENGRUPPEN ===
MASTER_INTEREST_GROUPS = [
    {
        "name": "Team/Eingangsmodul", 
        "code": "input_team",
        "description": "Email-Analyse, Meeting-Protokolle, Trigger-Erkennung - Das Nervensystem des QMS",
        "group_permissions": [
            "email_analysis", "meeting_transcripts", "trigger_recognition", 
            "input_capture", "workflow_initiation", "cross_functional_coordination"
        ],
        "ai_functionality": "Email-Analyse, Meeting-Protokolle, Trigger-Erkennung",
        "typical_tasks": "Bluetooth-Abkündigungen erfassen, Change-Requests initiieren, Meeting-Protokolle",
        "is_external": False,
        "priority": 1,  # Höchste Priorität - Das ist der Game Changer!
        "workflow_role": "trigger_initiator"
    },
    {
        "name": "Qualitätsmanagement", 
        "code": "quality_management",
        "description": "Finale Freigabe, Gap-Analyse, Compliance-Überwachung - QMS-Herzstück",
        "group_permissions": [
            "final_approval", "gap_analysis", "norm_checking", "audit_management", 
            "capa_coordination", "system_administration", "workflow_oversight"
        ],
        "ai_functionality": "Gap-Analyse, Norm-Compliance-Prüfung, Workflow-Überwachung",
        "typical_tasks": "Finale Freigaben, CAPA-Management, Compliance-Überwachung, Audit-Koordination",
        "is_external": False,
        "priority": 2,  # Zweithöchste - Finale Kontrolle
        "workflow_role": "final_approver"
    },
    {
        "name": "Entwicklung", 
        "code": "development",
        "description": "Design-Control, Ersatzbauteil-Definition, technische Spezifikationen",
        "group_permissions": [
            "design_control", "component_specification", "technical_documentation", 
            "change_management", "prototype_approval", "design_verification"
        ],
        "ai_functionality": "Design-Control, Kompatibilitätsprüfung, Spezifikations-Analyse",
        "typical_tasks": "Ersatzbauteile definieren, technische Spezifikationen, Design-Änderungen",
        "is_external": False,
        "priority": 3,
        "workflow_role": "technical_designer"
    },
    {
        "name": "Einkauf", 
        "code": "procurement",
        "description": "Lieferantenbewertung, Beschaffung, Vendor-Management",
        "group_permissions": [
            "supplier_evaluation", "vendor_management", "purchase_approval", 
            "supplier_audit", "cost_analysis", "contract_management"
        ],
        "ai_functionality": "Lieferantenbewertung, Preisanalyse, Verfügbarkeits-Checks",
        "typical_tasks": "Neue Lieferanten finden, Lieferanten-Audits, Beschaffungs-Koordination",
        "is_external": False,
        "priority": 4,
        "workflow_role": "supplier_coordinator"
    },
    {
        "name": "Produktion", 
        "code": "production",
        "description": "Fertigungssteuerung, Bauteil-Integration, Arbeitsanweisungen",
        "group_permissions": [
            "production_planning", "work_instructions", "quality_control", 
            "process_optimization", "equipment_management", "production_approval"
        ],
        "ai_functionality": "Arbeitsanweisungen-Generierung, Prozess-Optimierung",
        "typical_tasks": "Bauteil-Integration planen, Arbeitsanweisungen anpassen, Qualitätskontrolle",
        "is_external": False,
        "priority": 5,
        "workflow_role": "production_integrator"
    },
    {
        "name": "HR/Schulung", 
        "code": "hr_training",
        "description": "Mitarbeiter-Qualifikation, Schulungsplanung, Kompetenz-Management",
        "group_permissions": [
            "training_management", "competence_tracking", "qualification_approval", 
            "training_planning", "skill_assessment", "certification_management"
        ],
        "ai_functionality": "Schulungsbedarfs-Analyse, Kompetenz-Matching",
        "typical_tasks": "Schulungen für neue Bauteile, Mitarbeiter-Qualifikation, Zertifizierungen",
        "is_external": False,
        "priority": 6,
        "workflow_role": "training_coordinator"
    },
    {
        "name": "Dokumentation", 
        "code": "documentation",
        "description": "Technische Dokumentation, Anleitungen, Handbücher",
        "group_permissions": [
            "document_creation", "manual_updates", "translation_management", 
            "version_control", "template_management", "document_approval"
        ],
        "ai_functionality": "Dokumenten-Generierung, Übersetzungs-Hilfe, Template-Optimierung",
        "typical_tasks": "Bedienungsanleitungen anpassen, Service-Handbücher, Arbeitsanweisungen",
        "is_external": False,
        "priority": 7,
        "workflow_role": "documentation_manager"
    },
    {
        "name": "Service/Support", 
        "code": "service_support",
        "description": "Kundendienst, Field-Feedback, Post-Market-Surveillance",
        "group_permissions": [
            "customer_support", "field_feedback", "complaint_handling", 
            "post_market_surveillance", "repair_coordination", "customer_communication"
        ],
        "ai_functionality": "Beschwerdeanalyse, Trend-Erkennung, Field-Feedback-Auswertung",
        "typical_tasks": "Kundenfeedback sammeln, Service-Koordination, Post-Market-Surveillance",
        "is_external": False,
        "priority": 8,
        "workflow_role": "customer_interface"
    },
    {
        "name": "Vertrieb", 
        "code": "sales",
        "description": "Kundenanforderungen, Markt-Feedback, Vertriebsunterstützung",
        "group_permissions": [
            "customer_requirements", "market_analysis", "sales_support", 
            "customer_communication", "requirement_specification", "market_feedback"
        ],
        "ai_functionality": "Marktanalyse, Kundenanforderungs-Extraktion",
        "typical_tasks": "Kundenanforderungen sammeln, Markt-Feedback, Vertriebsunterstützung",
        "is_external": False,
        "priority": 9,
        "workflow_role": "market_interface"
    },
    {
        "name": "Regulatory Affairs", 
        "code": "regulatory",
        "description": "Zulassungen, Compliance, Behörden-Kommunikation",
        "group_permissions": [
            "regulatory_approval", "compliance_monitoring", "authority_communication", 
            "registration_management", "regulatory_documentation", "market_authorization"
        ],
        "ai_functionality": "Compliance-Checks, Zulassungs-Tracking",
        "typical_tasks": "Zulassungen für neue Bauteile, Compliance-Prüfungen, Behörden-Kommunikation",
        "is_external": False,
        "priority": 10,
        "workflow_role": "compliance_guardian"
    },
    {
        "name": "IT-Abteilung", 
        "code": "it_department",
        "description": "Software-Validierung, IT-QM-Prozesse, System-Dokumentation",
        "group_permissions": [
            "software_validation", "it_documentation", "system_qualification", 
            "software_testing", "it_process_management", "technical_compliance"
        ],
        "ai_functionality": "Software-Validierung, IT-Compliance-Checks, System-Dokumentation",
        "typical_tasks": "Software-Validierung, IT-QM-Prozesse, Systemdokumentation, Compliance",
        "is_external": False,
        "priority": 11,
        "workflow_role": "it_specialist"
    },
    {
        "name": "Externe Auditoren", 
        "code": "external_auditors",
        "description": "Unabhängige Qualitätsprüfung, Compliance-Audits",
        "group_permissions": [
            "read_only_access", "audit_trail_access", "compliance_reporting", 
            "gap_analysis", "certification_support", "external_assessment"
        ],
        "ai_functionality": "Audit-Unterstützung, Gap-Analyse, Compliance-Reports",
        "typical_tasks": "Externe Audits, Zertifizierungen, Compliance-Bewertungen",
        "is_external": True,
        "priority": 12,
        "workflow_role": "external_validator"
    },
    {
        "name": "Lieferanten", 
        "code": "suppliers",
        "description": "Externe Partner, Dokumenten-Upload, Selbstauskunft",
        "group_permissions": [
            "restricted_upload", "self_declaration", "document_submission", 
            "supplier_portal", "qualification_documents", "communication_interface"
        ],
        "ai_functionality": "Dokumenten-Validierung, Checklisten-Unterstützung",
        "typical_tasks": "Dokumentenübermittlung, Qualifikations-Nachweise, Selbstbewertung",
        "is_external": True,
        "priority": 13,
        "workflow_role": "external_contributor"
    }
]

# === HELPER FUNCTIONS ===

def get_group_by_code(code: str) -> dict | None:
    """Gruppe nach Code finden"""
    for group in MASTER_INTEREST_GROUPS:
        if group["code"] == code:
            return group
    return None

def get_internal_groups() -> list:
    """Nur interne Gruppen"""
    return [g for g in MASTER_INTEREST_GROUPS if not g["is_external"]]

def get_external_groups() -> list:
    """Nur externe Gruppen"""
    return [g for g in MASTER_INTEREST_GROUPS if g["is_external"]]

def get_workflow_roles() -> dict:
    """Mapping von Workflow-Rollen zu Gruppen"""
    return {g["workflow_role"]: g["code"] for g in MASTER_INTEREST_GROUPS}

def validate_consistency() -> bool:
    """Validiere Konsistenz der Gruppendefinitionen"""
    codes = [g["code"] for g in MASTER_INTEREST_GROUPS]
    names = [g["name"] for g in MASTER_INTEREST_GROUPS]
    
    # Prüfe auf Duplikate
    if len(codes) != len(set(codes)):
        print("❌ Fehler: Doppelte Codes gefunden!")
        return False
    
    if len(names) != len(set(names)):
        print("❌ Fehler: Doppelte Namen gefunden!")
        return False
    
    # Prüfe Anzahl
    if len(MASTER_INTEREST_GROUPS) != 13:
        print(f"❌ Fehler: {len(MASTER_INTEREST_GROUPS)} Gruppen statt 13!")
        return False
    
    print("✅ Interessengruppen-Konsistenz validiert!")
    return True

# === EXPORT FÜR SCRIPTS ===
def get_groups_for_db_init() -> list:
    """Formatiert für Datenbank-Initialisierung"""
    db_groups = []
    for group in MASTER_INTEREST_GROUPS:
        db_group = {
            "name": group["name"],
            "code": group["code"], 
            "description": group["description"],
            "group_permissions": json.dumps(group["group_permissions"]),
            "ai_functionality": group["ai_functionality"],
            "typical_tasks": group["typical_tasks"],
            "is_external": group["is_external"]
        }
        db_groups.append(db_group)
    return db_groups

def get_groups_for_update() -> list:
    """Formatiert für Datenbank-Update (mit JSON-String conversion)"""
    return MASTER_INTEREST_GROUPS  # Return original structure for update script

if __name__ == "__main__":
    print("🔍 KI-QMS Master Interest Groups Validation")
    print("=" * 50)
    
    validate_consistency()
    
    print(f"\n📊 Definierte Gruppen ({len(MASTER_INTEREST_GROUPS)}):")
    for i, group in enumerate(MASTER_INTEREST_GROUPS, 1):
        status = "🌐" if group["is_external"] else "🏢"
        print(f"  {i:2d}. {status} {group['name']} ({group['code']})")
    
    print(f"\n🏢 Interne Gruppen: {len(get_internal_groups())}")
    print(f"🌐 Externe Gruppen: {len(get_external_groups())}")
    
    print(f"\n🔄 Workflow-Rollen:")
    for role, code in get_workflow_roles().items():
        print(f"  • {role}: {code}") 