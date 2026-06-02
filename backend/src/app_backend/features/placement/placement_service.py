import uuid
from datetime import date, datetime, timezone
from typing import List, Optional, Protocol

from sqlalchemy import select

from app_backend.models.activity_logs import ActivityLogs
from app_backend.models.placements import Placements
from app_backend.repositories.activity_log_repository import ActivityLogRepository
from app_backend.repositories.placement_repository import PlacementRepository
from app_backend.schemas.placement import ActivityLogCreate, ActivityLogResponse, PlacementResponse


class IPlacementService(Protocol):
    def get_my_placements(self, student_id: uuid.UUID) -> List[PlacementResponse]: ...
    def create_activity_log(
        self, student_id: uuid.UUID, placement_id: uuid.UUID, data: ActivityLogCreate
    ) -> ActivityLogResponse: ...
    def list_activity_logs(
        self, placement_id: uuid.UUID, student_id: Optional[uuid.UUID] = None
    ) -> List[ActivityLogResponse]: ...


class PlacementService:
    def __init__(
        self,
        placement_repo: PlacementRepository,
        activity_log_repo: ActivityLogRepository,
    ):
        self.placement_repo = placement_repo
        self.activity_log_repo = activity_log_repo

    def get_my_placements(self, student_id: uuid.UUID) -> List[PlacementResponse]:
        query = select(Placements).where(Placements.student_id == student_id)
        placements = self.placement_repo.session.scalars(query).all()
        return [PlacementResponse.model_validate(p) for p in placements]

    def create_activity_log(self, student_id: uuid.UUID, placement_id: uuid.UUID, data: ActivityLogCreate) -> ActivityLogResponse:
        placement = self.placement_repo.get_by_id(placement_id)
        if not placement:
            raise ValueError("Penempatan tidak ditemukan")
        if placement.student_id != student_id:
            raise PermissionError("Bukan pemilik penempatan")

        if data.log_date > date.today():
            raise ValueError(f"Tanggal log ({data.log_date}) tidak boleh di masa depan (Hari ini: {date.today()})")

        if data.log_date < placement.start_date or data.log_date > placement.end_date:
            raise ValueError(f"Tanggal log ({data.log_date}) di luar rentang magang ({placement.start_date} s/d {placement.end_date})")

        query = select(ActivityLogs).where(
            ActivityLogs.placement_id == placement_id,
            ActivityLogs.activity_date == data.log_date,
        )
        existing = self.activity_log_repo.session.scalars(query).first()
        if existing:
            raise ValueError("Log untuk tanggal ini sudah ada")

        # Calculate duration
        start_dt = datetime.combine(data.log_date, data.start_time)
        end_dt = datetime.combine(data.log_date, data.end_time)
        if end_dt <= start_dt:
            raise ValueError("Waktu selesai harus setelah waktu mulai")

        duration = (end_dt - start_dt).total_seconds() / 3600.0

        try:
            log = ActivityLogs(
                id=uuid.uuid4(),
                placement_id=placement_id,
                activity_date=data.log_date,
                duration_hours=duration,
                description_raw=data.description_raw,
                updated_at=datetime.now(timezone.utc),
            )
            self.activity_log_repo.create(log)
            self.activity_log_repo.save_changes()
            return ActivityLogResponse.model_validate(log)
        except Exception as exc:
            self.activity_log_repo.rollback()
            raise exc

    def list_activity_logs(self, placement_id: uuid.UUID, student_id: Optional[uuid.UUID] = None) -> List[ActivityLogResponse]:
        placement = self.placement_repo.get_by_id(placement_id)
        if not placement:
            raise ValueError("Penempatan tidak ditemukan")
        if student_id and placement.student_id != student_id:
            raise PermissionError("Bukan pemilik penempatan")

        query = select(ActivityLogs).where(ActivityLogs.placement_id == placement_id).order_by(ActivityLogs.activity_date.desc())
        logs = self.activity_log_repo.session.scalars(query).all()
        return [ActivityLogResponse.model_validate(log) for log in logs]

    def list_admin_placements(self) -> List[PlacementResponse]:
        return [PlacementResponse.model_validate(p) for p in self.placement_repo.get_all()]
