"""
Login User Feature - Command Handler
Fitur untuk login dan autentikasi user
"""
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app_backend.models.user import UserModel
from app_backend.schemas.user import UserLogin
from app_backend.shared.security import verify_password, create_access_token


class LoginUserException(Exception):
    """Exception yang terjadi saat login user"""
    pass


@dataclass
class LoginUserCommand:
    """Command untuk login user"""
    payload: UserLogin


@dataclass
class LoginUserResult:
    """Result dari proses login"""
    access_token: Optional[str] = None
    token_type: str = "bearer"
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        """Cek apakah ada error"""
        return self.error_message is not None


def login_user_command_handler(
    command: LoginUserCommand, 
    session: Session
) -> LoginUserResult:
    """
    Handle login user
    
    Business Rules:
    1. User harus ada dengan email yang diberikan
    2. Password harus cocok
    3. User harus aktif
    4. Generate JWT token jika autentikasi berhasil
    """
    
    # Cari user berdasarkan email
    user = session.query(UserModel).filter(
        UserModel.email == command.payload.email
    ).first()
    
    if not user:
        return LoginUserResult(error_message="Email atau password salah")
    
    # Verifikasi password
    if not verify_password(command.payload.password, user.hashed_password):
        return LoginUserResult(error_message="Email atau password salah")
    
    # Cek apakah user aktif
    if not user.is_active:
        return LoginUserResult(error_message="Akun dinonaktifkan")
    
    # Buat access token
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "username": user.username
    }
    
    access_token = create_access_token(data=token_data)
    
    return LoginUserResult(
        access_token=access_token,
        token_type="bearer"
    )
