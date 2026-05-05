#set page(paper: "a4", flipped: true, margin: 1cm)
#set text(font: "New Computer Modern", size: 10pt)
#set par(justify: true)

// Allow line-breaks after hyphens/underscores so long tokens (UUIDs,
// SNAKE_CASE constants) wrap instead of overflowing the cell.
#show regex("[-_]"): it => it + "\u{200B}"

#align(center)[
  #text(size: 14pt, weight: "bold")[
    Test Case Backend --- IPB Internship and Career Tracker
  ]
]

#v(0.5em)

== Skenario Pengujian (10 Positive + 10 Negative)

#table(
  columns: (0.8cm, 2.2cm, 3.7cm, 4.2cm, 5cm, 4.2cm, 4.8cm, 1.7cm),
  align: (center + horizon, center + horizon, left + horizon, left + horizon, left + horizon, left + horizon, left + horizon, center + horizon),
  stroke: 0.6pt,
  inset: 5pt,

  // ── Header ────────────────────────────────────────────────────────────────
  table.header(
    [*No*],
    [*Fitur Utama*],
    [*ID Test Case*],
    [*Tujuan*],
    [*Langkah-langkah*],
    [*Data Input*],
    [*Expected Result*],
    [*Status*],
  ),

  // ══════════════════════════════════════════════════════════════════════════
  //  LOGIN (3 rows: 1 positive, 2 negative)
  // ══════════════════════════════════════════════════════════════════════════

  // 1 - Login sukses
  [1.],
  table.cell(rowspan: 3)[LOGIN],
  [TC_LOGIN_001],
  [Menguji login sukses dengan kredensial valid],
  [
    1. Buka halaman login. \
    2. Masukkan email dan password valid. \
    3. Klik "Login".
  ],
  [
    Email: student\@ipb.ac.id \
    Password: Password123
  ],
  [HTTP 200, mengembalikan access\_token, refresh\_token, dan data user],
  [Passed],

  // 2 - Login password salah
  [2.],
  [TC_LOGIN_002],
  [Menguji login ditolak ketika password salah],
  [
    1. Buka halaman login. \
    2. Masukkan email valid + password salah. \
    3. Klik "Login".
  ],
  [
    Email: student\@ipb.ac.id \
    Password: wrong
  ],
  [HTTP 401, pesan "Email atau password salah"],
  [Passed],

  // 3 - Login akun nonaktif
  [3.],
  [TC_LOGIN_003],
  [Menguji login ditolak untuk akun yang dinonaktifkan],
  [
    1. Gunakan akun is\_active = false. \
    2. POST /api/v1/auth/login.
  ],
  [
    Email: nonaktif\@ipb.ac.id \
    Password: Password123
  ],
  [HTTP 401, pesan "Akun dinonaktifkan. Hubungi admin."],
  [Passed],

  // ══════════════════════════════════════════════════════════════════════════
  //  REGISTER (3 rows: 1 positive, 2 negative)
  // ══════════════════════════════════════════════════════════════════════════

  // 4 - Register student sukses
  [4.],
  table.cell(rowspan: 3)[REGISTER],
  [TC_REGISTER_001],
  [Menguji registrasi mahasiswa baru dengan data valid],
  [
    1. Buka halaman registrasi. \
    2. Isi form (email, password, NIM, nama, semester). \
    3. Klik "Daftar".
  ],
  [
    Email: mahasiswa\@ipb.ac.id \
    NIM: G1234567890 \
    Password: Password123
  ],
  [HTTP 201, akun terbuat dengan role STUDENT],
  [Passed],

  // 5 - Register email duplikat
  [5.],
  [TC_REGISTER_002],
  [Menguji registrasi gagal jika email sudah terdaftar],
  [
    1. Daftarkan email pertama. \
    2. Daftarkan email yang sama lagi.
  ],
  [
    Email: mahasiswa\@ipb.ac.id (sudah ada)
  ],
  [HTTP 409, pesan "Email sudah terdaftar"],
  [Passed],

  // 6 - Register field hilang
  [6.],
  [TC_REGISTER_003],
  [Menguji validasi schema saat field NIM tidak dikirim],
  [
    1. Kirim payload register tanpa NIM. \
    2. Periksa response.
  ],
  [
    Email + password + nama (NIM dihilangkan)
  ],
  [HTTP 422, validation error dari Pydantic],
  [Passed],

  // ══════════════════════════════════════════════════════════════════════════
  //  AUTH (1 row: 1 negative)
  // ══════════════════════════════════════════════════════════════════════════

  // 7 - Reset password token expired
  [7.],
  [AUTH],
  [TC_AUTH_001],
  [Menguji reset password dengan token kadaluarsa ditolak],
  [
    1. POST /api/v1/auth/password/reset dengan token expired. \
    2. Periksa response.
  ],
  [
    token: expired\_token \
    new\_password: NewPass456
  ],
  [HTTP 400, pesan "Token tidak valid atau sudah expired"],
  [Passed],

  // ══════════════════════════════════════════════════════════════════════════
  //  PROFILE (3 rows: 2 positive, 1 negative)
  // ══════════════════════════════════════════════════════════════════════════

  // 8 - Get profile sukses
  [8.],
  table.cell(rowspan: 3)[PROFILE],
  [TC_PROFILE_001],
  [Menguji student dapat melihat profilnya sendiri],
  [
    1. Login sebagai student. \
    2. Akses GET /api/v1/profile/me.
  ],
  [
    Authorization: Bearer \<token student\>
  ],
  [HTTP 200, data profil lengkap (NIM, nama, departemen, skills) tampil],
  [Passed],

  // 9 - Update CV data sukses
  [9.],
  [TC_PROFILE_002],
  [Menguji update data CV student sukses],
  [
    1. Login sebagai student. \
    2. Kirim PUT /api/v1/profile/cv-data dengan payload valid. \
    3. Periksa response.
  ],
  [
    phone: +6281234567890 \
    linkedin\_url: valid \
    skills: \[\{id, level: 4\}\]
  ],
  [HTTP 200, pesan "Data CV berhasil diperbarui"],
  [Passed],

  // 10 - Upload CV bukan PDF
  [10.],
  [TC_PROFILE_003],
  [Menguji upload CV ditolak jika file bukan PDF],
  [
    1. Login student. \
    2. POST /api/v1/profile/student/cv dengan file .txt.
  ],
  [
    file: dummy.txt (text/plain)
  ],
  [HTTP 400, pesan "File harus berformat PDF"],
  [Passed],

  // ══════════════════════════════════════════════════════════════════════════
  //  VACANCY (3 rows: 2 positive, 1 negative)
  // ══════════════════════════════════════════════════════════════════════════

  // 11 - Admin create vacancy sukses
  [11.],
  table.cell(rowspan: 3)[VACANCY],
  [TC_VACANCY_001],
  [Menguji admin dapat membuat lowongan baru],
  [
    1. Login sebagai admin. \
    2. POST /api/v1/vacancies dengan data lowongan. \
    3. Periksa response.
  ],
  [
    title: Software Engineer Intern \
    type: INTERNSHIP\_GENERAL \
    company\_id: valid UUID
  ],
  [HTTP 201, lowongan tersimpan dan is\_active = true],
  [Passed],

  // 12 - Get vacancy detail sukses
  [12.],
  [TC_VACANCY_002],
  [Menguji student dapat melihat detail lowongan],
  [
    1. Login sebagai student. \
    2. GET /api/v1/vacancies/\{id\}. \
    3. Periksa response.
  ],
  [
    vacancy\_id: ffffffff-ffff-ffff-ffff-ffffffffffff
  ],
  [HTTP 200, detail lowongan beserta info perusahaan tampil],
  [Passed],

  // 13 - Student create vacancy forbidden
  [13.],
  [TC_VACANCY_003],
  [Menguji student tidak boleh membuat lowongan baru],
  [
    1. Login sebagai student. \
    2. POST /api/v1/vacancies dengan payload lowongan.
  ],
  [
    Authorization: Bearer \<token student\>
  ],
  [HTTP 403, akses ditolak (role bukan ADMIN)],
  [Passed],

  // ══════════════════════════════════════════════════════════════════════════
  //  APPLICATION (3 rows: 1 positive, 2 negative)
  // ══════════════════════════════════════════════════════════════════════════

  // 14 - Apply vacancy sukses
  [14.],
  table.cell(rowspan: 3)[APPLICATION],
  [TC_APPLY_001],
  [Menguji student dapat melamar lowongan setelah upload CV],
  [
    1. Login sebagai student dengan CV terupload. \
    2. POST /api/v1/applications. \
    3. Periksa response.
  ],
  [
    vacancy\_id: 11111111-1111-1111-1111-111111111111
  ],
  [HTTP 201, application dibuat dengan status APPLIED],
  [Passed],

  // 15 - Apply tanpa CV
  [15.],
  [TC_APPLY_002],
  [Menguji apply ditolak ketika student belum upload CV],
  [
    1. Login student tanpa CV. \
    2. POST /api/v1/applications.
  ],
  [
    vacancy\_id: valid UUID \
    cv\_url: belum ada
  ],
  [HTTP 400, pesan "You must upload a CV before applying"],
  [Passed],

  // 16 - Apply duplikat
  [16.],
  [TC_APPLY_003],
  [Menguji apply ditolak jika sudah pernah melamar lowongan yang sama],
  [
    1. Login student yang sudah pernah apply. \
    2. POST /api/v1/applications dengan vacancy\_id sama.
  ],
  [
    vacancy\_id: lowongan yang sudah dilamar
  ],
  [HTTP 400, pesan "You have already applied to this vacancy"],
  [Passed],

  // ══════════════════════════════════════════════════════════════════════════
  //  WISHLIST (2 rows: 1 positive, 1 negative)
  // ══════════════════════════════════════════════════════════════════════════

  // 17 - Add wishlist sukses
  [17.],
  table.cell(rowspan: 2)[WISHLIST],
  [TC_WISHLIST_001],
  [Menguji student dapat menambahkan lowongan ke wishlist],
  [
    1. Login sebagai student. \
    2. POST /api/v1/wishlist. \
    3. Periksa response.
  ],
  [
    vacancy\_id: valid UUID \
    notes: "Lowongan menarik"
  ],
  [HTTP 201, wishlist tersimpan dengan vacancy\_id sesuai],
  [Passed],

  // 18 - Wishlist duplikat
  [18.],
  [TC_WISHLIST_002],
  [Menguji penolakan saat menambahkan lowongan yang sudah ada di wishlist],
  [
    1. Login student. \
    2. POST /api/v1/wishlist dengan vacancy\_id yang sudah ada.
  ],
  [
    vacancy\_id: lowongan yang sudah di wishlist
  ],
  [HTTP 400, pesan "Lowongan sudah ada di wishlist"],
  [Passed],

  // ══════════════════════════════════════════════════════════════════════════
  //  DOCUMENT (1 row: 1 positive)
  // ══════════════════════════════════════════════════════════════════════════

  // 19 - Document request sukses
  [19.],
  [DOCUMENT],
  [TC_DOC_001],
  [Menguji request pembuatan cover letter sukses],
  [
    1. Login sebagai student. \
    2. POST /api/v1/document-requests. \
    3. Periksa response.
  ],
  [
    document\_type: COVER\_LETTER \
    purpose: "Melamar Data Analyst"
  ],
  [HTTP 201, document\_id dikembalikan dan task Celery di-trigger],
  [Passed],

  // ══════════════════════════════════════════════════════════════════════════
  //  ADMIN (1 row: 1 positive)
  // ══════════════════════════════════════════════════════════════════════════

  // 20 - Admin toggle user active sukses
  [20.],
  [ADMIN],
  [TC_ADMIN_001],
  [Menguji admin dapat menonaktifkan akun user],
  [
    1. Login sebagai admin. \
    2. PATCH /api/v1/admin/users/\{id\}/toggle-active. \
    3. Periksa response.
  ],
  [
    user\_id: UUID student valid
  ],
  [HTTP 200, status is\_active user berubah],
  [Passed],
)

#v(1em)

#text(size: 9pt)[
  *Catatan:* Semua skenario di atas merupakan test case yang sudah
  diimplementasikan pada direktori `backend/tests/` dan telah lulus
  (passed) saat dijalankan dengan `pytest`.
]
