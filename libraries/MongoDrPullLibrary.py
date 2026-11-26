# -*- coding: utf-8 -*-
"""
MongoDrPullLibrary.py
MongoDB Library for drpulltelkomsel v2.0.0
Manages smsCore.dr_pull_telkomsel collection, document planting, status assertions,
concurrency CAS simulation (claimPulling and claimPublishing).
"""

from datetime import datetime, timezone, timedelta
import json
import os
import threading
import time
from bson import ObjectId
import pymongo
from robot.api import logger
from robot.api.deco import keyword
from LogHelper import _log_chunked, log_transparent_comparison


class MongoDrPullLibrary:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.host = os.environ.get("MONGO_HOST", "192.168.181.63")
        self.port = int(os.environ.get("MONGO_PORT", 27017))
        self.username = os.environ.get("MONGO_USER", "jnsCore")
        self.password = os.environ.get("MONGO_PASS", "jnsCore123")
        self.dbname = os.environ.get("MONGO_DB", "jnsCore")
        self.colname = "dr_pull_telkomsel"

    @keyword("Mongo Hubungkan Ke Database Dr Pull")
    def mongo_hubungkan_ke_database_dr_pull(self, host=None, port=None, username=None, password=None, dbname=None):
        if self.client is not None:
            logger.info("Koneksi MongoDB Dr Pull sudah aktif.")
            return

        self.host = str(host or self.host)
        self.port = int(port or self.port)
        self.username = str(username or self.username)
        self.password = str(password or self.password)
        self.dbname = str(dbname or self.dbname)

        uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}?authSource={self.dbname}&serverSelectionTimeoutMS=5000"
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[self.dbname]
        self.collection = self.db[self.colname]
        logger.info(f"Berhasil terhubung ke MongoDB pada {self.host}:{self.port}, db={self.dbname}, col={self.colname}")

    @keyword("Mongo Putuskan Dari Database Dr Pull")
    def mongo_putuskan_dari_database_dr_pull(self):
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None
            self.collection = None
            logger.info("Koneksi MongoDB Dr Pull berhasil diputuskan.")

    @keyword("Mongo Bersihkan Dokumen Uji")
    def mongo_bersihkan_dokumen_uji(self, provider_trxid):
        if self.collection is None:
            self.mongo_hubungkan_ke_database_dr_pull()
        res = self.collection.delete_many({"provider_trxid": str(provider_trxid)})
        logger.info(f"Dihapus {res.deleted_count} dokumen uji untuk provider_trxid='{provider_trxid}'.")

    @keyword("Mongo Tanam Dokumen Dr Pull")
    def mongo_tanam_dokumen_dr_pull(
        self,
        provider_trxid,
        appsid="cp_sample",
        sid="sender_sample",
        status="PENDING",
        attempt=0,
        next_pull_at_offset_seconds=-10,
        lease_id=None,
        pwd=None,
        last_error=None,
    ):
        if self.collection is None:
            self.mongo_hubungkan_ke_database_dr_pull()

        now_dt = datetime.now(timezone.utc)
        next_pull_epoch = time.time() + float(next_pull_at_offset_seconds)
        next_pull_dt = datetime.fromtimestamp(next_pull_epoch, tz=timezone.utc)

        doc = {
            "provider_trxid": str(provider_trxid),
            "status": str(status),
            "attempt": int(attempt),
            "next_pull_at": next_pull_dt,
            "created_at": now_dt,
            "updated": now_dt,
        }

        if appsid is not None and str(appsid).strip() != "":
            doc["appsid"] = str(appsid).strip()
        if sid is not None and str(sid).strip() != "":
            doc["sid"] = str(sid).strip()
        if lease_id is not None:
            doc["lease_id"] = str(lease_id)
        if pwd is not None:
            doc["pwd"] = str(pwd)
        if last_error is not None:
            doc["last_error"] = str(last_error)

        self.collection.delete_many({"provider_trxid": str(provider_trxid)})
        res = self.collection.insert_one(doc)
        logger.info(f"Berhasil menanam dokumen Dr Pull id={res.inserted_id}, provider_trxid='{provider_trxid}', status='{status}', attempt={attempt}")
        return str(res.inserted_id)

    @keyword("Mongo Ambil Dokumen Dr Pull")
    def mongo_ambil_dokumen_dr_pull(self, provider_trxid):
        if self.collection is None:
            self.mongo_hubungkan_ke_database_dr_pull()
        doc = self.collection.find_one({"provider_trxid": str(provider_trxid)})
        if not doc:
            raise AssertionError(f"Dokumen tidak ditemukan pada koleksi dr_pull_telkomsel untuk trxid: {provider_trxid}")
        doc["_id"] = str(doc["_id"])
        _log_chunked(f"Dokumen MongoDB [{provider_trxid}]", doc)
        return doc

    @keyword("Mongo Verifikasi Status Dokumen")
    def mongo_verifikasi_status_dokumen(self, provider_trxid, expected_status):
        doc = self.mongo_ambil_dokumen_dr_pull(provider_trxid)
        actual_status = doc.get("status")
        if actual_status != str(expected_status):
            raise AssertionError(f"Status mismatch for {provider_trxid}: expected '{expected_status}' but got '{actual_status}'")
        logger.info(f"Status dokumen {provider_trxid} terbukti: {actual_status}")
        return doc

    @keyword("Mongo Update Status Dokumen")
    def mongo_update_status_dokumen(self, provider_trxid, new_status, resolved_by=None):
        if self.collection is None:
            self.mongo_hubungkan_ke_database_dr_pull()
        update_fields = {"status": str(new_status), "updated": datetime.now(timezone.utc)}
        if resolved_by:
            update_fields["resolved_by"] = str(resolved_by)
        res = self.collection.update_one({"provider_trxid": str(provider_trxid)}, {"$set": update_fields})
        logger.info(f"Update MongoDB {provider_trxid} -> status={new_status}, resolved_by={resolved_by} (matched={res.matched_count})")

    @keyword("Mongo Verifikasi Attempt Dokumen")
    def mongo_verifikasi_attempt_dokumen(self, provider_trxid, expected_attempt):
        doc = self.mongo_ambil_dokumen_dr_pull(provider_trxid)
        actual_attempt = doc.get("attempt")
        if int(actual_attempt) != int(expected_attempt):
            raise AssertionError(f"Attempt mismatch for {provider_trxid}: expected {expected_attempt} but got {actual_attempt}")
        logger.info(f"Attempt dokumen {provider_trxid} terbukti: {actual_attempt}")

    @keyword("Mongo Verifikasi Field Null")
    def mongo_verifikasi_field_null(self, provider_trxid, field_name):
        doc = self.mongo_ambil_dokumen_dr_pull(provider_trxid)
        val = doc.get(field_name)
        if val is not None:
            raise AssertionError(f"Field '{field_name}' diharapkan null tetapi bernilai: {val}")
        logger.info(f"Field '{field_name}' pada {provider_trxid} terbukti null.")

    @keyword("Mongo Verifikasi Field Not Null")
    def mongo_verifikasi_field_not_null(self, provider_trxid, field_name):
        doc = self.mongo_ambil_dokumen_dr_pull(provider_trxid)
        val = doc.get(field_name)
        if val is None:
            raise AssertionError(f"Field '{field_name}' diharapkan not null tetapi None.")
        logger.info(f"Field '{field_name}' pada {provider_trxid} terbukti terisi: {val}")

    @keyword("Mongo Verifikasi Last Error Mengandung")
    def mongo_verifikasi_last_error_mengandung(self, provider_trxid, expected_substring):
        doc = self.mongo_ambil_dokumen_dr_pull(provider_trxid)
        last_error = str(doc.get("last_error") or "")
        if expected_substring not in last_error:
            raise AssertionError(f"last_error mismatch: expected substring '{expected_substring}' in '{last_error}'")
        logger.info(f"last_error pada {provider_trxid} terbukti memuat '{expected_substring}': {last_error}")

    @keyword("Mongo Hitung Dokumen Memuat Secret")
    def mongo_hitung_dokumen_memuat_secret(self):
        if self.collection is None:
            self.mongo_hubungkan_ke_database_dr_pull()
        count = self.collection.count_documents({"$or": [{"pwd": {"$exists": True}}, {"client_secret": {"$exists": True}}]})
        logger.info(f"Total dokumen memuat secret/pwd di MongoDB: {count}")
        return count

    @keyword("Mongo Simulasikan Claim Pulling Bersamaan")
    def mongo_simulasikan_claim_pulling_bersamaan(self, provider_trxid):
        """Simulasikan 2 worker bersaing mengeksekusi claimPulling CAS update."""
        if self.collection is None:
            self.mongo_hubungkan_ke_database_dr_pull()

        doc = self.collection.find_one({"provider_trxid": str(provider_trxid)})
        if not doc:
            raise AssertionError(f"Dokumen tidak ditemukan untuk {provider_trxid}")

        doc_id = doc["_id"]
        results = [None, None]

        def _worker_claim(worker_idx, lease_id):
            update_res = self.collection.update_one(
                {"_id": doc_id, "status": "PENDING"},
                {"$set": {"status": "PULLING", "lease_id": lease_id, "updated": datetime.now(timezone.utc)}}
            )
            results[worker_idx] = (update_res.matched_count == 1)

        t1 = threading.Thread(target=_worker_claim, args=(0, "lease-worker-1"))
        t2 = threading.Thread(target=_worker_claim, args=(1, "lease-worker-2"))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        logger.info(f"Hasil kompetisi claimPulling: Worker 1={results[0]}, Worker 2={results[1]}")
        return results

    @keyword("Mongo Simulasikan Claim Publishing Bersamaan")
    def mongo_simulasikan_claim_publishing_bersamaan(self, provider_trxid, initial_lease_id):
        """Simulasikan 2 worker bersaing mengeksekusi claimPublishing CAS update."""
        if self.collection is None:
            self.mongo_hubungkan_ke_database_dr_pull()

        results = [None, None]

        def _worker_publish_claim(worker_idx, new_lease_id):
            update_res = self.collection.update_one(
                {"provider_trxid": str(provider_trxid), "status": "PULLING", "lease_id": str(initial_lease_id)},
                {"$set": {"status": "PUBLISHING", "lease_id": new_lease_id, "updated": datetime.now(timezone.utc)}}
            )
            results[worker_idx] = (update_res.matched_count == 1)

        t1 = threading.Thread(target=_worker_publish_claim, args=(0, "pub-lease-1"))
        t2 = threading.Thread(target=_worker_publish_claim, args=(1, "pub-lease-2"))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        logger.info(f"Hasil kompetisi claimPublishing: Worker 1={results[0]}, Worker 2={results[1]}")
        return results

    @keyword("Mongo Verifikasi Dokumen Terdaftar Tanpa Password")
    def mongo_verifikasi_dokumen_terdaftar_tanpa_password(self, messageid, expected_provider_trxid=None, timeout_sec=15):
        if self.collection is None:
            self.mongo_hubungkan_ke_database_dr_pull()

        mid = str(messageid).strip()
        end_time = time.time() + float(timeout_sec)
        doc = None
        while time.time() < end_time:
            doc = self.collection.find_one({"trxid": mid})
            if doc:
                break
            time.sleep(0.5)

        if not doc:
            raise AssertionError(f"Dokumen dengan trxid={mid} TIDAK DITEMUKAN pada MongoDB dr_pull_telkomsel setelah {timeout_sec}s!")

        # Anti-truncation log chunked
        doc_copy = dict(doc)
        if "_id" in doc_copy:
            doc_copy["_id"] = str(doc_copy["_id"])
        _log_chunked(f"Dokumen MongoDB Terdaftar [{mid}]", json.dumps(doc_copy, default=str, indent=2))

        # Strict Assertions
        if "pwd" in doc:
            raise AssertionError(f"Dokumen MongoDB memuat field terlarang 'pwd': {doc.get('pwd')}")
        if "client_secret" in doc:
            raise AssertionError(f"Dokumen MongoDB memuat field terlarang 'client_secret': {doc.get('client_secret')}")

        status = doc.get("status")
        if status != "PENDING":
            raise AssertionError(f"Status dokumen diharapkan 'PENDING' tetapi didapatkan '{status}'")

        attempt = str(doc.get("attempt", "0"))
        if attempt != "0":
            raise AssertionError(f"Attempt dokumen diharapkan '0' tetapi didapatkan '{attempt}'")

        if not doc.get("appsid") or not doc.get("sid"):
            raise AssertionError(f"Kredensial appsid/sid tidak lengkap di dokumen: appsid={doc.get('appsid')}, sid={doc.get('sid')}")

        provider_trxid = doc.get("provider_trxid")
        if not provider_trxid:
            raise AssertionError("Field provider_trxid pada dokumen kosong!")

        if expected_provider_trxid and str(provider_trxid).strip() != str(expected_provider_trxid).strip():
            raise AssertionError(
                f"Korelasi gagal! provider_trxid di MongoDB '{provider_trxid}' tidak cocok dengan ACK Transmitter '{expected_provider_trxid}'"
            )

        doc_id = str(doc["_id"])
        logger.info(
            f"Dokumen MongoDB terbukti valid tanpa password: _id={doc_id}, trxid={mid}, provider_trxid={provider_trxid}, status=PENDING, zero pwd"
        )
        return doc_id

    @keyword("Mongo Verifikasi Dokumen Resolved Sesuai Id Dan Metadata")
    def mongo_verifikasi_dokumen_resolved_sesuai_id_dan_metadata(
        self, doc_id, expected_trxid, expected_provider_trxid, expected_status="RESOLVED", timeout_sec=15
    ):
        if self.collection is None:
            self.mongo_hubungkan_ke_database_dr_pull()

        oid = ObjectId(str(doc_id).strip())
        target_trx = str(expected_trxid).strip()
        target_prov = str(expected_provider_trxid).strip()
        end_time = time.time() + float(timeout_sec)
        doc = None
        while time.time() < end_time:
            doc = self.collection.find_one({"_id": oid})
            if doc and doc.get("status") == str(expected_status):
                break
            time.sleep(0.3)

        if not doc:
            raise AssertionError(f"Dokumen _id={doc_id} TIDAK DITEMUKAN pada MongoDB dr_pull_telkomsel!")

        # Anti-truncation log chunked
        doc_copy = dict(doc)
        doc_copy["_id"] = str(doc_copy["_id"])
        _log_chunked(f"Dokumen MongoDB RESOLVED Sesuai _id [{doc_id}]", json.dumps(doc_copy, default=str, indent=2))

        # Strict Assertions
        actual_status = doc.get("status")
        if actual_status != str(expected_status):
            raise AssertionError(f"Status mismatch untuk _id={doc_id}: expected '{expected_status}' but got '{actual_status}'")

        actual_trxid = str(doc.get("trxid", ""))
        if actual_trxid != target_trx:
            raise AssertionError(f"trxid korelasi mismatch untuk _id={doc_id}: expected '{target_trx}' but got '{actual_trxid}'")

        actual_prov = str(doc.get("provider_trxid", ""))
        if actual_prov != target_prov:
            raise AssertionError(f"provider_trxid korelasi mismatch untuk _id={doc_id}: expected '{target_prov}' but got '{actual_prov}'")

        resolved_by = doc.get("resolved_by")
        if resolved_by != "pull":
            raise AssertionError(f"resolved_by mismatch untuk _id={doc_id}: expected 'pull' but got '{resolved_by}'")

        dr_pub = doc.get("dr_published_at")
        if not dr_pub:
            raise AssertionError(f"Metadata dr_published_at kosong pada dokumen _id={doc_id}!")

        sql_pub = doc.get("sql_published_at")
        if not sql_pub:
            raise AssertionError(f"Metadata sql_published_at kosong pada dokumen _id={doc_id}!")

        logger.info(
            f"Dokumen _id={doc_id} terverifikasi 100% konsisten: trxid={actual_trxid}, provider_trxid={actual_prov}, "
            f"status={actual_status}, resolved_by={resolved_by}, dr_published_at={dr_pub}, sql_published_at={sql_pub}"
        )
        return doc_copy

    @keyword("Mongo Percepat Waktu Next Pull Menjadi Jatuh Tempo")
    def mongo_percepat_waktu_next_pull_menjadi_jatuh_tempo(self, provider_trxid):
        if self.collection is None:
            self.mongo_hubungkan_ke_database_dr_pull()

        target_trx = str(provider_trxid).strip()
        past_time = datetime.now(timezone.utc) - timedelta(seconds=10)
        res = self.collection.update_one(
            {"provider_trxid": target_trx},
            {"$set": {"next_pull_at": past_time}}
        )
        if res.matched_count == 0:
            raise AssertionError(f"Gagal mempercepat next_pull_at: dokumen {target_trx} tidak ditemukan")
        logger.info(f"Waktu next_pull_at untuk {target_trx} berhasil dimajukan menjadi jatuh tempo.")
