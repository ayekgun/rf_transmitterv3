# -*- coding: utf-8 -*-
"""Katalog Skenario Uji (Test Catalog) untuk Transmitter Infobip (JNS 6.5)

Digunakan oleh ExcelReporter untuk memetakan Test Case ID (TC001 s/d TC027)
ke dalam format pelaporan SIT standar Jatis SQA (.xlsx).
"""

TEST_CATALOG = {
    "TC001": {
        "description": "Normal Flow - Direct Route",
        "scenario": "Transmitter Infobip - Direct Send No Match",
        "test_case": "Verifikasi pengiriman pesan ke Infobip dengan sender id di DB dan no key match",
        "steps": "1. Put pesan ke queue jns.transmitter.infobip.premium.247.\n2. Verifikasi transmitter memproses pesan.\n3. Verifikasi HTTP POST ke endpoint Telco Infobip.\n4. Verifikasi field Msisdn, Sender, Message, NotifyUrl match.\n5. Verifikasi submit result dihasilkan ke queue ack.",
        "test_data": "msisdn=6281802000319, sender=QueueSenderID, servicetype=HTTPALERT",
        "expected": "Pesan sukses terkirim ke Mock Telco Infobip dengan HTTP 200 OK dan ack submitresult valid.",
    },
    "TC002": {
        "description": "Normal Flow - Direct Route",
        "scenario": "Transmitter Infobip - Direct Send Variant",
        "test_case": "Verifikasi pengiriman pesan varian sender id di DB no key match",
        "steps": "1. Put pesan ke queue transmitter.\n2. Verifikasi pemrosesan dan hit ke Telco Infobip.\n3. Verifikasi response submit result.",
        "test_data": "msisdn=6281802000319, sender=QueueSenderID",
        "expected": "Pesan sukses dikirim dan respons submitresult tercatat.",
    },
    "TC003": {
        "description": "Normal Flow - JSON Sender ID",
        "scenario": "Transmitter Infobip - Sender ID on JSON",
        "test_case": "Verifikasi pengiriman pesan dengan sender id di parameter JSON key match",
        "steps": "1. Kirim pesan dengan parameter senderids JSON.\n2. Verifikasi transmitter menggunakan kredensial dari JSON.\n3. Verifikasi pemanggilan Telco Infobip.",
        "test_data": "senderids JSON format dengan matching key provider",
        "expected": "Transmitter memprioritaskan kredensial JSON dan hit Telco sukses.",
    },
    "TC004": {
        "description": "Normal Flow - Sender ID Selection",
        "scenario": "Transmitter Infobip - Senderids on DB",
        "test_case": "Verifikasi pengiriman pesan dengan fallback senderids di DB",
        "steps": "1. Kirim pesan tanpa override spesifik.\n2. Verifikasi transmitter mengambil sender id dari DB.",
        "test_data": "senderid DB config",
        "expected": "Transmitter sukses mengirimkan pesan dengan konfigurasi senderid dari DB.",
    },
    "TC005": {
        "description": "Validation - Without Param Senderids",
        "scenario": "Transmitter Infobip - Missing Param Senderids",
        "test_case": "Verifikasi pengiriman pesan tanpa parameter senderids",
        "steps": "1. Kirim pesan tanpa field senderids.\n2. Verifikasi perilaku default transmitter.",
        "test_data": "senderids=''",
        "expected": "Pesan tetap terkirim menggunakan parameter default transmitter.",
    },
    "TC006": {
        "description": "Negative Testing - Malformed JSON",
        "scenario": "Transmitter Infobip - Bad JSON Format",
        "test_case": "Verifikasi penanganan graceful ketika format JSON senderids rusak/invalid",
        "steps": "1. Kirim pesan dengan format JSON senderids tidak valid (bad syntax).\n2. Verifikasi transmitter tidak crash dan fallback dengan aman.",
        "test_data": "senderids={invalid_json...}",
        "expected": "Transmitter menangani parsing error secara graceful dan tidak crash.",
    },
    "TC007": {
        "description": "Expiry Testing - Expired Message",
        "scenario": "Transmitter Infobip - Expired Message",
        "test_case": "Verifikasi penolakan pesan yang sudah expired berdasarkan timestamp expiry",
        "steps": "1. Kirim pesan dengan date expired lebih kecil dari waktu sekarang.\n2. Verifikasi pesan di-drop/tidak dikirim ke Telco.",
        "test_data": "expiry < current_timestamp",
        "expected": "Transmitter tidak mengirim pesan expired ke Telco dan mengirim status ERR_EXPIRED.",
    },
    "TC008": {
        "description": "Expiry Testing - Valid Expiry",
        "scenario": "Transmitter Infobip - Non-Expired Message",
        "test_case": "Verifikasi pengiriman pesan yang belum melewati waktu expiry",
        "steps": "1. Kirim pesan dengan expiry masih valid di masa depan.\n2. Verifikasi pesan diproses normal ke Telco.",
        "test_data": "expiry > current_timestamp",
        "expected": "Pesan diproses dan berhasil dikirim ke mock Telco Infobip.",
    },
    "TC009": {
        "description": "Expiry Testing - DB Sender Expired",
        "scenario": "Transmitter Infobip - DB Sender Match Expired",
        "test_case": "Verifikasi pesan expired dengan konfigurasi DB sender",
        "steps": "1. Kirim pesan expired dengan sender id DB.\n2. Verifikasi pencegahan pengiriman ke provider.",
        "test_data": "expiry expired, DB sender",
        "expected": "Pesan expired ditolak dengan benar.",
    },
    "TC010": {
        "description": "Validation - Without Parameter Senderid",
        "scenario": "Transmitter Infobip - Null Senderid",
        "test_case": "Verifikasi pengiriman pesan tanpa parameter senderid eksplisit",
        "steps": "1. Kirim pesan dengan parameter senderid kosong.\n2. Verifikasi fallback ke config transmitter.",
        "test_data": "senderid=''",
        "expected": "Pesan berhasil diproses menggunakan senderid dari konfigurasi.",
    },
    "TC011": {
        "description": "Redirect Testing - Origin MQ Name",
        "scenario": "Transmitter Infobip - Origin MQ Validation",
        "test_case": "Verifikasi pengiriman pesan dengan originMQ name",
        "steps": "1. Kirim pesan dengan field origin_mq_name.\n2. Verifikasi alur redirect transmitter.",
        "test_data": "origin_mq_name terdefinisi",
        "expected": "Pesan diproses sesuai konfigurasi routing origin.",
    },
    "TC012": {
        "description": "Redirect Testing - Telkomsel 818 Origin",
        "scenario": "Transmitter Infobip - Redirect from 818",
        "test_case": "Verifikasi redirect pesan dari origin MQ 818",
        "steps": "1. Kirim pesan melalui jalur 818.\n2. Verifikasi redirect ke transmitter 247.",
        "test_data": "origin_mq_name=jns.transmitter.infobip.premium.818",
        "expected": "Pesan sukses di-redirect dan diproses ke antrean target.",
    },
    "TC013": {
        "description": "Redirect Testing - Telkomsel 623 Origin",
        "scenario": "Transmitter Infobip - Redirect from 623",
        "test_case": "Verifikasi redirect pesan dari origin MQ 623",
        "steps": "1. Kirim pesan melalui jalur 623.\n2. Verifikasi redirect ke transmitter 247.",
        "test_data": "origin_mq_name=jns.transmitter.infobip.premium.623",
        "expected": "Pesan sukses di-redirect dan diproses ke antrean target.",
    },
    "TC014": {
        "description": "Redirect & Masking - JSON Match Other Channel 247",
        "scenario": "Transmitter Infobip - Sender ID JSON with Channel Origin 247",
        "test_case": "Verifikasi sender id on json key match dengan originMQ Name channel lain 247",
        "steps": "1. Kirim pesan dengan parameter senderids JSON key match dan origin_mq_name automq247.\n2. Verifikasi routing dan seleksi sender ID.",
        "test_data": "origin_mq_name=automq247, senderids JSON matching",
        "expected": "Pesan diproses sukses menggunakan sender ID dari JSON dan routing origin tervalidasi.",
    },
    "TC015": {
        "description": "Expiry & Origin - JSON Match Expired with Origin",
        "scenario": "Transmitter Infobip - Expired Message with Origin MQ",
        "test_case": "Verifikasi penanganan pesan expired dengan originMQ Name automq818",
        "steps": "1. Kirim pesan dengan timestamp expired dan origin_mq_name automq818.\n2. Verifikasi transmitter menolak/drop pesan.",
        "test_data": "expiry=expired, origin_mq_name=automq818",
        "expected": "Pesan expired tidak dikirim ke provider dan di-handle status error expired.",
    },
    "TC016": {
        "description": "Expiry & Origin - JSON Match Valid Expiry with Origin",
        "scenario": "Transmitter Infobip - Valid Expiry with Origin MQ",
        "test_case": "Verifikasi pesan non-expired dengan originMQ Name jns.transmitter.other.623",
        "steps": "1. Kirim pesan dengan expiry valid dan origin_mq_name jns.transmitter.other.623.\n2. Verifikasi pesan diproses ke provider.",
        "test_data": "expiry=valid, origin_mq_name=jns.transmitter.other.623",
        "expected": "Pesan berhasil diproses dan dikirim ke Telco Infobip.",
    },
    "TC017": {
        "description": "Fallback - DB Sender without Param Senderids with Origin",
        "scenario": "Transmitter Infobip - Fallback DB Sender with Origin MQ",
        "test_case": "Verifikasi sender id di DB tanpa parameter senderids dengan originMQ Name",
        "steps": "1. Kirim pesan tanpa field senderids tetapi memiliki originMQ Name.\n2. Verifikasi transmitter mengambil konfigurasi sender id dari DB.",
        "test_data": "senderids='', origin_mq_name defined",
        "expected": "Pesan diproses normal menggunakan sender id fallback dari DB.",
    },
    "TC018": {
        "description": "Credential Validation - Empty Username on Matching Key",
        "scenario": "Transmitter Infobip - JSON Key Match with Empty Username",
        "test_case": "Verifikasi perilaku saat key matching pada senderids JSON memiliki username kosong",
        "steps": "1. Kirim pesan dengan key match tetapi username pada JSON bernilai kosong.\n2. Verifikasi fallback atau pengiriman kredensial.",
        "test_data": "senderids JSON: username=''",
        "expected": "Transmitter memproses pesan atau fallback ke kredensial antrean/DB.",
    },
    "TC019": {
        "description": "Credential Validation - Empty Password on Matching Key",
        "scenario": "Transmitter Infobip - JSON Key Match with Empty Password",
        "test_case": "Verifikasi perilaku saat key matching pada senderids JSON memiliki password kosong",
        "steps": "1. Kirim pesan dengan key match tetapi password pada JSON bernilai kosong.\n2. Verifikasi penanganan transmitter.",
        "test_data": "senderids JSON: password=''",
        "expected": "Transmitter memproses pesan atau fallback ke konfigurasi default password.",
    },
    "TC020": {
        "description": "Credential Validation - Empty User & Password on Matching Key",
        "scenario": "Transmitter Infobip - JSON Key Match with Empty User and Password",
        "test_case": "Verifikasi key matching pada senderids JSON dengan username dan password kosong",
        "steps": "1. Kirim pesan dengan key match tetapi user & password JSON kosong.\n2. Verifikasi transmitter fallback ke kredensial antrean atau default.",
        "test_data": "senderids JSON: username='', password=''",
        "expected": "Transmitter fallback mengambil kredensial antrean/DB dan memproses pesan.",
    },
    "TC021": {
        "description": "Credential Validation - Empty Sender ID on Matching Key",
        "scenario": "Transmitter Infobip - JSON Key Match with Empty Sender",
        "test_case": "Verifikasi key matching pada senderids JSON dengan sender ID kosong",
        "steps": "1. Kirim pesan dengan key match tetapi sender ID JSON kosong.\n2. Verifikasi fallback ke sender queue/DB.",
        "test_data": "senderids JSON: senderID=''",
        "expected": "Transmitter fallback ke sender ID dari antrean/DB.",
    },
    "TC022": {
        "description": "Negative Testing - Empty Credential in Both JSON & Queue",
        "scenario": "Transmitter Infobip - Empty User and Password in Both Layers",
        "test_case": "Verifikasi handling ketika username dan password kosong pada JSON senderids dan queue",
        "steps": "1. Kirim pesan dengan user & pass kosong di JSON serta uid & pwd kosong di parameter antrean.\n2. Verifikasi validasi kredensial transmitter.",
        "test_data": "JSON user/pass kosong & in queue uid/pwd kosong",
        "expected": "Transmitter menolak atau menandai pesan gagal otentikasi kredensial.",
    },
    "TC023": {
        "description": "Performance & Sleep Mode",
        "scenario": "Transmitter Infobip - Sleep Mode Handling",
        "test_case": "Verifikasi pengiriman 10 pesan beruntun saat transmitter dalam sleep mode",
        "steps": "1. Kirim 10 pesan secara berurutan ke queue.\n2. Verifikasi jeda sleep_after_send dihormati oleh transmitter.",
        "test_data": "Batch 10 pesan normal",
        "expected": "Semua 10 pesan diproses sesuai interval sleep mode tanpa kehilangan data.",
    },
    "TC024": {
        "description": "Flow Control - Smart Break",
        "scenario": "Transmitter Infobip - Smart Break Mechanism",
        "test_case": "Verifikasi mekanisme Smart Break untuk menghentikan / melanjutkan konsumsi pesan",
        "steps": "1. Kirim topic command break.\n2. Verifikasi consumer berhenti membaca antrean.\n3. Kirim topic command resume.\n4. Verifikasi consumer aktif kembali.",
        "test_data": "Topic jns.topic.command",
        "expected": "Consumer berhenti saat break dan melanjutkan saat resume.",
    },
    "TC025": {
        "description": "Dual-Site Retry Mechanism",
        "scenario": "Transmitter Infobip - Retry 1 Dual-Site",
        "test_case": "Verifikasi kegagalan HTTP 404/500 memicu penyimpanan retry ke MongoDB dengan schema dual-site (site='PROD', status='READY', message_id)",
        "steps": "1. Mock Telco Infobip diset mengembalikan error 404 (id=137).\n2. Kirim pesan ke antrean.\n3. Verifikasi transmitter mendeteksi error HTTP dan menyimpan data ke MongoDB collection retry_transmitter.\n4. Validasi schema MongoDB: site='PROD', status='READY', message_id terisi, retry_count=1.",
        "test_data": "Dummy HTTP 404 response",
        "expected": "Dokumen retry tersimpan di MongoDB dengan status='READY', site='PROD', dan message_id yang cocok.",
    },
    "TC026": {
        "description": "Dual-Site Retry Mechanism",
        "scenario": "Transmitter Infobip - Retry 2 Dual-Site",
        "test_case": "Verifikasi retry kedua menyimpan dokumen retry dengan counter retry_count=2",
        "steps": "1. Pemicuan retry kedua.\n2. Verifikasi update dokumen di MongoDB.",
        "test_data": "Retry step 2",
        "expected": "Retry count diupdate menjadi 2 di MongoDB.",
    },
    "TC027": {
        "description": "Dual-Site Retry Mechanism",
        "scenario": "Transmitter Infobip - Max Retry Exceeded",
        "test_case": "Verifikasi setelah mencapai max_retry, transmitter menghentikan retry dan mengirim status FAILED_SUBMIT",
        "steps": "1. Pemicuan retry melebihi max_retry (3).\n2. Verifikasi status akhir di submitresult.",
        "test_data": "Retry step 3 (max)",
        "expected": "Pesan di-drop dari retry loop dan status submitresult FAILED_SUBMIT dikirim.",
    },
    "TC028": {
        "description": "Dual-Site Single DB Deduplication",
        "scenario": "Transmitter Mitracomm - Dual Site Deduplication",
        "test_case": "Verifikasi ketika kedua broker (PROD & DRC) dikirimi antrean identik secara simultan, hanya masuk 1 data di DB MongoDB retry_transmitter",
        "steps": "1. Set dummy response Telco ke error HTTP 404 (id=93) untuk memicu retry.\n2. Injeksi pesan antrean dengan trx_id dan message_id identik ke broker ActiveMQ PROD (.51) dan DRC (.58).\n3. Kedua transmitter (PROD & DRC) memproses antrean dan berusaha menyimpan retry ke MongoDB.\n4. Verifikasi bahwa tepat 1 dokumen retry tersimpan di MongoDB retry_transmitter (idempotent / deduplicated).",
        "test_data": "Injeksi paralel ActiveMQ PROD (192.168.181.51) dan DRC (192.168.181.58)",
        "expected": "Tepat 1 record retry tersimpan di MongoDB dengan status='READY' dan site ('PROD' atau 'DRC').",
    },
}

# Added for PB172645142601YA - Boundary Testing (IFA v5.0 MT V2)
TEST_CATALOG["TC029"] = {
    "description": "Boundary Testing - SMS 1999 Chars",
    "scenario": "Transmitter Telkomsel MT V2 - Boundary SMS Near Max Limit",
    "test_case": "Verifikasi Transmitter mampu memproses dan mengirimkan pesan SMS dengan panjang 1999 karakter secara utuh tanpa pemotongan",
    "steps": "1. Kirim antrean dengan payload sms sepanjang 1999 karakter.\n2. Verifikasi SUT membentuk JSON MT V2 ke mock Telkomsel.\n3. Validasi panjang dan isi field sms di mock sama persis 1999 karakter.\n4. Verifikasi ACK submit SUCCESS_RECEIVED.",
    "test_data": "SMS text 1999 characters (Boundary near max)",
    "expected": "Pesan 1999 karakter terkirim utuh tanpa truncate, signature valid, submit result SUCCESS_RECEIVED."
}

TEST_CATALOG["TC030"] = {
    "description": "Boundary Testing - SMS 2000 Chars Max Limit",
    "scenario": "Transmitter Telkomsel MT V2 - Boundary SMS Max Limit",
    "test_case": "Verifikasi Transmitter mampu memproses dan mengirimkan pesan SMS dengan panjang tepat 2000 karakter (batas maksimum IFA v5.0) secara utuh",
    "steps": "1. Kirim antrean dengan payload sms sepanjang 2000 karakter.\n2. Verifikasi SUT membentuk JSON MT V2 ke mock Telkomsel.\n3. Validasi panjang dan isi field sms di mock sama persis 2000 karakter.\n4. Verifikasi ACK submit SUCCESS_RECEIVED.",
    "test_data": "SMS text 2000 characters (Boundary exact max)",
    "expected": "Pesan 2000 karakter terkirim utuh tanpa truncate, signature valid, submit result SUCCESS_RECEIVED."
}

TEST_CATALOG["TC031"] = {
    "description": "Boundary Testing - SMS 2001 Chars Over Limit",
    "scenario": "Transmitter Telkomsel MT V2 - Boundary SMS Over Limit",
    "test_case": "Verifikasi perilaku Transmitter saat menerima pesan SMS melebihi batas 2000 karakter (2001 karakter)",
    "steps": "1. Kirim antrean dengan payload sms sepanjang 2001 karakter.\n2. Observasi apakah SUT menolak atau meneruskan ke endpoint Telkomsel.\n3. Verifikasi konsistensi payload dan respon submit.",
    "test_data": "SMS text 2001 characters (Boundary over limit)",
    "expected": "SUT menangani pesan 2001 karakter sesuai kontrak atau diteruskan secara aman ke provider."
}

TEST_CATALOG["TC032"] = {
    "description": "HTTP Socket Timeout Testing - SUT Client Timeout >= 15 Seconds",
    "scenario": "Transmitter Telkomsel MT V2 - Real HTTP Socket Timeout Handling (IFA v5.0 Section D)",
    "test_case": "Verifikasi Transmitter mematuhi batas client timeout minimum 15 detik, memicu SocketTimeoutException saat vendor tidak merespon dalam 16s, dan mengirimkan ACK FAILED_SUBMIT / SUCCESS_RECEIVED ke queue submitresults",
    "steps": "1. Set dummy response simulator Telkomsel dengan sleep = 16 detik (melebihi konfigurasi timeout SUT 15 detik).\n2. Kirim pesan ke antrean jns.transmitter.telkomsel.reg.247 dengan retry = 3.\n3. SUT mengirimkan request MT V2 ke mock dan menunggu hingga 15 detik sebelum timeout.\n4. Verifikasi SUT memicu SocketTimeoutException tanpa hanging thread.\n5. Verifikasi antrean jns.app.submitresults menerima ACK dengan PROVIDER_SUBMIT_STATUS = FAILED_SUBMIT dan TRANSMITTER_SUBMIT_STATUS = SUCCESS_RECEIVED.",
    "test_data": "Dummy response ID 185 (sleep = 16s, timeout limit = 15s, retry = 3)",
    "expected": "SUT mendeteksi timeout pada detik ke-15, melempar SocketTimeoutException, dan mengirimkan submit result PROVIDER_SUBMIT_STATUS=FAILED_SUBMIT serta TRANSMITTER_SUBMIT_STATUS=SUCCESS_RECEIVED."
}

TEST_CATALOG["TC033"] = {
    "description": "MSISDN Validation - Valid Alternative Telkomsel NDC Prefix 62811 (Kartu Halo)",
    "scenario": "Transmitter Telkomsel MT V2 - Valid MSISDN Halo Prefix 62811",
    "test_case": "Verifikasi Transmitter mampu mengirimkan SMS MT V2 ke nomor pelanggan dengan prefix resmi Telkomsel 62811 (Kartu Halo)",
    "steps": "1. Kirim pesan ke antrean jns.transmitter.telkomsel.reg.247 dengan MSISDN 6281102000319.\n2. Verifikasi SUT membentuk payload JSON dengan msisdn 6281102000319 dan HMAC signature valid.\n3. Vendor menerima pesan dan merespons HTTP 200 (response_code 1).\n4. Verifikasi ACK submit SUCCESS_RECEIVED (status 1).",
    "test_data": "MSISDN = 6281102000319 (Telkomsel Halo), dummy_id = 177",
    "expected": "Pesan berhasil diproses dan dikirimkan ke vendor dengan response_code 1, ACK submit status 1."
}

TEST_CATALOG["TC034"] = {
    "description": "MSISDN Validation - Invalid Non-Telkomsel MSISDN Prefix 62818 (XL Axiata)",
    "scenario": "Transmitter Telkomsel MT V2 - Negative Test Non-Telkomsel Operator Prefix",
    "test_case": "Verifikasi penanganan Transmitter saat mengirimkan nomor operator non-Telkomsel (62818 XL), vendor menolak dengan HTTP 400 (Invalid Request, code 4), dan SUT fail-fast tanpa retry",
    "steps": "1. Kirim pesan ke antrean jns.transmitter.telkomsel.reg.247 dengan MSISDN 6281802000319.\n2. SUT meneruskan pesan ke vendor.\n3. Vendor menolak dengan HTTP 400 (response_code 4 Invalid Request).\n4. SUT memetakan response_code 4 sebagai error permanen (non-retryable).\n5. Verifikasi antrean submitresults menerima ACK PROVIDER_SUBMIT_STATUS=4 dan TRANSMITTER_SUBMIT_STATUS=FAILED_SUBMIT tanpa ada pengulangan pengiriman (retry=0).",
    "test_data": "MSISDN = 6281802000319 (XL Axiata non-Telkomsel), dummy_id = 178",
    "expected": "Vendor merespon HTTP 400 (code 4), SUT tidak melakukan retry, dan mencatat submit result PROVIDER_SUBMIT_STATUS=4 serta TRANSMITTER_SUBMIT_STATUS=FAILED_SUBMIT."
}

TEST_CATALOG["TC035"] = {
    "description": "MSISDN Validation - Malformed MSISDN Local Format Without Country Code 62",
    "scenario": "Transmitter Telkomsel MT V2 - Negative Test Malformed MSISDN Without CC",
    "test_case": "Verifikasi penanganan Transmitter saat format nomor tidak menyertakan kode negara 62 (081202000319), vendor menolak dengan HTTP 400 (code 4), dan SUT fail-fast tanpa retry",
    "steps": "1. Kirim pesan ke antrean jns.transmitter.telkomsel.reg.247 dengan MSISDN 081202000319.\n2. SUT meneruskan pesan ke vendor.\n3. Vendor menolak dengan HTTP 400 (response_code 4 Invalid Request).\n4. SUT mendeteksi HTTP 400 sebagai non-retryable error.\n5. Verifikasi submit result mencatat PROVIDER_SUBMIT_STATUS=4 dan TRANSMITTER_SUBMIT_STATUS=FAILED_SUBMIT.",
    "test_data": "MSISDN = 081202000319 (Local format no CC 62), dummy_id = 178",
    "expected": "Vendor menolak format nomor lokal dengan HTTP 400, SUT fail-fast tanpa retry, submit result PROVIDER_SUBMIT_STATUS=4 dan TRANSMITTER_SUBMIT_STATUS=FAILED_SUBMIT."
}

TEST_CATALOG["TC036"] = {
    "description": "Delivery Report - Registrasi DR Pull PENDING pada ActiveMQ jns.db.mongodbv2",
    "scenario": "Transmitter Telkomsel MT V2 - Verification DR Pull PENDING Registration",
    "test_case": "Verifikasi Transmitter menerbitkan perintah registrasi DR Pull berstatus PENDING ke ActiveMQ antrean jns.db.mongodbv2 setelah MT V2 berhasil dikirim ke Telkomsel",
    "steps": "1. Kirim pesan ke antrean jns.transmitter.telkomsel.reg.247 dengan MSISDN 6281102000319.\n2. SUT meneruskan MT SMS ke Telkomsel IFA v5.0 dan menerima HTTP 200 (Success).\n3. SUT menerbitkan ACK ke antrean jns.app.submitresults.\n4. SUT memanggil registerDrPull() dan mempublikasikan command JSON ke antrean ActiveMQ jns.db.mongodbv2.\n5. Verifikasi payload ActiveMQ: collection=dr_pull_telkomsel, type=insert, status=PENDING, provider_id=1, channel_name=TSEL, attempt=0, next_pull_at=+2 menit.\n6. Verifikasi trace log SUT mencatat 'publish PENDING provider_trxid=... to queue jns.db.mongodbv2'.",
    "test_data": "MSISDN = 6281102000319, dummy_id = 177, queue = jns.db.mongodbv2",
    "expected": "Dokumen registrasi DR Pull PENDING diterbitkan ke ActiveMQ jns.db.mongodbv2 dengan metadata lengkap dan next_pull_at dijadwalkan tepat 2 menit setelah submit_date."
}
