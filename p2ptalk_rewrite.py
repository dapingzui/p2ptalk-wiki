#!/usr/bin/env python3
"""Rewrite P2PTalk person pages: replace old ita-person format with new card format."""

import json, re
from pathlib import Path

with open('/tmp/p2ptalk_processed.json') as f:
    data = json.load(f)

all_messages = data['all_messages']
person_monthly = data['person_monthly']
person_concepts = data['person_concepts']
all_concepts_in_messages = data.get('all_concepts_in_messages', {})

# Build co-occurrence map
person_people = {}
for msg in all_messages:
    p = msg['person']
    for c in msg.get('concepts', []):
        if not c or c not in all_concepts_in_messages:
            continue
        for m in all_concepts_in_messages[c]:
            if m['person'] != p:
                person_people.setdefault(p, {})
                person_people[p].setdefault(m['person'], 0)
                person_people[p][m['person']] += 1

def get_shared(p1, p2, n=3):
    c1 = set(person_concepts.get(p1, {}).keys())
    c2 = set(person_concepts.get(p2, {}).keys())
    shared = c1 & c2
    if not shared:
        return []
    return sorted(shared, key=lambda c: person_concepts.get(p1, {}).get(c, 0) + person_concepts.get(p2, {}).get(c, 0), reverse=True)[:n]

def last_month(person):
    dates = sorted([m['date'] for m in all_messages if m['person'] == person], reverse=True)
    return dates[0][:7] if dates else ''

_CHINESE_TO_SLUG = {
    '叶鹏': 'YePeng', '文博': 'WenBo', '沄涣': 'YunHuan',
    '矢孤': 'ShiGu', '胥亚朋': 'XuYapeng', '雷雷': 'LeiLei',
}
def slug(name):
    return _CHINESE_TO_SLUG.get(name, name.replace(' ', '_'))

def decode_subject(subject):
    import email.header
    if not subject or '=' not in subject:
        return subject
    s = re.sub(r'\r?\n[ =]*\?=', '?', subject)
    s = re.sub(r'=\?$', '?=', s)
    try:
        parts = email.header.decode_header(s)
        result = []
        for part, charset in parts:
            if isinstance(part, bytes):
                charset = charset or 'utf-8'
                try: result.append(part.decode(charset))
                except: result.append(part.decode('utf-8', errors='replace'))
            else: result.append(part)
        return ''.join(result)
    except:
        return subject

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def build_timeline(person):
    monthly = person_monthly.get(person, {})
    if not monthly:
        return ''
    months = sorted(monthly.keys(), reverse=True)
    max_c = max(monthly.values())
    html = '<div class="person-timeline">\n'
    for month in months[:12]:
        c = monthly[month]
        y, m = month.split('-')
        w = max(4, int(c / max_c * 100))
        html += f'<div class="ptl-month">\n'
        html += f'<div class="ptl-month-label"><span class="ptl-dot"></span>{y}年{m}月<span class="ptl-year">{c}条</span></div>\n'
        html += f'<div class="ptl-bar"><div class="ptl-bar-fill" style="width:{w}%;"></div></div>\n'
        for msg in [m for m in all_messages if m.get('person') == person and m.get('month') == month][:5]:
            subj = decode_subject(msg.get('subject', '（无主题）'))
            if len(subj) > 60: subj = subj[:60] + '…'
            tags = ''.join(f'<span class="ptl-tag">{esc(t.split("/")[-1])}</span>' for t in msg.get('concepts', [])[:3])
            date = msg.get('date', '')[:10]
            q = '❓ ' if msg.get('is_question') else ''
            body = msg.get('body_preview', '')
            exp = f'<span class="ptl-expand">▼ 展开</span><div class="ptl-expanded">{esc(body)}</div>' if body else ''
            html += f'<div class="ptl-msg">{q}<div class="ptl-msg-subject">{esc(subj)}</div><div class="ptl-msg-meta">{tags}<span>{date}</span></div>{exp}</div>\n'
        if len([m for m in all_messages if m.get('person') == person and m.get('month') == month]) > 5:
            html += f'<div style="font-size:11px;color:var(--text-muted);padding-left:10px;">还有更多消息</div>\n'
        html += '</div>\n'
    html += '</div>\n'
    return html

def build_cards(person):
    if not person_people.get(person):
        return ''
    people = sorted(person_people[person].items(), key=lambda x: x[1], reverse=True)[:12]
    cards = ''
    for other, count in people:
        shared = get_shared(person, other)
        last = last_month(other)
        tags = ''.join(f'<span class="ip-tag">{esc(t.split("/")[-1])}</span>' for t in shared) if shared else '<span class="ip-tag-empty">共同概念</span>'
        cards += f'''<a href="person_{slug(other)}.html" class="ip-card">
  <div class="ip-card-name">👤 {esc(other)}</div>
  <div class="ip-card-msgs">{count}条消息</div>
  <div class="ip-card-tags">{tags}</div>
  <div class="ip-card-date">📅 {last}</div>
</a>'''
    return f'''<section class="interaction-section">
<h2>💬 与{person}的对话</h2>
<div class="ip-grid">{cards}</div>
</section>'''

# NEW clean CSS
NEW_CSS = """.person-timeline{margin:16px 0 24px 0;}
.ptl-month{margin-bottom:18px;}
.ptl-month-label{display:flex;align-items:center;gap:8px;margin-bottom:8px;color:var(--accent);font-size:12px;font-weight:600;}
.ptl-dot{width:8px;height:8px;border-radius:50%;background:var(--accent);flex-shrink:0;}
.ptl-year{font-size:10px;color:var(--text-muted);background:rgba(255,255,255,0.08);padding:1px 5px;border-radius:8px;font-weight:400;}
.ptl-bar{display:flex;gap:3px;margin:6px 0 10px 16px;align-items:flex-end;}
.ptl-bar-fill{height:20px;background:var(--accent);border-radius:2px;opacity:0.7;min-width:4px;flex:1;}
.ptl-msg{margin-bottom:10px;padding:6px 10px;background:rgba(255,255,255,0.03);border-radius:6px;border-left:2px solid var(--accent);}
.ptl-msg-subject{font-size:12px;color:var(--text);margin-bottom:3px;}
.ptl-msg-meta{font-size:10px;color:var(--text-muted);display:flex;gap:8px;flex-wrap:wrap;}
.ptl-expand{display:inline-block;font-size:10px;color:var(--accent);cursor:pointer;margin-top:3px;}
.ptl-expanded{display:none;margin-top:6px;padding:6px 8px;background:rgba(0,0,0,0.2);border-radius:4px;font-size:11px;color:var(--text-muted);line-height:1.5;}
.ptl-tag{display:inline-block;font-size:9px;padding:1px 5px;background:rgba(255,255,255,0.1);border-radius:3px;margin-right:3px;color:var(--text-muted);}
.interaction-section{padding:20px;background:#fafafa;border-radius:12px;margin:20px 0}
.interaction-section h2{font-size:18px;margin:0 0 16px 0;color:#333}
.ip-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px}
.ip-card{display:flex;flex-direction:column;gap:6px;padding:14px;border:1px solid #e0e0e0;border-radius:10px;background:#fff;text-decoration:none;color:#333;transition:all .2s}
.ip-card:hover{border-color:#4CAF50;box-shadow:0 2px 8px rgba(0,0,0,.08);transform:translateY(-1px)}
.ip-card-name{font-weight:600;font-size:15px}
.ip-card-msgs{font-size:12px;color:#888}
.ip-card-tags{display:flex;flex-wrap:wrap;gap:4px;margin-top:2px}
.ip-tag{font-size:11px;padding:2px 6px;background:#e8f5e9;color:#2e7d32;border-radius:4px}
.ip-tag-empty{font-size:11px;padding:2px 6px;background:#f5f5f5;color:#999;border-radius:4px}
.ip-card-date{font-size:11px;color:#aaa;margin-top:auto}"""

# OLD CSS classes to strip (they appear as .classname{...} in <style>)
OLD_CSS_CLASSES = [
    'ita-person', 'ita-person-name', 'ita-person-count', 'ita-toggle',
    'ita-detail', 'ita-concepts', 'ita-concept-tag', 'ita-count',
    'interaction-section', '.ita-', 'ita-'
]

REPO = Path('/tmp/p2ptalk-wiki')

for html_file in sorted(REPO.glob('person_*.html')):
    content = html_file.read_text(encoding='utf-8')
    name = html_file.stem.replace('person_', '')
    # Find person name from h1
    m = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
    if not m:
        continue
    person = m.group(1).strip()

    # Step 1: Strip ALL old CSS rules (they look like .classname{...} in <style> tags)
    def remove_old_css(text):
        for cls in OLD_CSS_CLASSES:
            # Remove entire CSS rule blocks like .ita-person{...} or .interaction-section{...}
            pattern = re.compile(r'\.' + re.escape(cls) + r'\{[^}]+\}', re.DOTALL)
            text = pattern.sub('', text)
            # Also remove any leftover property lines referencing the old class
            pattern2 = re.compile(r'[^\n;]*' + re.escape(cls) + r'[^\n;]*;?\n', re.MULTILINE)
            text = pattern2.sub('', text)
        return text

    content = remove_old_css(content)

    # Step 2: Remove OLD interaction HTML elements (ita-person, ita-detail, ita-toggle spans)
    # Remove ita-person anchor tags and their contents
    content = re.sub(r'<a class="ita-person"[^>]*>.*?</a>\s*', '', content, flags=re.DOTALL)
    # Remove ita-detail divs
    content = re.sub(r'<div class="ita-detail"[^>]*>.*?</div>\s*', '', content, flags=re.DOTALL)
    # Remove standalone ita-toggle spans
    content = re.sub(r'<span class="ita-toggle"[^>]*>.*?</span>\s*', '', content, flags=re.DOTALL)

    # Step 3: Inject new CSS
    if '</style>' in content:
        content = content.replace('</style>', NEW_CSS + '\n</style>')

    # Step 4: Replace timeline
    tl = build_timeline(person)
    if tl:
        pattern = re.compile(r'<div class="person-timeline">.*?</div>\s*</div>', re.DOTALL)
        content = pattern.sub(tl.rstrip() + '\n', content)

    # Step 5: Replace interaction section
    cards = build_cards(person)
    if cards:
        marker = '<h2>\U0001f465 参与者</h2>'
        idx = content.find(marker)
        if idx >= 0:
            next_h2 = content.find('<h2>', idx + len(marker))
            if next_h2 >= 0:
                content = content[:idx] + cards + content[next_h2:]
            else:
                # No next h2, just replace from marker to end of section
                content = content[:idx] + cards
        else:
            # Marker gone, try inserting before <h2>🗂️
            idx2 = content.find('<h2>🗂️')
            if idx2 >= 0:
                content = content[:idx2] + cards + content[idx2:]

    # Step 6: Add JS
    if 'ptl-expand' not in content and '</body>' in content:
        js = """<script>
document.addEventListener('DOMContentLoaded',function(){
  document.querySelectorAll('.ptl-expand').forEach(function(b){
    b.addEventListener('click',function(){
      var e=b.nextElementSibling;
      if(e&&e.classList.contains('ptl-expanded')){
        var open=e.style.display!=='none';
        e.style.display=open?'none':'block';
        b.textContent=open?'\\u25bc \\u5c55\\u5f00':'\\u25b2 \\u6536\\u8d77';
      }
    });
  });
});
</script>"""
        content = content.replace('</body>', js + '</body>')

    html_file.write_text(content, encoding='utf-8')
    tm = len(person_monthly.get(person, {}))
    print(f"  ok {html_file.name} ({tm}mo)")

print('\nDone')
