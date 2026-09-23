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
  echo "Skipping PyObjC and llama-cpp-python. The dictation agent itself runs on macOS." >&2
fi

# Q8 weights are about 714 MB. One worker fits an 8 GB MacBook Air.
orukeet install --device auto --cache "$ROOT/orukeet-cache" --output "$ROOT/installation.json"

echo
echo "Installed. On the Mac, run:"
echo "  $ROOT/scripts/run.sh"
