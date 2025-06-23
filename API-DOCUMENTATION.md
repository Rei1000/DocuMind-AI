# KI-QMS API Documentation 📚

> **Comprehensive RESTful API Documentation for KI-QMS v2.0.0**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.3-blue.svg)](https://swagger.io/specification/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![ISO 13485](https://img.shields.io/badge/ISO_13485-compliant-blue.svg)](https://www.iso.org/standard/59752.html)

## 📋 Inhaltsverzeichnis

- [🎯 API-Überblick](#-api-überblick)
- [🔐 Authentifizierung](#-authentifizierung)
- [📊 API-Endpunkte](#-api-endpunkte)
- [📝 Request/Response-Schemas](#-requestresponse-schemas)
- [🛡️ Fehlerbehandlung](#️-fehlerbehandlung)
- [📈 Rate Limiting](#-rate-limiting)
- [🧪 Testing & Entwicklung](#-testing--entwicklung)
- [📖 Code-Beispiele](#-code-beispiele)

## 🎯 API-Überblick

### Base URL

```
Development:   http://localhost:8000/
```

### API-Versioning

```
Current Version: v1
Format:          /api/v1/{resource}
Deprecation:     12 months notice
```

### Interaktive Dokumentation

| Interface | URL | Beschreibung |
|-----------|-----|--------------|
| **Swagger UI** | `/docs` | Interaktive API-Tests |
| **ReDoc** | `/redoc` | Strukturierte Dokumentation |
| **OpenAPI JSON** | `/openapi.json` | API-Spezifikation |

### Content Types

- **Request**: `application/json`, `multipart/form-data` (für Datei-Uploads)
- **Response**: `application/json`
- **Encoding**: UTF-8

## 🔐 Authentifizierung

### OAuth2 mit JWT

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@company.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user_id": 2,
  "user_name": "Max Mustermann"
}
```

### Permissions-System

| Permission Level | Code | Beschreibung |
|------------------|------|--------------|
| **Standard** | `1` | Basis-Berechtigung (Lesen) |
| **Teamleiter** | `2` | Team-Verwaltung + Prüfung |
| **Abteilungsleiter** | `3` | Abteilungs-Freigaben |
| **QM-Manager** | `4` | System-weite QM-Freigaben |

## 📊 API-Endpunkte

### 🏥 System & Health

| Methode | Endpunkt | Beschreibung | Auth |
|---------|----------|--------------|------|
| `GET` | `/health` | System-Status | ❌ |
| `GET` | `/version` | API-Version und Build-Info | ❌ |
| `GET` | `/metrics` | System-Metriken | ✅ |

### 🔐 Authentication

| Methode | Endpunkt | Beschreibung | Auth |
|---------|----------|--------------|------|
| `POST` | `/api/auth/login` | Benutzer-Anmeldung | ❌ |
| `POST` | `/api/auth/logout` | Benutzer-Abmeldung | ✅ |
| `POST` | `/api/auth/refresh` | Token erneuern | ✅ |
| `POST` | `/api/auth/reset-password` | Passwort zurücksetzen | ❌ |

### 👥 Users

| Methode | Endpunkt | Beschreibung | Permissions |
|---------|----------|--------------|-------------|
| `GET` | `/api/users` | Alle Benutzer | ✅ |
| `POST` | `/api/users` | Benutzer erstellen | ✅ |
| `GET` | `/api/users/{user_id}` | Einzelnen Benutzer abrufen | `user_read` |
| `PUT` | `/api/users/{user_id}` | Benutzer aktualisieren | `user_update` |
| `DELETE` | `/api/users/{user_id}` | Benutzer deaktivieren | `user_delete` |
| `GET` | `/api/users/me/profile` | Eigenes Profil | ✅ |
| `PUT` | `/api/users/me/profile` | Eigenes Profil aktualisieren | ✅ |
| `GET` | `/api/users/{user_id}/departments` | Benutzer-Abteilungen | `user_read` |

### 🏢 Interest Groups

| Methode | Endpunkt | Beschreibung | Permissions |
|---------|----------|--------------|-------------|
| `GET` | `/api/interest-groups` | Alle Interessensgruppen | `group_read` |
| `POST` | `/api/interest-groups` | Neue Gruppe erstellen | `group_create` |
| `GET` | `/api/interest-groups/{group_id}` | Einzelne Gruppe abrufen | `group_read` |
| `PUT` | `/api/interest-groups/{group_id}` | Gruppe aktualisieren | `group_update` |
| `DELETE` | `/api/interest-groups/{group_id}` | Gruppe deaktivieren | `group_delete` |

### 📄 Documents

| Methode | Endpunkt | Beschreibung | Permissions |
|---------|----------|--------------|-------------|
| `GET` | `/api/documents` | Dokumente auflisten | ✅ |
| `POST` | `/api/documents` | Dokument erstellen | ✅ |
| `POST` | `/api/documents/with-file` | Mit Datei-Upload | ✅ |
| `GET` | `/api/documents/{doc_id}` | Dokument abrufen | `document_read` |
| `PUT` | `/api/documents/{doc_id}` | Dokument aktualisieren | `document_update` |
| `DELETE` | `/api/documents/{doc_id}` | Dokument löschen | `document_delete` |
| `PUT` | `/api/documents/{doc_id}/status` | Status ändern | `document_approve` |
| `GET` | `/api/documents/{doc_id}/history` | Status-Historie | `document_read` |
| `POST` | `/api/documents/upload` | Datei hochladen | `document_create` |

### ⚙️ Equipment

| Methode | Endpunkt | Beschreibung | Permissions |
|---------|----------|--------------|-------------|
| `GET` | `/api/equipment` | Equipment auflisten | `equipment_read` |
| `POST` | `/api/equipment` | Equipment erstellen | `equipment_create` |
| `GET` | `/api/equipment/{eq_id}` | Equipment abrufen | `equipment_read` |
| `PUT` | `/api/equipment/{eq_id}` | Equipment aktualisieren | `equipment_update` |
| `DELETE` | `/api/equipment/{eq_id}` | Equipment deaktivieren | `equipment_delete` |
| `GET` | `/api/equipment/due-calibrations` | Überfällige Kalibrierungen | `equipment_read` |

### 🔧 Calibrations

| Methode | Endpunkt | Beschreibung | Permissions |
|---------|----------|--------------|-------------|
| `GET` | `/api/calibrations` | Kalibrierungen auflisten | `calibration_read` |
| `POST` | `/api/calibrations` | Kalibrierung erstellen | `calibration_create` |
| `GET` | `/api/calibrations/{cal_id}` | Kalibrierung abrufen | `calibration_read` |
| `PUT` | `/api/calibrations/{cal_id}` | Kalibrierung aktualisieren | `calibration_update` |

### 📋 Norms

| Methode | Endpunkt | Beschreibung | Permissions |
|---------|----------|--------------|-------------|
| `GET` | `/api/norms` | Normen auflisten | `norm_read` |
| `POST` | `/api/norms` | Norm erstellen | `norm_create` |
| `GET` | `/api/norms/{norm_id}` | Norm abrufen | `norm_read` |
| `PUT` | `/api/norms/{norm_id}` | Norm aktualisieren | `norm_update` |

## 📝 Request/Response-Schemas

### User Schema

```json
{
  "UserCreate": {
    "email": "string (EmailStr)",
    "full_name": "string (2-200 chars)",
    "employee_id": "string (optional, 50 chars)",
    "organizational_unit": "string (optional, 100 chars)",
    "password": "string (8-128 chars, strong password required)",
    "individual_permissions": ["string"],
    "is_department_head": "boolean",
    "approval_level": "integer (1-4)"
  },
  "UserResponse": {
    "id": "integer",
    "email": "string",
    "full_name": "string",
    "employee_id": "string|null",
    "organizational_unit": "string|null",
    "individual_permissions": ["string"],
    "is_department_head": "boolean",
    "approval_level": "integer",
    "is_active": "boolean",
    "created_at": "datetime (ISO 8601)"
  }
}
```

### Document Schema

```json
{
  "DocumentCreate": {
    "title": "string (2-255 chars)",
    "document_type": "enum (QM_MANUAL|SOP|WORK_INSTRUCTION|...)",
    "version": "string (20 chars, default: '1.0')",
    "content": "string (optional, 10000 chars)",
    "creator_id": "integer",
    "file_name": "string (optional, 255 chars)",
    "file_size": "integer (optional, >= 0)",
    "mime_type": "string (optional, 100 chars)",
    "remarks": "string (optional, 2000 chars)",
    "chapter_numbers": "string (optional, 200 chars)",
    "compliance_status": "enum (ZU_BEWERTEN|EINGEHALTEN|TEILWEISE|NICHT_ZUTREFFEND)",
    "priority": "enum (HOCH|MITTEL|NIEDRIG)",
    "scope": "string (optional, 1000 chars)"
  },
  "DocumentResponse": {
    "id": "integer",
    "title": "string",
    "document_number": "string (auto-generated)",
    "document_type": "enum",
    "version": "string",
    "status": "enum (DRAFT|REVIEWED|APPROVED|OBSOLETE)",
    "content": "string|null",
    "file_path": "string|null",
    "file_name": "string|null",
    "file_size": "integer|null",
    "file_hash": "string|null (SHA-256)",
    "mime_type": "string|null",
    "extracted_text": "string|null",
    "keywords": "string|null",
    "creator_id": "integer",
    "created_at": "datetime",
    "updated_at": "datetime",
    "reviewed_by_id": "integer|null",
    "reviewed_at": "datetime|null",
    "approved_by_id": "integer|null",
    "approved_at": "datetime|null",
    "creator": "UserResponse|null",
    "reviewed_by": "UserResponse|null",
    "approved_by": "UserResponse|null"
  }
}
```

### Equipment Schema

```json
{
  "EquipmentCreate": {
    "name": "string (required)",
    "equipment_number": "string (unique, required)",
    "manufacturer": "string (optional)",
    "model": "string (optional)",
    "serial_number": "string (unique, required)",
    "location": "string (optional)",
    "status": "enum (active|maintenance|retired, default: active)",
    "calibration_interval_months": "integer (default: 12)"
  },
  "EquipmentResponse": {
    "id": "integer",
    "name": "string",
    "equipment_number": "string",
    "manufacturer": "string|null",
    "model": "string|null",
    "serial_number": "string",
    "location": "string|null",
    "status": "enum",
    "calibration_interval_months": "integer",
    "last_calibration": "datetime|null",
    "next_calibration": "datetime|null",
    "created_at": "datetime"
  }
}
```

## 🛡️ Fehlerbehandlung

### Standard HTTP Status Codes

| Code | Name | Verwendung |
|------|------|------------|
| `200` | OK | Erfolgreich |
| `201` | Created | Erfolgreich erstellt |
| `204` | No Content | Erfolgreich gelöscht (DELETE) |
| `400` | Bad Request | Ungültige Anfrage |
| `401` | Unauthorized | Authentifizierung erforderlich |
| `403` | Forbidden | Keine Berechtigung |
| `404` | Not Found | Ressource nicht gefunden |
| `409` | Conflict | Konflikt (z.B. Duplikat) |
| `422` | Unprocessable Entity | Validierungsfehler |
| `429` | Too Many Requests | Rate Limit überschritten |
| `500` | Internal Server Error | Server-Fehler |

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Die übermittelten Daten sind ungültig.",
    "details": [
      {
        "field": "email",
        "message": "Ungültiges E-Mail-Format.",
        "type": "value_error.email"
      }
    ],
    "timestamp": "2024-12-20T10:30:00Z",
    "path": "/api/users",
    "request_id": "req_123456789"
  }
}
```

### Error Codes

| Code | Beschreibung | HTTP Status |
|------|--------------|-------------|
| `VALIDATION_ERROR` | Pydantic Validierungsfehler | 422 |
| `AUTHENTICATION_FAILED` | Login-Daten ungültig | 401 |
| `TOKEN_EXPIRED` | JWT Token abgelaufen | 401 |
| `PERMISSION_DENIED` | Fehlende Berechtigung | 403 |
| `RESOURCE_NOT_FOUND` | Ressource existiert nicht | 404 |
| `DUPLICATE_ENTRY` | Eindeutigkeit verletzt | 409 |
| `RATE_LIMIT_EXCEEDED` | Zu viele Anfragen | 429 |
| `INTERNAL_ERROR` | Server-Fehler | 500 |

## 📈 Rate Limiting

### Standard Limits

| Endpunkt-Typ | Limit | Zeitfenster |
|---------------|-------|-------------|
| **Authentication** | 5 Versuche | 15 Minuten |
| **File Upload** | 10 Uploads | 1 Stunde |
| **Standard API** | 1000 Requests | 1 Stunde |
| **Bulk Operations** | 100 Requests | 1 Stunde |

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640001600
X-RateLimit-Window: 3600
```

## 🧪 Testing & Entwicklung

### Test Server

```bash
# Development Server starten
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Mit Debug-Modus
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level debug
```

### API-Testing mit curl

```bash
# Health Check
curl -X GET "http://localhost:8000/health"

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@company.com", "password": "admin123"}'

# Dokumente abrufen
curl -X GET "http://localhost:8000/api/documents" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Dokument erstellen
curl -X POST "http://localhost:8000/api/documents" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test SOP",
    "document_type": "SOP",
    "version": "1.0",
    "content": "Dies ist ein Test-Dokument.",
    "creator_id": 1
  }'
```

### Python Client Beispiel

```python
import requests

class QMSClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def login(self, email: str, password: str) -> bool:
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return True
        return False

# Verwendung
client = QMSClient()
if client.login("admin@company.com", "admin123"):
    documents = client.get_documents()
    print(f"Gefunden: {len(documents)} Dokumente")
```

## 📖 Code-Beispiele

### JavaScript/Fetch

```javascript
class QMSAPIClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.token = null;
    }

    async login(email, password) {
        const response = await fetch(`${this.baseURL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });
        
        if (response.ok) {
            const data = await response.json();
            this.token = data.access_token;
            return true;
        }
        return false;
    }

    async getDocuments() {
        const response = await fetch(`${this.baseURL}/api/documents`, {
            headers: {
                'Authorization': `Bearer ${this.token}`,
            },
        });
        return response.json();
    }

    async createDocument(documentData) {
        const response = await fetch(`${this.baseURL}/api/documents`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(documentData),
        });
        return response.json();
    }
}

// Verwendung
const client = new QMSAPIClient();
await client.login('admin@company.com', 'admin123');
const documents = await client.getDocuments();
console.log(`Gefunden: ${documents.length} Dokumente`);
```

### Postman Collection

```json
{
  "info": {
    "name": "KI-QMS API",
    "version": "2.0.0",
    "description": "Complete API collection for KI-QMS"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"{{user_email}}\",\n  \"password\": \"{{user_password}}\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/auth/login",
              "host": ["{{base_url}}"],
              "path": ["api", "auth", "login"]
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "user_email",
      "value": "admin@company.com"
    },
    {
      "key": "user_password",
      "value": "admin123"
    }
  ]
}
```

---

## 📞 Support & Kontakt

- **📧 Technical Support:** [api-support@ki-qms.com](mailto:api-support@ki-qms.com)
- **📖 API Issues:** [GitHub Issues](https://github.com/IhrUsername/KI-QMS/issues)
- **💡 Feature Requests:** [GitHub Discussions](https://github.com/IhrUsername/KI-QMS/discussions)
- **📚 Wiki:** [API Wiki](https://github.com/IhrUsername/KI-QMS/wiki)

---

**KI-QMS API Documentation v2.0.0** | **Last Updated: 2024-12-20** | **FastAPI 0.110+** 