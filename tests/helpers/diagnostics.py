"""
Test-Diagnostik-Helper
Instrumentiert FastAPI-Apps zur Laufzeit für Exception-Diagnose
"""

import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


def inject_exception_logger(app):
    """
    Registriert Exception-Handler in FastAPI-App für Diagnose
    
    Args:
        app: FastAPI-App-Instanz
    """
    
    @app.exception_handler(Exception)
    async def exception_logger(request: Request, exc: Exception):
        """Loggt alle Exceptions mit Details"""
        
        # Exception-Details extrahieren
        exc_type = type(exc).__name__
        exc_msg = str(exc)
        exc_repr = repr(exc)
        
        # Log-Zeile 1: Exception-Typ und Message
        print(f"[EXC] type={exc_type} msg={exc_msg}")
        
        # Log-Zeile 2: Stacktrace (erste 3 Frames)
        tb_lines = traceback.format_exc().split('\n')
        trace_info = ' | '.join(tb_lines[:6])  # Erste 3 Frames (je 2 Zeilen)
        print(f"[TRACE] {trace_info}")
        
        # Response mit sichtbarem Detail für Tests
        return JSONResponse(
            status_code=500,
            content={"detail": f"EXC::{exc_type}::{exc_msg}"}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_logger(request: Request, exc: RequestValidationError):
        """Spezielle Behandlung für Validation-Fehler"""
        
        exc_type = "RequestValidationError"
        exc_msg = str(exc)
        
        print(f"[EXC] type={exc_type} msg={exc_msg}")
        
        # Validation-Fehler haben oft detaillierte Errors
        if hasattr(exc, 'errors') and exc.errors:
            for error in exc.errors[:2]:  # Erste 2 Fehler
                print(f"[VALIDATION] field={error.get('loc', [])} msg={error.get('msg', '')}")
        
        return JSONResponse(
            status_code=422,
            content={"detail": f"EXC::{exc_type}::{exc_msg}"}
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_logger(request: Request, exc: HTTPException):
        """Spezielle Behandlung für HTTP-Exceptions"""
        
        exc_type = "HTTPException"
        exc_msg = str(exc.detail)
        
        print(f"[EXC] type={exc_type} msg={exc_msg} status={exc.status_code}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": f"EXC::{exc_type}::{exc_msg}"}
        )
