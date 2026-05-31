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
    from sqlalchemy.orm import joinedload
    placements = session.query(Placements).options(
        joinedload(Placements.student),
        joinedload(Placements.company)
    ).all()

    return ListAdminPlacementsResult(placements=placements)
