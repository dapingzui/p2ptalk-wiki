#!/usr/bin/env python3
"""
P2PTalk Wiki - Person Page Enhancement
1. Visual timeline grouped by month
2. Interaction details: who they talked with about which concepts
"""
import json, re, quopri
from pathlib import Path
from collections import defaultdict

REPO = Path('/tmp/p2ptalk-wiki')
DATA_FILE = Path('/tmp/p2ptalk_processed.json')

with open(DATA_FILE) as f:
    data = json.load(f)

person_msgs = data.get('person_messages', {})
person_monthly = data.get('person_monthly', {})
person_concepts = data.get('person_concepts', {})
all_msgs = data['all_messages']

# Person slug mapping
person_files = {}
for f in REPO.glob('person_*.html'):
    name = f.stem.replace('person_', '')
    person_files[name] = f

NEW_CSS = """.person-timeline{margin:16px 0 24px 0;}
.ptl-month{margin-bottom:18px;}
.ptl-month-label{display:flex;align-items:center;gap:8px;margin-bottom:8px;color:var(--accent);font-size:12px;font-weight:600;}
.ptl-month-label .ptl-dot{width:8px;height:8px;border-radius:50%;background:var(--accent);}
.ptl-month-label .ptl-year{color:var(--text-muted);font-size:10px;font-weight:400;margin-left:4px;}
.ptl-msgs{margin-left:16px;border-left:2px solid var(--border);padding-left:14px;}
.ptl-msg{margin-bottom:10px;padding:8px 10px;background:rgba(255,255,255,0.02);border-radius:6px;border:1px solid var(--border);font-size:12px;line-height:1.5;}
.ptl-msg:hover{border-color:var(--accent);}
.ptl-msg-date{color:var(--text-muted);font-size:10px;margin-bottom:4px;}
.ptl-msg-subject{color:var(--accent);margin-bottom:4px;font-weight:500;}
.ptl-msg-subject a{color:var(--accent);text-decoration:none;}
.ptl-msg-subject a:hover{text-decoration:underline;}
.ptl-msg-body{color:var(--text);font-size:11px;line-height:1.5;display:none;}
.ptl-msg-body.open{display:block;}
.ptl-msg-concepts{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px;}
.ptl-msg-concept{background:var(--accent2);color:var(--text);font-size:10px;padding:2px 7px;border-radius:10px;border:1px solid var(--border);}
.ptl-expand{background:none;border:1px solid var(--accent);color:var(--accent);font-size:10px;cursor:pointer;padding:2px 8px;border-radius:5px;margin-top:4px;display:inline-block;}
.ptl-expand:hover{background:rgba(233,69,96,0.1);}
.ptl-bar{height:4px;background:var(--accent2);border-radius:2px;margin:4px 0 8px 0;overflow:hidden;}
.ptl-bar-fill{height:100%;background:var(--accent);border-radius:2px;transition:width 0.3s;}
.interaction-section{margin:16px 0 24px 0;}
.ita-person{display:flex;align-items:center;gap:10px;padding:8px 10px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:8px;margin-bottom:8px;cursor:pointer;text-decoration:none;color:var(--text);}
.ita-person:hover{border-color:var(--accent);color:var(--accent);}
.ita-person-name{font-weight:600;color:var(--accent);font-size:13px;}
.ita-person-count{color:var(--text-muted);font-size:11px;}
.ita-concepts{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px;}
.ita-concept-tag{background:var(--accent2);color:var(--text);font-size:10px;padding:2px 7px;border-radius:10px;border:1px solid var(--border);}"""

NEW_JS = """<script>
document.addEventListener('DOMContentLoaded',function(){
  document.querySelectorAll('.ptl-msg').forEach(function(msg){
    var btn=msg.querySelector('.ptl-expand');
    var body=msg.querySelector('.ptl-msg-body');
    if(btn&&body){
      btn.addEventListener('click',function(e){e.stopPropagation();
        body.classList.toggle('open');
        btn.textContent=body.classList.contains('open')?'收起 ▲':'展开 ▾';
      });
    }
  });
  document.querySelectorAll('.ita-person').forEach(function(card){
    card.addEventListener('click',function(e){
      var detail=card.nextElementSibling;
      if(detail&&detail.classList.contains('ita-detail')){
        detail.style.display=detail.style.display?'':'none';
        var toggle=card.querySelector('.ita-toggle');
        if(toggle)toggle.textContent=detail.style.display?'▲':'▼';
      }
    });
  });
});
</script>"""

def decode_subject(subject):
    """Decode MIME encoded email subject (RFC 2047), handling base64 and QP."""
    import email.header
    try:
        parts = email.header.decode_header(subject)
        result = []
        for part, charset in parts:
            if isinstance(part, bytes):
                result.append(part.decode(charset or 'utf-8', errors='replace'))
            elif part:
                result.append(part)
        decoded = ''.join(result).strip()
        if decoded and decoded != subject:
            return decoded
    except Exception:
        pass
    return subject.strip()

def clean_body(body):
    """Strip HTML tags and decode quoted-printable for email body."""
    try:
        if '=?' in body[:30]:
            decoded = quopri.decodestring(body.encode('utf-8', errors='replace'))
            body = decoded.decode('utf-8', errors='replace')
    except Exception:
        pass
    if body.lstrip().startswith('<!DOCTYPE') or body.lstrip().startswith('<html') or '<html>' in body[:200]:
        body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL | re.IGNORECASE)
        body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL | re.IGNORECASE)
        body = re.sub(r'<[^>]+>', ' ', body)
        body = re.sub(r'&nbsp;', ' ', body)
        body = re.sub(r'&[a-z]+;', ' ', body)
        body = re.sub(r'\s+', ' ', body).strip()
    return body

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def build_timeline(person):
    """Build visual timeline for a person."""
    monthly = person_monthly.get(person, {})
    if not monthly:
        return ''
    
    # Get person's messages sorted by date
    msgs = person_msgs.get(person, [])
    sorted_msgs = sorted(msgs, key=lambda m: m.get('date', ''), reverse=True)
    
    # Group by YYYY-MM
    by_month = defaultdict(list)
    for m in sorted_msgs:
        month = m.get('month', '')[:7]  # YYYY-MM
        if month:
            by_month[month].append(m)
    
    # Sort months descending
    sorted_months = sorted(by_month.keys(), reverse=True)
    max_count = max(len(v) for v in by_month.values()) if by_month else 1
    
    html = '<div class="person-timeline">\n'
    for month in sorted_months:
        year, mon = month.split('-')
        count = len(by_month[month])
        bar_pct = int(count / max_count * 100)
        
        html += f'<div class="ptl-month">\n'
        html += f'<div class="ptl-month-label">'
        html += f'<span class="ptl-dot"></span>'
        html += f'{year}年{mon}月'
        html += f'<span class="ptl-year">{count}条</span>'
        html += '</div>\n'
        html += f'<div class="ptl-bar"><div class="ptl-bar-fill" style="width:{bar_pct}%"></div></div>\n'
        html += '<div class="ptl-msgs">\n'
        
        # Show up to 5 messages per month
        for m in by_month[month][:5]:
            date = m.get('date', '')[:10] if m.get('date') else ''
            subject = decode_subject(m.get('subject', ''))
            if subject.lower() in ['re:', '']:
                subject = '(无主题)'
            body_preview = clean_body(m.get('body_preview', '') or m.get('body', '')[:200])
            if len(body_preview) > 100:
                body_preview = body_preview[:100] + '\u2026'
            concepts = m.get('concepts', [])
            if isinstance(concepts, str):
                try:
                    import ast
                    concepts = ast.literal_eval(concepts)
                except Exception:
                    concepts = []
            
            html += f'<div class="ptl-msg">\n'
            html += f'<div class="ptl-msg-date">{date}</div>\n'
            html += f'<div class="ptl-msg-subject">{esc(subject)}</div>\n'
            if concepts:
                html += '<div class="ptl-msg-concepts">\n'
                for c in concepts[:4]:
                    cname = c.split('/')[-1] if '/' in c else c
                    html += f'<span class="ptl-msg-concept">{esc(cname)}</span>\n'
                html += '</div>\n'
            if body_preview:
                html += f'<div class="ptl-msg-body">{esc(body_preview)}</div>\n'
                html += '<button class="ptl-expand">展开 ▾</button>\n'
            html += '</div>\n'
        
        if len(by_month[month]) > 5:
            html += f'<div style="text-align:center;color:var(--text-muted);font-size:11px;padding:4px">还有{len(by_month[month])-5}条消息</div>\n'
        
        html += '</div>\n</div>\n'
    
    html += '</div>\n'
    return html


def build_interactions(person):
    """Build interaction section: who did this person talk with about which concepts."""
    msgs = person_msgs.get(person, [])
    if not msgs:
        return ''
    
    # For each message, find other participants in the same concept
    # Build a map: other_person -> {concepts: set, msg_count: int, last_date: str}
    interactions = defaultdict(lambda: {'concepts': set(), 'count': 0, 'last_date': ''})
    
    for m in msgs:
        concepts = m.get('concepts', [])
        if isinstance(concepts, str):
            try:
                import ast
                concepts = ast.literal_eval(concepts)
            except Exception:
                concepts = []
        
        date = m.get('date', '')
        for other in all_msgs:
            if other.get('person') == person:
                continue
            other_concepts = other.get('concepts', [])
            if isinstance(other_concepts, str):
                try:
                    import ast
                    other_concepts = ast.literal_eval(other_concepts)
                except Exception:
                    other_concepts = []
            # If they share a concept, count as interaction
            shared = set(c for c in concepts if c in other_concepts)
            if shared:
                interactions[other.get('person')]['concepts'].update(shared)
                interactions[other.get('person')]['count'] += 1
                od = other.get('date', '')
                if od > interactions[other.get('person')]['last_date']:
                    interactions[other.get('person')]['last_date'] = od
    
    # Sort by interaction strength (shared concept count * msg count)
    sorted_interactions = sorted(
        interactions.items(),
        key=lambda x: len(x[1]['concepts']) * x[1]['count'],
        reverse=True
    )
    
    if not sorted_interactions:
        return ''
    
    html = '<div class="interaction-section">\n'
    for other_person, data in sorted_interactions[:10]:  # Top 10 interactions
        concepts = sorted(data['concepts'], key=lambda c: c.split('/')[-1])
        slug = other_person.replace(' ', '_')
        html += f'<a href="../person_{esc(slug)}.html" class="ita-person">\n'
        html += f'<div>\n'
        html += f'<div class="ita-person-name">{esc(other_person)}</div>\n'
        html += f'<div class="ita-person-count">{data["count"]}条互动 · {len(data["concepts"])}个共同概念</div>\n'
        html += '</div>\n'
        html += '<span class="ita-toggle" style="margin-left:auto;font-size:12px;color:var(--text-muted)">▼</span>\n'
        html += '</a>\n'
        html += '<div class="ita-detail" style="display:none;padding:8px 10px 12px 10px;margin-bottom:12px;background:rgba(255,255,255,0.02);border-radius:6px;">\n'
        html += '<div class="ita-concepts">\n'
        for c in concepts[:8]:
            cname = c.split('/')[-1]
            html += f'<span class="ita-concept-tag">{esc(cname)}</span>\n'
        html += '</div>\n'
        if data['last_date']:
            html += f'<div style="font-size:10px;color:var(--text-muted);margin-top:6px;">最近互动: {data["last_date"][:10]}</div>\n'
        html += '</div>\n'
    
    html += '</div>\n'
    return html


def enhance_person_html(html_content, person):
    if '</style>' in html_content:
        html_content = html_content.replace('</style>', NEW_CSS + '\n</style>')
    
    # Replace existing timeline div with new one
    timeline_html = build_timeline(person)
    if timeline_html:
        # Replace the existing <div class="timeline">...</div>
        pattern = re.compile(r'<div class="timeline">.*?</div>\s*</div>', re.DOTALL)
        html_content = pattern.sub(timeline_html.rstrip() + '\n', html_content)
    
    # Add interaction section after 参与者 links, before 概念 h2
    interaction_html = build_interactions(person)
    if interaction_html:
        # Find 参与者 h2, then insert after its closing </h2> and following links
        marker = '<h2>\U0001f465 参与者</h2>'
        idx = html_content.find(marker)
        if idx >= 0:
            # Find the next <h2> after this section
            next_h2 = html_content.find('<h2>', idx + len(marker))
            if next_h2 >= 0:
                html_content = html_content[:next_h2] + interaction_html + html_content[next_h2:]
    
    if '</body>' in html_content:
        html_content = html_content.replace('</body>', NEW_JS + '\n</body>')
    
    return html_content


def main():
    enhanced = 0
    for person, html_file in person_files.items():
        try:
            content = html_file.read_text(encoding='utf-8')
            enhanced_content = enhance_person_html(content, person)
            html_file.write_text(enhanced_content, encoding='utf-8')
            enhanced += 1
            t_count = len(person_monthly.get(person, {}))
            i_count = len(person_msgs.get(person, []))
            print(f'  ok {html_file.name} (timeline:{t_count}mo, msgs:{i_count})')
        except Exception as e:
            print(f'  err {person}: {e}')
    print(f'\nEnhanced {enhanced} person pages')


if __name__ == '__main__':
    main()
