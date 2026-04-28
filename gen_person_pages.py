#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict

with open('/tmp/p2ptalk_processed.json') as f:
    data = json.load(f)

# Build all person pages
person_order = sorted(data['person_messages'].keys(), key=lambda p: -len(data['person_messages'][p]))

# Sidebar HTML
def get_sidebar(current_person):
    sidebar = '<div class="sidebar"><h2>👥 参与者</h2>'
    for p in person_order:
        cls = 'active' if p == current_person else ''
        sidebar += f'<a href="person_{p}.html" class="{cls}">{p} ({len(data["person_messages"][p])})</a>'
    sidebar += '<h2>🗂️ 概念</h2><a href="index.html">← 概念总览</a></div>'
    return sidebar

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
            concept_name = concept.split('/')[-1]
            pct = count / max_count
            concept_bars.append((concept_name, count, pct, concept))
    
    questions = [m for m in msgs if '?' in m['body'][:300] or '？' in m['body'][:300]]
    latest_msgs = sorted(msgs, key=lambda x: x['date'], reverse=True)[:10]
    
    # Build monthly timeline
    timeline_html = ''
    for mo in monthly_sorted:
        count = monthly[mo]
        pct = count / max_monthly
        timeline_html += f'''<div class="timeline-item">
  <div class="timeline-month">{mo} <span class="timeline-count">{count}条</span></div>
  <div class="bar-track" style="width:200px"><div class="bar-fill" style="width:{pct*100}%"></div></div>
</div>'''
    
    # Concept bars
    concept_bars_html = ''
    for concept_name, count, pct, concept_slug in concept_bars:
        concept_bars_html += f'''<div class="bar-row">
  <div class="bar-label">{concept_name}</div>
  <div class="bar-track"><div class="bar-fill" style="width:{pct*100}%"></div></div>
  <div class="bar-count">{count}</div>
</div>'''
    
    # Questions
    questions_html = ''
    for m in questions[:8]:
        body_short = m['body'][:250].replace('\n', ' ').replace('"', '')[:200]
        concept_tags = ''.join(f'<span class="msg-concept-tag">{c.split("/")[-1]}</span>' for c in m['concepts'][:3])
        questions_html += f'''<div class="msg-item">
  <div class="msg-date">{m['month']} · {m['subject'][:60]}</div>
  <div class="msg-body">{body_short}...</div>
  <div class="msg-concepts">{concept_tags}</div>
</div>'''
    
    # Latest messages
    msgs_html = ''
    for m in latest_msgs:
        body_short = m['body'][:300].replace('\n', ' ').replace('"', '')[:200]
        concept_tags = ''.join(f'<span class="msg-concept-tag">{c.split("/")[-1]}</span>' for c in m['concepts'][:3])
        msgs_html += f'''<li class="msg-item">
  <div class="msg-date">{m['month']} · {m['subject'][:80]}</div>
  <div class="msg-body">{body_short}</div>
  <div class="msg-concepts">{concept_tags}</div>
</li>'''
    
    peak_month = max(monthly.keys(), key=lambda k: monthly[k]) if monthly else '-'
    
    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{person} — P2PTalk 人物</title>
<style>
:root {{
  --bg: #1a1a2e;
  --sidebar-bg: #16213e;
  --accent: #e94560;
  --accent2: #0f3460;
  --text: #eaeaea;
  --text-muted: #a0a0a0;
  --border: #2a2a4a;
  --code-bg: #0d1117;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ height: 100%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }}
body {{ display: flex; flex-direction: column; }}
.back-link {{ color: var(--accent); font-size: 12px; margin-bottom: 16px; display: inline-block; text-decoration: none; }}
.back-link:hover {{ text-decoration: underline; }}
header {{ background: var(--sidebar-bg); border-bottom: 1px solid var(--border); padding: 12px 20px; }}
header h1 {{ font-size: 18px; color: var(--accent); margin-bottom: 4px; }}
header .subtitle {{ color: var(--text-muted); font-size: 13px; }}
.container {{ display: flex; flex: 1; overflow: hidden; height: calc(100vh - 52px); }}
.sidebar {{ width: 200px; background: var(--sidebar-bg); border-right: 1px solid var(--border); overflow-y: auto; padding: 16px 0; flex-shrink: 0; }}
.sidebar h2 {{ font-size: 10px; text-transform: uppercase; letter-spacing: 1.2px; color: var(--text-muted); padding: 10px 16px 4px; }}
.sidebar a {{ display: block; padding: 4px 16px; color: var(--text); text-decoration: none; font-size: 12px; border-left: 2px solid transparent; }}
.sidebar a:hover {{ background: var(--accent2); border-left-color: var(--accent); }}
.sidebar a.active {{ background: var(--accent2); border-left-color: var(--accent); }}
.main {{ flex: 1; overflow-y: auto; padding: 24px 32px; max-width: 900px; }}
.section {{ margin-bottom: 36px; }}
.section h2 {{ font-size: 14px; color: var(--accent); margin-bottom: 14px; border-bottom: 1px solid var(--border); padding-bottom: 6px; }}
.stat-row {{ display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }}
.stat {{ background: var(--accent2); padding: 10px 16px; border-radius: 8px; border: 1px solid var(--border); min-width: 80px; }}
.stat .num {{ font-size: 22px; color: var(--accent); font-weight: 600; }}
.stat .label {{ font-size: 10px; color: var(--text-muted); text-transform: uppercase; margin-top: 2px; }}
.bar-chart {{ margin: 12px 0; }}
.bar-row {{ display: flex; align-items: center; margin: 6px 0; font-size: 12px; }}
.bar-label {{ width: 130px; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 11px; }}
.bar-track {{ flex: 1; height: 6px; background: var(--accent2); border-radius: 3px; margin: 0 8px; overflow: hidden; }}
.bar-fill {{ height: 100%; background: var(--accent); border-radius: 3px; transition: width 0.3s; }}
.bar-count {{ width: 30px; text-align: right; color: var(--text-muted); font-size: 10px; }}
.msg-list {{ list-style: none; }}
.msg-item {{ background: var(--accent2); border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; }}
.msg-date {{ font-size: 10px; color: var(--text-muted); margin-bottom: 4px; }}
.msg-subject {{ font-size: 12px; color: var(--accent); margin-bottom: 6px; }}
.msg-body {{ font-size: 12px; color: var(--text); line-height: 1.6; max-height: 80px; overflow: hidden; }}
.msg-concepts {{ margin-top: 6px; }}
.msg-concept-tag {{ background: rgba(233,69,96,0.2); color: var(--accent); padding: 1px 6px; border-radius: 4px; font-size: 10px; margin-right: 4px; display: inline-block; }}
.question-badge {{ background: var(--accent); color: #fff; padding: 1px 6px; border-radius: 4px; font-size: 10px; margin-left: 6px; }}
.timeline {{ margin-top: 12px; }}
.timeline-item {{ margin-bottom: 16px; padding-left: 8px; border-left: 2px solid var(--border); position: relative; }}
.timeline-item::before {{ content: ''; position: absolute; left: -5px; top: 2px; width: 8px; height: 8px; background: var(--accent); border-radius: 50%; }}
.timeline-month {{ font-size: 11px; color: var(--text-muted); margin-bottom: 4px; }}
.timeline-count {{ color: var(--accent); margin-left: 8px; }}
</style>
</head>
<body>
<header>
  <a href="index.html" class="back-link">← P2PTalk 总览</a>
  <h1>{person}</h1>
  <span class="subtitle">{len(msgs)} 条消息 · {len(monthly)} 个月活跃</span>
</header>
<div class="container">
{get_sidebar(person)}
<div class="main">
  <div class="section">
    <div class="stat-row">
      <div class="stat"><div class="num">{len(msgs)}</div><div class="label">总消息</div></div>
      <div class="stat"><div class="num">{len(concepts)}</div><div class="label">涉及概念</div></div>
      <div class="stat"><div class="num">{peak_month}</div><div class="label">最活跃月</div></div>
      <div class="stat"><div class="num">{len(questions)}</div><div class="label">提问数</div></div>
    </div>
  </div>

  <div class="section">
    <h2>📊 注意力分布（按月）</h2>
    <div class="timeline">{timeline_html}</div>
  </div>

  <div class="section">
    <h2>🧠 关注概念分布</h2>
    <div class="bar-chart">{concept_bars_html}</div>
  </div>

  <div class="section">
    <h2>❓ 提出过的问题 <span style="color:var(--text-muted);font-size:12px">({len(questions)}条)</span></h2>
    {questions_html}
  </div>

  <div class="section">
    <h2>📬 最新消息</h2>
    <ul class="msg-list">{msgs_html}</ul>
  </div>
</div>
</div>
</body>
</html>'''
    
    out_path = Path(f'/tmp/p2ptalk-wiki/person_{person}.html')
    out_path.write_text(html, encoding='utf-8')
    print(f'Written: person_{person}.html ({len(msgs)} msgs, {len(concepts)} concepts)')

# Update index to add person link
index_html = Path('/tmp/p2ptalk-wiki/index.html').read_text(encoding='utf-8')

# Add person overview section before the concept cards
person_link = f'<a href="person_{person_order[0]}.html" class="person-link">{person_order[0]}</a>'

# Find a good insertion point - after the stats div
insert_after = '<div class="page">'
stats_line = f'''
<div class="person-intro">
  <h2>👥 人物视角</h2>
  <div class="person-links">'''
for p in person_order:
    stats_line += f'<a href="person_{p}.html" class="person-tag">{p}</a>'
stats_line += '</div></div>'

index_html = index_html.replace(insert_after, insert_after + stats_line, 1)

# Add CSS for person links
css_addition = '''
.person-intro { background: var(--accent2); border-radius: 12px; padding: 16px 20px; margin: 20px 0; border: 1px solid var(--border); }
.person-intro h2 { font-size: 14px; color: var(--accent); margin-bottom: 12px; }
.person-links { display: flex; flex-wrap: wrap; gap: 8px; }
.person-tag { background: rgba(233,69,96,0.15); color: var(--accent); padding: 5px 12px; border-radius: 16px; font-size: 12px; text-decoration: none; border: 1px solid rgba(233,69,96,0.3); transition: all 0.2s; }
.person-tag:hover { background: rgba(233,69,96,0.3); text-decoration: none; }'''

old_end = '.page a.wiki-link:hover'
if old_end in index_html:
    index_html = index_html.replace(old_end, old_end + css_addition)
else:
    # Find a safe insertion point in CSS
    idx = index_html.find('.page h2 {')
    if idx > 0:
        index_html = index_html[:idx] + css_addition + '\n' + index_html[idx:]

Path('/tmp/p2ptalk-wiki/index.html').write_text(index_html, encoding='utf-8')
print('\nUpdated index.html with person links')

print('\n=== ALL DONE ===')
for p in person_order:
    print(f'  {p}: {len(data["person_messages"][p])} msgs')
