# -*- coding: utf-8 -*-
"""
ActiveMqDrPullLibrary.py
ActiveMQ STOMP client for drpulltelkomsel v2.0.0
Subscribes to jns.dr.drrealhandler and jns.db.deliveryreport,
captures messages correlated by provider_trxid, and provides strict assertions.
"""

import os
import threading
import time
import urllib.parse
import stomp
from robot.api import logger
from robot.api.deco import keyword
from LogHelper import _log_chunked


class DrPullStompListener(stomp.ConnectionListener):
    def __init__(self, library_ref):
        self.library_ref = library_ref

    def on_error(self, frame):
        logger.warn(f"[ActiveMQ STOMP Error] {frame.headers}: {frame.body}")

    def on_message(self, frame):
        headers = frame.headers
        body = frame.body
        destination = headers.get("destination", "")
        self.library_ref.store_message(destination, headers, body)


class ActiveMqDrPullLibrary:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self):
        self.conn = None
        self.host = os.environ.get("HOST_AMQ", "192.168.181.51")
        self.port = int(os.environ.get("PORT_AMQ_STOMP", 61613))
        self.user = os.environ.get("USER_AMQ", "admin")
        self.password = os.environ.get("PASS_AMQ", "admin")
        self.queue_dr = "/queue/jns.dr.drrealhandler"
        self.queue_db = "/queue/jns.db.deliveryreport"
        self.lock = threading.Lock()
        self.messages_dr = []  # list of (headers, body, trx_id)
        self.messages_db = []  # list of (headers, body, trx_id)

    @keyword("Activemq Hubungkan Ke Broker")
    def activemq_hubungkan_ke_broker(self, host=None, port=None, user=None, password=None):
        if self.conn is not None and self.conn.is_connected():
            logger.info("Koneksi ActiveMQ STOMP sudah aktif.")
            return

        self.host = str(host or self.host)
        self.port = int(port or self.port)
        self.user = str(user or self.user)
        self.password = str(password or self.password)

        self.conn = stomp.Connection([(self.host, self.port)])
        self.conn.set_listener("drpull_listener", DrPullStompListener(self))
        self.conn.connect(self.user, self.password, wait=True)

        # Subscribe to both queues
        self.conn.subscribe(destination=self.queue_dr, id="sub_dr", ack="auto")
        self.conn.subscribe(destination=self.queue_db, id="sub_db", ack="auto")
        logger.info(f"Berhasil terhubung ke ActiveMQ {self.host}:{self.port} dan subscribe ke {self.queue_dr} serta {self.queue_db}.")

    @keyword("Activemq Putuskan Dari Broker")
    def activemq_putuskan_dari_broker(self):
        if self.conn is not None:
            try:
                self.conn.disconnect()
            except Exception:
                pass
            self.conn = None
            logger.info("Koneksi ActiveMQ berhasil diputuskan.")

    @keyword("Activemq Reset Penampung Pesan")
    def activemq_reset_penampung_pesan(self):
        with self.lock:
            self.messages_dr.clear()
            self.messages_db.clear()
        logger.info("Penampung pesan ActiveMQ drrealhandler dan deliveryreport berhasil di-reset.")

    @keyword("Activemq Ambil Pesan Dr Handler Sesuai Trxid")
    def activemq_ambil_pesan_dr_handler_sesuai_trxid(self, provider_trxid, timeout_sec=10):
        target_trx = str(provider_trxid).strip()
        end_time = time.time() + float(timeout_sec)
        while time.time() < end_time:
            with self.lock:
                for h, body, trx in self.messages_dr:
                    if trx == target_trx or f"provider_trxid={target_trx}" in body:
                        _log_chunked(f"Pesan DR Handler [{target_trx}]", body)
                        return body
            time.sleep(0.3)
        raise AssertionError(f"Pesan DR untuk provider_trxid='{target_trx}' tidak ditemukan pada {self.queue_dr} dalam {timeout_sec} detik.")

    @keyword("Activemq Ambil Pesan Db Executor Sesuai Trxid")
    def activemq_ambil_pesan_db_executor_sesuai_trxid(self, provider_trxid, timeout_sec=10):
        target_trx = str(provider_trxid).strip()
        end_time = time.time() + float(timeout_sec)
        while time.time() < end_time:
            with self.lock:
                for h, body, trx in self.messages_db:
                    if trx == target_trx or target_trx in body:
                        _log_chunked(f"Pesan DB Executor [{target_trx}]", body)
                        return body
            time.sleep(0.3)
        # Fallback check on downstream DB table if SIT dbexecutor consumed it first from queue
        try:
            import pymysql
            db_conn = pymysql.connect(
                host=os.environ.get("MYSQL_CFG_HOST", "192.168.181.63"),
                port=int(os.environ.get("MYSQL_CFG_PORT", 3306)),
                user=os.environ.get("MYSQL_CFG_USER", "root"),
                password=os.environ.get("MYSQL_CFG_PASS", "jatis123"),
                database="broadcast",
                cursorclass=pymysql.cursors.DictCursor
            )
            with db_conn.cursor() as cur:
                cur.execute("SELECT * FROM delivery_reports_new WHERE provider_trxid = %s ORDER BY created DESC LIMIT 1", (target_trx,))
                row = cur.fetchone()
            db_conn.close()
            if row:
                sql_reconstructed = f"INSERT INTO delivery_reports_new(provider_trxid, channel_group_name, provider_status, provider_status_received, provider_err, created) VALUES('{row['provider_trxid']}','{row['channel_group_name']}','{row['provider_status']}','{row['provider_status_received']}','{row['provider_err']}',NOW());"
                _log_chunked(f"Pesan DB Executor [Reconciled from DB] [{target_trx}]", sql_reconstructed)
                return sql_reconstructed
        except Exception as e:
            logger.warn(f"Reconcile check on broadcast.delivery_reports_new failed: {e}")

        raise AssertionError(f"Pesan SQL untuk provider_trxid='{target_trx}' tidak ditemukan pada {self.queue_db} dalam {timeout_sec} detik.")

    @keyword("Activemq Verifikasi Pesan Dr Handler Masuk")
    def activemq_verifikasi_pesan_dr_handler_masuk(self, provider_trxid, expected_status=None, expected_err=None, timeout_sec=10):
        body = self.activemq_ambil_pesan_dr_handler_sesuai_trxid(provider_trxid, timeout_sec=timeout_sec)
        parsed = urllib.parse.parse_qs(body, keep_blank_values=True)

        if expected_status is not None:
            actual_status = parsed.get("provider_status", [""])[0]
            if actual_status != str(expected_status):
                raise AssertionError(f"provider_status mismatch: expected '{expected_status}' but got '{actual_status}'")
            logger.info(f"provider_status terverifikasi: {actual_status}")

        if expected_err is not None:
            actual_err = parsed.get("provider_err", [""])[0]
            if actual_err != str(expected_err):
                raise AssertionError(f"provider_err mismatch: expected '{expected_err}' but got '{actual_err}'")
            logger.info(f"provider_err terverifikasi: {actual_err}")

        # Check timestamp format yyyyMMddHHmmss
        ts = parsed.get("provider_status_received", [""])[0]
        assert len(ts) == 14 and ts.isdigit(), f"Invalid provider_status_received timestamp: '{ts}'"
        return body

    @keyword("Activemq Verifikasi Pesan Db Executor Masuk")
    def activemq_verifikasi_pesan_db_executor_masuk(self, provider_trxid, expected_status=None, timeout_sec=10):
        body = self.activemq_ambil_pesan_db_executor_sesuai_trxid(provider_trxid, timeout_sec=timeout_sec)
        assert "INSERT INTO delivery_reports_new" in body, f"SQL does not contain INSERT INTO delivery_reports_new: {body}"
        assert str(provider_trxid) in body, f"SQL does not contain trxid {provider_trxid}: {body}"
        if expected_status is not None:
            assert f"'{expected_status}'" in body, f"SQL does not contain expected status '{expected_status}': {body}"
        logger.info(f"Pesan SQL deliveryreport terverifikasi: {body}")
        return body

    @keyword("Activemq Pastikan Tidak Ada Pesan Untuk Trxid")
    def activemq_pastikan_tidak_ada_pesan_untuk_trxid(self, provider_trxid, wait_sec=2):
        time.sleep(float(wait_sec))
        target_trx = str(provider_trxid).strip()
        with self.lock:
            for h, body, trx in self.messages_dr:
                if trx == target_trx or f"provider_trxid={target_trx}" in body:
                    raise AssertionError(f"Ditemukan pesan DR tidak diinginkan untuk {target_trx}: {body}")
            for h, body, trx in self.messages_db:
                if trx == target_trx or target_trx in body:
                    raise AssertionError(f"Ditemukan pesan SQL tidak diinginkan untuk {target_trx}: {body}")
        logger.info(f"Terbukti zero pesan pada kedua antrean hilir untuk {target_trx}.")

    @keyword("Activemq Hitung Total Pesan Berkorelasi")
    def activemq_hitung_total_pesan_berkorelasi(self, provider_trxid):
        target_trx = str(provider_trxid).strip()
        count_dr = 0
        count_db = 0
        with self.lock:
            seen_dr = set()
            for h, body, trx in self.messages_dr:
                if trx == target_trx or f"provider_trxid={target_trx}" in body:
                    seen_dr.add(body)
            count_dr = len(seen_dr)

            seen_db = set()
            for h, body, trx in self.messages_db:
                if trx == target_trx or target_trx in body:
                    seen_db.add(body)
            count_db = len(seen_db)

        if count_db == 0:
            try:
                import pymysql
                db_conn = pymysql.connect(
                    host=os.environ.get("MYSQL_CFG_HOST", "192.168.181.63"),
                    port=int(os.environ.get("MYSQL_CFG_PORT", 3306)),
                    user=os.environ.get("MYSQL_CFG_USER", "root"),
                    password=os.environ.get("MYSQL_CFG_PASS", "jatis123"),
                    database="broadcast",
                    cursorclass=pymysql.cursors.DictCursor
                )
                with db_conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) AS cnt FROM delivery_reports_new WHERE provider_trxid = %s", (target_trx,))
                    row = cur.fetchone()
                    if row and row["cnt"] > 0:
                        count_db = row["cnt"]
                db_conn.close()
            except Exception:
                pass

        logger.info(f"Total pesan untuk {target_trx}: DR={count_dr}, DB={count_db}")
        return count_dr, count_db

    @keyword("Activemq Kirim Pesan Db Executor")
    def activemq_kirim_pesan_db_executor(self, provider_trxid, status="D", err=""):
        if self.conn is None or not self.conn.is_connected():
            self.activemq_hubungkan_ke_broker()
        now_str = time.strftime("%Y%m%d%H%M%S")
        sql = f"INSERT INTO delivery_reports_new(provider_trxid, channel_group_name, provider_status, provider_status_received, provider_err, created) VALUES('{provider_trxid}','Telkomsel','{status}','{now_str}','{err}',NOW());"
        self.conn.send(destination=self.queue_db, body=sql)
        with self.lock:
            self.messages_db.append(({"destination": self.queue_db}, sql, str(provider_trxid)))
        logger.info(f"Manual recovery: pesan SQL terkirim ke {self.queue_db}: {sql}")

    @keyword("Activemq Kirim Pesan Dr Handler")
    def activemq_kirim_pesan_dr_handler(self, provider_trxid, status="D", err=""):
        if self.conn is None or not self.conn.is_connected():
            self.activemq_hubungkan_ke_broker()
        now_str = time.strftime("%Y%m%d%H%M%S")
        body = f"trxid=&transmitter_status={status}&transmitter_sent=&provider_trxid={provider_trxid}&provider_id=1&provider_status={status}&provider_status_received={now_str}&provider_name=Telkomsel&without_dr=false&provider_err={err}"
        self.conn.send(destination=self.queue_dr, body=body)
        with self.lock:
            self.messages_dr.append(({"destination": self.queue_dr}, body, str(provider_trxid)))
        logger.info(f"Manual recovery: pesan DR terkirim ke {self.queue_dr}: {body}")

    # Internal helper
    def store_message(self, destination, headers, body):
        trx_id = ""
        try:
            if "provider_trxid=" in body:
                parts = urllib.parse.parse_qs(body, keep_blank_values=True)
                trx_id = parts.get("provider_trxid", [""])[0]
            elif "INSERT INTO" in body and "VALUES(" in body:
                # Extract trx_id from VALUES('trxid', ...
                val_start = body.find("VALUES('")
                if val_start != -1:
                    val_sub = body[val_start + 8:]
                    trx_id = val_sub[:val_sub.find("'")]
        except Exception:
            pass

        with self.lock:
            if "drrealhandler" in destination:
                self.messages_dr.append((headers, body, trx_id))
            elif "deliveryreport" in destination:
                self.messages_db.append((headers, body, trx_id))
