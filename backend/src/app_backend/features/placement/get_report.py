from dataclasses import dataclass
from typing import Optional
import uuid

from sqlalchemy.orm import Session

from app_backend.models.placements import Placements


@dataclass
class GetReportCommand:
    placement_id: uuid.UUID
    student_id: uuid.UUID


@dataclass
class GetReportResult:
    status: Optional[str] = None
    report_url: Optional[str] = None
    last_generated_at: Optional[str] = None
    error_message: Optional[str] = None
    error_code: int = 400

    def got_error(self) -> bool:
        return self.error_message is not None


def get_report_command_handler(
    command: GetReportCommand,
    session: Session,
) -> GetReportResult:
    placement = session.query(Placements).filter_by(
        id=command.placement_id,
        student_id=command.student_id,
    ).first()

    if not placement:
        return GetReportResult(error_message="Placement tidak ditemukan", error_code=404)

    if placement.auto_generated_report_url:
        return GetReportResult(
            status="generated",
            report_url=placement.auto_generated_report_url,
            last_generated_at=(
                placement.last_report_generated_at.isoformat()
                if placement.last_report_generated_at
                else None
            ),
        )

    return GetReportResult(status="not_generated")
