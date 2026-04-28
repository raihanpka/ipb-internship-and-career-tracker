from dataclasses import dataclass
from datetime import date
from typing import Optional
import uuid

from sqlalchemy.orm import Session

from app_backend.models.placements import Placements
from app_backend.shared.tasks.report_tasks import generate_final_report


@dataclass
class GenerateReportCommand:
    placement_id: uuid.UUID
    student_id: uuid.UUID


@dataclass
class GenerateReportResult:
    task_id: Optional[str] = None
    message: Optional[str] = None
    error_message: Optional[str] = None
    error_code: int = 400

    def got_error(self) -> bool:
        return self.error_message is not None


def generate_report_command_handler(
    command: GenerateReportCommand,
    session: Session,
) -> GenerateReportResult:
    placement = session.query(Placements).filter_by(
        id=command.placement_id,
        student_id=command.student_id,
    ).first()

    if not placement:
        return GenerateReportResult(error_message="Placement tidak ditemukan", error_code=404)

    if placement.end_date > date.today():
        return GenerateReportResult(
            error_message="Laporan hanya bisa digenerate setelah masa penempatan selesai",
            error_code=400,
        )

    task = generate_final_report.apply_async(
        args=[str(placement.id)],
        queue="report",
    )

    return GenerateReportResult(
        task_id=task.id,
        message="Pembuatan laporan sedang diproses. Gunakan endpoint GET /report untuk mengecek status.",
    )
