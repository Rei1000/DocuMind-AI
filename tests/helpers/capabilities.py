"""
Capability Detection für Legacy API Endpoints
Erkennt verfügbare Endpoints zur Laufzeit
"""

import os
import sys
from typing import Dict, Any, Optional
from fastapi.testclient import TestClient


def detect_user_api_capabilities() -> Dict[str, bool]:
    """
    Erkennt verfügbare User API Endpoints zur Laufzeit
    
    Returns:
        Dict mit Flags für verfügbare Endpoints
    """
    capabilities = {
        "HAS_USERS_GET": False,
        "HAS_USERS_POST": False,
        "HAS_USERS_PUT": False,
        "HAS_USERS_DELETE": False
    }
    
    try:
        # Import der App
        from backend.app.main import app
        client = TestClient(app)
        
        # Test GET /api/users
        try:
            response = client.get("/api/users")
            capabilities["HAS_USERS_GET"] = response.status_code in [200, 401, 403]  # 401/403 = Endpoint existiert
        except Exception:
            capabilities["HAS_USERS_GET"] = False
        
        # Test GET /api/users/{id}
        try:
            response = client.get("/api/users/1")
            capabilities["HAS_USERS_GET"] = capabilities["HAS_USERS_GET"] or response.status_code in [200, 404, 401, 403]
        except Exception:
            pass
        
        # Test POST /api/users
        try:
            response = client.post("/api/users", json={})
            capabilities["HAS_USERS_POST"] = response.status_code in [400, 401, 403, 422]  # 400/422 = Endpoint existiert
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
        print(f"[CAPABILITIES] Detection failed: {e}")
        # Fallback: Alle auf False setzen
        for key in capabilities:
            capabilities[key] = False
    
    return capabilities


def get_capability_flags() -> Dict[str, bool]:
    """
    Gibt aktuelle Capability-Flags zurück
    
    Returns:
        Dict mit aktuellen Capability-Flags
    """
    return detect_user_api_capabilities()


def log_capabilities() -> None:
    """
    Loggt verfügbare Capabilities
    """
    caps = get_capability_flags()
    print(f"[CAPABILITIES] User API Endpoints:")
    for cap, available in caps.items():
        status = "✓" if available else "✗"
        print(f"[CAPABILITIES]   {cap}: {status}")

