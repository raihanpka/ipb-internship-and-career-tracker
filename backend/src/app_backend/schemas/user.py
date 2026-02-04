"""Pydantic schemas untuk validasi request/response API.

Berisi schema untuk validasi data user
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Schema dasar untuk user"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema untuk registrasi user"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(char.isdigit() for char in v):
            raise ValueError('Password harus mengandung minimal satu angka')
        if not any(char.isupper() for char in v):
            raise ValueError('Password harus mengandung minimal satu huruf besar')
        if not any(char.islower() for char in v):
            raise ValueError('Password harus mengandung minimal satu huruf kecil')
        return v


class UserUpdate(BaseModel):
    """Schema untuk update profil user"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)


class UserResponse(UserBase):
    """Schema untuk response user"""
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema untuk login user"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema untuk response JWT token"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema untuk payload token"""
    user_id: Optional[uuid.UUID] = None
    email: Optional[str] = None
