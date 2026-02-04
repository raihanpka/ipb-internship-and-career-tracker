"""
Load Fixtures Script
Script untuk populate database dengan data dummy untuk testing
"""
import uuid

import click

from app_backend.models.user import UserModel
from app_backend.shared.database import Base, engine, SessionLocal
from app_backend.shared.security import hash_password

from faker import Faker

fake = Faker()


@click.command()
def load_fixtures():
    """Load fixtures ke database"""
    click.echo('Load fixtures dimulai')
    Base.metadata.drop_all(bind=engine)
    click.echo('Semua tabel berhasil dihapus')
    Base.metadata.create_all(bind=engine)
    click.echo('Semua tabel berhasil dibuat')

    try:
        with SessionLocal.begin() as db:
            click.echo('Mulai seeding database dengan data dummy')
            
            # Buat test users
            for i in range(5):
                db.add(
                    UserModel(
                        id=uuid.uuid4(),
                        email=fake.email(),
                        username=f"user{i}_{fake.user_name()}",
                        full_name=fake.name(),
                        hashed_password=hash_password("Password123"),
                        is_active=True,
                        is_verified=fake.boolean(),
                    )
                )
            
            # Buat default test user
            db.add(
                UserModel(
                    id=uuid.uuid4(),
                    email="test@example.com",
                    username="testuser",
                    full_name="Test User",
                    hashed_password=hash_password("Password123"),
                    is_active=True,
                    is_verified=True,
                )
            )
            
            click.echo('Selesai seeding database dengan data dummy')
            db.commit()
            click.echo('Fixture berhasil dimuat')
            click.echo('\nKredensial untuk testing:')
            click.echo('Email: test@example.com')
            click.echo('Password: Password123')
    except Exception as e:
        click.echo(f'Error: {e}')
        db.rollback()
        click.echo('Error saat load fixtures!!!')
    finally:
        db.close()


if __name__ == '__main__':
    load_fixtures()
