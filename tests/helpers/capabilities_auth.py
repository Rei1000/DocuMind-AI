"""
Capability Detection für Authentication API Endpoints
Erkennt verfügbare Auth-Endpoints zur Laufzeit
"""

import os
import sys
from typing import Dict, Any, Optional
from fastapi.testclient import TestClient


def detect_auth_api_capabilities() -> Dict[str, bool]:
    """
    Erkennt verfügbare Auth API Endpoints zur Laufzeit
    
    Returns:
        Dict mit Flags für verfügbare Endpoints
    """
    capabilities = {
        "HAS_REGISTER": False,
        "HAS_USER_SET_PASSWORD": False,
        "HAS_RESET_REQUEST": False,
        "HAS_RESET_CONFIRM": False,
        "HAS_CHANGE_PASSWORD": False,
        "HAS_TEMP_PASSWORD": False,
        "HAS_LOGIN": False,
        "HAS_ME": False,
        "HAS_USERS_GET": False,
        "HAS_USERS_POST": False,
        "HAS_USERS_PUT": False,
        "HAS_USERS_DELETE": False
    }
    
    try:
        # Import der App
        from backend.app.main import app
        client = TestClient(app)
        
        # Test POST /api/auth/register
        try:
            response = client.post("/api/auth/register", json={})
            capabilities["HAS_REGISTER"] = response.status_code in [400, 401, 403, 422]  # Endpoint existiert
        except Exception:
            capabilities["HAS_REGISTER"] = False
        
        # Test PUT /api/users/{id}/password
        try:
            response = client.put("/api/users/1/password", json={})
            capabilities["HAS_USER_SET_PASSWORD"] = response.status_code in [400, 401, 403, 404, 422]  # Endpoint existiert
        except Exception:
            capabilities["HAS_USER_SET_PASSWORD"] = False
        
        # Test POST /api/auth/reset/request
        try:
            response = client.post("/api/auth/reset/request", json={})
            capabilities["HAS_RESET_REQUEST"] = response.status_code in [400, 401, 403, 422]  # Endpoint existiert
        except Exception:
            capabilities["HAS_RESET_REQUEST"] = False
        
        # Test POST /api/auth/reset/confirm
        try:
            response = client.post("/api/auth/reset/confirm", json={})
            capabilities["HAS_RESET_CONFIRM"] = response.status_code in [400, 401, 403, 422]  # Endpoint existiert
        except Exception:
            capabilities["HAS_RESET_CONFIRM"] = False
        
        # Test PUT /api/auth/change-password
        try:
            response = client.put("/api/auth/change-password", json={})
            capabilities["HAS_CHANGE_PASSWORD"] = response.status_code in [400, 401, 403, 422]  # Endpoint existiert
        except Exception:
            capabilities["HAS_CHANGE_PASSWORD"] = False
        
        # Test POST /api/users/{id}/temp-password
        try:
            response = client.post("/api/users/1/temp-password", json={})
            capabilities["HAS_TEMP_PASSWORD"] = response.status_code in [400, 401, 403, 404, 422]  # Endpoint existiert
        except Exception:
            capabilities["HAS_TEMP_PASSWORD"] = False
        
        # Test POST /api/auth/login
        try:
            response = client.post("/api/auth/login", json={})
            capabilities["HAS_LOGIN"] = response.status_code in [400, 401, 403, 422]  # Endpoint existiert
        except Exception:
            capabilities["HAS_LOGIN"] = False
        
        # Test GET /api/auth/me
        try:
            response = client.get("/api/auth/me")
            capabilities["HAS_ME"] = response.status_code in [200, 401, 403]  # Endpoint existiert
        except Exception:
            capabilities["HAS_ME"] = False
        
        # Test GET /api/users
        try:
            response = client.get("/api/users")
            capabilities["HAS_USERS_GET"] = response.status_code in [200, 401, 403]  # Endpoint existiert
        except Exception:
            capabilities["HAS_USERS_GET"] = False
        
        # Test POST /api/users
        try:
            response = client.post("/api/users", json={})
            capabilities["HAS_USERS_POST"] = response.status_code in [400, 401, 403, 422]  # Endpoint existiert
        except Exception:
            capabilities["HAS_USERS_POST"] = False
        
        # Test PUT /api/users/{id}
        try:
            response = client.put("/api/users/1", json={})
            capabilities["HAS_USERS_PUT"] = response.status_code in [400, 401, 403, 404, 422]  # Endpoint existiert
        except Exception:
            capabilities["HAS_USERS_PUT"] = False
        
        # Test DELETE /api/users/{id}
        try:
            response = client.delete("/api/users/1")
            capabilities["HAS_USERS_DELETE"] = response.status_code in [200, 204, 401, 403, 404]  # Endpoint existiert
        except Exception:
            capabilities["HAS_USERS_DELETE"] = False
            
    except Exception as e:
        print(f"[CAPABILITIES] Auth detection failed: {e}")
        # Fallback: Alle auf False setzen
        for key in capabilities:
            capabilities[key] = False
    
    return capabilities


def get_auth_capability_flags() -> Dict[str, bool]:
    """
    Gibt aktuelle Auth Capability-Flags zurück
    
    Returns:
        Dict mit aktuellen Auth Capability-Flags
    """
    return detect_auth_api_capabilities()


def log_auth_capabilities() -> None:
    """
    Loggt verfügbare Auth Capabilities
    """
    caps = get_auth_capability_flags()
    print(f"[CAPABILITIES] Auth API Endpoints:")
    for cap, available in caps.items():
        status = "✓" if available else "✗"
        print(f"[CAPABILITIES]   {cap}: {status}")
