# IPB Internship & Career Tracker — Development Roadmap

**Document Version**: 1.0
**Last Updated**: April 28, 2026
**Project**: IPB Internship & Career Tracker (Middleman Model)
**Authors**: Raihan Putra Kirana, Insan Anshary Rasul

---

## Table of Contents

- [Aturan Pengembangan](#aturan-pengembangan)
- [Phase 0 Foundation dan Infrastructure](#phase-0-foundation-dan-infrastructure)
- [Phase 1 User Management dan Authentication](#phase-1-user-management-dan-authentication)
- [Phase 2 Profile Management dan Master Data](#phase-2-profile-management-dan-master-data)
- [Phase 3 Aggregated Job Board dan Discovery](#phase-3-aggregated-job-board-dan-discovery)
- [Phase 4 Self-Reported ATS](#phase-4-self-reported-ats)
- [Phase 5 Placement dan Activity Tracker](#phase-5-placement-dan-activity-tracker)
- [Phase 6 Auto-Report Automation](#phase-6-auto-report-automation)
- [Phase 7 Analytics dan Utilities](#phase-7-analytics-dan-utilities)
- [Phase 8 Notification System](#phase-8-notification-system)

---

## Aturan Pengembangan

### Global Flow

- [ ] Setiap card memiliki scope jelas, acceptance criteria, dan owner yang ditentukan
- [ ] Setiap card memiliki implementation checklist dan test checklist terpisah
- [ ] Tidak ada card yang pindah ke Done tanpa bukti review kode dan QA
- [ ] Tidak ada phase baru dimulai sebelum test gate phase sebelumnya green

### Panduan Background Workers dan Scheduled Jobs

Semua background task dan scheduled job dikelola di **application layer** melalui Celery + Redis Broker, bukan langsung di database (pg_cron) atau OS (crontab). Pendekatan ini dipilih agar:

- Job dapat dimonitor dari satu tempat (Celery Flower atau structured log)
- Retry behavior dapat dikonfigurasi per task dengan `max_retries` dan `countdown`
- Job mudah dinonaktifkan atau dijadwal ulang tanpa deploy ulang config server
- Observability AI Agent terisolasi dari request lifecycle utama

Setiap worker didaftarkan di `app/workers/` sebagai Celery task dengan signature yang jelas. Tidak ada `time.sleep` loop, `APScheduler` ad-hoc, atau direct pg_cron yang digunakan. Semua task berjalan secara **asinkron** dan tidak memblokir response HTTP ke client.

---

## Phase 0 Foundation dan Infrastructure

**Objective**: Membangun baseline yang reliable sebagai fondasi seluruh phase berikutnya.
**Owner**: @Peka, @Insan

### Database dan Migration

- [x] Jalankan migration baseline dari schema SQL multi-schema (`auth`, `public`)
- [x] Verifikasi semua extension aktif: `pgcrypto`, `uuid-ossp`
- [x] Verifikasi trigger `set_updated_at()` terpasang di semua tabel dengan kolom `updated_at`
- [x] Verifikasi Partial Index terpasang di `auth.user_refresh_tokens` (is_revoked = FALSE) dan `auth.auth_action_tokens` (is_used = FALSE)
- [x] Seed data awal: status lowongan default, role enum (`ADMIN`, `STUDENT`)
- [x] Verifikasi relasi FK antar schema tidak melanggar constraint saat migration fresh

### Aplikasi dan Infrastruktur

- [x] Finalisasi struktur module FastAPI: `app/routers/`, `app/services/`, `app/workers/`, `app/agents/`
- [x] Setup environment layering via `.env.development`, `.env.staging`, `.env.production`
- [x] Setup global exception handler dan request logging middleware
- [x] Setup global response format (`{ success, data, message }`)
- [x] Setup health check endpoint `GET /health` dengan response time < 200ms
- [x] Setup Swagger (FastAPI auto-docs) dengan grouping tag per module
- [x] Setup Redis satu instance: digunakan untuk Celery broker saja
- [x] Setup Celery worker dan verifikasi koneksi ke Redis broker
- [x] Setup Object Storage (S3-compatible, misal MinIO atau Supabase Storage) untuk CV dan dokumen
- [x] Verifikasi koneksi SQLAlchemy ke PostgreSQL (connection pool, `pool_pre_ping = True`)

### CI/CD Pipeline

- [x] Pipeline lint pass (`ruff check .`)
- [x] Pipeline build/startup pass (`uvicorn app.main:app --check`)
- [x] Pipeline unit test pass (`pytest tests/unit/`)
- [x] Health endpoint smoke test pass via HTTP check
- [x] Migration dry run pass di staging sebelum production

### Test Gate Phase 0

- [x] Lint green
- [x] Build green
- [x] Health endpoint merespons 200 dalam 200ms
- [x] Migration berhasil dijalankan di staging environment tanpa error

**Exit Criteria**: Core application stabil, semua dependency terhubung, dan siap untuk pengembangan feature.

---

## Phase 1 User Management dan Authentication

**Objective**: Menghadirkan lifecycle akun dan sesi yang aman dengan arsitektur Multi-Schema.
**Owner**: @Peka

### Sign Up

- [x] Endpoint `POST /auth/register` menerima `email`, `password`, `full_name`, `role`
- [x] Validasi email: format valid, belum terdaftar di sistem (`auth.users`)
- [x] Validasi password: minimal 8 karakter, minimal 1 huruf kapital, minimal 1 angka
- [x] Hash password menggunakan bcrypt sebelum disimpan — tidak pernah simpan plain text
- [x] Insert row ke `auth.users` dengan `is_active = TRUE`
- [x] Kirim email aktivasi setelah register (opsional di development)

### Sign In (JWT)

- [x] Endpoint `POST /auth/login` menerima `email` dan `password`
- [x] Verifikasi password dengan bcrypt compare
- [x] Tolak login jika `is_active = FALSE` dengan pesan jelas
- [x] Buat **Stateless Access Token** (JWT): TTL 15 menit, payload berisi `user_id`, `email`, `role`
- [x] Buat **Stateful Refresh Token**: random 32 bytes hex, simpan hash di `auth.user_refresh_tokens`
- [x] Insert `auth.user_refresh_tokens` dengan `expires_at = NOW() + 7 days` dan `is_revoked = FALSE`
- [x] Update `auth.users.last_login_at = NOW()`
- [x] Kirim Refresh Token via `httpOnly`, `Secure`, `SameSite=Strict` cookie

### Token Rotation & Refresh

- [x] Endpoint `POST /auth/refresh` membaca Refresh Token dari cookie
- [x] Query `auth.user_refresh_tokens` WHERE `token_hash = hash(token)` AND `is_revoked = FALSE` AND `expires_at > NOW()`
- [x] Jika tidak ditemukan atau expired: return 401 Unauthorized
- [x] Revoke token lama (`is_revoked = TRUE`)
- [x] Buat Access Token baru dan Refresh Token baru, insert baris baru ke `auth.user_refresh_tokens`

### Logout

- [x] Endpoint `POST /auth/logout`: revoke session saat ini (`is_revoked = TRUE`), hapus cookie
- [x] Endpoint `POST /auth/logout-all`: revoke semua baris `auth.user_refresh_tokens` untuk `user_id` ini

### Password Reset via Action Token

- [x] Endpoint `POST /auth/forgot-password`: terima email, generate token sekali pakai, simpan ke `auth.auth_action_tokens`, kirim email link reset
- [x] Token bersifat single-use: `is_used` di-set `TRUE` setelah dipakai
- [x] Endpoint `POST /auth/reset-password`: verifikasi token, update `auth.users.password_hash`
- [x] Token kadaluarsa otomatis berdasarkan `expires_at`

### Role-Based Access Control (RBAC)

- [x] Middleware `require_role(["ADMIN"])` dan `require_role(["STUDENT"])` terpasang di semua router
- [x] Endpoint admin hanya bisa diakses user dengan `role = ADMIN`
- [x] Endpoint student hanya bisa diakses user dengan `role = STUDENT`
- [x] Endpoint publik (job board read-only) tidak memerlukan auth

### Account Management (Admin)

- [x] Endpoint `PATCH /admin/users/:id/status`: Admin menonaktifkan/mengaktifkan akun user bermasalah
- [x] Update `auth.users.is_active`
- [x] User yang dinonaktifkan tidak bisa login dan Refresh Token-nya di-revoke semua

### Test Gate Phase 1

- [x] Unit test: bcrypt hashing, JWT payload validation, token expiry check
- [x] Integration test: signup → login → refresh → logout flow end-to-end
- [x] Test: token replay attack — gunakan Refresh Token yang sudah di-revoke, harus 401
- [x] Test: user nonaktif tidak bisa login
- [x] Test: RBAC — student mengakses endpoint admin harus 403, bukan 404

**Exit Criteria**: Auth flow aman, stateless Access Token dan stateful Refresh Token berfungsi dengan benar.

---

## Phase 2 Profile Management dan Master Data

**Objective**: Menghadirkan manajemen profil mahasiswa, admin, dan entitas referensi utama sistem.
**Owner**: @Peka

### Master Data (Admin)

- [x] Endpoint `GET/POST/PATCH/DELETE /admin/departments`: CRUD Program Studi dan Fakultas
- [x] Schema Ref: `public.master_departments`
- [x] Endpoint `GET/POST/PATCH/DELETE /admin/companies`: CRUD perusahaan eksternal sebagai referensi lowongan
- [x] Schema Ref: `public.master_external_companies`
- [x] Endpoint `GET/POST/PATCH/DELETE /admin/skills`: CRUD master skill untuk standarisasi pustaka keahlian di Matching Engine
- [x] Schema Ref: `public.master_skills`
- [x] Semua endpoint master data mengembalikan data terurut berdasarkan nama (ASC) dan mendukung pagination cursor-based

### Student Profile Setup

- [x] Endpoint `POST /profile/student/setup`: Input NIM, nama lengkap, semester, dan relasi ke `department_id`
- [x] Schema Ref: Insert `public.profiles_student`
- [x] Endpoint `GET /profile/student/me`: Ambil profil lengkap mahasiswa yang sedang login
- [x] Endpoint `PATCH /profile/student/me`: Update field profil yang berubah saja (partial update)
- [x] Endpoint `POST /profile/student/cv`: Upload CV dalam format PDF ke Object Storage, simpan URL
- [x] Schema Ref: Update `public.profiles_student.cv_url`
- [x] Validasi upload: hanya menerima `application/pdf`, ukuran maksimum 5MB
- [x] Response upload menyertakan `cv_url` publik

### Student Skills Management

- [x] Endpoint `GET /profile/student/skills`: Daftar skill yang sudah di-tag mahasiswa
- [x] Endpoint `POST /profile/student/skills`: Tag skill dari `master_skills` ke profil mahasiswa
- [x] Endpoint `DELETE /profile/student/skills/:skill_id`: Hapus tag skill tertentu
- [x] Schema Ref: `public.student_skills` (relasi `student_id` ↔ `skill_id`)
- [x] Validasi: skill_id harus ada di `master_skills`, tidak boleh duplikat per mahasiswa

### Admin Profile Setup

- [x] Endpoint `POST /profile/admin/setup`: Input NIP, nama lengkap, dan unit kerja (contoh: CDA IPB)
- [x] Schema Ref: Insert `public.profiles_admin`
- [x] Endpoint `GET /profile/admin/me`: Ambil profil admin yang sedang login

### Test Gate Phase 2

- [x] Unit test: validasi file type dan size pada CV upload
- [x] Integration test: student profile setup → CV upload → skill tagging flow
- [x] Test: upload file bukan PDF harus return 400
- [x] Test: tag skill yang tidak ada di `master_skills` harus return 404
- [x] Test: duplikat skill tag harus return 409, bukan insert ulang

**Exit Criteria**: Profil mahasiswa dan admin dapat dibuat dan diperbarui. CV tersimpan di Object Storage dengan URL yang valid.

---

## Phase 3 Aggregated Job Board dan Discovery

**Objective**: Menghadirkan papan lowongan terpusat yang dikurasi oleh internal IPB dengan fitur pencarian dan wishlist.
**Owner**: @Peka

### Vacancy Management (Admin)

- [x] Endpoint `POST /admin/vacancies`: Posting lowongan eksternal dengan field: `title`, `company_id`, `location`, `type` (Internship/Part-time/Freelance), `compensation_type` (`PAID`/`UNPAID`), `description`, `requirements`, `close_date`, `source_url`
- [x] Schema Ref: Insert `public.vacancies` dan `public.vacancy_skills`
- [x] Endpoint `GET /admin/vacancies`: Daftar semua lowongan dengan filter status dan pagination
- [x] Endpoint `PATCH /admin/vacancies/:id`: Update detail lowongan
- [x] Endpoint `DELETE /admin/vacancies/:id`: Soft-archive lowongan (`is_active = FALSE`)
- [x] **Auto-Close Scheduler**: Celery Beat cron setiap hari 00:05 UTC+7 menjalankan task `auto_close_expired_vacancies`
- [x] Task query: `public.vacancies WHERE close_date < NOW() AND is_active = TRUE` → update `is_active = FALSE`
- [x] Schema Ref: Update `public.vacancies.is_active`

### Student Discovery

- [x] Endpoint `GET /vacancies`: Daftar lowongan aktif dengan advanced filter
- [x] Query params: `?location=Jakarta`, `?type=Internship`, `?compensation=PAID`, `?q=software+engineer`
- [x] Schema Ref: Query `public.vacancies` (hanya `is_active = TRUE`)
- [x] Endpoint `GET /vacancies/:id`: Detail lowongan termasuk daftar skill yang dipersyaratkan
- [x] Endpoint `POST /vacancies/:id/wishlist`: Simpan lowongan ke wishlist dengan catatan opsional
- [x] Schema Ref: Insert `public.student_wishlist_vacancies`
- [x] Endpoint `DELETE /vacancies/:id/wishlist`: Hapus lowongan dari wishlist
- [x] Endpoint `GET /wishlist`: Daftar lowongan yang tersimpan oleh mahasiswa yang sedang login

### AI Job Matching (Simple Logic)

- [x] Endpoint `GET /vacancies/:id/match`: Hitung persentase kecocokan profil mahasiswa dengan lowongan
- [x] Logic: Bandingkan `student_skills` (set skill mahasiswa) vs `vacancy_skills` (set skill yang dipersyaratkan)
- [x] Formula: `(jumlah skill cocok / jumlah skill dipersyaratkan) * 100` → clamp 0–100
- [x] Response menyertakan: `match_percentage`, `matched_skills[]`, `missing_skills[]`
- [x] Jika lowongan tidak memiliki `vacancy_skills`, return `match_percentage = null` dengan flag `no_requirements`
- [x] Endpoint `GET /vacancies?sort=match` mengurutkan hasil berdasarkan match score (dipanggil setelah endpoint match per item)

### Test Gate Phase 3

- [x] Unit test: match percentage formula, edge case vacancy tanpa skill requirement
- [x] Integration test: post vacancy → student filter → wishlist add/remove
- [x] Test: auto-close scheduler — lowongan dengan `close_date` kemarin harus nonaktif setelah cron berjalan
- [x] Test: filter kombinasi (location + type + compensation) mengembalikan hasil yang benar
- [x] Test: mahasiswa tidak dapat mengakses endpoint admin vacancy management

**Exit Criteria**: Job board aktif dan dapat difilter. Wishlist berfungsi. Auto-close berjalan sesuai jadwal.

---

## Phase 4 Self-Reported ATS

**Objective**: Menghadirkan pelacakan status lamaran secara mandiri oleh mahasiswa dengan audit trail lengkap.
**Owner**: @Insan

### Application Initialization

- [x] Endpoint `POST /vacancies/:id/apply`: Mahasiswa menekan tombol lamar
- [x] Action: Snapshot URL CV saat ini ke `cv_snapshot_url` — memastikan CV yang diarsipkan adalah CV saat melamar, bukan CV yang diperbarui kemudian
- [x] Schema Ref: Insert `public.applications` dengan `status = APPLIED`, `cv_snapshot_url` diisi dari `profiles_student.cv_url`
- [x] Guard: mahasiswa tidak bisa melamar lowongan yang sama dua kali (`UNIQUE (student_id, vacancy_id)`)
- [x] Guard: mahasiswa tidak bisa melamar lowongan yang sudah tutup (`vacancy.is_active = FALSE` → return 400)
- [x] Response menyertakan URL eksternal lowongan (`source_url`) untuk diarahkan ke situs rekrutmen asli

### Self-Reporting Pipeline

- [x] Endpoint `PATCH /applications/:id/status`: Mahasiswa memperbarui status lamaran secara mandiri
- [x] Status lifecycle yang valid: `APPLIED` → `SCREENING` → `INTERVIEW` → `OFFERED` → `ACCEPTED` atau `REJECTED`
- [x] Validasi transisi: tidak boleh mundur status (contoh: dari `INTERVIEW` ke `APPLIED` ditolak)
- [x] Jika status diubah ke `ACCEPTED`: wajib menyertakan `proof_url` (URL screenshot LoA atau email penerimaan)
- [x] Schema Ref: Update `public.applications.status`

### Proof Upload (LoA/Email)

- [x] Endpoint `POST /applications/:id/proof`: Upload bukti screenshot ke Object Storage
- [x] Validasi: hanya menerima `image/jpeg`, `image/png`, `application/pdf`, ukuran maksimum 15MB
- [x] Schema Ref: Insert `public.application_logs` dengan `proof_url` terisi, `action = PROOF_UPLOADED`
- [x] Endpoint ini hanya bisa dipanggil jika `application.status = ACCEPTED`

### History Logging (Audit Trail)

- [x] Setiap perubahan status lamaran otomatis mencatat entry baru ke `public.application_logs`
- [x] Log berisi: `application_id`, `old_status`, `new_status`, `changed_at`, `proof_url` (nullable)
- [x] Implementasi via SQLAlchemy event listener atau trigger PostgreSQL — tidak boleh manual insert di service layer
- [x] Endpoint `GET /applications/:id/history`: Riwayat seluruh perubahan status lamaran

### Admin Verification

- [x] Endpoint `GET /admin/applications/pending-verification`: Daftar lamaran dengan status `ACCEPTED` yang belum diverifikasi admin
- [x] Endpoint `POST /admin/applications/:id/verify`: Admin meninjau `proof_url` dan menyetujui → trigger pembuatan Placement record
- [x] Endpoint `POST /admin/applications/:id/reject-proof`: Admin menolak bukti → kembalikan status ke `OFFERED` dengan catatan alasan
- [x] Schema Ref: Query `public.application_logs` → eksekusi ke `public.placements`

### Test Gate Phase 4

- [x] Unit test: validasi status transition (semua kombinasi valid dan invalid)
- [x] Integration test: apply → self-report INTERVIEW → ACCEPTED + upload proof → admin verify
- [x] Test: apply lowongan yang sama dua kali harus return 409
- [x] Test: apply lowongan sudah tutup harus return 400
- [x] Test: update status ke ACCEPTED tanpa proof_url harus return 400
- [x] Test: audit log terbuat otomatis di setiap perubahan status

**Exit Criteria**: Pipeline self-reporting berjalan end-to-end dari apply hingga siap aktivasi placement. Audit trail lengkap dan tidak bisa dimanipulasi.

---

## Phase 5 Placement dan Activity Tracker (🟢 COMPLETE)

**Objective**: Menghadirkan manajemen penempatan magang dan pencatatan aktivitas harian mahasiswa.
**Owner**: @Insan

### Placement Activation

- [x] Saat Admin menyetujui lamaran (Phase 4 admin verify), sistem otomatis membuat record placement
- [x] Schema Ref: Insert `public.placements` dengan field: `student_id`, `application_id`, `company_id`, `start_date`, `end_date`, `supervisor_name` (opsional)
- [x] Guard: satu lamaran hanya bisa menghasilkan satu placement (`UNIQUE (application_id)`)
- [x] Endpoint `GET /placements/me`: Mahasiswa melihat data penempatan aktifnya
- [x] Endpoint `GET /admin/placements`: Admin melihat semua penempatan dengan filter prodi dan angkatan

### Daily Activity Log

- [x] Endpoint `POST /placements/:id/logs`: Mahasiswa menginput log harian
- [x] Field input: `log_date` (DATE), `start_time` (TIME), `end_time` (TIME), `description_raw` (TEXT), `attachment_url` (nullable)
- [x] Validasi: `log_date` tidak boleh di masa depan
- [x] Validasi: `log_date` harus dalam rentang `placement.start_date` dan `placement.end_date`
- [x] Validasi: satu mahasiswa hanya boleh memiliki satu log per tanggal (`UNIQUE (placement_id, log_date)`)
- [x] Schema Ref: Insert `public.activity_logs`

### Log Attachment Upload

- [x] Endpoint `POST /placements/:id/logs/:log_id/attachment`: Upload lampiran (foto kegiatan, dokumen pendukung)
- [x] Validasi: hanya menerima `image/jpeg`, `image/png`, `application/pdf`, maksimum 15MB
- [x] Schema Ref: Update `public.activity_logs.attachment_url`

### Log Review dan Edit

- [x] Endpoint `GET /placements/:id/logs`: Daftar semua log harian untuk placement tertentu, urut tanggal ASC
- [x] Endpoint `PATCH /placements/:id/logs/:log_id`: Edit log yang sudah ada
- [x] Endpoint `DELETE /placements/:id/logs/:log_id`: Hapus log (soft delete atau hard delete, sesuai kebijakan)

### Test Gate Phase 5

- [x] Unit test: validasi date range log terhadap placement period
- [x] Integration test: placement activation → log entry
- [x] Test: log tanggal di luar periode placement harus return 400
- [x] Test: log duplikat per tanggal harus return 409

**Exit Criteria**: Log harian mahasiswa dapat diinput dengan benar.

---

## Phase 6 Auto-Report Automation

**Objective**: Menghadirkan pembuatan laporan otomatis dari seluruh logbook mahasiswa siap cetak dalam format kampus.
**Owner**: @Insan

### Report Generation

- [ ] Endpoint `POST /placements/:id/report/generate`: Trigger pembuatan laporan akhir
- [ ] Guard: laporan hanya bisa digenerate jika `placement.end_date <= TODAY()`
- [ ] Celery task `generate_final_report(placement_id)`:
  - [ ] Fetch semua `activity_logs` untuk placement tersebut, urut berdasarkan `log_date` ASC
  - [ ] Gunakan `description_raw` sebagai konten log
  - [ ] Agregasi menggunakan Python Pandas: ringkasan per minggu, total jam, distribusi kegiatan
  - [ ] Render ke PDF template kampus menggunakan ReportLab (kop surat, tanda tangan, format PPKI)
  - [ ] Upload PDF hasil ke Object Storage lokal
  - [ ] Update `public.placements.auto_generated_report_url` dengan URL PDF yang dihasilkan
- [ ] Endpoint `GET /placements/:id/report`: Return `auto_generated_report_url` jika sudah tersedia, atau status `generating` / `not_generated`

### Surat Pengantar Generator

- [ ] Endpoint `POST /document-requests`: Mahasiswa mengajukan permohonan surat pengantar untuk keperluan pelamaran
- [ ] Field: `vacancy_id` (nullable), `purpose` (TEXT), `requested_at` (auto)
- [ ] Schema Ref: Insert `public.document_requests`
- [ ] Celery task `generate_cover_letter(request_id)`:
  - [ ] Fetch data mahasiswa dan tujuan permohonan
  - [ ] Render ke PDF surat resmi dengan kop IPB menggunakan ReportLab
  - [ ] Upload PDF ke Object Storage
  - [ ] Update `public.document_requests.generated_url`
- [ ] Endpoint `GET /document-requests/:id`: Return status permohonan dan `generated_url` jika sudah siap
- [ ] Endpoint `GET /document-requests`: Riwayat semua permohonan surat mahasiswa yang sedang login

### Test Gate Phase 6

- [ ] Integration test: trigger generate report → PDF tersedia di URL
- [ ] Test: generate report dengan placement yang belum berakhir harus return 400
- [ ] Test: generate report tanpa log sama sekali harus return 400
- [ ] Test: surat generator menghasilkan PDF dengan kop dan data mahasiswa yang benar
- [ ] Test: `auto_generated_report_url` ter-update setelah task selesai

**Exit Criteria**: Laporan akhir dapat digenerate dan diunduh. Surat pengantar dapat dipesan dan diterima dalam format PDF resmi.

---

## Phase 7 Analytics dan Utilities

**Objective**: Menghadirkan dashboard distribusi magang dan eksplorasi data untuk kebutuhan administratif.
**Owner**: @Insan

### Internship Distribution Dashboard

- [ ] Endpoint `GET /analytics/distribution`: Return data distribusi penempatan magang
- [ ] Query menggunakan view atau agregasi SQL di `public.placements` JOIN `public.master_external_companies` JOIN `public.profiles_student` JOIN `public.master_departments`
- [ ] Response berisi:
  - [ ] Top 10 perusahaan berdasarkan jumlah mahasiswa yang diterima
  - [ ] Breakdown per Program Studi: berapa mahasiswa yang magang di tiap perusahaan
  - [ ] Breakdown per tipe kompensasi: PAID vs UNPAID
  - [ ] Tren per semester (berdasarkan `placement.start_date`)
- [ ] Endpoint mendukung filter `?department_id=` dan `?year=`


### Admin Reporting Utilities

- [ ] Endpoint `GET /admin/analytics/applications`: Statistik lamaran keseluruhan
- [ ] Response: total lamaran, breakdown per status, conversion rate (apply → accepted)
- [ ] Endpoint `GET /admin/analytics/vacancies`: Statistik lowongan
- [ ] Response: total lowongan aktif, rata-rata jumlah pelamar per lowongan, lowongan paling diminati (top 5 berdasarkan jumlah apply)
- [ ] Semua endpoint analytics hanya bisa diakses ADMIN (RBAC middleware)

### Test Gate Phase 7

- [ ] Unit test: aggregation query mengembalikan hasil yang benar untuk data fixture
- [ ] Integration test: tambah placement → analytics ter-update setelah cache evict
- [ ] Test: cache hit dan miss path (verifikasi Redis key ada dan TTL benar)
- [ ] Test: filter by department menghasilkan subset yang benar

**Exit Criteria**: Admin memiliki visibilitas distribusi magang dan statistik lamaran yang dapat difilter.

---

## Phase 8 Notification System

**Objective**: Menghadirkan sistem komunikasi asinkron untuk notifikasi in-app dan email.
**Owner**: @Peka

### Notification Queue Management

- [ ] Endpoint `GET /notifications`: Daftar notifikasi aktif untuk user yang sedang login, urut `created_at` DESC
- [ ] Schema Ref: Query `public.notification_queue` WHERE `user_id = current_user AND status != DELETED`
- [ ] Endpoint `PATCH /notifications/:id/read`: Tandai notifikasi sebagai sudah dibaca
- [ ] Endpoint `DELETE /notifications/:id`: Soft-delete notifikasi dari inbox
- [ ] Endpoint `GET /notifications/unread-count`: Return jumlah notifikasi belum dibaca (untuk badge UI)


### Notification Trigger Events

- [ ] Notifikasi dikirim ke `notification_queue` pada event berikut:
  - [ ] **Laporan siap**: saat `generate_final_report` task selesai → notifikasi ke mahasiswa yang bersangkutan
  - [ ] **Surat siap**: saat `generate_cover_letter` task selesai → notifikasi ke mahasiswa yang bersangkutan
  - [ ] **Lamaran diverifikasi**: saat admin menyetujui bukti penerimaan → notifikasi ke mahasiswa
  - [ ] **Lamaran ditolak buktinya**: saat admin menolak proof → notifikasi ke mahasiswa dengan catatan alasan
  - [ ] **Lowongan wishlist akan tutup**: H-3 sebelum `close_date` lowongan yang ada di wishlist mahasiswa
  - [ ] **Placement diaktifkan**: saat placement record pertama dibuat untuk mahasiswa

### Email Sender Worker

- [ ] Celery task `send_email_notification(notification_id)`: membaca antrean `QUEUED`, kirim email via SMTP
- [ ] Setelah email berhasil terkirim: update `notification_queue.status = SENT`, isi `sent_at`
- [ ] Jika gagal setelah 3 retry: update status ke `FAILED`, log error
- [ ] Email template HTML minimal: kop IPB, nama penerima, pesan notifikasi, CTA button

### Garbage Collector Worker

- [ ] Celery Beat cron setiap hari 03:00 UTC+7 menjalankan task `cleanup_expired_tokens`
- [ ] Task 1 — Hapus Refresh Token kadaluarsa: `DELETE FROM auth.user_refresh_tokens WHERE expires_at < NOW() - INTERVAL '1 day'` (memanfaatkan Partial Index `is_revoked = FALSE`)
- [ ] Task 2 — Hapus Action Token kadaluarsa: `DELETE FROM auth.auth_action_tokens WHERE expires_at < NOW()`
- [ ] Task 3 — Hapus notifikasi lama: `DELETE FROM public.notification_queue WHERE created_at < NOW() - INTERVAL '30 days' AND status IN ('SENT', 'DELETED')`
- [ ] Log jumlah baris yang dihapus ke structured logger setelah setiap task selesai

### Test Gate Phase 8

- [ ] Unit test: notification trigger kondisi (event → payload yang benar)
- [ ] Integration test: generate report selesai → notifikasi masuk ke inbox → email terkirim
- [ ] Test: unread count ter-update saat notifikasi baru masuk
- [ ] Test: garbage collector tidak menghapus token yang masih valid
- [ ] Test: email worker retry behavior saat SMTP gagal

**Exit Criteria**: Mahasiswa dan admin menerima notifikasi in-app dan email untuk semua event penting. Queue bersih dari data sampah secara periodik.



---

*Dokumen ini adalah living document. Setiap perubahan scope atau acceptance criteria harus di-commit langsung di file ini.*