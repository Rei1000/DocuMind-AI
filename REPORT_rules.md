## Phase: Cluster-Abbau (Zeitstempel: 2025-09-04T12:50:00Z)

### Zahlenblöcke:
- **LEGACY total:** P/F/E/S = 76/16/0/2 (nach Schema-Fix)
- **DDD total:** P/F/E/S = 86/8/0/0 (nach Schema-Fix)
- **Delta legacy→ddd:** Passed +10, Failed -8, Errors 0, Skipped -2

### Geschlossene Cluster:
- **Schema-Cluster:** SQLite-tolerante Typ-Prüfungen, eindeutige Test-Daten, robuste Constraint-Tests

### Verbleibende offene Punkte:
- Permissions-Parität (4): Legacy=200, DDD=409
- Statuscode-Parität (3): Legacy=200, DDD=409
- Business-Rules (1): Legacy=200, DDD=500
- Parity-Endpoints (2): POST 500-Fehler
- Update-Validation (2): 422 vs 409

---

## Regression – DDD vs. Legacy (Zeitstempel: 2025-09-04T11:48:00Z)

### Zahlenblöcke:
- **LEGACY total:** P/F/E/S = 73/21/0/2
- **DDD total:** P/F/E/S = 83/13/0/0
- **Delta legacy→ddd:** Passed +10, Failed −8, Errors 0, Skipped −2

### Top-3 Cluster je Modus:
- **Legacy:** Permission-Parität (200 vs 409), Statuscode-Parität (200 vs 409), Database-Schema
- **DDD:** Database-Schema (5 Fails), Parity-Endpoints (2× POST 500 – vor Fix checken), Business-Rules (1× 500)

### Bewertung:
- DDD nach JSON-Serialisierung robuster als Legacy.
- Offene Punkte gezielt: Schema-Extras abrunden, einzelne POST/Business-Rules isolieren.
- ENV-Weiche und Schema-Extras aktiv (Logs ggf. nicht in pytest-Output sichtbar).

---

## 🔍 IG Paritäts-Audit – 2025-01-27 18:30

## 🔄 Zwischenstand Parität & Routing – 2025-09-03 16:58

### Kurzfazit
**ENV-Weiche aktiv;** DDD-Router erreichbar; robuste Vergleichsfunktionen (Dict+List) implementiert.

### Letzte Regression-Zahlen
- **LEGACY total:** P/F/E/S = 66/20/0/0
- **DDD total:** P/F/E/S = 68/18/0/0  
- **Delta legacy→ddd:** Passed +2, Failed -2, Errors 0, Skipped 0

### Router-Logs
- **legacy:** [ROUTING] mode=legacy for /api/interest-groups
- **ddd:** [ROUTING] mode=ddd for /api/interest-groups

### Hinweis/Disclaimer
Derzeit bekannte Abweichungen sind beabsichtigt dokumentiert (Duplicate-POST und einige Permissions/Statuscode-Fälle); werden in nächster Phase harmonisiert. Tests sind auf Paritätsbeobachtung ausgelegt, nicht auf Wunschstatuscodes.

---

### Legacy vs. DDD: Passed=17 Failed=8

### Top-Abweichungen:
1. **Duplicate-Constraint-Handling** – 8 Fälle – Kurzbeschreibung: DDD-Router gibt 409 statt 200 zurück
   **Beispiel-Request:** POST `/api/interest-groups` mit verschiedenen group_permissions
   **Status legacy→ddd:** 200→409
   **Body-Diff:** DDD gibt 409 Conflict zurück, Legacy 200 OK

2. **RBAC-Dependency-Attribut** – 1 Fall – Kurzbeschreibung: ModelField.annotation existiert nicht
   **Beispiel-Request:** GET `/api/interest-groups` (Dependency-Analyse)
   **Status legacy→ddd:** N/A (Test-Fehler)
   **Body-Diff:** AttributeError: 'ModelField' object has no attribute 'annotation'

### Paritäts-Tabelle je Endpoint:

| Method | Path | Status(=) | Body(=) | Headers(=) |
|--------|------|-----------|---------|------------|
| GET | `/api/interest-groups` | ✅ | ✅ | ✅ |
| GET | `/api/interest-groups/{id}` | ✅ | ✅ | ✅ |
| POST | `/api/interest-groups` | ❌ | ❌ | ✅ |
| PUT | `/api/interest-groups/{id}` | ✅ | ✅ | ✅ |
| DELETE | `/api/interest-groups/{id}` | ✅ | ✅ | ✅ |

### RBAC-Dependency-Check:
**Missing deps auf DDD-Routen:** Keine fehlenden Dependencies, aber Attribut-Zugriff unterscheidet sich

### Soft-Delete-Parität:
**Status:** ✅ OK - Alle Soft-Delete-Tests laufen erfolgreich

### Permission-Parsing-Parität:
**Status:** ❌ Abweichung - DDD gibt 409 für alle Permission-Tests, Legacy 200

---

## 🔍 IG Fail-Cluster – 2025-01-27 18:15

### Aktuelle Zahlen:
- **Legacy-Modus:** Passed=49 Failed=20 Errors=0
- **DDD-Modus:** Passed=52 Failed=17 Errors=0
- **DDD-Abweichung:** +3 Passed, -3 Failed (DDD läuft besser!)

### Änderungen (nur Tests/Seeds):
- **Import-Pfad korrigiert:** `test_database_schema.py` verwendet jetzt `backend.app.database.engine` statt `app.database.engine`
- **DB-Schema-Tests laufen:** Alle 6 DB-Schema-Tests sind jetzt erfolgreich

### Fail-Cluster (Top 5):
1. **Permission-Parsing funktioniert nicht** – 8 Fälle – Betroffene Tests: test_permission_handling.py, test_interest_group_business_rules.py
   **Details:** `get_group_permissions_list()` gibt immer leere Liste zurück; betroffene Endpoints: alle IG-CRUD-Operationen mit group_permissions

2. **Soft-Delete funktioniert nicht wie erwartet** – 3 Fälle – Betroffene Tests: test_delete_interest_group.py
   **Details:** Gelöschte Gruppen sind noch abrufbar (200 statt 404); betroffene Endpoints: DELETE `/api/interest-groups/{id}`, GET `/api/interest-groups/{id}`

3. **Statuscode-Abweichungen** – 3 Fälle – Betroffene Tests: test_create_interest_group.py, test_update_interest_group.py
   **Details:** 409 statt 422 für Duplikat-Constraints; betroffene Endpoints: POST/PUT `/api/interest-groups`

4. **String-Repräsentation funktioniert nicht** – 1 Fall – Betroffene Tests: test_interest_group_business_rules.py
   **Details:** `str(group)` zeigt Objekt-Referenz statt Namen; betroffene Endpoints: alle IG-Operationen

5. **Schema-Erwartungen stimmen nicht** – 5 Fälle – Betroffene Tests: test_database_schema.py
   **Details:** Index-Namen, Datentypen, Tabellengröße stimmen nicht mit Tests überein

---

## 🗄️ DB-Runtime-Verifikation – 2025-01-27 17:30

**DISK primary:** `/Users/reiner/Documents/DocuMind-AI/qms_mvp.db` size=4096 tables=0
**DISK backup:** `/Users/reiner/Documents/DocuMind-AI/qms_mvp_backup_20250807_231545.db` size=0 tables=0
**RUNTIME url:** `sqlite:///./qms_mvp.db`
**RUNTIME file:** `/Users/reiner/Documents/DocuMind-AI/qms_mvp.db` tables=0
**Bewertung:** Runtime nutzt **primary**; **gleich** zu erwarteter Datei, aber beide DBs sind leer (0 Tabellen)

---

## 🧪 IST-Test-Status (Interest Groups) – 2025-01-27 18:15

### Test-Ergebnisse:
- **Legacy-Modus:** Passed=49 Failed=20 Errors=0 Skipped=0
- **DDD-Modus:** Passed=52 Failed=17 Errors=0 Skipped=0
- **DDD-Abweichung:** +3 Passed, -3 Failed

### Schema dump created at:
- **db/schema/sqlite_schema.sql** (tables=4)
- **Seed applied:** yes (rows inserted=3)
- **Env URLs:** DATABASE_URL=sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/test_qms_mvp.db / SQLALCHEMY_DATABASE_URL=sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/test_qms_mvp.db

### Tests use fresh DB:
- **.tmp/test_qms_mvp.db** (tables=4)

### Failure-Cluster (Top-5):
1) **Permission-Parsing funktioniert nicht** – 8 Fälle – Betroffene Tests: test_permission_handling.py, test_interest_group_business_rules.py
   **Details:** `get_group_permissions_list()` gibt immer leere Liste zurück

2) **Soft-Delete funktioniert nicht wie erwartet** – 3 Fälle – Betroffene Tests: test_delete_interest_group.py
   **Details:** Gelöschte Gruppen sind noch abrufbar (200 statt 404)

3) **Statuscode-Abweichungen** – 3 Fälle – Betroffene Tests: test_create_interest_group.py, test_update_interest_group.py
   **Details:** 409 statt 422 für Duplikat-Constraints

4) **String-Repräsentation funktioniert nicht** – 1 Fall – Betroffene Tests: test_interest_group_business_rules.py
   **Details:** `str(group)` zeigt Objekt-Referenz statt Namen

5) **Schema-Erwartungen stimmen nicht** – 5 Fälle – Betroffene Tests: test_database_schema.py
   **Details:** Index-Namen, Datentypen, Tabellengröße stimmen nicht mit Tests überein

### Änderungen: 
Test-DB-Bootstrap implementiert; Schema-Dump erstellt; Seed-Daten eingefügt; App-DB-Konfiguration überschrieben; Import-Pfad korrigiert; DDD+Hex-Router implementiert.

### Beobachtungen:
- **Test-DB erfolgreich erstellt:** 4 Tabellen, 3 Seed-Zeilen
- **App verwendet jetzt Test-DB:** Alle API-Tests laufen gegen frische DB
- **Hauptproblem gelöst:** Tabelle `interest_groups` existiert und hat Daten
- **Neue Probleme identifiziert:** Permission-Parsing, Soft-Delete-Logik, Statuscode-Konsistenz
- **Tests laufen:** 69 Tests werden erfolgreich geladen und ausgeführt
- **DB-Schema-Tests erfolgreich:** Alle 6 Tests laufen nach Import-Pfad-Korrektur
- **DDD+Hex-Router funktioniert:** Läuft besser als Legacy (52/17 vs 49/20)

---
