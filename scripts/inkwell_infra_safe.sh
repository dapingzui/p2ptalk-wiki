#!/bin/bash
set -euo pipefail
cd /Users/ice/.openclaw/workspace
source /Users/ice/.openclaw/workspace/.env.inkwell
python3 /Users/ice/.openclaw/workspace/scripts/inkwell_fetch.py articles --limit 20 --sort date --search "datacenter GPU inference networking optical power semiconductor AI infrastructure"
