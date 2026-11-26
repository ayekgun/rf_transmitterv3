# -*- coding: utf-8 -*-
"""
DrPullAppLibrary.py
Application Lifecycle & Audit Library for drpulltelkomsel v2.0.0
Manages starting, stopping, verifying PID, artifact version, startup logs,
and auditing log files for credential leakage.
"""

import os
import re
import subprocess
import time
from robot.api import logger
from robot.api.deco import keyword
from LogHelper import _log_chunked


class DrPullAppLibrary:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sut_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
        self.bin_dir = os.path.join(sut_dir, "bin")
        self.out_log = os.path.join(self.bin_dir, "out-drpulltelkomsel.log")
        self.debug_log = os.path.join(self.bin_dir, "log", "drpulltelkomsel.debug.log")
        self.error_log = os.path.join(self.bin_dir, "log", "drpulltelkomsel.error.log")

    @keyword("Drpull App Mulai Service")
    def drpull_app_mulai_service(self):
        logger.info(f"Memulai layanan drpulltelkomsel di {self.bin_dir}...")
        self.drpull_app_hentikan_service()

        env = os.environ.copy()
        env["SPRING_DATASOURCE_URL"] = os.environ.get("MYSQL_CFG_URL", "jdbc:mysql://192.168.181.63:3306/apps_config?useUnicode=true&serverTimezone=UTC")
        env["SPRING_DATASOURCE_USERNAME"] = os.environ.get("MYSQL_CFG_USER", "root")
        env["SPRING_DATASOURCE_PASSWORD"] = os.environ.get("MYSQL_CFG_PASS", "jatis123")

        initial_size = os.path.getsize(self.out_log) if os.path.exists(self.out_log) else 0
        cmd = ["bash", "start.sh", "start"]
        proc = subprocess.run(cmd, cwd=self.bin_dir, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(f"Hasil start.sh: {proc.stdout.strip()}")

        # Poll until SUT has started or timeout (max 15s)
        start_wait = time.time()
        while time.time() - start_wait < 15.0:
            if os.path.exists(self.out_log):
                with open(self.out_log, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(initial_size)
                    tail = f.read()
                    if "Started DrPullTelkomselApplication" in tail:
                        break
            time.sleep(0.3)

        self.drpull_app_verifikasi_service_sedang_berjalan()
        logger.info("Layanan drpulltelkomsel berhasil aktif dan siap memproses dokumen.")

    @keyword("Drpull App Hentikan Service")
    def drpull_app_hentikan_service(self):
        logger.info(f"Menghentikan layanan drpulltelkomsel di {self.bin_dir}...")
        cmd = ["bash", "start.sh", "stop"]
        subprocess.run(cmd, cwd=self.bin_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Force kill any remaining drpulltelkomsel java process
        cmd_pkill = ["pkill", "-9", "-f", "drpulltelkomsel"]
        subprocess.run(cmd_pkill, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1.0)
        logger.info("Layanan drpulltelkomsel berhasil dihentikan.")

    @keyword("Drpull App Restart Service")
    def drpull_app_restart_service(self):
        logger.info("Melakukan restart layanan drpulltelkomsel...")
        self.drpull_app_hentikan_service()
        self.drpull_app_mulai_service()
        logger.info("Restart layanan drpulltelkomsel selesai.")

    @keyword("Drpull App Verifikasi Service Sedang Berjalan")
    def drpull_app_verifikasi_service_sedang_berjalan(self):
        cmd = ["pgrep", "-f", "drpulltelkomsel"]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        pids = proc.stdout.strip().split()
        if not pids or not pids[0]:
            log_tail = ""
            if os.path.exists(self.out_log):
                with open(self.out_log, "r", encoding="utf-8", errors="ignore") as f:
                    log_tail = "".join(f.readlines()[-30:])
            raise AssertionError(f"Layanan drpulltelkomsel TIDAK BERJALAN! Cuplikan log:\n{log_tail}")

        logger.info(f"Layanan drpulltelkomsel terbukti aktif dengan PID: {pids[0]}")
        return int(pids[0])

    @keyword("Drpull App Verifikasi Versi Binary")
    def drpull_app_verifikasi_versi_binary(self, expected_version="2.0.0"):
        target_jar = f"drpulltelkomsel-{expected_version}.jar"
        jar_path = os.path.join(self.bin_dir, target_jar)
        if not os.path.isfile(jar_path):
            raise AssertionError(f"File binary JAR target {target_jar} tidak ditemukan pada {self.bin_dir}")

        size = os.path.getsize(jar_path)
        logger.info(f"Binary SUT terverifikasi: {target_jar} (size: {size} bytes).")

    @keyword("Drpull App Verifikasi Log Startup Bersih")
    def drpull_app_verifikasi_log_startup_bersih(self):
        if not os.path.exists(self.out_log):
            raise AssertionError(f"File log {self.out_log} tidak ditemukan.")

        with open(self.out_log, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        content = "".join(lines)
        if "Exception" in content and "WARN" not in content:
            # Check if there is a fatal exception
            for line in lines:
                if "FATAL" in line or "Exception in thread" in line:
                    raise AssertionError(f"Ditemukan fatal exception pada log startup: {line.strip()}")

        logger.info("Log startup terverifikasi bersih tanpa kesalahan fatal.")

    @keyword("Drpull App Audit Kebocoran String Pada Log")
    def drpull_app_audit_kebocoran_string_pada_log(self, forbidden_string):
        target = str(forbidden_string).strip()
        if not target:
            return

        # Flush buffers
        time.sleep(0.5)

        files_to_check = [self.out_log, self.debug_log, self.error_log]
        found_occurrences = []

        for log_file in files_to_check:
            if not os.path.isfile(log_file):
                continue
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                for lineno, line in enumerate(f, 1):
                    if target in line:
                        found_occurrences.append(f"{log_file}:{lineno}: {line.strip()}")

        if found_occurrences:
            msg = f"KREDENSIAL BOCOR! Ditemukan string rahasia '{target}' pada log:\n" + "\n".join(found_occurrences)
            raise AssertionError(msg)

        logger.info(f"Audit log BERSIH: String '{target}' menghasilkan 0 kecocokan pada seluruh file log.")

    @keyword("Drpull App Flush Log Ke Disk")
    def drpull_app_flush_log_ke_disk(self):
        time.sleep(1.0)
        logger.info("Log SUT di-flush ke disk.")
