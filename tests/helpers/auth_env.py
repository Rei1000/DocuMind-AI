"""
Auth Environment Helper
Setzt deterministische Auth-ENV-Variablen für Tests
"""

import os


def set_auth_env_for_tests():
    """
    Setzt deterministische Auth-ENV-Variablen für Tests
    """
    # Deterministische Test-Werte
    os.environ["SECRET_KEY"] = "test-secret-123"
    os.environ["ALGORITHM"] = "HS256"  # Wird in auth.py hardcoded, aber für Konsistenz
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "5"
    
    # Zusätzliche JWT-ENV für Vollständigkeit
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["JWT_SECRET"] = "test-secret-123"
    
    # Log
    secret_set = bool(os.environ.get("SECRET_KEY"))
    algorithm = os.environ.get("ALGORITHM", "HS256")
    exp_minutes = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "5")
    
    print(f"[AUTH-ENV] secret_set={secret_set} alg={algorithm} exp_min={exp_minutes}")


def get_auth_env_summary():
    """
    Gibt eine Zusammenfassung der gesetzten Auth-ENV zurück
    """
    return {
        "SECRET_KEY": os.environ.get("SECRET_KEY", "not_set"),
        "ALGORITHM": os.environ.get("ALGORITHM", "not_set"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "not_set"),
        "JWT_ALGORITHM": os.environ.get("JWT_ALGORITHM", "not_set"),
        "JWT_SECRET": os.environ.get("JWT_SECRET", "not_set")
    }

