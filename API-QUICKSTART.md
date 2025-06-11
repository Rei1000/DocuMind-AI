# KI-QMS API – Quickstart

Die KI-QMS API ist eine moderne REST-API auf Basis von FastAPI. Sie ermöglicht das Management von Benutzern, Interessensgruppen, Dokumenten, Normen, Equipment und Kalibrierungen.

## Basis-URL

```
http://127.0.0.1:8000/api
```

## Authentifizierung

- **MVP:** Keine Authentifizierung erforderlich (alle Endpunkte offen)
- **Production:** OAuth2/JWT geplant

## Wichtige Endpunkte (Auszug)

### Benutzer (Users)
- `GET    /api/users` – Alle Benutzer auflisten
- `GET    /api/users/{id}` – Einzelnen Benutzer abrufen
- `POST   /api/users` – Benutzer anlegen
- `PUT    /api/users/{id}` – Benutzer aktualisieren
- `DELETE /api/users/{id}` – Benutzer deaktivieren (Soft Delete)

### Interessensgruppen (Interest Groups)
- `GET    /api/interest-groups` – Alle Gruppen
- `POST   /api/interest-groups` – Neue Gruppe anlegen

### Dokumente (Documents)
- `GET    /api/documents` – Dokumente suchen/auflisten
- `POST   /api/documents` – Neues Dokument anlegen

### Normen (Norms)
- `GET    /api/norms` – Alle Normen
- `POST   /api/norms` – Neue Norm anlegen

### Equipment & Kalibrierung
- `GET    /api/equipment` – Alle Geräte
- `POST   /api/equipment` – Gerät anlegen
- `GET    /api/calibrations` – Kalibrierungen auflisten

## Beispiel: Benutzer anlegen

```http
POST /api/users
Content-Type: application/json

{
  "email": "neuer.user@company.com",
  "password": "SicheresPasswort123!",
  "full_name": "Neuer User",
  "employee_id": "NU001",
  "organizational_unit": "Qualitätssicherung"
}
```

## Swagger/OpenAPI

- Interaktive API-Doku: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

**Hinweis:**
- Für Details zu Feldern, Query-Parametern und Response-Strukturen siehe Swagger UI.
- Dokumentation und Notion-Vorlagen sind **nicht** Teil des öffentlichen Repos. 