# IPB Internship and Career Tracker - Backend

## Deskripsi

Backend API untuk aplikasi IPB Internship and Career Tracker menggunakan FastAPI dengan Vertical Slice Architecture dan pemisahan ORM Models dan Domain Models.

## Struktur Lengkap

```
backend/
├── src/
│   └── app_backend/
│       ├── conf/              # Konfigurasi aplikasi
│       ├── domain/            # Domain models dan business logic
│       ├── features/          # Fitur-fitur aplikasi (vertical slices)
│       ├── models/            # ORM models (database)
│       ├── routers/           # API endpoints
│       ├── schemas/           # Pydantic schemas (request/response)
│       ├── scripts/           # Script utility
│       ├── shared/            # Shared utilities dan helpers
│       └── main.py            # Entry point aplikasi
└── tests/                     # Unit dan integration tests
```

## Cara Menjalankan

### Pre-requisites

- Python 3.11+
- Poetry 1.2+
- Docker & Docker Compose
- PostgreSQL 15

### Environment Variables

```env
DB_URL=postgresql://user:password@localhost:5432/internship_career_tracker
DB_TEST_URL=postgresql://user:password@localhost:5432/internship_career_tracker_test
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Menjalankan Aplikasi
Jalankan container Docker:
```
make up
```

Hentikan container Docker:
```
make down
```

Jalankan server lokal:
```
make start-local
```

Isi database dengan data palsu:
```
make load-fixtures
```

Jalankan tes:
```
make test
```

Jalankan tes dengan coverage:
```
make coverage
```

Jalankan tes dengan coverage fitur:
```
make coverage-features
```

Server: http://localhost:8000
API Docs: http://localhost:8000/docs

## Prinsip Desain Sistem

1. Vertical Slice Architecture
2. Domain-Driven Design
3. CQRS Pattern
4. Dependency Injection

## Dependencies

- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
- passlib[bcrypt]
- python-jose[cryptography]
- email-validator
- psycopg2-binary
