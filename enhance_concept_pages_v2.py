#!/usr/bin/env python3
"""
P2PTalk Wiki - Concept Page Enhancement v2
1. Full discussion threads (all messages, not just 2 previews)
2. Participant summary row at top of people section
3. Q→A status section
4. Sort person blocks by message count
"""
import json, re, quopri, html as html_mod
from pathlib import Path
from collections import defaultdict

REPO = Path('/tmp/p2ptalk-wiki')
DATA_FILE = Path('/tmp/p2ptalk_processed.json')

with open(DATA_FILE) as f:
    data = json.load(f)

all_msgs = data['all_messages']

# Build concept -> messages (full body)
concept_msgs = defaultdict(list)
for msg in all_msgs:
    body = msg.get('body', '').strip()
    if not body:
        continue
    for concept in msg.get('concepts', []):
        concept_msgs[concept].append(msg)

# Slug -> HTML file mapping
slug_to_file = {}
for cat in ['atom', 'consensus', 'broadcast', 'meeting', 'market', 'ai', 'security', 'math']:
    cat_dir = REPO / cat
    if not cat_dir.exists():
        continue
    for f in cat_dir.glob('*.html'):
        slug_to_file[f'{cat}/{f.stem}'] = f

NEW_CSS = """.all-msgs-section{margin:0 0 24px 0;}
.all-msgs-header{display:flex;align-items:center;gap:10px;cursor:pointer;padding:10px 14px;background:var(--accent2);border-radius:8px;border:1px solid var(--border);margin-bottom:12px;}
.all-msgs-header:hover{border-color:var(--accent);}
.all-msgs-header h3{font-size:13px;color:var(--accent);font-weight:600;margin:0;}
.all-msgs-header .toggle-icon{color:var(--accent);font-size:16px;margin-left:auto;}
.all-msgs-list{display:none;}
.all-msgs-list.open{display:block;}
.msg-thread{border:1px solid var(--border);border-radius:8px;margin-bottom:8px;overflow:hidden;}
.msg-thread-header{display:flex;align-items:center;gap:8px;padding:8px 12px;background:rgba(255,255,255,0.03);border-bottom:1px solid var(--border);cursor:pointer;}
.msg-thread-header:hover{background:rgba(233,69,96,0.06);}
.msg-thread-header .msg-person{color:var(--accent);font-size:12px;font-weight:600;}
.msg-thread-header .msg-date{color:var(--text-muted);font-size:10px;margin-left:auto;}
.msg-q-badge{background:#ff6b6b;color:#fff;font-size:10px;padding:2px 7px;border-radius:10px;margin-left:4px;}
.msg-thread-body{padding:10px 12px;font-size:12px;line-height:1.65;color:var(--text);display:none;background:rgba(255,255,255,0.02);}
.msg-thread-body.open{display:block;}
.msg-full{white-space:pre-wrap;word-break:break-word;}
.msg-email-header{font-size:10px;color:var(--text-muted);margin-bottom:6px;padding-bottom:6px;border-bottom:1px dashed var(--border);}
.msg-expand-btn{background:none;border:1px solid var(--accent);color:var(--accent);font-size:11px;cursor:pointer;padding:4px 10px;border-radius:6px;margin-top:6px;display:inline-block;}
.msg-expand-btn:hover{background:rgba(233,69,96,0.1);}
.people-summary{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px;padding:10px 12px;background:rgba(233,69,96,0.05);border-radius:8px;border:1px solid var(--border);}
.people-summary-label{font-size:10px;color:var(--text-muted);width:100%;margin-bottom:4px;}
.people-summary .p-tag{background:var(--accent2);color:var(--text);font-size:11px;padding:3px 9px;border-radius:12px;border:1px solid var(--border);cursor:pointer;text-decoration:none;transition:border-color 0.15s;}
.people-summary .p-tag:hover{border-color:var(--accent);color:var(--accent);}
.people-summary .p-tag .p-msg-count{color:var(--text-muted);margin-left:3px;}"""

NEW_JS = """<script>
document.addEventListener('DOMContentLoaded',function(){
  var h=document.querySelector('.all-msgs-header');
  var l=document.querySelector('.all-msgs-list');
  if(h&&l){h.addEventListener('click',function(){
    var o=l.classList.contains('open');
    l.classList.toggle('open');
    h.querySelector('.toggle-icon').textContent=o?'\\u25b6':'\\u25bc';
  });}
  document.querySelectorAll('.msg-thread-header').forEach(function(hd){
    hd.addEventListener('click',function(){
      var b=hd.nextElementSibling;
      if(b&&b.classList.contains('msg-thread-body')){b.classList.toggle('open');}
    });
  });
  document.querySelectorAll('.msg-expand-btn').forEach(function(btn){
    btn.addEventListener('click',function(e){e.stopPropagation();
      var full=btn.previousElementSibling;
      if(full){full.style.whiteSpace='pre-wrap';full.style.wordBreak='break-word';full.style.maxHeight='none';}
      btn.style.display='none';
    });
  });
});
</script>"""


def esc(s):
    """Escape string for HTML."""
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')


def clean_body(body):
    """Strip HTML tags and decode quoted-printable for email body."""
    try:
        if '=?' in body[:30]:
            decoded = quopri.decodestring(body.encode('utf-8', errors='replace'))
            body = decoded.decode('utf-8', errors='replace')
    except Exception:
        pass
    # If body is HTML email, strip tags
    if body.lstrip().startswith('<!DOCTYPE') or body.lstrip().startswith('<html') or '<html>' in body[:200]:
        body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL | re.IGNORECASE)
        body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL | re.IGNORECASE)
        body = re.sub(r'<[^>]+>', ' ', body)
        body = re.sub(r'&nbsp;', ' ', body)
        body = re.sub(r'&[a-z]+;', ' ', body)
        body = re.sub(r'\s+', ' ', body).strip()
    return body


def build_all_messages_section(concept_slug):
    msgs = concept_msgs.get(concept_slug, [])
    if not msgs:
        return ''
    sorted_msgs = sorted(msgs, key=lambda m: m.get('date', ''))
    total = len(sorted_msgs)
    q_count = sum(1 for m in sorted_msgs if m.get('is_question') or '?' in m.get('body','')[:300])

    html = '<div class="all-msgs-section">\n'
    html += '<div class="all-msgs-header">\n'
    label = f'\U0001f4ac 全部讨论（共{total}条'
    if q_count > 0:
        label += f'，{q_count}个问题'
    label += '）'
    html += f'<h3>{label}</h3>\n'
    html += '<span class="toggle-icon">\u25bc</span>\n'
    html += '</div>\n'
    html += '<div class="all-msgs-list">\n'

    for m in sorted_msgs:
        body = m.get('body', '')
        is_q = bool(m.get('is_question')) or ('?' in body[:200] and len(body) > 50)
        q_badge = '<span class="msg-q-badge">\u2753 问</span>' if is_q else ''
        date_str = m.get('date', '')[:10] if m.get('date') else ''
        person = esc(m.get('person', 'Unknown'))
        subject = m.get('subject', '')
        subj_html = f'<div class="msg-email-header">\u4e3b\u9898: {esc(subject)}</div>' if subject and subject not in ['Re:', ''] else ''
        if len(body) > 500:
            cleaned_full = clean_body(body)
            short = cleaned_full[:500]
            rest = cleaned_full[500:]
            body_html = f'{subj_html}<div class="msg-full">{esc(short)}</div>'
            body_html += f'<div class="msg-rest" style="display:none;">{esc(rest)}</div>'
            body_html += '<button class="msg-expand-btn" onclick="var r=this.previousElementSibling;r.style.display=r.style.display?\'\':\'none\';this.textContent=r.style.display?\'\u5c55\u5f00\u5168\u6587 \u25bc\':\'\u6536\u8d77 \u25b4\';var f=r.previousElementSibling;if(f&&f.classList.contains(\'msg-full\'))f.style.display=r.style.display?\'none\':\'block\';">\u5c55\u5f00\u5168\u6587 \u25bc</button>'
        else:
            body_html = f'{subj_html}<div class="msg-full">{esc(clean_body(body))}</div>'

        html += f'<div class="msg-thread">\n'
        html += f'<div class="msg-thread-header">\n'
        html += f'<span class="msg-person">{person}</span>\n{q_badge}\n'
        html += f'<span class="msg-date">{esc(date_str)}</span>\n'
        html += '</div>\n'
        html += f'<div class="msg-thread-body">\n{body_html}\n</div>\n</div>\n'

    html += '</div>\n</div>\n'
    return html


def build_people_summary(concept_slug):
    msgs = concept_msgs.get(concept_slug, [])
    if not msgs:
        return ''
    counts = defaultdict(int)
    for msg in msgs:
        counts[msg.get('person', 'Unknown')] += 1
    sorted_persons = sorted(counts.items(), key=lambda x: -x[1])

    html = '<div class="people-summary">\n'
    html += '<div class="people-summary-label">\u53c2\u4e0e\u8ba8\u8bba\u7684\u4eba</div>\n'
    for person, count in sorted_persons:
        slug_name = person.replace(' ', '_')
        html += f'<a href="../person_{esc(slug_name)}.html" class="p-tag">{esc(person)}<span class="p-msg-count">({count}\u6761)</span></a>\n'
    html += '</div>\n'
    return html


def extract_qa_items(body_html):
    qa_items = []
    seen = set()
    for tag in ['h2', 'h3']:
        for m in re.finditer(rf'<{tag}>([^<]*)</{tag}>', body_html):
            text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            if not text:
                continue
            clean = re.sub(r'[\U0001f534\U0001f7e1\U0001f7e2\U0001f535\U0001f7e0\u2753\u3299\s]+', '', text).strip()
            if len(clean) < 5:
                continue
            key = ('open', clean[:50])
            if any(c in text for c in ['\U0001f534', '\U0001f535', '\u2753']) and key not in seen:
                seen.add(key); qa_items.append(('open', clean))
            elif '\U0001f7e1' in text and key not in seen:
                seen.add(key); qa_items.append(('pending', clean))
            elif '\U0001f7e2' in text and key not in seen:
                seen.add(key); qa_items.append(('resolved', clean))
    return qa_items


def build_qa_section(qa_items):
    if not qa_items:
        return ''
    sc = {'open': 0, 'pending': 0, 'resolved': 0}
    for s, _ in qa_items:
        sc[s] += 1
    html = '<div class="qa-section">\n<div class="qa-header">\U0001f4cb Q\u2192A \u72b6\u6001\u8ffd\u8e2a<span class="qa-count">'
    if sc['open']: html += f' \U0001f534{sc["open"]}'
    if sc['pending']: html += f' \U0001f7e1{sc["pending"]}'
    if sc['resolved']: html += f' \U0001f7e2{sc["resolved"]}'
    html += '</span></div>\n<div class="qa-body">\n'
    icons = {'open': '\U0001f534', 'pending': '\U0001f7e1', 'resolved': '\U0001f7e2'}
    for status, text in qa_items:
        html += f'<div class="qa-item {status}"><span class="qa-status">{icons[status]}</span>'
        html += f'<div class="qa-question {status}">{esc(text)}</div></div>\n'
    html += '</div>\n</div>\n'
    return html


def sort_person_blocks(html):
    pattern = re.compile(r'<div class="person-block">.*?</div>\s*</div>\s*</div>\s*</div>', re.DOTALL)
    blocks = []
    for m in pattern.finditer(html):
        block = m.group()
        cnt_m = re.search(r'<span class="person-count">(\d+)条</span>', block)
        cnt = int(cnt_m.group(1)) if cnt_m else 0
        blocks.append((cnt, block))
    if len(blocks) <= 1:
        return html
    blocks.sort(key=lambda x: -x[0])
    ps = html.find('<div class="people-section">')
    if ps < 0:
        return html
    end_marker = '</div></div></div></div></body>'
    pe = html.find(end_marker)
    if pe < 0:
        return html
    before = html[:ps]
    after = html[pe:]
    mid = html[ps:pe]
    h3m = re.search(r'(<h3>[^<]*</h3>)', mid)
    if not h3m:
        return html
    header = h3m.group(1)
    new_blocks = header + '\n'
    for _, block, _, _ in blocks:
        clean = re.sub(r'^<h3>[^<]*</h3>\s*', '', block, flags=re.DOTALL)
        new_blocks += clean + '\n'
    return before + new_blocks + after


def enhance_html(html_content, concept_slug):
    if '</style>' in html_content:
        html_content = html_content.replace('</style>', NEW_CSS + '\n</style>')

    all_msgs_html = build_all_messages_section(concept_slug)
    people_start = html_content.find('<div class="people-section">')

    if all_msgs_html and people_start > 0:
        ins = html_content.rfind('</div>', 0, people_start)
        if ins > 0:
            html_content = html_content[:ins] + '\n' + all_msgs_html + html_content[ins:]
            people_start += len(all_msgs_html)

    ps_html = build_people_summary(concept_slug)
    if ps_html and people_start > 0:
        ps_content = html_content[people_start:]
        h3_pattern = re.compile(r'<h3>\U0001f465 [^<]*</h3>')
        h3m = h3_pattern.search(ps_content)
        if h3m:
            ins = people_start + h3m.end()
            html_content = html_content[:ins] + '\n' + ps_html + html_content[ins:]

    body_only = html_content[:people_start] if people_start > 0 else html_content
    qa_items = extract_qa_items(body_only)
    qa_html = build_qa_section(qa_items)
    if qa_html and people_start > 0:
        ins = html_content.rfind('</div>', 0, people_start)
        if ins > 0:
            html_content = html_content[:ins] + '\n' + qa_html + html_content[ins:]

    html_content = sort_person_blocks(html_content)

    if '</body>' in html_content:
        html_content = html_content.replace('</body>', NEW_JS + '\n</body>')
    return html_content


def main():
    enhanced = 0
    for slug, html_file in slug_to_file.items():
        try:
            content = html_file.read_text(encoding='utf-8')
            if 'people-section' not in content:
                continue
            enhanced_content = enhance_html(content, slug)
            html_file.write_text(enhanced_content, encoding='utf-8')
            enhanced += 1
            msg_count = len(concept_msgs.get(slug, []))
            print(f'  ok {html_file.parent.name}/{html_file.name} ({msg_count} msgs)')
        except Exception as e:
            print(f'  err {slug}: {e}')

    print(f'\nEnhanced {enhanced} concept pages')


if __name__ == '__main__':
    main()
