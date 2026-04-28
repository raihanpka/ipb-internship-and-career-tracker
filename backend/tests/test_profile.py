"""
Tests: Profile Router   –  GET/PUT /api/v1/profile/*

Covers:
  GET /profile/me       – 200 data lengkap, 403 bukan student, 404 profil tidak ada
  PUT /profile/cv-data  – 200 update sukses, 400 error, 403 bukan student
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from tests.conftest import DEPT_ID, NOW, SKILL_ID, STUDENT_USER_ID

PROFILE_RESPONSE = {
    "user_id": str(STUDENT_USER_ID),
    "email": "student@ipb.ac.id",
    "role": "STUDENT",
    "is_active": True,
    "nim": "G1234567890",
    "full_name": "Budi Santoso",
    "semester": 5,
    "department": {
        "id": str(DEPT_ID),
        "code": "ILK",
        "name": "Ilmu Komputer",
        "faculty": "FMIPA",
    },
    "gpa": "3.75",
    "is_mbkm_eligible": True,
    "phone_number": "+6281234567890",
    "linkedin_url": "https://linkedin.com/in/budi",
    "cv_url": "https://drive.google.com/file/abc",
    "skills": [
        {
            "skill_id": str(SKILL_ID),
            "skill_name": "Python",
            "skill_category": "Programming",
            "level": 4,
        }
    ],
    "updated_at": NOW.isoformat(),
}


# ════════════════════════════════════════════════════════════════════════════
#  GET /profile/me
# ════════════════════════════════════════════════════════════════════════════


def test_get_student_profile_success(client_as_student):
    with patch(
        "app_backend.routers.api.profile.get_student_profile_command_handler"
    ) as mock_handler:
        from app_backend.schemas.profile import (DepartmentInfo, SkillInfo,
                                                 StudentProfileResponse)

        mock_handler.return_value = MagicMock(
            got_error=lambda: False,
            profile=StudentProfileResponse(
                user_id=STUDENT_USER_ID,
                email="student@ipb.ac.id",
                role="STUDENT",
                is_active=True,
                nim="G1234567890",
                full_name="Budi Santoso",
                semester=5,
                department=DepartmentInfo(
                    id=DEPT_ID,
                    code="ILK",
                    name="Ilmu Komputer",
                    faculty="FMIPA",
                ),
                gpa=Decimal("3.75"),
                is_mbkm_eligible=True,
                phone_number="+6281234567890",
                linkedin_url="https://linkedin.com/in/budi",
                cv_url="https://drive.google.com/file/abc",
                skills=[
                    SkillInfo(
                        skill_id=SKILL_ID,
                        skill_name="Python",
                        skill_category="Programming",
                        level=4,
                    )
                ],
                updated_at=NOW,
            ),
        )
        resp = client_as_student.get("/api/v1/profile/me")

    assert resp.status_code == 200
    data = resp.json()
    assert data["nim"] == "G1234567890"
    assert data["email"] == "student@ipb.ac.id"
    assert data["department"]["code"] == "ILK"
    assert len(data["skills"]) == 1
    assert data["skills"][0]["skill_name"] == "Python"
    assert data["skills"][0]["level"] == 4


def test_get_student_profile_no_department(client_as_student):
    """Profil tanpa department masih bisa dikembalikan (department = None)."""
    with patch(
        "app_backend.routers.api.profile.get_student_profile_command_handler"
    ) as mock_handler:
        from app_backend.schemas.profile import StudentProfileResponse

        mock_handler.return_value = MagicMock(
            got_error=lambda: False,
            profile=StudentProfileResponse(
                user_id=STUDENT_USER_ID,
                email="student@ipb.ac.id",
                role="STUDENT",
                is_active=True,
                nim="G1234567890",
                full_name="Budi Santoso",
                semester=5,
                department=None,
                gpa=None,
                is_mbkm_eligible=True,
                phone_number=None,
                linkedin_url=None,
                cv_url=None,
                skills=[],
                updated_at=NOW,
            ),
        )
        resp = client_as_student.get("/api/v1/profile/me")

    assert resp.status_code == 200
    data = resp.json()
    assert data["department"] is None
    assert data["skills"] == []


def test_get_student_profile_not_found(client_as_student):
    with patch(
        "app_backend.routers.api.profile.get_student_profile_command_handler"
    ) as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Profil mahasiswa tidak ditemukan",
        )
        resp = client_as_student.get("/api/v1/profile/me")

    assert resp.status_code == 404
    assert "tidak ditemukan" in resp.json()["detail"]


def test_get_student_profile_forbidden_for_admin(client_as_admin):
    """Admin tidak boleh akses /profile/me (hanya STUDENT)."""
    resp = client_as_admin.get("/api/v1/profile/me")
    assert resp.status_code == 403


def test_get_student_profile_unauthenticated(client_no_auth):
    resp = client_no_auth.get("/api/v1/profile/me")
    assert resp.status_code == 401


# ════════════════════════════════════════════════════════════════════════════
#  PUT /profile/cv-data
# ════════════════════════════════════════════════════════════════════════════

CV_PAYLOAD = {
    "phone_number": "+6281234567890",
    "linkedin_url": "https://linkedin.com/in/budi",
    "cv_url": "https://drive.google.com/file/d/abc/view",
    "skills": [
        {"skill_id": str(SKILL_ID), "level": 4},
    ],
}


def test_update_cv_data_success(client_as_student):
    with patch(
        "app_backend.routers.api.profile.update_cv_data_command_handler"
    ) as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: False,
            message="Data CV berhasil diperbarui",
        )
        resp = client_as_student.put("/api/v1/profile/cv-data", json=CV_PAYLOAD)

    assert resp.status_code == 200
    assert resp.json()["message"] == "Data CV berhasil diperbarui"


def test_update_cv_data_partial(client_as_student):
    """Hanya update phone_number saja — field lain tidak dikirim."""
    with patch(
        "app_backend.routers.api.profile.update_cv_data_command_handler"
    ) as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: False,
            message="Data CV berhasil diperbarui",
        )
        resp = client_as_student.put(
            "/api/v1/profile/cv-data", json={"phone_number": "+628987654321"}
        )

    assert resp.status_code == 200


def test_update_cv_data_invalid_skill_id(client_as_student):
    """Skill ID yang tidak ada di master → service mengembalikan error."""
    with patch(
        "app_backend.routers.api.profile.update_cv_data_command_handler"
    ) as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Update gagal: FK constraint violated",
        )
        resp = client_as_student.put(
            "/api/v1/profile/cv-data",
            json={"skills": [{"skill_id": str(SKILL_ID), "level": 4}]},
        )

    assert resp.status_code == 400


def test_update_cv_data_level_out_of_range(client_as_student):
    """Level di luar 1-5 harus ditolak oleh Pydantic sebelum masuk handler."""
    resp = client_as_student.put(
        "/api/v1/profile/cv-data",
        json={"skills": [{"skill_id": str(SKILL_ID), "level": 99}]},
    )
    assert resp.status_code == 422


def test_update_cv_data_forbidden_for_admin(client_as_admin):
    resp = client_as_admin.put("/api/v1/profile/cv-data", json=CV_PAYLOAD)
    assert resp.status_code == 403


def test_update_cv_data_unauthenticated(client_no_auth):
    resp = client_no_auth.put("/api/v1/profile/cv-data", json=CV_PAYLOAD)
    assert resp.status_code == 401


# ════════════════════════════════════════════════════════════════════════════
#  POST /profile/student/cv
# ════════════════════════════════════════════════════════════════════════════

def test_upload_cv_success(client_as_student):
    with patch(
        "app_backend.routers.api.profile.upload_cv_command_handler"
    ) as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: False,
            message="CV berhasil diupload",
            cv_url="/uploads/cv/dummy.pdf"
        )
        
        file_content = b"%PDF-1.4 dummy content"
        files = {"file": ("dummy.pdf", file_content, "application/pdf")}
        resp = client_as_student.post("/api/v1/profile/student/cv", files=files)
        
    assert resp.status_code == 200
    assert resp.json()["message"] == "CV berhasil diupload"
    assert "cv_url" in resp.json()
    assert resp.json()["cv_url"].startswith("/uploads/cv/")


def test_upload_cv_not_pdf(client_as_student):
    with patch(
        "app_backend.routers.api.profile.upload_cv_command_handler"
    ) as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: True,
            error_message="File harus berformat PDF",
        )
        
        file_content = b"Not a PDF"
        files = {"file": ("dummy.txt", file_content, "text/plain")}
        resp = client_as_student.post("/api/v1/profile/student/cv", files=files)
        
    assert resp.status_code == 400
    assert "File harus berformat PDF" in resp.json()["detail"]
