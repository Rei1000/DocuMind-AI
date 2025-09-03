"""
A/B Test Runner für Legacy vs. DDD Vergleich
Vergleicht exakt dieselben Requests zwischen beiden Modi
"""

import os
import sys
import json
from contextlib import contextmanager
from typing import Dict, Any, Tuple, Optional, List
from fastapi.testclient import TestClient
from deepdiff import DeepDiff


def run_legacy(app_import: str, db_path: str, method: str, path: str, json_data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Tuple[int, Dict[str, Any]]:
    """
    Führt einen Request im Legacy-Modus mit isoliertem TestClient aus
    
    Args:
        app_import: Import-Pfad zur App (z.B. "backend.app.main:app")
        db_path: Pfad zur Datenbank
        method: HTTP-Methode (GET, POST, PUT, DELETE)
        path: API-Pfad
        json_data: JSON-Payload (optional)
        headers: HTTP-Headers (optional)
        **kwargs: Weitere Parameter für client.request()
    
    Returns:
        Tuple aus (status_code, response_json)
    """
    # IG_IMPL aus os.environ entfernen (Legacy-Modus)
    old_ig_impl = os.environ.pop("IG_IMPL", None)
    
    try:
        # Frischen App-Import erzwingen
        if "backend.app.main" in sys.modules:
            del sys.modules["backend.app.main"]
        
        # App importieren
        module_name, app_name = app_import.split(":")
        module = __import__(module_name, fromlist=[app_name])
        app = getattr(module, app_name)
        
        # Neuen TestClient erstellen
        client = TestClient(app)
        
        # Default-Headers setzen
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if headers:
            request_headers.update(headers)
        
        # Request-Parameter vorbereiten
        request_kwargs = {
            "method": method,
            "url": path,
            "headers": request_headers,
            **kwargs
        }
        
        if json_data is not None:
            request_kwargs["json"] = json_data
        
        # Request ausführen
        response = client.request(**request_kwargs)
        
        # Response verarbeiten
        try:
            response_json = response.json() if response.content else {}
        except Exception:
            response_json = {}
        
        # Client schließen
        client.close()
        
        return response.status_code, response_json
        
    finally:
        # IG_IMPL wiederherstellen
        if old_ig_impl is not None:
            os.environ["IG_IMPL"] = old_ig_impl


def run_ddd(app_import: str, db_path: str, method: str, path: str, json_data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Tuple[int, Dict[str, Any]]:
    """
    Führt einen Request im DDD-Modus mit isoliertem TestClient aus
    
    Args:
        app_import: Import-Pfad zur App (z.B. "backend.app.main:app")
        db_path: Pfad zur Datenbank
        method: HTTP-Methode (GET, POST, PUT, DELETE)
        path: API-Pfad
        json_data: JSON-Payload (optional)
        headers: HTTP-Headers (optional)
        **kwargs: Weitere Parameter für client.request()
    
    Returns:
        Tuple aus (status_code, response_json)
    """
    # IG_IMPL=ddd setzen
    old_ig_impl = os.environ.pop("IG_IMPL", None)
    os.environ["IG_IMPL"] = "ddd"
    
    try:
        # Frischen App-Import erzwingen
        if "backend.app.main" in sys.modules:
            del sys.modules["backend.app.main"]
        
        # App importieren
        module_name, app_name = app_import.split(":")
        module = __import__(module_name, fromlist=[app_name])
        app = getattr(module, app_name)
        
        # Neuen TestClient erstellen
        client = TestClient(app)
        
        # Default-Headers setzen
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if headers:
            request_headers.update(headers)
        
        # Request-Parameter vorbereiten
        request_kwargs = {
            "method": method,
            "url": path,
            "headers": request_headers,
            **kwargs
        }
        
        if json_data is not None:
            request_kwargs["json"] = json_data
        
        # Request ausführen
        response = client.request(**request_kwargs)
        
        # Response verarbeiten
        try:
            response_json = response.json() if response.content else {}
        except Exception:
            response_json = {}
        
        # Client schließen
        client.close()
        
        return response.status_code, response_json
        
    finally:
        # IG_IMPL wiederherstellen
        if old_ig_impl is not None:
            os.environ["IG_IMPL"] = old_ig_impl
        else:
            os.environ.pop("IG_IMPL", None)


@contextmanager
def toggle_ig_impl(impl: str):
    """Context Manager für IG_IMPL Toggle"""
    old_impl = os.environ.pop("IG_IMPL", None)
    os.environ["IG_IMPL"] = impl
    try:
        yield
    finally:
        if old_impl is not None:
            os.environ["IG_IMPL"] = old_impl
        else:
            os.environ.pop("IG_IMPL", None)


def run_request(
    client: TestClient,
    mode: str,
    method: str,
    path: str,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
    """
    Führt einen Request in einem bestimmten Modus aus
    
    Args:
        client: TestClient
        mode: "legacy" oder "ddd"
        method: HTTP-Methode
        path: API-Pfad
        json_data: JSON-Payload
        headers: HTTP-Headers
        **kwargs: Weitere Parameter
    
    Returns:
        Tuple aus (status_code, response_json, response_headers)
    """
    with toggle_ig_impl(mode):
        # Frischen App-Import erzwingen
        if "backend.app.main" in sys.modules:
            del sys.modules["backend.app.main"]
        
        # Request ausführen
        request_kwargs = {
            "method": method,
            "url": path,
            "headers": headers or {},
            **kwargs
        }
        
        if json_data is not None:
            request_kwargs["json"] = json_data
        
        response = client.request(**request_kwargs)
        
        # Response verarbeiten
        try:
            response_json = response.json() if response.content else {}
        except Exception:
            response_json = {}
        
        # Headers extrahieren
        response_headers = dict(response.headers)
        
        return response.status_code, response_json, response_headers


def compare_responses(
    legacy_response: Tuple[int, Any, Dict[str, str]],
    ddd_response: Tuple[int, Any, Dict[str, str]]
) -> Dict[str, Any]:
    """
    Vergleicht Legacy- und DDD-Responses (robust für Dict und List)
    
    Args:
        legacy_response: (status, body, headers) von Legacy
        ddd_response: (status, body, headers) von DDD
    
    Returns:
        Dict mit Vergleichsergebnissen
    """
    from tests.helpers.compare import compare_responses_robust
    
    # Relevante Felder für Dict-Bodies (nur wenn beide Dicts sind)
    relevant_fields = ['name', 'code', 'description', 'group_permissions', 'ai_functionality', 'typical_tasks', 'is_external', 'is_active']
    
    return compare_responses_robust(legacy_response, ddd_response, relevant_fields)


def format_comparison_result(comparison: Dict[str, Any]) -> str:
    """Formatiert Vergleichsergebnis für bessere Lesbarkeit"""
    if comparison["equal"]:
        return "✅ IDENTISCH"
    
    parts = []
    if not comparison["status_equal"]:
        parts.append(f"Status: {comparison['status_diff']['legacy']}→{comparison['status_diff']['ddd']}")
    
    if not comparison["body_equal"]:
        parts.append("Body unterscheidet sich")
    
    if not comparison["headers_equal"]:
        parts.append("Headers unterscheiden sich")
    
    return f"❌ ABWEICHUNG: {' | '.join(parts)}"
