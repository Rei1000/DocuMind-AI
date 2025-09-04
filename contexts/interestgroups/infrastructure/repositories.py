"""
Legacy Repository Adapter für Interest Groups
Verwendet bestehende backend.app.database und backend.app.models unverändert
"""

from typing import List, Optional, Dict, Any
from backend.app.database import get_db
from backend.app.models import InterestGroup
from backend.app.schemas import InterestGroupCreate, InterestGroupUpdate
from sqlalchemy.orm import Session
import json


class InterestGroupRepositoryLegacy:
    """
    Legacy Repository Adapter für Interest Groups
    Implementiert CRUD-Operationen exakt wie im bestehenden Code
    """
    
    def list(self, db: Session) -> List[InterestGroup]:
        """Liste aller aktiven Interest Groups (wie im bestehenden Code)"""
        return db.query(InterestGroup).filter(InterestGroup.is_active == True).all()
    
    def get(self, db: Session, group_id: int) -> Optional[InterestGroup]:
        """Hole einzelne Interest Group nach ID (wie im bestehenden Code)"""
        return db.query(InterestGroup).filter(
            InterestGroup.id == group_id,
            InterestGroup.is_active == True
        ).first()
    
    def get_by_code(self, db: Session, code: str) -> Optional[InterestGroup]:
        """Hole Interest Group nach Code (für Duplicate-Check)"""
        return db.query(InterestGroup).filter(
            InterestGroup.code == code,
            InterestGroup.is_active == True
        ).first()
    
    def create(self, db: Session, group_data: InterestGroupCreate) -> InterestGroup:
        """Erstelle neue Interest Group (wie im bestehenden Code)"""
        # Prüfe Duplikate (wie im bestehenden Code)
        existing_name = db.query(InterestGroup).filter(
            InterestGroup.name == group_data.name,
            InterestGroup.is_active == True
        ).first()
        if existing_name:
            raise ValueError(f"Interest group with name '{group_data.name}' already exists")
        
        existing_code = db.query(InterestGroup).filter(
            InterestGroup.code == group_data.code,
            InterestGroup.is_active == True
        ).first()
        if existing_code:
            raise ValueError(f"Interest group with code '{group_data.code}' already exists")
        
        # Serialisiere group_permissions zu JSON-String vor DB-Insert
        permissions_value = group_data.group_permissions
        if isinstance(permissions_value, (list, dict)):
            permissions_value = json.dumps(permissions_value, ensure_ascii=False)
        
        # Erstelle neue Gruppe (wie im bestehenden Code)
        db_group = InterestGroup(
            name=group_data.name,
            code=group_data.code,
            description=group_data.description,
            group_permissions=permissions_value,
            ai_functionality=group_data.ai_functionality,
            typical_tasks=group_data.typical_tasks,
            is_external=group_data.is_external,
            is_active=group_data.is_active
        )
        
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return db_group
    
    def update(self, db: Session, group_id: int, group_data: InterestGroupUpdate) -> Optional[InterestGroup]:
        """Aktualisiere Interest Group (wie im bestehenden Code)"""
        db_group = self.get(db, group_id)
        if not db_group:
            return None
        
        # Prüfe Duplikate bei Updates (wie im bestehenden Code)
        if hasattr(group_data, 'name') and group_data.name is not None:
            existing_name = db.query(InterestGroup).filter(
                InterestGroup.name == group_data.name,
                InterestGroup.id != group_id,
                InterestGroup.is_active == True
            ).first()
            if existing_name:
                raise ValueError(f"Interest group with name '{group_data.name}' already exists")
        
        if hasattr(group_data, 'code') and group_data.code is not None:
            existing_code = db.query(InterestGroup).filter(
                InterestGroup.code == group_data.code,
                InterestGroup.id != group_id,
                InterestGroup.is_active == True
            ).first()
            if existing_code:
                raise ValueError(f"Interest group with code '{group_data.code}' already exists")
        
        # Update Felder (wie im bestehenden Code)
        update_data = group_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            # Serialisiere group_permissions zu JSON-String vor DB-Update
            if field == 'group_permissions' and isinstance(value, (list, dict)):
                value = json.dumps(value, ensure_ascii=False)
            setattr(db_group, field, value)
        
        db.commit()
        db.refresh(db_group)
        return db_group
    
    def delete(self, db: Session, group_id: int) -> bool:
        """Lösche Interest Group (Soft-Delete, wie im bestehenden Code)"""
        # Für DELETE: auch inaktive Gruppen finden können (nicht nur aktive)
        db_group = db.query(InterestGroup).filter(InterestGroup.id == group_id).first()
        if not db_group:
            return False
        
        # Soft-Delete (wie im bestehenden Code)
        db_group.is_active = False
        db.commit()
        return True
