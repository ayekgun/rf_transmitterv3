#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mock_drpull.py
Mock Server Telkomsel Get Delivery Status V2 (IFA SMS Bulk Premium v5.0 E.iv & E.vi)
Running directly on Server 51 with REST Control API for Robot Framework / CI.
"""

import datetime
import hashlib
import hmac
import json
import os
import socket
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get("MOCK_PORT", 8095))
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


class MockState:
    def __init__(self):
        self.lock = threading.Lock()
        self.hit_counter = 0
        self.secret = "7s5tLvM1"
        self.secrets_map = {}
        self.virtual_clock_delta = None
        self.captured_requests = {}
        self.custom_rules = {}
        self.events = []

    def reset(self):
        with self.lock:
            self.hit_counter = 0
            self.secret = "7s5tLvM1"
            self.secrets_map.clear()
            self.virtual_clock_delta = None
            self.captured_requests.clear()
            self.custom_rules.clear()
            self.events.clear()

    def record_event(self, event_type, **kwargs):
        with self.lock:
            payload = {
                "ts": datetime.datetime.now().isoformat(timespec="seconds"),
                "event": event_type,
            }
            payload.update(kwargs)
            self.events.append(payload)

    def drain_events(self):
        with self.lock:
            drained = list(self.events)
            self.events.clear()
            return drained

    def store_captured(self, trx_id, data):
        with self.lock:
            self.captured_requests[trx_id] = data

    def get_captured(self, trx_id=None):
        with self.lock:
            if trx_id:
                return self.captured_requests.get(trx_id)
            return dict(self.captured_requests)

    def set_custom_rule(self, trx_id, status_code, body):
        with self.lock:
            self.custom_rules[trx_id] = {"status_code": status_code, "body": body}

    def resolve_expected_secret(self, appsid, sid):
        with self.lock:
            composite_key = f"{appsid}:{sid}"
            if composite_key in self.secrets_map:
                return self.secrets_map[composite_key]
            if appsid in self.secrets_map:
                return self.secrets_map[appsid]
            return self.secret


state = MockState()


class MockHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        # Suppress noisy stdout
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
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Control API routes
        if path == "/mock-ctrl/health":
            self._send_json(200, {"status": "ok", "port": PORT})
            return

        if path == "/mock-ctrl/captured":
            trx_id = query.get("trx_id", [None])[0]
            data = state.get_captured(trx_id)
            self._send_json(200, {"data": data})
            return

        if path == "/mock-ctrl/events":
            drain = query.get("drain", ["1"])[0] != "0"
            events = state.drain_events() if drain else list(state.events)
            self._send_json(200, {"events": events})
            return

        if path == "/mock-ctrl/stats":
            with state.lock:
                stats = {
                    "hit_counter": state.hit_counter,
                    "captured_count": len(state.captured_requests),
                    "events_count": len(state.events),
                    "default_secret": state.secret,
                    "virtual_clock_delta": state.virtual_clock_delta,
                }
            self._send_json(200, stats)
            return

        # SUT hit via GET
        with state.lock:
            state.hit_counter += 1
        state.record_event("HTTP_GET_RECEIVED", path=self.path, method="GET")
        self._send_error(405, 2405, "Use POST")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parsed.query

        # Control API routes
        if path.startswith("/mock-ctrl/"):
            self._handle_control_post(path)
            return

        # Telkomsel V2 Status Check endpoint
        with state.lock:
            state.hit_counter += 1

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

        # 4. Timestamp check with Request-Anchored Virtual Clock
        try:
            ts_int = int(timestamp)
        except ValueError:
            self._send_error(401, 2401, "Authentication Error: invalid timestamp format")
            return

        with state.lock:
            virtual_delta = state.virtual_clock_delta

        if virtual_delta is not None:
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
        expected_secret = state.resolve_expected_secret(appsid, sid)

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
        state.store_captured(trx_id, captured)
        state.record_event("TELKOMSEL_V2_REQUEST", trx_id=trx_id, appsid=appsid, signature=signature)

        # 8. Scenario Routing
        with state.lock:
            custom_rule = state.custom_rules.get(trx_id)

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

    def _handle_control_post(self, path):
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            body = json.loads(raw_body)
        except Exception:
            body = {}

        if path == "/mock-ctrl/reset":
            state.reset()
            self._send_json(200, {"status": "ok", "message": "Mock state reset"})
            return

        if path == "/mock-ctrl/set-secret":
            secret = body.get("secret", "7s5tLvM1")
            with state.lock:
                state.secret = str(secret)
            self._send_json(200, {"status": "ok", "secret": state.secret})
            return

        if path == "/mock-ctrl/set-secret-map":
            s_map = body.get("secrets_map", {})
            with state.lock:
                state.secrets_map = dict(s_map)
            self._send_json(200, {"status": "ok", "count": len(state.secrets_map)})
            return

        if path == "/mock-ctrl/set-skew":
            skew = body.get("skew_seconds")
            with state.lock:
                state.virtual_clock_delta = int(skew) if skew is not None else None
            self._send_json(200, {"status": "ok", "virtual_clock_delta": state.virtual_clock_delta})
            return

        if path == "/mock-ctrl/set-rule":
            trx_id = body.get("trx_id")
            status_code = body.get("status_code", 200)
            res_body = body.get("body", {})
            if trx_id:
                state.set_custom_rule(trx_id, status_code, res_body)
                self._send_json(200, {"status": "ok", "trx_id": trx_id})
            else:
                self._send_error(400, 400, "Missing trx_id")
            return

        self._send_error(404, 404, "Unknown control path")


def run_server():
    server = ThreadedHTTPServer(("0.0.0.0", PORT), MockHandler)
    print(f"MockTelkomselV2 running on 0.0.0.0:{PORT} (PID {os.getpid()})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
