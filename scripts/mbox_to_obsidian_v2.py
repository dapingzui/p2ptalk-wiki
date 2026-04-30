#!/usr/bin/env python3
"""
MBOX → Obsidian Vault (结构化版)
按「日期/主题/参与者」组织，不是扁平文件堆叠
"""

import mailbox
import email
import os
import re
import json
from email.header import decode_header
from datetime import datetime
from collections import defaultdict

SRC  = "/Users/ice/.openclaw/workspace/inbox/p2ptalk/topics.mbox"
DEST = "/Users/ice/.openclaw/workspace/inbox/p2ptalk/P2PTalk_Vault"
os.makedirs(DEST, exist_ok=True)

# ── Helpers ─────────────────────────────────────────────────────────────────

def decode_str(s):
    if s is None: return ""
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

def parse_date(date_str):
    if not date_str: return None
    date_str = re.sub(r'\s*\([^)]*\)\s*$', '', date_str.strip())
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except Exception:
        pass
    return None

def get_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    charset = part.get_content_charset() or "utf-8"
                    body = part.get_payload(decode=True).decode(charset, errors="replace")
                    break
                except Exception: pass
    else:
        try:
            charset = msg.get_content_charset() or "utf-8"
            body = msg.get_payload(decode=True).decode(charset, errors="replace")
        except Exception: pass
    # Strip signature
    lines = body.split("\n")
    clean = []
    for l in lines:
        if l.strip().startswith("-- ") and "----" in l: break
        clean.append(l)
    return "\n".join(clean).strip()

def slug(text):
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    return re.sub(r"\s+", "_", text.strip())[:50]

def classify_thread(subject):
    """Return (category, subfolder) based on subject keywords."""
    s = subject.lower()
    if any(k in s for k in ["会前同步", "会中同步", "会后", "会议同步"]):
        return "会议记录", "01_会议"
    if any(k in s for k in ["匹配会议", "匹配广播", "会议广播"]):
        return "匹配广播", "02_匹配广播"
    if any(k in s for k in ["atom", "atom的", "atom数据", "数据结构"]):
        return "Atom研究", "03_Atom"
    if any(k in s for k in ["广播", "nonce", "pow", "p2pmarket", "market"]):
        return "广播与市场", "04_广播市场"
    if any(k in s for k in ["最长链", "强制同步", "难度", "中本聪", "共识"]):
        return "共识机制", "05_共识"
    if any(k in s for k in ["领取计算", "请求计算", "计算结果", "返回计算"]):
        return "算力市场", "06_算力市场"
    if any(k in s for k in ["代码", "代码分享", "review"]):
        return "代码协作", "07_代码"
    if any(k in s for k in ["规则", "会议规则", "线下开会"]):
        return "规则设计", "08_规则"
    if any(k in s for k in ["私人", "私信", "private"]):
        return "私人通信", "09_私人"
    return "其他话题", "10_其他"

# ── Parse ────────────────────────────────────────────────────────────────────

print(f"Reading {SRC}...")
mbox = mailbox.mbox(SRC)
print(f"Total messages: {len(mbox)}")

threads = defaultdict(list)
for i, msg in enumerate(mbox):
    sub = decode_str(msg.get("Subject", ""))
    sub_clean = re.sub(r"^Re:\s*", "", sub).strip()
    sub_clean = re.sub(r"^回复：\s*", "", sub_clean).strip()
    threads[sub_clean].append((i, msg))

print(f"Unique threads: {len(threads)}")

# ── Build vault ─────────────────────────────────────────────────────────────

# Create folder structure
folders = {
    "01_会议":     "会议记录（会前/会中/会后同步）",
    "02_匹配广播": "匹配系统与会议广播",
    "03_Atom":     "Atom数据结构研究",
    "04_广播市场": "广播机制与P2P市场",
    "05_共识":     "共识机制（最长链/难度调整）",
    "06_算力市场": "算力请求与计算任务",
    "07_代码":     "代码协作与分享",
    "08_规则":     "协议规则设计",
    "09_私人":     "私人通信",
    "10_其他":     "其他话题",
}

for folder, desc in folders.items():
    os.makedirs(os.path.join(DEST, folder), exist_ok=True)

# Stats
stats = {k: [] for k in folders}
all_files = []

for thread_subj, msgs in threads.items():
    if not thread_subj:
        thread_subj = "(无标题)"

    cat, folder = classify_thread(thread_subj)

    # Sort messages by date
    def get_msg_date(m):
        d = parse_date(m[1].get("Date", ""))
        return d if d else datetime(2000, 1, 1)

    msgs_sorted = sorted(msgs, key=lambda m: get_msg_date(m))

    first_date = get_msg_date(msgs_sorted[0])
    last_date  = get_msg_date(msgs_sorted[-1])
    first_str  = first_date.strftime("%Y-%m-%d") if first_date else "unknown"
    last_str   = last_date.strftime("%Y-%m-%d")   if last_date else "unknown"
    first_dt   = first_date.strftime("%Y-%m-%d %H:%M") if first_date else "unknown"
    last_dt    = last_date.strftime("%Y-%m-%d %H:%M")  if last_date else "unknown"

    participants = list(set(decode_str(m.get("From", "")) for _, m in msgs_sorted))
    participant_names = [p.split("<")[0].strip().strip(">").strip() for p in participants]
    part_names = sorted(set(n for n in participant_names if n))

    # Filename: date + slug
    filename = f"{first_str}_{slug(thread_subj)}.md"
    filepath = os.path.join(DEST, folder, filename)
    counter = 1
    while os.path.exists(filepath):
        filename = f"{first_str}_{slug(thread_subj)[:30]}_{counter}.md"
        filepath = os.path.join(DEST, folder, filename)
        counter += 1

    # ── Build content ──
    lines = [
        "---",
        f"subject: \"{thread_subj}\"",
        f"category: {cat}",
        f"thread_size: {len(msgs_sorted)}",
        f"first_date: {first_dt}",
        f"last_date: {last_dt}",
        f"participants: {json.dumps(part_names, ensure_ascii=False)}",
        f"source: Google Groups p2ptalk",
        "created: \"{created}\"".replace("{created}", datetime.now().strftime("%Y-%m-%d")),
        "tags:",
        "  - p2ptalk",
        f"  - {slug(cat)}",
        "---",
        "",
        f"# {thread_subj}",
        "",
        f"**{len(msgs_sorted)} 条消息** · {first_str} → {last_str}",
        f"**分类：** {cat}",
        "",
        "## 参与者",
        " | ".join(part_names),
        "",
        "---",
        "",
        "## 消息时间线",
        "",
    ]

    for msg_num, (idx, msg) in enumerate(msgs_sorted):
        sender  = decode_str(msg.get("From", ""))
        date_v  = parse_date(msg.get("Date", ""))
        date_s  = date_v.strftime("%Y-%m-%d %H:%M") if date_v else "unknown"
        body    = get_body(msg)
        in_reply = decode_str(msg.get("In-Reply-To", ""))

        lines.append(f"### {msg_num+1}. {sender}  ·  {date_s}")
        if in_reply:
            lines.append(f"> ↩ 回复: `{in_reply[:60]}`")
        lines.append("")
        if body:
            body_lines = body.split("\n")[:100]
            body_text = "\n".join(body_lines)
            if len(body_text) > 6000:
                body_text = body_text[:6000] + "\n\n_(内容已截断)_"
            lines.append(body_text)
        else:
            lines.append("_(无正文内容)_")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    all_files.append({
        "subject": thread_subj,
        "filename": filepath.replace(DEST + "/", ""),
        "folder": folder,
        "category": cat,
        "count": len(msgs_sorted),
        "first": first_str,
        "last": last_str,
        "participants": part_names,
    })
    stats[folder].append(filepath)

# ── Write index per folder ───────────────────────────────────────────────────

for folder in folders:
    files = sorted([f for f in all_files if f["folder"] == folder],
                   key=lambda x: x["first"], reverse=True)
    idx_path = os.path.join(DEST, folder, "00_INDEX.md")
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"type: folder-index\n")
        f.write(f"folder: {folder}\n")
        f.write(f"desc: {folders[folder]}\n")
        f.write(f"threads: {len(files)}\n")
        f.write("tags:\n  - p2ptalk\n  - index\n")
        f.write("---\n\n")
        f.write(f"# {folders[folder]}\n\n")
        if files:
            f.write(f"共 **{len(files)}** 个线程\n\n")
            f.write("| 线程 | 消息数 | 时间 | 参与者 |\n")
            f.write("|---|---|---|---|\n")
            for fi in files:
                names = ", ".join(fi["participants"][:3])
                if len(fi["participants"]) > 3:
                    names += f" +{len(fi['participants'])-3}"
                f.write(f"| [{fi['subject']}]({fi['filename']}) | {fi['count']} | {fi['first']} | {names} |\n")
        else:
            f.write("（暂无内容）\n")

# ── Master index ────────────────────────────────────────────────────────────

all_files_sorted = sorted(all_files, key=lambda x: x["first"], reverse=True)
master_path = os.path.join(DEST, "00_MASTER_INDEX.md")
with open(master_path, "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write(f"type: master-index\n")
    f.write(f"total_threads: {len(all_files)}\n")
    f.write(f"total_messages: {len(mbox)}\n")
    f.write(f"date_range: {all_files_sorted[-1]['first']} ~ {all_files_sorted[0]['first']}\n")
    f.write("tags:\n  - p2ptalk\n  - index\n")
    f.write("---\n\n")
    f.write("# P2PTalk 总索引\n\n")
    f.write(f"共 **{len(all_files)}** 个线程，**{len(mbox)}** 条消息\n\n")
    for folder, desc in folders.items():
        count = len([x for x in all_files if x["folder"] == folder])
        f.write(f"## {desc}\n")
        f.write(f"[[{folder}/00_INDEX.md|{count} 个线程]]\n\n")
    f.write("---\n\n")
    f.write("## 所有线程（按时间倒序）\n\n")
    f.write("| 线程 | 分类 | 消息数 | 时间 | 参与者 |\n")
    f.write("|---|---|---|---|---|\n")
    for fi in all_files_sorted:
        names = ", ".join(fi["participants"][:2])
        if len(fi["participants"]) > 2:
            names += f" +{len(fi['participants'])-2}"
        f.write(f"| [{fi['subject']}]({fi['folder']}/{fi['filename']}) | {fi['category']} | {fi['count']} | {fi['first']} | {names} |\n")

# ── Participants index ─────────────────────────────────────────────────────

from collections import Counter
all_participants = Counter()
for fi in all_files:
    for p in fi["participants"]:
        all_participants[p] += fi["count"]

part_path = os.path.join(DEST, "00_PARTICIPANTS.md")
with open(part_path, "w", encoding="utf-8") as f:
    f.write("---\ntype: participants\ntags:\n  - p2ptalk\n  - participants\n---\n\n")
    f.write("# 参与者\n\n")
    f.write(f"共 **{len(all_participants)}** 位参与者\n\n")
    for name, count in all_participants.most_common():
        f.write(f"- **{name}** — {count} 条消息\n")

print(f"\n✅ 生成完毕")
print(f"📁 路径: {DEST}")
print(f"📄 主索引: {master_path}")
print()
print("各分类线程数:")
for folder, desc in folders.items():
    cnt = len([x for x in all_files if x["folder"] == folder])
    print(f"  {folder}: {cnt}")
