#!/bin/bash
# Watchdog: monitor mihomo proxy + openclaw gateway
# Runs as KeepAlive LaunchAgent

LOG="/Users/ice/.openclaw/logs/watchdog-monitor.log"
PROXY_PORT=7892
CHECK_INTERVAL=30

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" >> "$LOG"
}

check_proxy() {
  # Use curl to check if proxy is actually responding to HTTP requests
  # (netstat/lsof can't reliably detect root-owned mihomo sockets)
  if curl -s --max-time 3 --noproxy '*' http://127.0.0.1:${PROXY_PORT} > /dev/null 2>&1; then
    return 0
  fi
  return 1
}

restart_mihomo() {
  log "PROXY_DOWN: port ${PROXY_PORT} not listening, restarting Clash Party"
  killall "Clash Party" 2>/dev/null
  sleep 5
  open -a "Clash Party"
  sleep 30
  if check_proxy; then
    log "PROXY_RECOVERED: Clash Party restarted successfully"
  else
    log "PROXY_STILL_DOWN: Clash Party restart failed, will retry next cycle"
  fi
}

check_gateway() {
  local pid
  pid=$(launchctl list 2>/dev/null | grep "ai.openclaw.gateway$" | awk '{print $1}')
  if [ "$pid" = "-" ] || [ -z "$pid" ]; then
    return 1
  fi
  return 0
}

restart_gateway() {
  log "GATEWAY_DOWN: restarting openclaw gateway"
  launchctl bootout gui/501/ai.openclaw.gateway 2>/dev/null
  sleep 2
  launchctl load /Users/ice/Library/LaunchAgents/ai.openclaw.gateway.plist 2>/dev/null
  sleep 5
  if check_gateway; then
    log "GATEWAY_RECOVERED: openclaw gateway restarted"
  else
    log "GATEWAY_STILL_DOWN: restart failed"
  fi
}

# Collect top processes for diagnostics (once per 30s cycle)
collect_top() {
  local top_cpu top_mem
  top_cpu=$(ps -eo pid,%cpu,rss,comm | sort -k2 -rn | head -8 | awk '{printf "[%s %.1f%% %dKB] %s | ", $1, $2, $3, $4}')
  top_mem=$(ps -eo pid,rss,comm | sort -k2 -rn | head -8 | awk '{printf "[%s %dKB %.1f%%] %s | ", $1, $2, $2/65536/100, $3}')
  log "TOP_CPU: $top_cpu"
}

log "STARTED: watchdog-monitor pid=$$"

proxy_fail_count=0
RESTART_LOCK="/tmp/watchdog_mihomo_restart.lock"
LOCK_AGE_MAX=90  # seconds to wait after a restart attempt before retrying

while true; do
  # Skip check if cooldown lock exists and is recent
  if [ -f "$RESTART_LOCK" ]; then
    lock_age=$(($(date +%s) - $(stat -f %m "$RESTART_LOCK" 2>/dev/null || echo 0)))
    if [ "$lock_age" -lt "$LOCK_AGE_MAX" ]; then
      sleep $CHECK_INTERVAL
      continue
    else
      # Cooldown expired, remove stale lock
      rm -f "$RESTART_LOCK"
      proxy_fail_count=0
    fi
  fi

  # Check proxy
  if ! check_proxy; then
    proxy_fail_count=$((proxy_fail_count + 1))
    if [ $proxy_fail_count -ge 2 ]; then
      touch "$RESTART_LOCK"  # Set lock before restart
      restart_mihomo
      # Keep lock for COOLDOWN period (prevents restart loop)
      # Lock will be removed when age > LOCK_AGE_MAX on next iteration
      log "PROXY_RESTART_DONE: next retry in ${LOCK_AGE_MAX}s (cooldown active)"
      sleep $CHECK_INTERVAL
      continue
    else
      log "PROXY_WARN: port ${PROXY_PORT} not listening (count=$proxy_fail_count, waiting for next check)"
    fi
  else
    proxy_fail_count=0
    # Proxy healthy — remove any stale lock immediately
    rm -f "$RESTART_LOCK"
  fi

  # Check gateway
  if ! check_gateway; then
    restart_gateway
  fi

  # Diagnostics every 10 minutes (every 20 cycles)
  if [ $((RANDOM % 20)) -eq 0 ]; then
    collect_top
  fi

  sleep $CHECK_INTERVAL
done
