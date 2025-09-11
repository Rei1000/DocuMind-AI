"""
Robuste Vergleichsfunktionen für Test-Responses
Kann sowohl Dict- als auch List-Responses korrekt vergleichen
"""

import json
from typing import Any, Dict, List, Tuple, Union, Optional


def canonicalize(obj: Any) -> Any:
    """
    Macht ein Objekt vergleichbar durch Normalisierung
    
    Args:
        obj: Zu normalisierendes Objekt (Dict, Liste, primitiv)
    
    Returns:
        Normalisiertes Objekt für Vergleich
    """
    if isinstance(obj, dict):
        # Dict: Keys sortieren, Werte rekursiv canonicalize
        return {k: canonicalize(v) for k, v in sorted(obj.items())}
    
    elif isinstance(obj, list):
        # Liste: Elemente canonicalize, dann sortierbar machen
        canonical_elements = [canonicalize(item) for item in obj]
        # JSON dumps für konsistente Sortierung
        return sorted([json.dumps(item, sort_keys=True) for item in canonical_elements])
    
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        # Primitive Typen: unverändert
        return obj
    
    else:
        # Andere Typen: JSON serialisieren
        try:
            return json.dumps(obj, sort_keys=True)
        except (TypeError, ValueError):
            return str(obj)


def equal(a: Any, b: Any) -> bool:
    """
    Vergleicht zwei Objekte nach Canonicalisierung
    
    Args:
        a: Erstes Objekt
        b: Zweites Objekt
    
    Returns:
        True wenn identisch nach Canonicalisierung
    """
    return canonicalize(a) == canonicalize(b)


def extract_status_and_body(response: Tuple[int, Any, Dict[str, str]]) -> Tuple[int, Any]:
    """
    Extrahiert Status und Body aus Test-Response
    
    Args:
        response: (status_code, body, headers) Tuple
    
    Returns:
        (status_code, parsed_body) Tuple
    """
    if len(response) == 3:
        status_code, body, _ = response
    elif len(response) == 2:
        status_code, body = response
    else:
        raise ValueError(f"Unerwartetes Response-Format: {len(response)} Werte")
    
    # Body bereits geparst (von TestClient)
    if isinstance(body, (dict, list)):
        return status_code, body
    
    # Fallback: String versuchen zu parsen
    if isinstance(body, str):
        try:
            return status_code, json.loads(body)
        except (json.JSONDecodeError, ValueError):
            return status_code, body
    
    return status_code, body


def compare_responses_robust(
    legacy_response: Tuple[int, Any, Dict[str, str]],
    ddd_response: Tuple[int, Any, Dict[str, str]],
    relevant_fields: List[str] = None
) -> Dict[str, Any]:
    """
    Robuster Response-Vergleich für Dict- und List-Bodies
    
    Args:
        legacy_response: (status, body, headers) von Legacy
        ddd_response: (status, body, headers) von DDD
        relevant_fields: Optional - nur für Dict-Bodies, relevante Felder
    
    Returns:
        Dict mit Vergleichsergebnissen
    """
    # Extrahiere Status und Body
    legacy_status, legacy_body = extract_status_and_body(legacy_response)
    ddd_status, ddd_body = extract_status_and_body(ddd_response)
    
    # Headers extrahieren (falls vorhanden)
    legacy_headers = legacy_response[2] if len(legacy_response) > 2 else {}
    ddd_headers = ddd_response[2] if len(ddd_response) > 2 else {}
    
    # Status-Vergleich
    status_equal = legacy_status == ddd_status
    
    # Body-Vergleich: Unterscheidung zwischen Dict und Liste
    if isinstance(legacy_body, dict) and isinstance(ddd_body, dict):
        # Dict-Bodies: Feld-Subset-Vergleich möglich
        if relevant_fields:
            body_equal = True
            body_diff = {}
            
            for field in relevant_fields:
                legacy_value = legacy_body.get(field)
                ddd_value = ddd_body.get(field)
                
                if not canonicalize(legacy_value) == canonicalize(ddd_value):
                    body_equal = False
                    body_diff[field] = {
                        "legacy": legacy_value,
                        "ddd": ddd_value
                    }
        else:
            # Vollständiger Dict-Vergleich
            body_equal = canonicalize(legacy_body) == canonicalize(ddd_body)
            body_diff = {} if body_equal else {"full_diff": "Bodies unterscheiden sich"}
    
    elif isinstance(legacy_body, list) and isinstance(ddd_body, list):
        # Listen: Vollständiger Vergleich
        body_equal = canonicalize(legacy_body) == canonicalize(ddd_body)
        body_diff = {} if body_equal else {"list_diff": "Listen unterscheiden sich"}
    
    else:
        # Gemischte Typen oder andere: Direkter Vergleich
        body_equal = canonicalize(legacy_body) == canonicalize(ddd_body)
        body_diff = {} if body_equal else {"type_diff": f"Unterschiedliche Typen: {type(legacy_body)} vs {type(ddd_body)}"}
    
    # Header-Vergleich
    header_diffs = {}
    for key in set(legacy_headers.keys()) | set(ddd_headers.keys()):
        legacy_value = legacy_headers.get(key)
        ddd_value = ddd_headers.get(key)
        
        if legacy_value != ddd_value:
            header_diffs[key] = {
                "legacy": legacy_value,
                "ddd": ddd_value
            }
    
    headers_equal = len(header_diffs) == 0
    
    # Gesamt-Ergebnis
    result_equal = status_equal and body_equal and headers_equal
    
    return {
        "equal": result_equal,
        "status_equal": status_equal,
        "body_equal": body_equal,
        "headers_equal": headers_equal,
        "status_diff": {
            "legacy": legacy_status,
            "ddd": ddd_status
        } if not status_equal else None,
        "body_diff": body_diff if not body_equal else None,
        "header_diffs": header_diffs
    }


def compare_status_legacy_vs_ddd(
    legacy_resp: Tuple[int, Any], 
    ddd_resp: Tuple[int, Any], 
    path: str = "unknown",
    method: str = "unknown",
    *, 
    allow_intentional: Optional[List[Tuple[str, str, int, int]]] = None
) -> Dict[str, Any]:
    """
    Vergleicht Status-Codes zwischen Legacy und DDD mit Toleranz für intentional non-parity.
    
    Args:
        legacy_resp: (status_code, response_body) für Legacy
        ddd_resp: (status_code, response_body) für DDD
        path: API-Pfad für Vergleich
        method: HTTP-Methode für Vergleich
        allow_intentional: Liste von (path, method, legacy_code, ddd_code) für erlaubte Abweichungen
        
    Returns:
        Dict mit Vergleichsergebnissen
    """
    legacy_status, legacy_body = legacy_resp
    ddd_status, ddd_body = ddd_resp
    
    # Prüfe auf intentional non-parity
    allow_intentional = allow_intentional or []
    
    for allowed_path, allowed_method, legacy_code, ddd_code in allow_intentional:
        if (path == allowed_path and method == allowed_method and 
            legacy_status == legacy_code and ddd_status == ddd_code):
            print(f"[STATUS-NP] method={method} path={path} legacy={legacy_code} ddd={ddd_code}")
            return {
                "equal": True,  # Als "equal" behandelt, da intentional
                "status_equal": True,
                "intentional_non_parity": True,
                "legacy_status": legacy_status,
                "ddd_status": ddd_status,
                "path": path,
                "method": method
            }
    
    # Normale Paritäts-Prüfung
    status_equal = legacy_status == ddd_status
    
    if not status_equal:
        print(f"[STATUS-PARITY] legacy={legacy_status} ddd={ddd_status} path={path}")
    
    return {
        "equal": status_equal,
        "status_equal": status_equal,
        "intentional_non_parity": False,
        "legacy_status": legacy_status,
        "ddd_status": ddd_status,
        "path": path,
        "method": method
    }


def get_intentional_non_parity_list() -> List[Tuple[str, str, int, int]]:
    """
    Gibt die Liste der bekannten intentional non-parity Fälle zurück.
    
    Returns:
        Liste von (path, method, legacy_code, ddd_code)
    """
    return [
        # POST /api/interest-groups duplicate handling
        ("/api/interest-groups", "POST", 200, 409),
        # PUT /api/interest-groups duplicate constraints  
        ("/api/interest-groups/{id}", "PUT", 422, 409),
        # Auth guard differences (Legacy vs DDD enforcement)
        ("/api/auth/me", "GET", 200, 401),
        ("/api/users/me", "GET", 200, 401),
        # Schema validation differences
        ("/api/interest-groups", "POST", 422, 409),
        # Permission handling differences
        ("/api/users", "GET", 200, 403),
        ("/api/users", "POST", 200, 403),
        ("/api/users/{id}", "PUT", 200, 403),
        ("/api/users/{id}", "DELETE", 200, 403),
        # Content-Type validation differences
        ("/api/interest-groups", "POST", 200, 422),
        # Edge case handling
        ("/api/interest-groups", "POST", 200, 409),
    ]
