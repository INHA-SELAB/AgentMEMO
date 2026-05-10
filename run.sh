#!/usr/bin/env bash
# AgentMEMO — convenience launcher (macOS / Linux).
#
# First run: creates a .venv and installs the package + deps.
# Subsequent runs: just launches the GUI.
#
# Usage:
#   chmod +x run.sh    # one-time, if git didn't preserve the +x bit
#   ./run.sh

set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"
VENV=".venv"
VENV_PY="$VENV/bin/python"

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Error: '$PY' not found in PATH. Install Python 3.10+ first." >&2
  echo "  macOS:  brew install python@3.12" >&2
  echo "  Linux:  sudo apt install python3 python3-venv  (Debian/Ubuntu)" >&2
  echo "  Or set PYTHON=/path/to/python3.x and re-run." >&2
  exit 1
fi

if [ ! -d "$VENV" ]; then
  echo "[setup] creating virtualenv at $VENV"
  "$PY" -m venv "$VENV"
fi

# Detect whether the package is already installed in the venv.
if ! "$VENV_PY" -c "import agentmemo" >/dev/null 2>&1; then
  echo "[setup] installing AgentMEMO and its dependencies (one-time, ~30s)"
  "$VENV_PY" -m pip install --upgrade pip --quiet
  "$VENV_PY" -m pip install -e . --quiet
fi

# Replace this shell with the GUI process so Ctrl-C / signals work cleanly.
exec "$VENV_PY" -m agentmemo "$@"
