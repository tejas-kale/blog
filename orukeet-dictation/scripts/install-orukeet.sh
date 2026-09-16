#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 --version
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r server/requirements.txt

# Q8 + Metal on Apple silicon (~714 MB weights). Avoid F16 and NeMo on 8 GB.
orukeet install --device auto --cache "$ROOT/orukeet-cache" --output "$ROOT/installation.json"

echo
echo "Installed. Next:"
echo "  source $ROOT/.venv/bin/activate"
echo "  $ROOT/scripts/run.sh"
