#!/bin/sh
#!/bin/sh
set -eu
cd "$(dirname "$0")"
emacs --batch -l org --eval \
  '(org-babel-tangle-file "tts_preprocessing.org")' >/dev/null
git diff --exit-code -- tts_preprocessing.py run-experiment.sh
/Users/tejaskale/Code/blog/.venv/bin/python tts_preprocessing.py
