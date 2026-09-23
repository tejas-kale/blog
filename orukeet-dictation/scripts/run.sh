#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This agent pastes into macOS apps. Run it on the Mac." >&2
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
export ORUKEET_SPAWN_SERVER="${ORUKEET_SPAWN_SERVER:-true}"

exec python -m dictation
