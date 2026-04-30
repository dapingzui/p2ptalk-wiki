#!/bin/bash
set -euo pipefail

# Ensure PATH includes homebrew (cron doesn't inherit shell profile)
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# Export lossless-claw summaries to markdown files for qmd indexing
# Runs periodically to keep qmd up-to-date with new conversations

LCM_DB="/Users/ice/.openclaw/lcm.db"
EXPORT_DIR="/Users/ice/.openclaw/history/lcm-exports"
QMD_BIN="/opt/homebrew/bin/qmd"

if [ ! -f "$LCM_DB" ]; then
  echo "[lcm-sync] lcm.db not found" >&2
  exit 1
fi

mkdir -p "$EXPORT_DIR"

# Export summaries grouped by conversation, with metadata
sqlite3 "$LCM_DB" <<'SQL' | while IFS='|' read -r conv_id session_id created_at; do
SELECT conversation_id, session_id, created_at FROM conversations;
SQL
  CONV_FILE="$EXPORT_DIR/conversation-${conv_id}.md"
  
  # Get all summaries for this conversation
  SUMMARIES=$(sqlite3 "$LCM_DB" "
    SELECT summary_id, kind, depth, created_at, content 
    FROM summaries 
    WHERE conversation_id = $conv_id 
    ORDER BY created_at ASC;
  " 2>/dev/null) || true

  if [ -z "$SUMMARIES" ]; then
    continue
  fi

  # Write conversation file
  {
    echo "# Conversation $conv_id"
    echo "**Session:** $session_id"
    echo "**Started:** $created_at"
    echo ""
    echo "---"
    echo ""
    
    echo "$SUMMARIES" | while IFS='|' read -r sum_id kind depth sum_created content; do
      echo "## Summary ($kind, depth $depth)"
      echo "*Created: $sum_created*"
      echo ""
      echo "$content"
      echo ""
      echo "---"
      echo ""
    done
  } > "$CONV_FILE"
done

# Also export recent raw messages (last 24h) that haven't been summarized yet
RECENT_FILE="$EXPORT_DIR/recent-messages.md"
{
  echo "# Recent Messages (unsummarized)"
  echo "*Exported: $(date -u +%Y-%m-%dT%H:%M:%SZ)*"
  echo ""
  
  sqlite3 "$LCM_DB" "
    SELECT m.message_id, m.role, m.created_at, 
           GROUP_CONCAT(mp.text_content, ' ') as content
    FROM messages m
    JOIN message_parts mp ON mp.message_id = m.message_id
    WHERE m.created_at > datetime('now', '-24 hours')
      AND mp.part_type = 'text'
      AND m.role IN ('user', 'assistant')
    GROUP BY m.message_id
    ORDER BY m.created_at ASC
    LIMIT 200;
  " | while IFS='|' read -r msg_id role created content; do
    # Skip heartbeat messages
    case "$content" in
      *HEARTBEAT*) continue ;;
      *"Read HEARTBEAT"*) continue ;;
    esac
    # Skip very short system noise
    if [ ${#content} -lt 5 ]; then continue; fi
    
    echo "### [$role] $created"
    echo "$content" | head -c 500
    echo ""
    echo ""
  done
} > "$RECENT_FILE"

# Count exported files
EXPORTED=$(ls "$EXPORT_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "[lcm-sync] exported $EXPORTED files to $EXPORT_DIR"

# ── Also sync to workspace qmd/ directory ─────────────────────────────
set +u  # avoid unbound variable errors in this section
WORKSPACE_QMD="/Users/ice/Document/QuantaAlpha/qmd/workspace-quantaalpha"
mkdir -p "$WORKSPACE_QMD"

# Sync all conversation exports to workspace qmd/
cp -f "$EXPORT_DIR"/conversation-*.md "$WORKSPACE_QMD/" 2>/dev/null || true
cp -f "$EXPORT_DIR"/recent-messages.md "$WORKSPACE_QMD/" 2>/dev/null || true

# Also update the workspace's own memory files into qmd/ (daily memory + MEMORY.md)
MEMORY_FILES=$(ls /Users/ice/Document/QuantaAlpha/memory/*.md 2>/dev/null || true)
for f in $MEMORY_FILES; do
  [ -f "$f" ] && cp -f "$f" "$WORKSPACE_QMD/" 2>/dev/null || true
done
[ -f /Users/ice/Document/QuantaAlpha/MEMORY.md ] && cp -f /Users/ice/Document/QuantaAlpha/MEMORY.md "$WORKSPACE_QMD/" 2>/dev/null || true

WS_SYNCED=$(ls "$WORKSPACE_QMD"/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "[lcm-sync] synced $WS_SYNCED files to workspace qmd/"

# Re-index qmd
export QMD_EMBED_MODEL="hf:Qwen/Qwen3-Embedding-0.6B-GGUF/Qwen3-Embedding-0.6B-Q8_0.gguf"
export XDG_CONFIG_HOME="/Users/ice/.openclaw/agents/main/qmd/xdg-config"
export XDG_CACHE_HOME="/Users/ice/.openclaw/agents/main/qmd/xdg-cache"
export XDG_DATA_HOME="/Users/ice/.openclaw/agents/main/qmd/xdg-data"

"$QMD_BIN" update 2>&1 | tail -5
"$QMD_BIN" embed 2>&1 | tail -3

echo "[lcm-sync] done at $(date)"
