#!/usr/bin/env python3
"""
Rebuild QMS Database from Schema Dump

Usage:
    python rebuild_qms_db_from_dump.py --out /path/to/output.db [--schema /path/to/schema.sql]
"""

import argparse
import sqlite3
import os
import sys
from pathlib import Path


def rebuild_database(output_path: str, schema_path: str = "db/schema/sqlite_schema.sql") -> int:
    """
    Rebuild database from schema dump
    
    Args:
        output_path: Path to output database
        schema_path: Path to schema SQL file
        
    Returns:
        0 on success, non-zero on error
    """
    try:
        # Convert to absolute paths
        output_path = Path(output_path).resolve()
        schema_path = Path(schema_path).resolve()
        
        # Check if schema file exists
        if not schema_path.exists():
            print(f"ERROR: Schema file not found: {schema_path}")
            return 1
            
        # Remove output file if it exists
        if output_path.exists():
            os.remove(output_path)
            print(f"Removed existing database: {output_path}")
            
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read schema file
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        # Create new database and execute schema
        conn = sqlite3.connect(output_path)
        conn.executescript(schema_sql)
        conn.close()
        
        # Verify database was created and count tables
        conn = sqlite3.connect(output_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        table_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"[REBUILD] out={output_path} tables={table_count}")
        return 0
        
    except Exception as e:
        print(f"ERROR: Failed to rebuild database: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Rebuild QMS database from schema dump")
    parser.add_argument("--out", required=True, help="Output database path")
    parser.add_argument("--schema", default="db/schema/sqlite_schema.sql", help="Schema SQL file path")
    
    args = parser.parse_args()
    
    exit_code = rebuild_database(args.out, args.schema)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
