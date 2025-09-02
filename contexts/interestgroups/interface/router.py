"""
Interface Router für Interest Groups
Implementiert dieselben Endpunkte wie im bestehenden Code
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas import InterestGroup, InterestGroupCreate, InterestGroupUpdate
from contexts.interestgroups.application.services import InterestGroupService
from contexts.interestgroups.infrastructure.repositories import InterestGroupRepositoryLegacy
from typing import List

# Router mit gleichem Prefix wie im bestehenden Code
router = APIRouter(prefix="/api/interest-groups", tags=["interest-groups"])

# Dependency Injection
def get_interest_group_service():
    """Dependency für Interest Group Service"""
    repository = InterestGroupRepositoryLegacy()
    return InterestGroupService(repository)


@router.get("/", response_model=List[InterestGroup])
def get_interest_groups(
    db: Session = Depends(get_db),
    service: InterestGroupService = Depends(get_interest_group_service)
):
    """GET /api/interest-groups - Liste aller aktiven Interest Groups"""
    try:
        groups = service.list_groups(db)
        return groups
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{group_id}", response_model=InterestGroup)
def get_interest_group(
    group_id: int,
    db: Session = Depends(get_db),
    service: InterestGroupService = Depends(get_interest_group_service)
):
    """GET /api/interest-groups/{group_id} - Einzelne Interest Group"""
    try:
        group = service.get_group(db, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interest group not found"
            )
        return group
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", response_model=InterestGroup, status_code=status.HTTP_200_OK)
def create_interest_group(
    group: InterestGroupCreate,
    db: Session = Depends(get_db),
    service: InterestGroupService = Depends(get_interest_group_service)
):
    """POST /api/interest-groups - Neue Interest Group erstellen"""
    try:
        created_group = service.create_group(db, group)
        return created_group
    except ValueError as e:
        # Duplikat-Fehler (wie im bestehenden Code)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{group_id}", response_model=InterestGroup)
def update_interest_group(
    group_id: int,
    group: InterestGroupUpdate,
    db: Session = Depends(get_db),
    service: InterestGroupService = Depends(get_interest_group_service)
):
    """PUT /api/interest-groups/{group_id} - Interest Group aktualisieren"""
    try:
        updated_group = service.update_group(db, group_id, group)
        if not updated_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interest group not found"
            )
        return updated_group
    except ValueError as e:
        # Duplikat-Fehler (wie im bestehenden Code)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{group_id}", status_code=status.HTTP_200_OK)
def delete_interest_group(
    group_id: int,
    db: Session = Depends(get_db),
    service: InterestGroupService = Depends(get_interest_group_service)
):
    """DELETE /api/interest-groups/{group_id} - Interest Group löschen (Soft-Delete)"""
    try:
        success = service.delete_group(db, group_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interest group not found"
            )
        return {"message": "Interest group deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
