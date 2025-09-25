"""
Password Policy Detection und Validation
Erkennt Hash-Schemes und validiert Passwort-Komplexität
"""

import re
from typing import Dict, Any, Optional
import hashlib
import secrets
import string


def detect_hash_scheme(value: str) -> Dict[str, Any]:
    """
    Erkennt das Hash-Schema aus einem Hash-Wert
    
    Args:
        value: Hash-Wert aus der Datenbank
    
    Returns:
        Dict mit scheme und valid Flag
    """
    if not value or not isinstance(value, str):
        return {"scheme": "unknown", "valid": False}
    
    # BCrypt: $2a$, $2b$, $2y$
    if value.startswith("$2a$") or value.startswith("$2b$") or value.startswith("$2y$"):
        # BCrypt Format: $2b$cost$salt+hash (60 Zeichen total)
        if len(value) == 60 and value.count("$") == 3:
            return {"scheme": "bcrypt", "valid": True}
        else:
            return {"scheme": "bcrypt", "valid": False}
    
    # Argon2: $argon2id$, $argon2i$, $argon2d$
    if value.startswith("$argon2"):
        # Argon2 Format: $argon2id$v=19$m=65536,t=2,p=1$salt$hash
        if "$v=" in value and "$m=" in value and "$t=" in value:
            return {"scheme": "argon2", "valid": True}
        else:
            return {"scheme": "argon2", "valid": False}
    
    # PBKDF2: pbkdf2:sha256:iterations:salt:hash
    if value.startswith("pbkdf2:"):
        parts = value.split(":")
        if len(parts) >= 5 and parts[1] in ["sha256", "sha512"]:
            try:
                int(parts[2])  # iterations should be numeric
                return {"scheme": "pbkdf2", "valid": True}
            except ValueError:
                return {"scheme": "pbkdf2", "valid": False}
        else:
            return {"scheme": "pbkdf2", "valid": False}
    
    # MD5: 32 hex chars
    if len(value) == 32 and all(c in "0123456789abcdef" for c in value.lower()):
        return {"scheme": "md5", "valid": True}
    
    # SHA1: 40 hex chars
    if len(value) == 40 and all(c in "0123456789abcdef" for c in value.lower()):
        return {"scheme": "sha1", "valid": True}
    
    # SHA256: 64 hex chars
    if len(value) == 64 and all(c in "0123456789abcdef" for c in value.lower()):
        return {"scheme": "sha256", "valid": True}
    
    return {"scheme": "unknown", "valid": False}


def validate_password_complexity(password: str) -> Dict[str, Any]:
    """
    Validiert Passwort-Komplexität (nur dokumentieren, nicht erzwingen)
    
    Args:
        password: Klartext-Passwort
    
    Returns:
        Dict mit Validierungsergebnissen
    """
    if not password:
        return {
            "valid": False,
            "length_ok": False,
            "has_uppercase": False,
            "has_lowercase": False,
            "has_digit": False,
            "has_special": False,
            "issues": ["Password is empty"]
        }
    
    issues = []
    
    # Mindestlänge
    length_ok = len(password) >= 8
    if not length_ok:
        issues.append("Password too short (minimum 8 characters)")
    
    # Großbuchstaben
    has_uppercase = bool(re.search(r'[A-Z]', password))
    if not has_uppercase:
        issues.append("No uppercase letters")
    
    # Kleinbuchstaben
    has_lowercase = bool(re.search(r'[a-z]', password))
    if not has_lowercase:
        issues.append("No lowercase letters")
    
    # Ziffern
    has_digit = bool(re.search(r'\d', password))
    if not has_digit:
        issues.append("No digits")
    
    # Sonderzeichen
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    if not has_special:
        issues.append("No special characters")
    
    # Common passwords (einfache Liste)
    common_passwords = [
        "123456", "password", "123456789", "12345678", "12345",
        "1234567", "1234567890", "qwerty", "abc123", "password123"
    ]
    
    if password.lower() in common_passwords:
        issues.append("Common password detected")
    
    return {
        "valid": len(issues) == 0,
        "length_ok": length_ok,
        "has_uppercase": has_uppercase,
        "has_lowercase": has_lowercase,
        "has_digit": has_digit,
        "has_special": has_special,
        "issues": issues
    }


def make_password_hash(password: str, scheme: str = "bcrypt") -> str:
    """
    Erstellt einen Passwort-Hash (nur für Seed-Fallback; niemals Klartext loggen)
    
    Args:
        password: Klartext-Passwort
        scheme: Hash-Schema (bcrypt, argon2, pbkdf2, md5, sha256)
    
    Returns:
        Hash-Wert
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Sicherheitshinweis: Niemals Klartext-Passwörter loggen
    print(f"[PASSWORD] Creating hash with scheme: {scheme}")
    
    if scheme == "bcrypt":
        # BCrypt mit passlib (falls verfügbar)
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            return pwd_context.hash(password)
        except ImportError:
            # Fallback: Einfacher BCrypt-ähnlicher Hash
            salt = secrets.token_hex(16)
            combined = password + salt
            hash_obj = hashlib.sha256(combined.encode())
            return f"$2b$12${salt}${hash_obj.hexdigest()[:22]}"
    
    elif scheme == "argon2":
        # Argon2 (falls verfügbar)
        try:
            from argon2 import PasswordHasher
            ph = PasswordHasher()
            return ph.hash(password)
        except ImportError:
            # Fallback: SHA256 mit Salt
            salt = secrets.token_hex(16)
            combined = password + salt
            hash_obj = hashlib.sha256(combined.encode())
            return f"$argon2id$v=19$m=65536,t=2,p=1${salt}${hash_obj.hexdigest()}"
    
    elif scheme == "pbkdf2":
        # PBKDF2
        salt = secrets.token_hex(16)
        iterations = 100000
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), iterations)
        return f"pbkdf2:sha256:{iterations}:{salt}:{hash_obj.hex()}"
    
    elif scheme == "md5":
        # MD5 (unsicher, nur für Tests)
        return hashlib.md5(password.encode()).hexdigest()
    
    elif scheme == "sha256":
        # SHA256 (unsicher ohne Salt, nur für Tests)
        return hashlib.sha256(password.encode()).hexdigest()
    
    else:
        raise ValueError(f"Unsupported hash scheme: {scheme}")


def generate_secure_password(length: int = 12) -> str:
    """
    Generiert ein sicheres Passwort für Tests
    
    Args:
        length: Passwort-Länge
    
    Returns:
        Sicheres Passwort
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # Sicherstellen, dass mindestens ein Zeichen jeder Kategorie vorhanden ist
    if not re.search(r'[A-Z]', password):
        password = password[:-1] + secrets.choice(string.ascii_uppercase)
    if not re.search(r'[a-z]', password):
        password = password[:-1] + secrets.choice(string.ascii_lowercase)
    if not re.search(r'\d', password):
        password = password[:-1] + secrets.choice(string.digits)
    if not re.search(r'[!@#$%^&*]', password):
        password = password[:-1] + secrets.choice("!@#$%^&*")
    
    return password


def is_common_password(password: str) -> bool:
    """
    Prüft ob ein Passwort zu den häufigsten gehört
    
    Args:
        password: Klartext-Passwort
    
    Returns:
        True wenn es ein häufiges Passwort ist
    """
    common_passwords = [
        "123456", "password", "123456789", "12345678", "12345",
        "1234567", "1234567890", "qwerty", "abc123", "password123",
        "admin", "root", "user", "test", "guest", "welcome"
    ]
    
    return password.lower() in common_passwords

