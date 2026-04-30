#!/bin/bash
# Soul Guardian security check — runs as cron, no LLM needed
# Checks core agent files for unauthorized changes, alerts via Telegram
set -euo pipefail

GUARDIAN_SCRIPT=""
for path in \
  "$HOME/.openclaw/skills/clawsec/soul_guardian.py" \
  /opt/homebrew/lib/node_modules/openclaw/skills/clawsec/skills/soul-guardian/scripts/soul_guardian.py \
  "$HOME/.openclaw/skills/clawsec/skills/soul-guardian/scripts/soul_guardian.py"; do
  if [ -f "$path" ]; then
    GUARDIAN_SCRIPT="$path"
    break
  fi
done

if [ -z "$GUARDIAN_SCRIPT" ]; then
  exit 0  # Soul Guardian not installed, skip silently
fi

cd /Users/ice/.openclaw/workspace

# Run check
OUTPUT=$(python3 "$GUARDIAN_SCRIPT" check --actor cron --output-format alert 2>&1) || true

if [ -n "$OUTPUT" ] && [ "$OUTPUT" != "OK" ]; then
  # Ignore-mode drift is intentionally non-actionable; keep freshness without noisy alerts.
  ACTIONABLE=$(printf '%s\n' "$OUTPUT" | grep -v '\[ignore\]' || true)
  if [ -z "$ACTIONABLE" ]; then
    echo "[soul-guardian] OK at $(date) (ignored drift only)"
    exit 0
  fi

  # Security alert — send via Telegram
  TOKEN=$(python3 -c "
import json
with open('/Users/ice/.openclaw/openclaw.json') as f:
    d = json.load(f)
for k,v in d.get('channels',{}).get('telegram',{}).get('providers',{}).items():
    t = v.get('token','')
    if t: print(t); break
" 2>/dev/null)

  CHAT_ID="426529471"

  if [ -n "$TOKEN" ]; then
    curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
      -d "chat_id=${CHAT_ID}" \
      -d "text=🚨 Soul Guardian Alert

${ACTIONABLE}" \
      -d "parse_mode=Markdown" > /dev/null 2>&1 || \
    curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
      -d "chat_id=${CHAT_ID}" \
      -d "text=🚨 Soul Guardian Alert: $(echo "$ACTIONABLE" | head -c 500)" > /dev/null 2>&1
  fi

  echo "[soul-guardian] ALERT at $(date): $ACTIONABLE"
else
  echo "[soul-guardian] OK at $(date)"
fi
