"""
Application Service für Interest Groups
Orchestriert Repository-Operationen ohne DB- oder Framework-Imports
"""

from typing import List, Optional
from backend.app.schemas import InterestGroupCreate, InterestGroupUpdate, InterestGroup
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class InterestGroupService:
    """
    Application Service für Interest Groups
    Reine Orchestrierung; keine DB- oder Framework-Imports
    """
    
    def __init__(self, repository):
        """Initialisiere Service mit Repository (Dependency Injection)"""
        self.repository = repository
    
    def list_groups(self, db: Session) -> List[InterestGroup]:
        """Liste aller aktiven Interest Groups"""
        return self.repository.list(db)
    
    def get_group(self, db: Session, group_id: int) -> Optional[InterestGroup]:
        """Hole einzelne Interest Group nach ID"""
        return self.repository.get(db, group_id)
    
    def get_group_by_code(self, db: Session, code: str) -> Optional[InterestGroup]:
        """Hole Interest Group nach Code (für Duplicate-Check)"""
        return self.repository.get_by_code(db, code)
    
    def create_group(self, db: Session, group_data: InterestGroupCreate) -> InterestGroup:
        """Erstelle neue Interest Group - atomare Transaktion mit Legacy-Compat"""
        
        # Defensive Defaults für optionale Felder
        if group_data.group_permissions is None or group_data.group_permissions == "":
            group_data.group_permissions = []
        
        # 1. Vor dem Insert: Duplicate-Check für Legacy-Compat
        if group_data.code:
            try:
                existing_group = self.repository.get_by_code(db, group_data.code)
                if existing_group:
                    return existing_group
            except Exception:
                # Ignoriere Fehler beim Lookup, versuche Insert
                pass
        
        # 2. Atomare Transaktion: Insert mit flush/refresh
        try:
            # Beginne Transaktion (Repository macht bereits commit/refresh)
            created_group = self.repository.create(db, group_data)
            
            # Garantiere echte ID > 0
            if not created_group or created_group.id <= 0:
                raise ValueError("Repository returned group without valid ID")
            
            return created_group
            
        except IntegrityError as e:
            # 3. IntegrityError: Duplicate-Handling für Legacy-Compat
            db.rollback()  # Rollback der fehlgeschlagenen Transaktion
            
            # Versuche bestehenden Datensatz zu finden
            if group_data.code:
                try:
                    existing_group = self.repository.get_by_code(db, group_data.code)
                    if existing_group:
                        return existing_group
                except Exception:
                    pass
            
            # Wenn kein bestehender Datensatz gefunden, als HTTP 400 weiterreichen
            raise ValueError(f"Duplicate constraint violation: {str(e)}")
            
        except Exception as e:
            # 4. Andere Fehler: Rollback und weiterreichen
            db.rollback()
            raise e
    
    def update_group(self, db: Session, group_id: int, group_data: InterestGroupUpdate) -> Optional[InterestGroup]:
        """Aktualisiere Interest Group"""
        return self.repository.update(db, group_id, group_data)
    
    def delete_group(self, db: Session, group_id: int) -> bool:
        """Lösche Interest Group (Soft-Delete)"""
        return self.repository.delete(db, group_id)
