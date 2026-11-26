# -*- coding: utf-8 -*-
"""
SutLogLibrary.py - SUT Log Evidence Capture & Soft-Assertion for Robot Framework
Complies with "Pre-Implementasi: SUT Log Evidence pada testcase.csv" (28 Oktober 2026).

Arsitektur:
- LogSource (LocalLogSource & SftpLogSource)
- SutProfile (Opsional YAML profile)
- DeltaCollector (Snapshot, Settle, Delta Slicing, Rotated/Truncated Handling)
- EvidenceSelector (Anggaran Karakter, Jatah Minimum, Keyword & Error Prioritization)
- EvidenceFormatter (Kolom Log & Kolom Actual Output)
- SutLogLibrary (Robot Framework Listener v3 & Library Scope GLOBAL)
"""

import abc
import fnmatch
import json
import os
import re
import stat
import time
from typing import Any, Dict, List, Optional, Tuple

try:
    from robot.api import logger
    from robot.api.deco import keyword
    from robot.libraries.BuiltIn import BuiltIn
except ImportError:
    # Standalone / Unit test fallback
    class _MockLogger:
        def info(self, msg, html=False): pass
        def warn(self, msg, html=False): pass
        def error(self, msg, html=False): pass
        def debug(self, msg, html=False): pass
    logger = _MockLogger()
    def keyword(name=None):
        def decorator(func): return func
        return decorator
    BuiltIn = None


# ==============================================================================
# 1. LogSource Abstraction
# ==============================================================================

class LogSource(abc.ABC):
    """Antarmuka sumber log abstrak."""

    @abc.abstractmethod
    def list_files(self) -> List[Tuple[str, int, float]]:
        """Mengembalikan daftar tuple (rel_name, size_bytes, mtime_epoch)."""
        pass

    @abc.abstractmethod
    def read_range(self, rel_name: str, start: int, max_bytes: int) -> Tuple[bytes, bool]:
        """Membaca data biner dari start offset hingga max_bytes.
        Mengembalikan (data_bytes, is_truncated).
        """
        pass

    def close(self):
        """Menutup koneksi/resource jika ada."""
        pass


class LocalLogSource(LogSource):
    """Implementasi sumber log lokal pada filesystem."""

    def __init__(self, log_dir: str, exclude_patterns: Optional[List[str]] = None, max_files: int = 50):
        self.log_dir = os.path.abspath(log_dir) if log_dir else ""
        self.exclude_patterns = exclude_patterns or []
        self.max_files = max_files

    def list_files(self) -> List[Tuple[str, int, float]]:
        if not self.log_dir or not os.path.isdir(self.log_dir):
            raise FileNotFoundError(f"Folder log SUT tidak ditemukan: {self.log_dir}")

        results = []
        for root, dirs, files in os.walk(self.log_dir):
            for fname in files:
                full_path = os.path.join(root, fname)
                rel_name = os.path.relpath(full_path, self.log_dir)

                # Cek pola exclude
                if any(fnmatch.fnmatch(rel_name, pat) or fnmatch.fnmatch(fname, pat) for pat in self.exclude_patterns):
                    continue

                try:
                    st = os.stat(full_path)
                    if stat.S_ISREG(st.st_mode):
                        results.append((rel_name, st.st_size, st.st_mtime))
                except (OSError, IOError):
                    continue

                if len(results) >= self.max_files:
                    break
            if len(results) >= self.max_files:
                break

        results.sort(key=lambda x: x[0])
        return results

    def read_range(self, rel_name: str, start: int, max_bytes: int) -> Tuple[bytes, bool]:
        full_path = os.path.join(self.log_dir, rel_name)
        if not os.path.isfile(full_path):
            return b"", False

        with open(full_path, "rb") as f:
            f.seek(start)
            data = f.read(max_bytes + 1)
            is_truncated = len(data) > max_bytes
            return data[:max_bytes], is_truncated


class SftpLogSource(LogSource):
    """Implementasi sumber log remote via SFTP (lazy import paramiko)."""

    def __init__(self, host: str, port: int = 22, username: Optional[str] = None,
                 password: Optional[str] = None, key_filename: Optional[str] = None,
                 log_dir: str = "/app/logs", exclude_patterns: Optional[List[str]] = None,
                 max_files: int = 50):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.log_dir = log_dir
        self.exclude_patterns = exclude_patterns or []
        self.max_files = max_files
        self._client = None
        self._sftp = None

    def _connect(self):
        if self._sftp is not None:
            return
        try:
            import paramiko
        except ImportError:
            raise ImportError("Modul paramiko belum terinstall di runtime untuk koneksi SFTP.")

        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
            hostname=self.host, port=self.port,
            username=self.username, password=self.password,
            key_filename=self.key_filename, timeout=10
        )
        self._sftp = self._client.open_sftp()

    def list_files(self) -> List[Tuple[str, int, float]]:
        self._connect()
        results = []
        try:
            entries = self._sftp.listdir_attr(self.log_dir)
            for attr in entries:
                fname = attr.filename
                if any(fnmatch.fnmatch(fname, pat) for pat in self.exclude_patterns):
                    continue
                if stat.S_ISREG(attr.st_mode):
                    results.append((fname, attr.st_size, attr.st_mtime))
                if len(results) >= self.max_files:
                    break
        except Exception as e:
            raise IOError(f"Gagal membaca direktori SFTP {self.log_dir}: {e}")

        results.sort(key=lambda x: x[0])
        return results

    def read_range(self, rel_name: str, start: int, max_bytes: int) -> Tuple[bytes, bool]:
        self._connect()
        remote_path = f"{self.log_dir.rstrip('/')}/{rel_name}"
        try:
            with self._sftp.open(remote_path, "rb") as f:
                f.seek(start)
                data = f.read(max_bytes + 1)
                is_truncated = len(data) > max_bytes
                return data[:max_bytes], is_truncated
        except Exception:
            return b"", False

    def close(self):
        if self._sftp:
            try: self._sftp.close()
            except Exception: pass
            self._sftp = None
        if self._client:
            try: self._client.close()
            except Exception: pass
            self._client = None


# ==============================================================================
# 2. SutProfile Loader (Opsional YAML)
# ==============================================================================

class SutProfile:
    """Parser profil konfigurasi opsional SUT."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self.data = data or {}
        self.sut = self.data.get("sut", "")
        self.version = self.data.get("version_validated", "")
        self.access = self.data.get("access", "local")
        self.log_dir = self.data.get("log_dir", "")
        self.exclude_files = self.data.get("exclude_files", [])
        self.files_cfg = {f["name"]: f for f in self.data.get("files", []) if isinstance(f, dict) and "name" in f}
        self.known_noise = self.data.get("known_noise", [])
        self.settle_seconds = float(self.data.get("settle_seconds", 2.0))
        self.max_delta_bytes = int(self.data.get("max_delta_bytes", 1048576))
        self.keywords_per_tc = self.data.get("keywords_per_tc", {})

    @classmethod
    def load(cls, profile_path: str):
        if not profile_path or not os.path.exists(profile_path):
            return cls({})
        try:
            import yaml
            with open(profile_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                return cls(content if isinstance(content, dict) else {})
        except Exception:
            return cls({})

    def is_error_file(self, filename: str) -> bool:
        if filename in self.files_cfg:
            return bool(self.files_cfg[filename].get("error_like", False))
        return False

    def get_timestamp_regex(self, filename: str) -> Optional[str]:
        if filename in self.files_cfg:
            return self.files_cfg[filename].get("timestamp_regex")
        return None

    def get_keywords_for_tc(self, tc_id: str) -> List[str]:
        tc_cfg = self.keywords_per_tc.get(tc_id, {})
        return tc_cfg.get("keywords_from", [])


# ==============================================================================
# 3. DeltaCollector & Settle
# ==============================================================================

class DeltaCollector:
    """Mengumpulkan delta log terisolasi antar-snapshot dengan mekanisme settle."""

    def __init__(self, log_source: LogSource, profile: Optional[SutProfile] = None,
                 settle_seconds: float = 2.0, settle_max: float = 10.0,
                 max_delta_bytes: int = 1048576, errfile_pattern: str = "*error*"):
        self.log_source = log_source
        self.profile = profile or SutProfile()
        self.settle_seconds = settle_seconds
        self.settle_max = settle_max
        self.max_delta_bytes = max_delta_bytes
        self.errfile_pattern = errfile_pattern

    def take_snapshot(self) -> Dict[str, Dict[str, Any]]:
        files = self.log_source.list_files()
        return {name: {"size": size, "mtime": mtime} for name, size, mtime in files}

    def wait_settle(self, initial_snapshot: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], float]:
        start_time = time.time()
        last_state = None
        stable_since = None

        while True:
            elapsed = time.time() - start_time
            if elapsed >= self.settle_max:
                break

            try:
                current_snapshot = self.take_snapshot()
            except Exception:
                break

            curr_sizes = {name: d["size"] for name, d in current_snapshot.items()}

            if last_state == curr_sizes:
                if stable_since is None:
                    stable_since = time.time()
                elif (time.time() - stable_since) >= self.settle_seconds:
                    return current_snapshot, elapsed
            else:
                last_state = curr_sizes
                stable_since = None

            poll_interval = min(0.1, self.settle_seconds / 2.0 if self.settle_seconds > 0 else 0.05)
            time.sleep(poll_interval)

        return self.take_snapshot(), (time.time() - start_time)

    def collect(self, initial_snapshot: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        final_snapshot, settle_dur = self.wait_settle(initial_snapshot)
        deltas = {}

        for filename, curr_info in final_snapshot.items():
            init_info = initial_snapshot.get(filename)
            curr_size = curr_info["size"]

            if init_info is None:
                start_offset = 0
                flags = ["NEW_FILE"]
            elif curr_size > init_info["size"]:
                start_offset = init_info["size"]
                flags = []
            elif curr_size < init_info["size"]:
                start_offset = 0
                flags = ["ROTATED"]
            else:
                # Tidak ada penambahan
                continue

            data_bytes, is_trunc = self.log_source.read_range(filename, start_offset, self.max_delta_bytes)
            if is_trunc:
                flags.append("TRUNCATED")

            # Decode aman UTF-8
            text = data_bytes.decode("utf-8", errors="replace")
            # Sanitasi: tab diganti spasi, buang karakter kontrol
            text = text.replace("\t", "    ")
            text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

            ts_regex = self.profile.get_timestamp_regex(filename)
            lines = self._group_lines(text, ts_regex)

            is_err = self.profile.is_error_file(filename) or fnmatch.fnmatch(filename.lower(), self.errfile_pattern.lower())

            deltas[filename] = {
                "initial_offset": start_offset,
                "final_size": curr_size,
                "delta_bytes": len(data_bytes),
                "raw_bytes": data_bytes,
                "lines": lines,
                "flags": flags,
                "is_error_file": is_err,
                "settle_dur": settle_dur
            }

        return deltas

    def _group_lines(self, text: str, ts_regex: Optional[str]) -> List[str]:
        raw_lines = text.splitlines()
        if not raw_lines:
            return []
        if not ts_regex:
            return [line.strip() for line in raw_lines if line.strip()]

        grouped = []
        pattern = re.compile(ts_regex)
        for line in raw_lines:
            s_line = line.strip()
            if not s_line:
                continue
            if pattern.search(s_line) or not grouped:
                grouped.append(s_line)
            else:
                grouped[-1] += " " + s_line
        return grouped


# ==============================================================================
# 4. EvidenceSelector (Anggaran Sel & Prioritas Baris)
# ==============================================================================

class EvidenceSelector:
    """Memilih baris log berdasarkan prioritas dan anggaran karakter sel spreadsheet (maksimal 30.000 karakter, aman untuk Excel & Google Sheets)."""

    def __init__(self, max_chars: int = 30000, max_line_chars: int = 3000,
                 max_lines_per_file: int = 100, max_lines_total: int = 200,
                 min_lines_per_file: int = 2):
        self.max_chars = max_chars
        self.max_line_chars = max_line_chars
        self.max_lines_per_file = max_lines_per_file
        self.max_lines_total = max_lines_total
        self.min_lines_per_file = min_lines_per_file

    def select(self, deltas: Dict[str, Any], keywords: Optional[List[str]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        kw_map = {k.strip(): k.strip().lower() for k in (keywords or []) if k.strip()}
        kw_hits_count = 0
        file_kw_results = {}

        # 1. Analisis awal & scoring baris per file
        file_analysis = {}
        for filename, fdelta in deltas.items():
            lines = fdelta["lines"]
            is_err = fdelta["is_error_file"]
            hit_kws_in_file = set()

            scored = []
            for idx, line in enumerate(lines):
                line_lower = line.lower()
                matched_kws = [orig for orig, low in kw_map.items() if low in line_lower]
                if matched_kws:
                    hit_kws_in_file.update(matched_kws)
                    prio = 1  # Keyword match
                elif is_err:
                    prio = 2  # Error file
                elif idx == 0 or idx == len(lines) - 1:
                    prio = 3  # Head/Tail
                else:
                    prio = 4  # Normal

                display_line = line
                if len(display_line) > self.max_line_chars:
                    display_line = display_line[:self.max_line_chars - 3] + "..."

                scored.append({
                    "priority": prio,
                    "index": idx,
                    "line": display_line
                })

            if kw_map:
                file_kw_results[filename] = {
                    "hits": sorted(list(hit_kws_in_file)),
                    "misses": sorted(list(set(kw_map.keys()) - hit_kws_in_file))
                }
                kw_hits_count += len(hit_kws_in_file)

            file_analysis[filename] = {
                "total_lines": len(lines),
                "is_error_file": is_err,
                "flags": fdelta["flags"],
                "scored": scored,
                "selected": []
            }

        # 2. Seleksi per file (Full fidelity jika total muat dalam anggaran, prioritas jika melebihi)
        overhead = 250 + (len(deltas) * 60)
        total_chars = sum(sum(len(c["line"]) + 1 for c in data["scored"]) for data in file_analysis.values())
        all_lines_count = sum(len(data["scored"]) for data in file_analysis.values())

        if (total_chars + overhead <= self.max_chars) and (all_lines_count <= self.max_lines_total):
            # SEMUA BARIS MUAT UTUH: pertahankan 100% tanpa ada baris terpotong
            for filename, data in file_analysis.items():
                data["selected"] = [c["line"] for c in data["scored"]]
        else:
            total_selected = 0
            for filename, data in file_analysis.items():
                scored = data["scored"]
                if not scored:
                    continue

                by_prio = sorted(scored, key=lambda x: (x["priority"], x["index"]))
                take_count = min(self.max_lines_per_file, len(by_prio))
                chosen = sorted(by_prio[:take_count], key=lambda x: x["index"])
                data["selected"] = [c["line"] for c in chosen]
                total_selected += len(data["selected"])

            # Pangkas jika total_selected melebihi max_lines_total
            if total_selected > self.max_lines_total:
                for filename, data in file_analysis.items():
                    if len(data["selected"]) > self.min_lines_per_file:
                        data["selected"] = data["selected"][:self.min_lines_per_file]
                    total_selected = sum(len(d["selected"]) for d in file_analysis.values())
                    if total_selected <= self.max_lines_total:
                        break

        kw_stats = {
            "total": len(kw_map),
            "hits": kw_hits_count,
            "per_file": file_kw_results
        }

        return file_analysis, kw_stats


# ==============================================================================
# 5. EvidenceFormatter (Keluaran Log & Actual Output)
# ==============================================================================

class EvidenceFormatter:
    """Menyusun string keluaran untuk kolom Log dan kolom Actual Output."""

    def format_log_column(self, base_prefix: str, selected_data: Dict[str, Any],
                          kw_stats: Dict[str, Any], artifact_rel_path: str,
                          max_chars: int = 30000) -> str:
        if not selected_data:
            return f"{base_prefix} | [SUT LOG] files=0 (tidak ada log baru)"

        total_files = len(selected_data)
        total_lines = sum(d["total_lines"] for d in selected_data.values())
        err_files = sum(1 for d in selected_data.values() if d["is_error_file"])
        kw_str = f"kw={kw_stats.get('hits', 0)}/{kw_stats.get('total', 0)}" if kw_stats.get("total", 0) > 0 else "kw=0"

        header = f"{base_prefix} | [SUT LOG] files={total_files} lines={total_lines} {kw_str} errfile={err_files}"
        blocks = [header]

        for filename, d in selected_data.items():
            tot = d["total_lines"]
            sel = len(d["selected"])
            omitted = tot - sel
            flag_str = f" [{', '.join(d['flags'])}]" if d["flags"] else ""

            if omitted > 0:
                head = f"--- {filename} ({tot} baris, tampil {sel}, +{omitted} dipotong){flag_str} ---"
            else:
                head = f"--- {filename} ({tot} baris){flag_str} ---"

            blocks.append(head)
            for line in d["selected"]:
                blocks.append(line)

        if artifact_rel_path:
            blocks.append(f"artifact={artifact_rel_path}")

        full_text = "\n".join(blocks)
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars - 3] + "..."
        return full_text

    def format_actual_output_column(self, selected_data: Dict[str, Any], kw_stats: Dict[str, Any]) -> str:
        if not selected_data:
            return "SUT Log: files=0 (tidak ada log baru)"

        files_str = ", ".join(selected_data.keys())
        parts = [f"SUT Log: {len(selected_data)} file bertambah ({files_str})"]

        per_file = kw_stats.get("per_file", {})
        kw_details = []
        for fname, res in per_file.items():
            hits = res.get("hits", [])
            misses = res.get("misses", [])
            tokens = []
            if hits:
                tokens.append(f"HIT {','.join(hits)}")
            if misses:
                tokens.append(f"MISS {','.join(misses)}")
            if tokens:
                kw_details.append(f"{fname}: {' '.join(tokens)}")

        if kw_details:
            parts.append("Keyword: " + "; ".join(kw_details))

        return " | ".join(parts)


# ==============================================================================
# 6. SutLogLibrary (Robot Framework Listener v3 & Library Scope GLOBAL)
# ==============================================================================

class SutLogLibrary:
    """Library Robot Framework & Listener API v3 untuk bukti log SUT."""

    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    _REGISTRY = {}  # tc_id -> evidence dict

    def __init__(self, log_dir: Optional[str] = None, access: str = "local",
                 profile: Optional[str] = None, **kwargs):
        self.ROBOT_LIBRARY_LISTENER = self
        self.log_dir = log_dir or os.environ.get("SUT_LOG_DIR", "")
        self.access = access or os.environ.get("SUT_LOG_ACCESS", "local")
        self.profile_path = profile or os.environ.get("SUT_LOG_PROFILE", "")
        self.kwargs = kwargs

        # Profile loader
        self.profile = SutProfile.load(self.profile_path)
        if not self.log_dir and self.profile.log_dir:
            self.log_dir = self.profile.log_dir

        self.max_chars = int(kwargs.get("max_chars", os.environ.get("SUT_LOG_MAX_CHARS", 30000)))
        self.max_line_chars = int(kwargs.get("max_line_chars", os.environ.get("SUT_LOG_MAX_LINE_CHARS", 3000)))
        self.max_lines_per_file = int(kwargs.get("max_lines_per_file", os.environ.get("SUT_LOG_MAX_LINES_PER_FILE", 100)))
        self.max_lines_total = int(kwargs.get("max_lines_total", os.environ.get("SUT_LOG_MAX_LINES_TOTAL", 200)))
        self.settle_seconds = float(kwargs.get("settle_seconds", os.environ.get("SUT_LOG_SETTLE_SECONDS", self.profile.settle_seconds or 2.0)))
        self.settle_max = float(kwargs.get("settle_max", os.environ.get("SUT_LOG_SETTLE_MAX", 10.0)))
        self.max_delta_bytes = int(kwargs.get("max_delta_bytes", os.environ.get("SUT_LOG_MAX_DELTA_BYTES", self.profile.max_delta_bytes or 1048576)))
        self.max_files = int(kwargs.get("max_files", os.environ.get("SUT_LOG_MAX_FILES", 50)))
        self.errfile_pattern = kwargs.get("errfile_pattern", os.environ.get("SUT_LOG_ERRFILE_PATTERN", "*error*"))
        self.artifact_dir = kwargs.get("artifact_dir", os.environ.get("SUT_LOG_ARTIFACT_DIR", "results/logs"))

        self.log_source: Optional[LogSource] = None
        self._init_error = None
        self._init_log_source()

        self.collector = DeltaCollector(
            self.log_source, self.profile,
            settle_seconds=self.settle_seconds,
            settle_max=self.settle_max,
            max_delta_bytes=self.max_delta_bytes,
            errfile_pattern=self.errfile_pattern
        ) if self.log_source else None

        self.selector = EvidenceSelector(
            max_chars=self.max_chars,
            max_line_chars=self.max_line_chars,
            max_lines_per_file=self.max_lines_per_file,
            max_lines_total=self.max_lines_total
        )
        self.formatter = EvidenceFormatter()

        self._current_tc_id: Optional[str] = None
        self._current_snapshot: Optional[Dict[str, Dict[str, Any]]] = None
        self._current_keywords: List[str] = []
        self._run_id = time.strftime("%Y%m%d_%H%M%S")

    def _init_log_source(self):
        try:
            if self.access == "sftp":
                host = self.kwargs.get("host", os.environ.get("SUT_LOG_SFTP_HOST", "localhost"))
                port = int(self.kwargs.get("port", os.environ.get("SUT_LOG_SFTP_PORT", 22)))
                username = self.kwargs.get("username", os.environ.get("SUT_LOG_SFTP_USER"))
                password = self.kwargs.get("password", os.environ.get("SUT_LOG_SFTP_PASS"))
                key_file = self.kwargs.get("key_filename", os.environ.get("SUT_LOG_SFTP_KEY"))
                self.log_source = SftpLogSource(
                    host=host, port=port, username=username, password=password,
                    key_filename=key_file, log_dir=self.log_dir,
                    exclude_patterns=self.profile.exclude_files, max_files=self.max_files
                )
            else:
                self.log_source = LocalLogSource(
                    self.log_dir, exclude_patterns=self.profile.exclude_files, max_files=self.max_files
                )
        except Exception as e:
            self._init_error = str(e)
            self.log_source = None

    # --------------------------------------------------------------------------
    # Listener API v3 Hooks
    # --------------------------------------------------------------------------

    def start_test(self, data, result):
        """Dipanggil otomatis sebelum setiap testcase mulai."""
        tc_id = self._extract_tc_id(result.name, getattr(result, "tags", []))
        self._current_tc_id = tc_id
        self._current_keywords = []

        if self.profile and tc_id:
            profile_kws = self.profile.get_keywords_for_tc(tc_id)
            self._current_keywords.extend(profile_kws)

        if self.collector:
            try:
                self._current_snapshot = self.collector.take_snapshot()
            except Exception as e:
                self._current_snapshot = {}
                logger.warn(f"[SutLogLibrary] Gagal mengambil snapshot awal untuk {tc_id}: {e}")

    def end_keyword(self, data, result):
        """Dipanggil setiap keyword selesai. Deteksi otomatis ${CURRENT_MESSAGE_ID} jika ada."""
        if not self._current_tc_id:
            return
        if BuiltIn:
            try:
                msg_id = BuiltIn().get_variable_value("${CURRENT_MESSAGE_ID}")
                if msg_id and str(msg_id).strip() and str(msg_id).strip() not in self._current_keywords:
                    self._current_keywords.append(str(msg_id).strip())
            except Exception:
                pass

    def end_test(self, data, result):
        """Dipanggil otomatis setelah setiap testcase selesai."""
        tc_id = self._current_tc_id or self._extract_tc_id(result.name, getattr(result, "tags", []))
        elapsed_sec = result.elapsed_time.total_seconds() if hasattr(result, "elapsed_time") else 0.0
        status = result.status

        if BuiltIn:
            try:
                msg_id = BuiltIn().get_variable_value("${CURRENT_MESSAGE_ID}")
                if msg_id and str(msg_id).strip() and str(msg_id).strip() not in self._current_keywords:
                    self._current_keywords.append(str(msg_id).strip())
            except Exception:
                pass

        base_prefix = f"[{status}] Elapsed: {elapsed_sec:.2f}s"
        if status == "FAIL" and getattr(result, "message", None):
            base_prefix += f" | Error: {result.message}"

        if self._init_error:
            formatted_log = f"{base_prefix} | [SUT LOG] ERROR: {self._init_error}"
            formatted_actual = f"SUT Log ERROR: {self._init_error}"
            self._store_result(tc_id, formatted_log, formatted_actual)
            return

        if not self.collector or self._current_snapshot is None:
            formatted_log = f"{base_prefix} | [SUT LOG] ERROR: Snapshot collector tidak aktif"
            formatted_actual = "SUT Log ERROR: Snapshot collector tidak aktif"
            self._store_result(tc_id, formatted_log, formatted_actual)
            return

        try:
            # 1. Kumpulkan delta
            deltas = self.collector.collect(self._current_snapshot)

            # 2. Tulis file artefak per TC
            artifact_rel_path = self._write_artifacts(tc_id, deltas)

            # 3. Seleksi baris sesuai anggaran
            selected_data, kw_stats = self.selector.select(deltas, self._current_keywords)

            # 4. Format keluaran
            formatted_log = self.formatter.format_log_column(
                base_prefix, selected_data, kw_stats, artifact_rel_path, max_chars=self.max_chars
            )
            formatted_actual = self.formatter.format_actual_output_column(selected_data, kw_stats)

            # 5. Log chunked ke log.html
            self._log_to_html(tc_id, deltas, selected_data)

            # 6. Simpan hasil
            self._store_result(tc_id, formatted_log, formatted_actual)

        except Exception as e:
            err_msg = f"{base_prefix} | [SUT LOG] ERROR: Exception saat ekstraksi log ({type(e).__name__}: {e})"
            logger.warn(err_msg)
            self._store_result(tc_id, err_msg, f"SUT Log ERROR: {e}")

    def close(self):
        """Tutup koneksi jika ada."""
        if self.log_source:
            self.log_source.close()

    # --------------------------------------------------------------------------
    # Robot Keywords Eksplisit
    # --------------------------------------------------------------------------

    @keyword("Daftarkan Keyword Log SUT")
    def daftarkan_keyword_log_sut(self, *keywords):
        """Mendaftarkan string keyword untuk diprioritaskan dan di-soft-check pada log SUT saat TC berjalan."""
        for kw in keywords:
            if kw and str(kw).strip():
                self._current_keywords.append(str(kw).strip())
        logger.info(f"[SutLogLibrary] Keyword log SUT terdaftar: {self._current_keywords}")

    @keyword("Set Directory Log SUT")
    def set_directory_log_sut(self, directory_path):
        """Mengubah target folder log SUT secara dinamis."""
        self.log_dir = directory_path
        self._init_error = None
        self._init_log_source()
        if self.log_source:
            self.collector = DeltaCollector(
                self.log_source, self.profile,
                settle_seconds=self.settle_seconds,
                settle_max=self.settle_max,
                max_delta_bytes=self.max_delta_bytes,
                errfile_pattern=self.errfile_pattern
            )
        logger.info(f"[SutLogLibrary] Target direktori log SUT diset ke: {directory_path}")

    @keyword("Ambil Bukti Log SUT Untuk Testcase")
    def ambil_bukti_log_sut_untuk_testcase(self, tc_id):
        """Mengambil dict bukti log untuk TC tertentu dari registry global."""
        return self._REGISTRY.get(tc_id, {})

    # --------------------------------------------------------------------------
    # Helper Internal
    # --------------------------------------------------------------------------

    def _extract_tc_id(self, test_name: str, tags: List[str]) -> str:
        match = re.search(r"(TC-[A-Z0-9]+-\d+|TC-\d+)", test_name, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        for tag in tags:
            tag_match = re.match(r"^(TC-[A-Z0-9]+-\d+|TC-\d+)$", tag, re.IGNORECASE)
            if tag_match:
                return tag_match.group(1).upper()
        return test_name.split()[0] if test_name else "TC-UNKNOWN"

    def _write_artifacts(self, tc_id: str, deltas: Dict[str, Any]) -> str:
        if not deltas:
            return ""

        target_dir = os.path.join(self.artifact_dir, self._run_id, tc_id)
        os.makedirs(target_dir, exist_ok=True)

        meta = {}
        for fname, d in deltas.items():
            safe_fname = fname.replace("/", "_")
            out_file = os.path.join(target_dir, safe_fname)
            with open(out_file, "wb") as f:
                f.write(d["raw_bytes"])

            meta[fname] = {
                "initial_offset": d["initial_offset"],
                "final_size": d["final_size"],
                "delta_bytes": d["delta_bytes"],
                "flags": d["flags"],
                "is_error_file": d["is_error_file"],
                "settle_dur": d["settle_dur"]
            }

        meta_file = os.path.join(target_dir, "_meta.json")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return os.path.relpath(target_dir)

    def _log_to_html(self, tc_id: str, deltas: Dict[str, Any], selected: Dict[str, Any]):
        if not deltas:
            return
        logger.info(f"--- [SUT LOG EVIDENCE: {tc_id}] {len(deltas)} file bertambah ---")
        for fname, d in selected.items():
            tot = d["total_lines"]
            sel = len(d["selected"])
            logger.info(f"[SUT Log: {fname}] (Total {tot} baris delta, ditampilkan {sel} baris):")
            for line in d["selected"]:
                logger.info(f"  | {line}")

    def _store_result(self, tc_id: str, formatted_log: str, formatted_actual: str):
        self._REGISTRY[tc_id] = {
            "log": formatted_log,
            "actual_output": formatted_actual
        }

        # Set variable BuiltIn Robot Framework jika tersedia
        if BuiltIn:
            try:
                b = BuiltIn()
                b.set_variable_value("${SUT_ACTUAL_LOG}", formatted_log)
                b.set_variable_value("${SUT_ACTUAL_OUTPUT}", formatted_actual)

                try:
                    collector = b.get_library_instance("EvidenceCollector")
                    if collector:
                        collector.record_evidence("SUT Log", formatted_actual)
                except Exception:
                    pass
            except Exception:
                pass

    @classmethod
    def get_evidence(cls, tc_id: str) -> Dict[str, str]:
        """Helper global untuk dibaca listener eksternal seperti CsvResultListener."""
        return cls._REGISTRY.get(tc_id, {})
