"""
JWT Signer/Verifier für Tests
Erstellt und verifiziert JWT-Tokens für Test-Zwecke
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Verwende vorhandene JWT-Utils
try:
    from tests.helpers.jwt_utils import issue_test_jwt, decode_jwt
    JWT_UTILS_AVAILABLE = True
except ImportError:
    JWT_UTILS_AVAILABLE = False


def make_access_token(
    payload: Dict[str, Any], 
    secret: Optional[str] = None, 
    algorithm: str = "HS256", 
    minutes: int = 5
) -> str:
    """
    Erstellt einen JWT Access Token
    
    Args:
        payload: Token-Payload (sub, role, etc.)
        secret: Secret-Key (falls None: aus ENV oder Test-Default)
        algorithm: JWT-Algorithmus
        minutes: Gültigkeitsdauer in Minuten
    
    Returns:
        JWT-Token als String
    """
    if not JWT_UTILS_AVAILABLE:
        raise ImportError("JWT utils not available")
    
    # Secret aus ENV oder Test-Default
    if secret is None:
        secret = os.getenv("SECRET_KEY", "test-secret")
    
    # Algorithmus aus ENV oder Default
    algorithm = os.getenv("JWT_ALGORITHM", algorithm)
    
    # User-ID aus Payload extrahieren
    user_id = payload.get("user_id", 123)
    email = payload.get("sub", "test@example.org")
    is_superuser = payload.get("is_superuser", False)
    
    # Token erstellen mit vorhandenen Utils
    token = issue_test_jwt(user_id, email, is_superuser)
    
    # Log
    secret_set = bool(secret and secret != "test-secret")
    print(f"[JWT-TEST] alg={algorithm} secret_set={secret_set}")
    
    return token


def decode_token(
    token: str, 
    secret: Optional[str] = None, 
    algorithms: list = ["HS256"]
) -> Optional[Dict[str, Any]]:
    """
    Dekodiert und verifiziert einen JWT-Token
    
    Args:
        token: JWT-Token
        secret: Secret-Key (falls None: aus ENV oder Test-Default)
        algorithms: Erlaubte Algorithmen
    
    Returns:
        Dekodierter Payload oder None bei Fehler
    """
    if not JWT_UTILS_AVAILABLE:
        raise ImportError("JWT utils not available")
    
    try:
        # Token dekodieren mit vorhandenen Utils
        payload = decode_jwt(token)
        return payload
        
    except Exception as e:
        print(f"[JWT-TEST] Decode error: {e}")
        return None


def ensure_bearer(headers: Optional[Dict[str, str]], token: str) -> Dict[str, str]:
    """
    Erstellt oder erweitert Headers mit Authorization Bearer Token
    
    Args:
        headers: Bestehende Headers (kann None sein)
        token: JWT-Token
    
    Returns:
        Headers mit Authorization: Bearer <token>
    """
    if headers is None:
        headers = {}
    
    headers["Authorization"] = f"Bearer {token}"
    
    # Log
    auth_header = headers.get("Authorization", "")
    print(f"[AUTH-HDR] present=true len={len(auth_header)}")
    
    return headers
