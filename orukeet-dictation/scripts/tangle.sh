#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
emacs --batch --eval "(progn (require 'org) (org-babel-tangle-file \"$ROOT/orukeet-dictation.org\"))"
