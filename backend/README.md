# IPB Internship and Career Tracker - Backend

## Deskripsi

Backend API untuk aplikasi IPB Internship and Career Tracker (LARAS) menggunakan FastAPI dengan Vertical Slice Architecture dan Domain-Driven Design.

## Struktur Folder

```bash
backend/
├── src/
│   └── app_backend/
│       ├── conf/              # Konfigurasi aplikasi (settings, environment)
│       ├── domain/            # Domain models dan business logic
│       ├── features/          # Fitur aplikasi (vertical slices)
│       │   ├── auth/          # Authentication (login, register, reset password)
│       │   ├── admin/         # Admin management (departments, skills, companies)
│       │   ├── profile/       # Student & Admin profile management
│       │   ├── vacancy/       # Job vacancies & job matching
│       │   ├── wishlist/      # Student wishlist
│       │   └── application/   # Application tracking (Self-Reported ATS)
│       ├── models/            # SQLAlchemy ORM models
│       ├── routers/           # FastAPI endpoint routers
│       ├── schemas/           # Pydantic schemas (request/response)
│       ├── shared/            # Shared utilities (security, database, dependencies)
│       └── main.py            # Entry point aplikasi
├── tests/                     # Unit dan integration tests
├── alembic/                   # Database migrations
├── docs/                      # Feature documentation
└── scripts/                   # Utility scripts
```

## Tech Stack

| Technology | Version | Description |
|------------|---------|-------------|
| Python | >= 3.11 | Programming language |
| FastAPI | ^0.128.0 | Async web framework |
| SQLAlchemy | ^2.0.46 | ORM database |
| PostgreSQL | >= 15 | Database |
| Pydantic | ^2.0.0 | Data validation & serialization |
| Alembic | ^1.11.1 | Database migration tool |
| python-jose | ^3.5.0 | JWT token handling |
| passlib | ^1.7.4 | Password hashing (bcrypt) |
| Celery | ^5.4.0 | Distributed task queue |
| Redis | ^5.2.0 | Message broker untuk Celery |
| LangChain | ^0.3.0 | LLM framework |
| LangGraph | ^0.2.0 | AI agent orchestration |

## Cara Menjalankan

### Prasyarat

- Python 3.11+
- Poetry 1.2+
- PostgreSQL 15+
- Redis (optional, untuk Celery)

### Setup Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env sesuai kebutuhan
```

### Variabel Lingkungan

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/internship_career_tracker
DATABASE_TEST_URL=postgresql://user:password@localhost:5432/internship_career_tracker_test

# JWT Settings
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=32

# Password Reset
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES=15

# Environment (development, staging, production)
ENVIRONMENT=development
```

### Menjalankan Aplikasi

```bash
# Install dependencies
make install
# atau
poetry install

# Jalankan migrasi database
poetry run alembic upgrade head

# Jalankan server development
make dev
# atau
poetry run uvicorn app_backend.main:app --reload
```

Server: http://localhost:8000
Dokumentasi API: http://localhost:8000/docs

## Available Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies dengan Poetry |
| `make dev` | Jalankan development server |
| `make test` | Jalankan unit tests |
| `make coverage` | Jalankan tests dengan coverage report |
| `make format` | Format kode dengan Black dan isort |
| `make lint` | Lint kode dengan Flake8 |

## Database & Migrasi

Model ORM SQLAlchemy di `src/app_backend/models` adalah source of truth untuk schema database.

```bash
# Buat migrasi baru dari perubahan model
poetry run alembic revision --autogenerate -m "deskripsi perubahan"

# Terapkan migrasi
poetry run alembic upgrade head

# Rollback satu step
poetry run alembic downgrade -1

# Lihat history migrasi
poetry run alembic history
```

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register/student` - Registrasi mahasiswa
- `POST /register/admin` - Registrasi admin (admin only)
- `POST /login` - Login
- `POST /refresh-token` - Refresh access token
- `POST /logout` - Logout
- `POST /password/reset-request` - Request reset password
- `POST /password/reset` - Reset password
- `GET /me` - Get current user info

### Profile (`/api/v1/profile`)
- `GET /student/me` - Get student profile
- `PATCH /student/me` - Update student profile

### Admin (`/api/v1/admin`)
- `PATCH /users/{id}/toggle-active` - Toggle user active status
- CRUD `/departments` - Manage departments
- CRUD `/skills` - Manage master skills
- CRUD `/companies` - Manage external companies

### Vacancies (`/api/v1/vacancies`)
- `GET /vacancies` - List vacancies
- `GET /vacancies/search` - Search with filters
- `GET /vacancies/{id}` - Get vacancy detail
- `POST /vacancies` - Create vacancy (admin only)
- `PUT /vacancies/{id}` - Update vacancy (admin only)
- `DELETE /vacancies/{id}` - Delete vacancy (admin only)

### Wishlist (`/api/v1/wishlist`)
- `GET /wishlist` - List student wishlist
- `POST /wishlist` - Add to wishlist
- `DELETE /wishlist/{id}` - Remove from wishlist

### Job Matching (`/api/v1/job-matching`)
- `GET /job-matching` - List job matches for student
- `GET /job-matching/{vacancy_id}` - Get match detail

### Applications (`/api/v1/applications`)
- `POST /applications/initialize` - Initialize external application

## Prinsip Desain

1. **Vertical Slice Architecture** - Setiap fitur diorganisir dalam folder terpisah dengan command handler pattern
2. **Domain-Driven Design** - Business logic dipisahkan ke domain layer
3. **CQRS Pattern** - Command dan Query dipisahkan untuk scalability
4. **Repository Pattern** - Data access layer terenkapsulasi

## Testing

```bash
# Jalankan semua tests
make test

# Jalankan dengan coverage
make coverage

# Jalankan test spesifik
poetry run pytest tests/test_auth.py -v
```
