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

if [[ "$(uname -s)" == "Darwin" ]]; then
  python -m pip install -r requirements.txt
else
  echo "Skipping PyObjC. The dictation agent itself only runs on macOS." >&2
fi

# Q8 + Metal on Apple silicon (~714 MB weights). Avoid F16 and NeMo on 8 GB.
orukeet install --device auto --cache "$ROOT/orukeet-cache" --output "$ROOT/installation.json"

echo
echo "Installed. Next, on the Mac:"
echo "  $ROOT/scripts/run.sh"
