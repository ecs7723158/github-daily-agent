#!/usr/bin/env bash
# ==============================================================================
# Daily Sideproject Agent Runner Script for macOS Crontab / Launchd
# ==============================================================================

set -o pipefail

# Setup standard environment PATH for macOS (Homebrew, pyenv, standard bins)
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.pyenv/shims:$PATH"

# Resolve absolute directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Load .env if present
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/.env"
    set +a
fi

LOG_FILE="$SCRIPT_DIR/cron.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
echo "========================================================" >> "$LOG_FILE"
echo "[$TIMESTAMP] Starting daily_sideproject_agent.py execution..." >> "$LOG_FILE"

# Detect Python 3 binary
if command -v /opt/homebrew/bin/python3 >/dev/null 2>&1; then
    PYTHON_BIN="/opt/homebrew/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN=$(command -v python3)
else
    echo "[$TIMESTAMP] [ERROR] Python 3 not found in PATH!" >> "$LOG_FILE"
    exit 1
fi

# Execute script with passed arguments or defaults
"$PYTHON_BIN" "$SCRIPT_DIR/daily_sideproject_agent.py" "$@" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

END_TIME=$(date "+%Y-%m-%d %H:%M:%S")
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$END_TIME] [SUCCESS] Agent executed successfully." >> "$LOG_FILE"
else
    echo "[$END_TIME] [ERROR] Agent failed with exit code $EXIT_CODE." >> "$LOG_FILE"
fi
echo "========================================================" >> "$LOG_FILE"

exit $EXIT_CODE
