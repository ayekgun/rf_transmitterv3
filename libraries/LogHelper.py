"""
LogHelper.py - Anti-Truncation & Transparent Payload Logging for Robot Framework 5.0.1+
Complies with Global QA SDET & RF Constitution:
- Chunk size 4000 characters to prevent log message truncation in RF 5.0.1
- Pretty-printed JSON snapshots (indent=2)
- Transparent PASS and FAIL comparison logging (Expected vs Actual field-by-field)
"""
import json
from robot.api import logger

CHUNK_SIZE = 4000

def _format_content(content):
    if isinstance(content, (dict, list)):
        return json.dumps(content, indent=2, ensure_ascii=False, default=str)
    return str(content)

def _log_chunked(title, content, chunk_size=CHUNK_SIZE):
    """
    Emits chunked log messages into Robot Framework log.html.
    Prevents truncation in RF 5.0.1 without relying on --maxlogmessage.
    """
    text = _format_content(content)
    total_len = len(text)
    total_parts = max(1, (total_len + chunk_size - 1) // chunk_size)

    logger.info(f"--- START {title} | Length={total_len} chars | Parts={total_parts} ---")
    if total_len <= chunk_size:
        logger.info(text)
    else:
        for idx in range(total_parts):
            start = idx * chunk_size
            end = start + chunk_size
            logger.info(f"[{title} | PART {idx + 1}/{total_parts}]\n{text[start:end]}")
    logger.info(f"--- END {title} ---")

def deep_compare(expected, actual, path=""):
    """
    Recursively compares expected vs actual values (dicts, lists, scalars).
    Handles numeric equality between int and float (e.g. 500 == 500.0).
    Returns a list of human-readable mismatch strings.
    """
    mismatches = []
    current_path = path if path else "root"

    # Numeric equivalence check
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        if abs(float(expected) - float(actual)) > 1e-6:
            mismatches.append(f"At '{current_path}': expected numeric {expected}, got {actual}")
        return mismatches

    # Dict comparison
    if isinstance(expected, dict) and isinstance(actual, dict):
        all_keys = sorted(set(expected.keys()) | set(actual.keys()))
        for k in all_keys:
            subpath = f"{current_path}.{k}" if path else str(k)
            if k not in expected:
                mismatches.append(f"At '{subpath}': unexpected extra key in actual payload (value: {actual[k]})")
            elif k not in actual:
                mismatches.append(f"At '{subpath}': expected key missing from actual payload (expected: {expected[k]})")
            else:
                mismatches.extend(deep_compare(expected[k], actual[k], subpath))
        return mismatches

    # List comparison
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            mismatches.append(f"At '{current_path}': array length mismatch. Expected {len(expected)} items, got {len(actual)} items.")
        min_len = min(len(expected), len(actual))
        for i in range(min_len):
            subpath = f"{current_path}[{i}]"
            mismatches.extend(deep_compare(expected[i], actual[i], subpath))
        return mismatches

    # String & other scalar comparison
    if str(expected).strip() != str(actual).strip():
        mismatches.append(f"At '{current_path}': expected '{expected}', got '{actual}'")
    return mismatches

def log_transparent_comparison(title, expected, actual, mismatches=None):
    """
    Logs full snapshots of Expected and Actual payloads plus field-by-field verification.
    MANDATORY: Must be logged for BOTH PASS and FAIL outcomes to ensure auditable logs.
    """
    logger.info(f"================================================================================")
    logger.info(f" TRANSPARENT PAYLOAD AUDIT: {title}")
    logger.info(f"================================================================================")
    _log_chunked(f"[EXPECTED PAYLOAD] {title}", expected)
    _log_chunked(f"[ACTUAL PAYLOAD] {title}", actual)

    if mismatches:
        logger.error(f"--- [COMPARISON RESULT: {title}] FAIL - {len(mismatches)} MISMATCH(ES) FOUND ---")
        for idx, diff in enumerate(mismatches, 1):
            logger.error(f"  [{idx}] {diff}")
    else:
        logger.info(f"--- [COMPARISON RESULT: {title}] PASS - 100% MATCH (All fields identical) ---")
    logger.info(f"================================================================================")
