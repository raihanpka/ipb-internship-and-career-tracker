"""
Application Settings
Konfigurasi aplikasi menggunakan Pydantic Settings
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Konfigurasi aplikasi"""
    
    db_url: str = "postgresql://user:password@localhost:5432/internship_career_tracker"
    db_test_url: str = "postgresql://user:password@localhost:5432/internship_career_tracker_test"

    session_auto_commit: bool = False
    session_auto_flush: bool = False
    
    # JWT Settings
    secret_key: str = "your-secret-key-here-change-in-production-09876543210987654321"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
