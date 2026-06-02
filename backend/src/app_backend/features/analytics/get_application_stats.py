from dataclasses import dataclass, field
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app_backend.models.applications import Applications


@dataclass
class GetApplicationStatsCommand:
    pass


@dataclass
class StatusBreakdownData:
    status: str
    total: int


@dataclass
class GetApplicationStatsResult:
    total_applications: int = 0
    status_breakdown: List[StatusBreakdownData] = field(default_factory=list)
    conversion_rate: float = 0.0
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None


def get_application_stats_command_handler(
    command: GetApplicationStatsCommand,
    session: Session,
) -> GetApplicationStatsResult:

    total = session.query(func.count(Applications.id)).filter(Applications.status != 'WITHDRAWN').scalar() or 0

    rows = (
        session.query(
            Applications.status,
            func.count(Applications.id).label("total"),
        )
        .filter(Applications.status != 'WITHDRAWN')
        .group_by(Applications.status)
        .order_by(func.count(Applications.id).desc())
        .all()
    )
    status_breakdown = [
        StatusBreakdownData(
            status=row[0] if row[0] is not None else "UNKNOWN",
            total=row[1],
        )
        for row in rows
    ]

    accepted = next((s.total for s in status_breakdown if s.status == "ACCEPTED"), 0)
    conversion_rate = round((accepted / total * 100), 2) if total > 0 else 0.0

    return GetApplicationStatsResult(
        total_applications=total,
        status_breakdown=status_breakdown,
        conversion_rate=conversion_rate,
    )
