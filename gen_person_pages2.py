#!/usr/bin/env python3
"""Generate person pages with linked concept tags"""
import json
from pathlib import Path
from collections import defaultdict

with open('/tmp/p2ptalk_processed.json') as f:
    data = json.load(f)

def concept_to_url(slug):
    """atom/Atom是什么 → ../atom/Atom是什么.html"""
    if '/' in slug:
        cat, name = slug.split('/', 1)
        return f'../{cat}/{name}.html'
    return f'../{slug}.html'

person_order = sorted(data['person_messages'].keys(), key=lambda p: -len(data['person_messages'][p]))

def get_sidebar(current):
    html = '<div class="sidebar"><h2>👥 参与者</h2>'
    for p in person_order:
        cls = 'active' if p == current else ''
        html += f'<a href="person_{p}.html" class="{cls}">{p} ({len(data["person_messages"][p])})</a>'
    html += '<h2>🗂️ 概念</h2><a href="index.html">← 概念总览</a></div>'
    return html

for person in person_order:
    msgs = data['person_messages'][person]
    concepts = data['person_concepts'].get(person, {})
    monthly = data['person_monthly'].get(person, {})
    
    monthly_sorted = sorted(monthly.keys())
    max_monthly = max(monthly.values()) if monthly else 1
    
    concept_bars = []
    if concepts:
        max_count = max(concepts.values())
        for concept, count in sorted(concepts.items(), key=lambda x: -x[1])[:10]:
            name = concept.split('/')[-1]
            pct = count / max_count
            concept_bars.append((name, count, pct, concept))
    
    questions = [m for m in msgs if '?' in m['body'][:300] or '？' in m['body'][:300]]
    latest_msgs = sorted(msgs, key=lambda x: x['date'], reverse=True)[:10]
    peak = max(monthly.keys(), key=lambda k: monthly[k]) if monthly else '-'
    
    timeline = ''
    for mo in monthly_sorted:
        c = monthly[mo]
        pct = c / max_monthly
        timeline += f'''<div class="tl-item"><div class="tl-month">{mo} <span class="tl-count">{c}条</span></div>
<div class="tl-bar"><div class="tl-fill" style="width:{pct*100}%"></div></div></div>'''
    
    bars_html = ''
    for name, count, pct, slug in concept_bars:
        url = concept_to_url(slug)
        bars_html += f'''<div class="bar-row"><div class="bar-label">{name}</div>
<div class="bar-track"><div class="bar-fill" style="width:{pct*100}%"></div></div>
<div class="bar-count">{count}</div></div>'''
    
    questions_html = ''
    for m in questions[:8]:
        body_short = m['body'][:200].replace('\n', ' ').replace('"', '')[:180]
        tags = ''.join(f'<a href="{concept_to_url(c)}" class="ctag">{c.split("/")[-1]}</a>' for c in m['concepts'][:3])
        questions_html += f'''<div class="msg-item"><div class="msg-date">{m['month']} · {m['subject'][:60]}</div>
<div class="msg-body">{body_short}...</div><div class="msg-tags">{tags}</div></div>'''
    
    msgs_html = ''
    for m in latest_msgs:
        body_short = m['body'][:200].replace('\n', ' ').replace('"', '')[:150]
        tags = ''.join(f'<a href="{concept_to_url(c)}" class="ctag">{c.split("/")[-1]}</a>' for c in m['concepts'][:3])
        msgs_html += f'''<div class="msg-item"><div class="msg-date">{m['month']} · {m['subject'][:80]}</div>
<div class="msg-body">{body_short}</div><div class="msg-tags">{tags}</div></div>'''
    
    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{person} — P2PTalk 人物</title>
<style>
:root {{--bg:#1a1a2e;--sb:#16213e;--acc:#e94560;--acc2:#0f3460;--txt:#eaeaea;--muted:#a0a0a0;--bd:#2a2a4a;}}
* {{box-sizing:border-box;margin:0;padding:0}}
html,body {{height:100%;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--txt)}}
body {{display:flex;flex-direction:column}}
.blink {{color:var(--acc);font-size:12px;margin-bottom:16px;display:inline-block;text-decoration:none}}
.blink:hover {{text-decoration:underline}}
header {{background:var(--sb);border-bottom:1px solid var(--bd);padding:12px 20px}}
header h1 {{font-size:18px;color:var(--acc);margin-bottom:4px}}
header .sub {{color:var(--muted);font-size:13px}}
.container {{display:flex;flex:1;overflow:hidden;height:calc(100vh - 52px)}}
.sidebar {{width:200px;background:var(--sb);border-right:1px solid var(--bd);overflow-y:auto;padding:16px 0;flex-shrink:0}}
.sidebar h2 {{font-size:10px;text-transform:uppercase;letter-spacing:1.2px;color:var(--muted);padding:10px 16px 4px}}
.sidebar a {{display:block;padding:4px 16px;color:var(--txt);text-decoration:none;font-size:12px;border-left:2px solid transparent}}
.sidebar a:hover {{background:var(--acc2);border-left-color:var(--acc)}}
.sidebar a.active {{background:var(--acc2);border-left-color:var(--acc)}}
.main {{flex:1;overflow-y:auto;padding:24px 32px;max-width:900px}}
.sec {{margin-bottom:36px}}
.sec h2 {{font-size:14px;color:var(--acc);margin-bottom:14px;border-bottom:1px solid var(--bd);padding-bottom:6px}}
.stats {{display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap}}
.stat {{background:var(--acc2);padding:10px 16px;border-radius:8px;border:1px solid var(--bd);min-width:80px}}
.stat .n {{font-size:22px;color:var(--acc);font-weight:600}}
.stat .l {{font-size:10px;color:var(--muted);text-transform:uppercase;margin-top:2px}}
.tl-item {{margin-bottom:14px}}
.tl-month {{font-size:11px;color:var(--muted);margin-bottom:4px}}
.tl-count {{color:var(--acc);margin-left:8px}}
.tl-bar {{height:6px;background:var(--acc2);border-radius:3px;overflow:hidden}}
.tl-fill {{height:100%;background:var(--acc);border-radius:3px}}
.bar-row {{display:flex;align-items:center;margin:6px 0;font-size:12px}}
.bar-label {{width:130px;color:var(--txt);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px}}
.bar-track {{flex:1;height:6px;background:var(--acc2);border-radius:3px;margin:0 8px;overflow:hidden}}
.bar-fill {{height:100%;background:var(--acc);border-radius:3px}}
.bar-count {{width:30px;text-align:right;color:var(--muted);font-size:10px}}
.msg-item {{background:var(--acc2);border:1px solid var(--bd);border-radius:8px;padding:10px 14px;margin-bottom:8px}}
.msg-date {{font-size:10px;color:var(--muted);margin-bottom:4px}}
.msg-body {{font-size:12px;color:var(--txt);line-height:1.6;max-height:72px;overflow:hidden}}
.msg-tags {{margin-top:6px;display:flex;flex-wrap:wrap;gap:4px}}
.ctag {{background:rgba(233,69,96,0.2);color:var(--acc);padding:1px 6px;border-radius:4px;font-size:10px;text-decoration:none}}
.ctag:hover {{background:rgba(233,69,96,0.4);text-decoration:none}}
</style>
</head>
<body>
<header>
  <a href="index.html" class="blink">← P2PTalk 总览</a>
  <h1>{person}</h1>
  <span class="sub">{len(msgs)} 条消息 · {len(monthly)} 个月活跃</span>
</header>
<div class="container">
{get_sidebar(person)}
<div class="main">
  <div class="sec">
    <div class="stats">
      <div class="stat"><div class="n">{len(msgs)}</div><div class="l">总消息</div></div>
      <div class="stat"><div class="n">{len(concepts)}</div><div class="l">涉及概念</div></div>
      <div class="stat"><div class="n">{peak}</div><div class="l">最活跃月</div></div>
      <div class="stat"><div class="n">{len(questions)}</div><div class="l">提问数</div></div>
    </div>
  </div>
  <div class="sec">
    <h2>📊 注意力分布（按月）</h2>
    <div class="timeline">{timeline}</div>
  </div>
  <div class="sec">
    <h2>🧠 关注概念分布</h2>
    <div class="bars">{bars_html}</div>
  </div>
  <div class="sec">
    <h2>❓ 提出过的问题 <span style="color:var(--muted);font-size:12px">({len(questions)}条)</span></h2>
    {questions_html}
  </div>
  <div class="sec">
    <h2>📬 最新消息</h2>
    {msgs_html}
  </div>
</div>
</div>
</body>
</html>'''
    
    out = Path(f'/tmp/p2ptalk-wiki/person_{person}.html')
    out.write_text(html, encoding='utf-8')
    print(f'Written: person_{person}.html ({len(msgs)} msgs, {len(concepts)} concepts, {len(questions)} questions)')
