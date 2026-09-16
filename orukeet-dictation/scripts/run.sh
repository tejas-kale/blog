#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This agent is a macOS dictation helper." >&2
  exit 1
fi

if [[ ! -d .venv ]]; then
  echo "Run scripts/install-orukeet.sh first." >&2
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

export ORUKEET_INSTALLATION="${ORUKEET_INSTALLATION:-$ROOT/installation.json}"
export ORUKEET_SERVER_SCRIPT="${ORUKEET_SERVER_SCRIPT:-$ROOT/server/orukeet_server.py}"
export ORUKEET_PYTHON="${ORUKEET_PYTHON:-$ROOT/.venv/bin/python}"
export ORUKEET_SPAWN_SERVER="${ORUKEET_SPAWN_SERVER:-true}"

if ! command -v swift >/dev/null 2>&1; then
  echo "Install Xcode Command Line Tools, then: swift build -c release --product orukeet-dictation" >&2
  echo "Starting the Orukeet worker only. The Swift agent is required to paste into other apps." >&2
  exec "$ORUKEET_PYTHON" "$ORUKEET_SERVER_SCRIPT"
fi

swift build -c release --product orukeet-dictation
exec "$(swift build -c release --show-bin-path)/orukeet-dictation"
