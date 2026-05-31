# Use Case Description - Sistem LARAS

Dokumen ini berisi penjelasan detail untuk masing-masing Use Case yang terdapat dalam Use Case Diagram sistem LARAS (Layanan Administrasi Rekrutmen & Magang Mahasiswa).

---

## 1. Mengelola Profil & CV

| Field | Description |
|---|---|
| **Use Case Name** | Mengelola Profil & CV |
| **Scenario** | Mahasiswa melengkapi dan memperbarui data diri serta mengunggah CV untuk keperluan melamar magang. |
| **Triggering Event** | Mahasiswa baru mendaftar atau ingin memperbarui kualifikasinya di halaman profil. |
| **Brief Description** | Use case yang memungkinkan mahasiswa untuk mengelola identitas, riwayat pendidikan, dan mengunggah CV dalam format PDF. |
| **Actor** | Mahasiswa |
| **Related Use Case(s)** | `<<include>>` Mengevaluasi Kecocokan Lowongan Otomatis |
| **Stakeholders** | Mahasiswa (pengguna utama), Administrator |
| **Precondition(s)** | Mahasiswa telah login ke dalam sistem LARAS. |
| **Postcondition(s)** | Data profil tersimpan dan file CV berhasil diunggah ke storage. |
| **Flow of Activities** | 1. Mahasiswa membuka halaman profil.<br>2. Mahasiswa mengisi/memperbarui data diri.<br>3. Mahasiswa mengunggah file CV.<br>4. Sistem menyimpan pembaruan profil.<br>5. Sistem memicu proses ekstraksi keahlian (skill) otomatis dari CV (Use Case terpisah). |
| **Exception Condition** | Format CV salah (bukan PDF) atau ukuran melebihi batas (error akan ditampilkan). |

---

## 2. Mengevaluasi Kecocokan Lowongan Otomatis

| Field | Description |
|---|---|
| **Use Case Name** | Mengevaluasi Kecocokan Lowongan Otomatis |
| **Scenario** | Sistem membaca CV mahasiswa dan mencocokkan keahliannya dengan persyaratan lowongan. |
| **Triggering Event** | Terpicu secara otomatis ketika mahasiswa mengunggah CV. |
| **Brief Description** | Fitur AI/otomasi sistem untuk mengekstrak keahlian (skills) dari teks CV mahasiswa dan menyimpannya di basis data untuk dihitung persentase kecocokannya dengan kualifikasi lowongan. |
| **Actor** | Sistem (Background Process) |
| **Related Use Case(s)** | Di-`<<include>>` oleh Mengelola Profil & CV |
| **Stakeholders** | Mahasiswa |
| **Precondition(s)** | Mahasiswa berhasil mengunggah CV. |
| **Postcondition(s)** | Tabel `student_skills` mahasiswa diperbarui dengan hasil ekstraksi teks CV. |
| **Flow of Activities** | 1. Sistem menerima input file CV.<br>2. Sistem (background worker) membaca teks dari PDF.<br>3. Sistem mencocokkan teks dengan `Master Skills`.<br>4. Sistem menyimpan keahlian yang terdeteksi ke profil mahasiswa. |
| **Exception Condition** | Teks CV tidak dapat dibaca karena terenkripsi atau format PDF rusak (sistem mengabaikan ekstraksi dan skill dikosongkan). |

---

## 3. Mencari Lowongan

| Field | Description |
|---|---|
| **Use Case Name** | Mencari Lowongan |
| **Scenario** | Mahasiswa menelusuri katalog lowongan magang yang tersedia. |
| **Triggering Event** | Mahasiswa mengakses halaman pencarian lowongan. |
| **Brief Description** | Memungkinkan mahasiswa untuk melihat, memfilter, mencari lowongan berdasarkan posisi atau perusahaan, dan melihat detail kecocokan persentase skill. |
| **Actor** | Mahasiswa |
| **Related Use Case(s)** | Di-`<<extend>>` oleh Menyimpan Lowongan (Bookmark/Wishlist) |
| **Stakeholders** | Mahasiswa |
| **Precondition(s)** | Mahasiswa sudah login ke sistem. |
| **Postcondition(s)** | Mahasiswa menemukan lowongan yang diminati. |
| **Flow of Activities** | 1. Mahasiswa membuka halaman pencarian.<br>2. Sistem menampilkan daftar lowongan yang rilis (terverifikasi).<br>3. Mahasiswa memasukkan kata kunci pencarian atau memilih filter.<br>4. Sistem menampilkan hasil pencarian beserta persentase kecocokan skill.<br>5. Mahasiswa mengeklik lowongan untuk melihat detail. |
| **Exception Condition** | Tidak ada lowongan yang sesuai dengan kata kunci (Sistem menampilkan pesan "Data tidak ditemukan"). |

---

## 4. Menyimpan Lowongan (Bookmark/Wishlist)

| Field | Description |
|---|---|
| **Use Case Name** | Menyimpan Lowongan (Bookmark/Wishlist) |
| **Scenario** | Mahasiswa menandai lowongan untuk dilihat atau dilamar nanti. |
| **Triggering Event** | Mahasiswa menekan tombol ikon "Simpan" (Bookmark) pada kartu lowongan. |
| **Brief Description** | Mahasiswa dapat menyimpan lowongan magang ke dalam daftar wishlist pribadinya. |
| **Actor** | Mahasiswa |
| **Related Use Case(s)** | `<<extend>>` Mencari Lowongan |
| **Stakeholders** | Mahasiswa |
| **Precondition(s)** | Mahasiswa sedang melihat daftar lowongan atau detail lowongan. |
| **Postcondition(s)** | Lowongan tersimpan di halaman Wishlist mahasiswa. |
| **Flow of Activities** | 1. Mahasiswa melihat suatu lowongan yang menarik.<br>2. Mahasiswa menekan tombol simpan/bookmark.<br>3. Sistem menambahkan lowongan tersebut ke tabel `student_wishlist_vacancies`. |
| **Exception Condition** | Jika lowongan sudah ditutup, tombol bookmark dinonaktifkan. |

---

## 5. Mengajukan Lamaran

| Field | Description |
|---|---|
| **Use Case Name** | Mengajukan Lamaran |
| **Scenario** | Mahasiswa mengirimkan lamaran ke perusahaan pada lowongan yang dipilih. |
| **Triggering Event** | Mahasiswa menekan tombol "Lamar" pada detail lowongan. |
| **Brief Description** | Proses utama mahasiswa melamar pekerjaan. Mahasiswa memilih opsi penggunaan CV, menambahkan dokumen pelengkap, dan menyetujui syarat pelamaran. |
| **Actor** | Mahasiswa |
| **Related Use Case(s)** | `<<include>>` Melaporkan Status Lamaran<br>Di-`<<extend>>` oleh Mengajukan Surat Pengantar |
| **Stakeholders** | Mahasiswa, Administrator |
| **Precondition(s)** | Mahasiswa sudah memiliki CV dan melengkapi profil dasar. |
| **Postcondition(s)** | Lamaran baru terbentuk di database dengan status `PENDING`. |
| **Flow of Activities** | 1. Mahasiswa berada di detail lowongan.<br>2. Mahasiswa mengeklik "Lamar Sekarang".<br>3. Sistem menampilkan formulir konfirmasi lamaran.<br>4. Mahasiswa mengirimkan lamaran.<br>5. Sistem memicu pembuatan status lamaran awal (Melaporkan Status Lamaran - Include). |
| **Exception Condition** | Jika profil mahasiswa tidak lengkap atau belum ada CV, sistem membatalkan proses dan meminta mahasiswa melengkapi profil terlebih dahulu. |

---

## 6. Mengajukan Surat Pengantar

| Field | Description |
|---|---|
| **Use Case Name** | Mengajukan Surat Pengantar |
| **Scenario** | Mahasiswa yang membutuhkan surat rekomendasi resmi dari kampus (Fakultas/Departemen) dapat memintanya saat melamar. |
| **Triggering Event** | Mahasiswa memilih opsi "Butuh Surat Pengantar" saat mengisi form pengajuan lamaran. |
| **Brief Description** | Opsi tambahan ketika melamar magang. Apabila perusahaan membutuhkan dokumen legal institusi, mahasiswa memintanya melalui use case ini. |
| **Actor** | Mahasiswa |
| **Related Use Case(s)** | `<<extend>>` Mengajukan Lamaran<br>`<<include>>` Membuat Surat Otomatis Berdasarkan Template |
| **Stakeholders** | Mahasiswa, Administrator |
| **Precondition(s)** | Mahasiswa sedang dalam alur pengajuan lamaran magang. |
| **Postcondition(s)** | Permintaan dokumen surat pengantar (Document Request) terbuat di sistem dan berstatus pending. |
| **Flow of Activities** | 1. Saat melamar, mahasiswa mencentang kebutuhan surat pengantar.<br>2. Mahasiswa mengisi rincian penerima surat (nama PIC perusahaan, jabatan).<br>3. Mahasiswa menekan Submit.<br>4. Sistem men-trigger otomatis pembuatan draft surat (Include). |
| **Exception Condition** | Form detail PIC perusahaan kosong sehingga permintaan ditolak (validation error). |

---

## 7. Membuat Surat Otomatis Berdasarkan Template

| Field | Description |
|---|---|
| **Use Case Name** | Membuat Surat Otomatis Berdasarkan Template |
| **Scenario** | Sistem menyusun draf dokumen surat dengan mengisi variabel dari data mahasiswa. |
| **Triggering Event** | Mahasiswa selesai mensubmit permintaan surat pengantar. |
| **Brief Description** | Generator otomatis untuk memadukan data diri mahasiswa (Nama, NIM, Departemen) dengan template baku surat pengantar institusi. |
| **Actor** | Sistem |
| **Related Use Case(s)** | Di-`<<include>>` oleh Mengajukan Surat Pengantar |
| **Stakeholders** | Mahasiswa, Administrator |
| **Precondition(s)** | Mahasiswa berhasil melakukan request dokumen. |
| **Postcondition(s)** | Draf dokumen PDF/Docx tergenerate siap diunduh atau diproses oleh Admin. |
| **Flow of Activities** | 1. Sistem menerima payload data mahasiswa dan tujuan surat.<br>2. Sistem memuat template surat yang sudah ditetapkan.<br>3. Sistem menyuntikkan data mahasiswa ke template.<br>4. File surat disimpan ke server. |
| **Exception Condition** | Jika template surat di server hilang, proses gagal dan status request ditandai sebagai ERROR. |

---

## 8. Melaporkan Status Lamaran

| Field | Description |
|---|---|
| **Use Case Name** | Melaporkan Status Lamaran |
| **Scenario** | Mahasiswa melakukan self-reporting progres rekrutmen magangnya (contoh: PENDING -> INTERVIEW -> OFFERED). |
| **Triggering Event** | Mahasiswa mendapatkan pembaruan status dari perusahaan dan meng-update-nya di sistem LARAS. |
| **Brief Description** | Proses pembaruan riwayat status lamaran. Mahasiswa bertanggung jawab untuk melaporkan secara mandiri tahapan seleksi hingga sampai menerima tawaran kerja magang (LoA/Offering Letter). |
| **Actor** | Mahasiswa |
| **Related Use Case(s)** | Di-`<<include>>` oleh Mengajukan Lamaran<br>Di-`<<extend>>` oleh Memverifikasi Bukti Penerimaan |
| **Stakeholders** | Mahasiswa, Administrator |
| **Precondition(s)** | Mahasiswa telah mengirimkan minimal 1 lamaran. |
| **Postcondition(s)** | Status lamaran di database berubah sesuai dengan inputan mahasiswa. |
| **Flow of Activities** | 1. Mahasiswa membuka tab "Lamaran Saya".<br>2. Mahasiswa memilih lamaran yang ingin diperbarui.<br>3. Mahasiswa memilih status terbaru (misal: "Offered").<br>4. Mahasiswa mengunggah bukti/Letter of Acceptance (LoA) (Jika mengubah status ke Offered).<br>5. Sistem menyimpan perubahan. |
| **Exception Condition** | Jika mahasiswa tidak melampirkan bukti LoA saat status diubah ke "Offered", sistem menolak perubahan. |

---

## 9. Memverifikasi Bukti Penerimaan

| Field | Description |
|---|---|
| **Use Case Name** | Memverifikasi Bukti Penerimaan |
| **Scenario** | Administrator meninjau bukti Letter of Acceptance (LoA) yang diunggah mahasiswa. |
| **Triggering Event** | Mahasiswa mengubah status lamarannya menjadi "OFFERED" dan melampirkan bukti LoA. |
| **Brief Description** | Admin memvalidasi keabsahan dokumen penerimaan. Jika valid, lamaran akan ditandai ACCEPTED dan secara otomatis sistem akan meng-generate "Placement (Data Penempatan)". |
| **Actor** | Administrator |
| **Related Use Case(s)** | `<<extend>>` Melaporkan Status Lamaran |
| **Stakeholders** | Administrator, Mahasiswa |
| **Precondition(s)** | Terdapat lamaran mahasiswa yang berstatus "OFFERED" menunggu verifikasi. |
| **Postcondition(s)** | Status lamaran berubah menjadi ACCEPTED dan data Penempatan (Placement) terbentuk di tabel `placements`. |
| **Flow of Activities** | 1. Admin masuk ke menu "Verifikasi".<br>2. Admin membuka detail lamaran dengan status OFFERED.<br>3. Admin mengunduh/melihat dokumen LoA.<br>4. Admin mengisi periode mulai/selesai magang berdasarkan dokumen.<br>5. Admin mengeklik tombol "Terima Lamaran (Verify)".<br>6. Sistem membuat entitas Placement untuk mahasiswa. |
| **Exception Condition** | Dokumen LoA palsu atau tidak terbaca: Admin mengeklik "Tolak Bukti" sehingga status mahasiswa kembali ke status sebelumnya, dan data Placement tidak dibuat. |

---

## 10. Mengisi Jurnal Harian (Jika Magang Aktif)

| Field | Description |
|---|---|
| **Use Case Name** | Mengisi Jurnal Harian |
| **Scenario** | Mahasiswa secara berkala mencatat aktivitas yang dilakukannya di tempat magang. |
| **Triggering Event** | Mahasiswa ingin melaporkan progres aktivitas hariannya. |
| **Brief Description** | Form pengisian logbook harian (activity logs). Mahasiswa menulis tanggal, durasi jam kerja, dan rincian pekerjaan. Data jurnal dapat disempurnakan dengan bantuan AI. |
| **Actor** | Mahasiswa |
| **Related Use Case(s)** | `<<include>>` Mengisi Laporan Magang |
| **Stakeholders** | Mahasiswa, Administrator/Dosen Pembimbing |
| **Precondition(s)** | Mahasiswa memiliki data "Placement" yang aktif (berstatus ACTIVE). |
| **Postcondition(s)** | Entitas Jurnal (Activity Log) baru tersimpan untuk Placement tersebut. |
| **Flow of Activities** | 1. Mahasiswa membuka halaman Penempatan Aktif.<br>2. Mahasiswa mengeklik "Tambah Jurnal".<br>3. Mahasiswa mengisi tanggal, jam, dan deskripsi kegiatan mentah.<br>4. (Opsional) Mahasiswa mengeklik "Enhance dengan AI" untuk merapikan kalimat.<br>5. Mahasiswa menyimpan jurnal. |
| **Exception Condition** | Tanggal jurnal tidak valid (di luar periode magang) atau data isian wajib ada yang kosong. Sistem menolak dan menampilkan validasi error. |

---

## 11. Mengisi Laporan Magang

| Field | Description |
|---|---|
| **Use Case Name** | Mengisi Laporan Magang |
| **Scenario** | Kumpulan jurnal harian akan dirangkum sebagai bagian tak terpisahkan dari pelaporan akhir. |
| **Triggering Event** | Mahasiswa selesai menjalani masa magang dan perlu membuat rekap laporan. |
| **Brief Description** | Berisi proses kompilasi seluruh aktivitas selama magang dari awal hingga akhir periode magang. |
| **Actor** | Mahasiswa |
| **Related Use Case(s)** | Di-`<<include>>` oleh Mengisi Jurnal Harian<br>Di-`<<extend>>` oleh Mengunduh Hasil Laporan Terstruktur dengan AI |
| **Stakeholders** | Mahasiswa, Administrator |
| **Precondition(s)** | Mahasiswa memiliki catatan Jurnal Harian. |
| **Postcondition(s)** | Sistem memiliki rekap keseluruhan data laporan akhir mahasiswa. |
| **Flow of Activities** | 1. Mahasiswa memastikan seluruh jurnal harian telah terisi lengkap.<br>2. Sistem merekap otomatis data-data jurnal.<br>3. Mahasiswa me-review kompilasi laporan (Include Use Case). |
| **Exception Condition** | Jika tidak ada jurnal sama sekali, laporan magang dinyatakan kosong. |

---

## 12. Mengunduh Hasil Laporan Terstruktur dengan AI

| Field | Description |
|---|---|
| **Use Case Name** | Mengunduh Hasil Laporan Terstruktur dengan AI |
| **Scenario** | Mahasiswa menekan tombol Generate Laporan, dan AI merangkum semua jurnal menjadi PDF format resmi. |
| **Triggering Event** | Mahasiswa mengeklik tombol "Generate Report" pada dashboard placement. |
| **Brief Description** | Sistem memanggil AI (LLM) untuk membaca seluruh log aktivitas, merangkum pencapaian utama, dan menuliskannya dalam format laporan akhir berstandar kampus yang dapat diunduh (PDF). |
| **Actor** | Mahasiswa |
| **Related Use Case(s)** | `<<extend>>` Mengisi Laporan Magang |
| **Stakeholders** | Mahasiswa |
| **Precondition(s)** | Mahasiswa setidaknya memiliki 1 atau lebih Jurnal Harian pada penempatannya. |
| **Postcondition(s)** | File laporan magang (PDF) berhasil dihasilkan dan link download tersedia. |
| **Flow of Activities** | 1. Mahasiswa mengeklik "Buat Laporan Final".<br>2. Background job (Celery) mengambil seluruh jurnal mahasiswa.<br>3. AI LLM membuat summary eksekutif dan memformat tabel kegiatan.<br>4. Sistem men-generate PDF.<br>5. Mahasiswa mengunduh PDF tersebut. |
| **Exception Condition** | Limit AI tercapai atau proses gagal. Mahasiswa menerima notifikasi error dan dapat mencoba men-generate ulang. |

---

## 13. Input Data Lowongan

| Field | Description |
|---|---|
| **Use Case Name** | Input Data Lowongan |
| **Scenario** | Admin mengelola data lowongan perusahaan yang masuk. |
| **Triggering Event** | Admin butuh memasukkan daftar loker terbaru ke dalam platform. |
| **Brief Description** | Use case tingkat atas yang mewadahi proses pembuatan data lowongan baru. Dapat dilakukan dengan Input Manual atau menggunakan metode Scraping. |
| **Actor** | Administrator |
| **Related Use Case(s)** | `<<include>>` Input Manual<br>Di-`<<extend>>` oleh Scraping URL |
| **Stakeholders** | Administrator |
| **Precondition(s)** | Admin sudah login ke dashboard admin LARAS. |
| **Postcondition(s)** | Lowongan baru tersimpan ke dalam database. |
| **Flow of Activities** | 1. Admin masuk ke halaman Kelola Lowongan.<br>2. Admin memilih metode penambahan lowongan.<br>3. Admin memasukkan data.<br>4. Sistem menyimpan lowongan tersebut (default status: belum rilis/draf). |
| **Exception Condition** | Gagal terhubung ke database. |

---

## 14. Input Manual

| Field | Description |
|---|---|
| **Use Case Name** | Input Manual |
| **Scenario** | Admin mengetik secara manual judul, deskripsi, gaji, serta tanggal lowongan magang. |
| **Triggering Event** | Admin memilih "Tambah Manual" di menu Lowongan. |
| **Brief Description** | Pembuatan lowongan dengan form standar di mana admin harus mengisi semua informasi dari awal tanpa bantuan otomasi. |
| **Actor** | Administrator |
| **Related Use Case(s)** | Di-`<<include>>` oleh Input Data Lowongan |
| **Stakeholders** | Administrator |
| **Precondition(s)** | Admin berada di halaman tambah lowongan. |
| **Postcondition(s)** | Lowongan tersimpan di database. |
| **Flow of Activities** | 1. Admin memilih instansi/perusahaan dari Master Data.<br>2. Admin mengetikkan Posisi, Deskripsi, Tanggal Buka-Tutup, dan Lokasi.<br>3. Admin memilih Kebutuhan Skill (Opsional).<br>4. Admin menekan Simpan. |
| **Exception Condition** | Admin lupa mengisi kolom wajib seperti Judul, sistem memberikan peringatan validasi pada UI. |

---

## 15. Scraping URL

| Field | Description |
|---|---|
| **Use Case Name** | Scraping URL |
| **Scenario** | Admin hanya perlu memasukkan link lowongan dari job portal luar (ex: Kalibrr, Glints), dan sistem mengekstrak detailnya secara otomatis. |
| **Triggering Event** | Admin mengeklik tombol "Scrape Lowongan" dan memasukkan daftar URL. |
| **Brief Description** | Fitur otomatisasi administrasi (data entry). Sistem memanggil worker background untuk membaca metadata JSON-LD pada link yang diberikan dan mengimpornya sebagai Draf Lowongan. |
| **Actor** | Administrator |
| **Related Use Case(s)** | `<<extend>>` Input Data Lowongan |
| **Stakeholders** | Administrator |
| **Precondition(s)** | Admin menyalin link URL lowongan dari portal eksternal. |
| **Postcondition(s)** | Satu atau lebih lowongan draf berhasil diimpor beserta kecocokan tag skill yang otomatis terdeteksi. |
| **Flow of Activities** | 1. Admin membuka modal Scraping.<br>2. Admin mem-paste URL (bisa lebih dari satu, multiline).<br>3. Admin mengeklik Mulai Scraping.<br>4. Sistem mendelegasikan tugas ke worker background (Celery).<br>5. Worker memproses URL, membaca atribut, dan menyimpannya ke DB. |
| **Exception Condition** | Struktur web tidak dikenali atau error timeout koneksi: Sistem menyimpan informasi bahwa link URL tersebut "Gagal (Failed)" pada laporan hasil scraping. |

---

## 16. Mempublikasi Lowongan Terverifikasi

| Field | Description |
|---|---|
| **Use Case Name** | Mempublikasi Lowongan Terverifikasi |
| **Scenario** | Lowongan draf (hasil manual atau scraping) dihidupkan (diaktifkan) agar bisa dilihat mahasiswa. |
| **Triggering Event** | Admin mengubah status lowongan menjadi "Publik" / Aktif. |
| **Brief Description** | Use Case kurasi dan aktivasi. Lowongan yang ada di platform belum bisa dilamar sampai Admin meyakini data tersebut kredibel dan mempublikasikannya. |
| **Actor** | Administrator |
| **Related Use Case(s)** | Tidak ada |
| **Stakeholders** | Administrator, Mahasiswa |
| **Precondition(s)** | Ada setidaknya 1 lowongan dengan status Inactive (is_active = False). |
| **Postcondition(s)** | Lowongan berubah menjadi is_active = True dan langsung tampil di halaman pencarian mahasiswa. |
| **Flow of Activities** | 1. Admin meninjau data lowongan pada mode edit.<br>2. Admin mengeklik "Publikasikan Lowongan".<br>3. Sistem memperbarui atribut is_active menjadi True.<br>4. Mahasiswa dapat langsung melamar lowongan tersebut. |
| **Exception Condition** | Jika tanggal close (penutupan) lowongan sudah lewat di hari saat dipublikasi, sistem akan memperingatkan admin untuk memperpanjang tanggal penutupan. |

---

## Pemetaan User Story & Prioritas Implementasi

Tabel berikut menjelaskan pemetaan antara User Story, Fitur yang diimplementasikan, serta tingkat prioritas beserta justifikasi singkatnya.

| User Story | Fitur yang diimplementasikan | Prioritas & Alasan |
|---|---|---|
| Mahasiswa ingin sistem otomatis mengekstrak CV dan mencocokkannya dengan lowongan. | **AI Resume Parser & Skill Matching** | **Tinggi** - Menghemat waktu pencarian lowongan yang paling sesuai dengan kompetensi. |
| Mahasiswa ingin melacak status lamaran dari awal hingga diterima di satu tempat. | **Self-Reported ATS (Applicant Tracking System)** | **Tinggi** - Bebas dari kerumitan mengecek status rekrutmen di berbagai website atau email. |
| Admin ingin memverifikasi LoA untuk mengotomatisasi data penempatan magang. | **Verifikasi Bukti & Auto-Placement** | **Tinggi** - Membebaskan admin dari tugas rekap data mahasiswa magang secara manual. |
| Mahasiswa ingin merapikan bahasa logbook harian ke standar profesional otomatis. | **AI Logbook Enhancement** | **Menengah** - Laporan harian instan rapi dan profesional tanpa repot merangkai kata. |
| Admin ingin mengimpor data lowongan kerja bermodal tautan (URL) saja. | **Automated Vacancy Scraping** | **Menengah** - Memangkas drastis waktu administrasi dan *copy-paste* dari portal eksternal. |
| Mahasiswa ingin meminta surat pengantar kampus secara langsung saat melamar. | **Automated Document Request** | **Menengah** - Memotong birokrasi fisik; tidak perlu repot antre ke loket tata usaha. |
| Mahasiswa ingin otomatis merangkum log harian menjadi draf laporan PDF. | **AI Final Report Generation** | **Rendah** - Sangat praktis, namun kepentingannya hanya terjadi sekali di akhir siklus magang. |
