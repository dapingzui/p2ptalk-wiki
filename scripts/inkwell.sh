#!/bin/bash
set -euo pipefail
source /Users/ice/.openclaw/workspace/.env.inkwell
python3 /Users/ice/.openclaw/workspace/scripts/inkwell_fetch.py "$@"
