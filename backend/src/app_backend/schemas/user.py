import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# Shared


class UserRole(str, Enum):
    """Role user sesuai DB enum auth.user_role_enum."""

    ADMIN = "ADMIN"
    STUDENT = "STUDENT"


def _validate_password_strength(v: str) -> str:
    """Validasi kekuatan password: min 8 char, ada angka, huruf besar & kecil."""
    if not any(c.isdigit() for c in v):
        raise ValueError("Password harus mengandung minimal satu angka")
    if not any(c.isupper() for c in v):
        raise ValueError("Password harus mengandung minimal satu huruf besar")
    if not any(c.islower() for c in v):
        raise ValueError("Password harus mengandung minimal satu huruf kecil")
    return v


# Registration


class StudentRegister(BaseModel):
    """Payload registrasi mahasiswa baru. Role otomatis STUDENT."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    nim: str = Field(..., min_length=6, max_length=20)
    full_name: str = Field(..., min_length=3, max_length=150)
    semester: int = Field(..., ge=1, le=14)
    department_id: uuid.UUID

    @field_validator("email")
    @classmethod
    def validate_ipb_domain(cls, v: str) -> str:
        domain = v.split("@")[-1].lower()
        if domain not in ("ipb.ac.id", "apps.ipb.ac.id"):
            raise ValueError("Hanya diperbolehkan mendaftar dengan email domain @ipb.ac.id atau @apps.ipb.ac.id")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)


class AdminRegister(BaseModel):
    """Payload registrasi admin / fasilitator CDA. Role otomatis ADMIN."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=3, max_length=150)
    unit_name: str = Field(..., min_length=2, max_length=150, description="Unit kerja (contoh: CDA IPB)")
    nip: Optional[str] = Field(None, max_length=30, description="NIP (opsional)")

    @field_validator("email")
    @classmethod
    def validate_ipb_domain(cls, v: str) -> str:
        domain = v.split("@")[-1].lower()
        if domain not in ("ipb.ac.id", "apps.ipb.ac.id"):
            raise ValueError("Hanya diperbolehkan mendaftar dengan email domain @ipb.ac.id atau @apps.ipb.ac.id")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)


# Login


class UserLogin(BaseModel):
    """Payload login dengan email + password."""

    email: str
    password: str


# Tokens


class TokenData(BaseModel):
    """Isi payload JWT access token."""

    user_id: Optional[uuid.UUID] = None
    email: Optional[str] = None
    role: Optional[str] = None


class Token(BaseModel):
    """Response login: access token saja (backward-compat)."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Durasi validitas token dalam detik")


class TokenWithRefresh(BaseModel):
    """Response login lengkap: access + refresh token."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Durasi validitas access token dalam detik")


class RefreshTokenRequest(BaseModel):
    """Payload untuk rotate refresh token."""

    refresh_token: str = Field(..., description="Refresh token yang valid dan belum di-revoke")


class LogoutRequest(BaseModel):
    """Payload logout – revoke satu sesi (refresh token tertentu)."""

    refresh_token: str = Field(..., description="Refresh token sesi yang akan di-revoke")


# Password reset


class RequestResetPassword(BaseModel):
    """Req untuk meminta link reset password dikirim ke email."""

    email: EmailStr = Field(..., description="Email akun yang akan direset")


class ResetPassword(BaseModel):
    """Payload reset password menggunakan action token."""

    token: str = Field(..., description="Token reset password dari email")
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)


class ChangePassword(BaseModel):
    """Payload ganti password untuk user yang sudah login."""

    current_password: str = Field(..., description="Password saat ini")
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)


class ProfileUpdate(BaseModel):
    """Payload untuk update data profil."""

    full_name: Optional[str] = Field(None, min_length=3, max_length=150)
    semester: Optional[int] = Field(None, ge=1, le=14)
    nim: Optional[str] = Field(None, max_length=20)
    phone_number: Optional[str] = Field(None, max_length=20)
    linkedin_url: Optional[str] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    department_id: Optional[uuid.UUID] = None
    cv_url: Optional[str] = None


# Response


class UserResponse(BaseModel):
    """Response data user (tidak ekspos password_hash)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    full_name: Optional[str] = None
    nim: Optional[str] = None
    semester: Optional[int] = None
    unit_name: Optional[str] = None
    phone_number: Optional[str] = None
    linkedin_url: Optional[str] = None
    cv_url: Optional[str] = None
    avatar_url: Optional[str] = None
    gpa: Optional[float] = None
    department_id: Optional[uuid.UUID] = None
    department_name: Optional[str] = None
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LoginResponse(BaseModel):
    """Response login lengkap: token + user info."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
