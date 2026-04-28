"""
Dependencies untuk Authentication & Authorization.
Berisi FastAPI Depends yang digunakan pada protected routes.
"""

import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app_backend.domain.student import Student as DomainStudent
from app_backend.domain.user import User as DomainUser
from app_backend.models.profiles_student import ProfilesStudent
from app_backend.models.users import Users
from app_backend.shared.database import get_session
from app_backend.shared.security import decode_access_token, verify_token_type

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> DomainUser:
    """Decode JWT access token dan kembalikan domain User."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kredensial tidak valid",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(credentials.credentials)
    if not payload or not verify_token_type(payload, "access"):
        raise credentials_exception

    user_id_str: Optional[str] = payload.get("user_id")
    try:
        user_id = uuid.UUID(user_id_str)
    except (TypeError, ValueError):
        raise credentials_exception

    user = session.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user.to_domain()


async def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> DomainStudent:
    """Decode JWT access token dan kembalikan domain Student."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kredensial tidak valid",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(credentials.credentials)
    if not payload or not verify_token_type(payload, "access"):
        raise credentials_exception

    user_id_str: Optional[str] = payload.get("user_id")
    try:
        user_id = uuid.UUID(user_id_str)
    except (TypeError, ValueError):
        raise credentials_exception

    # Get user and check role
    user = session.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise credentials_exception

    if user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Hanya STUDENT.",
        )

    # Get student profile
    profile = session.query(ProfilesStudent).filter(ProfilesStudent.user_id == user_id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil mahasiswa tidak ditemukan",
        )

    return DomainStudent(
        user_id=profile.user_id,
        nim=profile.nim,
        full_name=profile.full_name,
        semester=profile.semester,
        department_id=profile.department_id,
        gpa=profile.gpa,
        phone_number=profile.phone_number,
        linkedin_url=profile.linkedin_url,
        cv_url=profile.cv_url,
        is_mbkm_eligible=profile.is_mbkm_eligible if profile.is_mbkm_eligible else False,
        updated_at=profile.updated_at,
    )


async def get_current_active_user(
    current_user: DomainUser = Depends(get_current_user),
) -> DomainUser:
    """Pastikan user aktif."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun dinonaktifkan. Hubungi admin.",
        )
    return current_user


async def require_admin(
    current_user: DomainUser = Depends(get_current_active_user),
) -> DomainUser:
    """Hanya ADMIN yang boleh akses endpoint ini."""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Hanya ADMIN.",
        )
    return current_user


async def require_student(
    current_user: DomainUser = Depends(get_current_active_user),
) -> DomainUser:
    """Hanya STUDENT yang boleh akses endpoint ini."""
    if not current_user.is_student():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Hanya STUDENT.",
        )
    return current_user


async def get_current_active_student(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> DomainStudent:
    """
    Pastikan student profile aktif.
    Menggunakan dependency injection untuk session agar tidak ada leak.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kredensial tidak valid",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(credentials.credentials)
    if not payload or not verify_token_type(payload, "access"):
        raise credentials_exception

    user_id_str: Optional[str] = payload.get("user_id")
    try:
        user_id = uuid.UUID(user_id_str)
    except (TypeError, ValueError):
        raise credentials_exception

    # Get user and check if active
    user = session.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun dinonaktifkan. Hubungi admin.",
        )

    if user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Hanya STUDENT.",
        )

    # Get student profile
    profile = session.query(ProfilesStudent).filter(ProfilesStudent.user_id == user_id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil mahasiswa tidak ditemukan",
        )

    return DomainStudent(
        user_id=profile.user_id,
        nim=profile.nim,
        full_name=profile.full_name,
        semester=profile.semester,
        department_id=profile.department_id,
        gpa=profile.gpa,
        phone_number=profile.phone_number,
        linkedin_url=profile.linkedin_url,
        cv_url=profile.cv_url,
        is_mbkm_eligible=profile.is_mbkm_eligible if profile.is_mbkm_eligible else False,
        updated_at=profile.updated_at,
    )


def require_roles(roles: list[str]):
    """
    Factory dependency untuk multi-role RBAC.
    Contoh: Depends(require_roles(['ADMIN', 'STUDENT']))
    """

    async def role_checker(
        current_user: DomainUser = Depends(get_current_active_user),
    ) -> DomainUser:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses ditolak. Role yang diizinkan: {', '.join(roles)}",
            )
        return current_user

    return role_checker
