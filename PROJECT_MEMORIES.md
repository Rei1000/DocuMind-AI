# Projekt-Memories - DocuMind-AI DDD Migration

## 1. DB/Route Unifier aktiv (same_engine=true)
DDD-Auth-Login und DDD-Guard verwenden identische Datenbank-Sessions über UserRepositoryImpl mit DATABASE_URL. DB-Binding-Logs zeigen engine_url=sqlite:////Users/reiner/Documents/DocuMind-AI/qms_mvp.db für beide Komponenten.

## 2. DDD-Guard-Overlay verfügbar unter /api/auth/me-ddd (nur bei IG_IMPL=ddd)
Zusätzliche Guard-Route für DDD-spezifische Authentifizierung. Frontend-kompatible Route /api/auth/me bleibt erhalten. Beide Routen verwenden dieselbe DB-Session.

## 3. Intentional Non-Parity-Liste gepflegt
POST /api/interest-groups duplicate handling: legacy=200 vs ddd=409. Weitere Non-Parity-Fälle in REPORT_rules.md dokumentiert.

## 4. ENV-Switch
Das Projekt kann in zwei Modi laufen:
- **Standard = Legacy** (IG_IMPL nicht gesetzt)
- **DDD-Modus** durch Umgebungsvariable `IG_IMPL=ddd` aktivieren

**Implementierung:** ENV-Weiche in `backend/app/main.py` Zeile 714

## 2. Allowlist/Denylist
**Nur Änderungen erlaubt in:**
- `contexts/interestgroups/application/`
- `tests/**`

**Niemals ändern:**
- `backend/**`
- `router.py`
- `repositories.py`

## 3. Teststruktur
- Alle Paritätstests vergleichen Legacy vs. DDD und dokumentieren Unterschiede
- Tests dürfen angepasst werden, aber Produktivcode außerhalb der Allowlist bleibt unangetastet
- Paritätstests in `tests/characterization/interestgroups/`

## 4. Schema-Extras
- Beim Bootstrap werden `sqlite_schema_extras_test.sql` angewendet
- Diese Datei enthält zusätzliche Indizes und Constraints für Testzwecke
- Schema-Extras werden über `tests/helpers/bootstrap_from_schema.py` geladen

## 5. Regression Snapshot
- **Snapshot (2025-09-10 09:15):** Legacy P=107 F=87 E=0 S=6, DDD P=111 F=83 E=0 S=6, Delta +4/−4/±0/±0
- **Intentional Non-Parity:** POST /api/interest-groups duplicate (Legacy 200 vs DDD 409)
- **Auth-Routen:** Login /api/auth/login (JSON email/password → access_token), Guard /api/auth/me (Bearer)

## 6. Soft Delete Policy
- Für Interest Groups gilt Soft Delete (`is_active = false`)
- Hard Delete wird nicht verwendet, um Datenkonsistenz sicherzustellen
- DELETE-Endpoints setzen `is_active = False` und geben 200 OK zurück

## 6. JSON-Serialisierung
- `group_permissions` werden vor DB-Insert als JSON-String serialisiert
- Nur wenn Typ `list` oder `dict` → `json.dumps(value, ensure_ascii=False)`
- `None`/`""` bleiben unverändert (Legacy-Compat)

## 7. Regression-Status (2025-09-04)
- **Legacy:** 73/21/0/2 (P/F/E/S)
- **DDD:** 83/13/0/0 (P/F/E/S)
- **Delta:** +10/-8 (DDD robuster nach JSON-Fix)

## 8. Regression Snapshot (2025-01-09 14:45)
- **Snapshot:** Legacy 100/83/0/5, DDD 105/80/0/3, Delta +5/−3
- **Intentional non-parity:** IG duplicate (Legacy 200 vs DDD 409)
- **Auth:** Login /api/auth/login (JSON email/password → access_token), Guard /api/auth/me (Bearer)

## 9. Commit-Policy
- Dokumentation und Tests können committet werden
- Produktivcode außerhalb Allowlist bleibt unverändert
- ADR-008 dokumentiert aktuellen Regression-Status

## 10. Diagnose-Logs
- Tests und Helper geben Diagnose-Logs aus:
  - `[ROUTING]` → zeigt aktiven Modus (legacy/ddd)
  - `[SCHEMA-EXTRAS]` → bestätigt Anwendung zusätzlicher Constraints
  - `[RUNTIME]` → zeigt genutzte DB-Dateien und Tabellen
- Logs dienen der Nachvollziehbarkeit in Regressionstests

## 10. Vergleichs-Helper
- Alle Response-Vergleiche laufen über `tests/helpers/compare.py`
- Unterstützt Dict- und List-Bodies (Canonicalisierung, Feld-Subset-Vergleiche)

## 11. How-to Regression
- **Legacy:** `pytest -q tests/characterization/interestgroups`
- **DDD:** `IG_IMPL=ddd pytest -q tests/characterization/interestgroups`

## 12. Pflege
- Diese Datei wird bei Änderungen an Weiche, Policies oder Testinfrastruktur aktualisiert
- Verantwortlich: <Team/Owner>
- Stand: 2025-09-04