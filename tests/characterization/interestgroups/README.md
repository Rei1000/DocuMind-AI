# 🧪 Charakterisierungstests für Interest Groups Management

## Übersicht

Diese Tests dokumentieren das **bestehende Verhalten** des Interest Groups Management Moduls ohne neue Regeln zu erfinden. Sie dienen als "Fotografie" des aktuellen Systems für die DDD+Hex-Refaktorierung.

## 📁 Test-Struktur

```
tests/characterization/interestgroups/
├── README.md                           # Diese Datei
├── test_get_interest_groups.py         # GET /api/interest-groups
├── test_get_interest_group_by_id.py    # GET /api/interest-groups/{id}
├── test_create_interest_group.py       # POST /api/interest-groups
├── test_update_interest_group.py       # PUT /api/interest-groups/{id}
├── test_delete_interest_group.py       # DELETE /api/interest-groups/{id}
├── test_interest_group_business_rules.py # Business Rules der Entity
├── test_permission_handling.py         # Berechtigungsverwaltung
└── test_database_schema.py            # Datenbankstruktur
```

## 🎯 Test-Ziele

### 1. API-Tests (5 Dateien)
- **Alle Endpunkte abgedeckt:** GET, POST, PUT, DELETE
- **Status-Codes dokumentiert:** 200, 404, 422
- **Validierung getestet:** Name, Code, Permissions
- **Fehlerbehandlung:** Ungültige IDs, Duplikate, Constraints

### 2. Business Logic Tests (2 Dateien)
- **Entity-Verhalten:** InterestGroup.get_group_permissions_list()
- **Permission-Parsing:** JSON, Komma-separiert, Fehlerbehandlung
- **Standardwerte:** is_external=False, is_active=True
- **Constraints:** Feldlängen, Unique-Constraints

### 3. Datenbank-Tests (1 Datei)
- **Schema-Struktur:** Alle Spalten, Typen, Constraints
- **Indizes:** Primary Key, Unique-Constraints
- **Foreign Keys:** Beziehungen zu user_group_memberships
- **Constraint-Enforcement:** NOT NULL, UNIQUE

## 🔍 Was wird getestet

### API-Verhalten
- ✅ Alle 5 CRUD-Endpunkte funktionieren
- ✅ Status-Codes sind konsistent
- ✅ Validierung funktioniert korrekt
- ✅ Fehlerbehandlung ist robust
- ✅ Keine Authentifizierung erforderlich

### Business Rules
- ✅ Code-Format: snake_case (2-50 Zeichen)
- ✅ Name-Format: 2-100 Zeichen
- ✅ Permissions: JSON/Liste/Komma-separiert
- ✅ Standardwerte: is_external=False, is_active=True
- ✅ Unique-Constraints: name und code

### Datenbank-Schema
- ✅ Tabelle existiert mit korrekter Struktur
- ✅ Alle 10 Spalten sind vorhanden
- ✅ Datentypen sind korrekt
- ✅ Constraints werden durchgesetzt
- ✅ Beziehungen sind definiert

## ⚠️ Wichtige Hinweise

### Keine neuen Regeln erfinden
- Tests importieren **bestehenden Code** aus `backend/app/`
- Alle Assertions basieren auf **heutigem Verhalten**
- Tests brechen bei **Verhaltensänderungen** (das ist gewollt!)

### Import-Pfade
```python
# Alle Tests importieren aus bestehenden Pfaden
from backend.app.main import app
from backend.app.models import InterestGroup
from backend.app.database import get_db, SessionLocal
```

### Test-Daten
- Tests erstellen temporäre Test-Daten
- Cleanup wird nach jedem Test durchgeführt
- Keine dauerhaften Änderungen an der Datenbank

## 🚀 Ausführung

### Einzelne Tests
```bash
# Alle Tests des Moduls
pytest tests/characterization/interestgroups/

# Einzelne Test-Datei
pytest tests/characterization/interestgroups/test_get_interest_groups.py

# Einzelner Test
pytest tests/characterization/interestgroups/test_get_interest_groups.py::TestGetInterestGroups::test_get_interest_groups_returns_list
```

### Mit Coverage
```bash
pytest tests/characterization/interestgroups/ --cov=backend.app.models --cov-report=html
```

## 📊 Test-Statistiken

- **Gesamtanzahl Tests:** 8 Test-Dateien
- **API-Tests:** 5 Dateien (alle Endpunkte)
- **Business Logic Tests:** 2 Dateien (Entity + Permissions)
- **Datenbank-Tests:** 1 Datei (Schema + Constraints)
- **Geschätzte Test-Cases:** 50+ einzelne Tests

## 🔄 Nächste Schritte

1. **Tests ausführen:** Alle Tests sollten durchlaufen
2. **Verhalten dokumentieren:** Tests zeigen aktuelles System-Verhalten
3. **DDD+Hex-Plan:** Move-Plan basierend auf Tests erstellen
4. **Refaktorierung:** Code schrittweise in neue Struktur verschieben
5. **Tests anpassen:** Neue Pfade nach Refaktorierung verwenden

## 📝 Wartung

### Bei Code-Änderungen
- Tests brechen bei Verhaltensänderungen (gewollt!)
- Neue Tests nur für **neue Funktionalität**
- Bestehende Tests dokumentieren **heutiges Verhalten**

### Bei Schema-Änderungen
- `test_database_schema.py` aktualisieren
- Neue Constraints dokumentieren
- Beziehungen anpassen

---

**Status:** ✅ Charakterisierungstests erstellt  
**Zweck:** Dokumentation des bestehenden Verhaltens für DDD+Hex-Refaktorierung  
**Nächster Schritt:** Tests ausführen und Verhalten dokumentieren
