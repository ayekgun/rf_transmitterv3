#!/bin/bash
# Start/stop script for MockTelkomselV2 daemon on Server 51.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$DIR/mock_drpull.pid"
OUTLOG="$DIR/mock_drpull.log"
PYTHON_BIN=$(command -v python3 || echo "/usr/bin/python3")
PORT="${MOCK_PORT:-8095}"

case "$1" in
start)
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "Mock Telkomsel V2 is already running (PID=$(cat "$PIDFILE"))."
        exit 0
    fi
    echo "Starting Mock Telkomsel V2 on port $PORT..."
    MOCK_PORT="$PORT" nohup "$PYTHON_BIN" "$DIR/mock_drpull.py" > "$OUTLOG" 2>&1 &
    PID=$!
    echo "$PID" > "$PIDFILE"
    sleep 1
    if kill -0 "$PID" 2>/dev/null; then
        echo "Mock Telkomsel V2 started successfully (PID=$PID, Port=$PORT)."
    else
        echo "Failed to start Mock Telkomsel V2. Check log: $OUTLOG"
        exit 1
    fi
    ;;
stop)
    if [ ! -f "$PIDFILE" ]; then
        # Check if process is running by name
        PIDS=$(pgrep -f "mock_drpull.py" 2>/dev/null)
        if [ -n "$PIDS" ]; then
            kill -15 $PIDS 2>/dev/null
            sleep 1
            kill -9 $PIDS 2>/dev/null
            echo "Mock Telkomsel V2 stopped (PIDs: $PIDS)."
        else
            echo "Mock Telkomsel V2 is not running."
        fi
        exit 0
    fi
    PID=$(cat "$PIDFILE")
    kill -15 "$PID" 2>/dev/null
    sleep 1
    kill -9 "$PID" 2>/dev/null
    rm -f "$PIDFILE"
    echo "Mock Telkomsel V2 (PID=$PID) stopped."
    ;;
status)
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "Mock Telkomsel V2 is running (PID=$(cat "$PIDFILE"), Port=$PORT)."
        curl -s -m 2 "http://127.0.0.1:$PORT/mock-ctrl/health" || true
        echo ""
    else
        PIDS=$(pgrep -f "mock_drpull.py" 2>/dev/null)
        if [ -n "$PIDS" ]; then
            echo "Mock Telkomsel V2 is running (PIDs: $PIDS)."
        else
            echo "Mock Telkomsel V2 is stopped."
        fi
    fi
    ;;
restart)
    "$0" stop
    sleep 2
    "$0" start
    ;;
*)
    echo "Usage: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac

exit 0
