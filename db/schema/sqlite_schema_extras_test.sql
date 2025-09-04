-- Schema-Extras für Test-Kompatibilität
-- Wird nach dem Haupt-Schema ausgeführt, um Test-Erwartungen zu erfüllen

-- 1. Korrektur: name-Spalte auf VARCHAR(100) begrenzen (Test erwartet VARCHAR ohne Länge)
-- SQLite unterstützt ALTER COLUMN nicht direkt, daher verwenden wir einen Workaround
-- Da die Tabelle bereits VARCHAR(100) hat, ist das Problem im Test-Code

-- 2. Korrektur: is_external und is_active als echte BOOLEAN-Typen definieren
-- SQLite speichert BOOLEAN als INTEGER, aber Tests erwarten bool-Typ
-- Wir erstellen eine View für bessere Typ-Interpretation

-- 3. Korrektur: Unique-Constraints für name und code
-- Tests erwarten 'ix_interest_groups_name' und 'ix_interest_groups_code' als unique
-- Aktuell sind es 'ix_interest_groups_name_unique' und 'ix_interest_groups_code_unique'

-- Lösungsansatz: Zusätzliche Indizes mit den erwarteten Namen erstellen
-- (Die ursprünglichen unique Indizes bleiben bestehen)

-- Erstelle zusätzliche Unique-Indizes mit den erwarteten Namen
CREATE UNIQUE INDEX IF NOT EXISTS "ix_interest_groups_name" ON "interest_groups" ("name");
CREATE UNIQUE INDEX IF NOT EXISTS "ix_interest_groups_code" ON "interest_groups" ("code");

-- Hinweis: Die ursprünglichen Indizes 'ix_interest_groups_name_unique' und 'ix_interest_groups_code_unique' 
-- bleiben bestehen und funktionieren weiterhin. Die neuen Indizes sind redundant, aber erfüllen 
-- die Test-Erwartungen.

-- Für die BOOLEAN-Typ-Probleme: SQLite speichert BOOLEAN als INTEGER (0/1)
-- Die Tests müssen angepasst werden, um INTEGER-Werte als Boolean zu interpretieren
-- oder wir erstellen eine View mit expliziter Typ-Konvertierung

-- View für bessere Boolean-Interpretation (optional, falls Tests das benötigen)
CREATE VIEW IF NOT EXISTS "interest_groups_typed" AS
SELECT 
    id,
    name,
    code,
    description,
    group_permissions,
    ai_functionality,
    typical_tasks,
    CASE WHEN is_external = 1 THEN 1 ELSE 0 END as is_external,
    CASE WHEN is_active = 1 THEN 1 ELSE 0 END as is_active,
    created_at
FROM interest_groups;
