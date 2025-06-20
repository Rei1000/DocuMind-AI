#!/usr/bin/env python3
"""
KI-QMS Datenbank-Neuinitialisierung Script

Erstellt eine saubere, neue Datenbank mit allen aktuellen Modellen,
korrigierten Schemas und einem vollständigen Testdatensatz.

Usage:
    python backend/scripts/create_clean_db.py
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db, DATABASE_URL
from app.models import (
    InterestGroup, User, UserGroupMembership, Document, Norm, 
    Equipment, Calibration, DocumentNormMapping, CalibrationRequirement,
    DocumentType, DocumentStatus, EquipmentStatus
)

def create_clean_database():
    """Erstellt eine komplett neue, saubere Datenbank."""
    
    print("🔄 Erstelle neue KI-QMS Datenbank...")
    
    # Engine erstellen
    engine = create_engine(DATABASE_URL)
    
    # Alle Tabellen löschen und neu erstellen
    print("📊 Lösche alte Tabellen...")
    Base.metadata.drop_all(bind=engine)
    
    print("🏗️ Erstelle neue Tabellen...")
    Base.metadata.create_all(bind=engine)
    
    # Session erstellen
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # === 1. INTERESSENSGRUPPEN ===
        print("👥 Erstelle Interessensgruppen...")
        
        groups_data = [
            {"name": "Einkauf", "code": "procurement", "description": "Strategischer Einkauf und Lieferantenmanagement", "is_external": False},
            {"name": "Qualitätsmanagement", "code": "quality_management", "description": "QM-System, Compliance und Dokumentenlenkung", "is_external": False},
            {"name": "Entwicklung", "code": "development", "description": "Produktentwicklung und Design Controls", "is_external": False},
            {"name": "Produktion", "code": "production", "description": "Fertigungssteuerung und Produktionsqualität", "is_external": False},
            {"name": "Service & Support", "code": "service_support", "description": "Kundendienst und technischer Support", "is_external": False},
            {"name": "Vertrieb", "code": "sales", "description": "Vertrieb und Markterschließung", "is_external": False},
            {"name": "Regulatorische Angelegenheiten", "code": "regulatory", "description": "Zulassungen und regulatorische Compliance", "is_external": False},
            {"name": "Klinik", "code": "clinical", "description": "Klinische Studien und Anwendung", "is_external": False},
            {"name": "IT", "code": "it", "description": "IT-Infrastruktur und Systemsicherheit", "is_external": False},
            {"name": "Geschäftsleitung", "code": "management", "description": "Strategische Führung und Entscheidungen", "is_external": False},
            {"name": "Externe Auditoren", "code": "external_auditors", "description": "Unabhängige Qualitätsprüfung", "is_external": True},
            {"name": "Lieferanten", "code": "suppliers", "description": "Externe Zulieferunternehmen", "is_external": True},
            {"name": "Kunden", "code": "customers", "description": "Endkunden und Anwender", "is_external": True}
        ]
        
        groups = []
        for group_data in groups_data:
            group = InterestGroup(**group_data)
            db.add(group)
            groups.append(group)
        
        db.commit()
        
        # === 2. BENUTZER ===
        print("👤 Erstelle Benutzer...")
        
        users_data = [
            {"email": "admin@company.com", "full_name": "Admin User", "employee_id": "EMP001", "organizational_unit": "IT", "approval_level": 4, "is_department_head": True},
            {"email": "maria.qm@company.com", "full_name": "Dr. Maria Qualität", "employee_id": "EMP002", "organizational_unit": "Qualitätsmanagement", "approval_level": 4, "is_department_head": True},
            {"email": "thomas.dev@company.com", "full_name": "Thomas Entwickler", "employee_id": "EMP003", "organizational_unit": "Entwicklung", "approval_level": 2, "is_department_head": False},
            {"email": "anna.prod@company.com", "full_name": "Anna Produktion", "employee_id": "EMP004", "organizational_unit": "Produktion", "approval_level": 3, "is_department_head": True},
            {"email": "klaus.einkauf@company.com", "full_name": "Klaus Käufer", "employee_id": "EMP005", "organizational_unit": "Einkauf", "approval_level": 2, "is_department_head": False}
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                hashed_password="$2b$12$dummy_hash_for_testing",  # Dummy hash
                **user_data
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        
        # === 3. NORMEN ===
        print("📖 Erstelle Normen...")
        
        norms_data = [
            {"name": "ISO 13485:2016", "full_title": "Medizinprodukte - Qualitätsmanagementsysteme", "version": "2016", "authority": "ISO", "description": "Anforderungen für regulatorische Zwecke"},
            {"name": "ISO 14971:2019", "full_title": "Medizinprodukte - Anwendung des Risikomanagements", "version": "2019", "authority": "ISO", "description": "Risikomanagement für Medizinprodukte"},
            {"name": "IEC 62304:2006", "full_title": "Medizinprodukte-Software - Software-Lebenszyklus-Prozesse", "version": "2006", "authority": "IEC", "description": "Software-Entwicklung für Medizinprodukte"},
            {"name": "MDR 2017/745", "full_title": "Verordnung über Medizinprodukte", "version": "2017", "authority": "EU Commission", "description": "EU-Medizinprodukteverordnung"},
            {"name": "ISO 10993-1:2018", "full_title": "Biologische Beurteilung von Medizinprodukten", "version": "2018", "authority": "ISO", "description": "Beurteilung und Prüfung von Medizinprodukten"}
        ]
        
        norms = []
        for norm_data in norms_data:
            norm = Norm(
                effective_date=datetime(2020, 1, 1),
                created_at=datetime.now(),
                **norm_data
            )
            db.add(norm)
            norms.append(norm)
        
        db.commit()
        
        # === 4. EQUIPMENT ===
        print("🔧 Erstelle Equipment...")
        
        equipment_data = [
            {"name": "Präzisionswaage", "equipment_number": "EQ001", "manufacturer": "Sartorius", "model": "Secura324-1S", "serial_number": "SN001", "location": "Labor 1", "calibration_interval_months": 12},
            {"name": "Messschieber", "equipment_number": "EQ002", "manufacturer": "Mitutoyo", "model": "CD-15APX", "serial_number": "SN002", "location": "Produktion", "calibration_interval_months": 6},
            {"name": "Temperaturmessgerät", "equipment_number": "EQ003", "manufacturer": "Testo", "model": "testo 175", "serial_number": "SN003", "location": "Lager", "calibration_interval_months": 12}
        ]
        
        equipment_list = []
        for eq_data in equipment_data:
            last_cal = datetime.now() - timedelta(days=30)
            next_cal = last_cal + timedelta(days=eq_data["calibration_interval_months"] * 30)
            
            equipment = Equipment(
                last_calibration=last_cal,
                next_calibration=next_cal,
                status=EquipmentStatus.ACTIVE,
                created_at=datetime.now(),
                **eq_data
            )
            db.add(equipment)
            equipment_list.append(equipment)
        
        db.commit()
        
        # === 5. TESTDOKUMENTE ===
        print("📄 Erstelle Testdokumente...")
        
        # QM-Handbuch
        qm_manual = Document(
            title="QM-Handbuch ISO 13485",
            document_number="QMH-001",
            document_type=DocumentType.QM_MANUAL,
            version="1.0",
            status=DocumentStatus.APPROVED,
            content="Qualitätsmanagement-Handbuch nach ISO 13485:2016",
            creator_id=users[1].id,  # Dr. Maria Qualität
            approved_by_id=users[1].id,
            approved_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(qm_manual)
        
        # Standard-Norm
        norm_doc = Document(
            title="ISO 13485:2016 - Volltext",
            document_number="NORM-001",
            document_type=DocumentType.STANDARD_NORM,
            version="1.0",
            status=DocumentStatus.APPROVED,
            content="Volltext der ISO 13485:2016 Norm",
            creator_id=users[1].id,
            approved_by_id=users[1].id,
            approved_at=datetime.now(),
            compliance_status="EINGEHALTEN",
            priority="HOCH",
            scope="Gesamtes QMS",
            chapter_numbers="4.1, 4.2, 5.1, 6.1, 7.1, 8.1",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(norm_doc)
        
        # SOP
        sop_doc = Document(
            title="SOP-001: Dokumentenlenkung",
            document_number="SOP-001",
            document_type=DocumentType.SOP,
            version="2.1",
            status=DocumentStatus.APPROVED,
            content="Standard Operating Procedure für Dokumentenlenkung",
            creator_id=users[1].id,
            approved_by_id=users[1].id,
            approved_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(sop_doc)
        
        db.commit()
        
        print("✅ Datenbank erfolgreich erstellt!")
        print(f"📊 Erstellt:")
        print(f"   - {len(groups)} Interessensgruppen")
        print(f"   - {len(users)} Benutzer")
        print(f"   - {len(norms)} Normen")
        print(f"   - {len(equipment_list)} Equipment-Einträge")
        print(f"   - 3 Testdokumente")
        print()
        print("🎯 System bereit für Upload-Tests!")
        
    except Exception as e:
        print(f"❌ Fehler bei Datenbank-Erstellung: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_clean_database() 