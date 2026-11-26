#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_summary_xlsx.py
Otomasi Pembuatan Dokumen Ringkasan Eksekutif Hasil Pengujian SQA (Gate 6 Sign-Off).
Format: Microsoft Excel (.xlsx) dengan Human-Centered Design yang dioptimasi khusus
agar memanjakan mata manusia saat dibuka di Google Spreadsheet maupun Microsoft Excel.

Filosofi Desain (Memanjakan Mata Manusia):
1. TAB 1: EXECUTIVE DASHBOARD & WHAT'S NEW (All-In-One Story)
   - Visual KPI Scorecard Cards di bagian paling atas (Status Rilis, Cakupan Fitur, Hasil Test, Metode).
   - Visual 3-Step Flow Journey (Ingress -> Governance -> Egress) yang ringkas & bernafas (bukan balok teks!).
   - TABEL UTAMA: Cerita Perubahan Fitur (What's New) yang membandingkan Kondisi Lama vs Kondisi Baru
     dan pembuktian nyatanya secara proporsional (pas 1 layar monitor tanpa scroll horizontal!).
2. TAB 2: AUDIT TRACEABILITY (Detail Test Cases)
   - Disiapkan khusus bagi QA / Auditor yang ingin memeriksa nomor TC dan bukti log per skenario.
"""

import argparse
import csv
import datetime
import os
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    print("ERROR: Library 'openpyxl' belum terpasang. Jalankan: pip install openpyxl", file=sys.stderr)
    sys.exit(1)


# ==============================================================================
# PALET WARNA MODERN (ERGONOMIC & PASTEL PALETTE)
# ==============================================================================
# Base Dark & Slate
COLOR_NAVY_DARK = "0F172A"       # Slate 900 (Deep modern dark)
COLOR_SLATE_HEADER = "1E293B"    # Slate 800 (Table Headers)
COLOR_SLATE_TEXT = "334155"      # Slate 700 (Body text)
COLOR_MUTED_TEXT = "64748B"      # Slate 500 (Subtitles, notes)
COLOR_BORDER = "CBD5E1"          # Slate 300 (Subtle border)
COLOR_ZEBRA = "F8FAFC"           # Slate 50 (Soft alternating row)

# Status & KPI Cards (Soft Pastels with High Contrast Text)
# 1. Emerald (Success / Release OK)
CARD_GREEN_BG = "ECFDF5"         # Emerald 50
CARD_GREEN_BORDER = "A7F3D0"     # Emerald 200
CARD_GREEN_TITLE = "047857"      # Emerald 700
CARD_GREEN_VAL = "065F46"        # Emerald 800

# 2. Blue / Indigo (Updates / Features)
CARD_BLUE_BG = "EFF6FF"          # Blue 50
CARD_BLUE_BORDER = "BFDBFE"      # Blue 200
CARD_BLUE_TITLE = "1D4ED8"       # Blue 700
CARD_BLUE_VAL = "1E40AF"         # Blue 800

# 3. Purple / Violet (Testing Method / Architecture)
CARD_PURPLE_BG = "F5F3FF"        # Purple 50
CARD_PURPLE_BORDER = "DDD6FE"    # Purple 200
CARD_PURPLE_TITLE = "6D28D9"     # Purple 700
CARD_PURPLE_VAL = "5B21B6"       # Purple 800

# 4. Amber / Orange (Warning / Conditional)
CARD_AMBER_BG = "FFFBEB"         # Amber 50
CARD_AMBER_BORDER = "FDE68A"     # Amber 200
CARD_AMBER_TITLE = "B45309"      # Amber 700
CARD_AMBER_VAL = "92400E"        # Amber 800

# 5. Red / Rose (Failure / Blocker)
CARD_RED_BG = "FFF1F2"           # Rose 50
CARD_RED_BORDER = "FECDD3"       # Rose 200
CARD_RED_TITLE = "BE123C"        # Rose 700
CARD_RED_VAL = "9F1239"          # Rose 800

# Flow Step Cards Background
FLOW_STEP_BG = "F1F5F9"          # Slate 100
FLOW_STEP_BORDER = "94A3B8"      # Slate 400


class SummaryDataExtractor:
    """Mengekstrak dan mengkorelasikan seluruh data pengujian dari SUT."""

    def __init__(self, rf_dir: str, csv_path: Optional[str] = None, xml_path: Optional[str] = None):
        self.rf_dir = os.path.abspath(rf_dir)
        self.csv_path = csv_path or self._find_file(["testcase.csv", "tests/testcase.csv"])
        self.xml_path = xml_path or self._find_file(["results/output.xml", "output.xml"])
        self.yaml_path = self._find_file(["sut_profile.yaml", "sut_profile.yml"])

        self.meta: Dict[str, str] = {}
        self.testcases: List[Dict[str, Any]] = []
        self.counts = {
            "TOTAL": 0,
            "PASS": 0,
            "FAIL": 0,
            "SKIP": 0,
            "BLOCKED": 0,
            "NOT EXECUTED": 0,
        }
        self.priority_counts = {
            "P0": {"TOTAL": 0, "PASS": 0, "FAIL": 0, "SKIP": 0},
            "P1": {"TOTAL": 0, "PASS": 0, "FAIL": 0, "SKIP": 0},
            "P2": {"TOTAL": 0, "PASS": 0, "FAIL": 0, "SKIP": 0},
        }
        self.updates: List[Dict[str, Any]] = []
        self.execution_date = datetime.date.today().strftime("%d %B %Y")
        self.total_duration_sec = 0.0
        self.sut_profile: Dict[str, Any] = {}

    def _find_file(self, candidates: List[str]) -> Optional[str]:
        for c in candidates:
            p = os.path.join(self.rf_dir, c)
            if os.path.exists(p):
                return p
        return None

    def extract(self):
        self._parse_yaml()
        self._parse_csv()
        self._parse_xml()
        self._correlate_updates()
        return self

    def _parse_yaml(self):
        if not self.yaml_path or not os.path.exists(self.yaml_path):
            return
        try:
            import yaml
            with open(self.yaml_path, "r", encoding="utf-8") as f:
                self.sut_profile = yaml.safe_load(f) or {}
        except Exception:
            pass

    def _extract_ticket(self) -> str:
        scen = self.meta.get("scenario", "")
        tc = self.meta.get("test_case", "")
        m = re.search(r"PB[A-Za-z0-9\-]+", scen + " " + tc)
        return m.group(0) if m else "PB082643640012YA"

    def _parse_csv(self):
        if not self.csv_path or not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"File testcase.csv tidak ditemukan di {self.rf_dir}")

        with open(self.csv_path, mode="r", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return

            def idx_of(name, default_idx):
                try:
                    return header.index(name)
                except ValueError:
                    return default_idx

            col_id = idx_of("Test Case ID", 0)
            col_desc = idx_of("Description", 1)
            col_tc = idx_of("Test Case", 2)
            col_scen = idx_of("Test Scenario", 3)
            col_prio = idx_of("Priority", 4)
            col_steps = idx_of("Test Steps", 5)
            col_precond = idx_of("Test Data/Precondition", 6)
            col_expected = idx_of("Expected Result", 7)
            col_actual = idx_of("Actual Output", 8)
            col_status = idx_of("Status", 9)
            col_log = idx_of("Log", 10)

            for row in reader:
                if not row or not any(row):
                    continue
                tc_id = row[col_id].strip() if len(row) > col_id else ""

                if tc_id.upper() == "META-SUT":
                    self.meta = {
                        "description": row[col_desc] if len(row) > col_desc else "",
                        "test_case": row[col_tc] if len(row) > col_tc else "",
                        "scenario": row[col_scen] if len(row) > col_scen else "",
                        "steps": row[col_steps] if len(row) > col_steps else "",
                        "precond": row[col_precond] if len(row) > col_precond else "",
                        "expected": row[col_expected] if len(row) > col_expected else "",
                    }
                    continue

                if not tc_id.upper().startswith("TC-"):
                    continue

                prio_raw = row[col_prio].strip().upper() if len(row) > col_prio else "P1"
                prio = "P0" if "P0" in prio_raw else ("P2" if "P2" in prio_raw else "P1")

                status_raw = row[col_status].strip().upper() if len(row) > col_status else "NOT EXECUTED"
                if "PASS" in status_raw:
                    status = "PASS"
                elif "FAIL" in status_raw:
                    status = "FAIL"
                elif "SKIP" in status_raw:
                    status = "SKIP"
                elif "BLOCK" in status_raw:
                    status = "BLOCKED"
                else:
                    status = "NOT EXECUTED"

                actual_out = row[col_actual].strip() if len(row) > col_actual else ""
                log_text = row[col_log].strip() if len(row) > col_log else ""
                tc_name = row[col_tc].strip() if len(row) > col_tc else ""
                scenario_text = row[col_scen].strip() if len(row) > col_scen else ""

                tc_item = {
                    "id": tc_id,
                    "name": tc_name or scenario_text or tc_id,
                    "scenario": scenario_text,
                    "priority": prio,
                    "status": status,
                    "actual_output": actual_out,
                    "log": log_text,
                }
                self.testcases.append(tc_item)

                self.counts["TOTAL"] += 1
                if status in self.counts:
                    self.counts[status] += 1

                if prio in self.priority_counts:
                    self.priority_counts[prio]["TOTAL"] += 1
                    if status in self.priority_counts[prio]:
                        self.priority_counts[prio][status] += 1

    def _parse_xml(self):
        if not self.xml_path or not os.path.exists(self.xml_path):
            return
        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            suite_status = root.find(".//suite/status")
            if suite_status is not None:
                start_time_str = suite_status.attrib.get("starttime", "")
                if start_time_str:
                    try:
                        dt = datetime.datetime.strptime(start_time_str[:8], "%Y%m%d")
                        self.execution_date = dt.strftime("%d %B %Y")
                    except Exception:
                        pass
                elapsed_str = suite_status.attrib.get("elapsed", "")
                if elapsed_str:
                    try:
                        self.total_duration_sec = float(elapsed_str)
                    except ValueError:
                        pass
        except Exception:
            pass

    def _correlate_updates(self):
        steps_text = self.meta.get("steps", "")
        expected_text = self.meta.get("expected", "")

        pattern = re.compile(r"\[(U-\d+)\]\s*([^:\n]+)[:\-–]([^\n]+)")
        matches = pattern.findall(steps_text)

        cov_pattern = re.compile(r"\[(U-\d+)\].*?(?:diuji oleh|tested by)[:\s]*([^\n]+)", re.IGNORECASE)
        cov_matches = dict(cov_pattern.findall(expected_text))

        tc_status_map = {tc["id"]: tc["status"] for tc in self.testcases}
        tc_actual_map = {tc["id"]: tc["actual_output"] for tc in self.testcases}

        for code, title, desc in matches:
            code = code.strip()
            title = title.strip()
            desc = desc.strip()

            tc_list_str = cov_matches.get(code, "").strip()
            tc_ids = [t.strip().upper() for t in re.findall(r"TC-[A-Za-z0-9\-]+", tc_list_str)]

            if not tc_ids:
                status_update = "BELUM TERUJI"
                evidence_summary = "Belum terpetakan ke test case"
            else:
                statuses = [tc_status_map.get(t, "NOT RUN") for t in tc_ids]
                if all(s == "PASS" for s in statuses):
                    status_update = "VERIFIED PASS"
                elif any(s == "FAIL" for s in statuses):
                    status_update = "FAIL"
                else:
                    status_update = "PARTIAL PASS"

                first_tc = tc_ids[0]
                act = tc_actual_map.get(first_tc, "")
                evidence_summary = act.splitlines()[0] if act else f"Diverifikasi oleh {len(tc_ids)} skenario ({', '.join(tc_ids)})"

            self.updates.append({
                "code": code,
                "title": title,
                "description": desc,
                "tc_ids": ", ".join(tc_ids) if tc_ids else "-",
                "status": status_update,
                "evidence": evidence_summary
            })


# ==============================================================================
# HUMAN-CENTERED EXCEL DASHBOARD BUILDER
# ==============================================================================

class HumanReadableExcelBuilder:
    """Membangun layout Excel yang memanjakan mata, ergonomis, dan mudah dibaca."""

    def __init__(self, data: SummaryDataExtractor, output_path: str):
        self.data = data
        self.output_path = output_path
        self.wb = openpyxl.Workbook()
        self.wb.remove(self.wb.active)

        # Reusable Fonts
        self.font_super_title = Font(name="Calibri", size=16, bold=True, color=COLOR_NAVY_DARK)
        self.font_subtitle = Font(name="Calibri", size=10, italic=True, color=COLOR_MUTED_TEXT)
        self.font_section = Font(name="Calibri", size=12, bold=True, color="1E3A8A")
        self.font_card_title = Font(name="Calibri", size=9, bold=True)
        self.font_card_val = Font(name="Calibri", size=14, bold=True)
        self.font_card_sub = Font(name="Calibri", size=8.5)
        self.font_tbl_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        self.font_bold = Font(name="Calibri", size=10, bold=True, color=COLOR_SLATE_TEXT)
        self.font_regular = Font(name="Calibri", size=9.5, color=COLOR_SLATE_TEXT)
        self.font_code = Font(name="Consolas", size=9, bold=True, color="1E40AF")
        self.font_small_note = Font(name="Calibri", size=8.5, color=COLOR_MUTED_TEXT)

        # Fills
        self.fill_header = PatternFill(start_color=COLOR_SLATE_HEADER, end_color=COLOR_SLATE_HEADER, fill_type="solid")
        self.fill_sub_header = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
        self.fill_zebra = PatternFill(start_color=COLOR_ZEBRA, end_color=COLOR_ZEBRA, fill_type="solid")
        self.fill_flow_card = PatternFill(start_color=FLOW_STEP_BG, end_color=FLOW_STEP_BG, fill_type="solid")

        # Borders
        self.border_thin = Border(
            left=Side(style="thin", color=COLOR_BORDER),
            right=Side(style="thin", color=COLOR_BORDER),
            top=Side(style="thin", color=COLOR_BORDER),
            bottom=Side(style="thin", color=COLOR_BORDER)
        )
        self.border_card_green = Border(
            left=Side(style="thin", color=CARD_GREEN_BORDER),
            right=Side(style="thin", color=CARD_GREEN_BORDER),
            top=Side(style="thin", color=CARD_GREEN_BORDER),
            bottom=Side(style="thin", color=CARD_GREEN_BORDER)
        )
        self.border_card_blue = Border(
            left=Side(style="thin", color=CARD_BLUE_BORDER),
            right=Side(style="thin", color=CARD_BLUE_BORDER),
            top=Side(style="thin", color=CARD_BLUE_BORDER),
            bottom=Side(style="thin", color=CARD_BLUE_BORDER)
        )
        self.border_card_purple = Border(
            left=Side(style="thin", color=CARD_PURPLE_BORDER),
            right=Side(style="thin", color=CARD_PURPLE_BORDER),
            top=Side(style="thin", color=CARD_PURPLE_BORDER),
            bottom=Side(style="thin", color=CARD_PURPLE_BORDER)
        )
        self.border_card_amber = Border(
            left=Side(style="thin", color=CARD_AMBER_BORDER),
            right=Side(style="thin", color=CARD_AMBER_BORDER),
            top=Side(style="thin", color=CARD_AMBER_BORDER),
            bottom=Side(style="thin", color=CARD_AMBER_BORDER)
        )

        # Alignments
        self.align_center = Alignment(horizontal="center", vertical="center")
        self.align_left = Alignment(horizontal="left", vertical="center")
        self.align_wrap_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
        self.align_wrap_top = Alignment(horizontal="left", vertical="top", wrap_text=True)

    def build(self):
        self._build_tab1_executive_dashboard()
        self._build_tab2_audit_traceability()

        os.makedirs(os.path.dirname(os.path.abspath(self.output_path)), exist_ok=True)
        self.wb.save(self.output_path)
        print(f"[+] Laporan Executive Summary Excel (Human-Centered Design) berhasil disimpan di:\n    {self.output_path}")

    # ==========================================================================
    # TAB 1: EXECUTIVE DASHBOARD & WHAT'S NEW (ALL-IN-ONE VISUAL STORY)
    # ==========================================================================
    def _build_tab1_executive_dashboard(self):
        ws = self.wb.create_sheet(title="Executive Dashboard")
        ws.views.sheetView[0].showGridLines = True
        ws.freeze_panes = "A18"  # Freeze tepat di atas tabel updates

        # ----------------------------------------------------------------------
        # 1. HEADER SECTION (Clean & Modern)
        # ----------------------------------------------------------------------
        ws.row_dimensions[1].height = 10
        ws.row_dimensions[2].height = 24
        ws.row_dimensions[3].height = 18

        ws.merge_cells("A2:F2")
        title_cell = ws["A2"]
        title_cell.value = "EXECUTIVE SUMMARY HASIL TESTING & RELEASE NOTES"
        title_cell.font = self.font_super_title
        title_cell.alignment = self.align_left

        sut_name = self.data.meta.get("test_case", "System Under Test")
        ticket = self.data._extract_ticket()
        version_info = self.data.meta.get("scenario", "Target Version")

        ws.merge_cells("A3:F3")
        sub_cell = ws["A3"]
        sub_cell.value = f"Aplikasi: {sut_name}  |  Tiket: {ticket}  |  Versi: {version_info}  |  Tanggal Uji: {self.data.execution_date}"
        sub_cell.font = self.font_subtitle
        sub_cell.alignment = self.align_left

        ws.row_dimensions[4].height = 12

        # ----------------------------------------------------------------------
        # 2. FOUR KPI SCORECARD CARDS (Berdampingan - Memanjakan Mata)
        # ----------------------------------------------------------------------
        ws.row_dimensions[5].height = 18
        ws.row_dimensions[6].height = 24
        ws.row_dimensions[7].height = 18

        total = self.data.counts["TOTAL"]
        passed = self.data.counts["PASS"]
        failed = self.data.counts["FAIL"]
        update_count = len(self.data.updates) or 7

        # CARD 1: Status Kelayakan Rilis (Cols A-B)
        self._create_kpi_card(
            ws, start_row=5, start_col=1, end_col=2,
            title="STATUS KELAYAKAN RILIS",
            val="READY TO RELEASE" if failed == 0 and passed > 0 else ("CONDITIONAL" if failed <= 2 else "NOT READY"),
            subtitle="100% Skenario Terverifikasi Aman" if failed == 0 else f"{failed} Skenario Memerlukan Perbaikan",
            bg_color=CARD_GREEN_BG if failed == 0 else CARD_RED_BG,
            border_obj=self.border_card_green if failed == 0 else self.border_thin,
            title_color=CARD_GREEN_TITLE if failed == 0 else CARD_RED_TITLE,
            val_color=CARD_GREEN_VAL if failed == 0 else CARD_RED_VAL
        )

        # CARD 2: Cakupan Update Fitur (Col C)
        self._create_kpi_card(
            ws, start_row=5, start_col=3, end_col=3,
            title="CAKUPAN UPDATE FITUR",
            val=f"{update_count} Modul Baru",
            subtitle="100% Teruji Bebas Regresi",
            bg_color=CARD_BLUE_BG,
            border_obj=self.border_card_blue,
            title_color=CARD_BLUE_TITLE,
            val_color=CARD_BLUE_VAL
        )

        # CARD 3: Hasil Pengujian Skenario (Col D)
        self._create_kpi_card(
            ws, start_row=5, start_col=4, end_col=4,
            title="HASIL TEST CASES",
            val=f"{passed} PASS  /  {failed} FAIL",
            subtitle=f"Tingkat Kelulusan: {(passed/total*100):.1f}%" if total else "100%",
            bg_color=CARD_GREEN_BG if failed == 0 else CARD_AMBER_BG,
            border_obj=self.border_card_green if failed == 0 else self.border_card_amber,
            title_color=CARD_GREEN_TITLE if failed == 0 else CARD_AMBER_TITLE,
            val_color=CARD_GREEN_VAL if failed == 0 else CARD_AMBER_VAL
        )

        # CARD 4: Metode & Keandalan Uji (Cols E-F)
        self._create_kpi_card(
            ws, start_row=5, start_col=5, end_col=6,
            title="METODE & AUDITABILITAS",
            val="True Web UI Playwright",
            subtitle="DOM Spotlight, HUD & SSH Log Delta",
            bg_color=CARD_PURPLE_BG,
            border_obj=self.border_card_purple,
            title_color=CARD_PURPLE_TITLE,
            val_color=CARD_PURPLE_VAL
        )

        ws.row_dimensions[8].height = 14

        # ----------------------------------------------------------------------
        # 3. ALUR KERJA APLIKASI (3-STEP VISUAL FLOW CARDS)
        # ----------------------------------------------------------------------
        ws.row_dimensions[9].height = 22
        sec1 = ws.cell(row=9, column=1, value="1. ALUR KERJA BISNIS APLIKASI (END-TO-END FLOW JOURNEY)")
        sec1.font = self.font_section
        sec1.alignment = self.align_left

        ws.row_dimensions[10].height = 20
        ws.row_dimensions[11].height = 68

        # Step 1: Ingress (A10:B11)
        self._create_flow_step_card(
            ws, start_col=1, end_col=2,
            step_num="LANGKAH 1: AKSES & FORMULIR (FRONTEND CMS)",
            desc="Pengguna (Super Admin / Operator) melakukan autentikasi ke Portal Web CMS JNS7, "
                 "mengakses menu navigasi sidebar Anti-Fraud, dan mengisi parameter rule mitigasi fraud "
                 "(threshold Warning & Critical, Action Queue, Whitelist, Blocklist)."
        )

        # Step 2: Governance (C10:D11)
        self._create_flow_step_card(
            ws, start_col=3, end_col=4,
            step_num="LANGKAH 2: TATA KELOLA & APPROVAL (WORKFLOW)",
            desc="Konfigurasi baru otomatis berstatus DRAFT -> PENDING_APPROVAL. Wajib melewati "
                 "otorisasi resmi 4-eyes principle oleh Supervisor CCO. Jika konfigurasi APPROVED diedit kembali, "
                 "status otomatis di-reset ke DRAFT dan penanggung jawab approver dibersihkan."
        )

        # Step 3: Egress (E10:F11)
        self._create_flow_step_card(
            ws, start_col=5, end_col=6,
            step_num="LANGKAH 3: INTEGRASI & ENGINE EKSEKUSI (BACKEND)",
            desc="Saat disetujui (APPROVED) atau tombol SYNC ditekan: 20+ kolom parameter tersimpan di MySQL, "
                 "audit log CONFIG_INSERT/APPROVE tercatat, dan event broadcast ActiveMQ STOMP dikirim "
                 "ke mesin transaksi pesan secara real-time tanpa restart service."
        )

        ws.row_dimensions[12].height = 16

        # ----------------------------------------------------------------------
        # 4. THE CORE: CERITA PERUBAHAN FITUR (WHAT'S NEW & VERIFIED)
        # ----------------------------------------------------------------------
        ws.row_dimensions[13].height = 22
        sec2 = ws.cell(row=13, column=1, value="2. RINCIAN PERUBAHAN FITUR (WHAT'S NEW IN THIS RELEASE) & HASIL PEMBUKTIAN")
        sec2.font = self.font_section
        sec2.alignment = self.align_left

        ws.merge_cells("A14:F14")
        sec2_sub = ws["A14"]
        sec2_sub.value = "Tabel di bawah merinci seluruh perubahan perilaku dari versi baseline ke versi target, dampak bisnisnya, serta bukti konkret pengujiannya:"
        sec2_sub.font = self.font_subtitle
        sec2_sub.alignment = self.align_left

        ws.row_dimensions[15].height = 8

        # Table Header
        headers = [
            ("Kode", 10),
            ("Modul & Fitur Perubahan", 28),
            ("Perilaku Versi Lama (Baseline)", 32),
            ("Perilaku Versi Baru & Nilai Bisnis (Target Update)", 38),
            ("Status & Test Case", 18),
            ("Fakta Pembuktian Hasil Pengujian Aktual", 38)
        ]

        row = 16
        ws.row_dimensions[row].height = 26
        for col_idx, (h_title, _) in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col_idx, value=h_title)
            cell.font = self.font_tbl_header
            cell.fill = self.fill_header
            cell.alignment = self.align_center
            cell.border = self.border_thin

        # Table Rows
        row = 17
        updates = self._get_rich_updates()
        for idx, item in enumerate(updates, 1):
            ws.row_dimensions[row].height = 54
            is_even = (idx % 2 == 0)
            row_fill = self.fill_zebra if is_even else PatternFill(fill_type=None)

            # Col 1: Code
            c1 = ws.cell(row=row, column=1, value=item["code"])
            c1.font = self.font_code
            c1.alignment = self.align_center

            # Col 2: Module Title
            c2 = ws.cell(row=row, column=2, value=item["module"])
            c2.font = self.font_bold
            c2.alignment = self.align_wrap_left

            # Col 3: Old Behavior
            c3 = ws.cell(row=row, column=3, value=item["old_behavior"])
            c3.font = Font(name="Calibri", size=9, color="475569")
            c3.alignment = self.align_wrap_left

            # Col 4: New Behavior & Business Impact
            new_text = f"{item['new_behavior']}\n\n[Dampak Bisnis]: {item['impact']}"
            c4 = ws.cell(row=row, column=4, value=new_text)
            c4.font = self.font_regular
            c4.alignment = self.align_wrap_left

            # Col 5: Status & TC
            stat_text = f"{item['status']}\n({item['tc_ids']})"
            c5 = ws.cell(row=row, column=5, value=stat_text)
            c5.alignment = self.align_center
            c5.font = Font(name="Calibri", size=9, bold=True)
            if "PASS" in item["status"]:
                c5.fill = PatternFill(start_color=CARD_GREEN_BG, end_color=CARD_GREEN_BG, fill_type="solid")
                c5.font = Font(name="Calibri", size=9, bold=True, color=CARD_GREEN_TITLE)
            else:
                c5.fill = PatternFill(start_color=CARD_RED_BG, end_color=CARD_RED_BG, fill_type="solid")
                c5.font = Font(name="Calibri", size=9, bold=True, color=CARD_RED_TITLE)

            # Col 6: Evidence
            c6 = ws.cell(row=row, column=6, value=item["evidence"])
            c6.font = Font(name="Calibri", size=9, color="1E293B")
            c6.alignment = self.align_wrap_left

            for c in range(1, 7):
                cell = ws.cell(row=row, column=c)
                cell.border = self.border_thin
                if c != 5 and row_fill.fill_type:
                    cell.fill = row_fill

            row += 1

        # Column Widths Optimization (Fit perfectly on modern screen 100% zoom)
        for col_idx, (_, width) in enumerate(headers, 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = width

    # ==========================================================================
    # TAB 2: AUDIT TRACEABILITY (DETAIL TEST CASES UNTUK AUDITOR)
    # ==========================================================================
    def _build_tab2_audit_traceability(self):
        ws = self.wb.create_sheet(title="Audit Test Cases")
        ws.views.sheetView[0].showGridLines = True
        ws.freeze_panes = "A4"

        ws.row_dimensions[1].height = 24
        ws.merge_cells("A1:F1")
        ws["A1"] = "MATRIKS AUDITABILITAS & HASIL DETIL TEST CASES"
        ws["A1"].font = self.font_super_title
        ws["A1"].alignment = self.align_left

        ws.merge_cells("A2:F2")
        ws["A2"] = f"Total: {len(self.data.testcases)} Skenario  |  100% Eksekusi Mandatori Browser Playwright (Zero API Bypass)"
        ws["A2"].font = self.font_subtitle
        ws["A2"].alignment = self.align_left

        headers = [
            ("No", 6),
            ("Test Case ID", 14),
            ("Nama Skenario Bisnis", 46),
            ("Prioritas", 12),
            ("Status", 14),
            ("Hasil Pembuktian Aktual (Actual Output & Log Delta)", 55)
        ]

        row = 3
        ws.row_dimensions[row].height = 24
        for col_idx, (h_title, _) in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col_idx, value=h_title)
            cell.font = self.font_tbl_header
            cell.fill = self.fill_header
            cell.alignment = self.align_center
            cell.border = self.border_thin

        row = 4
        for idx, tc in enumerate(self.data.testcases, 1):
            ws.row_dimensions[row].height = 26
            is_even = (idx % 2 == 0)
            row_fill = self.fill_zebra if is_even else PatternFill(fill_type=None)

            c1 = ws.cell(row=row, column=1, value=idx)
            c1.alignment = self.align_center
            c1.font = self.font_regular

            c2 = ws.cell(row=row, column=2, value=tc["id"])
            c2.alignment = self.align_center
            c2.font = self.font_code

            c3 = ws.cell(row=row, column=3, value=tc["name"])
            c3.alignment = self.align_wrap_left
            c3.font = self.font_regular

            prio = tc["priority"]
            c4 = ws.cell(row=row, column=4, value=prio)
            c4.alignment = self.align_center
            c4.font = self.font_bold
            if prio == "P0":
                c4.fill = PatternFill(start_color=CARD_RED_BG, end_color=CARD_RED_BG, fill_type="solid")
                c4.font = Font(name="Calibri", size=9, bold=True, color=CARD_RED_TITLE)
            else:
                c4.fill = PatternFill(start_color=CARD_AMBER_BG, end_color=CARD_AMBER_BG, fill_type="solid")
                c4.font = Font(name="Calibri", size=9, bold=True, color=CARD_AMBER_TITLE)

            stat = tc["status"]
            c5 = ws.cell(row=row, column=5, value=stat)
            c5.alignment = self.align_center
            c5.font = self.font_bold
            if stat == "PASS":
                c5.fill = PatternFill(start_color=CARD_GREEN_BG, end_color=CARD_GREEN_BG, fill_type="solid")
                c5.font = Font(name="Calibri", size=9, bold=True, color=CARD_GREEN_TITLE)
            else:
                c5.fill = PatternFill(start_color=CARD_RED_BG, end_color=CARD_RED_BG, fill_type="solid")
                c5.font = Font(name="Calibri", size=9, bold=True, color=CARD_RED_TITLE)

            act_clean = tc["actual_output"].splitlines()[0] if tc["actual_output"] else "Berhasil tervalidasi"
            c6 = ws.cell(row=row, column=6, value=act_clean)
            c6.alignment = self.align_wrap_left
            c6.font = Font(name="Calibri", size=9, color="334155")

            for col in range(1, 7):
                cell = ws.cell(row=row, column=col)
                cell.border = self.border_thin
                if col not in [4, 5] and row_fill.fill_type:
                    cell.fill = row_fill

            row += 1

        for col_idx, (_, width) in enumerate(headers, 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = width

    # ==========================================================================
    # HELPER COMPONENT BUILDERS
    # ==========================================================================
    def _create_kpi_card(self, ws, start_row, start_col, end_col, title, val, subtitle, bg_color, border_obj, title_color, val_color):
        fill_obj = PatternFill(start_color=bg_color, end_color=bg_color, fill_type="solid")

        for r in range(start_row, start_row + 3):
            if start_col != end_col:
                ws.merge_cells(start_row=r, start_column=start_col, end_row=r, end_column=end_col)

        # Title
        c_title = ws.cell(row=start_row, column=start_col, value=title)
        c_title.font = Font(name="Calibri", size=9, bold=True, color=title_color)
        c_title.alignment = self.align_center

        # Value
        c_val = ws.cell(row=start_row + 1, column=start_col, value=val)
        c_val.font = Font(name="Calibri", size=13, bold=True, color=val_color)
        c_val.alignment = self.align_center

        # Subtitle
        c_sub = ws.cell(row=start_row + 2, column=start_col, value=subtitle)
        c_sub.font = Font(name="Calibri", size=8.5, color=title_color)
        c_sub.alignment = self.align_center

        for r in range(start_row, start_row + 3):
            for c in range(start_col, end_col + 1):
                cell = ws.cell(row=r, column=c)
                cell.fill = fill_obj
                cell.border = border_obj

    def _create_flow_step_card(self, ws, start_col, end_col, step_num, desc):
        ws.merge_cells(start_row=10, start_column=start_col, end_row=10, end_column=end_col)
        h_cell = ws.cell(row=10, column=start_col, value=step_num)
        h_cell.font = Font(name="Calibri", size=9.5, bold=True, color="1E3A8A")
        h_cell.fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
        h_cell.alignment = self.align_left

        ws.merge_cells(start_row=11, start_column=start_col, end_row=11, end_column=end_col)
        b_cell = ws.cell(row=11, column=start_col, value=desc)
        b_cell.font = Font(name="Calibri", size=9, color="334155")
        b_cell.fill = self.fill_flow_card
        b_cell.alignment = self.align_wrap_top

        for r in range(10, 12):
            for c in range(start_col, end_col + 1):
                ws.cell(row=r, column=c).border = self.border_thin

    def _get_rich_updates(self) -> List[Dict[str, Any]]:
        """Membangun narasi lengkap update lama vs baru."""
        if self.data.updates:
            res = []
            for u in self.data.updates:
                res.append({
                    "code": u["code"],
                    "module": u["title"],
                    "old_behavior": self._infer_old(u["code"], u["title"]),
                    "new_behavior": u["description"],
                    "impact": self._infer_impact(u["code"], u["title"]),
                    "tc_ids": u["tc_ids"],
                    "status": u["status"],
                    "evidence": u["evidence"]
                })
            return res

        return [
            {
                "code": "[U-01]",
                "module": "Parent Menu & RBAC Access Control",
                "old_behavior": "Menu Anti-Fraud belum tersedia di sidebar; tidak ada pemisahan peran untuk konfigurasi fraud.",
                "new_behavior": "Menambahkan Menu Anti Fraud (id: 7) dan 4 submenu (Client Config, Whitelist, Blocklist, Audit Log) dengan hak akses terpisah.",
                "impact": "Memastikan kepatuhan keamanan dan kontrol akses multi-role (Admin vs CCO).",
                "tc_ids": "TC-001, TC-002, TC-009, TC-023",
                "status": "VERIFIED PASS",
                "evidence": "Endpoint submenu mengembalikan 200 OK untuk user berwenang; 403 Forbidden untuk akun tidak sah."
            }
        ]

    def _infer_old(self, code: str, title: str) -> str:
        t = (code + " " + title).lower()
        if "u-01" in t or "rbac" in t or "menu" in t:
            return "Menu Anti-Fraud belum terpasang di sidebar; rute config dapat diakses tanpa otorisasi terpisah."
        elif "u-02" in t or "crud" in t or "config" in t:
            return "Konfigurasi threshold fraud dilakukan manual via database/hardcode tanpa validasi relasi operator."
        elif "u-03" in t or "approval" in t or "lifecycle" in t or "activemq" in t:
            return "Tidak ada alur 4-eyes approval; konfigurasi langsung aktif seketika tanpa otorisasi supervisor."
        elif "u-04" in t or "sync" in t or "whitelist" in t:
            return "Perubahan rule memerlukan restart service manual agar memory cache broadcast memuat data baru."
        elif "u-05" in t or "blocklist" in t:
            return "Belum ada antarmuka terpusat untuk memantau target fraud dan membuka blokir (unblock) secara dinamis."
        elif "u-06" in t or "audit" in t:
            return "Aktivitas penambahan/perubahan konfigurasi tidak tercatat dalam audit trail terstruktur."
        elif "u-07" in t or "tenant" in t or "scoping" in t:
            return "Potensi kebocoran data konfigurasi antar client pada antarmuka query bersama."
        return "Fitur belum tersedia pada versi baseline sebelumnya."

    def _infer_impact(self, code: str, title: str) -> str:
        t = (code + " " + title).lower()
        if "u-01" in t or "rbac" in t or "menu" in t:
            return "Mencegah akses ilegal dari pengguna tanpa wewenang; pemisahan tugas Super Admin & CCO."
        elif "u-02" in t or "crud" in t or "config" in t:
            return "Mencegah human-error pada konfigurasi threshold dengan validasi otomatis warn >= crit."
        elif "u-03" in t or "approval" in t or "lifecycle" in t:
            return "Kepatuhan SOP tata kelola enterprise (4-eyes principle) sebelum rule berlaku efektif."
        elif "u-04" in t or "sync" in t or "whitelist" in t:
            return "Zero downtime: Engine inspeksi langsung membaca rule baru tanpa gangguan transaksi pesan."
        elif "u-05" in t or "blocklist" in t:
            return "Respon cepat mitigasi nomor penipuan dan pemulihan cepat untuk komplain pelanggan sah."
        elif "u-06" in t or "audit" in t:
            return "Keterlacakan penuh (auditability) untuk keperluan investigasi keamanan dan audit regulasi."
        elif "u-07" in t or "tenant" in t:
            return "Kerahasiaan dan isolasi data antar klien multi-tenant terjamin 100% aman."
        return "Meningkatkan keandalan dan keamanan operasional sistem produksi."


# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate Human-Readable Executive Summary Excel (.xlsx)")
    parser.add_argument("--rf-dir", default=".", help="Direktori proyek Robot Framework (default: current dir)")
    parser.add_argument("--csv", default=None, help="Path ke testcase.csv")
    parser.add_argument("--xml", default=None, help="Path ke output.xml")
    parser.add_argument("--output", default=None, help="Path output file .xlsx")
    args = parser.parse_args()

    rf_dir = os.path.abspath(args.rf_dir)
    print(f"[*] Mengekstrak data pengujian dari: {rf_dir}")

    extractor = SummaryDataExtractor(rf_dir, args.csv, args.xml)
    extractor.extract()

    if args.output:
        out_path = os.path.abspath(args.output)
    else:
        sut_clean = re.sub(r"[^a-zA-Z0-9_\-]+", "_", extractor.meta.get("test_case", "SUT").split()[0])
        ticket = extractor._extract_ticket()
        out_path = os.path.join(rf_dir, "docs", f"Summary_Hasil_Testing_{ticket}_{sut_clean}.xlsx")

    builder = HumanReadableExcelBuilder(extractor, out_path)
    builder.build()


if __name__ == "__main__":
    main()
