"""
JWT Utilities für Test-JWT-Generierung und -Validierung
Erstellt Test-JWTs mit deterministischen Secrets für Seed-Fallbacks
"""

import os
import time
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
import json


# Test-Secret für deterministische JWT-Generierung
TEST_JWT_SECRET = "test-jwt-secret-key-for-deterministic-tokens"
TEST_JWT_ALGORITHM = "HS256"


def set_test_secret_keys() -> None:
    """
    Setzt Test-Secret-Keys für deterministische JWT-Generierung
    """
    os.environ["TEST_JWT_SECRET"] = TEST_JWT_SECRET
    os.environ["TEST_JWT_ALGORITHM"] = TEST_JWT_ALGORITHM
    os.environ["JWT_ALGORITHM"] = TEST_JWT_ALGORITHM
    os.environ["SECRET_KEY"] = TEST_JWT_SECRET
    os.environ["JWT_SECRET"] = TEST_JWT_SECRET
    print(f"[JWT] alg={TEST_JWT_ALGORITHM} secret=deterministic")


def set_test_secret(secret: str = "test-secret") -> None:
    """
    Setzt Test-Secret für JWT
    """
    os.environ["SECRET_KEY"] = secret
    os.environ["JWT_SECRET"] = secret
    os.environ["TEST_JWT_SECRET"] = secret


def issue_test_jwt(
    user_id: int,
    email: str = "test@company.com",
    is_superuser: bool = False,
    expires_in_hours: int = 24,
    claims_override: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generiert Test-JWT mit deterministischem Secret (Seed-Fallback)
    
    Args:
        user_id: User-ID
        email: Email-Adresse
        is_superuser: Superuser-Status
        expires_in_hours: Ablaufzeit in Stunden
        claims_override: Zusätzliche Claims
    
    Returns:
        str: JWT-Token
    """
    try:
        from jose import jwt
        
        # Standard Claims
        now = datetime.utcnow()
        exp = now + timedelta(hours=expires_in_hours)
        
        claims = {
            "sub": str(user_id),
            "email": email,
            "user_id": user_id,
            "is_superuser": is_superuser,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "iss": "test-qms",
            "aud": "test-qms-users"
        }
        
        # Zusätzliche Claims
        if claims_override:
            claims.update(claims_override)
        
        # JWT generieren
        token = jwt.encode(claims, TEST_JWT_SECRET, algorithm=TEST_JWT_ALGORITHM)
        
        print(f"[JWT] Test token issued: user_id={user_id}, exp={exp.isoformat()}")
        return token
        
    except ImportError:
        # Fallback: Einfacher Test-Token ohne jose
        import base64
        import hmac
        import hashlib
        
        # Header
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
        
        # Payload
        now = int(time.time())
        exp = now + (expires_in_hours * 3600)
        
        payload = {
            "sub": str(user_id),
            "email": email,
            "user_id": user_id,
            "is_superuser": is_superuser,
            "iat": now,
            "exp": exp,
            "iss": "test-qms",
            "aud": "test-qms-users"
        }
        
        if claims_override:
            payload.update(claims_override)
        
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
        
        # Signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            TEST_JWT_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        
        print(f"[JWT] Fallback token issued: user_id={user_id}, exp={exp}")
        return token


def decode_jwt(token: str) -> Optional[Dict[str, Any]]:
    """
    Dekodiert JWT-Token (ohne Verifikation für Tests)
    
    Args:
        token: JWT-Token
    
    Returns:
        Dict mit Claims oder None
    """
    try:
        from jose import jwt
        
        # Dekodieren ohne Verifikation (für Tests)
        claims = jwt.decode(token, key="", options={
            "verify_signature": False,
            "verify_aud": False,
            "verify_iss": False,
            "verify_exp": False,
            "verify_nbf": False,
            "verify_iat": False
        })
        return claims
        
    except ImportError:
        # Fallback: Manuelles Dekodieren
        try:
            import base64
            import json
            
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            # Payload dekodieren
            payload_b64 = parts[1]
            # Padding hinzufügen falls nötig
            payload_b64 += '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64)
            payload = json.loads(payload_bytes.decode())
            
            return payload
            
        except Exception as e:
            print(f"[JWT] Decode failed: {e}")
            return None
    
    except Exception as e:
        print(f"[JWT] Decode failed: {e}")
        return None


def assert_claims_subset(token: str, expected: Dict[str, Any]) -> bool:
    """
    Prüft ob Token die erwarteten Claims enthält (Subset)
    
    Args:
        token: JWT-Token
        expected: Erwartete Claims
    
    Returns:
        bool: True wenn alle erwarteten Claims vorhanden sind
    """
    claims = decode_jwt(token)
    if not claims:
        return False
    
    for key, expected_value in expected.items():
        if key not in claims:
            print(f"[JWT] Missing claim: {key}")
            return False
        
        if claims[key] != expected_value:
            print(f"[JWT] Claim mismatch: {key} = {claims[key]} (expected {expected_value})")
            return False
    
    return True


def bearer(token: str) -> Dict[str, str]:
    """
    Erstellt Authorization Header für Bearer Token
    
    Args:
        token: JWT-Token
    
    Returns:
        Dict mit Authorization Header
    """
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def mint_test_token(sub: str, roles: list = None, is_admin: bool = False) -> str:
    """
    Erstellt einen Test-JWT-Token mit dem in ENV gesetzten SECRET/ALG
    
    Args:
        sub: Subject (User-ID oder Email)
        roles: Liste von Rollen
        is_admin: Admin-Flag
    
    Returns:
        JWT-Token als String
    """
    try:
        from jose import jwt
        import os
        import time
        
        # ENV-Werte verwenden
        secret = os.getenv("SECRET_KEY", "test-secret-123")
        algorithm = os.getenv("ALGORITHM", "HS256")
        exp_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "5"))
        
        # Claims erstellen
        now = int(time.time())
        exp = now + (exp_minutes * 60)
        
        claims = {
            "sub": str(sub),
            "user_id": sub,
            "email": f"{sub}@example.org" if "@" not in str(sub) else str(sub),
            "iat": now,
            "exp": exp,
            "iss": "test-qms"
        }
        
        # Rollen hinzufügen
        if roles:
            claims["roles"] = roles
        elif is_admin:
            claims["roles"] = ["qms.admin"]
            claims["is_superuser"] = True
        else:
            claims["roles"] = ["user"]
        
        # Token erstellen
        token = jwt.encode(claims, secret, algorithm=algorithm)
        
        print(f"[JWT-MINT] sub={sub} roles={claims.get('roles')} exp_min={exp_minutes}")
        
        return token
        
    except ImportError:
        # Fallback: Verwende issue_test_jwt
        user_id = int(sub) if sub.isdigit() else 123
        email = f"{sub}@example.org" if "@" not in str(sub) else str(sub)
        return issue_test_jwt(user_id, email, is_admin)


def create_expired_token(
    user_id: int,
    email: str = "test@company.com",
    is_superuser: bool = False,
    expired_hours_ago: int = 1
) -> str:
    """
    Erstellt abgelaufenen JWT-Token für Expiry-Tests
    
    Args:
        user_id: User-ID
        email: Email-Adresse
        is_superuser: Superuser-Status
        expired_hours_ago: Vor wie vielen Stunden abgelaufen
    
    Returns:
        str: Abgelaufener JWT-Token
    """
    now = datetime.utcnow()
    exp = now - timedelta(hours=expired_hours_ago)
    
    claims_override = {
        "exp": int(exp.timestamp())
    }
    
    return issue_test_jwt(user_id, email, is_superuser, claims_override=claims_override)


def assert_in_codes(status: int, expected_codes: set) -> bool:
    """
    Prüft ob Status-Code in erwarteten Codes enthalten ist
    
    Args:
        status: HTTP Status Code
        expected_codes: Set von erwarteten Status Codes
    
    Returns:
        bool: True wenn Status in erwarteten Codes
    """
    return status in expected_codes


def create_token_with_claims(
    user_id: int,
    email: str = "test@company.com",
    is_superuser: bool = False,
    roles: Optional[list] = None,
    permissions: Optional[list] = None,
    expires_in_hours: int = 24
) -> str:
    """
    Erstellt JWT-Token mit spezifischen Claims
    
    Args:
        user_id: User-ID
        email: Email-Adresse
        is_superuser: Superuser-Status
        roles: Rollen-Liste
        permissions: Permissions-Liste
        expires_in_hours: Ablaufzeit in Stunden
    
    Returns:
        str: JWT-Token
    """
    claims_override = {}
    
    if roles:
        claims_override["roles"] = roles
    
    if permissions:
        claims_override["permissions"] = permissions
    
    return issue_test_jwt(user_id, email, is_superuser, expires_in_hours, claims_override)


def get_token_algorithm(token: str) -> Optional[str]:
    """
    Ermittelt den Algorithmus eines JWT-Tokens
    
    Args:
        token: JWT-Token
    
    Returns:
        str: Algorithmus oder None
    """
    try:
        import base64
        import json
        
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Header dekodieren
        header_b64 = parts[0]
        header_b64 += '=' * (4 - len(header_b64) % 4)
        header_bytes = base64.urlsafe_b64decode(header_b64)
        header = json.loads(header_bytes.decode())
        
        return header.get("alg")
        
    except Exception as e:
        print(f"[JWT] Algorithm detection failed: {e}")
        return None


def is_token_expired(token: str) -> bool:
    """
    Prüft ob JWT-Token abgelaufen ist
    
    Args:
        token: JWT-Token
    
    Returns:
        bool: True wenn abgelaufen
    """
    claims = decode_jwt(token)
    if not claims or "exp" not in claims:
        return True
    
    exp_timestamp = claims["exp"]
    now_timestamp = int(time.time())
    
    # 60 Sekunden Toleranz für Boundary-Tests
    return exp_timestamp < (now_timestamp - 60)


def log_jwt_info(token: str) -> None:
    """
    Loggt JWT-Informationen für Debugging
    
    Args:
        token: JWT-Token
    """
    claims = decode_jwt(token)
    algorithm = get_token_algorithm(token)
    expired = is_token_expired(token)
    
    print(f"[JWT] Token info: alg={algorithm}, expired={expired}, claims={list(claims.keys()) if claims else 'None'}")
