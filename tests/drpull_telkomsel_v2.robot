*** Settings ***
Documentation    Suite Pengujian Otomasi Robot Framework untuk drpulltelkomsel v2.0.0 (PB172645152602YA).
...              Migrasi Get Delivery Status V2 (POST + HMAC-SHA256, Secret apps_config, Non-blocking SUT Log Audit).
...              Menerapkan Clean BDD Murni, Zero False Positive, Audit Traceability, dan Idempotent Fencing.
Resource         ../resources/keywords/common_keywords.robot
Resource         ../resources/keywords/drpull_keywords.robot

Suite Setup      Inisialisasi Lingkungan Pengujian Drpull
Suite Teardown   Hentikan Lingkungan Pengujian Drpull
Test Setup       Persiapkan Konteks Pengujian
Test Teardown    Bersihkan Konteks Pengujian

*** Test Cases ***
TC-001 — Pengambilan Status SMS Berhasil (Delivered) dan Penerusan Laporan Hilir
    [Tags]    P0    TC-001    Pilar-1    e2e    happy_path
    Given Terdapat transaksi SMS berstatus PENDING yang menunggu pemeriksaan status
    And Konfigurasi kredensial mitra dan alamat endpoint Telkomsel V2 tersedia secara valid
    When Layanan DR Pull memeriksa status pengiriman ke Telkomsel V2
    Then Telkomsel merespons bahwa pesan berhasil diterima dengan status D
    And Transaksi pada database status diperbarui menjadi RESOLVED
    And Tepat satu pesan laporan pengiriman diteruskan ke antrean laporan DR untuk nomor transaksi tersebut
    And Tepat satu perintah SQL penyimpanan diteruskan ke antrean database executor untuk nomor transaksi tersebut

TC-002 — Pengambilan Status SMS Gagal (Not Delivered) dengan Kode Kesalahan Vendor
    [Tags]    P0    TC-002    Pilar-1    e2e    happy_path
    Given Terdapat transaksi SMS berstatus PENDING yang menunggu pemeriksaan status
    And Konfigurasi kredensial mitra dan alamat endpoint Telkomsel V2 tersedia secara valid
    When Layanan DR Pull memeriksa status pengiriman ke Telkomsel V2
    Then Telkomsel merespons bahwa pesan gagal terkirim dengan status ND dan kode kesalahan 061
    And Transaksi pada database status diperbarui menjadi RESOLVED
    And Laporan pengiriman diteruskan ke antrean laporan DR membawa status komposit ND bertanda kode 061
    And Perintah SQL penyimpanan diteruskan ke antrean database executor dengan rincian kode kesalahan

TC-003 — Kepatuhan Protokol Permintaan Keluar dan Sensitivitas Perhitungan HMAC-SHA256
    [Tags]    P0    TC-003    Pilar-2    security    protocol_conformance
    Given Layanan DR Pull siap melakukan pemeriksaan status ke vendor
    And Transaksi memiliki data nomor referensi transaksi yang valid
    When Permintaan status dikirimkan oleh sistem ke endpoint Telkomsel
    Then Permintaan menggunakan metode POST ke path V2 tanpa parameter pada query string URL
    And Permintaan menyertakan header Content-Type, appsid, sid, X-Timestamp, dan X-Signature yang valid
    And Tanda tangan terbukti sensitif terhadap perubahan komponen teks kanonikal (body, path, timestamp, dan secret)

TC-004 — Penjadwalan Ulang Pemeriksaan Status Saat Transaksi Belum Ditemukan di Vendor
    [Tags]    P1    TC-004    Pilar-4    resilience    retry_backoff
    Given Terdapat transaksi SMS berstatus PENDING dengan riwayat percobaan nol
    When Sistem menanyakan status transaksi ke Telkomsel dan Telkomsel menjawab status belum ditemukan 404
    Then Transaksi tetap berstatus PENDING untuk diperiksa kembali nanti
    And Jumlah percobaan bertambah menjadi satu
    And Waktu pemeriksaan berikutnya dijadwalkan mundur tiga puluh menit sesuai aturan penundaan
    And Tidak ada pesan laporan pengiriman yang diteruskan ke sistem hilir

TC-005 — Penghentian Permanen Transaksi yang Telah Melampaui Batas Maksimum Percobaan
    [Tags]    P1    TC-005    Pilar-4    resilience    max_attempt
    Given Terdapat transaksi SMS berstatus PENDING yang telah mengalami empat kali kegagalan sebelumnya
    When Sistem mencoba memeriksa status untuk kelima kalinya dan Telkomsel tetap menjawab 404
    Then Transaksi diubah statusnya secara permanen menjadi GIVE_UP
    And Nilai riwayat percobaan tetap tercatat empat dan catatan kesalahan menyebutkan batas maksimum terlampaui
    And Sistem tidak lagi menjadwalkan pemeriksaan ulang terhadap transaksi tersebut
    And Tidak ada pesan laporan pengiriman yang diteruskan ke sistem hilir

TC-006 — Penanganan Gangguan Server Vendor 500 Sebagai Kesalahan Sementara
    [Tags]    P1    TC-006    Pilar-4    resilience    retry_backoff
    Given Terdapat transaksi SMS berstatus PENDING yang menunggu pemeriksaan status
    When Sistem memeriksa status dan server Telkomsel mengalami gangguan internal dengan kode 500
    Then Transaksi tidak dinyatakan gagal permanen melainkan tetap berstatus PENDING
    And Jumlah riwayat percobaan bertambah dan waktu pemeriksaan berikutnya dijadwalkan ulang
    And Tidak ada pesan laporan pengiriman yang diteruskan ke sistem hilir

TC-007 — Penanganan Batas Waktu Koneksi Tiga Puluh Detik Secara Mandiri
    [Tags]    P1    TC-007    Pilar-4    resilience    timeout_handling
    Given Layanan DR Pull dikonfigurasi dengan batas waktu pembacaan soket (read timeout) tiga puluh detik
    And Terdapat transaksi SMS berstatus PENDING pada database
    When Sistem memanggil Telkomsel dan Telkomsel tidak merespons dalam tiga puluh detik
    Then Sistem memutus koneksi tepat pada batas waktu pembacaan soket tiga puluh detik
    And Transaksi dijadwalkan untuk dicoba kembali dengan status PENDING
    And Proses pemeriksaan transaksi lainnya tetap berjalan lancar tanpa mengalami kemacetan

TC-008 — Penanganan Format Isi Respons Rusak dengan Sanitasi Batas Karakter
    [Tags]    P1    TC-008    Pilar-4    resilience    data_sanitization
    Given Terdapat transaksi SMS berstatus PENDING pada database
    When Sistem memeriksa status dan Telkomsel menjawab status 200 namun isi pesan bukan format JSON yang benar atau format struktur status hilang
    Then Transaksi dijadwalkan untuk diperiksa ulang dengan status PENDING
    And Catatan kesalahan pada database dibatasi maksimal seratus enam puluh karakter untuk menjaga integritas data
    And Sistem tidak mengalami kesalahan fatal dan dapat melanjutkan pemrosesan berikutnya

TC-009 — Resolusi Kunci Rahasia Berdasarkan Appsid Saat Pasangan Lengkap Tidak Tersedia
    [Tags]    P1    TC-009    Pilar-2    security    secret_resolution
    Given Konfigurasi database memuat kunci khusus appsid tanpa pasangan sid
    And Terdapat transaksi yang memiliki appsid tersebut dengan sid sembarang
    When Sistem mencari kunci rahasia untuk menandatangani permintaan
    Then Kunci rahasia berdasarkan appsid berhasil ditemukan dan digunakan
    And Permintaan berhasil diverifikasi dan diterima oleh vendor Telkomsel

TC-010 — Penggunaan Kunci Rahasia Cadangan Default Saat Pasangan Khusus Tidak Terdaftar
    [Tags]    P1    TC-010    Pilar-2    security    secret_fallback
    Given Konfigurasi memuat daftar kunci khusus untuk mitra lain namun tidak untuk mitra yang sedang diproses
    And Konfigurasi kunci rahasia cadangan default terisi dengan nilai yang valid
    When Sistem memeriksa transaksi milik mitra yang tidak terdaftar pada daftar khusus
    Then Sistem otomatis beralih menggunakan kunci rahasia cadangan default
    And Permintaan berhasil diverifikasi dan diterima dengan sukses oleh vendor Telkomsel

TC-011 — Kompatibilitas Penuh Format Pesan Laporan Pengiriman Hilir
    [Tags]    P0    TC-011    Pilar-1    e2e    downstream_contract
    Given Transaksi berhasil mendapatkan status pengiriman dari Telkomsel
    When Sistem menyusun dan meneruskan laporan ke sistem hilir
    Then Format pesan pada antrean laporan DR memuat parameter URL-encoded yang lengkap dan sesuai standar
    And Format perintah SQL pada antrean database executor sesuai dengan struktur tabel riwayat pelaporan

TC-012 — Penguncian Atomic Tahap Pengambilan Transaksi (Pulling Fence) Mencegah Pemrosesan Ganda
    [Tags]    P0    TC-012    Pilar-4    resilience    concurrency_fencing
    Given Terdapat transaksi SMS berstatus PENDING pada database yang siap diproses
    When Dua instance worker melakukan pemindaian dan mencoba mengambil transaksi tersebut secara bersamaan
    Then Hanya satu worker yang berhasil memenangkan penguncian atomic status PENDING menjadi PULLING
    And Worker kedua gagal mendapatkan penguncian dan membatalkan pemrosesan transaksi tersebut di tahap awal
    And Worker kedua tidak melakukan panggilan HTTP keluar ke vendor untuk transaksi tersebut

TC-013 — Verifikasi Versi Aplikasi 2.0.0, Kesiapan Inisialisasi Layanan dan Keaktifan Scheduler
    [Tags]    P0    TC-013    Pilar-1    architecture    artifact_verification
    Given File biner drpulltelkomsel versi 2.0.0 terpasang pada folder bin server
    When Layanan dijalankan menggunakan skrip start aplikasi
    Then Aplikasi berjalan dengan benar menampilkan identitas versi 2.0.0
    And Catatan inisialisasi pada log bersih dari kesalahan fatal maupun peringatan konfigurasi
    And Komponen scheduler terbukti aktif memindai dan memproses transaksi uji secara normal

TC-014 — Penghentian Permanen Langsung Saat Permintaan Ditolak dengan Kesalahan 400
    [Tags]    P0    TC-014    Pilar-3    negative    fail_fast
    Given Terdapat transaksi SMS berstatus PENDING pada database
    When Sistem memeriksa status dan Telkomsel menolak permintaan dengan kode kesalahan 400 Bad Request
    Then Transaksi pada database seketika diubah statusnya menjadi GIVE_UP secara permanen
    And Riwayat jumlah percobaan tidak bertambah serta tidak ada jadwal pemeriksaan ulang
    And Tidak ada pesan laporan pengiriman yang diteruskan ke sistem hilir

TC-015 — Penghentian Permanen Langsung Saat Metode Ditolak dengan Kode 405
    [Tags]    P0    TC-015    Pilar-3    negative    fail_fast
    Given Terdapat transaksi SMS berstatus PENDING pada database
    When Sistem memeriksa status dan Telkomsel menolak dengan kode kesalahan 405 Method Not Allowed
    Then Transaksi pada database seketika diubah statusnya menjadi GIVE_UP secara permanen
    And Sistem tidak melakukan penjadwalan ulang terhadap transaksi tersebut
    And Tidak ada pesan laporan pengiriman yang diteruskan ke sistem hilir

TC-016 — Penghentian Permanen Langsung Saat Autentikasi Ditolak dengan Kode 401
    [Tags]    P0    TC-016    Pilar-3    negative    fail_fast
    Given Terdapat transaksi SMS berstatus PENDING pada database
    When Sistem memeriksa status dan Telkomsel menolak autentikasi dengan kode kesalahan 401
    Then Transaksi pada database seketika diubah statusnya menjadi GIVE_UP secara permanen
    And Catatan kesalahan menunjukkan kegagalan kredensial autentikasi pada vendor
    And Tidak ada pesan laporan pengiriman yang diteruskan ke sistem hilir

TC-017 — Penghentian Transaksi Tanpa Identitas Appsid Tanpa Melakukan Panggilan Jaringan
    [Tags]    P0    TC-017    Pilar-3    negative    zero_http_call
    Given Dokumen transaksi pada database memiliki sid namun field identitas appsid tidak terisi
    When Sistem melakukan pemindaian terhadap transaksi tidak lengkap tersebut
    Then Transaksi seketika diubah statusnya menjadi GIVE_UP
    And Catatan kesalahan menyebutkan kredensial tidak ditemukan pada dokumen
    And Terbukti sistem sama sekali tidak mengirimkan permintaan HTTP keluar ke server vendor

TC-018 — Penghentian Transaksi Tanpa Identitas SID Tanpa Melakukan Panggilan Jaringan
    [Tags]    P0    TC-018    Pilar-3    negative    zero_http_call
    Given Dokumen transaksi pada database memiliki appsid namun field identitas sid tidak terisi
    When Sistem melakukan pemindaian terhadap transaksi tidak lengkap tersebut
    Then Transaksi seketika diubah statusnya menjadi GIVE_UP
    And Catatan kesalahan menyebutkan kredensial tidak ditemukan pada dokumen
    And Terbukti sistem sama sekali tidak mengirimkan permintaan HTTP keluar ke server vendor

TC-019 — Penghentian Transaksi Tanpa Kunci Rahasia Terdaftar Tanpa Melakukan Panggilan Jaringan
    [Tags]    P0    TC-019    Pilar-3    negative    zero_http_call
    Given Transaksi memiliki appsid dan sid lengkap namun tidak terdaftar pada konfigurasi kunci rahasia
    And Konfigurasi kunci rahasia cadangan default dalam kondisi kosong
    When Sistem mencoba memproses transaksi tersebut
    Then Transaksi seketika diubah statusnya menjadi GIVE_UP
    And Catatan kesalahan menyebutkan kunci rahasia klien tidak ditemukan
    And Terbukti sistem sama sekali tidak mengirimkan permintaan HTTP keluar ke server vendor

TC-020 — Audit Kerahasiaan Kredensial Sensitif pada Seluruh Berkas Log Sistem
    [Tags]    P0    TC-020    Pilar-2    security    credential_audit
    Given Seluruh rangkaian pengujian penarikan status telah selesai dijalankan
    When Pemeriksaan mendalam dilakukan terhadap seluruh berkas log sistem yang terbentuk
    Then Ditemukan nol baris yang memuat nilai kunci rahasia klien sebenarnya
    And Ditemukan nol baris yang memuat nilai tanda tangan enam puluh empat karakter aktual yang digunakan pada transaksi
    And Ditemukan nol baris yang membocorkan nilai nomor pengirim rahasia

TC-021 — Audit Kerahasiaan Basis Data Bebas dari Penyimpanan Kunci Rahasia
    [Tags]    P0    TC-021    Pilar-2    security    storage_audit
    Given Data awal jumlah dokumen pada koleksi transaksi telah dicatat sebagai acuan dasar kontrol
    When Transaksi-transaksi baru diproses dan diselesaikan oleh sistem
    Then Dokumen-dokumen baru yang tersimpan terbukti tidak memiliki atribut kata sandi maupun kunci rahasia
    And Dokumen yang diproses tidak pernah ditambahi atribut rahasia serta jumlah dokumen ber-atribut rahasia tidak bertambah

TC-022 — Pemrosesan Kompatibel Transaksi Warisan Versi Lama yang Memuat Kata Sandi
    [Tags]    P1    TC-022    Pilar-2    compatibility    legacy_handling
    Given Terdapat transaksi warisan versi lama yang masih menyimpan kata sandi lama pada database
    When Sistem memeriksa status transaksi warisan tersebut ke Telkomsel V2
    Then Sistem mengabaikan kata sandi lama dan menggunakan kunci rahasia dari konfigurasi baru
    And Tanda tangan yang diterima vendor terbukti dihitung dari kunci konfigurasi baru dan bukan kata sandi lama
    And Transaksi berhasil diperiksa dan diperbarui statusnya menjadi RESOLVED

TC-023 — [Mock Contract Guard] Penegakan Aturan Mock Server Menolak Metode HTTP Non-POST
    [Tags]    P2    TC-023    Pilar-2    mock_validation    protocol_guard
    Given Server simulasi Telkomsel V2 aktif menegakkan aturan protokol IFA versi lima
    When Permintaan pemeriksaan dikirimkan menggunakan metode selain POST seperti metode GET
    Then Server simulasi menolak permintaan tersebut dengan status kode HTTP 405 Method Not Allowed
    And Isi balasan memuat kode kesalahan 2405 sesuai spesifikasi baku

TC-024 — [Mock Contract Guard] Penegakan Aturan Mock Server Menolak Parameter Query String
    [Tags]    P2    TC-024    Pilar-2    mock_validation    protocol_guard
    Given Server simulasi Telkomsel V2 aktif menegakkan aturan protokol IFA versi lima
    When Permintaan pemeriksaan dikirimkan membawa parameter pada bagian query string URL
    Then Server simulasi menolak permintaan tersebut dengan status kode HTTP 400 Bad Request
    And Isi balasan memuat kode kesalahan 2400 sesuai spesifikasi baku

TC-025 — Ketahanan Sistem Terhadap Kesalahan Penulisan Alamat URL Vendor
    [Tags]    P2    TC-025    Pilar-4    resilience    configuration_safety
    Given Alamat endpoint vendor pada konfigurasi database dituliskan dengan format rusak tanpa skema protokol
    And Terdapat transaksi SMS berstatus PENDING pada database
    When Sistem memproses transaksi menggunakan alamat endpoint yang rusak tersebut
    Then Transaksi dijadwalkan ulang dengan status PENDING dan catatan kesalahan tercatat di log
    And Aplikasi tetap berjalan lancar dan proses pemeriksaan transaksi lainnya tidak terhenti

TC-026 — Penanganan Operasional Aman Saat Konfigurasi Kunci Rahasia Kosong Total
    [Tags]    P2    TC-026    Pilar-3    negative    configuration_safety
    Given Basis data konfigurasi tidak memiliki rekaman kunci rahasia sama sekali
    And Terdapat transaksi SMS berstatus PENDING pada database
    When Layanan DR Pull dijalankan dan memproses transaksi tersebut
    Then Inisialisasi layanan berhasil berjalan lancar tanpa mengalami kegagalan fatal
    And Transaksi yang diperiksa diubah statusnya menjadi GIVE_UP karena ketiadaan kunci rahasia

TC-027 — Validasi Batas Toleransi Waktu Tanda Tangan Tepat Plus Minus Tiga Ratus Detik Berhasil
    [Tags]    P1    TC-027    Pilar-2    security    timestamp_boundary
    Given Transaksi SMS siap dilakukan pemeriksaan status
    When Permintaan dikirimkan dan dievaluasi terhadap jam server simulasi yang diselisihkan tepat tiga ratus detik
    Then Server vendor Telkomsel menerima permintaan dan memvalidasi tanda tangan dengan sukses pada kedua arah batas
    And Transaksi berhasil diselesaikan dan statusnya diperbarui menjadi RESOLVED

TC-028 — Penolakan Transaksi Saat Penanda Waktu Melampaui Batas Toleransi Tiga Ratus Satu Detik
    [Tags]    P1    TC-028    Pilar-2    security    timestamp_boundary
    Given Transaksi SMS siap dilakukan pemeriksaan status
    When Permintaan dikirimkan dan dievaluasi terhadap jam server simulasi yang melampaui batas toleransi selisih tiga ratus satu detik
    Then Server vendor menolak permintaan dengan kode kesalahan 401 karena penanda waktu kedaluwarsa
    And Transaksi seketika diubah statusnya menjadi GIVE_UP secara permanen tanpa dicoba ulang

TC-029 — Penegakan Prioritas Tertinggi Kunci Rahasia Pasangan Lengkap Appsid dan SID
    [Tags]    P0    TC-029    Pilar-2    security    secret_hierarchy
    Given Konfigurasi database memuat ketiga tingkat kunci rahasia sekaligus dengan nilai yang berbeda
    And Kunci tingkat satu appsid:sid bernilai Kunci A, tingkat dua bernilai Kunci B, dan default bernilai Kunci C
    When Sistem memproses transaksi yang memiliki pasangan appsid dan sid tersebut
    Then Sistem terbukti memprioritaskan Kunci A dan mengabaikan Kunci B maupun Kunci C
    And Permintaan berhasil diverifikasi dan diterima oleh vendor menggunakan Kunci A

TC-030 — Penanganan Gangguan Gerbang Jaringan Vendor 502 Bad Gateway Sebagai Kesalahan Sementara
    [Tags]    P1    TC-030    Pilar-4    resilience    retry_backoff
    Given Terdapat transaksi SMS berstatus PENDING pada database
    When Sistem memeriksa status dan gerbang jaringan Telkomsel mengembalikan respons 502 Bad Gateway
    Then Transaksi tidak dinyatakan gagal permanen melainkan tetap berstatus PENDING
    And Riwayat jumlah percobaan bertambah dan waktu pemeriksaan berikutnya dijadwalkan ulang
    And Tidak ada pesan laporan pengiriman yang diteruskan ke sistem hilir

TC-031 — Penanganan Kegagalan Parsial Antrean SQL dan Pencegahan Pengiriman Ulang Otomatis
    [Tags]    P1    TC-031    Pilar-4    resilience    downstream_failure_handling
    Given Konfigurasi antrean SQL disiapkan mengalami penolakan pengiriman broker
    And Terdapat transaksi SMS berstatus PENDING siap diperiksa dengan hasil Delivered
    When Layanan DR Pull memproses pemeriksaan status transaksi tersebut
    Then Pesan laporan DR berhasil dikirim tepat satu kali ke antrean jns.dr.drrealhandler
    And Pengiriman laporan ke antrean SQL gagal ditolak oleh broker
    And Layanan SUT mencatat kegagalan publikasi parsial dan perlunya investigasi manual pada log
    And Status dokumen transaksi tertahan pada status PUBLISHING di database MongoDB
    And Dokumen tidak diproses ulang pada siklus pemindaian berikutnya dan tidak terjadi duplikasi pesan
    And Layanan SUT tetap berjalan normal tanpa mengalami crash

TC-032 — Isolasi Pemrosesan Transaksi dalam Satu Siklus Batch Pemindaian Bersama
    [Tags]    P1    TC-032    Pilar-4    resilience    batch_isolation
    Given Terdapat tiga transaksi SMS sekaligus dalam satu siklus pemindaian berkala yang sama
    And Transaksi kedua mengalami batas waktu koneksi sedangkan transaksi pertama dan ketiga normal
    When Sistem menjalankan pemindaian dan pemrosesan batch transaksi tersebut dalam satu siklus sweep
    Then Transaksi kedua dijadwalkan ulang sesuai aturan penanganan kesalahan sementara
    And Transaksi pertama dan transaksi ketiga berhasil diselesaikan hingga status RESOLVED tanpa terganggu

TC-033 — Penguncian Atomic Multi-Instance Tahap Publikasi (Publishing Fence) Mencegah Duplikasi Laporan
    [Tags]    P0    TC-033    Pilar-4    resilience    concurrency_fencing
    Given Terdapat transaksi pada database yang telah berada pada tahap PULLING dengan status akhir diperoleh
    When Dua instance aplikasi DR Pull terpisah mencoba melakukan klaim publikasi secara bersamaan pada transaksi tersebut
    Then Hanya instance pemenang yang berhasil memenangkan penguncian atomic claimPublishing
    And Instance pemenang mengeksekusi penerbitan laporan secara penuh ke kedua antrean hilir dan mengubah status menjadi RESOLVED
    And Instance kedua membatalkan publikasi serta tidak menerbitkan pesan apa pun ke sistem hilir
    And Jumlah pesan yang diterima pada masing-masing antrean hilir terbukti tepat satu pesan

TC-034 — Penanganan Gangguan Layanan Vendor 503 Service Unavailable Sebagai Kesalahan Sementara
    [Tags]    P1    TC-034    Pilar-4    resilience    retry_backoff
    Given Terdapat transaksi SMS berstatus PENDING pada database
    When Sistem memeriksa status dan layanan Telkomsel sedang tidak dapat melayani dengan kode 503 Service Unavailable
    Then Transaksi tidak dinyatakan gagal permanen melainkan tetap berstatus PENDING
    And Riwayat jumlah percobaan bertambah dan waktu pemeriksaan berikutnya dijadwalkan ulang
    And Tidak ada pesan laporan pengiriman yang diteruskan ke sistem hilir
