"""
Dependencies untuk Authentication
Berisi dependencies yang digunakan untuk protected routes
"""
from typing import Optional
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app_backend.models.user import UserModel
from app_backend.shared.database import get_session
from app_backend.shared.security import decode_access_token
from app_backend.domain.user import User as DomainUser

# Security scheme untuk JWT
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> DomainUser:
    """
    Dependency untuk mendapatkan user yang sedang login dari JWT token
    
    Raises:
        HTTPException: Jika token invalid atau user tidak ditemukan
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kredensial tidak valid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    # Ambil user_id dari payload
    user_id_str: Optional[str] = payload.get("user_id")
    
    if user_id_str is None:
        raise credentials_exception
    
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception
    
    # Ambil user dari database
    user = session.query(UserModel).filter(UserModel.id == user_id).first()
    
    if user is None:
        raise credentials_exception
    
    # Cek apakah user aktif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun user dinonaktifkan"
        )
    
    # Convert ke domain model dan return
    return user.to_domain()


async def get_current_active_user(
    current_user: DomainUser = Depends(get_current_user)
) -> DomainUser:
    """
    Dependency untuk mendapatkan user aktif yang sedang login
    
    Raises:
        HTTPException: Jika user tidak aktif
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User tidak aktif"
        )
    return current_user


async def get_current_verified_user(
    current_user: DomainUser = Depends(get_current_user)
) -> DomainUser:
    """
    Dependency untuk mendapatkan user yang sudah terverifikasi
    
    Raises:
        HTTPException: Jika email user belum terverifikasi
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email belum terverifikasi"
        )
    return current_user
