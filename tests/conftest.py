import os, sys
from pathlib import Path

# Projekt-Root fest verdrahten (siehe Nutzerpfad)
PROJECT_ROOT = Path("/Users/reiner/Documents/DocuMind-AI").resolve()
BACKEND = PROJECT_ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import pytest
from fastapi.testclient import TestClient

# Import nach dem sys.path Setup
from app.main import app as fastapi_app

@pytest.fixture(scope="session")
def app():
    return fastapi_app

@pytest.fixture()
def client(app):
    return TestClient(app)
