from dataclasses import dataclass
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from app_backend.models.placements import Placements

@dataclass
class GetMyPlacementsCommand:
    student_id: uuid.UUID

@dataclass
class GetMyPlacementsResult:
    placements: Optional[List[Placements]] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None

def get_my_placements_command_handler(
    command: GetMyPlacementsCommand,
    session: Session,
) -> GetMyPlacementsResult:
    placements = session.query(Placements).filter_by(student_id=command.student_id).all()
    
    return GetMyPlacementsResult(placements=placements)
