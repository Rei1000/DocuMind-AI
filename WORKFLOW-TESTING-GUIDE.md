# 🧪 KI-QMS Workflow-Testing Guide

## 🏛️ **System-Architektur Understanding**

### **QMS System Administrator vs. IT-Abteilung**
```
🏛️ QMS SYSTEM ADMINISTRATOR:
   👤 qms.admin@company.com / admin123
   🚫 NICHT Teil der 13 Interessengruppen  
   🔧 Technische System-Administration
   📋 Aufgaben: Benutzer anlegen, System verwalten, Backups

💻 IT-ABTEILUNG (Interessengruppe):
   👥 Teil der 13 Kern-Interessengruppen
   📋 QM-Aufgaben: Software-Validierung, IT-Dokumentation
   🚫 KEINE System-Administration!
```

### **13 Aktive Interessengruppen**
```
 1. Einkauf                  7. Regulatory Affairs      
 2. Qualitätsmanagement      8. Geschäftsleitung       
 3. Entwicklung              9. Externe Auditoren      
 4. Produktion              10. Lieferanten            
 5. Service/Support         11. Team/Eingangsmodul    
 6. Vertrieb                12. HR/Schulung           
                            13. IT-Abteilung          
```

### **Deaktivierte Gruppen** (für später)
- Klinik, IT (old), Kunden, Dokumentation

## 🎯 **WORKFLOW-TESTING MIT VERSCHIEDENEN BENUTZERN**

### 📋 **VERFÜGBARE TEST-BENUTZER**

| **Rolle** | **Email** | **Passwort** | **Level** | **Abteilung** | **Berechtigungen** |
|-----------|-----------|--------------|-----------|----------------|-------------------|
| 🏆 **QMS System Admin** | `qms.admin@company.com` | `admin123` | **4** | System Administration | `system_administration`, `user_management`, `backup_management` |
| 🏆 **QM-Manager** | `test@qms.com` | `test123` | **4** | QM-Manager | `final_approval`, `gap_analysis`, `workflow_oversight` |
| 👑 **Abteilungsleiter** | `max.production@company.com` | `prodpass123` | **3** | Produktion | `production_oversight`, `department_approval` |
| 👤 **Teamleiter** | `sarah.dev@company.com` | `devpass123` | **2** | Entwicklung | `design_approval`, `technical_review` |
| 📝 **Standard-User** | `lisa.assistant@company.com` | `assist123` | **1** | Administration | Basis-Berechtigungen |
| 💻 **IT-Spezialist** | `it.admin@company.com` | `itpass123` | **2** | IT-Abteilung | `software_validation`, `it_documentation` |

> **✅ PASSWORT-UPDATE:** Alle Benutzer-Passwörter wurden korrekt mit BCrypt gehasht und sind einsatzbereit!

## 🔐 Wichtige Rollentrennung

### QMS System Administrator vs. IT-Abteilung
Das System trennt klar zwischen:

1. **🏛️ QMS System Administrator** (`qms.admin@company.com`)
   - **Technische System-Administration** (unabhängig von QM-Prozessen)
   - Berechtigungen: `system_administration`, `user_management`, `backup_management`
   - **NICHT** Teil der 13 Interessengruppen
   - Zuständig für: Benutzer anlegen/ändern, System-Wartung, Datenbank-Administration

2. **💻 IT-Abteilung** (`it.admin@company.com`) 
   - **Fachliche QM-Stakeholder** (Teil der 13 Interessengruppen)
   - Berechtigungen: `software_validation`, `it_documentation`, `system_qualification`
   - Zuständig für: Software-Validierung, IT-QM-Prozesse, System-Dokumentation
   - **KEINE** `system_administration` Rechte!

Diese Trennung gewährleistet **ISO 13485 Compliance** durch klare Rollentrennung!

---

## 🔄 **KOMPLETTER WORKFLOW-TEST**

### **SCHRITT 1: QM-Manager (Admin) - Benutzerverwaltung testen**

1. **Login:** `test@qms.com` / `test123`
2. **Navigation:** 👥 Benutzer
3. **Funktionen testen:**
   - ➕ **Neuen Benutzer erstellen**
   - 📋 **Benutzerliste** durchgehen
   - ❌ **Benutzer deaktivieren/aktivieren**
   - 📊 **Statistiken** anschauen

**Erwartetes Verhalten:**
- ✅ Vollzugriff auf alle Benutzerverwaltung-Funktionen
- ✅ Kann neue Benutzer anlegen
- ✅ Kann Benutzer aktivieren/deaktivieren

---

### **SCHRITT 2: Mitarbeiter - Dokument erstellen**

1. **Logout:** QM-Manager abmelden
2. **Login:** `lisa.assistant@company.com` / `assist123`
3. **Navigation:** 📤 Upload
4. **Dokument hochladen:**
   - Test-PDF oder Word-Datei auswählen
   - Titel: "Test SOP - Reinigungsvalidierung"
   - Typ: SOP
   - Upload starten

**Erwartetes Verhalten:**
- ✅ Kann Dokumente hochladen
- ✅ Status automatisch: `draft`
- ❌ **KEINE** Benutzerverwaltung sichtbar (keine Admin-Rechte)

---

### **SCHRITT 3: Mitarbeiter - Zur Prüfung weiterleiten**

1. **Navigation:** 📋 QM-Workflow
2. **Entwürfe-Tab:** Hochgeladenes Dokument finden
3. **Button:** 🔍 "Zur Prüfung" klicken

**Erwartetes Verhalten:**
- ✅ Status ändert sich: `draft` → `reviewed`
- ✅ Dokument verschwindet aus "Entwürfe"
- ✅ Dokument erscheint in "Geprüft"

---

### **SCHRITT 4: Teamleiter - Kann nicht final freigeben**

1. **Logout:** Lisa abmelden
2. **Login:** `sarah.dev@company.com` / `devpass123`
3. **Navigation:** 📋 QM-Workflow
4. **Geprüft-Tab:** Dokument sehen, aber...

**Erwartetes Verhalten:**
- ✅ Kann Dokument sehen
- ❌ **KEINE** Freigabe-Buttons (nur QM darf final freigeben)
- ✅ Kann eventuell eigene Dokumente zur Prüfung weiterleiten

---

### **SCHRITT 5: QM-Manager - Finale Freigabe**

1. **Logout:** Sarah abmelden
2. **Login:** `test@qms.com` / `test123`
3. **Navigation:** 📋 QM-Workflow
4. **QM-Manager Aktionen:**
   - Dokument zur Freigabe finden
   - ✅ **"Freigeben"** klicken
   - Optional: Kommentar hinzufügen

**Erwartetes Verhalten:**
- ✅ Status ändert sich: `reviewed` → `approved`
- ✅ Dokument erscheint in "Freigegeben"-Tab
- ✅ Benachrichtigung im Backend-Log

---

### **SCHRITT 6: Status-Historie prüfen**

1. **Freigegeben-Tab:** Dokument finden
2. **Button:** 📊 "Historie" klicken

**Erwartetes Verhalten:**
- ✅ Vollständiger Audit-Trail:
  - `draft` → `reviewed` (Lisa Assistent)
  - `reviewed` → `approved` (QM Manager)
- ✅ Kommentare und Zeitstempel

---

### **SCHRITT 7: Ablehnungs-Workflow testen**

1. **Neues Dokument:** Als Lisa ein weiteres Dokument hochladen
2. **Zur Prüfung weiterleiten**
3. **Als QM-Manager:** 
   - ❌ **"Ablehnen"** statt Freigeben
   - **Kommentar:** "Bitte Norm-Referenzen ergänzen"

**Erwartetes Verhalten:**
- ✅ Status: `reviewed` → `draft`
- ✅ Dokument zurück in "Entwürfe"
- ✅ Kommentar in Historie sichtbar

---

### **SCHRITT 8: Abteilungsleiter-Perspektive**

1. **Login:** `max.production@company.com` / `prodpass123`
2. **Funktionen testen:**
   - 📋 **Workflow-Dashboard** einsehen
   - 📤 **Eigene Dokumente** hochladen
   - 👥 **Benutzerverwaltung** → Sollte **NICHT** verfügbar sein

**Erwartetes Verhalten:**
- ✅ Kann Workflow einsehen
- ✅ Kann Dokumente hochladen und weiterleiten
- ❌ **KEINE** Benutzerverwaltung (kein `system_administration`)
- ❌ **KEINE** finale Freigabe (kein QM)

---

## 🎯 **TESTSZENARIEN FÜR VERSCHIEDENE ROLLEN**

### **👥 Benutzerverwaltung**
- **QM-Manager:** ✅ Vollzugriff
- **Abteilungsleiter:** ❌ Kein Zugriff
- **Teamleiter:** ❌ Kein Zugriff
- **Mitarbeiter:** ❌ Kein Zugriff

### **📋 Dokument-Workflow**
- **Erstellen:** ✅ Alle können Dokumente hochladen
- **Zur Prüfung:** ✅ Alle können weiterleiten
- **Freigeben:** ✅ Nur QM-Manager
- **Ablehnen:** ✅ Nur QM-Manager
- **Obsolet setzen:** ✅ Nur QM-Manager

### **📊 Dashboard-Sichtbarkeit**
- **QM-Manager:** ✅ Alle Dokumente und Statistiken
- **Abteilungsleiter:** ✅ Workflow-Übersicht
- **Teamleiter:** ✅ Workflow-Übersicht  
- **Mitarbeiter:** ✅ Workflow-Übersicht

---

## 🧪 **ERWEITERTE TEST-SZENARIEN**

### **Test 1: Bulk-Dokument-Processing**
1. Als verschiedene User mehrere Dokumente hochladen
2. Als QM-Manager batch-weise freigeben
3. Performance und UI-Responsiveness prüfen

### **Test 2: Gleichzeitige Bearbeitung**
1. Mehrere Browser-Tabs mit verschiedenen Usern öffnen
2. Workflow-Schritte parallel durchführen
3. Konflikte und Race-Conditions testen

### **Test 3: Berechtigungs-Edge-Cases**
1. Benutzer während aktiver Session deaktivieren
2. Berechtigungen ändern und Session-Verhalten prüfen
3. Token-Ablauf simulieren

### **Test 4: API-Direktzugriff**
```bash
# Status direkt per API ändern
curl -X PUT http://127.0.0.1:8000/api/documents/1/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"status": "approved", "comment": "API-Test"}'
```

---

## 🔍 **FEHLERBEHANDLUNG TESTEN**

### **Ungültige Login-Daten**
- **Email:** `wrong@email.com` / **Passwort:** `wrong`
- **Erwartet:** ❌ Fehlermeldung "Ungültige Anmeldedaten"

### **Abgelaufene Session**
- Nach 30 Minuten sollte Re-Login erforderlich sein

### **Unberechtigte Aktionen**
- Als Nicht-QM-User versuchen, Status auf `approved` zu setzen
- **Erwartet:** ❌ 403 Forbidden Error

### **Backend-Ausfall**
- Backend stoppen: `./stop-all.sh`
- Frontend sollte graceful degradieren

---

## 📊 **ERFOLGS-KRITERIEN**

### **✅ Funktionale Tests:**
- [x] Login/Logout für alle User-Typen
- [x] Rollenbasierte UI-Sichtbarkeit
- [x] Workflow-Status-Übergänge
- [x] Audit-Trail Vollständigkeit
- [x] Benutzerverwaltung (Admin-only)

### **✅ Sicherheitstests:**
- [x] Unauthorized-Access wird blockiert
- [x] Token-basierte Authentifizierung
- [x] Berechtigungsvalidierung
- [x] Session-Management

### **✅ Usability-Tests:**
- [x] Intuitive Navigation
- [x] Verständliche Fehlermeldungen
- [x] Responsive UI-Updates
- [x] Hilfe-Texte und Tooltips

---

## 🚀 **PRODUKTIVES TESTEN**

Für echte Workflow-Tests:

1. **Mit echten Dokumenten** (PDF, DOCX) testen
2. **Realistische Benutzer-Szenarien** durchspielen
3. **Verschiedene Abteilungen** simulieren
4. **ISO 13485 Compliance** validieren

**Das System ist jetzt bereit für reale QM-Workflows!** 🎉

---

## 📞 **SUPPORT & TROUBLESHOOTING**

Bei Problemen:
1. **Backend-Logs:** `tail -f ./logs/backend.log`
2. **Frontend-Logs:** Browser-Konsole (F12)
3. **API-Dokumentation:** `http://127.0.0.1:8000/docs`
4. **System-Neustart:** `./stop-all.sh && ./start-all.sh` 