"""
Auth Router - API endpoints untuk authentication
Berisi semua endpoint untuk registrasi, login, dan manajemen user
"""
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from app_backend.features.register_user.register_user_command import (
    RegisterUserCommand,
    register_user_command_handler,
)
from app_backend.features.login_user.login_user_command import (
    LoginUserCommand,
    login_user_command_handler,
)
from app_backend.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app_backend.shared.database import get_session
from app_backend.shared.dependencies import get_current_user, get_current_active_user
from app_backend.domain.user import User as DomainUser

router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"]
)


@router.post("/register", response_model=UserResponse, status_code=HTTPStatus.CREATED)
async def register(
    user_data: UserCreate,
    session=Depends(get_session),
) -> UserResponse:
    """
    Registrasi user baru
    
    - **email**: Alamat email yang valid (harus unik)
    - **username**: Username (harus unik, minimal 3 karakter)
    - **full_name**: Nama lengkap user
    - **password**: Password (minimal 8 karakter, harus mengandung huruf besar, kecil, dan angka)
    """
    result = register_user_command_handler(
        command=RegisterUserCommand(payload=user_data),
        session=session,
    )

    if result.got_error():
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, 
            detail=result.error_message
        )

    # Convert domain user ke response schema
    domain_user = result.user
    return UserResponse(
        id=domain_user.id,
        email=domain_user.email,
        username=domain_user.username,
        full_name=domain_user.full_name,
        is_active=domain_user.is_active,
        is_verified=domain_user.is_verified,
        created_at=domain_user.created_at,
        updated_at=domain_user.updated_at
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    session=Depends(get_session),
) -> Token:
    """
    Login dengan email dan password
    
    Mengembalikan JWT access token jika autentikasi berhasil
    
    - **email**: Email user
    - **password**: Password user
    """
    result = login_user_command_handler(
        command=LoginUserCommand(payload=credentials),
        session=session,
    )

    if result.got_error():
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=result.error_message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(
        access_token=result.access_token,
        token_type=result.token_type
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: DomainUser = Depends(get_current_active_user)
) -> UserResponse:
    """
    Mendapatkan informasi user yang sedang login
    
    Memerlukan JWT token yang valid di Authorization header
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def logout(
    current_user: DomainUser = Depends(get_current_user)
):
    """
    Logout user yang sedang login
    
    Catatan: Karena menggunakan JWT tokens, logout sebenarnya dilakukan di client-side
    dengan menghapus token. Endpoint ini ada untuk konsistensi API.
    Jika perlu server-side token blacklisting, implementasikan di sini.
    """
    # Dalam sistem JWT stateless, logout biasanya ditangani client-side
    # Jika butuh token blacklisting di server-side, implementasikan di sini
    return None
