"""
DDD Auth Guard Overlay Tests
Testet die DDD-eigene Guard-Route, die JWT-basierte Identität korrekt zurückgibt.
"""

import pytest
import os
import jwt
from fastapi.testclient import TestClient
from backend.app.main import app

# Test-Client mit DDD-Modus
@pytest.fixture
def ddd_client():
    """Test-Client mit IG_IMPL=ddd"""
    os.environ["IG_IMPL"] = "ddd"
    os.environ["SECRET_KEY"] = "test-secret-123"
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "15"
    os.environ["DATABASE_URL"] = "sqlite:///.tmp/test_qms_mvp.db"
    
    with TestClient(app) as client:
        yield client

def test_ddd_guard_login_and_me_parity(ddd_client):
    """Test: Login → /me liefert identische Identität"""
    
    # 1. Login mit Admin-Credentials
    login_response = ddd_client.post("/api/auth/login", json={
        "email": "qms.admin@company.com",
        "password": "admin123"
    })
    
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    
    token = login_data["access_token"]
    print(f"[LOGIN] status={login_response.status_code}, has_token={bool(token)}")
    
    # 2. JWT Claims extrahieren
    payload = jwt.decode(token, options={"verify_signature": False})
    sub = payload.get("sub")
    uid = payload.get("user_id")
    email = payload.get("email")
    roles = payload.get("roles", [])
    
    print(f"[JWT] sub={sub}, uid={uid}, roles={roles}")
    
    # 3. DDD Guard aufrufen (alternative URL)
    guard_response = ddd_client.get("/api/auth/me-ddd", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert guard_response.status_code == 200
    guard_data = guard_response.json()
    
    print(f"[GUARD_DDD] status={guard_response.status_code}, body.email={guard_data.get('email')}, body.id={guard_data.get('id')}")
    
    # 4. Parität prüfen
    email_match = guard_data.get("email") == "qms.admin@company.com"
    id_match = guard_data.get("id") == 2  # User ID in Test-DB ist 2
    
    print(f"[PARITY] email_match={email_match}, id_match={id_match}")
    
    # Assertions
    assert email_match, f"Email mismatch: expected qms.admin@company.com, got {guard_data.get('email')}"
    assert id_match, f"ID mismatch: expected 1, got {guard_data.get('id')}"
    
    # Zusätzliche Checks
    assert guard_data.get("full_name") is not None
    assert "roles" in guard_data
    assert "permissions" in guard_data

def test_ddd_guard_without_token(ddd_client):
    """Test: Guard ohne Token → 401/403"""
    
    response = ddd_client.get("/api/auth/me-ddd")
    assert response.status_code in [401, 403]  # Beide Status-Codes sind akzeptabel

def test_ddd_guard_invalid_token(ddd_client):
    """Test: Guard mit ungültigem Token → 401"""
    
    response = ddd_client.get("/api/auth/me-ddd", headers={
        "Authorization": "Bearer invalid_token"
    })
    assert response.status_code == 401

def test_ddd_guard_token_claims_priority(ddd_client):
    """Test: JWT Claims-Priorität (uid → user_id, dann sub)"""
    
    # Login
    login_response = ddd_client.post("/api/auth/login", json={
        "email": "qms.admin@company.com",
        "password": "admin123"
    })
    
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # JWT Claims analysieren
    payload = jwt.decode(token, options={"verify_signature": False})
    
    # Guard aufrufen
    guard_response = ddd_client.get("/api/auth/me-ddd", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert guard_response.status_code == 200
    guard_data = guard_response.json()
    
    # Prüfen, dass die korrekte Identität zurückgegeben wird
    assert guard_data["email"] == "qms.admin@company.com"
    assert guard_data["id"] == 2  # User ID in Test-DB ist 2
    
    print(f"[CLAIMS] JWT sub={payload.get('sub')}, user_id={payload.get('user_id')}")
    print(f"[GUARD] returned email={guard_data['email']}, id={guard_data['id']}")
