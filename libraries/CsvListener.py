"""
CsvListener.py - Standard 12-Column CSV Listener for Robot Framework
Automatically updates testcase.csv upon test completion.
Preserves all original fields, formatting, and quotes.
Supports SUT Log Evidence integration via BuiltIn variables or SutLogLibrary registry.
"""
import csv
import datetime
import os
import re

CANDIDATE_PATHS = [
    os.path.abspath("testcase.csv"),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "testcase.csv")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "testcase.csv")),
]
env_csv = os.environ.get("TESTCASE_CSV_PATH")
if env_csv:
    CANDIDATE_PATHS.insert(0, os.path.abspath(env_csv))

CSV_FILES = list(dict.fromkeys([p for p in CANDIDATE_PATHS if os.path.exists(p)]))

class CsvListener:
    ROBOT_LISTENER_API_VERSION = 2

    def end_test(self, name, attrs):
        tc_id = None
        for tag in attrs.get('tags', []):
            if re.match(r'^(TC[-_]?[A-Z0-9]+[-_]?\d+|\bTC\d{3}\b)', tag.strip(), re.IGNORECASE):
                tc_id = tag.strip().upper()
                break

        if not tc_id:
            m = re.search(r'\b(TC[-_]?[A-Z0-9]+[-_]?\d+)\b', name, re.IGNORECASE)
            if m:
                tc_id = m.group(1).upper()

        if not tc_id:
            return

        status = attrs.get('status', 'FAIL')
        message = attrs.get('message', '')
        elapsed_sec = float(attrs.get('elapsedtime', 0)) / 1000.0
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Coba baca dari BuiltIn variable
        actual_output = None
        log_entry = None

        try:
            from robot.libraries.BuiltIn import BuiltIn
            builtin = BuiltIn()
            actual_output = builtin.get_variable_value("${ACTUAL_OUTPUT}")
            log_entry = builtin.get_variable_value("${ACTUAL_LOG}")

            if not actual_output:
                try:
                    collector = builtin.get_library_instance("EvidenceCollector")
                    if collector and hasattr(collector, "format_evidence") and collector.has_evidence():
                        actual_output = collector.format_evidence()
                except Exception:
                    pass
        except Exception:
            pass

        # 2. Coba baca dari SutLogLibrary global registry jika belum ada
        if not log_entry or not actual_output:
            try:
                import SutLogLibrary
                evidence = SutLogLibrary.SutLogLibrary.get_evidence(tc_id)
                if evidence:
                    if not log_entry and evidence.get("log"):
                        log_entry = evidence["log"]
                    if not actual_output and evidence.get("actual_output"):
                        actual_output = evidence["actual_output"]
            except Exception:
                pass

        # 3. Fallback jika tidak ada custom evidence
        if not actual_output:
            if status == 'PASS':
                actual_output = f"Eksekusi {tc_id} berhasil sesuai skenario dan seluruh asersi valid. {message}".strip()
            else:
                actual_output = f"Eksekusi {tc_id} gagal: {message}".strip()

        if not log_entry:
            if status == 'PASS':
                log_entry = f"[{now_str}] PASS in {elapsed_sec:.2f}s. All Given/When/Then assertions satisfied."
            else:
                log_entry = f"[{now_str}] FAIL in {elapsed_sec:.2f}s. Root cause: {message}"

        self._update_csv(tc_id, actual_output, status, log_entry)

    def _update_csv(self, tc_id, actual_output, status, log_entry):
        for file_path in CSV_FILES:
            if not os.path.exists(file_path):
                continue

            rows = []
            with open(file_path, mode='r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0].strip().upper() == tc_id:
                        while len(row) < 12:
                            row.append("")
                        row[8] = actual_output
                        row[9] = status
                        row[10] = log_entry
                    rows.append(row)

            temp_path = file_path + ".tmp"
            with open(temp_path, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                writer.writerows(rows)
            os.replace(temp_path, file_path)
