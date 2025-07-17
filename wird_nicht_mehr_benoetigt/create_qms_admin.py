#!/usr/bin/env python3
"""
Erstellt einen funktionierenden QMS System Administrator für Ersteinrichtung

Usage:
    python backend/scripts/create_qms_admin.py
"""

import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.database import DATABASE_URL
from app.models import User
from app.auth import get_password_hash

def create_qms_admin():
    """Erstellt einen funktionierenden QMS System Administrator."""
    
    print("🔧 Erstelle QMS System Administrator...")
    
    # Engine und Session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Prüfe ob User bereits existiert
        existing_user = db.query(User).filter(User.email == "qms.admin@company.com").first()
        
        if existing_user:
            print("⚠️ QMS Admin existiert bereits - setze Passwort zurück...")
            # Passwort zurücksetzen mit korrektem Hash
            existing_user.hashed_password = get_password_hash("admin123")
            db.commit()
            print("✅ Passwort zurückgesetzt!")
        else:
            print("➕ Erstelle neuen QMS Admin...")
            # Neuen User erstellen
            admin_user = User(
                email="qms.admin@company.com",
                full_name="QMS System Administrator",
                hashed_password=get_password_hash("admin123"),
                employee_id="QMS001",
                organizational_unit="QMS System",
                approval_level=4,
                is_department_head=True,
                is_active=True
            )
            
            db.add(admin_user)
            db.commit()
            print("✅ QMS Admin erstellt!")
        
        print("\n🎯 Login-Daten:")
        print("📧 Email: qms.admin@company.com")
        print("🔑 Passwort: admin123")
        print("🏷️ Level: 4 (System Administrator)")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_qms_admin() 