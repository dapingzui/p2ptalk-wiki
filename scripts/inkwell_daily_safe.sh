#!/bin/bash
set -euo pipefail
cd /Users/ice/.openclaw/workspace
source /Users/ice/.openclaw/workspace/.env.inkwell
exec /Users/ice/.openclaw/workspace/scripts/inkwell_daily.sh
