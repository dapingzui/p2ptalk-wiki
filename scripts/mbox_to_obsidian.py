#!/usr/bin/env python3
"""
MBOX → Obsidian 转换脚本
将 Google Groups mbox 导出转为 Obsidian vault 格式
"""

import mailbox
import email
import os
import re
import json
from email.header import decode_header
from datetime import datetime
from collections import defaultdict

SRC = "/Users/ice/.openclaw/workspace/inbox/p2ptalk/topics.mbox"
OUT = "/Users/ice/.openclaw/workspace/inbox/p2ptalk/ObsidianVault"
os.makedirs(OUT, exist_ok=True)

def decode_str(s):
    if s is None:
        return ""
    try:
        parts = decode_header(s)
        result = []
        for part, enc in parts:
            if isinstance(part, bytes):
                result.append(part.decode(enc or "utf-8", errors="replace"))
            elif isinstance(part, str):
                result.append(part)
        return "".join(result)
    except Exception:
        return str(s)

def get_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                try:
                    charset = part.get_content_charset() or "utf-8"
                    body = part.get_payload(decode=True).decode(charset, errors="replace")
                    break
                except Exception:
                    pass
    else:
        try:
            charset = msg.get_content_charset() or "utf-8"
            body = msg.get_payload(decode=True).decode(charset, errors="replace")
        except Exception:
            pass
    # Strip signature lines
    lines = body.split("\n")
    clean = []
    for l in lines:
        if l.strip().startswith("-- ") and "----" in l:
            break
        clean.append(l)
    body = "\n".join(clean).strip()
    return body

def parse_date(date_str):
    """Parse email date string (RFC 2822)."""
    if not date_str:
        return datetime.now()
    # Remove extra timezone annotation in parens like (PST)
    date_str = date_str.strip()
    date_str = re.sub(r'\s*\([^)]*\)\s*$', '', date_str).strip()
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%d %b %Y %H:%M:%S %z",
        "%a %b %d %H:%M:%S %Y %z",
        "%a, %d %b %Y %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except Exception:
            pass
    # Fallback: try to parse with email.utils
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except Exception:
        pass
    return datetime.now()

def slug(text):
    """Make safe filename."""
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    text = text.strip()[:60]
    return re.sub(r"\s+", "_", text)

def extract_email_address(sender):
    """Extract email address from 'Name <email>' format."""
    match = re.search(r"<(.+?)>", sender)
    if match:
        return match.group(1)
    return sender

# ─── Parse mbox ────────────────────────────────────────────────────────────────

print(f"Reading {SRC}...")
mbox = mailbox.mbox(SRC)
print(f"Total messages: {len(mbox)}")

# Group messages by thread (Subject)
threads = defaultdict(list)
for i, msg in enumerate(mbox):
    sub = decode_str(msg.get("Subject", ""))
    sub_clean = re.sub(r"^Re:\s*", "", sub).strip()
    sub_clean = re.sub(r"^回复：\s*", "", sub_clean).strip()
    threads[sub_clean].append((i, msg))

print(f"Unique threads: {len(threads)}")

# ─── Generate Obsidian notes ─────────────────────────────────────────────────

# Build index
vault_index = []
created_files = []

for thread_subj, msgs in sorted(threads.items(), key=lambda x: -len(x[1])):
    if not thread_subj:
        thread_subj = "(无标题)"

    # File name: first 50 chars of subject, with reply count
    filename = f"{len(msgs)}-_{slug(thread_subj)}.md"
    filepath = os.path.join(OUT, filename)
    
    # Avoid filename collisions
    counter = 1
    while os.path.exists(filepath):
        filename = f"{len(msgs)}-_{slug(thread_subj)[:40]}_{counter}.md"
        filepath = os.path.join(OUT, filename)
        counter += 1

    # Frontmost message (oldest)
    first_date = parse_date(msgs[0][1].get("Date", "")).strftime("%Y-%m-%d %H:%M")
    last_date = parse_date(msgs[-1][1].get("Date", "")).strftime("%Y-%m-%d %H:%M")
    
    # All participants
    participants = list(set(decode_str(m.get("From", "")) for _, m in msgs))
    
    # Build content
    lines = [
        "---",
        f"subject: {thread_subj}",
        f"thread_size: {len(msgs)}",
        f"first_date: {first_date}",
        f"last_date: {last_date}",
        f"participants: {json.dumps(participants, ensure_ascii=False)}",
        f"source: Google Groups p2ptalk",
        "tags:",
        "  - p2ptalk",
        "  - thread",
        "---",
        "",
        f"# {thread_subj}",
        "",
        f"**{len(msgs)} 条消息** · {first_date} → {last_date}",
        "",
        "## 参与者",
    ]
    for p in sorted(participants):
        lines.append(f"- {p}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 消息列表")
    lines.append("")

    for msg_num, (idx, msg) in enumerate(msgs):
        sender = decode_str(msg.get("From", ""))
        date = parse_date(msg.get("Date", "")).strftime("%Y-%m-%d %H:%M")
        body = get_body(msg)
        in_reply_to = decode_str(msg.get("In-Reply-To", ""))
        
        # Header
        lines.append(f"### [{msg_num+1}] {sender}")
        lines.append(f"> {date}" + (f" · 回复 #{in_reply_to[:30]}" if in_reply_to else ""))
        lines.append("")
        
        # Body (trim to reasonable length)
        if body:
            body_lines = body.split("\n")[:80]  # max 80 lines per message
            body = "\n".join(body_lines)
            if len(body) > 5000:
                body = body[:5000] + "\n\n_(内容已截断)_"
            lines.append(body)
        else:
            lines.append("_(无正文内容)_")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    created_files.append(filepath)
    vault_index.append({
        "subject": thread_subj,
        "filename": os.path.basename(filepath),
        "message_count": len(msgs),
        "first_date": first_date,
        "last_date": last_date,
        "participants": len(participants),
    })

# ─── Write index ───────────────────────────────────────────────────────────────

vault_index.sort(key=lambda x: x["last_date"], reverse=True)
index_path = os.path.join(OUT, "00_INDEX.md")
with open(index_path, "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write("type: index\n")
    f.write(f"created: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    f.write(f"total_threads: {len(vault_index)}\n")
    f.write(f"total_messages: {len(mbox)}\n")
    f.write("tags:\n  - p2ptalk\n  - index\n")
    f.write("---\n\n")
    f.write("# P2PTalk 邮件组索引\n\n")
    f.write(f"共 **{len(vault_index)} 个线程**，{len(mbox)} 条消息\n\n")
    f.write("| 线程 | 消息数 | 参与者 | 时间范围 |\n")
    f.write("|---|---|---|---|\n")
    for item in vault_index:
        f.write(f"| [{item['subject']}]({item['filename']}) | {item['message_count']} | {item['participants']} | {item['first_date']} → {item['last_date']} |\n")

print(f"\n✅ 生成了 {len(created_files)} 个 Obsidian 笔记")
print(f"📁 输出目录: {OUT}")
print(f"📄 索引文件: {index_path}")

# Print top 10 by message count
print("\nTop 10 活跃线程:")
for item in vault_index[:10]:
    print(f"  {item['message_count']:3}x [{item['subject']}]")
