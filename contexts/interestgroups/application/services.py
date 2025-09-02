"""
Application Service für Interest Groups
Orchestriert Repository-Operationen ohne DB- oder Framework-Imports
"""

from typing import List, Optional
from backend.app.schemas import InterestGroupCreate, InterestGroupUpdate, InterestGroup
from sqlalchemy.orm import Session


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
    
    def create_group(self, db: Session, group_data: InterestGroupCreate) -> InterestGroup:
        """Erstelle neue Interest Group"""
        return self.repository.create(db, group_data)
    
    def update_group(self, db: Session, group_id: int, group_data: InterestGroupUpdate) -> Optional[InterestGroup]:
        """Aktualisiere Interest Group"""
        return self.repository.update(db, group_id, group_data)
    
    def delete_group(self, db: Session, group_id: int) -> bool:
        """Lösche Interest Group (Soft-Delete)"""
        return self.repository.delete(db, group_id)
