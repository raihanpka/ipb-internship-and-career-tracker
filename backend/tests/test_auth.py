"""
Tests: Auth Router          –  POST /api/v1/auth/*

Covers:
  Register Student          – 201 success, 409 email/NIM conflict
  Register Admin            – 201 success (admin token), 403 non-admin, 409 conflict
  Login                     – 200 success, 401 wrong password, 401 inactive account
  Refresh Token             – 200 success, 401 invalid/revoked token
  Logout                    – 204 success (idempotent)
  Password reset request    – 200 generic always
  Password reset            – 200 success, 400 invalid token
  GET /me                   – 200 success
  Health / Root             – sanity checks
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from tests.conftest import ADMIN_USER_ID, NOW, STUDENT_USER_ID

#  Sanity checks


def test_root(client_no_auth):
    resp = client_no_auth.get("/")
    assert resp.status_code == 200
    assert resp.json()["version"] == "1.0.0"


def test_health(client_no_auth):
    resp = client_no_auth.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}


import uuid

STUDENT_PAYLOAD = {
    "email": "mahasiswa@ipb.ac.id",
    "password": "Password123",
    "nim": "G1234567890",
    "full_name": "Windah Basudara",
    "semester": 5,
    "department_id": str(uuid.uuid4()),
}


def _make_user_orm(user_id, email, role):
    """Minimal ORM-like object returned by session.query(Users)."""
    m = MagicMock()
    m.id = user_id
    m.email = email
    m.role = role
    m.is_active = True
    m.last_login_at = NOW
    m.created_at = NOW
    m.updated_at = NOW
    return m


def test_register_student_success(client_no_auth, mock_session):
    # No duplicate found → both .first() return None
    mock_session.query.return_value.filter.return_value.first.return_value = None

    _make_user_orm(STUDENT_USER_ID, STUDENT_PAYLOAD["email"], "STUDENT")
    mock_session.refresh.side_effect = lambda obj: None

    with patch("app_backend.features.auth.auth_service.AuthService.register_student") as mock_method:
        from app_backend.schemas.user import UserResponse

        mock_method.return_value = UserResponse(
            id=STUDENT_USER_ID,
            email=STUDENT_PAYLOAD["email"],
            role="STUDENT",
            is_active=True,
            last_login_at=NOW,
            created_at=NOW,
            updated_at=NOW,
        )
        resp = client_no_auth.post("/api/v1/auth/register/student", json=STUDENT_PAYLOAD)

    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == STUDENT_PAYLOAD["email"]
    assert data["role"] == "STUDENT"


def test_register_student_duplicate_email(client_no_auth):
    with patch("app_backend.features.auth.auth_service.AuthService.register_student") as mock_method:
        mock_method.side_effect = ValueError("Email sudah terdaftar")
        resp = client_no_auth.post("/api/v1/auth/register/student", json=STUDENT_PAYLOAD)

    assert resp.status_code == 409
    assert "Email sudah terdaftar" in resp.json()["detail"]


def test_register_student_duplicate_nim(client_no_auth):
    with patch("app_backend.features.auth.auth_service.AuthService.register_student") as mock_method:
        mock_method.side_effect = ValueError("NIM sudah terdaftar")
        resp = client_no_auth.post("/api/v1/auth/register/student", json=STUDENT_PAYLOAD)

    assert resp.status_code == 409
    assert "NIM sudah terdaftar" in resp.json()["detail"]


def test_register_student_missing_field(client_no_auth):
    payload = {**STUDENT_PAYLOAD}
    del payload["nim"]
    resp = client_no_auth.post("/api/v1/auth/register/student", json=payload)
    assert resp.status_code == 422


#  Register Admin

ADMIN_PAYLOAD = {
    "email": "admin2@ipb.ac.id",
    "password": "Password123",
    "full_name": "Siti Admin",
    "unit_name": "CDA IPB",
    "nip": "198501012010011001",
}


def test_register_admin_success(client_as_admin):
    with patch("app_backend.features.auth.auth_service.AuthService.register_admin") as mock_method:
        from app_backend.schemas.user import UserResponse

        mock_method.return_value = UserResponse(
            id=ADMIN_USER_ID,
            email=ADMIN_PAYLOAD["email"],
            role="ADMIN",
            is_active=True,
            last_login_at=NOW,
            created_at=NOW,
            updated_at=NOW,
        )
        resp = client_as_admin.post("/api/v1/auth/register/admin", json=ADMIN_PAYLOAD)

    assert resp.status_code == 201
    assert resp.json()["role"] == "ADMIN"


def test_register_admin_forbidden_for_student(client_as_student):
    resp = client_as_student.post("/api/v1/auth/register/admin", json=ADMIN_PAYLOAD)
    assert resp.status_code == 403


def test_register_admin_duplicate(client_as_admin):
    with patch("app_backend.features.auth.auth_service.AuthService.register_admin") as mock_method:
        mock_method.side_effect = ValueError("Email sudah terdaftar")
        resp = client_as_admin.post("/api/v1/auth/register/admin", json=ADMIN_PAYLOAD)

    assert resp.status_code == 409


#  Login


def test_login_success(client_no_auth):
    with patch("app_backend.features.auth.auth_service.AuthService.login") as mock_method:
        from app_backend.schemas.user import LoginResponse, UserResponse

        mock_method.return_value = LoginResponse(
            access_token="access.jwt.token",
            refresh_token="refresh.jwt.token",
            token_type="bearer",
            expires_in=1800,
            user=UserResponse(
                id=STUDENT_USER_ID,
                email="student@ipb.ac.id",
                role="STUDENT",
                is_active=True,
                last_login_at=NOW,
                created_at=NOW,
                updated_at=NOW,
            ),
        )
        resp = client_no_auth.post(
            "/api/v1/auth/login",
            json={"email": "student@ipb.ac.id", "password": "Password123"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["access_token"] == "access.jwt.token"
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "student@ipb.ac.id"


def test_login_wrong_password(client_no_auth):
    with patch("app_backend.features.auth.auth_service.AuthService.login") as mock_method:
        mock_method.side_effect = ValueError("Email atau password salah")
        resp = client_no_auth.post(
            "/api/v1/auth/login",
            json={"email": "student@ipb.ac.id", "password": "wrong"},
        )

    assert resp.status_code == 401
    assert "WWW-Authenticate" in resp.headers


def test_login_inactive_account(client_no_auth):
    with patch("app_backend.features.auth.auth_service.AuthService.login") as mock_method:
        mock_method.side_effect = PermissionError("Akun dinonaktifkan. Hubungi admin.")
        resp = client_no_auth.post(
            "/api/v1/auth/login",
            json={"email": "student@ipb.ac.id", "password": "Password123"},
        )

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Akun dinonaktifkan. Hubungi admin."


def test_login_unverified_account(client_no_auth):
    with patch("app_backend.features.auth.auth_service.AuthService.login") as mock_method:
        mock_method.side_effect = PermissionError("Silakan verifikasi email Anda terlebih dahulu.")
        resp = client_no_auth.post(
            "/api/v1/auth/login",
            json={"email": "student@ipb.ac.id", "password": "Password123"},
        )

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Silakan verifikasi email Anda terlebih dahulu."


#  Refresh Token


def test_refresh_token_success(client_no_auth):
    with patch("app_backend.routers.api.auth.refresh_token_command_handler") as mock_handler:
        from app_backend.schemas.user import LoginResponse, UserResponse

        mock_handler.return_value = MagicMock(
            got_error=lambda: False,
            data=LoginResponse(
                access_token="new.access.token",
                refresh_token="new.refresh.token",
                token_type="bearer",
                expires_in=1800,
                user=UserResponse(
                    id=STUDENT_USER_ID,
                    email="student@ipb.ac.id",
                    role="STUDENT",
                    is_active=True,
                    last_login_at=NOW,
                    created_at=NOW,
                    updated_at=NOW,
                ),
            ),
        )
        resp = client_no_auth.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": "old.refresh.token"},
        )

    assert resp.status_code == 200
    assert resp.json()["access_token"] == "new.access.token"


def test_refresh_token_invalid(client_no_auth):
    with patch("app_backend.routers.api.auth.refresh_token_command_handler") as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Refresh token tidak valid atau sudah di-revoke",
        )
        resp = client_no_auth.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": "bad.token"},
        )

    assert resp.status_code == 401


#  Logout


def test_logout_success(client_no_auth):
    with patch("app_backend.routers.api.auth.logout_command_handler") as mock_handler:
        mock_handler.return_value = MagicMock(success=True)
        resp = client_no_auth.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "some.refresh.token"},
        )

    assert resp.status_code == 204


def test_logout_idempotent_already_revoked(client_no_auth):
    """Logout pada token yang sudah di-revoke tetap 204."""
    with patch("app_backend.routers.api.auth.logout_command_handler") as mock_handler:
        mock_handler.return_value = MagicMock(success=True)
        resp = client_no_auth.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "already.revoked.token"},
        )

    assert resp.status_code == 204


#  Password Reset


def test_reset_request_always_200(client_no_auth):
    """Endpoint selalu 200 untuk mencegah email enumeration."""
    with patch("app_backend.routers.api.auth.request_reset_password_command_handler") as mock_handler:
        mock_handler.return_value = MagicMock(
            message="Jika email terdaftar, instruksi reset password akan dikirim ke email Anda",
            token="raw_dev_token_xyz",
        )
        resp = client_no_auth.post(
            "/api/v1/auth/password/reset-request",
            json={"email": "anyone@ipb.ac.id"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data


def test_reset_request_unregistered_email_still_200(client_no_auth):
    with patch("app_backend.routers.api.auth.request_reset_password_command_handler") as mock_handler:
        mock_handler.return_value = MagicMock(
            message="Jika email terdaftar, instruksi reset password akan dikirim ke email Anda",
            token=None,
        )
        resp = client_no_auth.post(
            "/api/v1/auth/password/reset-request",
            json={"email": "nobody@nowhere.com"},
        )

    assert resp.status_code == 200


def test_reset_password_success(client_no_auth):
    with patch("app_backend.routers.api.auth.reset_password_command_handler") as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: False,
            message="Password berhasil direset",
        )
        resp = client_no_auth.post(
            "/api/v1/auth/password/reset",
            json={"token": "valid_one_time_token", "new_password": "NewPass456"},
        )

    assert resp.status_code == 200
    assert resp.json()["message"] == "Password berhasil direset"


def test_reset_password_invalid_token(client_no_auth):
    with patch("app_backend.routers.api.auth.reset_password_command_handler") as mock_handler:
        mock_handler.return_value = MagicMock(
            got_error=lambda: True,
            error_message="Token tidak valid atau sudah expired",
        )
        resp = client_no_auth.post(
            "/api/v1/auth/password/reset",
            json={"token": "expired_token", "new_password": "NewPass456"},
        )

    assert resp.status_code == 400
    assert "Token tidak valid" in resp.json()["detail"]


#  GET /me


def test_get_me_student(client_as_student):
    resp = client_as_student.get("/api/v1/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "student@ipb.ac.id"
    assert data["role"] == "STUDENT"


def test_get_me_admin(client_as_admin):
    resp = client_as_admin.get("/api/v1/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "admin@ipb.ac.id"
    assert data["role"] == "ADMIN"


def test_get_me_unauthenticated(client_no_auth):
    resp = client_no_auth.get("/api/v1/auth/me")
    assert resp.status_code == 401  # HTTPBearer returns 401 when no token


#  Check Availability


def test_check_availability_available(client_no_auth):
    with patch("app_backend.features.auth.auth_service.AuthService.check_availability") as mock_method:
        mock_method.return_value = {"available": True, "source": "db"}
        resp = client_no_auth.get("/api/v1/auth/register/check-availability?identifier=newstudent")

    assert resp.status_code == 200
    assert resp.json() == {"available": True, "source": "db"}


def test_check_availability_too_short(client_no_auth):
    resp = client_no_auth.get("/api/v1/auth/register/check-availability?identifier=ab")
    assert resp.status_code == 200
    assert resp.json()["available"] is False
    assert "minimal 3 karakter" in resp.json()["reason"]


def test_check_availability_invalid_domain(client_no_auth):
    resp = client_no_auth.get("/api/v1/auth/register/check-availability?identifier=student@gmail.com")
    assert resp.status_code == 200
    assert resp.json()["available"] is False
    assert "Domain email harus @ipb.ac.id" in resp.json()["reason"]
