"""
Test für Interest Groups Unique Constraints
"""

import pytest
import sys
from pathlib import Path

# Import-Pfad für Backend-Database
backend_path = Path("/Users/reiner/Documents/DocuMind-AI/backend")
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from backend.app.database import engine
from sqlalchemy import text

class TestInterestGroupsUniqueConstraints:
    """Test für InterestGroup Unique Constraints"""
    
    def test_interest_groups_unique_constraints(self):
        """Test: Unique-Constraints sind korrekt definiert"""
        with engine.connect() as connection:
            # Prüfe Unique-Constraints
            result = connection.execute(text("PRAGMA index_list(interest_groups)"))
            indexes = result.fetchall()
            
            # Finde Unique-Indizes
            unique_indexes = []
            for idx in indexes:
                if idx[2] == 1:  # unique = 1
                    unique_indexes.append(idx[1])
            
            # name und code sollten unique sein
            # Prüfe sowohl die ursprünglichen als auch die neuen Index-Namen
            name_unique = ('ix_interest_groups_name' in unique_indexes or 
                          'ix_interest_groups_name_unique' in unique_indexes)
            code_unique = ('ix_interest_groups_code' in unique_indexes or 
                          'ix_interest_groups_code_unique' in unique_indexes)
            
            assert name_unique, "Name-Index ist nicht unique (erwartet: ix_interest_groups_name oder ix_interest_groups_name_unique)"
            assert code_unique, "Code-Index ist nicht unique (erwartet: ix_interest_groups_code oder ix_interest_groups_code_unique)"
