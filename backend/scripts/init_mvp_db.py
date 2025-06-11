#!/usr/bin/env python3
"""
KI-QMS Database Initialisierung mit Beispieldaten

Dieses Script initialisiert die MVP-Datenbank mit einem kompletten
Datensatz für Demonstrationszwecke. Es erstellt das 13-Interessensgruppen-System,
Beispielbenutzer, QMS-Dokumente, Normen und Equipment mit Kalibrierungen.

Hauptfunktionen:
- Vollständige Datenbank-Initialisierung
- 13 praxisorientierte Interessensgruppen
- Beispielbenutzer mit realistischen Profilen  
- QMS-Dokumente mit allen 14 Dokumenttypen
- Compliance-Normen (ISO 13485, MDR, etc.)
- Equipment mit Kalibrierungs-Tracking
- Überfällige Kalibrierung für Demo-Zwecke

Verwendung:
    python backend/scripts/init_mvp_db.py

Autoren: KI-QMS Entwicklungsteam  
Version: 1.0.0 (MVP Phase 1)
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Pfad zum app-Modul hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine, SessionLocal, create_tables
from app.models import InterestGroup, User, UserGroupMembership, Document, Equipment, Norm, DocumentStatus, EquipmentStatus, Calibration, DocumentType

def init_interest_groups(db):
    """
    Initialisiert die 13 praxisorientierten Interessensgruppen.
    
    Erstellt ein vollständiges Stakeholder-System für das QMS,
    von internen Teams bis zu externen Partnern. Jede Gruppe
    hat spezifische Berechtigungen und KI-Funktionalitäten.
    
    Args:
        db: SQLAlchemy Session für Datenbankoperationen
        
    Returns:
        list: Liste der erstellten InterestGroup-Objekte
        
    Gruppenkategorien:
        - Interne Stakeholder: Einkauf, QM, Entwicklung, etc.
        - Produktion & Service: Fertigung, Service, Schulung
        - Compliance: Regulatory Affairs, Auditoren
        - Externe Partner: Lieferanten, Distributoren, Kunden
    """
    
    groups_data = [
        {
            "name": "Einkauf",
            "code": "procurement",
            "description": "Lieferantenbewertung, Benachrichtigungen, Prozesstrigger",
            "group_permissions": json.dumps([
                "supplier_evaluation", "purchase_notifications", "process_triggers", "vendor_management"
            ]),
            "ai_functionality": "Lieferantenbewertung, Benachrichtigungen",
            "typical_tasks": "Lieferantenqualifikation, Einkaufsprozesse, Vendor-Management",
            "is_external": False
        },
        {
            "name": "Qualitätsmanagement (QM)",
            "code": "quality_management",
            "description": "Alle Rechte, finale Freigabe, Gap-Analyse - Herzstück des QMS",
            "group_permissions": json.dumps([
                "all_rights", "final_approval", "gap_analysis", "norm_checking", 
                "audit_management", "capa_coordination", "system_administration"
            ]),
            "ai_functionality": "Gap-Analyse & Normprüfung",
            "typical_tasks": "QM-Freigaben, CAPA-Management, interne Audits, Gap-Analysen",
            "is_external": False
        },
        {
            "name": "Produktion",
            "code": "production",
            "description": "Arbeitsanweisungen, Formularanalyse, Prozessvorschläge",
            "group_permissions": json.dumps([
                "work_instructions", "form_analysis", "process_suggestions", "production_records"
            ]),
            "ai_functionality": "Arbeitsanweisungen, Formularanalyse",
            "typical_tasks": "Fertigung, Qualitätskontrolle, Arbeitsanweisungen",
            "is_external": False
        },
        {
            "name": "Service/Reparatur",
            "code": "service_repair",
            "description": "Fehlerdokumentation, Beschwerdedatenanalyse",
            "group_permissions": json.dumps([
                "error_documentation", "complaint_analysis", "repair_records", "field_feedback"
            ]),
            "ai_functionality": "Fehlerdokumentation, Beschwerdedatenanalyse",
            "typical_tasks": "Reparaturen, Serviceberichte, Kundendienst",
            "is_external": False
        },
        {
            "name": "Entwicklung",
            "code": "development",
            "description": "Design-Control, Normprüfung",
            "group_permissions": json.dumps([
                "design_control", "norm_verification", "technical_documentation", "change_management"
            ]),
            "ai_functionality": "Design-Control, Normprüfung",
            "typical_tasks": "Produktentwicklung, Design-FMEA, technische Dokumentation",
            "is_external": False
        },
        {
            "name": "Wareneingang/-ausgang",
            "code": "warehouse_io",
            "description": "Prüfberichte, Überwachung Messmittel",
            "group_permissions": json.dumps([
                "inspection_reports", "measurement_equipment_monitoring", "incoming_inspection", "shipping_control"
            ]),
            "ai_functionality": "Prüfberichte, Überwachung Messmittel",
            "typical_tasks": "Eingangsprüfung, Versandkontrolle, Lagerverwaltung",
            "is_external": False
        },
        {
            "name": "Vertrieb",
            "code": "sales",
            "description": "Kundenanforderungen, CAPA-Initiation aus Beschwerden",
            "group_permissions": json.dumps([
                "customer_requirements", "capa_initiation", "complaint_handling", "customer_communication"
            ]),
            "ai_functionality": "Kundenanforderungen, CAPA-Initiation",
            "typical_tasks": "Kundenbetreuung, Anforderungsmanagement, Beschwerdebearbeitung",
            "is_external": False
        },
        {
            "name": "HR/Schulung",
            "code": "hr_training",
            "description": "Schulungsmanagement, Kompetenzüberwachung",
            "group_permissions": json.dumps([
                "training_management", "competence_tracking", "employee_records", "qualification_management"
            ]),
            "ai_functionality": "Schulungsmanagement, Kompetenzüberwachung",
            "typical_tasks": "Mitarbeiterschulungen, Qualifikationsnachweise, Personalentwicklung",
            "is_external": False
        },
        {
            "name": "Team/Eingangsmodul",
            "code": "input_team",
            "description": "Meeting-Protokolle, E-Mail-Analyse, Trigger-Erkennung - REVOLUTION!",
            "group_permissions": json.dumps([
                "meeting_transcripts", "email_analysis", "trigger_recognition", "input_capture"
            ]),
            "ai_functionality": "Meeting-Protokolle, E-Mail-Analyse, Trigger-Erkennung",
            "typical_tasks": "Informationserfassung, Meeting-Management, Ereignis-Triggers",
            "is_external": False
        },
        {
            "name": "Systemadmin/IT",
            "code": "system_admin",
            "description": "Systemweite Kontrolle, Zugriffskontrolle",
            "group_permissions": json.dumps([
                "system_wide_control", "access_monitoring", "technical_administration", "security_management"
            ]),
            "ai_functionality": "Systemweite Kontrolle, Zugriffskontrolle",
            "typical_tasks": "Systemverwaltung, Sicherheitsmanagement, technischer Support",
            "is_external": False
        },
        {
            "name": "Auditor (extern)",
            "code": "external_auditor",
            "description": "Read-only extern, Gap-API, Remote-Zugriff",
            "group_permissions": json.dumps([
                "read_only_external", "gap_api", "remote_access", "audit_trail_access"
            ]),
            "ai_functionality": "Read-only extern, Gap-API",
            "typical_tasks": "Externe Audits, Compliance-Prüfungen, Zertifizierungen",
            "is_external": True
        },
        {
            "name": "Controlling",
            "code": "controlling",
            "description": "Reports, Dashboards, KPIs",
            "group_permissions": json.dumps([
                "reports", "dashboards", "kpis", "financial_analysis"
            ]),
            "ai_functionality": "Reports, Dashboards, KPIs",
            "typical_tasks": "Berichtswesen, Kennzahlenanalyse, Wirtschaftlichkeitsprüfung",
            "is_external": False
        },
        {
            "name": "Lieferanten",
            "code": "suppliers",
            "description": "Beschränkter Upload, Selbstauskunft",
            "group_permissions": json.dumps([
                "restricted_upload", "self_declaration", "document_submission", "supplier_portal"
            ]),
            "ai_functionality": "Checklisten, Rückmeldungen",
            "typical_tasks": "Dokumentenübermittlung, Selbstbewertung, Lieferantenportal",
            "is_external": True
        }
    ]
    
    print("📊 Erstelle 13 Interessensgruppen...")
    for group_data in groups_data:
        existing_group = db.query(InterestGroup).filter(InterestGroup.code == group_data["code"]).first()
        if not existing_group:
            group = InterestGroup(**group_data)
            db.add(group)
            print(f"  ✅ {group_data['name']} ({group_data['code']})")
        else:
            print(f"  ⚠️  {group_data['name']} existiert bereits")
    
    db.commit()

def init_test_users(db):
    """Erstellt Testbenutzer aus allen 13 Interessensgruppen"""
    
    # Interessensgruppen aus DB laden
    groups = {g.code: g.id for g in db.query(InterestGroup).all()}
    
    test_users = [
        # 1. Einkauf
        {
            "email": "max.einkauf@company.com",
            "full_name": "Max Kaufmann",
            "employee_id": "EK001",
            "organizational_unit": "Einkauf",
            "hashed_password": "hashed_password123",
            "groups": ["procurement"]
        },
        
        # 2. QM (Zentrale Rolle)
        {
            "email": "maria.qm@company.com",
            "full_name": "Dr. Maria Qualität",
            "employee_id": "QM001",
            "organizational_unit": "Qualitätsmanagement",
            "hashed_password": "hashed_password123",
            "individual_permissions": ["final_approval", "system_administration", "audit_management"],
            "is_department_head": True,
            "approval_level": 4,
            "groups": ["quality_management"],
            "primary": "quality_management"
        },
        
        # 3. Produktion
        {
            "email": "hans.produktion@company.com",
            "full_name": "Hans Fertiger",
            "employee_id": "PR001",
            "organizational_unit": "Produktion",
            "hashed_password": "hashed_password123",
            "individual_permissions": ["production_approval"],
            "is_department_head": True,
            "approval_level": 3,
            "groups": ["production"]
        },
        
        # 4. Service/Reparatur
        {
            "email": "anna.service@company.com",
            "full_name": "Anna Techniker",
            "employee_id": "SV001",
            "organizational_unit": "Service",
            "hashed_password": "hashed_password123",
            "individual_permissions": ["service_coordination"],
            "is_department_head": False,
            "approval_level": 2,
            "groups": ["service_repair"]
        },
        
        # 5. Entwicklung (Cross-Functional mit QM!)
        {
            "email": "dr.mueller@company.com",
            "full_name": "Dr. Peter Müller",
            "employee_id": "EN001",
            "organizational_unit": "Entwicklung",
            "hashed_password": "hashed_password123",
            "individual_permissions": ["design_approval", "change_management"],
            "is_department_head": True,
            "approval_level": 3,
            "groups": ["development", "quality_management"],  # Cross-Functional!
            "primary": "development"
        },
        
        # 6. Wareneingang/-ausgang (Cross-Functional mit QM!)
        {
            "email": "frank.wareneingang@company.com",
            "full_name": "Frank Prüfer",
            "employee_id": "WE001",
            "organizational_unit": "Logistik",
            "hashed_password": "hashed_password123",
            "individual_permissions": ["inspection_approval", "supplier_coordination"],
            "is_department_head": False,
            "approval_level": 2,
            "groups": ["goods_inout", "procurement"],  # Cross-Functional!
            "primary": "goods_inout"
        },
        
        # 7. Vertrieb (Cross-Functional mit Service!)
        {
            "email": "michael.vertrieb@company.com",
            "full_name": "Michael Verkäufer",
            "employee_id": "VT001",
            "organizational_unit": "Vertrieb",
            "hashed_password": "hashed_password123",
            "individual_permissions": ["customer_escalation", "complaint_coordination"],
            "is_department_head": True,
            "approval_level": 3,
            "groups": ["sales", "service_repair"],  # Cross-Functional!
            "primary": "sales"
        },
        
        # 8. HR/Schulung
        {
            "email": "nicole.hr@company.com",
            "full_name": "Nicole Personalerin",
            "employee_id": "HR001",
            "organizational_unit": "Personal",
            "hashed_password": "hashed_password123",
            "individual_permissions": ["training_approval", "competence_certification"],
            "is_department_head": True,
            "approval_level": 3,
            "groups": ["hr_training"]
        },
        
        # 9. Team/Eingangsmodul
        {
            "email": "ki.system@company.com",
            "full_name": "KI-System Erfassungsbot",
            "employee_id": "KI001",
            "organizational_unit": "IT-Services",
            "hashed_password": "hashed_password123",
            "individual_permissions": ["data_capture", "automated_analysis"],
            "is_department_head": False,
            "approval_level": 1,
            "groups": ["team_input"]
        },
        
        # 10. Systemadmin/IT (Cross-Functional - hat Zugriff auf alle Gruppen!)
        {
            "email": "max.admin@company.com",
            "full_name": "Max Administrator",
            "employee_id": "IT001",
            "organizational_unit": "IT",
            "hashed_password": "hashed_password123",
            "individual_permissions": ["system_administration", "user_management", "backup_management", "security_oversight"],
            "is_department_head": True,
            "approval_level": 4,
            "groups": ["system_admin", "quality_management", "controlling"],  # Super-User!
            "primary": "system_admin"
        },
        
        # 11. Auditor (extern)
        {
            "email": "dr.auditor@externa-firm.de",
            "full_name": "Dr. Franz Auditor",
            "employee_id": "AUD001",
            "organizational_unit": "Externa Audit GmbH",
            "hashed_password": "hashed_password123",
            "individual_permissions": ["audit_access", "gap_analysis", "compliance_review"],
            "is_department_head": False,
            "approval_level": 1,
            "groups": ["external_auditor"]
        },
        
        # 12. Controlling (Cross-Functional mit QM!)
        {
            "email": "petra.controlling@company.com",
            "full_name": "Petra Zahlen",
            "employee_id": "CO001",
            "organizational_unit": "Controlling",
            "hashed_password": "hashed_password123",
            "individual_permissions": ["financial_reporting", "kpi_management", "cost_analysis"],
            "is_department_head": True,
            "approval_level": 3,
            "groups": ["controlling", "quality_management"],  # Cross-Functional!
            "primary": "controlling"
        },
        
        # 13. Lieferanten
        {
            "email": "supplier.a@lieferant.de",
            "full_name": "Lieferant A GmbH",
            "employee_id": "SUP001",
            "organizational_unit": "Externe Lieferanten",
            "hashed_password": "hashed_password123",
            "individual_permissions": ["document_upload", "self_assessment"],
            "is_department_head": False,
            "approval_level": 1,
            "groups": ["suppliers"]
        }
    ]
    
    print("👥 Erstelle Testbenutzer...")
    for user_data in test_users:
        groups_for_user = user_data.pop("groups")
        primary_group = user_data.pop("primary", groups_for_user[0])
        permissions = user_data.get("permissions", [])
        
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user:
            # Individual permissions als JSON String speichern
            user_data["individual_permissions"] = json.dumps(permissions) if permissions else None
            user = User(**user_data)
            db.add(user)
            db.flush()  # Um user.id zu bekommen
            
            # Interessensgruppen zuweisen
            for group_code in groups_for_user:
                if group_code in groups:
                    # Rolle bestimmen basierend auf Primary Group
                    role = "PRIMARY_ROLE" if group_code == primary_group else "SECONDARY_ROLE"
                    
                    membership = UserGroupMembership(
                        user_id=user.id,
                        interest_group_id=groups[group_code],
                        role_in_group=role
                    )
                    db.add(membership)
            
            group_names = [f"{code}{'*' if code == primary_group else ''}" for code in groups_for_user]
            permission_info = f" | Permissions: {len(permissions)}" if permissions else ""
            approval_info = f" | Level {user_data.get('approval_level', 1)}"
            department_head = " | 👑 LEITER" if user_data.get('is_department_head') else ""
            print(f"  ✅ {user_data['full_name']} ({', '.join(group_names)}){permission_info}{approval_info}{department_head}")
        else:
            print(f"  ⚠️  {user_data['full_name']} existiert bereits")
    
    db.commit()

def init_sample_data(db):
    """Erstellt Beispieldaten für alle Kernmodelle"""
    
    print("📚 Erstelle Sample Documents...")
    documents = [
        Document(
            title="QM-Handbuch",
            document_number="QMH-001",
            document_type=DocumentType.QM_MANUAL,
            version="2.1",
            status=DocumentStatus.APPROVED,
            content="Dieses Handbuch beschreibt unser Qualitätsmanagementsystem nach ISO 13485...",
            creator_id=3,  # Maria QM-Leiterin
            tags='["QMS", "Handbuch", "ISO13485"]'
        ),
        Document(
            title="Kalibrierverfahren Messgeräte",
            document_number="SOP-CAL-001",
            document_type=DocumentType.CALIBRATION_PROCEDURE,
            version="1.3",
            status=DocumentStatus.APPROVED,
            content="Verfahren zur Kalibrierung von Messgeräten und Prüfmitteln...",
            creator_id=4,  # Andreas QM-Koordinator
            tags='["Kalibrierung", "SOP", "Messgeräte"]'
        ),
        Document(
            title="Risikomanagementplan",
            document_number="RMP-001",
            document_type=DocumentType.RISK_ASSESSMENT,
            version="1.0",
            status=DocumentStatus.REVIEW,
            content="Risikomanagementplan für Produktentwicklung nach ISO 14971...",
            creator_id=9,  # Dr. Klaus Müller (Entwicklung)
            tags='["Risikomanagement", "ISO14971", "Entwicklung"]'
        ),
        Document(
            title="Arbeitsanweisung Wareneingangsprüfung",
            document_number="WI-WEP-001",
            document_type=DocumentType.WORK_INSTRUCTION,
            version="2.0",
            status=DocumentStatus.APPROVED,
            content="Arbeitsanweisung für die Prüfung von Waren im Wareneingang...",
            creator_id=11,  # Frank Wareneingangsprüfer
            tags='["Wareneingang", "Prüfung", "Arbeitsanweisung"]'
        ),
        Document(
            title="CAPA-Verfahren",
            document_number="SOP-CAPA-001",
            document_type=DocumentType.SOP,
            version="1.5",
            status=DocumentStatus.APPROVED,
            content="Standard Operating Procedure für Corrective and Preventive Actions...",
            creator_id=3,  # Maria QM-Leiterin
            tags='["CAPA", "SOP", "Korrekturmaßnahmen"]'
        ),
        Document(
            title="Prüfformblatt Wareneingang",
            document_number="FORM-WE-001",
            document_type=DocumentType.FORM,
            version="1.2",
            status=DocumentStatus.APPROVED,
            content="Formblatt für die Dokumentation der Wareneingangsprüfung...",
            creator_id=11,  # Frank Wareneingangsprüfer
            tags='["Formblatt", "Wareneingang", "Prüfung"]'
        ),
        Document(
            title="Bedienungsanleitung Temperaturlogger",
            document_number="MAN-TEMP-001",
            document_type=DocumentType.USER_MANUAL,
            version="1.0",
            status=DocumentStatus.APPROVED,
            content="Bedienungsanleitung für den Testo 176 T1 Temperaturlogger...",
            creator_id=4,  # Andreas QM-Koordinator
            tags='["Bedienungsanleitung", "Temperaturlogger", "Testo"]'
        )
    ]
    
    for doc in documents:
        existing_doc = db.query(Document).filter(Document.document_number == doc.document_number).first()
        if not existing_doc:
            db.add(doc)
            print(f"  ✅ {doc.title} ({doc.document_number})")
        else:
            print(f"  ⚠️  {doc.title} existiert bereits")
    
    db.commit()
    
    print("📜 Erstelle Sample Norms...")
    norms = [
        Norm(
            name="ISO 13485",
            full_title="Medizinprodukte - Qualitätsmanagementsysteme - Anforderungen für regulatorische Zwecke",
            version="2016",
            authority="ISO",
            description="Internationale Norm für Qualitätsmanagementsysteme in der Medizinprodukteindustrie",
            effective_date=datetime(2016, 3, 1)
        ),
        Norm(
            name="MDR",
            full_title="Verordnung (EU) 2017/745 über Medizinprodukte",
            version="2017/745",
            authority="EU",
            description="EU-Medizinprodukteverordnung - ersetzt die Medizinprodukte-Richtlinien",
            effective_date=datetime(2021, 5, 26)
        ),
        Norm(
            name="ISO 14971",
            full_title="Medizinprodukte - Anwendung des Risikomanagements auf Medizinprodukte",
            version="2019",
            authority="ISO",
            description="Standard für Risikomanagement bei Medizinprodukten",
            effective_date=datetime(2019, 12, 1)
        ),
        Norm(
            name="IEC 62304",
            full_title="Medizingeräte-Software - Software-Lebenszyklusprozesse",
            version="2015",
            authority="IEC",
            description="Standard für Software-Entwicklung bei Medizinprodukten",
            effective_date=datetime(2015, 6, 1)
        ),
        Norm(
            name="ISO 14155",
            full_title="Klinische Prüfung von Medizinprodukten an Menschen",
            version="2020",
            authority="ISO",
            description="Standard für klinische Prüfungen von Medizinprodukten",
            effective_date=datetime(2020, 9, 1)
        )
    ]
    
    for norm in norms:
        existing_norm = db.query(Norm).filter(Norm.name == norm.name, Norm.version == norm.version).first()
        if not existing_norm:
            db.add(norm)
            print(f"  ✅ {norm.name} {norm.version}")
        else:
            print(f"  ⚠️  {norm.name} {norm.version} existiert bereits")
    
    db.commit()
    
    print("🔧 Erstelle Sample Equipment...")
    equipment_list = [
        Equipment(
            name="Digitale Präzisionswaage",
            equipment_number="WAA-001",
            manufacturer="Sartorius",
            model="Entris II Precision",
            serial_number="B12345678",
            location="Labor 1 - Qualitätskontrolle",
            status=EquipmentStatus.ACTIVE,
            calibration_interval_months=12,
            last_calibration=datetime.now() - timedelta(days=300),
            next_calibration=datetime.now() + timedelta(days=65)  # Bald fällig
        ),
        Equipment(
            name="Digitaler Messschieber",
            equipment_number="MES-001",
            manufacturer="Mitutoyo",
            model="CD-15DCX",
            serial_number="M98765432",
            location="Produktion - Arbeitsplatz 3",
            status=EquipmentStatus.ACTIVE,
            calibration_interval_months=6,
            last_calibration=datetime.now() - timedelta(days=200),
            next_calibration=datetime.now() - timedelta(days=20)  # ÜBERFÄLLIG!
        ),
        Equipment(
            name="Temperatur-/Feuchtigkeitslogger",
            equipment_number="TEMP-001",
            manufacturer="Testo",
            model="176 T1",
            serial_number="T11223344",
            location="Lager - Klimaüberwachung",
            status=EquipmentStatus.ACTIVE,
            calibration_interval_months=24,
            last_calibration=datetime.now() - timedelta(days=100),
            next_calibration=datetime.now() + timedelta(days=630)
        ),
        Equipment(
            name="Mikrometer",
            equipment_number="MIK-001",
            manufacturer="Mitutoyo",
            model="MDC-25SX",
            serial_number="MK55667788",
            location="Qualitätskontrolle",
            status=EquipmentStatus.ACTIVE,
            calibration_interval_months=12,
            last_calibration=datetime.now() - timedelta(days=180),
            next_calibration=datetime.now() + timedelta(days=185)
        ),
        Equipment(
            name="Alte Waage (defekt)",
            equipment_number="WAA-OLD-001",
            manufacturer="Unbekannt",
            model="Vintage Scale",
            serial_number="OLD123456",
            location="Lager - nicht in Betrieb",
            status=EquipmentStatus.RETIRED,
            calibration_interval_months=12,
            last_calibration=datetime.now() - timedelta(days=800),
            next_calibration=None  # Nicht mehr kalibriert
        )
    ]
    
    for equip in equipment_list:
        existing_equip = db.query(Equipment).filter(Equipment.equipment_number == equip.equipment_number).first()
        if not existing_equip:
            db.add(equip)
            status_emoji = "🔧" if equip.status == EquipmentStatus.ACTIVE else "🚫"
            print(f"  {status_emoji} {equip.name} ({equip.equipment_number})")
        else:
            print(f"  ⚠️  {equip.name} existiert bereits")
    
    db.commit()
    
    print("📊 Erstelle Sample Calibrations...")
    calibrations = [
        Calibration(
            equipment_id=1,  # Waage
            calibration_date=datetime.now() - timedelta(days=300),
            next_due_date=datetime.now() + timedelta(days=65),
            calibration_results='{"deviation_5g": "0.1g", "deviation_100g": "0.05g", "uncertainty": "±0.05g", "status": "passed", "certificate_nr": "CAL-2024-001"}',
            certificate_path="/certificates/waa-001-2024.pdf",
            status="valid",
            responsible_user_id=4  # Andreas QM-Koordinator
        ),
        Calibration(
            equipment_id=2,  # Messschieber  
            calibration_date=datetime.now() - timedelta(days=200),
            next_due_date=datetime.now() - timedelta(days=20),  # ÜBERFÄLLIG!
            calibration_results='{"deviation_10mm": "0.01mm", "deviation_100mm": "0.02mm", "uncertainty": "±0.01mm", "status": "passed", "certificate_nr": "CAL-2024-002"}',
            certificate_path="/certificates/mes-001-2024.pdf",
            status="expired",  # Status auf expired setzen
            responsible_user_id=11  # Frank Wareneingangsprüfer
        ),
        Calibration(
            equipment_id=3,  # Temperaturlogger
            calibration_date=datetime.now() - timedelta(days=100),
            next_due_date=datetime.now() + timedelta(days=630),
            calibration_results='{"temp_deviation_20C": "0.1°C", "temp_deviation_50C": "0.15°C", "humidity_deviation": "1%RH", "status": "passed", "certificate_nr": "CAL-2024-003"}',
            certificate_path="/certificates/temp-001-2024.pdf",
            status="valid",
            responsible_user_id=3  # Maria QM-Leiterin
        ),
        Calibration(
            equipment_id=4,  # Mikrometer
            calibration_date=datetime.now() - timedelta(days=180),
            next_due_date=datetime.now() + timedelta(days=185),
            calibration_results='{"deviation_1mm": "0.001mm", "deviation_20mm": "0.002mm", "uncertainty": "±0.001mm", "status": "passed", "certificate_nr": "CAL-2024-004"}',
            certificate_path="/certificates/mik-001-2024.pdf",
            status="valid",
            responsible_user_id=4  # Andreas QM-Koordinator
        )
    ]
    
    for cal in calibrations:
        # Prüfen ob schon eine Kalibrierung für dieses Equipment existiert
        existing_cal = db.query(Calibration).filter(
            Calibration.equipment_id == cal.equipment_id,
            Calibration.calibration_date == cal.calibration_date
        ).first()
        if not existing_cal:
            db.add(cal)
            equipment = db.query(Equipment).filter(Equipment.id == cal.equipment_id).first()
            status_emoji = "✅" if cal.status == "valid" else "⚠️"
            print(f"  {status_emoji} Kalibrierung für {equipment.name} ({cal.status})")
        else:
            print(f"  ⚠️  Kalibrierung existiert bereits")
    
    db.commit()
    
    print()
    print("🎯 Sample Data Übersicht:")
    print(f"   📚 Documents: {db.query(Document).count()}")
    print(f"   📜 Norms: {db.query(Norm).count()}")
    print(f"   🔧 Equipment: {db.query(Equipment).count()}")
    print(f"   📊 Calibrations: {db.query(Calibration).count()}")
    print()
    
    # Überfällige Kalibrierungen anzeigen
    overdue_equipment = db.query(Equipment).filter(
        Equipment.next_calibration < datetime.now()
    ).all()
    
    if overdue_equipment:
        print("⚠️  ÜBERFÄLLIGE KALIBRIERUNGEN:")
        for equip in overdue_equipment:
            days_overdue = (datetime.now() - equip.next_calibration).days
            print(f"   🚨 {equip.name} ({equip.equipment_number}) - {days_overdue} Tage überfällig")
    else:
        print("✅ Keine überfälligen Kalibrierungen")

def main():
    """
    Hauptfunktion für Datenbank-Initialisierung.
    
    Orchestriert die komplette Erstellung der MVP-Datenbank
    mit allen Testdaten und Beispiel-Inhalten.
    
    Durchführungsschritte:
    1. Tabellen-Erstellung/Validation
    2. 13 Interessensgruppen Setup
    3. Testbenutzer mit realistischen Profilen
    4. QMS-Beispieldokumente
    5. Normen und Compliance-Standards  
    6. Equipment mit Kalibrierungs-Tracking
    7. Überfällige Kalibrierung für Demo
    
    Error Handling:
        - Transactional: Bei Fehler wird alles zurückgerollt
        - Detaillierte Fehlerausgabe für Debugging
        - Existierende Daten werden übersprungen (idempotent)
    """
    print("🚀 KI-QMS MVP Database Initialization")
    print("=" * 50)
    
    try:
        # WICHTIG: Alte Datenbank komplett löschen für sauberen Start
        db_files = ['ki_qms.db', 'qms_mvp.db', 'ki_qms.db-wal', 'ki_qms.db-shm', 'qms_mvp.db-wal', 'qms_mvp.db-shm']
        for db_file in db_files:
            if os.path.exists(db_file):
                os.remove(db_file)
                print(f"🗑️  Alte Datenbankdatei {db_file} gelöscht")
        
        # Tabellen erstellen
        create_tables()
        print("✅ Datenbank-Tabellen erfolgreich erstellt/überprüft")
        
        # Datenbank-Session erstellen
        db = SessionLocal()
        
        try:
            # Daten initialisieren
            print("✅ Datenbank-Tabellen erstellt/überprüft")
            init_interest_groups(db)
            init_test_users(db)
            init_sample_data(db)
            
            print("\n🎉 ERFOLGREICH! KI-QMS MVP-Datenbank initialisiert")
            print("\n📊 Zusammenfassung:")
            print(f"   • 13 Interessensgruppen mit spezifischen Berechtigungen")
            print(f"   • {db.query(User).count()} Testbenutzer mit Multi-Group-Zuordnungen")
            print(f"   • {db.query(Document).count()} QMS-Dokumente aller Typen")
            print(f"   • {db.query(Norm).count()} Compliance-Normen")
            print(f"   • {db.query(Equipment).count()} Equipment-Einträge")
            print(f"   • {db.query(Calibration).count()} Kalibrierungsprotokolle")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Fehler bei der Datenbank-Initialisierung: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    main() 