#!/usr/bin/env bash
# ==============================================================================
# Entrypoint Utama: start.sh
# ==============================================================================
# Script wrapper ringkas yang meneruskan eksekusi ke scripts/run_tests.sh.
# Penggunaan:
#   ./scripts/start.sh
#   ./scripts/start.sh --test "*TC-035*"
# ==============================================================================
set -euo pipefail
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
exec "${SCRIPT_DIR}/run_tests.sh" "$@"
