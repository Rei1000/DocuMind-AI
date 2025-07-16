#!/usr/bin/env python3
"""
Fix Password Hashes and Database Structure Script
=================================================

Repariert beschädigte Passwort-Hashes und fügt fehlende Datenbank-Spalten hinzu.

Hintergrund:
- Einige Passwort-Hashes sind beschädigt und verursachen bcrypt-Fehler
- Die approval_level Spalte fehlt in user_group_memberships
- Das verursacht 500-Fehler beim Profil-Laden

"""

import sqlite3
import shutil
from datetime import datetime
import os
import sys
from passlib.context import CryptContext

# Füge das Backend-Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def backup_database(db_path: str) -> str:
    """Erstellt ein Backup der Datenbank"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{db_path}.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"📦 Backup erstellt: {backup_path}")
    return backup_path

def fix_password_hashes():
    """Repariert beschädigte Passwort-Hashes"""
    db_path = "qms_mvp.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank {db_path} nicht gefunden!")
        return False
    
    # Backup erstellen
    backup_path = backup_database(db_path)
    
    try:
        # Passwort-Kontext für bcrypt
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Verbindung zur Datenbank
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Überprüfe Benutzer und Passwort-Hashes...")
        
        # Alle Benutzer abrufen
        cursor.execute("SELECT id, email, full_name, hashed_password FROM users")
        users = cursor.fetchall()
        
        print(f"👥 Gefunden: {len(users)} Benutzer")
        
        # Bekannte Passwörter für Reparatur
        known_passwords = {
            "qms.admin@company.com": "Admin42!",  # Neues Passwort vom User
            "reiner@company.com": "SecurePassword123!",  # Falls verwendet
        }
        
        fixed_count = 0
        for user_id, email, full_name, hashed_password in users:
            print(f"\n👤 Überprüfe: {full_name} ({email})")
            
            # Teste ob Hash gültig ist
            hash_valid = True
            if hashed_password:
                try:
                    # Teste mit einem Dummy-Passwort
                    pwd_context.verify("test", hashed_password)
                except:
                    try:
                        # Nochmal testen, falls verify fehlschlägt wegen falschem Passwort
                        pwd_context.identify(hashed_password)
                    except:
                        hash_valid = False
            else:
                hash_valid = False
            
            if not hash_valid:
                print(f"  ⚠️  Hash ist beschädigt oder fehlt")
                
                # Versuche bekanntes Passwort
                if email in known_passwords:
                    new_password = known_passwords[email]
                    new_hash = pwd_context.hash(new_password)
                    
                    cursor.execute(
                        "UPDATE users SET hashed_password = ? WHERE id = ?",
                        (new_hash, user_id)
                    )
                    
                    print(f"  ✅ Hash repariert mit bekanntem Passwort")
                    fixed_count += 1
                else:
                    print(f"  ❌ Kein bekanntes Passwort für {email}")
            else:
                print(f"  ✅ Hash ist gültig")
        
        # Überprüfe ob approval_level Spalte existiert
        print(f"\n🔍 Überprüfe Datenbank-Struktur...")
        
        try:
            cursor.execute("SELECT approval_level FROM user_group_memberships LIMIT 1")
            print("  ✅ approval_level Spalte existiert bereits")
        except sqlite3.OperationalError:
            print("  ⚠️  approval_level Spalte fehlt, füge hinzu...")
            cursor.execute(
                "ALTER TABLE user_group_memberships ADD COLUMN approval_level INTEGER DEFAULT 1"
            )
            print("  ✅ approval_level Spalte hinzugefügt")
        
        # Änderungen speichern
        conn.commit()
        conn.close()
        
        print(f"\n✅ Fertig!")
        print(f"   📊 {fixed_count} Passwort-Hashes repariert")
        print(f"   💾 Backup: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Reparieren: {e}")
        
        # Backup wiederherstellen bei Fehler
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, db_path)
            print(f"🔄 Backup wiederhergestellt")
        
        return False

if __name__ == "__main__":
    print("🔧 KI-QMS Password Hash & Database Repair")
    print("=" * 50)
    
    if fix_password_hashes():
        print("\n🎉 Reparatur erfolgreich abgeschlossen!")
        print("💡 Du kannst dich jetzt mit den reparierten Passwörtern anmelden.")
    else:
        print("\n❌ Reparatur fehlgeschlagen!")
        print("💡 Prüfe die Fehlermeldungen und versuche es erneut.") 