#!/bin/sh
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python_bin=${EXPERIMENT_PYTHON:-/Users/tejaskale/Code/blog/.venv/bin/python}

emacs --batch -Q --eval "(progn (require 'org) (org-babel-tangle-file \"$here/tts_preprocessing.org\"))"
"$python_bin" "$here/backfill_quality.py"
"$python_bin" "$here/verify_quality.py"
