#!/bin/bash
set -euo pipefail
source /Users/ice/.openclaw/workspace/.env.inkwell
PY=/Users/ice/.openclaw/workspace/scripts/inkwell_fetch.py

echo '=== HOME ==='
python3 "$PY" home

echo
echo '=== TRENDING ==='
python3 "$PY" articles --limit 8 --sort likes

echo
echo '=== AI_ML ==='
python3 "$PY" articles --limit 8 --sort date --category 'AI & ML'
