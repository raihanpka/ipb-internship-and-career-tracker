import uuid
from unittest.mock import MagicMock, patch
import pytest

from tests.conftest import STUDENT_USER_ID, ADMIN_USER_ID, NOW

PLACEMENT_ID = uuid.UUID("33333333-3333-3333-3333-333333333333")
LOG_ID = uuid.UUID("44444444-4444-4444-4444-444444444444")

# ─── Self-Reporting Pipeline ──────────────────────────────────────────────────

def test_get_my_placements(client_as_student):
    with patch("app_backend.routers.api.placement.get_my_placements_command_handler") as mock_handler:
        from app_backend.schemas.placement import PlacementResponse
        import datetime
        mock_handler.return_value = MagicMock(
            got_error=lambda: False,
            placements=[
                PlacementResponse(
                    id=PLACEMENT_ID,
                    student_id=STUDENT_USER_ID,
                    company_id=uuid.uuid4(),
                    start_date=datetime.date(2026, 1, 1),
                    end_date=datetime.date(2026, 6, 30),
                    status="ACTIVE"
                )
            ]
        )
        resp = client_as_student.get("/api/v1/placements/me")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == str(PLACEMENT_ID)

def test_create_activity_log_success(client_as_student):
    with patch("app_backend.routers.api.placement.create_activity_log_command_handler") as mock_handler:
        from app_backend.schemas.placement import ActivityLogResponse
        import datetime
        mock_handler.return_value = MagicMock(
            got_error=lambda: False,
            log=ActivityLogResponse(
                id=LOG_ID,
                placement_id=PLACEMENT_ID,
                activity_date=datetime.date(2026, 2, 1),
                duration_hours=8.0,
                description_raw="Worked on feature X"
            )
        )
        resp = client_as_student.post(
            f"/api/v1/placements/{PLACEMENT_ID}/logs",
            json={
                "log_date": "2026-02-01",
                "start_time": "09:00",
                "end_time": "17:00",
                "description_raw": "Worked on feature X"
            }
        )
    assert resp.status_code == 201
    assert resp.json()["id"] == str(LOG_ID)

def test_create_activity_log_out_of_bounds(client_as_student):
    with patch("app_backend.routers.api.placement.create_activity_log_command_handler") as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: True,
            error_message="log_date harus dalam rentang periode magang",
            error_code=400
        )
        resp = client_as_student.post(
            f"/api/v1/placements/{PLACEMENT_ID}/logs",
            json={
                "log_date": "2026-08-01",
                "start_time": "09:00",
                "end_time": "17:00",
                "description_raw": "Out of bounds"
            }
        )
    assert resp.status_code == 400
    assert "rentang" in resp.json()["detail"]

def test_create_activity_log_duplicate(client_as_student):
    with patch("app_backend.routers.api.placement.create_activity_log_command_handler") as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Log untuk tanggal ini sudah ada",
            error_code=409
        )
        resp = client_as_student.post(
            f"/api/v1/placements/{PLACEMENT_ID}/logs",
            json={
                "log_date": "2026-02-01",
                "start_time": "09:00",
                "end_time": "17:00",
                "description_raw": "Duplicate"
            }
        )
    assert resp.status_code == 409
    assert "sudah ada" in resp.json()["detail"]

def test_upload_activity_log_attachment_success(client_as_student):
    with patch("app_backend.routers.api.placement.upload_activity_log_attachment_command_handler") as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: False,
            message="Lampiran berhasil diunggah",
            attachment_url="/uploads/activity_logs/test.png"
        )
        files = {"file": ("test.png", b"dummy content", "image/png")}
        resp = client_as_student.post(f"/api/v1/placements/{PLACEMENT_ID}/logs/{LOG_ID}/attachment", files=files)
    assert resp.status_code == 200
    assert resp.json()["attachment_url"] == "/uploads/activity_logs/test.png"

def test_list_admin_placements(client_as_admin):
    with patch("app_backend.routers.api.admin.list_admin_placements_command_handler") as mock_handler:
        mock_handler.return_value = MagicMock(got_error=lambda: False, placements=[])
        resp = client_as_admin.get("/api/v1/admin/placements")
    assert resp.status_code == 200
    assert resp.json() == []
