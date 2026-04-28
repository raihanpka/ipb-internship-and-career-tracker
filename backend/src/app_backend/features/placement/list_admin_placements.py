from dataclasses import dataclass
from typing import List, Optional
from sqlalchemy.orm import Session
from app_backend.models.placements import Placements

@dataclass
class ListAdminPlacementsCommand:
    pass

@dataclass
class ListAdminPlacementsResult:
    placements: Optional[List[Placements]] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None

def list_admin_placements_command_handler(
    command: ListAdminPlacementsCommand,
    session: Session,
) -> ListAdminPlacementsResult:
    # Optional filtering can be added here
    placements = session.query(Placements).all()
    
    return ListAdminPlacementsResult(placements=placements)
