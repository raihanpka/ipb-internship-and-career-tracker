"""
Auth Router – API endpoints untuk authentication & session management.

Endpoints:
  POST /register/student    – Registrasi mahasiswa
  POST /register/admin      – Registrasi admin/fasilitator (protected: admin only)
  POST /login               – Login, kembalikan access + refresh token
  POST /refresh-token       – Token rotation (stateful)
  POST /logout              – Revoke refresh token (device logout)
  POST /password/reset-request – Minta link reset password via email
  POST /password/reset         – Reset password dengan action token
  GET  /me                     – Info user yang sedang login
"""

from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request

from app_backend.conf.settings import settings
from app_backend.domain.user import User as DomainUser
from app_backend.features.auth.login_user import (LoginUserCommand,
                                                  login_user_command_handler)
from app_backend.features.auth.logout import (LogoutCommand,
                                              logout_command_handler)
from app_backend.features.auth.refresh_token import (
    RefreshTokenCommand, refresh_token_command_handler)
from app_backend.features.auth.register_admin import (
    RegisterAdminCommand, register_admin_command_handler)
from app_backend.features.auth.register_student import (
    RegisterStudentCommand, register_student_command_handler)
from app_backend.features.auth.reset_password import (
    RequestResetPasswordCommand, ResetPasswordCommand,
    request_reset_password_command_handler, reset_password_command_handler)
from app_backend.schemas.user import (AdminRegister, LoginResponse,
                                      LogoutRequest, RefreshTokenRequest,
                                      RequestResetPassword, ResetPassword,
                                      StudentRegister, UserLogin, UserResponse)
from app_backend.shared.database import get_session
from app_backend.shared.dependencies import (get_current_active_user,
                                             require_admin)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["authentication"],
)


# ─────────────────────────────────────────────
# Registration
# ─────────────────────────────────────────────


@router.post(
    "/register/student",
    response_model=UserResponse,
    status_code=HTTPStatus.CREATED,
    summary="Registrasi mahasiswa baru",
)
async def register_student(
    student_data: StudentRegister,
    session=Depends(get_session),
) -> UserResponse:
    """
    Daftarkan mahasiswa baru. Role otomatis **STUDENT**.

    - **email**: Alamat email unik
    - **password**: Min 8 char, harus ada angka + huruf besar + kecil
    - **nim**: NIM unik (6–20 karakter)
    - **full_name**: Nama lengkap
    - **semester**: Semester aktif (1–14)
    """
    result = register_student_command_handler(
        command=RegisterStudentCommand(payload=student_data),
        session=session,
    )
    if result.got_error():
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail=result.error_message
        )
    return result.user


@router.post(
    "/register/admin",
    response_model=UserResponse,
    status_code=HTTPStatus.CREATED,
    summary="Registrasi admin / fasilitator",
)
async def register_admin(
    admin_data: AdminRegister,
    session=Depends(get_session),
    _: DomainUser = Depends(require_admin),  # hanya ADMIN yang bisa buat admin baru
) -> UserResponse:
    """
    Daftarkan fasilitator/admin baru. Role otomatis **ADMIN**.
    Endpoint ini hanya dapat dipanggil oleh admin yang sudah login.

    - **email**: Alamat email unik
    - **password**: Min 8 char, harus ada angka + huruf besar + kecil
    - **full_name**: Nama lengkap
    - **unit_name**: Unit kerja (contoh: CDA IPB)
    - **nip**: NIP (opsional, harus unik jika diisi)
    """
    result = register_admin_command_handler(
        command=RegisterAdminCommand(payload=admin_data),
        session=session,
    )
    if result.got_error():
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail=result.error_message
        )
    return result.user


# ─────────────────────────────────────────────
# Session management
# ─────────────────────────────────────────────


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login – dapatkan access + refresh token",
)
async def login(
    credentials: UserLogin,
    request: Request,
    session=Depends(get_session),
) -> LoginResponse:
    """
    Autentikasi email + password.
    Mengembalikan **access token** (stateless JWT) + **refresh token** (disimpan di DB).
    """
    ip_address: Optional[str] = request.client.host if request.client else None
    user_agent: Optional[str] = request.headers.get("user-agent")

    result = login_user_command_handler(
        command=LoginUserCommand(
            payload=credentials,
            device_info=user_agent,
            ip_address=ip_address,
        ),
        session=session,
    )
    if result.got_error():
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=result.error_message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result.data


@router.post(
    "/refresh-token",
    response_model=LoginResponse,
    summary="Rotate refresh token – terbitkan token baru",
)
async def refresh_token(
    request_body: RefreshTokenRequest,
    request: Request,
    session=Depends(get_session),
) -> LoginResponse:
    """
    Token rotation: validasi refresh token di DB, revoke yang lama,
    dan terbitkan access token + refresh token baru.
    """
    ip_address: Optional[str] = request.client.host if request.client else None
    user_agent: Optional[str] = request.headers.get("user-agent")

    result = refresh_token_command_handler(
        command=RefreshTokenCommand(
            payload=request_body,
            device_info=user_agent,
            ip_address=ip_address,
        ),
        session=session,
    )
    if result.got_error():
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=result.error_message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result.data


@router.post(
    "/logout",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Logout – revoke refresh token sesi ini",
)
async def logout(
    request_body: LogoutRequest,
    session=Depends(get_session),
) -> None:
    """
    Revoke refresh token yang diberikan (device logout).
    Bersifat idempotent: logout ganda tidak menyebabkan error.
    """
    logout_command_handler(
        command=LogoutCommand(payload=request_body),
        session=session,
    )


# ─────────────────────────────────────────────
# Password reset
# ─────────────────────────────────────────────


@router.post(
    "/password/reset-request",
    status_code=HTTPStatus.OK,
    summary="Minta link reset password",
)
async def request_password_reset(
    request: RequestResetPassword,
    session=Depends(get_session),
) -> dict:
    """
    Kirim token reset password ke email terdaftar.
    Selalu mengembalikan respons generik untuk mencegah email enumeration.

    > **DEV**: Field `reset_token` hanya dikembalikan di mode development.
    > Di production, token dikirim via email dan tidak ada di response.
    """
    result = request_reset_password_command_handler(
        command=RequestResetPasswordCommand(payload=request),
        session=session,
    )
    response: dict = {"message": result.message}

    # Hanya kembalikan token di development mode
    if settings.is_development and result.token:
        response["reset_token"] = result.token

    return response


@router.post(
    "/password/reset",
    status_code=HTTPStatus.OK,
    summary="Reset password dengan action token",
)
async def reset_password(
    request: ResetPassword,
    session=Depends(get_session),
) -> dict:
    """
    Reset password menggunakan token yang diterima dari email.
    Token bersifat one-time use dan akan dinonaktifkan setelah dipakai.
    """
    result = reset_password_command_handler(
        command=ResetPasswordCommand(payload=request),
        session=session,
    )
    if result.got_error():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=result.error_message,
        )
    return {"message": result.message}


# ─────────────────────────────────────────────
# Current user info
# ─────────────────────────────────────────────


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Info user yang sedang login",
)
async def get_me(
    current_user: DomainUser = Depends(get_current_active_user),
) -> UserResponse:
    """Kembalikan data profil user berdasarkan JWT access token."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )
