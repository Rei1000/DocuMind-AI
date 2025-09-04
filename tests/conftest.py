import sys, sysconfig, os, sqlite3
from pathlib import Path

# venv-Info ausgeben
print(f"[VENV] executable={sys.executable}")
print(f"[VENV] prefix={sys.prefix}")

# Test-DB-Pfad definieren
TEST_DB = "/Users/reiner/Documents/DocuMind-AI/.tmp/test_qms_mvp.db"

# Verzeichnis .tmp anlegen, falls nicht vorhanden
tmp_dir = Path(TEST_DB).parent
tmp_dir.mkdir(exist_ok=True)

# Projekt-Root in sys.path einfügen, damit backend.* importierbar ist
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Test-DB aus Schema aufbauen
try:
    from tests.helpers.bootstrap_from_schema import make_fresh_test_db, insert_seed_data
    
    # Frische Test-DB erstellen
    db_info = make_fresh_test_db(TEST_DB)
    
    # Seed-Daten einfügen
    seed_rows = insert_seed_data(TEST_DB, "db/seed/interest_groups_seed.sql")
    
    print(f"[TEST-DB] path={TEST_DB} tables={db_info['tables']} seed_rows={seed_rows}")
    
except Exception as e:
    print(f"ERROR: Failed to bootstrap test database: {e}")
    sys.exit(1)

# ENV-Variablen für Test-DB setzen
os.environ["DATABASE_URL"] = f"sqlite:////{TEST_DB.lstrip('/')}"
os.environ["SQLALCHEMY_DATABASE_URL"] = f"sqlite:////{TEST_DB.lstrip('/')}"

# Prüfen, dass ENV-Variablen korrekt gesetzt sind
expected_url = f"sqlite:////{TEST_DB.lstrip('/')}"
if os.environ.get("DATABASE_URL") != expected_url or os.environ.get("SQLALCHEMY_DATABASE_URL") != expected_url:
    print(f"ERROR: ENV variables not set correctly!")
    print(f"Expected: {expected_url}")
    print(f"Actual DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    print(f"Actual SQLALCHEMY_DATABASE_URL: {os.environ.get('SQLALCHEMY_DATABASE_URL')}")
    sys.exit(1)

# WICHTIG: App-DB-Konfiguration überschreiben, bevor die App importiert wird
import backend.app.database
backend.app.database.DATABASE_URL = expected_url
backend.app.database.engine = backend.app.database.create_engine(
    expected_url,
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    },
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    echo=False
)
backend.app.database.SessionLocal = backend.app.database.sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=backend.app.database.engine
)

import pytest
from fastapi.testclient import TestClient

# Import nach dem sys.path Setup und der DB-Konfiguration
from backend.app.main import app as fastapi_app

@pytest.fixture(scope="session")
def app():
    return fastapi_app

@pytest.fixture()
def client(app):
    return TestClient(app)
