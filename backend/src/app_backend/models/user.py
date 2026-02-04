"""
ORM Model - Database table representation
"""
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, String, DateTime
from datetime import datetime
import uuid as uuid_lib

from app_backend.shared.database import Base


class UserModel(Base):
    """ORM Model for users table"""
    
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_domain(self):
        """Convert ORM model to domain model"""
        from app_backend.domain.user import User
        
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            full_name=self.full_name,
            hashed_password=self.hashed_password,
            is_active=self.is_active,
            is_verified=self.is_verified,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    @staticmethod
    def from_domain(user):
        """Create ORM model from domain model"""
        return UserModel(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
