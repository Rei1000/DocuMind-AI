"""
Auth Test Configuration
Setzt Test-Environment für JWT/Auth-Tests mit Hard Bind + Override
"""

import os
import pytest
import sqlite3
from pathlib import Path
from typing import Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Absoluter Pfad zur Test-DB
TEST_DB_ABS = "/Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"


def hard_bind_auth_schema():
    """
    Hard Bind: Erstellt Auth-Schema an absolutem Pfad
    """
    try:
        # Datei löschen falls vorhanden
        if Path(TEST_DB_ABS).exists():
            os.remove(TEST_DB_ABS)
        
        # Verzeichnis erstellen
        Path(TEST_DB_ABS).parent.mkdir(parents=True, exist_ok=True)
        
        # Neue DB erstellen und Schemas ausführen
        conn = sqlite3.connect(TEST_DB_ABS)
        
        # 1. Base schema
        base_schema_path = Path("db/schema/sqlite_schema.sql")
        if base_schema_path.exists():
            with open(base_schema_path, 'r', encoding='utf-8') as f:
                base_schema_sql = f.read()
            conn.executescript(base_schema_sql)
        
        # 2. Test extras
        extras_path = Path("db/schema/sqlite_schema_extras_test.sql")
        if extras_path.exists():
            with open(extras_path, 'r', encoding='utf-8') as f:
                extras_sql = f.read()
            conn.executescript(extras_sql)
        
        # 3. Auth extras
        auth_extras_path = Path("db/schema/sqlite_schema_auth_extras.sql")
        if auth_extras_path.exists():
            with open(auth_extras_path, 'r', encoding='utf-8') as f:
                auth_extras_sql = f.read()
            conn.executescript(auth_extras_sql)
        
        conn.close()
        
        # Tabellen zählen
        conn = sqlite3.connect(TEST_DB_ABS)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        first5 = tables[:5] if tables else []
        print(f"[SCHEMA-AUTH-EXTRAS] db={TEST_DB_ABS} tables={len(tables)} first5={first5}")
        
    except Exception as e:
        raise RuntimeError(f"Failed to create auth schema at {TEST_DB_ABS}: {e}")


def monkeypatch_database_engine():
    """
    Monkeypatch: Setzt Engine auf Test-DB
    """
    try:
        import backend.app.database as db
        
        # Neue Engine erstellen
        engine_url = f"sqlite:///{TEST_DB_ABS}"
        new_engine = create_engine(engine_url)
        
        # Monkeypatch setzen
        db.engine = new_engine
        db.SessionLocal = sessionmaker(bind=new_engine)
        
        # Probe-Query
        with new_engine.connect() as conn:
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in result]
            
            # PRAGMA database_list
            db_list_result = conn.execute("PRAGMA database_list").fetchall()
        
        # Verifizieren
        if 'users' not in tables:
            print(f"[MONKEYPATCH-ERROR] engine_url={engine_url}")
            print(f"[MONKEYPATCH-ERROR] tables={tables[:10]}")
            print(f"[MONKEYPATCH-ERROR] PRAGMA database_list: {db_list_result}")
            raise RuntimeError("users table not found after monkeypatch")
        
        print(f"[RUNTIME] engine_url={engine_url}")
        print(f"[RUNTIME] db_list={db_list_result}")
        print(f"[RUNTIME] tables={len(tables)} first5={tables[:5]}")
        
    except Exception as e:
        print(f"[MONKEYPATCH-ERROR] Failed: {e}")
        raise


def setup_auth_dependency_overrides(app):
    """
    Setzt Dependency Overrides für Auth (nur JWT-Verifikation, kein DB-Lookup)
    """
    from tests.helpers.jwt_signer import decode_token
    from fastapi import HTTPException, status, Security
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    import os
    
    security = HTTPBearer()
    
    async def test_get_current_user_stub(
        credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> dict:
        """Test Stub für get_current_user Dependency - nur JWT-Verifikation"""
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No credentials provided",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Authorization Header prüfen
        auth_header = credentials.credentials
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # JWT dekodieren
        token = auth_header[7:]  # Remove "Bearer " prefix
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        claims = decode_token(token, secret="test-secret", algorithms=[algorithm])
        
        if not claims:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Expiry prüfen
        if "exp" in claims:
            import time
            if claims["exp"] < time.time():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # User-Objekt erstellen (minimal für Guard)
        user_obj = {
            "id": claims.get("user_id", claims.get("sub", "unknown")),
            "email": claims.get("email", claims.get("sub", "unknown@example.org")),
            "role": claims.get("role", "user"),
            "is_superuser": claims.get("is_superuser", False)
        }
        
        # Log
        print(f"[GUARD-OVR] ok=true email={user_obj['email']} role={user_obj['role']}")
        
        return user_obj
    
    async def test_get_current_active_user_stub(current_user: dict = None) -> dict:
        """Test Stub für get_current_active_user Dependency"""
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No current user",
            )
        
        return current_user
    
    # Dependency Overrides setzen (falls die Dependencies existieren)
    try:
        from backend.app.auth import get_current_user, get_current_active_user
        app.dependency_overrides[get_current_user] = test_get_current_user_stub
        app.dependency_overrides[get_current_active_user] = test_get_current_active_user_stub
        print(f"[AUTH-OVERRIDE] deps=['get_current_user','get_current_active_user'] applied=true")
    except ImportError:
        # Fallback: Suche nach anderen Auth-Dependencies
        print(f"[AUTH-OVERRIDE] Standard auth deps not found, using fallback")
        # Hier könnten weitere Dependency-Namen versucht werden


def before_import_env(env: Dict[str, str]) -> None:
    """
    Hook: Setzt JWT-Environment vor App-Import
    """
    # DB-Binding eindeutig setzen
    env["DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
    env["SQLALCHEMY_DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
    
    # JWT-Environment
    env["JWT_ALGORITHM"] = "HS256"
    env["SECRET_KEY"] = "test-secret"
    env["ACCESS_TOKEN_EXPIRE_MINUTES"] = "5"
    env["JWT_SECRET"] = "test-secret"
    env["TOKEN_URL"] = "/api/auth/login"
    env["TEST_JWT_SECRET"] = "test-jwt-secret-key-for-deterministic-tokens"
    env["TEST_JWT_ALGORITHM"] = "HS256"


def after_import_override(app) -> None:
    """
    Hook: Setzt Dependency Overrides nach App-Import
    """
    # Hard Bind + Monkeypatch
    hard_bind_auth_schema()
    monkeypatch_database_engine()
    
    # Dependency Overrides
    setup_auth_dependency_overrides(app)


@pytest.fixture(scope="session", autouse=True)
def setup_auth_test_env():
    """
    Setzt Test-Environment für Auth-Tests
    """
    print(f"[AUTH-TEST-ENV] JWT_ALGORITHM=HS256, SECRET_KEY=test-secret, ACCESS_TOKEN_EXPIRE_MINUTES=5")
    
    yield
    
    # Cleanup (falls nötig)
    pass
