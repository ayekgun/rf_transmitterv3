# -*- coding: utf-8 -*-
"""
MySqlDrPullLibrary.py
MySQL Library for managing apps_config.jns_config (lookup_type='drpulltelkomsel')
Supports isolated backup & restore, dynamic secret configuration, and provider_status_url updates.
"""

import os
import pymysql
from robot.api import logger
from robot.api.deco import keyword


class MySqlDrPullLibrary:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self):
        self.conn = None
        self.host = os.environ.get("MYSQL_CFG_HOST", "192.168.181.63")
        self.port = int(os.environ.get("MYSQL_CFG_PORT", 3306))
        self.user = os.environ.get("MYSQL_CFG_USER", "root")
        self.password = os.environ.get("MYSQL_CFG_PASS", "jatis123")
        self.database = os.environ.get("MYSQL_CFG_DB", "apps_config")
        self.backup_rows = []

    def _get_connection(self):
        if self.conn is None or not self.conn.open:
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True,
                cursorclass=pymysql.cursors.DictCursor,
            )
        else:
            try:
                self.conn.ping(reconnect=True)
            except Exception:
                self.conn = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    autocommit=True,
                    cursorclass=pymysql.cursors.DictCursor,
                )
        return self.conn

    @keyword("Mysql Hubungkan Ke Database Apps Config")
    def mysql_hubungkan_ke_database_apps_config(self, host=None, port=None, user=None, password=None, database=None):
        self.host = str(host or self.host)
        self.port = int(port or self.port)
        self.user = str(user or self.user)
        self.password = str(password or self.password)
        self.database = str(database or self.database)
        conn = self._get_connection()
        logger.info(f"Berhasil terhubung ke MySQL apps_config pada {self.host}:{self.port}")

    @keyword("Mysql Putuskan Dari Database Apps Config")
    def mysql_putuskan_dari_database_apps_config(self):
        if self.conn is not None and self.conn.open:
            self.conn.close()
            self.conn = None
            logger.info("Koneksi MySQL apps_config berhasil diputuskan.")

    @keyword("Mysql Backup Konfigurasi Dr Pull")
    def mysql_backup_konfigurasi_dr_pull(self):
        conn = self._get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM jns_config WHERE lookup_type = 'drpulltelkomsel'")
            self.backup_rows = cur.fetchall()
        logger.info(f"Berhasil mem-backup {len(self.backup_rows)} baris konfigurasi drpulltelkomsel.")
        return len(self.backup_rows)

    @keyword("Mysql Restore Konfigurasi Dr Pull")
    def mysql_restore_konfigurasi_dr_pull(self):
        if not self.backup_rows:
            logger.warn("Tidak ada data backup konfigurasi untuk di-restore.")
            return

        conn = self._get_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM jns_config WHERE lookup_type = 'drpulltelkomsel'")
            for r in self.backup_rows:
                cols = ", ".join(r.keys())
                placeholders = ", ".join(["%s"] * len(r))
                sql = f"INSERT INTO jns_config ({cols}) VALUES ({placeholders})"
                cur.execute(sql, list(r.values()))
        logger.info(f"Berhasil me-restore {len(self.backup_rows)} baris konfigurasi drpulltelkomsel dari backup.")

    @keyword("Mysql Update Lookup Value")
    def mysql_update_lookup_value(self, lookup_name, lookup_value):
        conn = self._get_connection()
        with conn.cursor() as cur:
            # Check if exists
            cur.execute("SELECT COUNT(*) AS cnt FROM jns_config WHERE lookup_type = 'drpulltelkomsel' AND lookup_name = %s", (lookup_name,))
            cnt = cur.fetchone()["cnt"]
            if cnt > 0:
                cur.execute(
                    "UPDATE jns_config SET lookup_value = %s WHERE lookup_type = 'drpulltelkomsel' AND lookup_name = %s",
                    (lookup_value, lookup_name),
                )
            else:
                cur.execute(
                    "INSERT INTO jns_config (lookup_type, lookup_name, lookup_value) VALUES ('drpulltelkomsel', %s, %s)",
                    (lookup_name, lookup_value),
                )
        logger.info(f"Konfigurasi drpulltelkomsel key='{lookup_name}' diset ke: '{lookup_value}'")

    @keyword("Mysql Set Konfigurasi Dr Pull Secret Dan Json")
    def mysql_set_konfigurasi_dr_pull_secret_dan_json(self, client_secret=None, client_secrets_json=None):
        if client_secret is not None:
            self.mysql_update_lookup_value("client_secret", client_secret)
        if client_secrets_json is not None:
            self.mysql_update_lookup_value("client_secrets_json", client_secrets_json)
        logger.info("Konfigurasi secret drpulltelkomsel berhasil diperbarui.")

    @keyword("Mysql Set Konfigurasi Provider Status Url")
    def mysql_set_konfigurasi_provider_status_url(self, url):
        self.mysql_update_lookup_value("provider_status_url", str(url))

    @keyword("Mysql Hapus Seluruh Secret Dr Pull")
    def mysql_hapus_seluruh_secret_dr_pull(self):
        conn = self._get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM jns_config WHERE lookup_type = 'drpulltelkomsel' AND lookup_name IN ('client_secret', 'client_secrets_json')"
            )
        logger.info("Seluruh baris secret drpulltelkomsel berhasil dihapus dari jns_config.")

    @keyword("Mysql Verifikasi Key Konfigurasi Ada")
    def mysql_verifikasi_key_konfigurasi_ada(self, *expected_keys):
        conn = self._get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT lookup_name FROM jns_config WHERE lookup_type = 'drpulltelkomsel' AND lookup_name IN %s",
                (expected_keys,),
            )
            found = {row["lookup_name"] for row in cur.fetchall()}
        missing = set(expected_keys) - found
        if missing:
            raise AssertionError(f"Key konfigurasi drpulltelkomsel tidak ditemukan di apps_config: {missing}")
        logger.info(f"Semua key konfigurasi {expected_keys} terverifikasi ada pada database.")
