"""
OpenAPI Routes Snapshot für Interest Groups
Extrahiert alle verfügbaren API-Routen und erstellt eine Markdown-Dokumentation
"""

import pytest
import os
import sys
from pathlib import Path

# Projekt-Root fest verdrahten
PROJECT_ROOT = Path("/Users/reiner/Documents/DocuMind-AI").resolve()
BACKEND = PROJECT_ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Test-DB-Pfad sicher setzen
os.environ.setdefault("DATABASE_URL", "sqlite:////Users/reiner/Documents/DocuMind-AI/qms_mvp.db")

from app.main import app


class TestOpenAPIRoutesSnapshot:
    """Test der OpenAPI-Routen-Extraktion"""
    
    def test_extract_openapi_routes(self):
        """Extrahiert alle OpenAPI-Routen und erstellt Markdown-Dokumentation"""
        # OpenAPI-Schema abrufen
        openapi_schema = app.openapi()
        paths = openapi_schema.get("paths", {})
        
        # Interest Groups relevante Pfade definieren
        interest_groups_paths = [
            "/api/interest-groups",
            "/api/interest-groups/{group_id}"
        ]
        
        # Markdown-Tabelle erstellen
        markdown_content = """# OpenAPI Routes für Interest Groups

## Übersicht aller verfügbaren API-Routen

| Methode | Pfad | Handler-Funktion | Modulpfad | Interest Groups relevant |
|---------|------|------------------|-----------|-------------------------|
"""
        
        # Alle Routen durchgehen
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    # Handler-Funktion extrahieren
                    handler = operation.get("operationId", "N/A")
                    
                    # Modulpfad schätzen (basierend auf Tags)
                    tags = operation.get("tags", [])
                    module_path = "backend.app.main" if tags else "backend.app.main"
                    
                    # Interest Groups relevant markieren
                    is_ig_relevant = any(ig_path in path for ig_path in interest_groups_paths)
                    ig_marker = "✅" if is_ig_relevant else "❌"
                    
                    markdown_content += f"| {method.upper()} | {path} | {handler} | {module_path} | {ig_marker} |\n"
        
        # Markdown-Datei schreiben
        docs_dir = PROJECT_ROOT / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        markdown_file = docs_dir / "_openapi_interestgroups.md"
        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        print(f"✅ OpenAPI-Routen wurden nach {markdown_file} exportiert")
        
        # Zusätzliche Statistiken
        total_routes = len(paths)
        ig_routes = sum(1 for path in paths if any(ig_path in path for ig_path in interest_groups_paths))
        
        print(f"📊 Gesamtanzahl Routen: {total_routes}")
        print(f"🎯 Interest Groups relevante Routen: {ig_routes}")
        
        # Erfolg bestätigen
        assert markdown_file.exists(), "Markdown-Datei wurde nicht erstellt"
        assert total_routes > 0, "Keine Routen gefunden"
    
    def test_interest_groups_specific_routes(self):
        """Test: Interest Groups spezifische Routen sind verfügbar"""
        openapi_schema = app.openapi()
        paths = openapi_schema.get("paths", {})
        
        # Erwartete Interest Groups Routen
        expected_routes = [
            "/api/interest-groups",
            "/api/interest-groups/{group_id}"
        ]
        
        # Verfügbare Routen prüfen
        available_routes = []
        for path in paths.keys():
            if any(ig_path in path for ig_path in expected_routes):
                available_routes.append(path)
        
        print(f"🔍 Verfügbare Interest Groups Routen: {available_routes}")
        
        # Mindestens die Basis-Route sollte existieren
        assert len(available_routes) > 0, "Keine Interest Groups Routen gefunden"
        
        # Alle erwarteten Routen sollten verfügbar sein
        for expected_route in expected_routes:
            route_found = any(expected_route in available_route for available_route in available_routes)
            assert route_found, f"Route {expected_route} nicht gefunden"
