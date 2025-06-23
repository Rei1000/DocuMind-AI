#!/usr/bin/env python3
"""
Script zum Reparieren fehlender Interessensgruppen-Zuordnungen

Problem:
- QMS System Administrator hat keine Interessensgruppen-Zuordnung
- User brauchen korrekte Zuordnungen für Profil-Anzeige
- System Admin sollte alle Rechte in QM-Gruppe haben

Verwendung:
    python fix_missing_user_groups.py
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Backend-Module importieren
sys.path.append(str(Path(__file__).parent.parent))

import sqlite3
import json

def fix_user_groups():
    """Repariert fehlende Interessensgruppen-Zuordnungen"""
    print("🔧 Repariere fehlende Interessensgruppen-Zuordnungen...")
    print("=" * 60)
    
    # Datenbankpfad
    db_path = os.path.join(os.path.dirname(__file__), '..', 'qms_mvp.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Prüfe aktuelle Zuordnungen
        cursor.execute("""
            SELECT u.id, u.full_name, u.email, u.organizational_unit,
                   COUNT(ugm.id) as group_count
            FROM users u
            LEFT JOIN user_group_memberships ugm ON u.id = ugm.user_id AND ugm.is_active = 1
            WHERE u.is_active = 1
            GROUP BY u.id
        """)
        users = cursor.fetchall()
        
        print("📊 Aktuelle Benutzer und ihre Gruppenzuordnungen:")
        users_without_groups = []
        for user in users:
            user_id, name, email, dept, group_count = user
            status = f"✅ {group_count} Gruppen" if group_count > 0 else "❌ KEINE Gruppen"
            print(f"   User {user_id}: {name} ({email}) - {dept} | {status}")
            if group_count == 0:
                users_without_groups.append(user)
        
        print()
        
        # 2. Interessensgruppen laden
        cursor.execute("SELECT id, name, code FROM interest_groups WHERE is_active = 1")
        groups = {row[2]: (row[0], row[1]) for row in cursor.fetchall()}
        
        # 3. Abteilungs-Mapping (wie in main.py)
        department_mapping = {
            "Team/Eingangsmodul": groups.get("input_team", [None])[0],
            "Qualitätsmanagement": groups.get("quality_management", [None])[0], 
            "Entwicklung": groups.get("development", [None])[0],
            "Einkauf": groups.get("procurement", [None])[0],
            "Produktion": groups.get("production", [None])[0],
            "HR/Schulung": groups.get("hr_training", [None])[0],
            "Dokumentation": groups.get("documentation", [None])[0],
            "Service/Support": groups.get("service_support", [None])[0],
            "Vertrieb": groups.get("sales", [None])[0],
            "Regulatory Affairs": groups.get("regulatory", [None])[0],
            "IT-Abteilung": groups.get("it_department", [None])[0],
            "System Administration": groups.get("quality_management", [None])[0],  # System Admin → QM
        }
        
        # 4. Fehlende Zuordnungen erstellen
        repairs_made = 0
        for user in users_without_groups:
            user_id, name, email, dept, _ = user
            
            print(f"🔧 Repariere User {user_id}: {name} ({dept})")
            
            # Zielgruppe bestimmen
            if dept in department_mapping and department_mapping[dept]:
                group_id = department_mapping[dept]
                group_name = groups.get([k for k, v in groups.items() if v[0] == group_id][0], ["Unknown"])[1]
                
                # Approval Level bestimmen
                if "admin" in email.lower() or dept == "System Administration":
                    approval_level = 4  # QM-Manager Level
                    role = "System Administrator"
                    is_dept_head = True
                elif dept == "Qualitätsmanagement":
                    approval_level = 4
                    role = "QM-Manager"
                    is_dept_head = True
                else:
                    approval_level = 2  # Standard Teamleiter
                    role = "Mitarbeiter"
                    is_dept_head = False
                
                # UserGroupMembership erstellen
                cursor.execute("""
                    INSERT INTO user_group_memberships 
                    (user_id, interest_group_id, approval_level, role_in_group, 
                     is_department_head, is_active, joined_at, assigned_by_id, notes)
                    VALUES (?, ?, ?, ?, ?, 1, ?, 1, ?)
                """, (
                    user_id, 
                    group_id, 
                    approval_level, 
                    role,
                    is_dept_head,
                    datetime.now().isoformat(),
                    f"Automatisch repariert bei Missing Groups Fix - {dept} → {group_name}"
                ))
                
                repairs_made += 1
                print(f"   ✅ Zugeordnet zu: {group_name} (Level {approval_level}, {role})")
                
            else:
                print(f"   ⚠️ Keine passende Gruppe für Abteilung '{dept}' gefunden")
        
        # 5. System Admin zusätzliche Berechtigung hinzufügen
        cursor.execute("SELECT id FROM users WHERE email LIKE '%admin%' OR organizational_unit = 'System Administration'")
        admin_users = cursor.fetchall()
        
        for admin_user in admin_users:
            admin_id = admin_user[0]
            
            # Prüfe ob individual_permissions bereits gesetzt
            cursor.execute("SELECT individual_permissions FROM users WHERE id = ?", (admin_id,))
            current_perms = cursor.fetchone()[0]
            
            admin_permissions = [
                "system_administration",
                "final_approval", 
                "all_rights",
                "user_management",
                "document_creation",
                "document_approval"
            ]
            
            if current_perms:
                try:
                    existing_perms = json.loads(current_perms)
                    # Merge permissions
                    all_perms = list(set(existing_perms + admin_permissions))
                except:
                    all_perms = admin_permissions
            else:
                all_perms = admin_permissions
            
            cursor.execute(
                "UPDATE users SET individual_permissions = ? WHERE id = ?",
                (json.dumps(all_perms), admin_id)
            )
            print(f"   🔧 Admin-Berechtigungen aktualisiert für User {admin_id}")
        
        conn.commit()
        
        print()
        print(f"🎉 Reparatur abgeschlossen!")
        print(f"   📊 {repairs_made} Benutzer-Gruppen-Zuordnungen erstellt")
        print(f"   🔧 {len(admin_users)} Admin-Berechtigungen aktualisiert")
        
        # 6. Verifikation
        print("\n🔍 Verifikation der Reparaturen:")
        cursor.execute("""
            SELECT u.id, u.full_name, u.email, u.organizational_unit,
                   COUNT(ugm.id) as group_count,
                   GROUP_CONCAT(ig.name) as groups
            FROM users u
            LEFT JOIN user_group_memberships ugm ON u.id = ugm.user_id AND ugm.is_active = 1
            LEFT JOIN interest_groups ig ON ugm.interest_group_id = ig.id
            WHERE u.is_active = 1
            GROUP BY u.id
        """)
        verification = cursor.fetchall()
        
        for user in verification:
            user_id, name, email, dept, group_count, groups_str = user
            groups_display = groups_str if groups_str else "KEINE"
            status = "✅" if group_count > 0 else "❌"
            print(f"   {status} User {user_id}: {name} | {group_count} Gruppen: {groups_display}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Reparatur: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_user_groups()
    if success:
        print("\n✅ Script erfolgreich ausgeführt!")
        print("🔄 Starten Sie das Backend neu, um die Änderungen zu übernehmen.")
    else:
        print("\n❌ Script-Ausführung fehlgeschlagen!")
        sys.exit(1) 