"""
Tests: Admin Router                 –  /api/v1/admin/*

Covers:
  PATCH /users/{id}/toggle-active   – 200 success, 404 not found, 403 non-admin
  GET   /profile/me                  – 200, 404, 403 non-admin
  PATCH /profile/me                  – 200, 409 NIP conflict, 403 non-admin
  Departments CRUD                  – list, create (201/409), update (200/404), delete (204/404)
  Skills CRUD                       – list, create (201/409), update (200/404), delete (204/404)
  Companies CRUD                    – list, create (201/409), update (200/404), delete (204/404)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from tests.conftest import (ADMIN_USER_ID, COMPANY_ID, DEPT_ID, NOW, SKILL_ID,
                            STUDENT_USER_ID)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers – shared fake response objects
# ─────────────────────────────────────────────────────────────────────────────


def _dept_item():
    return {
        "id": str(DEPT_ID),
        "code": "ILK",
        "name": "Ilmu Komputer",
        "faculty": "FMIPA",
    }


def _skill_item():
    return {
        "id": str(SKILL_ID),
        "name": "Python",
        "category": "Programming",
    }


def _company_item():
    return {
        "id": str(COMPANY_ID),
        "name": "PT Teknologi Nusantara",
        "industry": "IT/Technology",
        "website_url": "https://teknusantara.id",
        "address": "Jakarta",
        "created_at": NOW.isoformat(),
    }


def _user_response():
    return {
        "id": str(STUDENT_USER_ID),
        "email": "student@ipb.ac.id",
        "role": "STUDENT",
        "is_active": False,
        "created_at": NOW.isoformat(),
        "last_login_at": None,
    }


def _admin_profile():
    return {
        "user_id": str(ADMIN_USER_ID),
        "email": "admin@ipb.ac.id",
        "role": "ADMIN",
        "is_active": True,
        "full_name": "Admin One",
        "unit_name": "Direktorat IT",
        "nip": "198001012010011001",
        "last_login_at": None,
        "updated_at": NOW.isoformat(),
    }


# ════════════════════════════════════════════════════════════════════════════
#  Toggle User Active
# ════════════════════════════════════════════════════════════════════════════


def test_toggle_user_active_success(client_as_admin):
    from app_backend.schemas.user import UserResponse

    fake_user = UserResponse(
        id=STUDENT_USER_ID,
        email="student@ipb.ac.id",
        role="STUDENT",
        is_active=False,
        created_at=NOW,
        last_login_at=None,
    )

    with patch(
        "app_backend.routers.api.admin.toggle_user_active_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(got_error=lambda: False, user=fake_user)
        resp = client_as_admin.patch(
            f"/api/v1/admin/users/{STUDENT_USER_ID}/toggle-active"
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(STUDENT_USER_ID)
    assert data["is_active"] is False


def test_toggle_user_active_not_found(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.toggle_user_active_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(
            got_error=lambda: True,
            error_message="User tidak ditemukan",
        )
        resp = client_as_admin.patch(
            f"/api/v1/admin/users/{STUDENT_USER_ID}/toggle-active"
        )

    assert resp.status_code == 404
    assert "tidak ditemukan" in resp.json()["detail"]


def test_toggle_user_active_forbidden_for_student(client_as_student):
    resp = client_as_student.patch(
        f"/api/v1/admin/users/{STUDENT_USER_ID}/toggle-active"
    )
    assert resp.status_code == 403


# ════════════════════════════════════════════════════════════════════════════
#  Admin Profile GET
# ════════════════════════════════════════════════════════════════════════════


def test_get_admin_profile_success(client_as_admin, mock_session):
    """Profile ditemukan → 200 dengan data lengkap."""
    from app_backend.models.profiles_admin import \
        ProfilesAdmin as ProfilesAdminModel

    fake_profile = MagicMock(spec=ProfilesAdminModel)
    fake_profile.full_name = "Admin One"
    fake_profile.unit_name = "Direktorat IT"
    fake_profile.nip = "198001012010011001"
    fake_profile.updated_at = NOW

    mock_session.query.return_value.filter.return_value.first.return_value = (
        fake_profile
    )

    resp = client_as_admin.get("/api/v1/admin/profile/me")

    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Admin One"
    assert data["nip"] == "198001012010011001"
    assert data["role"] == "ADMIN"


def test_get_admin_profile_not_found(client_as_admin, mock_session):
    mock_session.query.return_value.filter.return_value.first.return_value = None
    resp = client_as_admin.get("/api/v1/admin/profile/me")
    assert resp.status_code == 404
    assert "tidak ditemukan" in resp.json()["detail"]


def test_get_admin_profile_forbidden_for_student(client_as_student):
    resp = client_as_student.get("/api/v1/admin/profile/me")
    assert resp.status_code == 403


# ════════════════════════════════════════════════════════════════════════════
#  Admin Profile PATCH
# ════════════════════════════════════════════════════════════════════════════


def test_update_admin_profile_success(client_as_admin, mock_session):
    from app_backend.models.profiles_admin import \
        ProfilesAdmin as ProfilesAdminModel

    fake_profile = MagicMock(spec=ProfilesAdminModel)
    fake_profile.full_name = "Admin Updated"
    fake_profile.unit_name = "Rektorat"
    fake_profile.nip = "198001012010011999"
    fake_profile.updated_at = NOW

    mock_session.query.return_value.filter.return_value.first.return_value = (
        fake_profile
    )
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    resp = client_as_admin.patch(
        "/api/v1/admin/profile/me",
        json={"full_name": "Admin Updated", "unit_name": "Rektorat"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Admin Updated"


def test_update_admin_profile_nip_conflict(client_as_admin, mock_session):
    from sqlalchemy.exc import IntegrityError

    from app_backend.models.profiles_admin import \
        ProfilesAdmin as ProfilesAdminModel

    fake_profile = MagicMock(spec=ProfilesAdminModel)
    mock_session.query.return_value.filter.return_value.first.return_value = (
        fake_profile
    )
    mock_session.commit.side_effect = IntegrityError(
        "UNIQUE constraint failed", params={}, orig=Exception()
    )

    resp = client_as_admin.patch(
        "/api/v1/admin/profile/me", json={"nip": "198001012010011001"}
    )

    assert resp.status_code == 409
    assert "sudah digunakan" in resp.json()["detail"]


def test_update_admin_profile_not_found(client_as_admin, mock_session):
    mock_session.query.return_value.filter.return_value.first.return_value = None
    resp = client_as_admin.patch(
        "/api/v1/admin/profile/me", json={"full_name": "Siapa"}
    )
    assert resp.status_code == 404


def test_update_admin_profile_forbidden_for_student(client_as_student):
    resp = client_as_student.patch(
        "/api/v1/admin/profile/me", json={"full_name": "Hacked"}
    )
    assert resp.status_code == 403


# ════════════════════════════════════════════════════════════════════════════
#  Departments CRUD
# ════════════════════════════════════════════════════════════════════════════


def test_list_departments(client_as_admin):
    from app_backend.schemas.admin import DepartmentResponse

    fake = DepartmentResponse(
        id=DEPT_ID, code="ILK", name="Ilmu Komputer", faculty="FMIPA"
    )
    with patch(
        "app_backend.routers.api.admin.list_departments_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(items=[fake])
        resp = client_as_admin.get("/api/v1/admin/departments")

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["code"] == "ILK"


def test_list_departments_empty(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.list_departments_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(items=[])
        resp = client_as_admin.get("/api/v1/admin/departments")

    assert resp.status_code == 200
    assert resp.json() == []


def test_create_department_success(client_as_admin):
    from app_backend.schemas.admin import DepartmentResponse

    fake = DepartmentResponse(
        id=DEPT_ID, code="ILK", name="Ilmu Komputer", faculty="FMIPA"
    )
    with patch(
        "app_backend.routers.api.admin.create_department_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(got_error=lambda: False, item=fake)
        resp = client_as_admin.post(
            "/api/v1/admin/departments",
            json={"code": "ILK", "name": "Ilmu Komputer", "faculty": "FMIPA"},
        )

    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == "ILK"
    assert data["id"] == str(DEPT_ID)


def test_create_department_conflict(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.create_department_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Prodi dengan kode 'ILK' sudah ada",
        )
        resp = client_as_admin.post(
            "/api/v1/admin/departments",
            json={"code": "ILK", "name": "Ilmu Komputer", "faculty": "FMIPA"},
        )

    assert resp.status_code == 409


def test_create_department_missing_field(client_as_admin):
    resp = client_as_admin.post("/api/v1/admin/departments", json={"code": "ILK"})
    assert resp.status_code == 422


def test_update_department_success(client_as_admin):
    from app_backend.schemas.admin import DepartmentResponse

    fake = DepartmentResponse(
        id=DEPT_ID, code="ILK", name="Ilmu Komputer Updated", faculty="FMIPA"
    )
    with patch(
        "app_backend.routers.api.admin.update_department_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(got_error=lambda: False, item=fake)
        resp = client_as_admin.patch(
            f"/api/v1/admin/departments/{DEPT_ID}",
            json={"name": "Ilmu Komputer Updated"},
        )

    assert resp.status_code == 200
    assert resp.json()["name"] == "Ilmu Komputer Updated"


def test_update_department_not_found(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.update_department_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Prodi tidak ditemukan",
        )
        resp = client_as_admin.patch(
            f"/api/v1/admin/departments/{DEPT_ID}", json={"name": "X"}
        )

    assert resp.status_code == 404


def test_delete_department_success(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.delete_department_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(got_error=lambda: False)
        resp = client_as_admin.delete(f"/api/v1/admin/departments/{DEPT_ID}")

    assert resp.status_code == 204


def test_delete_department_not_found(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.delete_department_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Prodi tidak ditemukan",
        )
        resp = client_as_admin.delete(f"/api/v1/admin/departments/{DEPT_ID}")

    assert resp.status_code == 404


def test_department_endpoints_forbidden_for_student(client_as_student):
    resp = client_as_student.get("/api/v1/admin/departments")
    assert resp.status_code == 403


# ════════════════════════════════════════════════════════════════════════════
#  Skills CRUD
# ════════════════════════════════════════════════════════════════════════════


def test_list_skills(client_as_admin):
    from app_backend.schemas.admin import SkillResponse

    fake = SkillResponse(id=SKILL_ID, name="Python", category="Programming")
    with patch(
        "app_backend.routers.api.admin.list_skills_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(items=[fake])
        resp = client_as_admin.get("/api/v1/admin/skills")

    assert resp.status_code == 200
    assert resp.json()[0]["name"] == "Python"


def test_create_skill_success(client_as_admin):
    from app_backend.schemas.admin import SkillResponse

    fake = SkillResponse(id=SKILL_ID, name="Python", category="Programming")
    with patch(
        "app_backend.routers.api.admin.create_skill_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(got_error=lambda: False, item=fake)
        resp = client_as_admin.post(
            "/api/v1/admin/skills", json={"name": "Python", "category": "Programming"}
        )

    assert resp.status_code == 201
    assert resp.json()["name"] == "Python"


def test_create_skill_conflict(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.create_skill_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Skill 'Python' sudah terdaftar",
        )
        resp = client_as_admin.post("/api/v1/admin/skills", json={"name": "Python"})

    assert resp.status_code == 409


def test_create_skill_missing_name(client_as_admin):
    resp = client_as_admin.post(
        "/api/v1/admin/skills", json={"category": "Programming"}
    )
    assert resp.status_code == 422


def test_update_skill_success(client_as_admin):
    from app_backend.schemas.admin import SkillResponse

    fake = SkillResponse(id=SKILL_ID, name="Python 3", category="Programming")
    with patch(
        "app_backend.routers.api.admin.update_skill_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(got_error=lambda: False, item=fake)
        resp = client_as_admin.patch(
            f"/api/v1/admin/skills/{SKILL_ID}", json={"name": "Python 3"}
        )

    assert resp.status_code == 200
    assert resp.json()["name"] == "Python 3"


def test_update_skill_not_found(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.update_skill_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Skill tidak ditemukan",
        )
        resp = client_as_admin.patch(
            f"/api/v1/admin/skills/{SKILL_ID}", json={"name": "X"}
        )

    assert resp.status_code == 404


def test_delete_skill_success(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.delete_skill_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(got_error=lambda: False)
        resp = client_as_admin.delete(f"/api/v1/admin/skills/{SKILL_ID}")

    assert resp.status_code == 204


def test_delete_skill_not_found(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.delete_skill_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Skill tidak ditemukan",
        )
        resp = client_as_admin.delete(f"/api/v1/admin/skills/{SKILL_ID}")

    assert resp.status_code == 404


def test_skill_endpoints_forbidden_for_student(client_as_student):
    resp = client_as_student.get("/api/v1/admin/skills")
    assert resp.status_code == 403


# ════════════════════════════════════════════════════════════════════════════
#  Companies CRUD
# ════════════════════════════════════════════════════════════════════════════


def test_list_companies(client_as_admin):
    from app_backend.schemas.admin import CompanyResponse

    fake = CompanyResponse(
        id=COMPANY_ID,
        name="PT Teknologi Nusantara",
        industry="IT/Technology",
        website_url="https://teknusantara.id",
        address="Jakarta",
        created_at=NOW,
    )
    with patch(
        "app_backend.routers.api.admin.list_companies_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(items=[fake])
        resp = client_as_admin.get("/api/v1/admin/companies")

    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["name"] == "PT Teknologi Nusantara"


def test_create_company_success(client_as_admin):
    from app_backend.schemas.admin import CompanyResponse

    fake = CompanyResponse(
        id=COMPANY_ID,
        name="PT Teknologi Nusantara",
        industry="IT/Technology",
        created_at=NOW,
    )
    with patch(
        "app_backend.routers.api.admin.create_company_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(got_error=lambda: False, item=fake)
        resp = client_as_admin.post(
            "/api/v1/admin/companies",
            json={"name": "PT Teknologi Nusantara", "industry": "IT/Technology"},
        )

    assert resp.status_code == 201
    assert resp.json()["name"] == "PT Teknologi Nusantara"


def test_create_company_conflict(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.create_company_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Perusahaan 'PT Teknologi Nusantara' sudah terdaftar",
        )
        resp = client_as_admin.post(
            "/api/v1/admin/companies", json={"name": "PT Teknologi Nusantara"}
        )

    assert resp.status_code == 409


def test_create_company_missing_name(client_as_admin):
    resp = client_as_admin.post("/api/v1/admin/companies", json={"industry": "IT"})
    assert resp.status_code == 422


def test_update_company_success(client_as_admin):
    from app_backend.schemas.admin import CompanyResponse

    fake = CompanyResponse(
        id=COMPANY_ID,
        name="PT Teknologi Nusantara Updated",
        industry="IT/Technology",
        created_at=NOW,
    )
    with patch(
        "app_backend.routers.api.admin.update_company_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(got_error=lambda: False, item=fake)
        resp = client_as_admin.patch(
            f"/api/v1/admin/companies/{COMPANY_ID}",
            json={"name": "PT Teknologi Nusantara Updated"},
        )

    assert resp.status_code == 200
    assert resp.json()["name"] == "PT Teknologi Nusantara Updated"


def test_update_company_not_found(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.update_company_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Perusahaan tidak ditemukan",
        )
        resp = client_as_admin.patch(
            f"/api/v1/admin/companies/{COMPANY_ID}", json={"name": "X"}
        )

    assert resp.status_code == 404


def test_update_company_conflict(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.update_company_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Nama perusahaan sudah digunakan",
        )
        resp = client_as_admin.patch(
            f"/api/v1/admin/companies/{COMPANY_ID}", json={"name": "Duplikat"}
        )

    assert resp.status_code == 409


def test_delete_company_success(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.delete_company_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(got_error=lambda: False)
        resp = client_as_admin.delete(f"/api/v1/admin/companies/{COMPANY_ID}")

    assert resp.status_code == 204


def test_delete_company_not_found(client_as_admin):
    with patch(
        "app_backend.routers.api.admin.delete_company_command_handler"
    ) as mock_h:
        mock_h.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Perusahaan tidak ditemukan",
        )
        resp = client_as_admin.delete(f"/api/v1/admin/companies/{COMPANY_ID}")

    assert resp.status_code == 404


def test_company_endpoints_forbidden_for_student(client_as_student):
    resp = client_as_student.get("/api/v1/admin/companies")
    assert resp.status_code == 403


def test_company_endpoints_unauthenticated(client_no_auth):
    resp = client_no_auth.get("/api/v1/admin/companies")
    assert resp.status_code == 401

# ════════════════════════════════════════════════════════════════════════════
#  Applications Admin (Phase 4)
# ════════════════════════════════════════════════════════════════════════════

def test_list_pending_verification(client_as_admin):
    with patch("app_backend.routers.api.admin.list_pending_verification_command_handler") as mock_h:
        mock_h.return_value = MagicMock(got_error=lambda: False, items=[])
        resp = client_as_admin.get("/api/v1/admin/applications/pending-verification")
    assert resp.status_code == 200

def test_verify_application_success(client_as_admin):
    with patch("app_backend.routers.api.admin.verify_application_command_handler") as mock_h:
        mock_h.return_value = MagicMock(got_error=lambda: False, placement=MagicMock(id=uuid.uuid4()))
        resp = client_as_admin.post(
            f"/api/v1/admin/applications/{uuid.uuid4()}/verify",
            json={"start_date": "2026-06-01", "end_date": "2026-08-31"}
        )
    assert resp.status_code == 200

def test_reject_application_proof_success(client_as_admin):
    with patch("app_backend.routers.api.admin.reject_application_proof_command_handler") as mock_h:
        from app_backend.schemas.application import ApplicationResponse
        mock_h.return_value = MagicMock(
            got_error=lambda: False,
            application=ApplicationResponse(
                id=uuid.uuid4(),
                vacancy_id=uuid.uuid4(),
                student_id=STUDENT_USER_ID,
                cv_snapshot_url="https://example.com/cv.pdf",
                status="OFFERED"
            )
        )
        resp = client_as_admin.post(
            f"/api/v1/admin/applications/{uuid.uuid4()}/reject-proof",
            json={"reason": "Bukti tidak valid"}
        )
    assert resp.status_code == 200
