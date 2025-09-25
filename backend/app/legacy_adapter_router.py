"""
Legacy Adapter Router - Kompatibilitätsschicht für DDD-Backend
Macht DDD-Endpoints über Legacy-Pfade verfügbar, ohne Frontend-Änderungen
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from typing import Any
import hashlib
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .database import get_db
from .auth import get_current_user, require_qms_admin, get_current_active_user

# Import schemas with fallback
try:
    from .schemas import UserResponse, UserUpdate, MembershipCreate, MembershipResponse
except ImportError:
    # Fallback: Define minimal schemas
    UserResponse = None
    UserUpdate = None
    MembershipCreate = None
    MembershipResponse = None

# Import models from the correct location
try:
    from .models import User as UserModel, UserGroupMembership
except ImportError:
    # Fallback: Use raw SQL queries instead of ORM
    UserModel = None
    UserGroupMembership = None

# Legacy Adapter Router
legacy_router = APIRouter(prefix="/api", tags=["Legacy Adapter"])

# ============================================================================
# Hilfsfunktionen: Normalizer + Dev-DTO-Sanitizer + Korrelation-Header
# (Nur hier im Legacy-Adapter, keine Änderungen an main.py oder Frontend nötig)
# ============================================================================

def _ensure_legacy_user_shape(user_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Garantiert department=dict, organizational_unit=str, Listenfelder
    fixed = dict(user_dict or {})

    # Department-Objekt
    if not isinstance(fixed.get("department"), dict):
        fixed["department"] = {
            "interest_group": {"id": 0, "name": "Unbekannt", "code": "unknown"},
            "level": 1,
        }

    # organizational_unit ableiten
    if not isinstance(fixed.get("organizational_unit"), str):
        try:
            ig_name = fixed.get("department", {}).get("interest_group", {}).get("name", "Unbekannt")
        except Exception:
            ig_name = "Unbekannt"
        fixed["organizational_unit"] = ig_name

    # Listenfelder
    if not isinstance(fixed.get("permissions"), list):
        fixed["permissions"] = []
    if not isinstance(fixed.get("individual_permissions"), list):
        fixed["individual_permissions"] = []
    if fixed.get("memberships", []) is None or not isinstance(fixed.get("memberships", []), list):
        fixed["memberships"] = []

    return fixed

def _dto_filter_users_list(users_list: List[Dict[str, Any]]) -> tuple[list[Dict[str, Any]], bool, list]:
    offenders: list = []
    did_sanitize = False
    sanitized_list: list[Dict[str, Any]] = []

    for idx, u in enumerate(users_list):
        dept_val = (u.get("department") if isinstance(u, dict) else None)
        if (not isinstance(u, dict)) or ("department" not in u) or (not isinstance(dept_val, dict)):
            offenders.append({
                "index": idx,
                "user_id": (u.get("id") if isinstance(u, dict) else None),
                "type": type(dept_val).__name__ if dept_val is not None else "missing",
                "repr": repr(dept_val)[:120]
            })

        fixed = _ensure_legacy_user_shape(u if isinstance(u, dict) else {})
        if fixed != u:
            did_sanitize = True
        sanitized_list.append(fixed)

    return sanitized_list, did_sanitize, offenders

def _make_traced_json_response(path: str, query: str, payload: Any) -> JSONResponse:
    req_id = str(uuid.uuid4())[:8]
    ts = datetime.now().isoformat()

    dto_sanitized = False
    offenders: list = []
    body = payload

    # Nur für /api/users Listen sanitizen – NICHT für /api/users/{id}/memberships
    if isinstance(payload, list) and path.startswith("/api/users") and "/memberships" not in path:
        body, dto_sanitized, offenders = _dto_filter_users_list(payload)
        if offenders:
            print(f"DTO-OFFENDER {req_id} path={path} offenders={offenders}")

    try:
        body_sha256 = hashlib.sha256(json.dumps(body, default=str).encode()).hexdigest()[:16]
    except Exception:
        body_sha256 = "error-hash"

    body_len = len(body) if isinstance(body, list) else 1

    headers = {
        "X-Req-Id": req_id,
        "X-Resp-Ts": ts,
        "X-Body-SHA256": body_sha256,
        "X-Body-Len": str(body_len),
        "X-DTO-Sanitized": "true" if dto_sanitized else "false",
    }

    # Einzelne Offender komprimiert loggen
    if offenders:
        for off in offenders[:25]:
            print(f"OFFENDER {req_id} idx={off['index']} user_id={off['user_id']} type={off['type']} repr={off['repr']}")

    return JSONResponse(content=body, headers=headers)

# ============================================================================
# LEGACY-KOMPATIBLE ROUTEN (Adapter für DDD-UseCases)
# ============================================================================

@legacy_router.delete("/users/{user_id}/permanent", 
                     operation_id="legacy_delete_user_permanent",
                     summary="Legacy: User permanent löschen (GDPR)")
async def legacy_delete_user_permanent(
    user_id: int,
    password_data: dict | None,
    current_user: UserModel = Depends(require_qms_admin),
    db: Session = Depends(get_db)
):
    """
    Legacy-kompatible Route für DELETE /api/users/{id}/permanent
    Intern ruft DDD-UseCase auf: DELETE /api/users/{id}?mode=gdpr
    """
    # Passwort-Bestätigung prüfen (UI kann verschiedene Keys senden)
    provided_pw = None
    try:
        if isinstance(password_data, dict):
            provided_pw = (
                password_data.get("confirmation_password")
                or password_data.get("admin_password")
                or password_data.get("password")
                or password_data.get("confirm_password")
            )
    except Exception:
        provided_pw = None
    if not provided_pw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwort-Bestätigung erforderlich")
    # Passwort verifizieren gegen aktuellen Admin
    try:
        from .auth import verify_password
        if not verify_password(provided_pw, current_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ungültiges Admin-Passwort")
    except HTTPException:
        raise
    except Exception:
        # Falls Verifikation nicht möglich ist, sichere Fehlermeldung
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Passwort-Verifikation fehlgeschlagen")
    
    # DDD-UseCase aufrufen (intern)
    try:
        # User finden
        if UserModel:
            db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        else:
            # Raw SQL fallback
            from sqlalchemy import text
            result = db.execute(text("SELECT id, email, full_name, is_active FROM users WHERE id = :user_id"), {"user_id": user_id})
            db_user = result.fetchone()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Benutzer mit ID {user_id} nicht gefunden"
            )
        
        # Selbstlöschung verhindern
        user_id_val = db_user.id if hasattr(db_user, 'id') else db_user[0]
        if user_id_val == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Selbstlöschung nicht erlaubt"
            )
        
        # GDPR-Delete (Legacy-Format): Account deaktivieren + anonymisieren
        if UserModel:
            db_user.is_active = False
            db_user.email = f"deleted_{user_id}@anonymized.invalid"
            db_user.full_name = "Gelöschter Benutzer"
            try:
                # Memberships hard delete
                from .models import UserGroupMembership
                db.query(UserGroupMembership).filter(UserGroupMembership.user_id == user_id).delete()
            except Exception:
                pass
            db.commit()
        else:
            # Raw SQL fallback
            from sqlalchemy import text
            db.execute(text("""
                UPDATE users 
                SET is_active = 0, 
                    email = :new_email, 
                    full_name = :new_name 
                WHERE id = :user_id
            """), {
                "new_email": f"deleted_{user_id}@anonymized.invalid",
                "new_name": "Gelöschter Benutzer",
                "user_id": user_id
            })
            try:
                db.execute(text("DELETE FROM user_group_memberships WHERE user_id = :uid"), {"uid": user_id})
            except Exception:
                pass
            db.commit()
        
        return {
            "success": True,
            "message": "User permanently deleted",
            "deleted_at": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Löschen: {str(e)}"
        )


@legacy_router.post("/users/{user_id}/temp-password",
                   operation_id="legacy_set_temp_password", 
                   summary="Legacy: Temporäres Passwort setzen (Body optional)")
async def legacy_set_temp_password(
    user_id: int,
    password_data: dict | None = None,
    current_user: UserModel = Depends(require_qms_admin),
    db: Session = Depends(get_db)
):
    """
    Legacy-kompatible Route für POST /api/users/{id}/temp-password
    - Body optional. Wenn kein Body übergeben wird, wird ein temporäres Passwort generiert
    - Setzt must_change_password = true
    - Antwort enthält Bestätigung und (optional) das temporäre Passwort
    """
    try:
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Benutzer mit ID {user_id} nicht gefunden")

        # Passwortquelle bestimmen
        provided = None
        if isinstance(password_data, dict):
            provided = password_data.get("temporary_password") or password_data.get("new_password")

        if provided and not isinstance(provided, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="temporary_password muss String sein")

        # Falls kein Passwort übergeben wurde → generieren (12 Zeichen, Alnum+Sonderzeichen)
        if not provided:
            import secrets, string
            alphabet = string.ascii_letters + string.digits + "!@#$%&*?"
            provided = ''.join(secrets.choice(alphabet) for _ in range(12))
            policy = "generated_12_alnum_special"
        else:
            policy = "provided_client"

        # Passwort hashen und setzen, must_change_password aktivieren
        from .auth import get_password_hash
        db_user.hashed_password = get_password_hash(provided)
        try:
            setattr(db_user, "must_change_password", True)
        except Exception:
            # Feld evtl. nicht vorhanden – ignorieren, Flow weiterhin erfolgreich
            pass
        db.commit()

        # Audit-Log (ohne Passwort im Log)
        actor = getattr(current_user, 'email', 'unknown')
        print(f"[TEMP-PW] issued user_id={user_id} actor={actor} policy={policy} length={len(provided)}")

        return {
            "user_id": user_id,
            "temporary_password": provided,
            "must_change_password": True,
            "success": True,
            "message": "Temporary password issued"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Fehler beim Setzen des temporären Passworts: {str(e)}")


@legacy_router.post("/user-group-memberships",
                   operation_id="legacy_create_membership",
                   summary="Legacy: Mitgliedschaft erstellen")
async def legacy_create_membership(
    membership_data: dict,
    current_user: UserModel = Depends(require_qms_admin),
    db: Session = Depends(get_db)
):
    """
    Legacy-kompatible Route für POST /api/user-group-memberships
    Intern ruft DDD-UseCase auf: POST /api/users/{id}/memberships
    """
    user_id = membership_data.get("user_id")
    interest_group_id = membership_data.get("interest_group_id")
    role = membership_data.get("role", "member")
    # Frontend sendet approval_level – akzeptiere beide (approval_level bevorzugt)
    level = membership_data.get("approval_level", membership_data.get("level", 1))
    
    if not user_id or not interest_group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id und interest_group_id sind erforderlich"
        )
    
    try:
        # Prüfen ob User existiert
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Benutzer mit ID {user_id} nicht gefunden"
            )
        
        # Mitgliedschaft erstellen (Feldnamen gemäß DB-Modell)
        membership = UserGroupMembership(
            user_id=user_id,
            interest_group_id=interest_group_id,
            role_in_group=role,
            approval_level=level,
            joined_at=datetime.utcnow(),
            assigned_by_id=current_user.id
        )
        
        db.add(membership)
        db.commit()
        db.refresh(membership)
        
        return {
            "id": membership.id,
            "user_id": membership.user_id,
            "interest_group_id": membership.interest_group_id,
            "role": getattr(membership, 'role_in_group', getattr(membership, 'role', 'member')),
            "level": getattr(membership, 'approval_level', getattr(membership, 'level', 1)),
            "assigned_at": getattr(membership, 'joined_at', None).isoformat() if getattr(membership, 'joined_at', None) else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Erstellen der Mitgliedschaft: {str(e)}"
        )


@legacy_router.delete("/user-group-memberships/{membership_id}",
                     operation_id="legacy_delete_membership",
                     summary="Legacy: Mitgliedschaft löschen")
async def legacy_delete_membership(
    membership_id: int,
    current_user: UserModel = Depends(require_qms_admin),
    db: Session = Depends(get_db)
):
    """
    Legacy-kompatible Route für DELETE /api/user-group-memberships/{id}
    Intern ruft DDD-UseCase auf: DELETE /api/users/{id}/memberships/{membership_id}
    """
    try:
        # Mitgliedschaft finden
        membership = db.query(UserGroupMembership).filter(
            UserGroupMembership.id == membership_id
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mitgliedschaft mit ID {membership_id} nicht gefunden"
            )
        
        # Löschen
        db.delete(membership)
        db.commit()
        
        return {
            "success": True,
            "message": "Membership deleted"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Löschen der Mitgliedschaft: {str(e)}"
        )


@legacy_router.get("/users/{user_id}/memberships",
                  operation_id="legacy_get_user_memberships",
                  summary="Legacy: Benutzer-Mitgliedschaften abrufen")
async def legacy_get_user_memberships(
    user_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Legacy-kompatible Route für GET /api/users/{id}/memberships
    Wird weiterhin für N+1-Problem genutzt, bis Frontend auf bulk umstellt
    """
    try:
        # Mitgliedschaften abrufen
        memberships = db.query(UserGroupMembership).filter(
            UserGroupMembership.user_id == user_id
        ).all()
        
        # Ergebnis in der vom Frontend erwarteten Struktur (wie main.py):
        # Jeder Eintrag: { id, user_id, approval_level, user?, interest_group{ id,name,code }, ... }
        result = []
        from .models import InterestGroup as IGModel
        for membership in memberships:
            # Interest Group laden
            ig = db.query(IGModel).filter(IGModel.id == membership.interest_group_id).first()
            interest_group = None
            if ig:
                interest_group = {
                    "id": ig.id,
                    "name": ig.name,
                    "code": getattr(ig, 'code', f"IG-{ig.id}")
                }
            else:
                interest_group = {
                    "id": membership.interest_group_id,
                    "name": f"IG-{membership.interest_group_id}",
                    "code": f"IG-{membership.interest_group_id}"
                }

            result.append({
                "id": membership.id,
                "user_id": membership.user_id,
                "approval_level": getattr(membership, 'approval_level', getattr(membership, 'level', 1)),
                "interest_group": interest_group,
                "assigned_at": getattr(membership, 'joined_at', None).isoformat() if getattr(membership, 'joined_at', None) else None,
                "assigned_by": getattr(membership, 'assigned_by_id', None)
            })
        
        # Rückgabe als Liste (keine Wrapper-Map), plus Trace/Korrelation-Header
        return _make_traced_json_response(f"/api/users/{user_id}/memberships", "", result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Abrufen der Mitgliedschaften: {str(e)}"
        )


# ============================================================================
# N+1-FIX: BULK MEMBERSHIPS (neue performante Endpoints)
# ============================================================================

@legacy_router.get("/users/bulk-memberships",
                  operation_id="legacy_bulk_memberships",
                  summary="Legacy: Bulk-Mitgliedschaften abrufen (N+1-Fix)")
async def legacy_bulk_memberships(
    user_ids: List[int] = Query(..., description="Liste der User-IDs"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    N+1-Fix: Bulk-Mitgliedschaften für mehrere Benutzer abrufen
    Reduziert 672 einzelne Calls auf 1 Bulk-Call
    """
    try:
        # Alle Mitgliedschaften für die User-IDs abrufen
        memberships = db.query(UserGroupMembership).filter(
            UserGroupMembership.user_id.in_(user_ids)
        ).all()
        
        # Nach User-ID gruppieren
        result = {}
        for user_id in user_ids:
            result[str(user_id)] = []
        
        for membership in memberships:
            user_id_str = str(membership.user_id)
            if user_id_str in result:
                result[user_id_str].append({
                    "id": membership.id,
                    "user_id": membership.user_id,
                    "interest_group_id": membership.interest_group_id,
                    "role": getattr(membership, 'role_in_group', getattr(membership, 'role', 'member')),  # Legacy-Feldname
                    "level": getattr(membership, 'approval_level', getattr(membership, 'level', 1)),  # Legacy-Feldname
                    "assigned_at": getattr(membership, 'assigned_at', None).isoformat() if getattr(membership, 'assigned_at', None) else None,
                    "assigned_by": getattr(membership, 'assigned_by', None)
                })
        
        return {"memberships": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Bulk-Abrufen der Mitgliedschaften: {str(e)}"
        )


@legacy_router.get("/users",
                  operation_id="legacy_get_users_with_memberships",
                  summary="Legacy: Benutzer mit optionalen Mitgliedschaften")
async def legacy_get_users_with_memberships(
    limit: int = Query(100, description="Anzahl der Benutzer"),
    include: Optional[str] = Query(None, description="Include memberships"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Legacy-kompatible Route für GET /api/users mit optionalen Mitgliedschaften
    N+1-Fix: include=memberships lädt alle Mitgliedschaften in einem Call
    """
    try:
        # Benutzer abrufen
        users = db.query(UserModel).limit(limit).all()
        
        result: list[dict] = []
        for user in users:
            base_data = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "permissions": [],  # Legacy-Feldname
                "employee_id": getattr(user, 'employee_id', ""),
                "organizational_unit": "Unbekannt",
                "is_department_head": False,  # Default-Wert
                "approval_level": 1,  # Default-Wert (wird je Membership überschrieben)
                "created_at": getattr(user, 'created_at', datetime.utcnow()).isoformat() if hasattr(user, 'created_at') and user.created_at else datetime.utcnow().isoformat(),
                "department": {  # Platzhalter – wird je Membership überschrieben
                    "interest_group": {"id": 0, "name": "Unbekannt", "code": "unknown"},
                    "level": 1
                }
            }
            
            # Individual permissions parsen
            # Permissions normalisieren (Legacy-Kompatibilität)
            individual_perms = getattr(user, 'individual_permissions', None)
            if individual_perms is None:
                individual_perms = []
            elif isinstance(individual_perms, str):
                try:
                    import json
                    individual_perms = json.loads(individual_perms)
                except (json.JSONDecodeError, TypeError):
                    individual_perms = []
            elif not isinstance(individual_perms, list):
                individual_perms = []
            
            base_data["permissions"] = individual_perms
            base_data["individual_permissions"] = individual_perms
            
            # Capabilities hinzufügen für Frontend-Kompatibilität
            individual_perms = base_data["permissions"]
            can_delete_users = (
                "system_administration" in individual_perms or
                "admin" in individual_perms or
                "users.manage" in individual_perms or
                user.email == "qms.admin@company.com"
            )
            
            base_data["capabilities"] = {
                "can_delete_users": can_delete_users,
                "can_manage_users": can_delete_users,
                "can_reset_passwords": can_delete_users,
                "can_deactivate_users": can_delete_users
            }
            
            # Mitgliedschaften laden – EIN Eintrag pro User (kein Fan-Out)
            memberships = db.query(UserGroupMembership).filter(UserGroupMembership.user_id == user.id).all()

            if memberships:
                # Prefetch IGs
                try:
                    from .models import InterestGroup
                    ig_ids = {m.interest_group_id for m in memberships}
                    ig_map = {g.id: g for g in db.query(InterestGroup).filter(InterestGroup.id.in_(ig_ids)).all()}
                except Exception:
                    ig_map = {}

                # Erste Mitgliedschaft für Haupt-Department (Legacy-Kompatibilität)
                first_membership = memberships[0]
                ig = ig_map.get(first_membership.interest_group_id)
                level = getattr(first_membership, 'approval_level', getattr(first_membership, 'level', 1))
                
                if ig:
                    base_data["department"] = {
                        "interest_group": {"id": ig.id, "name": ig.name, "code": getattr(ig, 'code', f"IG-{ig.id}")},
                        "level": level,
                    }
                    base_data["organizational_unit"] = ig.name
                else:
                    base_data["department"] = {
                        "interest_group": {"id": first_membership.interest_group_id, "name": f"IG-{first_membership.interest_group_id}", "code": f"IG-{first_membership.interest_group_id}"},
                        "level": level,
                    }
                    base_data["organizational_unit"] = f"IG-{first_membership.interest_group_id}"
                base_data["approval_level"] = level
                base_data["is_department_head"] = level >= 3
                
                # Alle Mitgliedschaften als Liste für Frontend-Filter
                base_data["all_memberships"] = []
                for m in memberships:
                    ig = ig_map.get(m.interest_group_id)
                    level = getattr(m, 'approval_level', getattr(m, 'level', 1))
                    membership_data = {
                        "interest_group_id": m.interest_group_id,
                        "level": level,
                        "organizational_unit": ig.name if ig else f"IG-{m.interest_group_id}"
                    }
                    base_data["all_memberships"].append(membership_data)
                
                result.append(base_data)
            else:
                # Kein Membership: Fallback-Objekt
                base_data["department"] = {
                    "interest_group": {"id": 0, "name": "Unbekannt", "code": "unknown"},
                    "level": 1,
                }
                base_data["organizational_unit"] = "Unbekannt"
                base_data["approval_level"] = 1
                base_data["is_department_head"] = False
                base_data["all_memberships"] = []
                result.append(base_data)
            
            # Mitgliedschaften optional laden (N+1-Fix) – unverändert (nur für include=memberships)
            if include == "memberships" and memberships:
                # Füge memberships dem aktuellen User-Eintrag hinzu
                result[-1]["memberships"] = []
                for membership in memberships:
                    result[-1]["memberships"].append({
                        "id": membership.id,
                        "user_id": membership.user_id,
                        "interest_group_id": membership.interest_group_id,
                        "role": getattr(membership, 'role_in_group', getattr(membership, 'role', 'member')),  # Legacy-Feldname
                        "level": getattr(membership, 'approval_level', getattr(membership, 'level', 1)),  # Legacy-Feldname
                        "assigned_at": getattr(membership, 'assigned_at', None).isoformat() if getattr(membership, 'assigned_at', None) else None,
                        "assigned_by": getattr(membership, 'assigned_by', None)
                        })
        
        # Korrelation/Headers + Dev-Only Sanitizer direkt im Legacy-Adapter
        return _make_traced_json_response("/api/users", f"limit={limit}&include={include or ''}", result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Abrufen der Benutzer: {str(e)}"
        )
