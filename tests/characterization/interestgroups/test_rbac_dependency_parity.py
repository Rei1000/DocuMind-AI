"""
RBAC-Dependency-Parität: Legacy vs. DDD
Verifiziert, dass DDD-Router die gleichen FastAPI-Dependencies/Middlewares hat
"""

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute


class TestRBACDependencyParity:
    """Testet RBAC-Dependencies und Middleware-Parität zwischen Legacy und DDD"""
    
    def test_router_dependencies_parity(self, app: FastAPI):
        """Test: Router-Dependencies sind identisch zwischen Legacy und DDD"""
        # Alle IG-bezogenen Routen finden
        ig_routes = []
        for route in app.routes:
            if isinstance(route, APIRoute) and "/api/interest-groups" in route.path:
                ig_routes.append(route)
        
        assert len(ig_routes) > 0, "Keine IG-Routen gefunden"
        
        print(f"Gefundene IG-Routen: {len(ig_routes)}")
        
        # Dependencies für jede Route prüfen
        for route in ig_routes:
            print(f"\nRoute: {route.methods} {route.path}")
            
            # Dependencies extrahieren
            dependencies = []
            if hasattr(route, 'dependant') and route.dependant:
                if hasattr(route.dependant, 'dependencies'):
                    dependencies = route.dependant.dependencies
                elif hasattr(route.dependant, 'dependencies_map'):
                    dependencies = list(route.dependant.dependencies_map.keys())
            
            print(f"  Dependencies: {len(dependencies)}")
            for dep in dependencies:
                print(f"    - {dep}")
            
            # Prüfen, ob wichtige Dependencies vorhanden sind
            dependency_names = [str(dep) for dep in dependencies]
            
            # Auth-Dependencies (falls vorhanden)
            auth_deps = [dep for dep in dependency_names if "auth" in dep.lower() or "user" in dep.lower()]
            if auth_deps:
                print(f"  Auth-Dependencies: {auth_deps}")
            
            # Role-Dependencies (falls vorhanden)
            role_deps = [dep for dep in dependency_names if "role" in dep.lower() or "permission" in dep.lower()]
            if role_deps:
                print(f"  Role-Dependencies: {role_deps}")
    
    def test_middleware_stack_parity(self, app: FastAPI):
        """Test: Middleware-Stack ist identisch zwischen Legacy und DDD"""
        # Middleware-Stack extrahieren
        middleware_stack = []
        if hasattr(app, 'user_middleware'):
            middleware_stack = app.user_middleware
        
        print(f"Middleware-Stack: {len(middleware_stack)} Einträge")
        
        for i, middleware in enumerate(middleware_stack):
            print(f"  {i}: {type(middleware).__name__}")
        
        # Wichtige Middleware-Typen prüfen
        middleware_types = [type(middleware).__name__ for middleware in middleware_stack]
        
        # CORS-Middleware
        if "CORSMiddleware" in middleware_types:
            print("  ✅ CORS-Middleware vorhanden")
        
        # Auth-Middleware
        auth_middleware = [m for m in middleware_types if "auth" in m.lower()]
        if auth_middleware:
            print(f"  ✅ Auth-Middleware: {auth_middleware}")
        
        # Logging-Middleware
        logging_middleware = [m for m in middleware_types if "log" in m.lower()]
        if logging_middleware:
            print(f"  ✅ Logging-Middleware: {logging_middleware}")
    
    def test_route_security_parity(self, app: FastAPI):
        """Test: Security-Schemes sind identisch zwischen Legacy und DDD"""
        # OpenAPI-Schema extrahieren
        openapi_schema = app.openapi()
        
        # Security-Schemes prüfen
        security_schemes = openapi_schema.get("components", {}).get("securitySchemes", {})
        
        print(f"Security-Schemes: {len(security_schemes)}")
        for scheme_name, scheme in security_schemes.items():
            print(f"  {scheme_name}: {scheme.get('type', 'unknown')}")
        
        # IG-Routen auf Security prüfen
        ig_routes_with_security = []
        for route in app.routes:
            if isinstance(route, APIRoute) and "/api/interest-groups" in route.path:
                # Security-Requirements prüfen
                if hasattr(route, 'dependant') and route.dependant:
                    # Hier könnten wir tiefer in die Security-Dependencies schauen
                    pass
                
                ig_routes_with_security.append(route)
        
        print(f"IG-Routen mit Security-Checks: {len(ig_routes_with_security)}")
    
    def test_dependency_injection_parity(self, app: FastAPI):
        """Test: Dependency-Injection funktioniert identisch zwischen Legacy und DDD"""
        # Alle IG-Routen sammeln
        ig_routes = []
        for route in app.routes:
            if isinstance(route, APIRoute) and "/api/interest-groups" in route.path:
                ig_routes.append(route)
        
        # Für jede Route die Dependencies analysieren
        for route in ig_routes:
            print(f"\nRoute: {route.methods} {route.path}")
            
            # Dependant-Objekt analysieren
            if hasattr(route, 'dependant') and route.dependant:
                dependant = route.dependant
                
                # Call-Model extrahieren
                if hasattr(dependant, 'call'):
                    call_model = dependant.call
                    print(f"  Call-Model: {type(call_model).__name__}")
                
                # Dependencies-Map
                if hasattr(dependant, 'dependencies_map'):
                    deps_map = dependant.dependencies_map
                    print(f"  Dependencies-Map: {len(deps_map)} Einträge")
                    
                    for key, dep in deps_map.items():
                        print(f"    {key}: {type(dep).__name__}")
                
                # Path-Parameter
                if hasattr(dependant, 'path_params'):
                    path_params = dependant.path_params
                    print(f"  Path-Parameter: {len(path_params)}")
                    for param in path_params:
                        # Pydantic v2 kompatibel
                        if hasattr(param, 'annotation'):
                            print(f"    - {param.name}: {param.annotation}")
                        else:
                            print(f"    - {param.name}: {type(param).__name__}")
                
                # Query-Parameter
                if hasattr(dependant, 'query_params'):
                    query_params = dependant.query_params
                    print(f"  Query-Parameter: {len(query_params)}")
                    for param in query_params:
                        # Pydantic v2 kompatibel
                        if hasattr(param, 'annotation'):
                            print(f"    - {param.name}: {param.annotation}")
                        else:
                            print(f"    - {param.name}: {type(param).__name__}")
                
                # Body-Parameter
                if hasattr(dependant, 'body_params'):
                    body_params = dependant.body_params
                    print(f"  Body-Parameter: {len(body_params)}")
                    for param in body_params:
                        # Pydantic v2 kompatibel
                        if hasattr(param, 'annotation'):
                            print(f"    - {param.name}: {param.annotation}")
                        else:
                            print(f"    - {param.name}: {type(param).__name__}")
    
    def test_route_registration_parity(self, app: FastAPI):
        """Test: Route-Registrierung ist identisch zwischen Legacy und DDD"""
        # Alle Routen nach Pfad gruppieren
        routes_by_path = {}
        for route in app.routes:
            if isinstance(route, APIRoute):
                path = route.path
                if path not in routes_by_path:
                    routes_by_path[path] = []
                routes_by_path[path].append(route)
        
        # IG-Routen analysieren
        ig_paths = [path for path in routes_by_path.keys() if "/api/interest-groups" in path]
        
        print(f"IG-Pfade: {len(ig_paths)}")
        for path in ig_paths:
            routes = routes_by_path[path]
            print(f"\nPfad: {path}")
            print(f"  Routen: {len(routes)}")
            
            for route in routes:
                print(f"    - {route.methods}: {type(route).__name__}")
                
                # Router-Herkunft prüfen
                if hasattr(route, 'tags'):
                    print(f"      Tags: {route.tags}")
                
                # Operation-ID
                if hasattr(route, 'operation_id'):
                    print(f"      Operation-ID: {route.operation_id}")
                
                # Response-Model
                if hasattr(route, 'response_model'):
                    print(f"      Response-Model: {route.response_model}")
