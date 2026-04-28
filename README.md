<div align="center">

<h1>LARAS: IPB Internship and Career Tracker Platform</h1>

Integrated Internship and Career Tracker Platform for **IPB University**, built with **FastAPI** for backend and **React with Vite** for frontend.

<img src="./LARAS_Logo.png" alt="LARAS Logo" width="450">

[![License](https://img.shields.io/badge/License-AFL--3.0-blue)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![Poetry Version](https://img.shields.io/badge/Poetry-1.2+-red?logo=poetry)](https://python-poetry.org/)

</div>

---

## Tentang Aplikasi Ini

**LARAS (Lintasan Arah dan Rencana Aktualisasi Studi)** adalah platform pelacakan magang dan karir untuk mahasiswa IPB University. Platform ini memfasilitasi pencarian lowongan magang/kerja, pelacakan status lamaran, pencatatan aktivitas harian selama magang, dan pembuatan laporan otomatis. Sistem menggunakan arsitektur Middleman Model di mana admin CDA (Career Development and Alumni) IPB mengkurasi lowongan dari berbagai sumber eksternal.


## Fitur Utama

- **Authentication & Authorization:** Sistem login JWT dengan role-based access control (ADMIN & STUDENT)
- **Profile Management:** Pengelolaan profil mahasiswa dengan skill tagging dan upload CV
- **Job Board:** Papan lowongan terpusat dengan fitur pencarian dan filter
- **Job Matching:** Pencocokan otomatis profil mahasiswa dengan requirement lowongan
- **Application Tracking:** Pelacakan status lamaran secara mandiri (Self-Reported ATS)
- **Wishlist:** Simpan lowongan incaran dengan catatan pribadi
- **Activity Logging:** Pencatatan aktivitas harian selama magang

---

## Project Structure

```
ipb-internship-and-career-tracker/
├── backend/
│   ├── src/
│   │   └── app_backend/
│   │       ├── conf/              # Konfigurasi aplikasi
│   │       ├── domain/            # Domain models dan business logic
│   │       ├── features/          # Fitur aplikasi (vertical slices)
│   │       ├── models/            # ORM models (database)
│   │       ├── routers/           # API endpoints
│   │       ├── schemas/           # Pydantic schemas (request/response)
│   │       ├── shared/            # Shared utilities
│   │       └── main.py            # Entry point aplikasi
│   ├── tests/                     # Unit dan integration tests
│   ├── alembic/                   # Database migrations
│   └── docs/                      # Dokumentasi fitur
├── frontend/
│   ├── src/
│   │   ├── components/            # Reusable UI components
│   │   ├── pages/                 # Page components
│   │   └── main.jsx               # Entry point aplikasi
│   └── public/                    # Static assets
└── README.md
```

## Tech Stack

### Backend

| Technology | Version | Description |
|------------|---------|-------------|
| Python | >= 3.11 | Programming language |
| FastAPI | ^0.128.0 | Web framework |
| SQLAlchemy | ^2.0.46 | ORM database |
| PostgreSQL | >= 15 | Database |
| Pydantic | ^2.0.0 | Data validation |
| Alembic | ^1.11.1 | Database migration |
| python-jose | ^3.5.0 | JWT authentication |
| passlib | ^1.7.4 | Password hashing (bcrypt) |
| Celery | ^5.4.0 | Background task queue |
| Redis | ^5.2.0 | Message broker |
| LangChain | ^0.3.0 | AI/LLM framework |
| LangGraph | ^0.2.0 | AI agent orchestration |

### Frontend

| Technology | Version | Description |
|------------|---------|-------------|
| React | ^19.2.0 | UI library |
| Vite | ^7.3.1 | Build tool |
| Tailwind CSS | ^4.2.0 | Utility-first CSS |
| DaisyUI | ^5.5.18 | Component library |
| Axios | ^1.13.5 | HTTP client |
| Swiper | ^12.1.2 | Carousel/slider |
| React Icons | ^5.6.0 | Icon library |

## Prerequisites

Pastikan telah terinstall:

- **Python** >= 3.11 ([install guide](https://www.python.org/downloads/))
- **Poetry** >= 1.2 ([install guide](https://python-poetry.org/docs/#installation))
- **Node.js** >= 18 ([install guide](https://nodejs.org/))
- **PostgreSQL** >= 15 ([install guide](https://www.postgresql.org/download/))
- **Docker** (optional, wajib untuk production)

## Installation

Clone repository:

```bash
git clone https://github.com/raihanpka/ipb-internship-and-career-tracker.git
cd ipb-internship-and-career-tracker
```

### Backend Setup

```bash
cd backend

# Copy environment file
cp .env.example .env

# Install dependencies
poetry install

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn app_backend.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Configuration

### Backend Environment Variables

Edit `backend/.env.example`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/internship_career_tracker

# JWT Settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=32

# Environment
ENVIRONMENT=development
```

## Available Commands

### Backend

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make dev` | Run development server |
| `make test` | Run tests |
| `make coverage` | Run tests with coverage |
| `make format` | Format code |
| `make lint` | Lint code |
| `poetry run alembic upgrade head` | Apply migrations |
| `poetry run alembic revision --autogenerate -m "desc"` | Create migration |

### Frontend

| Command | Description |
|---------|-------------|
| `npm install` | Install dependencies |
| `npm run dev` | Run development server (http://localhost:5173) |
| `npm run build` | Build for production |
| `npm run lint` | Lint code |
| `npm run preview` | Preview production build |

## API Documentation

Setelah backend berjalan, akses dokumentasi API di:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Design Principles

1. **Vertical Slice Architecture** - Setiap fitur diorganisir dalam slice terpisah ([Referensi](https://www.jimmybogard.com/vertical-slice-architecture/))
2. **Domain-Driven Design** - Object-Oriented Domain Modeling ([Referensi](https://en.wikipedia.org/wiki/Domain-driven_design))
3. **CQRS Pattern** - Command Query Responsibility Segregation ([Referensi](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs))

---

## Credits

Project ini dikembangkan oleh **Kelompok 3 (P3)** untuk memenuhi tugas proyek mata kuliah **Analsis dan Desain Sistem (ADS)** dari **Departemen Ilmu Komputer, IPB University**.

**Anggota:**
| Nama | NIM | Role |
|------|-----|------|
| Raihan Putra Kirana | G6401231027 | Project Lead & DevOps Engineer |
| Ghaliyh Rayhan Adz Dzikra | G6401231001 | Frontend Developer & UI/UX Designer |
| Insan Anshary Rasul | G6401231132 | Backend Developer & System Analyst |

---

## License

This project is licensed under the `Academic Free License version 3.0`, see the [LICENSE](LICENSE) file for details.
