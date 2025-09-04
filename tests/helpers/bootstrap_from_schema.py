"""
Test Database Bootstrap Helper

Creates fresh test databases from schema dumps for isolated testing.
"""

import sqlite3
import os
from pathlib import Path
from typing import Dict, Any


def set_env_db(db_path: str) -> None:
    """
    Set DATABASE_URL and SQLALCHEMY_DATABASE_URL environment variables
    
    Args:
        db_path: Path to database file
    """
    db_url = f"sqlite:///{db_path}"
    os.environ["DATABASE_URL"] = db_url
    os.environ["SQLALCHEMY_DATABASE_URL"] = db_url


def make_fresh_db_at(db_path: str, schema_path: str = "db/schema/sqlite_schema.sql") -> int:
    """
    Delete db_path, create new DB from schema dump, return table count
    
    Args:
        db_path: Path to target database
        schema_path: Path to schema SQL file
        
    Returns:
        Number of tables created
    """
    try:
        # Convert to absolute paths
        db_path = Path(db_path).resolve()
        schema_path = Path(schema_path).resolve()
        
        # Check if schema file exists
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
            
        # Remove target file if it exists
        if db_path.exists():
            os.remove(db_path)
            
        # Create target directory if it doesn't exist
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read schema file
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        # Create new database and execute schema
        conn = sqlite3.connect(db_path)
        conn.executescript(schema_sql)
        
        # Apply schema extras if they exist
        extras_path = Path("db/schema/sqlite_schema_extras_test.sql")
        if extras_path.exists():
            with open(extras_path, 'r', encoding='utf-8') as f:
                extras_sql = f.read()
            conn.executescript(extras_sql)
            print(f"[SCHEMA-EXTRAS] applied=true tables=")
        else:
            print(f"[SCHEMA-EXTRAS] applied=false tables=")
        
        conn.close()
        
        # Verify database was created and count tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        table_count = cursor.fetchone()[0]
        conn.close()
        
        return table_count
        
    except Exception as e:
        raise RuntimeError(f"Failed to create fresh database at {db_path}: {e}")


def make_fresh_test_db(target_path: str, schema_path: str = "db/schema/sqlite_schema.sql") -> Dict[str, Any]:
    """
    Create a fresh test database from schema
    
    Args:
        target_path: Path to target test database
        schema_path: Path to schema SQL file
        
    Returns:
        Dict with 'path' and 'tables' keys
    """
    try:
        # Convert to absolute paths
        target_path = Path(target_path).resolve()
        schema_path = Path(schema_path).resolve()
        
        # Check if schema file exists
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
            
        # Remove target file if it exists
        if target_path.exists():
            os.remove(target_path)
            
        # Create target directory if it doesn't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read schema file
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        # Create new database and execute schema
        conn = sqlite3.connect(target_path)
        conn.executescript(schema_sql)
        
        # Apply schema extras if they exist
        extras_path = Path("db/schema/sqlite_schema_extras_test.sql")
        if extras_path.exists():
            with open(extras_path, 'r', encoding='utf-8') as f:
                extras_sql = f.read()
            conn.executescript(extras_sql)
            print(f"[SCHEMA-EXTRAS] applied=true tables=")
        else:
            print(f"[SCHEMA-EXTRAS] applied=false tables=")
        
        conn.close()
        
        # Verify database was created and count tables
        conn = sqlite3.connect(target_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        table_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "path": str(target_path),
            "tables": table_count
        }
        
    except Exception as e:
        raise RuntimeError(f"Failed to create fresh test database: {e}")


def insert_seed_data(target_path: str, seed_path: str = None) -> int:
    """
    Insert seed data into test database
    
    Args:
        target_path: Path to target test database
        seed_path: Path to seed SQL file (optional)
        
    Returns:
        Number of rows inserted
    """
    if not seed_path or not Path(seed_path).exists():
        return 0
        
    try:
        with open(seed_path, 'r', encoding='utf-8') as f:
            seed_sql = f.read()
            
        conn = sqlite3.connect(target_path)
        conn.executescript(seed_sql)
        conn.close()
        
        # Count rows in interest_groups
        conn = sqlite3.connect(target_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interest_groups")
        row_count = cursor.fetchone()[0]
        conn.close()
        
        return row_count
        
    except Exception as e:
        print(f"Warning: Failed to insert seed data: {e}")
        return 0
