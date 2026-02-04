"""
Register User Feature - Command Handler
Fitur untuk registrasi user baru
"""
import uuid
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app_backend.domain.user import User as DomainUser
from app_backend.models.user import UserModel
from app_backend.schemas.user import UserCreate
from app_backend.shared.security import hash_password


class RegisterUserException(Exception):
    """Exception yang terjadi saat registrasi user"""
    pass


@dataclass
class RegisterUserCommand:
    """Command untuk registrasi user baru"""
    payload: UserCreate


@dataclass
class RegisterUserResult:
    """Result dari proses registrasi user"""
    user: Optional[DomainUser] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        """Cek apakah ada error"""
        return self.error_message is not None


def register_user_command_handler(
    command: RegisterUserCommand, 
    session: Session
) -> RegisterUserResult:
    """
    Handle registrasi user baru
    
    Business Rules:
    1. Email harus unik
    2. Username harus unik
    3. Password harus di-hash sebelum disimpan
    4. User baru aktif by default tapi belum terverifikasi
    """
    
    # Cek apakah email sudah ada
    existing_email = session.query(UserModel).filter(
        UserModel.email == command.payload.email
    ).first()
    
    if existing_email:
        return RegisterUserResult(error_message="Email sudah terdaftar")
    
    # Cek apakah username sudah ada
    existing_username = session.query(UserModel).filter(
        UserModel.username == command.payload.username
    ).first()
    
    if existing_username:
        return RegisterUserResult(error_message="Username sudah digunakan")
    
    try:
        # Buat domain model (validasi business rules)
        domain_user = DomainUser(
            id=uuid.uuid4(),
            email=command.payload.email,
            username=command.payload.username,
            full_name=command.payload.full_name,
            hashed_password=hash_password(command.payload.password),
            is_active=True,
            is_verified=False
        )
        
        # Convert ke ORM model dan simpan
        user_model = UserModel.from_domain(domain_user)
        session.add(user_model)
        session.commit()
        session.refresh(user_model)
        
        # Convert kembali ke domain model untuk return
        return RegisterUserResult(user=user_model.to_domain())
        
    except ValueError as e:
        # Error validasi domain
        return RegisterUserResult(error_message=str(e))
    except Exception as e:
        session.rollback()
        return RegisterUserResult(error_message=f"Registrasi gagal: {str(e)}")
