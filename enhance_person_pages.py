#!/usr/bin/env python3
"""
P2PTalk Wiki - Person Page Enhancement
1. Visual timeline grouped by month
2. Interaction details: who they talked with about which concepts
"""
import json, re, quopri, email.header
from pathlib import Path
from collections import defaultdict

REPO = Path('/Users/ice/.openclaw/workspace/p2ptalk-wiki-publish')
DATA_FILE = Path('/Users/ice/.openclaw/workspace/inbox/p2ptalk/p2ptalk_processed.json')

with open(DATA_FILE) as f:
    data = json.load(f)

person_msgs = data.get('person_messages', {})
person_monthly = data.get('person_monthly', {})
person_concepts = data.get('person_concepts', {})
# Build flat all_msgs from person_messages (for interaction calculations)
all_msgs = []
for person, msgs in person_msgs.items():
    for m in msgs:
        m_copy = dict(m)
        m_copy['person'] = person
        all_msgs.append(m_copy)

person_files = {}
for f in REPO.glob('person_*.html'):
    name = f.stem.replace('person_', '')
    person_files[name] = f

NEW_CSS = """.person-timeline{margin:16px 0 24px 0;}
.ptl-month{margin-bottom:18px;}
.ptl-month-label{display:flex;align-items:center;gap:8px;margin-bottom:8px;color:var(--accent);font-size:12px;font-weight:600;}
.ptl-month-label .ptl-dot{width:8px;height:8px;border-radius:50%;background:var(--accent);}
.ptl-month-label .ptl-year{color:var(--text-muted);font-size:10px;font-weight:400;margin-left:4px;}
.ptl-month-label .ptl-msg-count{font-size:10px;color:var(--text-muted);margin-left:auto;}
.ptl-msgs{margin-left:16px;border-left:2px solid var(--border);padding-left:14px;}
.ptl-msg{margin-bottom:10px;padding:8px 10px;background:rgba(255,255,255,0.02);border-radius:6px;border:1px solid var(--border);font-size:12px;line-height:1.5;}
.ptl-msg:hover{border-color:var(--accent);}
.ptl-msg-date{color:var(--text-muted);font-size:10px;margin-bottom:4px;}
.ptl-msg-subject{color:var(--accent);margin-bottom:4px;font-weight:500;}
.ptl-msg-body{color:var(--text);font-size:11px;line-height:1.5;display:none;}
.ptl-msg-body.open{display:block;}
.ptl-msg-concepts{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px;}
.ptl-msg-concept{background:var(--accent2);color:var(--text);font-size:10px;padding:2px 7px;border-radius:10px;border:1px solid var(--border);}
.ptl-expand{background:none;border:1px solid var(--accent);color:var(--accent);font-size:10px;cursor:pointer;padding:2px 8px;border-radius:5px;margin-top:4px;display:inline-block;}
.ptl-expand:hover{background:rgba(233,69,96,0.1);}
.ptl-msg-hidden{display:none;}
.ptl-show-all{text-align:center;padding:6px 0;}
.ptl-show-all-btn{background:var(--accent2);border:1px solid var(--border);color:var(--text-muted);font-size:11px;cursor:pointer;padding:4px 14px;border-radius:12px;transition:all 0.2s;}
.ptl-show-all-btn:hover{background:rgba(233,69,96,0.15);color:var(--accent);border-color:var(--accent);}
.ptl-show-all-btn.open{background:rgba(233,69,96,0.15);color:var(--accent);border-color:var(--accent);}
.ptl-bar{height:4px;background:var(--accent2);border-radius:2px;margin:4px 0 8px 0;overflow:hidden;}
.ptl-bar-fill{height:100%;background:var(--accent);border-radius:2px;transition:width 0.3s;}
.interaction-section{margin:16px 0 24px 0;}
.ita-person{display:flex;align-items:center;gap:10px;padding:8px 10px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:8px;margin-bottom:8px;cursor:pointer;text-decoration:none;color:var(--text);}
.ita-person:hover{border-color:var(--accent);color:var(--accent);}
.ita-person-name{font-weight:600;color:var(--accent);font-size:13px;}
.ita-person-count{color:var(--text-muted);font-size:11px;}
.ita-toggle{font-size:12px;color:var(--text-muted);margin-left:auto;}
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
  document.querySelectorAll('.ptl-show-all-btn').forEach(function(btn){
    btn.addEventListener('click',function(){
      var month=this.getAttribute('data-month');
      var container=this.closest('.ptl-month');
      if(container){
        var hidden=container.querySelectorAll('.ptl-msg-hidden');
        var isOpen=this.classList.contains('open');
        hidden.forEach(function(msg){msg.style.display=isOpen?'none':'block';});
        this.classList.toggle('open');
        this.textContent=isOpen?('展开全部 '+hidden.length+' 条 ▾'):('收起 ▲');
      }
    });
  });
  document.querySelectorAll('.ita-person').forEach(function(card){
    card.addEventListener('click',function(e){
      e.preventDefault();
      var detail=card.nextElementSibling;
      if(detail&&detail.classList.contains('ita-detail')){
        detail.style.display=detail.style.display?'none':'block';
        var toggle=card.querySelector('.ita-toggle');
        if(toggle)toggle.textContent=detail.style.display?'▼':'▲';
      }
    });
  });
});
</script>"""

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def decode_subject(subject):
    """Decode MIME encoded email subject (RFC 2047), handling malformed and multi-line."""
    if not subject or '=?' not in subject:
        return subject.strip() if subject else ''
    # Normalize: join soft line breaks, fix malformed endings
    s = re.sub(r'\r?\n[ =]*\?=', '?', subject)
    s = re.sub(r'=\?$', '?=', s)
    try:
        parts = email.header.decode_header(s)
        result = []
        for part, charset in parts:
            if isinstance(part, bytes):
                result.append(part.decode(charset or 'utf-8', errors='replace'))
            elif part:
                result.append(part)
        decoded = ''.join(result).strip()
        if decoded:
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

def build_timeline(person):
    """Build visual timeline grouped by month."""
    monthly = person_monthly.get(person, {})
    if not monthly:
        return ''
    msgs = person_msgs.get(person, [])
    sorted_msgs = sorted(msgs, key=lambda m: m.get('date', ''), reverse=True)

    by_month = defaultdict(list)
    for m in sorted_msgs:
        month = m.get('month', '')[:7]
        if month:
            by_month[month].append(m)

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
        html += f'<span class="ptl-msg-count">{count}条消息</span>'
        html += '</div>\n'
        html += f'<div class="ptl-bar"><div class="ptl-bar-fill" style="width:{bar_pct}%"></div></div>\n'
        html += '<div class="ptl-msgs">\n'

        msgs_this_month = by_month[month]
        total = len(msgs_this_month)
        visible_count = min(5, total)

        for i, m in enumerate(msgs_this_month):
            if i >= 5:
                hidden_cls = ' ptl-msg-hidden'
            else:
                hidden_cls = ''

            date = m.get('date', '')[:10] if m.get('date') else ''
            subject = decode_subject(m.get('subject', ''))
            if subject.lower() in ['re:', '']:
                subject = '(无主题)'
            body_preview = clean_body(m.get('body', '')[:300])
            if len(body_preview) > 100:
                body_preview = body_preview[:100] + '\u2026'
            concepts = m.get('concepts', [])
            if isinstance(concepts, str):
                try:
                    import ast
                    concepts = ast.literal_eval(concepts)
                except Exception:
                    concepts = []

            html += f'<div class="ptl-msg{hidden_cls}">\n'
            html += f'<div class="ptl-msg-date">{esc(date)}</div>\n'
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

        if total > 5:
            html += f'<div class="ptl-show-all"><button class="ptl-show-all-btn" data-month="{month}">展开全部 {total} 条 ▾</button></div>\n'

        html += '</div>\n</div>\n'

    html += '</div>\n'
    html += '<!-- END_PERSON_TIMELINE -->\n'
    return html


def build_interactions(person):
    """Build interaction section using concept co-occurrence from all_messages."""
    concept_people = defaultdict(set)
    person_concept_set = defaultdict(set)
    for m in all_msgs:
        p = m.get('person')
        for c in m.get('concepts', []):
            concept_people[c].add(p)
            person_concept_set[p].add(c)

    my_concepts = person_concept_set.get(person, set())
    if not my_concepts:
        return ''

    interactions = {}
    for concept in my_concepts:
        for other in concept_people.get(concept, []):
            if other == person:
                continue
            if other not in interactions:
                interactions[other] = {'concepts': set(), 'count': 0, 'last_date': ''}
            interactions[other]['concepts'].add(concept)

    for m in all_msgs:
        if m.get('person') not in interactions:
            continue
        m_concepts = set(m.get('concepts', []))
        if m_concepts & my_concepts:
            interactions[m.get('person')]['count'] += 1
            d = m.get('date', '')
            if d > interactions[m.get('person')]['last_date']:
                interactions[m.get('person')]['last_date'] = d

    sorted_interactions = sorted(
        interactions.items(),
        key=lambda x: len(x[1]['concepts']) * x[1]['count'],
        reverse=True
    )

    if not sorted_interactions:
        return ''

    html = '<div class="interaction-section">\n'
    for other_person, data in sorted_interactions[:10]:
        concepts = sorted(data['concepts'], key=lambda c: c.split('/')[-1])
        slug = other_person.replace(' ', '_')
        html += f'<a href="../person_{esc(slug)}.html" class="ita-person">\n'
        html += f'<div class="ita-person-name">{esc(other_person)}</div>\n'
        html += f'<div class="ita-person-count">{data["count"]}条互动 · {len(data["concepts"])}个共同概念</div>\n'
        html += '<span class="ita-toggle">▼</span>\n'
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

    timeline_html = build_timeline(person)
    if timeline_html:
        # Find the timeline section and replace it entirely.
        # Use a marker-based approach: start from <div class="person-timeline">
        # and find where the next </section> or <h2> starts, then walk backwards
        # through the markup to find the correct closing </div>.
        start_tag = '<div class="person-timeline">'
        idx_start = html_content.find(start_tag)
        if idx_start >= 0:
            search_from = idx_start + len(start_tag)
            # Find earliest section or h2 boundary after the timeline
            bound = len(html_content)
            for m in ['</section>', '<h2>', '<div class="sidebar">', '</body>']:
                idx = html_content.find(m, search_from)
                if 0 < idx < bound:
                    bound = idx
            # Walk backwards from bound to find the pattern that closes the timeline container
            # The timeline container ends with: </div></div> (inner msgs close + ptl-month close + outer close)
            # Look for a </div> preceded by </div></div> (i.e., the container itself)
            # Just find the last </div> snippet containing exactly the timeline's outermost close
            snippet = html_content[idx_start:bound]
            # Find the outermost container close: count how many extra </div> close the section
            # The container itself adds 1 more </div> than opens (since the start tag isn't counted)
            # Find the first </div> that doesn't have another </div> right before it (marking container close)
            # Actually simpler: the person-timeline div is the outermost div that closes right before the section ends
            # Find the LAST </div> in the snippet that's not part of the nested month divs
            # Strategy: find '\n</div>\n</div>' - this marks the end of a ptl-month and the last one has an extra close
            # The closing structure is exactly: </div>\n</div>\n</div> (for the last ptl-msg > ptl-msgs > ptl-month)
            # Then the person-timeline's own </div> closes right before the next section
            # 
            # Better approach: just use the last </div> as the timeline end marker
            end_marker_pos = html_content.rfind('</div>', idx_start, bound)
            # Verify this </div> is followed by </section> or whitespace+</section>
            strict_check = html_content[end_marker_pos:end_marker_pos+50]
            close_end = end_marker_pos + len('</div>')
            old_timeline = html_content[idx_start:close_end]
            html_content = html_content.replace(old_timeline, timeline_html.rstrip() + '\n', 1)

    interaction_html = build_interactions(person)
    if interaction_html:
        marker = '<h2>\U0001f465 参与者</h2>'
        idx = html_content.find(marker)
        if idx >= 0:
            next_h2 = html_content.find('<h2>', idx + len(marker))
            if next_h2 >= 0:
                html_content = html_content[:next_h2] + interaction_html + html_content[next_h2:]

    if '</body>' in html_content:
        html_content = html_content.replace('</body>', NEW_JS + '\n</body>')

    return html_content


def main():
    enhanced = 0
    for _, html_file in person_files.items():
        try:
            content = html_file.read_text(encoding='utf-8')
            # Extract Chinese name from <h1> tag (file names are romanized)
            import re
            m = re.search(r'<h1>(.*?)</h1>', content)
            if not m:
                print(f'  err {html_file.name}: no <h1> found')
                continue
            person = m.group(1).strip()
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
