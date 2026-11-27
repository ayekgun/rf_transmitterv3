#!/usr/bin/env bash
# ==============================================================================
# Robot Framework Standard Runner for drpulltelkomsel v2.0.0
# Zero Truncation (--maxassignlength 0) | Clean BDD | Dual Listeners | 12-Column CSV
# ==============================================================================
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ -d "$DIR/../bin" ]; then
    DEFAULT_LOG_DIR="$(cd "$DIR/../bin" && pwd)"
else
    DEFAULT_LOG_DIR="$DIR/logs"
fi

export SUT_LOG_DIR="${SUT_LOG_DIR:-$DEFAULT_LOG_DIR}"
export SUT_LOG_PROFILE="${SUT_LOG_PROFILE:-$DIR/libraries/sut_profile.yaml}"
export TESTCASE_CSV_PATH="${TESTCASE_CSV_PATH:-$DIR/testcase.csv}"
export PYTHONPATH="$DIR/libraries:${PYTHONPATH:-}"

# Auto-detect runner IP for remote SUT (Jenkins CI / Server mode)
if [ -z "${MOCK_HOST:-}" ]; then
    if [ -n "${JENKINS_HOME:-}" ] || [ "${ENV:-}" = "server" ]; then
        DETECTED_IP=$(python3 -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('192.168.181.63', 3306)); print(s.getsockname()[0]); s.close()" 2>/dev/null || echo "127.0.0.1")
        export MOCK_HOST="$DETECTED_IP"
    else
        export MOCK_HOST="127.0.0.1"
    fi
fi

mkdir -p results/logs
rm -f results/output.xml results/log.html results/report.html

echo "========================================================================"
echo " Starting Robot Framework Automation Suite for drpulltelkomsel v2.0.0"
echo " Suite Dir:   $DIR"
echo " SUT Log Dir: $SUT_LOG_DIR"
echo " SUT Profile: $SUT_LOG_PROFILE"
echo " CSV Target:  $TESTCASE_CSV_PATH"
echo " Options:     --maxassignlength 0 | Dual Listeners (SutLogLibrary + CsvListener)"
echo "========================================================================"

exec python3 -m robot \
  --listener "libraries/SutLogLibrary.py" \
  --listener "libraries/CsvListener.py" \
  --maxassignlength 0 \
  -P libraries \
  --outputdir results \
  "$@" \
  tests/drpull_telkomsel_v2.robot
