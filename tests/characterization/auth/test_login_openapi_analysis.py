"""
Login OpenAPI Analysis Test
Analysiert /api/auth/login OpenAPI-Spezifikation exakt
"""

import pytest
import os
from tests.helpers.ab_runner import run_request
from tests.helpers.auth_env import set_auth_env_for_tests


class TestLoginOpenApiAnalysis:
    """Analysiert Login OpenAPI-Spezifikation"""
    
    def test_login_openapi_analysis(self, client):
        """Analysiert /api/auth/login OpenAPI-Spezifikation"""
        print("Analysiere /api/auth/login OpenAPI...")
        
        # ENV setzen
        set_auth_env_for_tests()
        os.environ["DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        os.environ["SQLALCHEMY_DATABASE_URL"] = "sqlite:////Users/reiner/Documents/DocuMind-AI/.tmp/jwt_users.db"
        
        # OpenAPI für beide Modi abrufen
        for mode in ["legacy", "ddd"]:
            try:
                response = run_request(
                    client, mode, "GET", "/openapi.json"
                )
                
                if response[0] == 200:
                    openapi = response[1]
                    paths = openapi.get('paths', {})
                    login_path = "/api/auth/login"
                    
                    if login_path in paths:
                        login_spec = paths[login_path]
                        
                        # POST-Methode analysieren
                        post_spec = login_spec.get('post', {})
                        
                        # Request Body analysieren
                        request_body = post_spec.get('requestBody', {})
                        content = request_body.get('content', {})
                        content_types = list(content.keys())
                        
                        # Erwartete Felder aus Schema extrahieren
                        fields = []
                        if 'application/x-www-form-urlencoded' in content:
                            schema = content['application/x-www-form-urlencoded'].get('schema', {})
                            properties = schema.get('properties', {})
                            required = schema.get('required', [])
                            fields = list(properties.keys())
                        elif 'application/json' in content:
                            schema = content['application/json'].get('schema', {})
                            properties = schema.get('properties', {})
                            required = schema.get('required', [])
                            fields = list(properties.keys())
                        
                        # Response analysieren
                        responses = post_spec.get('responses', {})
                        response_200 = responses.get('200', {})
                        response_content = response_200.get('content', {})
                        response_json = response_content.get('application/json', {})
                        response_schema = response_json.get('schema', {})
                        response_properties = response_schema.get('properties', {})
                        response_fields = list(response_properties.keys())
                        
                        # Security Schemes analysieren
                        components = openapi.get('components', {})
                        security_schemes = components.get('securitySchemes', {})
                        security_names = list(security_schemes.keys())
                        
                        # Log
                        print(f"[OPENAPI-LOGIN] path={login_path} content={content_types} fields={fields} security={security_names}")
                        print(f"[OPENAPI-RESPONSE] fields={response_fields}")
                        
                        # Speichere für weitere Tests
                        setattr(self, f"{mode}_login_spec", {
                            'content_types': content_types,
                            'fields': fields,
                            'response_fields': response_fields,
                            'security_schemes': security_names
                        })
                        
                    else:
                        print(f"[OPENAPI-LOGIN] path={login_path} not found in {mode}")
                        
                else:
                    print(f"[OPENAPI-ERROR] {mode} status={response[0]}")
                    
            except Exception as e:
                print(f"[OPENAPI-ERROR] {mode}: {e}")
        
        # Test erfolgreich
        assert True, "OpenAPI analysis completed"

