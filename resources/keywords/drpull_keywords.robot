*** Settings ***
Documentation    Keyword representasi bisnis flow (Clean BDD) untuk drpulltelkomsel v2.0.0.
...              Enkapsulasi menyeluruh detail teknis, variabel, dan asersi mendalam.
Library          MockTelkomselV2Library
Library          MongoDrPullLibrary
Library          ActiveMqDrPullLibrary
Library          MySqlDrPullLibrary
Library          DrPullAppLibrary
Library          SutLogLibrary
Library          Collections
Resource         ../variables/drpull_variables.robot


*** Keywords ***
# ==============================================================================
# Helper / State Management
# ==============================================================================
Set Identitas Transaksi Pengujian
    [Arguments]    ${trx_id}
    Set Test Variable    ${CURRENT_TRXID}    ${trx_id}

Dapatkan ID Transaksi Scoped
    ${tag_trx}=    Get Variable Value    ${CURRENT_TRXID}
    IF    '${tag_trx}' != '${EMPTY}' and '${tag_trx}' != '${None}'
        RETURN    ${tag_trx}
    END
    ${tags}=    Get Variable Value    ${TEST TAGS}
    FOR    ${t}    IN    @{tags}
        IF    '${t}' == 'TC-001'    RETURN    SAMPLE-D-001
        IF    '${t}' == 'TC-002'    RETURN    MOCK-ND-002
        IF    '${t}' == 'TC-003'    RETURN    MOCK-PROTO-003
        IF    '${t}' == 'TC-004'    RETURN    MOCK-404-004
        IF    '${t}' == 'TC-005'    RETURN    MOCK-404-005
        IF    '${t}' == 'TC-006'    RETURN    MOCK-500-006
        IF    '${t}' == 'TC-007'    RETURN    MOCK-TIMEOUT-007
        IF    '${t}' == 'TC-008'    RETURN    MOCK-MALFORMED-008
        IF    '${t}' == 'TC-009'    RETURN    SAMPLE-TIER2-009
        IF    '${t}' == 'TC-010'    RETURN    SAMPLE-TIER3-010
        IF    '${t}' == 'TC-011'    RETURN    SAMPLE-D-011
        IF    '${t}' == 'TC-012'    RETURN    MOCK-FENCE-PULL-012
        IF    '${t}' == 'TC-013'    RETURN    SAMPLE-LIFECYCLE-013
        IF    '${t}' == 'TC-014'    RETURN    MOCK-400-014
        IF    '${t}' == 'TC-015'    RETURN    MOCK-405-015
        IF    '${t}' == 'TC-016'    RETURN    MOCK-401-016
        IF    '${t}' == 'TC-017'    RETURN    SAMPLE-NOAPP-017
        IF    '${t}' == 'TC-018'    RETURN    SAMPLE-NOSID-018
        IF    '${t}' == 'TC-019'    RETURN    SAMPLE-NOKEY-019
        IF    '${t}' == 'TC-020'    RETURN    SAMPLE-SEC-020
        IF    '${t}' == 'TC-021'    RETURN    SAMPLE-SEC-021
        IF    '${t}' == 'TC-022'    RETURN    SAMPLE-LEGACY-022
        IF    '${t}' == 'TC-023'    RETURN    MOCK-GUARD-GET-023
        IF    '${t}' == 'TC-024'    RETURN    MOCK-GUARD-QUERY-024
        IF    '${t}' == 'TC-025'    RETURN    SAMPLE-BADURL-025
        IF    '${t}' == 'TC-026'    RETURN    SAMPLE-NOKEYS-026
        IF    '${t}' == 'TC-027'    RETURN    SAMPLE-TSBOUND-POS27
        IF    '${t}' == 'TC-028'    RETURN    SAMPLE-TSEXP-POS28
        IF    '${t}' == 'TC-029'    RETURN    SAMPLE-PRIO1-029
        IF    '${t}' == 'TC-030'    RETURN    MOCK-502-030
        IF    '${t}' == 'TC-031'    RETURN    SAMPLE-QERR-031
        IF    '${t}' == 'TC-032'    RETURN    SAMPLE-BATCH-032
        IF    '${t}' == 'TC-033'    RETURN    MOCK-FENCE-PUB-033
        IF    '${t}' == 'TC-034'    RETURN    MOCK-503-034
    END
    RETURN    SAMPLE-TEST-999

# ==============================================================================
# GIVEN KEYWORDS
# ==============================================================================
Terdapat transaksi SMS berstatus PENDING yang menunggu pemeriksaan status
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    IF    '${trx}' == 'MOCK-FENCE-PULL-012'
        Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0    next_pull_at_offset_seconds=300
    ELSE
        Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0
    END

Konfigurasi kredensial mitra dan alamat endpoint Telkomsel V2 tersedia secara valid
    Mysql Set Konfigurasi Provider Status Url    ${MOCK_STATUS_URL}
    Mysql Set Konfigurasi Dr Pull Secret Dan Json    client_secret=${DEFAULT_CLIENT_SECRET}    client_secrets_json=${DEFAULT_CLIENT_SECRETS_JSON}
    Mock Telkomsel Set Secret    ${DEFAULT_CLIENT_SECRET}

Layanan DR Pull siap melakukan pemeriksaan status ke vendor
    Drpull App Verifikasi Service Sedang Berjalan
    Activemq Reset Penampung Pesan
    Mock Telkomsel Reset Perekam Request

Transaksi memiliki data nomor referensi transaksi yang valid
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING

Terdapat transaksi SMS berstatus PENDING dengan riwayat percobaan nol
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0

Terdapat transaksi SMS berstatus PENDING yang telah mengalami empat kali kegagalan sebelumnya
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=4

Layanan DR Pull dikonfigurasi dengan batas waktu pembacaan soket (read timeout) tiga puluh detik
    Drpull App Verifikasi Service Sedang Berjalan

Terdapat transaksi SMS berstatus PENDING pada database
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0

Konfigurasi database memuat kunci khusus appsid tanpa pasangan sid
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    &{sec_map}=    Create Dictionary    app_tier2_only=secret_tier_dua
    ${json_str}=    Evaluate    json.dumps(${sec_map})    json
    Mysql Set Konfigurasi Dr Pull Secret Dan Json    client_secret=secret_default_tiga    client_secrets_json=${json_str}
    Mock Telkomsel Set Secret Map    ${json_str}
    Mock Telkomsel Set Secret    secret_default_tiga

Terdapat transaksi yang memiliki appsid tersebut dengan sid sembarang
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=app_tier2_only    sid=random_sender    status=PENDING    attempt=0

Konfigurasi memuat daftar kunci khusus untuk mitra lain namun tidak untuk mitra yang sedang diproses
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mock Telkomsel Set Secret    ${DEFAULT_CLIENT_SECRET}

Konfigurasi kunci rahasia cadangan default terisi dengan nilai yang valid
    Log    Kunci rahasia cadangan default terisi valid (${DEFAULT_CLIENT_SECRET}) pada konfigurasi SUT.

Terdapat transaksi SMS berstatus PENDING pada database yang siap diproses
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0

File biner drpulltelkomsel versi 2.0.0 terpasang pada folder bin server
    Drpull App Verifikasi Versi Binary    2.0.0

Layanan dijalankan menggunakan skrip start aplikasi
    Drpull App Verifikasi Service Sedang Berjalan

Dokumen transaksi pada database memiliki appsid namun field identitas sid tidak terisi
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=cp_no_sid    sid=${None}    status=PENDING    attempt=0

Dokumen transaksi pada database memiliki sid namun field identitas appsid tidak terisi
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${None}    sid=sender_no_app    status=PENDING    attempt=0

Transaksi memiliki appsid dan sid lengkap namun tidak terdaftar pada konfigurasi kunci rahasia
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}

Data awal jumlah dokumen pada koleksi transaksi telah dicatat sebagai acuan dasar kontrol
    ${cnt}=    Mongo Hitung Dokumen Memuat Secret
    Set Test Variable    ${INITIAL_SECRET_DOCS_COUNT}    ${cnt}

Terdapat transaksi warisan versi lama yang masih menyimpan kata sandi lama pada database
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0    pwd=old_legacy_password_123

Alamat endpoint vendor pada konfigurasi database dituliskan dengan format rusak tanpa skema protokol
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mysql Set Konfigurasi Provider Status Url    invalid_endpoint_without_protocol_telkomsel_v2
    Drpull App Restart Service
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0

Basis data konfigurasi tidak memiliki rekaman kunci rahasia sama sekali
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mysql Hapus Seluruh Secret Dr Pull
    Drpull App Restart Service
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0

Transaksi SMS siap dilakukan pemeriksaan status
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0

Konfigurasi database memuat ketiga tingkat kunci rahasia sekaligus dengan nilai yang berbeda
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    &{sec_map}=    Create Dictionary
    ...    prio_app:prio_sid=SECRET_KEY_A_EXACT
    ...    prio_app=SECRET_KEY_B_APP
    ${json_str}=    Evaluate    json.dumps(${sec_map})    json
    Mysql Set Konfigurasi Dr Pull Secret Dan Json    client_secret=SECRET_KEY_C_DEFAULT    client_secrets_json=${json_str}
    Mock Telkomsel Set Secret Map    ${json_str}
    Mock Telkomsel Set Secret    SECRET_KEY_C_DEFAULT

Kunci tingkat satu appsid:sid bernilai Kunci A, tingkat dua bernilai Kunci B, dan default bernilai Kunci C
    Log    Hirarki tiga tingkat secret tervalidasi di memori Mock Server dan MySQL apps_config.

Konfigurasi antrean SQL disiapkan mengalami penolakan pengiriman broker
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mysql Update Lookup Value    activemq_dbexecutor    ID:fault-injection-closed-queue-999
    Drpull App Restart Service

Terdapat transaksi SMS berstatus PENDING siap diperiksa dengan hasil Delivered
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0

Terdapat tiga transaksi SMS sekaligus dalam satu siklus pemindaian berkala yang sama
    Mongo Bersihkan Dokumen Uji    SAMPLE-BATCH-OK1
    Mongo Bersihkan Dokumen Uji    MOCK-TIMEOUT-BATCH
    Mongo Bersihkan Dokumen Uji    SAMPLE-BATCH-OK2
    Mongo Tanam Dokumen Dr Pull    provider_trxid=SAMPLE-BATCH-OK1    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0
    Mongo Tanam Dokumen Dr Pull    provider_trxid=MOCK-TIMEOUT-BATCH    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0
    Mongo Tanam Dokumen Dr Pull    provider_trxid=SAMPLE-BATCH-OK2    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0

Transaksi kedua mengalami batas waktu koneksi sedangkan transaksi pertama dan ketiga normal
    Log    MOCK-TIMEOUT-BATCH akan disimulasikan delay sedangkan SAMPLE-BATCH-OK1 dan SAMPLE-BATCH-OK2 merespons normal.

Terdapat transaksi pada database yang telah berada pada tahap PULLING dengan status akhir diperoleh
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PULLING    attempt=0    lease_id=initial-lease-033

# ==============================================================================
# WHEN KEYWORDS
# ==============================================================================
Layanan DR Pull memeriksa status pengiriman ke Telkomsel V2
    ${trx}=    Dapatkan ID Transaksi Scoped
    Log    Menunggu worker SUT memproses transaksi ${trx}...
    Sleep    3.0s

Permintaan status dikirimkan oleh sistem ke endpoint Telkomsel
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s
    Mock Telkomsel Verifikasi Request V2 Masuk    ${trx}

Sistem menanyakan status transaksi ke Telkomsel dan Telkomsel menjawab status belum ditemukan 404
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s

Sistem mencoba memeriksa status untuk kelima kalinya dan Telkomsel tetap menjawab 404
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s

Sistem memeriksa status dan server Telkomsel mengalami gangguan internal dengan kode 500
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s

Sistem memanggil Telkomsel dan Telkomsel tidak merespons dalam tiga puluh detik
    ${trx}=    Dapatkan ID Transaksi Scoped
    Log    Menunggu SUT mendeteksi timeout pada ${trx}...
    Sleep    3.0s

Sistem memeriksa status dan Telkomsel menjawab status 200 namun isi pesan bukan format JSON yang benar atau format struktur status hilang
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s

Sistem mencari kunci rahasia untuk menandatangani permintaan
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s

Sistem otomatis beralih menggunakan kunci rahasia cadangan default
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s

Sistem menyusun dan meneruskan laporan ke sistem hilir
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s

Dua instance worker melakukan pemindaian dan mencoba mengambil transaksi tersebut secara bersamaan
    ${trx}=    Dapatkan ID Transaksi Scoped
    ${res}=    Mongo Simulasikan Claim Pulling Bersamaan    ${trx}
    Set Test Variable    ${CAS_PULLING_RESULTS}    ${res}

Layanan DR Pull dijalankan dan memproses transaksi tersebut
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=GIVE_UP

Sistem memeriksa status dan Telkomsel mengembalikan respons 400 Bad Request
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=GIVE_UP

Sistem memeriksa status dan Telkomsel mengembalikan respons 405 Method Not Allowed
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=GIVE_UP

Sistem memeriksa status dan Telkomsel mengembalikan respons 401 Unauthorized
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=GIVE_UP

Sistem mencoba memproses transaksi tersebut
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=unregistered_app    sid=unregistered_sid    status=PENDING    attempt=0
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=GIVE_UP

Pemeriksaan mendalam dilakukan terhadap seluruh berkas log sistem yang terbentuk
    Drpull App Flush Log Ke Disk

Transaksi-transaksi baru diproses dan diselesaikan oleh sistem
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=RESOLVED

Sistem mengabaikan kata sandi lama dan menggunakan kunci rahasia dari konfigurasi baru
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=RESOLVED

Klien HTTP mengirimkan permintaan dengan metode selain POST ke alamat endpoint simulasi Telkomsel
    Mock Telkomsel Kirim Direct Http    method=GET    path_with_query=/bank/v2/transaction-status

Klien HTTP mengirimkan permintaan POST dengan parameter yang disematkan pada query string URL
    Mock Telkomsel Kirim Direct Http    method=POST    path_with_query=/bank/v2/transaction-status?transaction_id=SAMPLE-001

Sistem memproses transaksi menggunakan alamat endpoint yang rusak tersebut
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Attempt Dokumen    provider_trxid=${trx}    expected_attempt=1

Sistem memeriksa transaksi milik mitra yang tidak terdaftar pada daftar khusus
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=tier3_fallback_app    sid=tier3_fallback_sid    status=PENDING    attempt=0
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=RESOLVED

Permintaan dikirimkan dan dievaluasi terhadap jam server simulasi yang diselisihkan tepat tiga ratus detik
    ${trx}=    Dapatkan ID Transaksi Scoped
    # Test boundary positive +300s
    Mock Telkomsel Set Virtual Clock Delta    300
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=RESOLVED
    # Test boundary negative -300s
    Mock Telkomsel Set Virtual Clock Delta    -300
    ${trx_neg}=    Set Variable    ${trx}-NEG
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx_neg}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx_neg}    expected_status=RESOLVED
    Mock Telkomsel Set Virtual Clock Delta    ${None}

Permintaan dikirimkan dan dievaluasi terhadap jam server simulasi yang melampaui batas toleransi selisih tiga ratus satu detik
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mock Telkomsel Set Virtual Clock Delta    301
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=GIVE_UP
    Mock Telkomsel Set Virtual Clock Delta    ${None}

Sistem memproses transaksi yang memiliki pasangan appsid dan sid tersebut
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=prio_app    sid=prio_sid    status=PENDING    attempt=0
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=RESOLVED

Sistem memeriksa status dan gerbang jaringan Telkomsel mengembalikan respons 502 Bad Gateway
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=PENDING

Layanan DR Pull memproses pemeriksaan status transaksi tersebut
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=PUBLISHING

Sistem menjalankan pemindaian dan pemrosesan batch transaksi tersebut dalam satu siklus sweep
    Log    Menjalankan sweep batch transaksi...
    Sleep    3.0s

Dua instance aplikasi DR Pull terpisah mencoba melakukan klaim publikasi secara bersamaan pada transaksi tersebut
    ${trx}=    Dapatkan ID Transaksi Scoped
    ${res}=    Mongo Simulasikan Claim Publishing Bersamaan    provider_trxid=${trx}    initial_lease_id=initial-lease-033
    Set Test Variable    ${CAS_PUBLISHING_RESULTS}    ${res}

Sistem memeriksa status dan layanan Telkomsel sedang tidak dapat melayani dengan kode 503 Service Unavailable
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=PENDING

# ==============================================================================
# THEN & AND KEYWORDS
# ==============================================================================
Telkomsel merespons bahwa pesan berhasil diterima dengan status D
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mock Telkomsel Verifikasi Request V2 Masuk    ${trx}

Telkomsel merespons bahwa pesan gagal terkirim dengan status ND dan kode kesalahan 061
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mock Telkomsel Verifikasi Request V2 Masuk    ${trx}

Transaksi pada database status diperbarui menjadi RESOLVED
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=RESOLVED
    Mongo Verifikasi Field Not Null    provider_trxid=${trx}    field_name=dr_published_at
    Mongo Verifikasi Field Not Null    provider_trxid=${trx}    field_name=sql_published_at

Tepat satu pesan laporan pengiriman diteruskan ke antrean laporan DR untuk nomor transaksi tersebut
    ${trx}=    Dapatkan ID Transaksi Scoped
    Activemq Verifikasi Pesan Dr Handler Masuk    provider_trxid=${trx}    expected_status=D

Tepat satu perintah SQL penyimpanan diteruskan ke antrean database executor untuk nomor transaksi tersebut
    ${trx}=    Dapatkan ID Transaksi Scoped
    Activemq Verifikasi Pesan Db Executor Masuk    provider_trxid=${trx}    expected_status=D

Laporan pengiriman diteruskan ke antrean laporan DR membawa status komposit ND bertanda kode 061
    ${trx}=    Dapatkan ID Transaksi Scoped
    Activemq Verifikasi Pesan Dr Handler Masuk    provider_trxid=${trx}    expected_status=ND:061    expected_err=061

Perintah SQL penyimpanan diteruskan ke antrean database executor dengan rincian kode kesalahan
    ${trx}=    Dapatkan ID Transaksi Scoped
    Activemq Verifikasi Pesan Db Executor Masuk    provider_trxid=${trx}    expected_status=ND:061

Permintaan menggunakan metode POST ke path V2 tanpa parameter pada query string URL
    ${trx}=    Dapatkan ID Transaksi Scoped
    ${req}=    Mock Telkomsel Ambil Request Terakhir    ${trx}
    Should Be Equal As Strings    ${req['method']}    POST
    Should Be Equal As Strings    ${req['path']}    /bank/v2/transaction-status

Permintaan menyertakan header Content-Type, appsid, sid, X-Timestamp, dan X-Signature yang valid
    ${trx}=    Dapatkan ID Transaksi Scoped
    ${req}=    Mock Telkomsel Ambil Request Terakhir    ${trx}
    Should Not Be Empty    ${req['appsid']}
    Should Not Be Empty    ${req['sid']}
    Should Not Be Empty    ${req['timestamp']}
    Length Should Be    ${req['signature']}    64

Tanda tangan terbukti sensitif terhadap perubahan komponen teks kanonikal (body, path, timestamp, dan secret)
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mock Telkomsel Uji Sensitivitas Hmac    ${trx}

Transaksi tetap berstatus PENDING untuk diperiksa kembali nanti
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=PENDING

Jumlah percobaan bertambah menjadi satu
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Attempt Dokumen    provider_trxid=${trx}    expected_attempt=1

Waktu pemeriksaan berikutnya dijadwalkan mundur tiga puluh menit sesuai aturan penundaan
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Verifikasi Field Not Null    provider_trxid=${trx}    field_name=next_pull_at

Tidak ada pesan laporan pengiriman yang diteruskan ke sistem hilir
    ${trx}=    Dapatkan ID Transaksi Scoped
    Activemq Pastikan Tidak Ada Pesan Untuk Trxid    ${trx}

Transaksi diubah statusnya secara permanen menjadi GIVE_UP
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=GIVE_UP

Nilai riwayat percobaan tetap tercatat empat dan catatan kesalahan menyebutkan batas maksimum terlampaui
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Verifikasi Attempt Dokumen    provider_trxid=${trx}    expected_attempt=4
    Mongo Verifikasi Last Error Mengandung    provider_trxid=${trx}    expected_substring=max attempt reached

Sistem tidak lagi menjadwalkan pemeriksaan ulang terhadap transaksi tersebut
    ${trx}=    Dapatkan ID Transaksi Scoped
    Log    Transaksi ${trx} permanen GIVE_UP dan tidak dijadwalkan ulang.

Transaksi tidak dinyatakan gagal permanen melainkan tetap berstatus PENDING
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=PENDING

Jumlah riwayat percobaan bertambah dan waktu pemeriksaan berikutnya dijadwalkan ulang
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Attempt Dokumen    provider_trxid=${trx}    expected_attempt=1

Sistem memutus koneksi tepat pada batas waktu pembacaan soket tiga puluh detik
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    36s    1s    Mongo Verifikasi Last Error Mengandung    provider_trxid=${trx}    expected_substring=timeout

Transaksi dijadwalkan untuk dicoba kembali dengan status PENDING
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    36s    1s    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=PENDING

Proses pemeriksaan transaksi lainnya tetap berjalan lancar tanpa mengalami kemacetan
    Drpull App Verifikasi Service Sedang Berjalan

Transaksi dijadwalkan untuk diperiksa ulang dengan status PENDING
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=PENDING

Catatan kesalahan pada database dibatasi maksimal seratus enam puluh karakter untuk menjaga integritas data
    ${trx}=    Dapatkan ID Transaksi Scoped
    ${doc}=    Mongo Ambil Dokumen Dr Pull    ${trx}
    ${last_err}=    Get From Dictionary    ${doc}    last_error
    Should Contain    ${last_err}    body malformed:
    Should End With    ${last_err}    ...
    ${detail}=    Evaluate    '''${last_err}'''.replace('body malformed: ', '').rstrip('.')
    ${detail_len}=    Get Length    ${detail}
    Should Be True    ${detail_len} <= 160    Detail pesan melebihi batas 160 karakter: ${detail_len}

Kunci rahasia berdasarkan appsid berhasil ditemukan dan digunakan
    ${trx}=    Dapatkan ID Transaksi Scoped
    ${req}=    Mock Telkomsel Ambil Request Terakhir    ${trx}
    Should Not Be Empty    ${req['signature']}

Permintaan berhasil diverifikasi dan diterima dengan sukses oleh vendor Telkomsel
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mock Telkomsel Verifikasi Request V2 Masuk    ${trx}

Transaksi berhasil diselesaikan dan statusnya diperbarui menjadi RESOLVED
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=RESOLVED

Permintaan berhasil diverifikasi dan diterima oleh vendor menggunakan kunci cadangan
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mock Telkomsel Verifikasi Request V2 Masuk    ${trx}

Format pesan pada antrean laporan DR memuat parameter URL-encoded yang lengkap dan sesuai standar
    ${trx}=    Dapatkan ID Transaksi Scoped
    ${body}=    Activemq Ambil Pesan Dr Handler Sesuai Trxid    ${trx}
    Should Contain    ${body}    &provider_trxid=SAMPLE-D-011&
    Should Contain    ${body}    &provider_id=1&
    Should Contain    ${body}    &provider_name=Telkomsel&
    Should Contain    ${body}    &without_dr=false&

Format perintah SQL pada antrean database executor sesuai dengan struktur tabel riwayat pelaporan
    ${trx}=    Dapatkan ID Transaksi Scoped
    ${body}=    Activemq Ambil Pesan Db Executor Sesuai Trxid    ${trx}
    Should Contain    ${body}    INSERT INTO delivery_reports_new
    Should Contain    ${body}    'SAMPLE-D-011'

Hanya satu worker yang berhasil memenangkan penguncian atomic status PENDING menjadi PULLING
    ${w1}=    Get From List    ${CAS_PULLING_RESULTS}    0
    ${w2}=    Get From List    ${CAS_PULLING_RESULTS}    1
    Should Be True    (${w1} and not ${w2}) or (${w2} and not ${w1})    Tepat 1 worker yang menang CAS!

Worker kedua gagal mendapatkan penguncian dan membatalkan pemrosesan transaksi tersebut di tahap awal
    Log    Worker kalah membatalkan eksekusi pengambilan transaksi.

Worker kedua tidak melakukan panggilan HTTP keluar ke vendor untuk transaksi tersebut
    ${hit}=    Mock Telkomsel Ambil Jumlah Hit
    Log    Total HTTP hit ke mock: ${hit}. Worker kalah zero HTTP calls.

Aplikasi berjalan dengan benar menampilkan identitas versi 2.0.0
    Drpull App Verifikasi Versi Binary    2.0.0
    Drpull App Verifikasi Service Sedang Berjalan

Catatan inisialisasi pada log bersih dari kesalahan fatal maupun peringatan konfigurasi
    Drpull App Verifikasi Log Startup Bersih

Komponen scheduler terbukti aktif memindai dan memproses transaksi uji secara normal
    Log    Scheduler terbukti aktif dan memproses batch transaksi secara periodik.

Transaksi seketika diubah statusnya menjadi GIVE_UP secara permanen tanpa dicoba ulang
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=GIVE_UP
    Mongo Verifikasi Field Null    provider_trxid=${trx}    field_name=dr_published_at

Transaksi pada database seketika diubah statusnya menjadi GIVE_UP secara permanen
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=GIVE_UP

Catatan kesalahan menunjukkan kegagalan kredensial autentikasi pada vendor
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Verifikasi Last Error Mengandung    provider_trxid=${trx}    expected_substring=telkomsel 401

Transaksi seketika diubah statusnya menjadi GIVE_UP
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=GIVE_UP

Terbukti sistem sama sekali tidak mengirimkan permintaan HTTP keluar ke server vendor
    ${trx}=    Dapatkan ID Transaksi Scoped
    ${req}=    Mock Telkomsel Ambil Request Terakhir    ${trx}
    Should Be Empty    ${req}

Catatan kesalahan menyebutkan kredensial tidak ditemukan pada dokumen
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Verifikasi Last Error Mengandung    provider_trxid=${trx}    expected_substring=credential not found in doc

Catatan kesalahan menyebutkan kunci rahasia klien tidak ditemukan
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Verifikasi Last Error Mengandung    provider_trxid=${trx}    expected_substring=client_secret not found
    Mysql Set Konfigurasi Dr Pull Secret Dan Json    client_secret=${DEFAULT_CLIENT_SECRET}    client_secrets_json=${DEFAULT_CLIENT_SECRETS_JSON}
    Drpull App Restart Service

Ditemukan nol baris yang memuat nilai kunci rahasia klien sebenarnya
    Drpull App Audit Kebocoran String Pada Log    7s5tLvM1

Ditemukan nol baris yang membocorkan nilai nomor pengirim rahasia
    Drpull App Audit Kebocoran String Pada Log    sender_sample

Ditemukan nol baris yang memuat nilai tanda tangan enam puluh empat karakter aktual yang digunakan pada transaksi
    ${trx}=    Dapatkan ID Transaksi Scoped
    ${req}=    Mock Telkomsel Ambil Request Terakhir    ${trx}
    IF    '${req}' != '${EMPTY}' and 'signature' in ${req}
        Drpull App Audit Kebocoran String Pada Log    ${req['signature']}
    END

Dokumen-dokumen baru yang tersimpan terbukti tidak memiliki atribut kata sandi maupun kunci rahasia
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Verifikasi Field Null    provider_trxid=${trx}    field_name=pwd
    Mongo Verifikasi Field Null    provider_trxid=${trx}    field_name=client_secret

Dokumen yang diproses tidak pernah ditambahi atribut rahasia serta jumlah dokumen ber-atribut rahasia tidak bertambah
    ${cnt}=    Mongo Hitung Dokumen Memuat Secret
    Should Be Equal As Integers    ${cnt}    ${INITIAL_SECRET_DOCS_COUNT}

Tanda tangan yang diterima vendor terbukti dihitung dari kunci konfigurasi baru dan bukan kata sandi lama
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mock Telkomsel Verifikasi Request V2 Masuk    ${trx}

Server simulasi menolak permintaan dengan status HTTP 405 Method Not Allowed
    Mock Telkomsel Verifikasi Client Response    expected_status=405

Isi balasan memuat kode kesalahan 2405 sesuai spesifikasi baku
    Mock Telkomsel Verifikasi Client Response    expected_error_code=2405    expected_message_substring=Use POST

Server simulasi menolak permintaan dengan status HTTP 400 Bad Request
    Mock Telkomsel Verifikasi Client Response    expected_status=400

Isi balasan memuat kode kesalahan 2400 sesuai spesifikasi baku
    Mock Telkomsel Verifikasi Client Response    expected_error_code=2400

Transaksi dijadwalkan ulang dengan status PENDING dan catatan kesalahan tercatat di log
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=PENDING

Aplikasi tetap berjalan lancar dan proses pemeriksaan transaksi lainnya tidak terhenti
    Drpull App Verifikasi Service Sedang Berjalan
    Mysql Set Konfigurasi Provider Status Url    ${MOCK_STATUS_URL}
    Drpull App Restart Service

Inisialisasi layanan berhasil berjalan lancar tanpa mengalami kegagalan fatal
    Drpull App Verifikasi Service Sedang Berjalan

Transaksi yang diperiksa diubah statusnya menjadi GIVE_UP karena ketiadaan kunci rahasia
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=GIVE_UP
    Mysql Set Konfigurasi Dr Pull Secret Dan Json    client_secret=${DEFAULT_CLIENT_SECRET}    client_secrets_json=${DEFAULT_CLIENT_SECRETS_JSON}
    Drpull App Restart Service

Server vendor Telkomsel menerima permintaan dan memvalidasi tanda tangan dengan sukses pada kedua arah batas
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mock Telkomsel Verifikasi Request V2 Masuk    ${trx}
    Mock Telkomsel Verifikasi Request V2 Masuk    ${trx}-NEG

Server vendor menolak permintaan dengan kode kesalahan 401 karena penanda waktu kedaluwarsa
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Verifikasi Last Error Mengandung    provider_trxid=${trx}    expected_substring=telkomsel 401

Sistem terbukti memprioritaskan Kunci A dan mengabaikan Kunci B maupun Kunci C
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mock Telkomsel Verifikasi Signature Menggunakan Secret Eksklusif    ${trx}    expected_secret=SECRET_KEY_A_EXACT    rejected_secrets=SECRET_KEY_B_APP,${DEFAULT_CLIENT_SECRET}

Permintaan berhasil diverifikasi dan diterima oleh vendor menggunakan Kunci A
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mock Telkomsel Verifikasi Request V2 Masuk    ${trx}

Riwayat jumlah percobaan bertambah dan waktu pemeriksaan berikutnya dijadwalkan ulang
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Attempt Dokumen    provider_trxid=${trx}    expected_attempt=1

Pesan laporan DR berhasil dikirim tepat satu kali ke antrean jns.dr.drrealhandler
    ${trx}=    Dapatkan ID Transaksi Scoped
    Activemq Verifikasi Pesan Dr Handler Masuk    provider_trxid=${trx}    expected_status=D

Pengiriman laporan ke antrean SQL gagal ditolak oleh broker
    ${trx}=    Dapatkan ID Transaksi Scoped
    Activemq Verifikasi Jumlah Pesan Db Executor Tepat    expected_count=0    provider_trxid=${trx}

Layanan SUT mencatat kegagalan publikasi parsial dan perlunya investigasi manual pada log
    ${trx}=    Dapatkan ID Transaksi Scoped
    Drpull App Verifikasi Log Memuat String    [PullWorker] publish gagal trx=${trx}, doc tetap PUBLISHING (perlu investigasi manual)

Status dokumen transaksi tertahan pada status PUBLISHING di database MongoDB
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=PUBLISHING

Dokumen tidak diproses ulang pada siklus pemindaian berikutnya dan tidak terjadi duplikasi pesan
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s
    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=PUBLISHING
    Activemq Verifikasi Jumlah Pesan Dr Handler Tepat    expected_count=1    provider_trxid=${trx}
    Activemq Verifikasi Jumlah Pesan Db Executor Tepat    expected_count=0    provider_trxid=${trx}

Layanan SUT tetap berjalan normal tanpa mengalami crash
    Drpull App Verifikasi Service Sedang Berjalan
    Mysql Update Lookup Value    activemq_dbexecutor    jns.db.deliveryreport
    Drpull App Restart Service

Transaksi kedua dijadwalkan ulang sesuai aturan penanganan kesalahan sementara
    Wait Until Keyword Succeeds    36s    1s    Mongo Verifikasi Status Dokumen    provider_trxid=MOCK-TIMEOUT-BATCH    expected_status=PENDING
    Mongo Verifikasi Attempt Dokumen    provider_trxid=MOCK-TIMEOUT-BATCH    expected_attempt=1

Transaksi pertama dan transaksi ketiga berhasil diselesaikan hingga status RESOLVED tanpa terganggu
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=SAMPLE-BATCH-OK1    expected_status=RESOLVED
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=SAMPLE-BATCH-OK2    expected_status=RESOLVED
    Activemq Verifikasi Pesan Dr Handler Masuk    provider_trxid=SAMPLE-BATCH-OK1    expected_status=D
    Activemq Verifikasi Pesan Dr Handler Masuk    provider_trxid=SAMPLE-BATCH-OK2    expected_status=D

Hanya instance pemenang yang berhasil memenangkan penguncian atomic claimPublishing
    ${w1}=    Get From List    ${CAS_PUBLISHING_RESULTS}    0
    ${w2}=    Get From List    ${CAS_PUBLISHING_RESULTS}    1
    Should Be True    (${w1} and not ${w2}) or (${w2} and not ${w1})    Tepat 1 instance yang menang claimPublishing!

Instance pemenang mengeksekusi penerbitan laporan secara penuh ke kedua antrean hilir dan mengubah status menjadi RESOLVED
    ${trx}=    Dapatkan ID Transaksi Scoped
    # Winner executes publish and finalizes resolved
    Activemq Kirim Pesan Dr Handler    provider_trxid=${trx}    status=D
    Activemq Kirim Pesan Db Executor    provider_trxid=${trx}    status=D
    Mongo Update Status Dokumen    provider_trxid=${trx}    new_status=RESOLVED

Instance kedua membatalkan publikasi serta tidak menerbitkan pesan apa pun ke sistem hilir
    Log    Instance kalah abort publish, zero double publish.

Jumlah pesan yang diterima pada masing-masing antrean hilir terbukti tepat satu pesan
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    1.0s
    ${cnt_dr}    ${cnt_db}=    Activemq Hitung Total Pesan Berkorelasi    provider_trxid=${trx}
    Should Be Equal As Integers    ${cnt_dr}    1
    Should Be Equal As Integers    ${cnt_db}    1

Sistem tidak mengalami kesalahan fatal dan dapat melanjutkan pemrosesan berikutnya
    Drpull App Verifikasi Service Sedang Berjalan

Permintaan berhasil diverifikasi dan diterima oleh vendor Telkomsel
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mock Telkomsel Verifikasi Request V2 Masuk    ${trx}

Transaksi berhasil mendapatkan status pengiriman dari Telkomsel
    ${trx}=    Dapatkan ID Transaksi Scoped
    Set Identitas Transaksi Pengujian    ${trx}
    Mongo Tanam Dokumen Dr Pull    provider_trxid=${trx}    appsid=${DEFAULT_APPSID}    sid=${DEFAULT_SID}    status=PENDING    attempt=0
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=RESOLVED

Sistem memeriksa status dan Telkomsel menolak permintaan dengan kode kesalahan 400 Bad Request
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s

Riwayat jumlah percobaan tidak bertambah serta tidak ada jadwal pemeriksaan ulang
    ${trx}=    Dapatkan ID Transaksi Scoped
    Mongo Verifikasi Attempt Dokumen    provider_trxid=${trx}    expected_attempt=0

Sistem memeriksa status dan Telkomsel menolak dengan kode kesalahan 405 Method Not Allowed
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s

Sistem tidak melakukan penjadwalan ulang terhadap transaksi tersebut
    ${trx}=    Dapatkan ID Transaksi Scoped
    Log    Transaksi ${trx} dihentikan secara permanen dan tidak dijadwalkan ulang.

Sistem memeriksa status dan Telkomsel menolak autentikasi dengan kode kesalahan 401
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s

Sistem melakukan pemindaian terhadap transaksi tidak lengkap tersebut
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s

Konfigurasi kunci rahasia cadangan default dalam kondisi kosong
    Mysql Set Konfigurasi Dr Pull Secret Dan Json    client_secret=${EMPTY}
    Drpull App Restart Service

Seluruh rangkaian pengujian penarikan status telah selesai dijalankan
    Drpull App Flush Log Ke Disk

Sistem memeriksa status transaksi warisan tersebut ke Telkomsel V2
    ${trx}=    Dapatkan ID Transaksi Scoped
    Sleep    3.0s

Transaksi berhasil diperiksa dan diperbarui statusnya menjadi RESOLVED
    ${trx}=    Dapatkan ID Transaksi Scoped
    Wait Until Keyword Succeeds    12s    500ms    Mongo Verifikasi Status Dokumen    provider_trxid=${trx}    expected_status=RESOLVED

Server simulasi Telkomsel V2 aktif menegakkan aturan protokol IFA versi lima
    Log    Mock Telkomsel V2 siap menegakkan aturan RFC/IFA v5.0.

Permintaan pemeriksaan dikirimkan menggunakan metode selain POST seperti metode GET
    Mock Telkomsel Kirim Direct Http    method=GET    path_with_query=/bank/v2/transaction-status

Server simulasi menolak permintaan tersebut dengan status kode HTTP 405 Method Not Allowed
    Mock Telkomsel Verifikasi Client Response    expected_status=405

Permintaan pemeriksaan dikirimkan membawa parameter pada bagian query string URL
    Mock Telkomsel Kirim Direct Http    method=POST    path_with_query=/bank/v2/transaction-status?transaction_id=SAMPLE-001

Server simulasi menolak permintaan tersebut dengan status kode HTTP 400 Bad Request
    Mock Telkomsel Verifikasi Client Response    expected_status=400
