#!/usr/bin/env python3
"""
KI-QMS Interest Groups Update Script

Aktualisiert die Interessensgruppen in der bestehenden Datenbank 
auf die definitive Master-Definition.

WICHTIG: Dieses Script kann auf die laufende Datenbank angewendet werden
ohne Datenverlust!

Autoren: KI-QMS Entwicklungsteam
Version: 1.0.0
"""

import sys
import os
from datetime import datetime

# Pfad zum app-Modul hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine
from app.models import InterestGroup
from interest_groups_master import MASTER_INTEREST_GROUPS

def update_interest_groups():
    """
    Aktualisiert die Interessensgruppen auf die Master-Definition.
    
    - Deaktiviert alte, nicht mehr verwendete Gruppen
    - Erstellt neue Gruppen aus Master-Definition  
    - Aktualisiert bestehende Gruppen mit neuen Daten
    """
    
    print("🔄 KI-QMS Interest Groups Update")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # 1. Aktuelle Gruppen aus DB laden
        existing_groups = db.query(InterestGroup).all()
        existing_codes = {group.code: group for group in existing_groups}
        
        print(f"📊 Gefunden: {len(existing_groups)} bestehende Gruppen")
        
        # 2. Master-Codes sammeln
        master_codes = {group["code"] for group in MASTER_INTEREST_GROUPS}
        
        print(f"🎯 Ziel: {len(MASTER_INTEREST_GROUPS)} definitive Gruppen")
        
        # 3. Neue Gruppen erstellen oder bestehende aktualisieren
        updated_count = 0
        created_count = 0
        
        for master_group in MASTER_INTEREST_GROUPS:
            code = master_group["code"]
            
            if code in existing_codes:
                # Bestehende Gruppe aktualisieren
                existing_group = existing_codes[code]
                existing_group.name = master_group["name"]
                existing_group.description = master_group["description"]
                import json
                existing_group.group_permissions = json.dumps(master_group["group_permissions"])
                existing_group.ai_functionality = master_group["ai_functionality"]
                existing_group.typical_tasks = master_group["typical_tasks"]
                existing_group.is_external = master_group["is_external"]
                existing_group.is_active = True  # Reaktivieren falls deaktiviert
                
                print(f"  🔄 Aktualisiert: {master_group['name']} ({code})")
                updated_count += 1
                
            else:
                # Neue Gruppe erstellen
                import json
                new_group = InterestGroup(
                    name=master_group["name"],
                    code=master_group["code"],
                    description=master_group["description"],
                    group_permissions=json.dumps(master_group["group_permissions"]),
                    ai_functionality=master_group["ai_functionality"],
                    typical_tasks=master_group["typical_tasks"],
                    is_external=master_group["is_external"],
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(new_group)
                
                print(f"  ✅ Erstellt: {master_group['name']} ({code})")
                created_count += 1
        
        # 4. Veraltete Gruppen deaktivieren (Soft Delete)
        deactivated_count = 0
        for code, existing_group in existing_codes.items():
            if code not in master_codes and existing_group.is_active:
                existing_group.is_active = False
                print(f"  ⚠️  Deaktiviert: {existing_group.name} ({code})")
                deactivated_count += 1
        
        # 5. Änderungen speichern
        db.commit()
        
        print("\n🎉 Update erfolgreich abgeschlossen!")
        print(f"📊 Statistik:")
        print(f"   • {created_count} neue Gruppen erstellt")
        print(f"   • {updated_count} bestehende Gruppen aktualisiert")
        print(f"   • {deactivated_count} veraltete Gruppen deaktiviert")
        
        # 6. Finale Validierung
        final_groups = db.query(InterestGroup).filter(InterestGroup.is_active == True).all()
        print(f"   • {len(final_groups)} aktive Gruppen total")
        
        if len(final_groups) == 13:
            print("✅ Perfekt! Genau 13 aktive Interessensgruppen")
        else:
            print(f"⚠️  Warnung: {len(final_groups)} aktive Gruppen (erwartet: 13)")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Update: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

def list_current_groups():
    """Zeigt alle aktuellen Interessensgruppen an"""
    
    print("📋 Aktuelle Interessensgruppen:")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        groups = db.query(InterestGroup).order_by(InterestGroup.id).all()
        
        for group in groups:
            status = "✅" if group.is_active else "❌"
            external = "🌐" if group.is_external else "🏢"
            print(f"{status} {external} {group.name} ({group.code})")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='KI-QMS Interest Groups Update')
    parser.add_argument('--list', action='store_true', help='Aktuelle Gruppen anzeigen')
    parser.add_argument('--update', action='store_true', help='Gruppen aktualisieren')
    
    args = parser.parse_args()
    
    if args.list:
        list_current_groups()
    elif args.update:
        success = update_interest_groups()
        sys.exit(0 if success else 1)
    else:
        print("Verwendung:")
        print("  python update_interest_groups.py --list    # Aktuelle Gruppen anzeigen")
        print("  python update_interest_groups.py --update  # Gruppen aktualisieren") 