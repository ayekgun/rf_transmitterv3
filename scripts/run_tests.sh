#!/usr/bin/env bash
# ==============================================================================
# Robot Framework Standard Runner for drpulltelkomsel v2.0.0
# Zero Truncation (--maxassignlength 0) | Clean BDD | Dual Listeners | 12-Column CSV
# ==============================================================================
set -e

export PYTHONUNBUFFERED=1
export PATH="$HOME/.local/bin:$PATH"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ -d "$DIR/../bin" ]; then
    DEFAULT_LOG_DIR="$(cd "$DIR/../bin" && pwd)"
else
    DEFAULT_LOG_DIR="$DIR/logs"
fi
mkdir -p "$DEFAULT_LOG_DIR"

export SUT_LOG_DIR="${SUT_LOG_DIR:-$DEFAULT_LOG_DIR}"
export SUT_LOG_PROFILE="${SUT_LOG_PROFILE:-$DIR/libraries/sut_profile.yaml}"
export TESTCASE_CSV_PATH="${TESTCASE_CSV_PATH:-$DIR/testcase.csv}"
export PYTHONPATH="$DIR/libraries:${PYTHONPATH:-}"

# Auto-detect Python interpreter with robotframework installed
PYTHON_EXE=""
for py in python3.10 python3.11 python3.12 python3.13 python3.14 python3 python; do
  if command -v "$py" &>/dev/null; then
    if "$py" -c "import robot, pymongo" &>/dev/null; then
      PYTHON_EXE="$py"
      break
    fi
  fi
done

if [ -n "$PYTHON_EXE" ]; then
  RUNNER=("$PYTHON_EXE" -m robot)
elif command -v robot &>/dev/null; then
  RUNNER=(robot)
elif [ -x "$HOME/.local/bin/robot" ]; then
  RUNNER=("$HOME/.local/bin/robot")
else
  RUNNER=(python3 -m robot)
fi

# Default Mock Server coordinates (Server 51)
export MOCK_HOST="${MOCK_HOST:-192.168.181.51}"
export MOCK_PORT="${MOCK_PORT:-8095}"

mkdir -p results/logs
rm -f results/output.xml results/log.html results/report.html

echo "========================================================================"
echo " Starting Robot Framework Automation Suite for drpulltelkomsel v2.0.0"
echo " Suite Dir:   $DIR"
echo " Runner:      ${RUNNER[*]}"
echo " SUT Log Dir: $SUT_LOG_DIR"
echo " SUT Profile: $SUT_LOG_PROFILE"
echo " CSV Target:  $TESTCASE_CSV_PATH"
echo " Options:     --maxassignlength 0 | Dual Listeners (SutLogLibrary + CsvListener)"
echo "========================================================================"

exec "${RUNNER[@]}" \
  --listener "libraries/SutLogLibrary.py" \
  --listener "libraries/CsvListener.py" \
  --maxassignlength 0 \
  -P libraries \
  --outputdir results \
  "$@" \
  tests/drpull_telkomsel_v2.robot
