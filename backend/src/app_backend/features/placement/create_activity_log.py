from dataclasses import dataclass
import uuid
import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from app_backend.models.activity_logs import ActivityLogs
from app_backend.models.placements import Placements

@dataclass
class CreateActivityLogCommand:
    placement_id: uuid.UUID
    student_id: uuid.UUID
    log_date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    description_raw: str

@dataclass
class CreateActivityLogResult:
    log: Optional[ActivityLogs] = None
    error_message: Optional[str] = None
    error_code: int = 400

    def got_error(self) -> bool:
        return self.error_message is not None

def create_activity_log_command_handler(
    command: CreateActivityLogCommand,
    session: Session,
) -> CreateActivityLogResult:
    # Validasi placement exists & belongs to student
    placement = session.query(Placements).filter_by(id=command.placement_id, student_id=command.student_id).first()
    if not placement:
        return CreateActivityLogResult(error_message="Placement tidak ditemukan", error_code=404)

    # Validasi log_date tidak boleh di masa depan
    if command.log_date > datetime.date.today():
        return CreateActivityLogResult(error_message="log_date tidak boleh di masa depan")

    # Validasi log_date harus dalam rentang placement.start_date dan placement.end_date
    if not (placement.start_date <= command.log_date <= placement.end_date):
        return CreateActivityLogResult(error_message="log_date harus dalam rentang periode magang")

    # Validasi duplikasi (hanya 1 log per tanggal per placement)
    existing_log = session.query(ActivityLogs).filter_by(placement_id=placement.id, activity_date=command.log_date).first()
    if existing_log:
        return CreateActivityLogResult(error_message="Log untuk tanggal ini sudah ada", error_code=409)

    # Kalkulasi durasi
    start_dt = datetime.datetime.combine(command.log_date, command.start_time)
    end_dt = datetime.datetime.combine(command.log_date, command.end_time)
    
    if end_dt <= start_dt:
        return CreateActivityLogResult(error_message="waktu selesai harus lebih besar dari waktu mulai")

    delta = end_dt - start_dt
    duration_hours = Decimal(delta.total_seconds() / 3600.0)

    if duration_hours <= 0 or duration_hours > 24:
        return CreateActivityLogResult(error_message="Durasi harus antara 0 hingga 24 jam")

    log = ActivityLogs(
        placement_id=placement.id,
        activity_date=command.log_date,
        duration_hours=duration_hours,
        description_raw=command.description_raw
    )
    
    session.add(log)
    session.commit()
    session.refresh(log)
    
    return CreateActivityLogResult(log=log)
