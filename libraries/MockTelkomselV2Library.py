# -*- coding: utf-8 -*-
"""
MockTelkomselV2Library.py
Mock Server Telkomsel Get Delivery Status V2 (IFA SMS Bulk Premium v5.0 §E.iv & §E.vi)
Thread-safe HTTPServer with Request-Anchored Virtual Clock & mock_events_queue integration.
"""

import hmac
import hashlib
import json
import os
import socket
import threading
import time
import urllib.request
import urllib.parse
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

from robot.api import logger
from robot.api.deco import keyword
from mock_events_queue import record_mock_event, clear_mock_events
from LogHelper import _log_chunked

EXPECTED_PATH = "/bank/v2/transaction-status"
ALLOWED_TIMESTAMP_SKEW_SECONDS = 300
MALFORMED_HTML = b"<html><body><h1>Bad Gateway Error 502</h1><p>" + (b"x" * 250) + b"</p></body></html>"


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            try:
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except OSError:
                pass
        super().server_bind()


class TelkomselV2MockHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Override to suppress default console logging
        pass

    def _send_json(self, status, payload):
        try:
            body = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def _send_error(self, status, error_code, message):
        self._send_json(status, {"error": True, "error_code": error_code, "message": message})

    def do_GET(self):
        server_ref = self.server.library_ref
        server_ref.increment_hit_counter()
        record_mock_event("HTTP_GET_RECEIVED", path=self.path, method="GET")
        self._send_error(405, 2405, "Use POST")

    def do_POST(self):
        server_ref = self.server.library_ref
        server_ref.increment_hit_counter()

        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parsed_url.query

        # 1. Path check
        if path != EXPECTED_PATH:
            self._send_error(404, 2404, "Not Found")
            return

        # 2. Query string forbidden
        if query:
            self._send_error(400, 2400, "Invalid Request: parameters must not be in query string")
            return

        # 3. Headers check
        appsid = self.headers.get("appsid") or ""
        sid = self.headers.get("sid") or ""
        timestamp = self.headers.get("X-Timestamp") or ""
        signature = self.headers.get("X-Signature") or ""

        if not appsid or not sid or not timestamp or not signature:
            self._send_error(401, 2401, "Authentication Error: missing headers")
            return

        # 4. Request-Anchored Virtual Clock Skew Check
        try:
            ts_int = int(timestamp)
        except ValueError:
            self._send_error(401, 2401, "Authentication Error: invalid timestamp format")
            return

        with server_ref.lock:
            virtual_delta = server_ref.virtual_clock_delta

        if virtual_delta is not None:
            # Deterministic Request-Anchored Virtual Clock: mock_virtual_time = ts_int + virtual_delta
            # skew = abs(mock_virtual_time - ts_int) = abs(virtual_delta)
            skew = abs(virtual_delta)
        else:
            skew = abs(int(time.time()) - ts_int)

        if skew > ALLOWED_TIMESTAMP_SKEW_SECONDS:
            self._send_error(401, 2401, "Authentication Error: timestamp skew exceeded")
            return

        # 5. Read body
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else ""

        # 6. Verify HMAC Signature
        canonical = f"POST\n{path}\n{appsid}\n{sid}\n{timestamp}\n{raw_body}"
        expected_secret = server_ref.resolve_expected_secret(appsid, sid)

        if expected_secret:
            expected_sig = hmac.new(
                expected_secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature.lower(), expected_sig.lower()):
                self._send_error(401, 2401, "Authentication Error: signature mismatch")
                return

        # 7. Parse JSON body
        try:
            body_json = json.loads(raw_body)
            trx_id = str(body_json.get("transaction_id", ""))
        except Exception:
            self._send_error(400, 2400, "Invalid Request: body must be valid JSON")
            return

        if not trx_id:
            self._send_error(400, 2400, "Invalid Request: missing transaction_id")
            return

        # Store captured request
        captured = {
            "method": "POST",
            "path": path,
            "appsid": appsid,
            "sid": sid,
            "timestamp": timestamp,
            "signature": signature,
            "headers": dict(self.headers),
            "raw_body": raw_body,
            "transaction_id": trx_id,
            "skew": skew,
        }
        server_ref.store_captured_request(trx_id, captured)
        record_mock_event("TELKOMSEL_V2_REQUEST", trx_id=trx_id, appsid=appsid, signature=signature)

        # 8. Scenario Routing by transaction_id prefix or custom rule
        custom_rule = server_ref.get_custom_rule(trx_id)
        if custom_rule:
            status_code = custom_rule.get("status_code", 200)
            body = custom_rule.get("body", {})
            self._send_json(status_code, body)
            return

        if trx_id.startswith("MOCK-404-"):
            self._send_error(404, 2404, "Transaction Not Found")
        elif trx_id.startswith("MOCK-400-"):
            self._send_error(400, 2400, "Invalid Request")
        elif trx_id.startswith("MOCK-401-"):
            self._send_error(401, 2401, "Authentication Error")
        elif trx_id.startswith("MOCK-405-"):
            self._send_error(405, 2405, "Use POST")
        elif trx_id.startswith("MOCK-500-"):
            self._send_json(500, {"error": True, "error_code": 500, "message": "internal server error"})
        elif trx_id.startswith("MOCK-502-"):
            self._send_json(502, {"error": True, "error_code": 502, "message": "Bad Gateway"})
        elif trx_id.startswith("MOCK-503-"):
            self._send_json(503, {"error": True, "error_code": 503, "message": "Service Unavailable"})
        elif trx_id.startswith("MOCK-TIMEOUT-"):
            time.sleep(35)
            self._respond_success(trx_id, "D", "000")
        elif trx_id.startswith("MOCK-MALFORMED-"):
            self._send_json(200, MALFORMED_HTML)
        elif trx_id.startswith("MOCK-ND-"):
            self._respond_success(trx_id, "ND", "061")
        else:
            self._respond_success(trx_id, "D", "000")

    def _respond_success(self, trx_id, delivery_status, error_code):
        payload = {
            "transactionID": trx_id,
            "deliveryStatus": delivery_status,
            "errorCode": error_code,
            "deliveryDate": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self._send_json(200, payload)


class MockTelkomselV2Library:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self):
        self.server = None
        self.server_thread = None
        self.host = os.environ.get("MOCK_HOST", "192.168.181.51")
        self.port = int(os.environ.get("MOCK_PORT", 8095))
        self.lock = threading.Lock()
        self.hit_counter = 0
        self.secret = "7s5tLvM1"
        self.secrets_map = {}
        self.virtual_clock_delta = None
        self.captured_requests = {}
        self.custom_rules = {}
        self.is_remote = False
        self.control_url = f"http://{self.host}:{self.port}"

    def _remote_get(self, path):
        url = f"{self.control_url}{path}"
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.warn(f"Failed remote GET {url}: {e}")
            return {}

    def _remote_post(self, path, payload=None):
        url = f"{self.control_url}{path}"
        data = json.dumps(payload or {}).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.warn(f"Failed remote POST {url}: {e}")
            return {}

    def _sync_remote_events(self):
        if not self.is_remote:
            return
        res = self._remote_get("/mock-ctrl/events?drain=1")
        events = res.get("events", [])
        for ev in events:
            event_type = ev.get("event", "UNKNOWN")
            kwargs = {k: v for k, v in ev.items() if k not in ("ts", "event")}
            record_mock_event(event_type, **kwargs)

    @keyword("Mock Telkomsel Mulai Server")
    def mock_telkomsel_mulai_server(self, port=None, secret="7s5tLvM1"):
        if port is not None:
            self.port = int(port)
            self.control_url = f"http://{self.host}:{self.port}"
        if secret:
            self.secret = str(secret).strip()

        # Check if remote mock server is active (e.g. on Server 51)
        try:
            res = self._remote_get("/mock-ctrl/health")
            if res.get("status") == "ok":
                self.is_remote = True
                self._remote_post("/mock-ctrl/reset")
                self._remote_post("/mock-ctrl/set-secret", {"secret": self.secret})
                clear_mock_events()
                logger.info(f"Connected to remote Mock Telkomsel V2 Server at {self.control_url}")
                return
        except Exception:
            pass

        self.is_remote = False
        if self.server is not None:
            logger.info("Local Mock Telkomsel V2 Server sudah aktif.")
            return

        self.virtual_clock_delta = None
        with self.lock:
            self.hit_counter = 0
            self.captured_requests.clear()
            self.custom_rules.clear()
            self.secrets_map.clear()

        clear_mock_events()
        self.server = ThreadedHTTPServer(("0.0.0.0", self.port), TelkomselV2MockHandler)
        self.server.library_ref = self

        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        logger.info(f"Local Mock Telkomsel V2 Server berhasil berjalan pada port {self.port} dengan secret default '{self.secret}'.")

    @keyword("Mock Telkomsel Hentikan Server")
    def mock_telkomsel_hentikan_server(self):
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
            self.server_thread = None
            logger.info("Local Mock Telkomsel V2 Server berhasil dihentikan.")
        elif self.is_remote:
            logger.info(f"Remote Mock Telkomsel V2 Server at {self.control_url} tetap berjalan sebagai daemon.")

    @keyword("Mock Telkomsel Reset Perekam Request")
    def mock_telkomsel_reset_perekam_request(self):
        if self.is_remote:
            self._remote_post("/mock-ctrl/reset")
            self._remote_post("/mock-ctrl/set-secret", {"secret": self.secret})
        with self.lock:
            self.hit_counter = 0
            self.captured_requests.clear()
            self.custom_rules.clear()
            self.virtual_clock_delta = None
        clear_mock_events()
        logger.info("Rekaman request Mock Telkomsel V2 berhasil di-reset.")

    @keyword("Mock Telkomsel Set Secret")
    def mock_telkomsel_set_secret(self, secret):
        self.secret = str(secret).strip()
        if self.is_remote:
            self._remote_post("/mock-ctrl/set-secret", {"secret": self.secret})
        with self.lock:
            pass
        logger.info(f"Mock Telkomsel secret diset ke: {self.secret}")

    @keyword("Mock Telkomsel Set Virtual Clock Delta")
    def mock_telkomsel_set_virtual_clock_delta(self, delta_seconds):
        self.virtual_clock_delta = int(delta_seconds) if delta_seconds is not None else None
        if self.is_remote:
            self._remote_post("/mock-ctrl/set-skew", {"skew_seconds": self.virtual_clock_delta})
        logger.info(f"Mock Telkomsel Request-Anchored Virtual Clock Delta diset ke: {self.virtual_clock_delta} detik.")

    @keyword("Mock Telkomsel Set Aturan Respons Kustom")
    def mock_telkomsel_set_aturan_respons_kustom(self, trx_id, status_code=200, body=None):
        status = int(status_code)
        b = body if body is not None else {}
        if self.is_remote:
            self._remote_post("/mock-ctrl/set-rule", {"trx_id": str(trx_id), "status_code": status, "body": b})
        with self.lock:
            self.custom_rules[str(trx_id)] = {
                "status_code": status,
                "body": b,
            }
        logger.info(f"Aturan respons kustom untuk trx {trx_id} diset: HTTP {status_code}")

    @keyword("Mock Telkomsel Ambil Jumlah Hit")
    def mock_telkomsel_ambil_jumlah_hit(self):
        if self.is_remote:
            stats = self._remote_get("/mock-ctrl/stats")
            return stats.get("hit_counter", 0)
        with self.lock:
            return self.hit_counter

    @keyword("Mock Telkomsel Ambil Request Terakhir")
    def mock_telkomsel_ambil_request_terakhir(self, trx_id):
        self._sync_remote_events()
        if self.is_remote:
            res = self._remote_get(f"/mock-ctrl/captured?trx_id={trx_id}")
            return res.get("data") or {}
        with self.lock:
            return self.captured_requests.get(str(trx_id), {})

    @keyword("Mock Telkomsel Verifikasi Request V2 Masuk")
    def mock_telkomsel_verifikasi_request_v2_masuk(self, trx_id, expected_appsid=None, expected_sid=None):
        req = self.mock_telkomsel_ambil_request_terakhir(trx_id)
        if not req:
            raise AssertionError(f"Mock Telkomsel V2 tidak menerima request untuk trx_id: {trx_id}")

        assert req["method"] == "POST", f"Expected POST but got {req['method']}"
        assert req["path"] == EXPECTED_PATH, f"Expected {EXPECTED_PATH} but got {req['path']}"
        assert len(req["signature"]) == 64, f"Invalid signature length: {req['signature']}"
        assert req["transaction_id"] == trx_id, f"Expected trx_id {trx_id} but got {req['transaction_id']}"
        if expected_appsid:
            assert req["appsid"] == str(expected_appsid), f"Expected appsid {expected_appsid} but got {req['appsid']}"
        if expected_sid:
            assert req["sid"] == str(expected_sid), f"Expected sid {expected_sid} but got {req['sid']}"
        logger.info(f"Mock Telkomsel V2 berhasil memverifikasi request untuk {trx_id}: appsid={req['appsid']}, sid={req['sid']}, signature={req['signature']}")
        return req

    @keyword("Mock Telkomsel Verifikasi Signature Menggunakan Secret Eksklusif")
    def mock_telkomsel_verifikasi_signature_menggunakan_secret_eksklusif(self, trx_id, expected_secret, rejected_secrets):
        req = self.mock_telkomsel_ambil_request_terakhir(trx_id)
        if not req:
            raise AssertionError(f"Mock Telkomsel V2 tidak menerima request untuk trx_id: {trx_id}")

        sig_actual = req["signature"].lower()
        path = req["path"]
        appsid = req["appsid"]
        sid = req["sid"]
        timestamp = req["timestamp"]
        raw_body = req.get("raw_body", "")
        canonical = f"POST\n{path}\n{appsid}\n{sid}\n{timestamp}\n{raw_body}"

        # Calculate signature with expected secret
        expected_sig = hmac.new(
            str(expected_secret).encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256
        ).hexdigest().lower()

        if sig_actual != expected_sig:
            raise AssertionError(
                f"Signature mismatch! Actual {sig_actual} tidak cocok dengan kalkulasi secret yang diharapkan ({expected_secret}) -> {expected_sig}"
            )

        # Check rejected secrets
        if isinstance(rejected_secrets, str):
            rejected_list = [s.strip() for s in rejected_secrets.split(",")]
        elif isinstance(rejected_secrets, (list, tuple)):
            rejected_list = list(rejected_secrets)
        else:
            rejected_list = [str(rejected_secrets)]

        for rej_sec in rejected_list:
            rej_sig = hmac.new(
                str(rej_sec).encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256
            ).hexdigest().lower()
            if sig_actual == rej_sig:
                raise AssertionError(
                    f"Prioritas gagal! Signature cocok dengan secret tingkat bawah ({rej_sec})!"
                )

        logger.info(f"Kalkulasi signature {trx_id} terbukti valid menggunakan expected secret '{expected_secret}' dan berbeda dari seluruh alternatif {rejected_list}.")

    @keyword("Mock Telkomsel Set Secret Map")
    def mock_telkomsel_set_secret_map(self, secrets_json):
        if isinstance(secrets_json, str):
            try:
                self.secrets_map = json.loads(secrets_json)
            except Exception:
                self.secrets_map = {}
        elif isinstance(secrets_json, dict):
            self.secrets_map = dict(secrets_json)
        if self.is_remote:
            self._remote_post("/mock-ctrl/set-secret-map", {"secrets_map": self.secrets_map})
        logger.info(f"Mock Telkomsel secret map diset: {list(self.secrets_map.keys())}")

    @keyword("Mock Telkomsel Kirim Direct Http")
    def mock_telkomsel_kirim_direct_http(self, method="GET", path_with_query="/bank/v2/transaction-status", headers=None, body=None):
        import urllib.request
        import urllib.error
        base_url = self.control_url if self.is_remote else f"http://127.0.0.1:{self.port}"
        url = f"{base_url}{path_with_query}"
        req_headers = headers or {}
        req_data = body.encode("utf-8") if isinstance(body, str) else body
        req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                status = resp.status
                resp_body = resp.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            status = e.code
            resp_body = e.read().decode("utf-8", errors="ignore")
        except Exception as e:
            status = 0
            resp_body = str(e)

        try:
            parsed_json = json.loads(resp_body)
        except Exception:
            parsed_json = {}

        self.last_client_response = {
            "status": status,
            "raw_body": resp_body,
            "json": parsed_json,
        }
        _log_chunked("Direct Client Response", self.last_client_response)
        return self.last_client_response

    @keyword("Mock Telkomsel Verifikasi Client Response")
    def mock_telkomsel_verifikasi_client_response(self, expected_status=None, expected_error_code=None, expected_message_substring=None):
        resp = getattr(self, "last_client_response", None)
        if not resp:
            raise AssertionError("Belum ada direct client response yang dicatat.")

        if expected_status is not None and int(resp["status"]) != int(expected_status):
            raise AssertionError(f"Status mismatch: expected {expected_status} but got {resp['status']}")

        body_json = resp.get("json", {})
        if expected_error_code is not None:
            actual_code = body_json.get("error_code")
            if int(actual_code) != int(expected_error_code):
                raise AssertionError(f"error_code mismatch: expected {expected_error_code} but got {actual_code}")

        if expected_message_substring is not None:
            actual_msg = str(body_json.get("message", ""))
            if expected_message_substring not in actual_msg:
                raise AssertionError(f"message substring mismatch: expected '{expected_message_substring}' in '{actual_msg}'")

        logger.info(f"Direct Client Response terverifikasi: status={resp['status']}, body={resp['raw_body']}")

    @keyword("Mock Telkomsel Uji Sensitivitas Hmac")
    def mock_telkomsel_uji_sensitivitas_hmac(self, trx_id, secret=None):
        req = self.mock_telkomsel_ambil_request_terakhir(trx_id)
        if not req:
            raise AssertionError(f"Request {trx_id} tidak ditemukan.")

        sec = secret or self.resolve_expected_secret(req["appsid"], req["sid"])
        canon_orig = f"POST\n{req['path']}\n{req['appsid']}\n{req['sid']}\n{req['timestamp']}\n{req['raw_body']}"
        sig_orig = hmac.new(sec.encode("utf-8"), canon_orig.encode("utf-8"), hashlib.sha256).hexdigest()

        # 1. Mutasi body
        mut_body = req["raw_body"] + " "
        canon_body = f"POST\n{req['path']}\n{req['appsid']}\n{req['sid']}\n{req['timestamp']}\n{mut_body}"
        sig_mut_body = hmac.new(sec.encode("utf-8"), canon_body.encode("utf-8"), hashlib.sha256).hexdigest()
        assert sig_mut_body != sig_orig, "Mutasi body gagal mengubah signature!"

        # 2. Mutasi timestamp
        mut_ts = str(int(req["timestamp"]) + 1)
        canon_ts = f"POST\n{req['path']}\n{req['appsid']}\n{req['sid']}\n{mut_ts}\n{req['raw_body']}"
        sig_mut_ts = hmac.new(sec.encode("utf-8"), canon_ts.encode("utf-8"), hashlib.sha256).hexdigest()
        assert sig_mut_ts != sig_orig, "Mutasi timestamp gagal mengubah signature!"

        # 3. Mutasi secret
        mut_sec = sec + "_mutated"
        sig_mut_sec = hmac.new(mut_sec.encode("utf-8"), canon_orig.encode("utf-8"), hashlib.sha256).hexdigest()
        assert sig_mut_sec != sig_orig, "Mutasi secret gagal mengubah signature!"

        logger.info(f"[HMAC SENSITIVITY PROVEN] Original Sig: {sig_orig}")
        logger.info(f" - Body Mutated Sig:      {sig_mut_body} (DIFF)")
        logger.info(f" - Timestamp Mutated Sig: {sig_mut_ts} (DIFF)")
        logger.info(f" - Secret Mutated Sig:    {sig_mut_sec} (DIFF)")

    # Internal helpers
    def increment_hit_counter(self):
        with self.lock:
            self.hit_counter += 1

    def store_captured_request(self, trx_id, data):
        with self.lock:
            self.captured_requests[str(trx_id)] = data

    def get_custom_rule(self, trx_id):
        with self.lock:
            return self.custom_rules.get(str(trx_id))

    def resolve_expected_secret(self, appsid, sid):
        with self.lock:
            # 1. appsid:sid
            key_exact = f"{appsid}:{sid}"
            if key_exact in self.secrets_map:
                return self.secrets_map[key_exact]
            # 2. appsid
            if appsid in self.secrets_map:
                return self.secrets_map[appsid]
            # 3. default
            return self.secret
