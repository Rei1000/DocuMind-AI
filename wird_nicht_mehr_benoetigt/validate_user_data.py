#!/usr/bin/env python3
"""
Benutzer-Datenvalidierung und -reparatur Script

Prüft und repariert automatisch:
- Beschädigte JSON-Berechtigungen
- Inkonsistente Gruppenzuordnungen  
- Verwaiste Datenbankeinträge
- Ungültige approval_level Werte

Verwendung:
    python validate_user_data.py --check    # Nur prüfen
    python validate_user_data.py --repair   # Prüfen und reparieren
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path

# Backend-Module importieren
sys.path.append(str(Path(__file__).parent.parent))

from app.database import get_db
from app.models import User, UserGroupMembership, InterestGroup
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./qms_mvp.db"
engine = create_engine(DATABASE_URL)

def validate_user_permissions(db: Session, repair: bool = False):
    """Validiert und repariert Benutzer-Berechtigungen"""
    print("\n🔍 Prüfe Benutzer-Berechtigungen...")
    
    issues_found = 0
    repairs_made = 0
    
    users = db.query(User).all()
    
    for user in users:
        user_issues = []
        
        # 1. Prüfe individual_permissions JSON
        if user.individual_permissions:
            try:
                if isinstance(user.individual_permissions, str):
                    perms = json.loads(user.individual_permissions)
                    if not isinstance(perms, list):
                        user_issues.append("individual_permissions ist kein JSON-Array")
                    else:
                        # Prüfe Array-Inhalte
                        invalid_perms = [p for p in perms if not isinstance(p, str)]
                        if invalid_perms:
                            user_issues.append(f"Ungültige Berechtigung(en): {invalid_perms}")
                else:
                    user_issues.append("individual_permissions ist kein String")
            except json.JSONDecodeError:
                user_issues.append("individual_permissions ist kein gültiges JSON")
        
        # 2. Prüfe approval_level
        if user.approval_level is None or user.approval_level < 1 or user.approval_level > 4:
            user_issues.append(f"approval_level ungültig: {user.approval_level}")
        
        # 3. Prüfe required fields
        if not user.full_name or not user.email:
            user_issues.append("Fehlende Pflichtfelder (full_name oder email)")
        
        if user_issues:
            issues_found += len(user_issues)
            print(f"❌ User {user.id} ({user.email}):")
            for issue in user_issues:
                print(f"   • {issue}")
            
            if repair:
                # Reparaturen durchführen
                fixed_issues = 0
                
                # Repariere individual_permissions
                if user.individual_permissions:
                    try:
                        if isinstance(user.individual_permissions, str):
                            perms = json.loads(user.individual_permissions)
                            if not isinstance(perms, list):
                                user.individual_permissions = "[]"
                                fixed_issues += 1
                            else:
                                # Filtere ungültige Einträge
                                valid_perms = [str(p) for p in perms if isinstance(p, str) and p.strip()]
                                user.individual_permissions = json.dumps(valid_perms)
                                fixed_issues += 1
                        else:
                            user.individual_permissions = "[]"
                            fixed_issues += 1
                    except json.JSONDecodeError:
                        user.individual_permissions = "[]"
                        fixed_issues += 1
                
                # Repariere approval_level
                if user.approval_level is None or user.approval_level < 1 or user.approval_level > 4:
                    user.approval_level = 1  # Standard-Level
                    fixed_issues += 1
                
                # Repariere required fields
                if not user.full_name:
                    user.full_name = f"Benutzer {user.id}"
                    fixed_issues += 1
                if not user.email:
                    user.email = f"user{user.id}@qms.local"
                    fixed_issues += 1
                
                if fixed_issues > 0:
                    try:
                        db.commit()
                        repairs_made += fixed_issues
                        print(f"   ✅ {fixed_issues} Probleme repariert")
                    except Exception as e:
                        db.rollback()
                        print(f"   ❌ Reparatur fehlgeschlagen: {e}")
    
    return issues_found, repairs_made

def validate_user_groups(db: Session, repair: bool = False):
    """Validiert Benutzer-Gruppenzuordnungen"""
    print("\n🔍 Prüfe Benutzer-Gruppenzuordnungen...")
    
    issues_found = 0
    repairs_made = 0
    
    memberships = db.query(UserGroupMembership).all()
    
    for membership in memberships:
        membership_issues = []
        
        # 1. Prüfe Verweise auf existierende User/Groups
        if not membership.user:
            membership_issues.append("Verweis auf nicht-existierenden User")
        if not membership.interest_group:
            membership_issues.append("Verweis auf nicht-existierende Gruppe")
        
        # 2. Prüfe approval_level
        if not hasattr(membership, 'approval_level') or membership.approval_level is None:
            membership_issues.append("approval_level fehlt")
        elif membership.approval_level < 1 or membership.approval_level > 4:
            membership_issues.append(f"approval_level ungültig: {membership.approval_level}")
        
        if membership_issues:
            issues_found += len(membership_issues)
            print(f"❌ Membership {membership.id}:")
            for issue in membership_issues:
                print(f"   • {issue}")
            
            if repair:
                fixed_issues = 0
                
                # Lösche verwaiste Memberships
                if not membership.user or not membership.interest_group:
                    try:
                        db.delete(membership)
                        fixed_issues += 1
                        print(f"   ✅ Verwaiste Membership gelöscht")
                    except Exception as e:
                        print(f"   ❌ Löschung fehlgeschlagen: {e}")
                else:
                    # Repariere approval_level
                    if not hasattr(membership, 'approval_level') or membership.approval_level is None:
                        membership.approval_level = 1
                        fixed_issues += 1
                    elif membership.approval_level < 1 or membership.approval_level > 4:
                        membership.approval_level = 1
                        fixed_issues += 1
                
                if fixed_issues > 0:
                    try:
                        db.commit()
                        repairs_made += fixed_issues
                        if membership.user and membership.interest_group:
                            print(f"   ✅ {fixed_issues} Probleme repariert")
                    except Exception as e:
                        db.rollback()
                        print(f"   ❌ Reparatur fehlgeschlagen: {e}")
    
    return issues_found, repairs_made

def generate_report(db: Session):
    """Erstellt einen Datenintegritäts-Report"""
    print("\n📊 Datenintegritäts-Report")
    print("=" * 50)
    
    # User-Statistiken
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    print(f"👥 Benutzer: {total_users} total, {active_users} aktiv")
    
    # Gruppen-Statistiken
    total_groups = db.query(InterestGroup).count()
    total_memberships = db.query(UserGroupMembership).filter(UserGroupMembership.is_active == True).count()
    
    print(f"🏢 Interessensgruppen: {total_groups}")
    print(f"🔗 Aktive Memberships: {total_memberships}")
    
    # Problem-Identifikation
    users_without_email = db.query(User).filter(User.email.is_(None)).count()
    users_without_name = db.query(User).filter(User.full_name.is_(None)).count()
    
    print(f"⚠️ Benutzer ohne Email: {users_without_email}")
    print(f"⚠️ Benutzer ohne Namen: {users_without_name}")

def main():
    parser = argparse.ArgumentParser(description="Benutzer-Datenvalidierung")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Nur Probleme prüfen")
    group.add_argument("--repair", action="store_true", help="Probleme prüfen und reparieren")
    
    args = parser.parse_args()
    
    print("🔧 KI-QMS Benutzer-Datenvalidierung")
    print("=" * 50)
    
    # Database Session
    db = next(get_db())
    
    try:
        # Report generieren
        generate_report(db)
        
        # Validierung durchführen
        total_issues = 0
        total_repairs = 0
        
        # Benutzer-Berechtigungen
        user_issues, user_repairs = validate_user_permissions(db, repair=args.repair)
        total_issues += user_issues
        total_repairs += user_repairs
        
        # Gruppenzuordnungen
        group_issues, group_repairs = validate_user_groups(db, repair=args.repair)
        total_issues += group_issues
        total_repairs += group_repairs
        
        # Zusammenfassung
        print("\n" + "=" * 50)
        print("📈 Zusammenfassung")
        print(f"🔍 Probleme gefunden: {total_issues}")
        
        if args.repair:
            print(f"✅ Reparaturen durchgeführt: {total_repairs}")
            if total_repairs > 0:
                print("💾 Änderungen wurden in der Datenbank gespeichert.")
        else:
            print("ℹ️ Verwenden Sie --repair um Probleme zu beheben.")
        
        if total_issues == 0:
            print("🎉 Alle Daten sind konsistent!")
            
    except Exception as e:
        print(f"❌ Fehler bei der Validierung: {e}")
        return 1
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 