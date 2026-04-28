from dataclasses import dataclass
import uuid
import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from app_backend.models.activity_logs import ActivityLogs
from app_backend.models.placements import Placements

@dataclass
class UpdateActivityLogCommand:
    placement_id: uuid.UUID
    log_id: uuid.UUID
    student_id: uuid.UUID
    log_date: Optional[datetime.date] = None
    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None
    description_raw: Optional[str] = None

@dataclass
class UpdateActivityLogResult:
    log: Optional[ActivityLogs] = None
    error_message: Optional[str] = None
    error_code: int = 400

    def got_error(self) -> bool:
        return self.error_message is not None

def update_activity_log_command_handler(
    command: UpdateActivityLogCommand,
    session: Session,
) -> UpdateActivityLogResult:
    placement = session.query(Placements).filter_by(id=command.placement_id, student_id=command.student_id).first()
    if not placement:
        return UpdateActivityLogResult(error_message="Placement tidak ditemukan", error_code=404)

    log = session.query(ActivityLogs).filter_by(id=command.log_id, placement_id=placement.id).first()
    if not log:
        return UpdateActivityLogResult(error_message="Activity log tidak ditemukan", error_code=404)

    new_date = command.log_date if command.log_date is not None else log.activity_date

    if new_date > datetime.date.today():
        return UpdateActivityLogResult(error_message="log_date tidak boleh di masa depan")

    if not (placement.start_date <= new_date <= placement.end_date):
        return UpdateActivityLogResult(error_message="log_date harus dalam rentang periode magang")

    if new_date != log.activity_date:
        existing_log = session.query(ActivityLogs).filter_by(placement_id=placement.id, activity_date=new_date).first()
        if existing_log:
            return UpdateActivityLogResult(error_message="Log untuk tanggal ini sudah ada", error_code=409)

    # Note: Since start_time and end_time are not stored directly, if the user wants to update them,
    # they must provide BOTH or we just don't support updating time easily unless we add columns.
    # The roadmap only says "Edit log yang sudah ada". We will support updating description_raw and date.
    # If they provide start_time and end_time, we recalculate duration.
    if command.start_time is not None and command.end_time is not None:
        start_dt = datetime.datetime.combine(new_date, command.start_time)
        end_dt = datetime.datetime.combine(new_date, command.end_time)
        
        if end_dt <= start_dt:
            return UpdateActivityLogResult(error_message="waktu selesai harus lebih besar dari waktu mulai")

        delta = end_dt - start_dt
        duration_hours = Decimal(delta.total_seconds() / 3600.0)

        if duration_hours <= 0 or duration_hours > 24:
            return UpdateActivityLogResult(error_message="Durasi harus antara 0 hingga 24 jam")
            
        log.duration_hours = duration_hours

    log.activity_date = new_date
    if command.description_raw is not None:
        log.description_raw = command.description_raw

    session.commit()
    session.refresh(log)
    
    return UpdateActivityLogResult(log=log)
