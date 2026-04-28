"""
Tests for:
  POST  /api/v1/applications            (Initialize External Apply)
  PATCH /api/v1/applications/{id}/status (Self-Report Status Update)
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from tests.conftest import STUDENT_USER_ID, NOW

VACANCY_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
APPLICATION_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
LOG_ID = uuid.UUID("33333333-3333-3333-3333-333333333333")

APPLY_PAYLOAD = {
    "vacancy_id": str(VACANCY_ID),
}

STATUS_UPDATE_URL = f"/api/v1/applications/{APPLICATION_ID}/status"


# ─── Success ──────────────────────────────────────────────────────────────────


def test_initialize_apply_success(client_as_student):
    with patch(
        "app_backend.routers.api.application.initialize_apply_command_handler"
    ) as mock_handler:
        from app_backend.schemas.application import ApplicationResponse

        mock_handler.return_value = MagicMock(
            error_message=None,
            application=ApplicationResponse(
                id=APPLICATION_ID,
                vacancy_id=VACANCY_ID,
                student_id=STUDENT_USER_ID,
                cv_snapshot_url="https://example.com/cv.pdf",
                status="APPLIED",
            ),
        )
        resp = client_as_student.post("/api/v1/applications", json=APPLY_PAYLOAD)

    assert resp.status_code == 201
    data = resp.json()
    assert data["vacancy_id"] == str(VACANCY_ID)
    assert data["student_id"] == str(STUDENT_USER_ID)
    assert data["cv_snapshot_url"] == "https://example.com/cv.pdf"
    assert data["status"] == "APPLIED"


# ─── Business logic errors ────────────────────────────────────────────────────


def test_initialize_apply_no_cv(client_as_student):
    """Student has no CV uploaded yet."""
    with patch(
        "app_backend.routers.api.application.initialize_apply_command_handler"
    ) as mock_handler:
        mock_handler.return_value = MagicMock(
            error_message="You must upload a CV before applying to a vacancy.",
            application=None,
        )
        resp = client_as_student.post("/api/v1/applications", json=APPLY_PAYLOAD)

    assert resp.status_code == 400
    assert "CV" in resp.json()["detail"]


def test_initialize_apply_duplicate(client_as_student):
    """Student already applied to this vacancy."""
    with patch(
        "app_backend.routers.api.application.initialize_apply_command_handler"
    ) as mock_handler:
        mock_handler.return_value = MagicMock(
            error_message="You have already applied to this vacancy.",
            application=None,
        )
        resp = client_as_student.post("/api/v1/applications", json=APPLY_PAYLOAD)

    assert resp.status_code == 400
    assert "already applied" in resp.json()["detail"]


# ─── Validation errors ────────────────────────────────────────────────────────


def test_initialize_apply_missing_vacancy_id(client_as_student):
    """Request body is missing vacancy_id entirely."""
    resp = client_as_student.post("/api/v1/applications", json={})

    assert resp.status_code == 422


def test_initialize_apply_invalid_vacancy_id(client_as_student):
    """vacancy_id is not a valid UUID."""
    resp = client_as_student.post(
        "/api/v1/applications", json={"vacancy_id": "not-a-uuid"}
    )

    assert resp.status_code == 422


# ─── Authorization ────────────────────────────────────────────────────────────


def test_initialize_apply_as_admin_forbidden(client_as_admin_for_student_only):
    """Admin cannot access this student-only endpoint."""
    resp = client_as_admin_for_student_only.post(
        "/api/v1/applications", json=APPLY_PAYLOAD
    )

    assert resp.status_code == 403


def test_initialize_apply_unauthenticated(client_no_auth):
    """Request without a token is rejected."""
    resp = client_no_auth.post("/api/v1/applications", json=APPLY_PAYLOAD)

    assert resp.status_code == 401


# ─── PATCH /{id}/status — helpers ─────────────────────────────────────────────


def _make_status_update_result(
    new_status: str = "INTERVIEW",
    previous_status: str = "APPLIED",
    proof_url: str | None = None,
):
    """Build a mock UpdateApplicationStatusResult for happy-path tests."""
    from app_backend.schemas.application import ApplicationLogResponse, ApplicationResponse

    application = ApplicationResponse(
        id=APPLICATION_ID,
        vacancy_id=VACANCY_ID,
        student_id=STUDENT_USER_ID,
        cv_snapshot_url="https://example.com/cv.pdf",
        status=new_status,
    )
    log = ApplicationLogResponse(
        id=LOG_ID,
        application_id=APPLICATION_ID,
        new_status=new_status,
        previous_status=previous_status,
        changed_by=STUDENT_USER_ID,
        proof_url=proof_url,
        reason=None,
        created_at=NOW,
    )
    return MagicMock(error_message=None, error_status_code=400, application=application, log=log)


PATCH_HANDLER = "app_backend.routers.api.application.update_application_status_command_handler"


# ─── PATCH /{id}/status — Success ─────────────────────────────────────────────


def test_update_status_success(client_as_student):
    """Student self-reports a status change from APPLIED to INTERVIEW."""
    with patch(PATCH_HANDLER) as mock_handler:
        mock_handler.return_value = _make_status_update_result("INTERVIEW", "APPLIED")
        resp = client_as_student.patch(
            STATUS_UPDATE_URL, json={"new_status": "INTERVIEW"}
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["application"]["status"] == "INTERVIEW"
    assert data["log"]["new_status"] == "INTERVIEW"
    assert data["log"]["previous_status"] == "APPLIED"


def test_update_status_accepted_with_proof(client_as_student):
    """Changing to ACCEPTED with proof_url succeeds."""
    proof = "https://example.com/loa.png"
    with patch(PATCH_HANDLER) as mock_handler:
        mock_handler.return_value = _make_status_update_result("ACCEPTED", "OFFERED", proof)
        resp = client_as_student.patch(
            STATUS_UPDATE_URL,
            json={"new_status": "ACCEPTED", "proof_url": proof},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["application"]["status"] == "ACCEPTED"
    assert data["log"]["proof_url"] == proof


# ─── PATCH /{id}/status — Validation errors (422) ─────────────────────────────


def test_update_status_accepted_without_proof(client_as_student):
    """Pydantic rejects ACCEPTED without proof_url before reaching the handler."""
    resp = client_as_student.patch(
        STATUS_UPDATE_URL, json={"new_status": "ACCEPTED"}
    )

    assert resp.status_code == 422
    assert "proof_url" in resp.text


def test_update_status_invalid_status_value(client_as_student):
    """An unknown status string is rejected by Pydantic (422)."""
    resp = client_as_student.patch(
        STATUS_UPDATE_URL, json={"new_status": "FLYING"}
    )

    assert resp.status_code == 422


# ─── PATCH /{id}/status — Business logic errors ───────────────────────────────


def test_update_status_application_not_found(client_as_student):
    """Handler returns 404 when the application does not exist."""
    with patch(PATCH_HANDLER) as mock_handler:
        mock_handler.return_value = MagicMock(
            error_message="Lamaran tidak ditemukan.",
            error_status_code=404,
            application=None,
            log=None,
        )
        resp = client_as_student.patch(
            STATUS_UPDATE_URL, json={"new_status": "INTERVIEW"}
        )

    assert resp.status_code == 404


def test_update_status_wrong_student(client_as_student):
    """Handler returns 403 when the application belongs to another student."""
    with patch(PATCH_HANDLER) as mock_handler:
        mock_handler.return_value = MagicMock(
            error_message="Anda tidak memiliki izin untuk mengubah lamaran ini.",
            error_status_code=403,
            application=None,
            log=None,
        )
        resp = client_as_student.patch(
            STATUS_UPDATE_URL, json={"new_status": "INTERVIEW"}
        )

    assert resp.status_code == 403


def test_update_status_invalid_transition(client_as_student):
    """Handler returns 400 when the domain rejects the transition (e.g. WITHDRAWN → anything)."""
    with patch(PATCH_HANDLER) as mock_handler:
        mock_handler.return_value = MagicMock(
            error_message="Aplikasi yang sudah di-withdraw tidak bisa diupdate",
            error_status_code=400,
            application=None,
            log=None,
        )
        resp = client_as_student.patch(
            STATUS_UPDATE_URL, json={"new_status": "INTERVIEW"}
        )

    assert resp.status_code == 400
    assert "withdraw" in resp.json()["detail"]


# ─── PATCH /{id}/status — Authorization ───────────────────────────────────────


def test_update_status_as_admin_forbidden(client_as_admin_for_student_only):
    """Admin cannot access this student-only endpoint."""
    resp = client_as_admin_for_student_only.patch(
        STATUS_UPDATE_URL, json={"new_status": "INTERVIEW"}
    )

    assert resp.status_code == 403


def test_update_status_unauthenticated(client_no_auth):
    """Request without a token is rejected."""
    resp = client_no_auth.patch(STATUS_UPDATE_URL, json={"new_status": "INTERVIEW"})

    assert resp.status_code == 401
# ─── Self-Reporting Pipeline ──────────────────────────────────────────────────

def test_update_application_status_success(client_as_student):
    with patch("app_backend.routers.api.application.update_application_status_command_handler") as mock_handler:
        from app_backend.schemas.application import ApplicationResponse
        mock_handler.return_value = MagicMock(
            got_error=lambda: False,
            application=ApplicationResponse(
                id=APPLICATION_ID,
                vacancy_id=VACANCY_ID,
                student_id=STUDENT_USER_ID,
                cv_snapshot_url="https://example.com/cv.pdf",
                status="INTERVIEW",
            )
        )
        resp = client_as_student.patch(f"/api/v1/applications/{APPLICATION_ID}/status", json={"status": "INTERVIEW"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "INTERVIEW"

def test_upload_application_proof_success(client_as_student):
    with patch("app_backend.routers.api.application.upload_application_proof_command_handler") as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: False,
            message="Bukti berhasil diunggah",
            proof_url="/uploads/proofs/test.pdf"
        )
        files = {"file": ("test.pdf", b"dummy content", "application/pdf")}
        resp = client_as_student.post(f"/api/v1/applications/{APPLICATION_ID}/proof", files=files)
    assert resp.status_code == 200
    assert resp.json()["proof_url"] == "/uploads/proofs/test.pdf"

def test_get_application_history_success(client_as_student):
    with patch("app_backend.routers.api.application.get_application_history_command_handler") as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: False,
            logs=[]
        )
        resp = client_as_student.get(f"/api/v1/applications/{APPLICATION_ID}/history")
    assert resp.status_code == 200
