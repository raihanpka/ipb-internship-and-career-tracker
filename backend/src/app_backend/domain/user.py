"""
Domain Model - Pure business logic tanpa dependency database
Model domain murni yang berisi business logic
"""
import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class User:
    """Pure domain model untuk User - berisi business logic"""
    
    id: uuid.UUID
    email: str
    username: str
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validasi domain rules"""
        if not self.email or '@' not in self.email:
            raise ValueError("Alamat email tidak valid")
        
        if not self.username or len(self.username) < 3:
            raise ValueError("Username harus minimal 3 karakter")
        
        if not self.full_name:
            raise ValueError("Nama lengkap wajib diisi")
    
    def activate(self):
        """Aktifkan akun user"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Nonaktifkan akun user"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def verify_email(self):
        """Tandai email sebagai terverifikasi"""
        self.is_verified = True
        self.updated_at = datetime.utcnow()
    
    def update_profile(self, full_name: Optional[str] = None, username: Optional[str] = None):
        """Update profil user"""
        if full_name:
            self.full_name = full_name
        if username:
            if len(username) < 3:
                raise ValueError("Username harus minimal 3 karakter")
            self.username = username
        self.updated_at = datetime.utcnow()

