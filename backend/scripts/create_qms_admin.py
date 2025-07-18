#!/usr/bin/env python3
"""
Erstellt einen QMS-Admin-Benutzer für das System

Dieses Skript erstellt einen Standard-Admin-Benutzer mit:
- Benutzername: admin
- Passwort: admin123
- Rolle: admin
- Abteilung: QM
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User, InterestGroup, UserGroupMembership
from app.auth import get_password_hash
from datetime import datetime

def create_admin_user():
    """Erstellt einen Admin-Benutzer und weist QM-Gruppe zu"""
    
    db = SessionLocal()
    
    try:
        # Prüfe ob Admin bereits existiert
        existing_admin = db.query(User).filter(User.email == "admin@qms.local").first()
        if existing_admin:
            print("ℹ️ Admin-Benutzer existiert bereits")
            return True
        
        # Erstelle Admin-Benutzer
        admin_user = User(
            email="admin@qms.local",
            full_name="QMS Administrator",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            organizational_unit="QM",
            is_department_head=True,
            approval_level=4,
            created_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin-Benutzer erstellt:")
        print(f"   - E-Mail: {admin_user.email}")
        print(f"   - Passwort: admin123")
        print(f"   - Abteilung: {admin_user.organizational_unit}")
        print(f"   - Approval Level: {admin_user.approval_level}")
        
        # Weise QM-Gruppe zu
        qm_group = db.query(InterestGroup).filter(
            InterestGroup.name == "Qualitätsmanagement"
        ).first()
        
        if qm_group:
            membership = UserGroupMembership(
                user_id=admin_user.id,
                group_id=qm_group.id,
                joined_at=datetime.utcnow()
            )
            db.add(membership)
            db.commit()
            print(f"✅ Zur Gruppe '{qm_group.name}' hinzugefügt")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Admin-Benutzers: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Erstelle QMS-Admin-Benutzer...")
    print("-" * 50)
    
    success = create_admin_user()
    
    if success:
        print("\n✨ Admin-Benutzer bereit!")
        print("\nEinloggen mit:")
        print("  E-Mail: admin@qms.local")
        print("  Passwort: admin123")
    else:
        print("\n❌ Admin-Erstellung fehlgeschlagen!")
        sys.exit(1)