# Suite Otomasi Robot Framework — drpulltelkomsel v2.0.0
Proyek: **PB172645142601YA**  
Aplikasi Target (SUT): `drpulltelkomsel-2.0.0.jar` (Get Delivery Status Telkomsel V2)

---

## 1. Prasyarat Lingkungan (Prerequisites)

Sebelum menjalankan pengujian, pastikan:

1. **Koneksi Jaringan / VPN Aktif**:
   Akses ke subnet SIT `192.168.181.x` harus aktif:
   - `192.168.181.51` (ActiveMQ broker, Transmitter Telkomsel V2, DBExecutorMongoDb)
   - `192.168.181.63` (MySQL `apps_config`, MongoDB `dr_pull_telkomsel`)
   - `192.168.181.52` (Mock Telkomsel MT V2)

   Verifikasi konektivitas:
   ```bash
   ping -c 2 192.168.181.51
   ping -c 2 192.168.181.63
   ```

2. **Layanan Pendukung Aktif**:
   - **ActiveMQ Broker** di `192.168.181.51:61616` (OpenWire), `61613` (STOMP), `8161` (REST/Web Console).
   - **Transmitter Telkomsel V2** di `192.168.181.51` (mengonsumsi `jns.transmitter.telkomsel.reg.247`).
   - **DBExecutorMongoDb** di `192.168.181.51` (mengonsumsi `jns.db.mongodbv2` $\rightarrow$ insert ke MongoDB).
   - **MySQL apps_config** di `192.168.181.63:3306` (database `apps_config`, tabel `jns_config`).
   - **MongoDB** di `192.168.181.63:27017` (database `jnsCore`, koleksi `dr_pull_telkomsel`).

3. **Python Environment**:
   Python 3.10+ dengan dependensi:
   - `robotframework`
   - `stomp.py`
   - `pymongo`
   - `pymysql`
   - `requests`
   - `python-docx`, `openpyxl` (untuk generate laporan)

---

## 2. Cara Menjalankan Pengujian Manual

Masuk ke direktori suite Robot Framework:
```bash
cd /home/gunawan/Jamob/2026/PB172645142601YA/drpulltelkomsel/rf_drpulltelkomsel
```

### A. Menjalankan Khusus TC-035 (Integrasi Transmitter ke DR Pull)
Untuk menguji aliran end-to-end lengkap dari SMS MT Transmitter hingga status DR Pull RESOLVED:
```bash
./scripts/run_tests.sh --test "*TC-035*"
```

### B. Menjalankan Seluruh Test Suite (TC-001 s/d TC-035)
Untuk mengeksekusi seluruh 35 skenario pengujian:
```bash
./scripts/run_tests.sh
```

### C. Menjalankan Test Case Spesifik Tertentu
Gunakan opsi `--test` dengan pola nama test:
```bash
# Menjalankan TC-001 (Happy path Delivered)
./scripts/run_tests.sh --test "*TC-001*"

# Menjalankan TC-031 (Fault injection ActiveMQ queue error)
./scripts/run_tests.sh --test "*TC-031*"

# Menjalankan TC-033 (Multi-instance publishing fence)
./scripts/run_tests.sh --test "*TC-033*"
```

### D. Menjalankan Berdasarkan Tag Kategori
Gunakan opsi `--include`:
```bash
# Menjalankan hanya kategori P0
./scripts/run_tests.sh --include P0

# Menjalankan kategori end-to-end
./scripts/run_tests.sh --include end_to_end
```

---

## 3. Skrip Validasi & Audit Kepatuhan (Quality Gates)

Suite ini dilengkapi skrip verifikasi otomatis untuk memastikan standar Clean BDD dan integritas keyword:

```bash
# Cek duplikasi keyword antar berkas .robot
./scripts/check_duplicate_keywords.sh

# Cek potensi tabrakan / rekursi keyword
./scripts/check_keyword_collision.sh

# Cek apakah seluruh keyword di test case ter-resolve
./scripts/check_missing_keywords.sh
```

---

## 4. Menghasilkan Laporan Executive Summary (Word & Excel)

Setelah pengujian dijalankan, Anda dapat membuat ulang laporan ringkasan eksekutif secara otomatis:

```bash
# Generate laporan Excel
python3 scripts/generate_summary_xlsx.py

# Generate laporan Word
python3 scripts/generate_summary_docx.py
```

Laporan akan diperbarui pada direktori `docs/`:
- `docs/Summary_Hasil_Testing_PB172645152602YA_drpulltelkomsel.xlsx`
- `docs/Summary_Hasil_Testing_drpulltelkomsel_v2.0.0.docx`

---

## 5. Lokasi Berkas Hasil & Log Pengujian

| Berkas | Keterangan |
| :--- | :--- |
| `results/log.html` | Log interaktif Robot Framework (lengkap dengan payload dump chunked) |
| `results/report.html` | Ringkasan visual eksekusi pengujian |
| `results/output.xml` | XML log mesin Robot Framework untuk integrasi CI/CD |
| `testcase.csv` | Tabel 12 kolom resmi hasil pengujian (Status, Actual Result, Artifact log) |
| `doc/testcase.csv` | Salinan terarsip dari `testcase.csv` |
| `bin/log/` | Log aplikasi Java SUT (`drpulltelkomsel.debug.log`, `out-drpulltelkomsel.log`) |

---

## 6. Detail Validasi TC-035 (End-to-End Integration)

TC-035 membuktikan 6 kriteria penerimaan tanpa asumsi dan tanpa celah *false positive*:
1. **Identitas Konsisten**: `messageid` unik $\rightarrow$ ACK Transmitter $\rightarrow$ MongoDB `_id` & `provider_trxid` $\rightarrow$ Mock Telkomsel $\rightarrow$ Queue DR $\rightarrow$ Queue SQL $\rightarrow$ MongoDB RESOLVED.
2. **Secret Eksklusif MySQL**: Menggunakan pasangan `INTEG_APP_035:INTEG_SID_035` dengan secret khusus `SECRET_TC035_UNIQUE` di `apps_config.jns_config`. Signature dibuktikan lolos terhadap secret khusus dan gagal terhadap secret fallback/default.
3. **Penguncian Dokumen `_id`**: Dokumen awal dikunci melalui `_id` (ObjectId) saat PENDING dan dibuktikan berubah menjadi `RESOLVED` pada `_id` yang sama.
4. **Pesan Aktual ActiveMQ**: Pesan DR (`status=D`) dan SQL INSERT tertangkap langsung dari antrean ActiveMQ, masing-masing tepat 1 kali tanpa duplikasi.
5. **Metadata MongoDB Valid**: Dokumen final memuat `resolved_by = "pull"`, serta timestamp `dr_published_at` dan `sql_published_at` bertipe datetime valid pasca-publikasi.
6. **Isolasi Pengujian**: Data transaksi diisolasi menggunakan ID unik dan dibersihkan saat teardown.
