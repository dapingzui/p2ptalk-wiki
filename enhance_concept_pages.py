#!/usr/bin/env python3
"""
Enhance P2PTalk concept pages with:
1. Expand/collapse for .p-preview messages
2. Q→A status section extracted from page content
3. Sort person blocks by message count
"""
import os
import re
from pathlib import Path

REPO = Path('/tmp/p2ptalk-wiki')

# New CSS
NEW_CSS = """
/* Q→A Status Section */
.qa-section{margin:0 0 24px 0;border:1px solid var(--border);border-radius:8px;overflow:hidden;}
.qa-header{background:var(--accent2);padding:10px 16px;display:flex;align-items:center;font-size:13px;font-weight:600;color:var(--accent);}
.qa-header .qa-count{margin-left:auto;font-size:11px;color:var(--text-muted);font-weight:400;}
.qa-body{padding:0;}
.qa-item{padding:10px 16px;border-bottom:1px solid var(--border);display:flex;align-items:flex-start;gap:10px;}
.qa-item:last-child{border-bottom:none;}
.qa-item .qa-status{font-size:14px;flex-shrink:0;width:20px;text-align:center;padding-top:2px;}
.qa-item .qa-question{font-size:13px;color:var(--text);line-height:1.5;}
.qa-item .qa-question.open{color:#ff6b6b;}
.qa-item .qa-question.pending{color:#ffd93d;}
.qa-item .qa-question.resolved{color:#6bcb77;}
.qa-empty{padding:12px 16px;font-size:12px;color:var(--text-muted);font-style:italic;}
/* Expand/Collapse */
.p-expand-btn{background:none;border:none;color:var(--accent);font-size:11px;cursor:pointer;padding:2px 6px;margin-top:2px;display:inline-block;}
.p-expand-btn:hover{text-decoration:underline;}
.p-msg-wrapper{display:block;}
.p-preview{font-size:11px;color:var(--text);line-height:1.5;margin:3px 0;padding-left:8px;border-left:2px solid var(--border);}
"""

NEW_JS = """
<script>
document.addEventListener('DOMContentLoaded',function(){
  // Expand/collapse for .p-preview
  document.querySelectorAll('.p-preview').forEach(function(preview){
    var wrapper=document.createElement('div');
    wrapper.className='p-msg-wrapper';
    preview.parentNode.insertBefore(wrapper,preview);
    wrapper.appendChild(preview);
    var btn=document.createElement('button');
    btn.className='p-expand-btn';
    btn.textContent='展开 ▾';
    btn.style.display='inline-block';
    preview.parentNode.insertBefore(btn,preview.nextSibling);
    preview.style.maxHeight='60px';
    preview.style.overflow='hidden';
    preview.style.transition='max-height 0.3s ease';
    btn.addEventListener('click',function(){
      var isExpanded=preview.dataset.expanded==='1';
      if(isExpanded){
        preview.style.maxHeight='60px';
        preview.dataset.expanded='0';
        btn.textContent='展开 ▾';
      }else{
        preview.style.maxHeight='none';
        preview.dataset.expanded='1';
        btn.textContent='收起 ▴';
      }
    });
  });
});
</script>
"""


STATUS_ICONS = {'open': '🔴', 'pending': '🟡', 'resolved': '🟢'}

def extract_qa_items(body_html):
    """Extract Q→A items from HTML body content."""
    qa_items = []
    seen = set()
    
    # 1. Look for h2/h3 with status markers
    for tag in ['h2', 'h3']:
        for m in re.finditer(rf'<{tag}>([^<]*)</{tag}>', body_html):
            text = m.group(1).strip()
            text = re.sub(r'<[^>]+>', '', text).strip()
            if not text:
                continue
            if '🔴' in text or '❓' in text:
                clean = re.sub(r'^[🔴🟡🟢❓\s]+', '', text)
                key = ('open', clean[:50])
                if key not in seen and len(clean) > 5:
                    seen.add(key); qa_items.append(('open', clean))
            elif '🟡' in text:
                clean = re.sub(r'^[🔴🟡🟢❓\s]+', '', text)
                key = ('pending', clean[:50])
                if key not in seen and len(clean) > 5:
                    seen.add(key); qa_items.append(('pending', clean))
            elif '🟢' in text:
                clean = re.sub(r'^[🔴🟡🟢❓\s]+', '', text)
                key = ('resolved', clean[:50])
                if key not in seen and len(clean) > 5:
                    seen.add(key); qa_items.append(('resolved', clean))
    
    # 2. Look for list items with status markers
    for m in re.finditer(r'<li>([^<]+)</li>', body_html):
        text = m.group(1).strip()
        text = re.sub(r'<[^>]+>', '', text).strip()
        if not text or len(text) < 5:
            continue
        if '↩' in text or 'href' in text:
            continue
        if '🔴' in text or '❓' in text:
            clean = re.sub(r'^[🔴🟡🟢❓\s\d\.\)]+', '', text).strip()
            key = ('open', clean[:50])
            if key not in seen and len(clean) > 5:
                seen.add(key); qa_items.append(('open', clean))
        elif '🟡' in text:
            clean = re.sub(r'^[🔴🟡🟢❓\s\d\.\)]+', '', text).strip()
            key = ('pending', clean[:50])
            if key not in seen and len(clean) > 5:
                seen.add(key); qa_items.append(('pending', clean))
        elif '🟢' in text:
            clean = re.sub(r'^[🔴🟡🟢❓\s\d\.\)]+', '', text).strip()
            key = ('resolved', clean[:50])
            if key not in seen and len(clean) > 5:
                seen.add(key); qa_items.append(('resolved', clean))
    
    # 3. "未解答问题" / "待确认" / "已解答" sections
    section_map = [
        ('未解答问题', 'open'),
        ('待确认', 'pending'),
        ('已解答', 'resolved'),
        ('已确认', 'resolved'),
        ('关键未解答问题', 'open'),
    ]
    for section_name, status in section_map:
        idx = body_html.find(section_name)
        if idx >= 0:
            snippet = body_html[idx:idx+3000]
            for li_m in re.finditer(r'<li>([^<]{5,})</li>', snippet):
                text = li_m.group(1).strip()
                text = re.sub(r'<[^>]+>', '', text).strip()
                if '↩' in text or len(text) < 5:
                    continue
                key = (status, text[:50])
                if key not in seen:
                    seen.add(key); qa_items.append((status, text))
    
    return qa_items


def build_qa_section(qa_items):
    """Build Q→A status section HTML."""
    if not qa_items:
        return ''
    
    status_counts = {'open': 0, 'pending': 0, 'resolved': 0}
    for s, _ in qa_items:
        status_counts[s] = status_counts.get(s, 0) + 1
    
    html = '<div class="qa-section">\n'
    html += '<div class="qa-header">📋 Q→A 状态追踪<span class="qa-count">'
    if status_counts['open']:
        html += f' 🔴{status_counts["open"]}'
    if status_counts['pending']:
        html += f' 🟡{status_counts["pending"]}'
    if status_counts['resolved']:
        html += f' 🟢{status_counts["resolved"]}'
    html += '</span></div>\n<div class="qa-body">\n'
    
    for status, text in qa_items:
        icon = STATUS_ICONS[status]
        html += f'<div class="qa-item"><span class="qa-status">{icon}</span><div class="qa-question {status}">{text}</div></div>\n'
    
    html += '</div>\n</div>\n'
    return html


def sort_person_blocks(html):
    """Sort person blocks by message count descending."""
    pattern = re.compile(r'<div class="person-block">.*?</div>\s*</div>\s*</div>\s*</div>\s*<div class="person-block">', re.DOTALL)
    
    # Find all person blocks
    blocks = []
    starts = [(m.start(), m.group()) for m in pattern.finditer(html)]
    
    # Also get the last block (without trailing person-block)
    all_blocks_pattern = re.compile(r'<div class="person-block">.*?</div>\s*</div>\s*</div>\s*</div>', re.DOTALL)
    all_blocks = []
    for m in all_blocks_pattern.finditer(html):
        block = m.group()
        count_m = re.search(r'<span class="person-count">(\d+)条</span>', block)
        count = int(count_m.group(1)) if count_m else 0
        all_blocks.append((count, block, m.start(), m.end()))
    
    if len(all_blocks) <= 1:
        return html
    
    # Sort by count descending
    all_blocks.sort(key=lambda x: -x[0])
    
    # Reconstruct: find the people-section bounds
    ps_start = html.find('<div class="people-section">')
    if ps_start < 0:
        return html
    
    before = html[:ps_start]
    
    # Find end of people-section
    # It ends with: </div></div></div></div></body>
    after_marker = '</div></div></div></div></body>'
    ps_end = html.find(after_marker)
    if ps_end < 0:
        return html
    
    middle = html[ps_start:ps_end]
    after = html[ps_end:]
    
    # Extract just the opening tags and h3 from the middle
    h3_match = re.search(r'(<h3>.*?</h3>)', middle, re.DOTALL)
    if not h3_match:
        return html
    header_part = h3_match.group(1)
    
    # Build new person blocks
    new_blocks = header_part + '\n'
    for count, block, _, _ in all_blocks:
        # Strip the h3 we already extracted
        block_clean = re.sub(r'^<h3>.*?</h3>\s*', '', block, flags=re.DOTALL)
        new_blocks += block_clean + '\n'
    
    return before + new_blocks + after


def enhance_html(html_content):
    """Apply all enhancements to a concept page HTML."""
    # 1. Inject new CSS before </style>
    if '</style>' in html_content:
        html_content = html_content.replace('</style>', NEW_CSS + '\n</style>')
    
    # 2. Extract Q→A items and build section
    people_start = html_content.find('<div class="people-section">')
    body_content = html_content[:people_start] if people_start > 0 else html_content
    
    qa_items = extract_qa_items(body_content)
    qa_html = build_qa_section(qa_items)
    
    # Insert Q→A after </div> that closes .page div, before people-section
    if qa_html and people_start > 0:
        # Find the last </div> before people-section
        insert_at = html_content.rfind('</div>', 0, people_start)
        if insert_at > 0:
            html_content = html_content[:insert_at] + '\n' + qa_html + html_content[insert_at:]
    
    # 3. Sort person blocks
    html_content = sort_person_blocks(html_content)
    
    # 4. Inject JS before </body>
    if '</body>' in html_content:
        html_content = html_content.replace('</body>', NEW_JS + '\n</body>')
    
    return html_content


def main():
    categories = ['atom', 'consensus', 'broadcast', 'meeting', 'market', 'ai', 'security', 'math']
    
    enhanced = 0
    for cat in categories:
        cat_dir = REPO / cat
        if not cat_dir.exists():
            continue
        for html_file in sorted(cat_dir.glob('*.html')):
            try:
                content = html_file.read_text(encoding='utf-8')
                if 'people-section' not in content:
                    continue
                enhanced_content = enhance_html(content)
                html_file.write_text(enhanced_content, encoding='utf-8')
                enhanced += 1
                print(f'  ✓ {cat}/{html_file.name}')
            except Exception as e:
                print(f'  ✗ {cat}/{html_file.name}: {e}')
    
    print(f'\n✅ Enhanced {enhanced} concept pages')


if __name__ == '__main__':
    main()
