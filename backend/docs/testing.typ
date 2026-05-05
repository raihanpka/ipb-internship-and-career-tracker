#set page(paper: "a4", margin: 1.5cm)
#set text(font: "New Computer Modern", size: 10pt)
#set par(justify: true)

#align(center)[
  #text(size: 14pt, weight: "bold")[
    Test Case Backend --- IPB Internship and Career Tracker
  ]
]

#v(0.5em)

== Skenario Pengujian (10 Positive + 10 Negative)

#table(
  columns: (auto, 1.6cm, 2.2cm, 3.2cm, 3.4cm, 3cm, 3cm, 1.6cm),
  align: (center + horizon, left + horizon, left + horizon, left + horizon, left + horizon, left + horizon, left + horizon, center + horizon),
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
  //  POSITIVE TEST CASES (1-10)
  // ══════════════════════════════════════════════════════════════════════════

  // 1 - Login sukses
  [1.],
  [LOGIN],
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

  // 2 - Register student sukses
  [2.],
  [REGISTER],
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

  // 3 - Get profile sukses
  [3.],
  [PROFILE],
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

  // 4 - Update CV data sukses
  [4.],
  [PROFILE],
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
    skills: [\{id, level: 4\}]
  ],
  [HTTP 200, pesan "Data CV berhasil diperbarui"],
  [Passed],

  // 5 - Admin create vacancy sukses
  [5.],
  [VACANCY],
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

  // 6 - Get vacancy detail sukses
  [6.],
  [VACANCY],
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

  // 7 - Apply vacancy sukses
  [7.],
  [APPLICATION],
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

  // 8 - Add wishlist sukses
  [8.],
  [WISHLIST],
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

  // 9 - Document request sukses
  [9.],
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

  // 10 - Admin toggle user active sukses
  [10.],
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

  // ══════════════════════════════════════════════════════════════════════════
  //  NEGATIVE TEST CASES (11-20)
  // ══════════════════════════════════════════════════════════════════════════

  // 11 - Login password salah
  [11.],
  [LOGIN],
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

  // 12 - Login akun nonaktif
  [12.],
  [LOGIN],
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

  // 13 - Register email duplikat
  [13.],
  [REGISTER],
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

  // 14 - Register field hilang
  [14.],
  [REGISTER],
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

  // 15 - Apply tanpa CV
  [15.],
  [APPLICATION],
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
  [APPLICATION],
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

  // 17 - Student create vacancy forbidden
  [17.],
  [VACANCY],
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

  // 18 - Wishlist duplikat
  [18.],
  [WISHLIST],
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

  // 19 - Upload CV bukan PDF
  [19.],
  [PROFILE],
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

  // 20 - Reset password token expired
  [20.],
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
)

#v(1em)

#text(size: 9pt)[
  *Catatan:* Semua skenario di atas merupakan test case yang sudah
  diimplementasikan pada direktori `backend/tests/` dan telah lulus
  (passed) saat dijalankan dengan `pytest`.
]
