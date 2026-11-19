# -*- coding: utf-8 -*-
import datetime
import logging
import os
import shutil
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ExcelReporter")

# Import Test Catalog
try:
    from libraries.test_catalog import TEST_CATALOG
except ImportError:
    try:
        from test_catalog import TEST_CATALOG
    except ImportError:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from test_catalog import TEST_CATALOG


def safe_set_cell(ws, row, col, value=None):
    """Safely writes a value to a cell, automatically unmerging if the cell is a MergedCell."""
    cell = ws.cell(row, col)
    if isinstance(cell, openpyxl.cell.cell.MergedCell):
        for rng in list(ws.merged_cells.ranges):
            if cell.coordinate in rng:
                ws.unmerge_cells(str(rng))
                break
        cell = ws.cell(row, col)
    if value is not None:
        cell.value = value
    return cell


class ExcelReporter:
    """Robot Framework Library & Listener for generating and updating SIT Test Reports (.xlsx).

    Follows Jatis SQA SIT standard reporting format.
    Maintains a class-level cache so Library keywords and Listener hooks share the exact same state.
    """

    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    # Class-level results store shared across all Library and Listener instances
    _results = {}

    @staticmethod
    def _resolve_transmitter_name():
        t_name = os.environ.get("TRANSMITTER_NAME")
        if t_name:
            return t_name.strip()
        try:
            from robot.libraries.BuiltIn import BuiltIn
            val = BuiltIn().get_variable_value("${TransmitterName}")
            if val:
                return str(val).strip()
        except Exception:
            pass
        return None

    def __init__(self, excel_path=None, sheet_name=None, original_path=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_dir = base_dir

        self.excel_path = excel_path
        self.sheet_name = sheet_name or "SIT"
        self.original_path = original_path

        t_name = self._resolve_transmitter_name()

        if not self.excel_path:
            env_excel = os.environ.get("EXCEL_REPORT_PATH")
            if env_excel:
                self.excel_path = env_excel
            elif t_name:
                self.excel_path = os.path.join(
                    base_dir, "reports", f"Transmitter_{t_name}_Test_Results.xlsx"
                )
            else:
                self.excel_path = os.path.join(
                    base_dir, "reports", "TransmitterInfobip_Test_Results.xlsx"
                )

        if not self.original_path:
            template_candidates = [
                os.path.join(base_dir, "templates", f"Transmitter_{t_name}_Test_Results_Template.xlsx") if t_name else None,
                os.path.join(base_dir, "templates", "Transmitter_Template.xlsx"),
                os.path.join(base_dir, "templates", "TransmitterInfobip_Test_Results_Template.xlsx"),
                os.path.join(base_dir, "reports", "TransmitterInfobip_Test_Results.xlsx"),
                os.path.join(base_dir, "templates", "RedisCacheManager_Test_Results_Template.xlsx"),
            ]
            for candidate in template_candidates:
                if candidate and os.path.exists(candidate):
                    self.original_path = candidate
                    break

        if self.excel_path and not os.path.isabs(self.excel_path):
            self.excel_path = os.path.normpath(os.path.join(base_dir, self.excel_path))
        if self.original_path and not os.path.isabs(self.original_path):
            self.original_path = os.path.normpath(os.path.join(base_dir, self.original_path))

        self.ROBOT_LIBRARY_LISTENER = self

    def end_test(self, data, result):
        """Robot Framework Listener hook called at the end of each test case."""
        test_name = result.name
        if ":" in test_name:
            tc_id = test_name.split(":")[0].strip()
        elif "-" in test_name:
            tc_id = test_name.split("-")[0].strip()
        else:
            tc_id = test_name.strip()

        # Map Robot status
        if result.status == "PASS":
            status = "OK"
        elif result.status == "SKIP":
            status = "SKIP"
        else:
            status = "NOK"

        # Check if test keyword already recorded real output
        if tc_id in ExcelReporter._results and ExcelReporter._results[tc_id].get("actual"):
            # If keyword already gave a status, keep it, otherwise update
            if not ExcelReporter._results[tc_id].get("status"):
                ExcelReporter._results[tc_id]["status"] = status
            if result.message and status == "NOK":
                ExcelReporter._results[tc_id]["log"] = result.message
        else:
            # Fallback if keyword did not record output
            if status == "SKIP":
                actual_output = f"SKIPPED: {result.message}" if result.message else "Test Skipped (Environment offline)"
            elif status == "NOK":
                actual_output = result.message if result.message else f"HTTP Status: {status}"
            else:
                actual_output = f"HTTP Status: {status} (Verified successfully)"

            self.record_test_result(
                tc_id,
                status,
                actual_output,
                result.message if status in ["NOK", "SKIP"] else "Success",
            )

    def close(self):
        """Called automatically by Robot Framework when suite finishes."""
        self.flush_results_to_excel()

    def record_test_result(self, tc_id, status, actual_output, log_text=""):
        """Records a single test result into shared class-level cache."""
        clean_status = str(status).upper()
        if clean_status in ["PASS", "OK"]:
            final_status = "OK"
        elif clean_status in ["SKIP", "SKIPPED"]:
            final_status = "SKIP"
        else:
            final_status = "NOK"

        ExcelReporter._results[tc_id] = {
            "status": final_status,
            "actual": str(actual_output) if actual_output is not None else "",
            "log": str(log_text) if log_text is not None else "",
        }
        logger.info(f"Recorded test result for {tc_id}: {final_status}")

    def update_test_case_in_excel(
        self, tc_id, status="OK", actual_output=None, log_text=None
    ):
        """Keyword to immediately record and flush a specific test case to the Excel report."""
        self.record_test_result(tc_id, status, actual_output, log_text)
        self.flush_results_to_excel()

    def _ensure_workbook(self, target_path):
        """Loads existing workbook or copies from original SIT template."""
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        if os.path.exists(target_path):
            return openpyxl.load_workbook(target_path)

        if self.original_path and os.path.exists(self.original_path):
            shutil.copyfile(self.original_path, target_path)
            logger.info(f"Created {target_path} from template {self.original_path}")
            return openpyxl.load_workbook(target_path)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = self.sheet_name
        headers = [
            "Test Case ID",
            "Description",
            "Test Scenario",
            "Test case",
            "Test Steps",
            "Test Data/Precondition",
            "Expected Result",
            "Actual Output",
            "Status",
            "Log",
            "Note/Description",
        ]
        ws.append(headers)
        return wb

    def flush_results_to_excel(self):
        """Writes all test case execution results into the SIT report spreadsheet.

        Populates complete SIT scenario descriptions, test steps, curl payloads,
        and REAL actual output received from the server.
        """
        if not ExcelReporter._results:
            logger.info("No results to flush to Excel.")
            return

        t_name = self._resolve_transmitter_name()
        if t_name and (
            not self.excel_path
            or os.path.basename(self.excel_path) == "TransmitterInfobip_Test_Results.xlsx"
        ):
            self.excel_path = os.path.join(
                self.base_dir, "reports", f"Transmitter_{t_name}_Test_Results.xlsx"
            )

        if not self.original_path or not os.path.exists(self.original_path):
            template_candidates = [
                os.path.join(self.base_dir, "templates", f"Transmitter_{t_name}_Test_Results_Template.xlsx") if t_name else None,
                os.path.join(self.base_dir, "templates", "Transmitter_Template.xlsx"),
                os.path.join(self.base_dir, "templates", "TransmitterInfobip_Test_Results_Template.xlsx"),
                os.path.join(self.base_dir, "reports", "TransmitterInfobip_Test_Results.xlsx"),
                os.path.join(self.base_dir, "templates", "RedisCacheManager_Test_Results_Template.xlsx"),
            ]
            for candidate in template_candidates:
                if candidate and os.path.exists(candidate):
                    self.original_path = candidate
                    break

        target_path = self.excel_path
        try:
            wb = self._ensure_workbook(target_path)
            if self.sheet_name not in wb.sheetnames:
                ws = wb.create_sheet(self.sheet_name)
            else:
                ws = wb[self.sheet_name]

            # Unmerge cells from row 2 downwards to prevent MergedCell read-only conflicts
            for rng in list(ws.merged_cells.ranges):
                if rng.min_row >= 2:
                    try:
                        ws.unmerge_cells(str(rng))
                    except Exception:
                        pass

            # Styles
            pass_fill = PatternFill(
                start_color="66FF33", end_color="66FF33", fill_type="solid"
            )
            fail_fill = PatternFill(
                start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"
            )
            skip_fill = PatternFill(
                start_color="FFF2CC", end_color="FFF2CC", fill_type="solid"
            )

            pass_font = Font(name="Calibri", size=10, bold=True, color="006100")
            fail_font = Font(name="Calibri", size=10, bold=True, color="9C0006")
            skip_font = Font(name="Calibri", size=10, bold=True, color="7F6000")

            regular_font = Font(name="Calibri", size=10)
            bold_font = Font(name="Calibri", size=10, bold=True)
            align_left = Alignment(horizontal="left", vertical="top", wrap_text=True)
            align_center = Alignment(horizontal="center", vertical="top")

            thin_border = Border(
                left=Side(style="thin", color="D9D9D9"),
                right=Side(style="thin", color="D9D9D9"),
                top=Side(style="thin", color="D9D9D9"),
                bottom=Side(style="thin", color="D9D9D9"),
            )

            # Map existing rows by Test Case ID
            existing_row_map = {}
            for row in range(1, min(ws.max_row + 1, 100)):
                val = ws.cell(row, 1).value
                if val:
                    tc_id = str(val).strip()
                    existing_row_map[tc_id] = row

            all_tc_keys = list(TEST_CATALOG.keys())
            for k in ExcelReporter._results.keys():
                if k not in all_tc_keys:
                    all_tc_keys.append(k)

            # Find the highest row currently in use
            max_used_row = 1
            for r in range(1, min(ws.max_row + 1, 200)):
                if any(ws.cell(r, c).value for c in range(1, 12)):
                    max_used_row = r

            next_new_row = max(max_used_row + 1, 2)
            updated_count = 0

            for tc_id in all_tc_keys:
                res = ExcelReporter._results.get(tc_id)
                cat = TEST_CATALOG.get(tc_id) or {}

                # Determine row index
                if tc_id in existing_row_map:
                    row_idx = existing_row_map[tc_id]
                else:
                    row_idx = next_new_row
                    existing_row_map[tc_id] = row_idx
                    next_new_row += 1

                # Populate Columns A-G from catalog
                c1 = safe_set_cell(ws, row_idx, 1, tc_id)
                c1.font = bold_font
                c1.alignment = align_center
                c1.border = thin_border

                if cat.get("description"):
                    c2 = safe_set_cell(ws, row_idx, 2, cat["description"])
                    c2.font = regular_font
                    c2.alignment = align_left
                    c2.border = thin_border

                if cat.get("scenario"):
                    scenario_text = cat["scenario"]
                    if t_name and t_name.lower() != "infobip":
                        scenario_text = scenario_text.replace("Infobip", t_name.capitalize()).replace("infobip", t_name.lower())
                    c3 = safe_set_cell(ws, row_idx, 3, scenario_text)
                    c3.font = regular_font
                    c3.alignment = align_left
                    c3.border = thin_border

                if cat.get("test_case"):
                    tc_text = cat["test_case"]
                    if t_name and t_name.lower() != "infobip":
                        tc_text = tc_text.replace("Infobip", t_name.capitalize()).replace("infobip", t_name.lower())
                    c4 = safe_set_cell(ws, row_idx, 4, tc_text)
                    c4.font = regular_font
                    c4.alignment = align_left
                    c4.border = thin_border

                if cat.get("steps"):
                    c5 = safe_set_cell(ws, row_idx, 5, cat["steps"])
                    c5.font = regular_font
                    c5.alignment = align_left
                    c5.border = thin_border

                if cat.get("test_data"):
                    c6 = safe_set_cell(ws, row_idx, 6, cat["test_data"])
                    c6.font = regular_font
                    c6.alignment = align_left
                    c6.border = thin_border

                if cat.get("expected"):
                    c7 = safe_set_cell(ws, row_idx, 7, cat["expected"])
                    c7.font = regular_font
                    c7.alignment = align_left
                    c7.border = thin_border

                # Populate Real Execution Output (Columns H, I, J, K)
                if res:
                    actual_text = res.get("actual", "")
                    c_act = safe_set_cell(ws, row_idx, 8, actual_text)
                    c_act.font = regular_font
                    c_act.alignment = align_left
                    c_act.border = thin_border

                    status = res.get("status", "OK")
                    c_stat = safe_set_cell(ws, row_idx, 9, status)
                    c_stat.alignment = align_center
                    c_stat.border = thin_border
                    if status == "OK":
                        c_stat.fill = pass_fill
                        c_stat.font = pass_font
                    elif status == "SKIP":
                        c_stat.fill = skip_fill
                        c_stat.font = skip_font
                    else:
                        c_stat.fill = fail_fill
                        c_stat.font = fail_font

                    c_log = safe_set_cell(ws, row_idx, 10, res.get("log", ""))
                    c_log.font = regular_font
                    c_log.alignment = align_left
                    c_log.border = thin_border

                    c_note = safe_set_cell(
                        ws, row_idx, 11, "Automated - Robot Framework"
                    )
                    c_note.font = regular_font
                    c_note.alignment = align_center
                    c_note.border = thin_border

                    updated_count += 1

            # Update Summary Sheet if available
            if "Summary" in wb.sheetnames:
                sum_ws = wb["Summary"]
                overall_status = (
                    "OK"
                    if all(
                        r.get("status") in ["OK", "SKIP"]
                        for r in ExcelReporter._results.values()
                    )
                    else "NOK"
                )
                safe_set_cell(sum_ws, 11, 4, overall_status)
                safe_set_cell(sum_ws, 7, 4, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
                safe_set_cell(sum_ws, 14, 4, "Automated (Robot Framework)")
                if t_name:
                    safe_set_cell(sum_ws, 2, 4, f"PB - JATIS - JNS 6.5 - Transmitter {t_name.capitalize()}")
                    safe_set_cell(sum_ws, 15, 4, f"automation/transmitter/{t_name}")
                else:
                    safe_set_cell(sum_ws, 15, 4, "automation/transmitter")

            # Adjust column widths for professional presentation
            col_widths = {
                1: 16,  # Test Case ID
                2: 26,  # Description
                3: 30,  # Test Scenario
                4: 45,  # Test case
                5: 45,  # Test Steps
                6: 45,  # Test Data
                7: 45,  # Expected Result
                8: 55,  # Actual Output
                9: 12,  # Status
                10: 30,  # Log
                11: 25,  # Note
            }
            for col_idx, width in col_widths.items():
                col_letter = get_column_letter(col_idx)
                ws.column_dimensions[col_letter].width = width

            wb.save(target_path)
            logger.info(
                f"Successfully generated full SIT report with {updated_count} test cases in {target_path}"
            )
            print(
                f"[ExcelReporter] Successfully updated {updated_count} test cases in {target_path} (sheet: {self.sheet_name})"
            )
        except PermissionError:
            alt_path = target_path.replace(".xlsx", "_run_output.xlsx")
            wb.save(alt_path)
            logger.warning(f"File locked by Excel, saved to: {alt_path}")
            print(f"[ExcelReporter] File locked, saved results to {alt_path}")
        except Exception as e:
            logger.error(f"Failed to update Excel: {e}")
            raise
