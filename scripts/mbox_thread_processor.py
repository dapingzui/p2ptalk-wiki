#!/usr/bin/env python3
"""
MBOX Thread → Knowledge Graph Ingest
For each thread: extract key insights, generate summary page, update index.
"""
import os, re, sys
from collections import defaultdict

VAULT = "/Users/ice/.openclaw/workspace/inbox/p2ptalk/P2PTalk_Vault"
KG = "/Users/ice/.openclaw/workspace/inbox/p2ptalk/KnowledgeGraph"
THREADS = os.path.join(KG, "threads")

# Folder name mapping
FOLDER_MAP = {
    "01_会议": "01_会议",
    "02_匹配广播": "02_匹配广播",
    "03_Atom": "03_Atom",
    "04_广播市场": "04_广播市场",
    "05_共识": "05_共识",
    "06_算力市场": "06_算力市场",
    "07_代码": "07_代码",
    "08_规则": "08_规则",
    "09_私人": "09_私人",
    "10_其他": "10_其他",
}

def slug(text):
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    text = re.sub(r"\s+", "_", text.strip())[:50]
    return text

def extract_insights(content):
    """Extract key insights from thread content."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', content)
    text = re.sub(r'\s+', ' ', text)
    
    # Extract quoted text (between > markers)
    quotes = re.findall(r'^> (.+?)$', content, re.MULTILINE)
    
    # Extract key technical terms
    terms = []
    for term in ['atom', 'Atom', 'nonce', 'POW', '女巫', '泛洪', '中间会面', 
                  '谓词', 'Bitcoin', '比特币', '最长链', '难度', 'p2pmarket',
                  'throughRate', 'links_out', 'atoms_in', 'atoms_out',
                  'hashcash', '中本聪', '闪电贷', 'agent', 'AI']:
        if term.lower() in content.lower():
            terms.append(term)
    
    # Extract key statements (longer Chinese sentences)
    sentences = re.findall(r'[\u4e00-\u9fff][^\n。！？]{20,200}[。！？]', content)
    
    return {
        'terms': list(set(terms)),
        'quotes': quotes[:5],
        'sentences': sentences[:10]
    }

def get_body_text(content):
    """Strip HTML and metadata, get clean body."""
    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]
    
    # Remove message timeline markers
    content = re.sub(r'^## 参与者.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^## 消息时间线.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^### \d+\..*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^> ↩.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^---.*$', '', content, flags=re.MULTILINE)
    
    # Remove HTML
    text = re.sub(r'<[^>]+>', ' ', content)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'You received this message because.*$', '', text)
    text = re.sub(r'To unsubscribe from this group.*$', '', text)
    text = re.sub(r'To view this discussion visit.*$', '', text)
    
    return text.strip()

def process_all_threads():
    """Process all 74 threads and generate summary pages."""
    all_threads = []
    
    for folder in sorted(os.listdir(VAULT)):
        fp = os.path.join(VAULT, folder)
        if not os.path.isdir(fp) or folder.startswith('.'): continue
        
        folder_label = FOLDER_MAP.get(folder, folder)
        target_folder = os.path.join(THREADS, folder)
        os.makedirs(target_folder, exist_ok=True)
        
        for f in sorted(os.listdir(fp)):
            if not f.endswith('.md') or f.startswith('00_'): continue
            path = os.path.join(fp, f)
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            
            # Parse frontmatter
            frontmatter = {}
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    for line in parts[1].strip().split('\n'):
                        if ':' in line:
                            k, v = line.split(':', 1)
                            frontmatter[k.strip()] = v.strip().strip('"').strip("'")
            
            subject = frontmatter.get('subject', f.replace('.md',''))
            thread_size = frontmatter.get('thread_size', '?')
            first_date = frontmatter.get('first_date', '')
            last_date = frontmatter.get('last_date', '')
            participants_raw = frontmatter.get('participants', '[]')
            
            # Parse participants
            participants = re.findall(r'"([^"]+)"', participants_raw)
            
            # Extract sender names from content
            senders = re.findall(r'### \d+\. (.+?) <', content)
            senders += re.findall(r'From: (.+?) <', content)
            senders = list(set([s.strip() for s in senders if s.strip()]))
            
            # Get insights
            insights = extract_insights(content)
            body_text = get_body_text(content)
            
            # Generate summary page
            slug_name = slug(f.replace('.md', ''))
            
            summary_page = f"""---
type: thread-summary
subject: "{subject}"
folder: "{folder_label}"
thread_size: {thread_size}
first_date: "{first_date}"
last_date: "{last_date}"
participants: {json.dumps(participants) if participants else json.dumps(senders)}
tags: [p2ptalk, {folder_label}]
related_concepts: {json.dumps(insights['terms'][:8])}
created: 2026-04-20
source: p2ptalk/{folder_label}
---

# {subject}

**{thread_size}条消息** · {first_date[:10]} → {last_date[:10]}
**分类：** {folder_label}

## 参与者
{(' | '.join(participants)) if participants else (' | '.join(senders[:5]))}

## 关键概念
{', '.join([f'[[{t}]]' for t in insights['terms'][:8]]) if insights['terms'] else '（无特定概念）'}

---

## 关键讨论

"""
            
            # Add key sentences as bullet points
            unique_sentences = []
            seen = set()
            for s in insights['sentences']:
                clean = s.strip()[:200]
                if clean not in seen and len(clean) > 20:
                    seen.add(clean)
                    unique_sentences.append(clean)
            
            if unique_sentences:
                for s in unique_sentences[:8]:
                    summary_page += f"- {s}\n"
            else:
                # Fallback: use preview text
                preview = ' '.join(body_text.split())[:500]
                if preview:
                    summary_page += f"> {preview[:300]}...\n"
            
            summary_page += f"""

---

## 原始线程

> 此页为知识图谱摘要，原始线程存档：
> `P2PTalk_Vault/{folder_label}/{f}`

"""
            
            # Write summary page
            out_name = f"{first_date[:10]}_{slug_name}.md" if first_date else slug_name
            out_path = os.path.join(target_folder, out_name)
            with open(out_path, 'w', encoding='utf-8') as fh:
                fh.write(summary_page)
            
            all_threads.append({
                'folder': folder_label,
                'subject': subject,
                'path': out_path,
                'terms': insights['terms'],
                'size': thread_size,
                'date': first_date[:10] if first_date else 'unknown'
            })
    
    return all_threads

import json
if __name__ == "__main__":
    threads = process_all_threads()
    print(f"Processed {len(threads)} threads")
    for t in threads[:10]:
        print(f"  [{t['folder']}] {t['subject'][:50]} - {t['terms'][:3]}")
