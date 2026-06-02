import uuid
from dataclasses import dataclass
from datetime import date
from http import HTTPStatus
from typing import Optional

from sqlalchemy.orm import Session

from app_backend.models.placements import Placements
from app_backend.shared.tasks.report_tasks import generate_final_report


@dataclass
class GenerateReportCommand:
    placement_id: uuid.UUID
    student_id: uuid.UUID


@dataclass
class GenerateReportResult:
    message: Optional[str] = None
    error_message: Optional[str] = None
    error_status_code: HTTPStatus = HTTPStatus.BAD_REQUEST

    def got_error(self) -> bool:
        return self.error_message is not None


def generate_report_command_handler(command: GenerateReportCommand, session: Session) -> GenerateReportResult:
    placement = (
        session.query(Placements)
        .filter(
            Placements.id == command.placement_id,
            Placements.student_id == command.student_id,
        )
        .first()
    )

    from datetime import datetime, timedelta, timezone
    from http import HTTPStatus

    if not placement:
        return GenerateReportResult(
            error_message="Placement tidak ditemukan",
            error_status_code=HTTPStatus.NOT_FOUND,
        )

    if placement.end_date > date.today():
        return GenerateReportResult(
            error_message="Laporan hanya bisa di-generate setelah masa magang selesai",
            error_status_code=HTTPStatus.BAD_REQUEST,
        )

    # Rate Limiting: 5 minutes cooldown
    if placement.last_report_generated_at:
        now = datetime.now(timezone.utc)
        last_generated = placement.last_report_generated_at
        if last_generated.tzinfo is None:
            last_generated = last_generated.replace(tzinfo=timezone.utc)
        if now - last_generated < timedelta(minutes=5):
            return GenerateReportResult(
                error_message="Harap tunggu 5 menit sebelum men-generate laporan lagi.",
                error_status_code=HTTPStatus.TOO_MANY_REQUESTS,
            )

    # Trigger Celery Task
    placement.last_report_generated_at = datetime.now(timezone.utc)
    session.commit()
    generate_final_report.delay(str(placement.id))

    return GenerateReportResult(message="Proses pembuatan laporan sedang berjalan di background")
