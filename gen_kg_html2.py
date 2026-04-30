import os, re, markdown, shutil

src = '/Users/ice/.openclaw/workspace/inbox/p2ptalk/KnowledgeGraph'
out = '/Users/ice/.openclaw/workspace/p2ptalk-wiki-publish'
if os.path.exists(out):
    shutil.rmtree(out)
os.makedirs(out)

# Load all pages
pages = {}
concepts_dir = os.path.join(src, 'concepts')
for cat in sorted(os.listdir(concepts_dir)):
    cat_path = os.path.join(concepts_dir, cat)
    if not os.path.isdir(cat_path): continue
    for f in sorted(os.listdir(cat_path)):
        if not f.endswith('.md'): continue
        path = os.path.join(cat_path, f)
        with open(path) as fp:
            content = fp.read()
        if content.startswith('---'):
            parts = content.split('---', 2)
            fm = parts[1].strip()
            body = parts[2].strip() if len(parts) > 2 else ''
        else:
            fm, body = '', content
        meta = {}
        for line in fm.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
        name = f[:-3]
        pages[f'{cat}/{name}'] = {
            'category': cat,
            'name': name,
            'meta': meta,
            'body': body,
            'file': f[:-3]
        }

from collections import defaultdict
cats = defaultdict(list)
for slug, p in pages.items():
    cats[p['category']].append((slug, p))
cats = dict(sorted(cats.items()))

# Build reverse link index
# wiki link format: [[category/name]] or [[name]]
# Find all wiki links in all pages
all_wiki_links = defaultdict(set)  # target_slug -> set of source slugs
for src_slug, p in pages.items():
    for m in re.finditer(r'\[\[([^\]]+)\]\]', p['body']):
        raw = m.group(1).strip()
        # Resolve wiki link
        target = None
        if '/' in raw:
            parts = raw.split('/')
            target = raw  # already with category
        else:
            # Search by name across all categories
            for slug, pp in pages.items():
                if pp['name'] == raw:
                    target = slug
                    break
        if target and target in pages and target != src_slug:
            all_wiki_links[target].add(src_slug)

print(f"Wiki links found: {sum(len(v) for v in all_wiki_links.values())}")
print(f"Pages with backlinks: {len(all_wiki_links)}")

CSS = """
:root {
  --bg: #1a1a2e;
  --sidebar-bg: #16213e;
  --accent: #e94560;
  --accent2: #0f3460;
  --text: #eaeaea;
  --text-muted: #a0a0a0;
  --border: #2a2a4a;
  --code-bg: #0d1117;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
body { display: flex; flex-direction: column; }
header { background: var(--sidebar-bg); border-bottom: 1px solid var(--border); padding: 12px 20px; display: flex; align-items: center; gap: 16px; flex-shrink: 0; }
header h1 { font-size: 16px; color: var(--accent); font-weight: 600; }
header .subtitle { color: var(--text-muted); font-size: 13px; }
header .subtitle a { color: var(--accent); text-decoration: none; }
header .subtitle a:hover { text-decoration: underline; }
.container { display: flex; flex: 1; overflow: hidden; height: calc(100vh - 45px); }
.sidebar { width: 240px; background: var(--sidebar-bg); border-right: 1px solid var(--border); overflow-y: auto; padding: 16px 0; flex-shrink: 0; }
.sidebar h2 { font-size: 10px; text-transform: uppercase; letter-spacing: 1.2px; color: var(--text-muted); padding: 10px 16px 4px; display: flex; justify-content: space-between; align-items: center; }
.sidebar h2 .cat-count { color: var(--text-muted); font-size: 10px; }
.sidebar a { display: block; padding: 4px 16px; color: var(--text); text-decoration: none; font-size: 12px; border-left: 2px solid transparent; }
.sidebar a:hover, .sidebar a.active { background: var(--accent2); border-left-color: var(--accent); }
.main { flex: 1; overflow-y: auto; padding: 32px 48px; }
.page { max-width: 720px; }
.page h1 { font-size: 22px; color: var(--accent); margin-bottom: 4px; }
.page .subject { font-size: 12px; color: var(--text-muted); margin-bottom: 20px; }
.page h2 { font-size: 15px; color: #fff; margin: 24px 0 10px; border-bottom: 1px solid var(--border); padding-bottom: 5px; }
.page h3 { font-size: 14px; color: var(--accent); margin: 14px 0 8px; }
.page p { font-size: 14px; line-height: 1.75; color: var(--text); margin: 8px 0; }
.page blockquote { border-left: 3px solid var(--accent); padding: 8px 16px; margin: 14px 0; background: rgba(233,69,96,0.08); border-radius: 0 6px 6px 0; }
.page blockquote p { margin: 3px 0; color: #ccc; font-size: 13px; }
.page blockquote strong { color: var(--accent); }
.page code { background: var(--code-bg); padding: 2px 6px; border-radius: 4px; font-size: 12px; color: #f97583; }
.page pre { background: var(--code-bg); padding: 14px; border-radius: 8px; overflow-x: auto; margin: 14px 0; }
.page pre code { background: none; padding: 0; color: var(--text); font-size: 12px; }
.page table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 13px; }
.page th { background: var(--accent2); padding: 8px 12px; text-align: left; border: 1px solid var(--border); color: #fff; }
.page td { padding: 7px 12px; border: 1px solid var(--border); }
.page tr:nth-child(even) td { background: rgba(255,255,255,0.03); }
.page a.wiki-link { color: var(--accent); text-decoration: none; background: rgba(233,69,96,0.12); padding: 1px 5px; border-radius: 4px; font-size: 13px; }
.page a.wiki-link:hover { background: rgba(233,69,96,0.25); text-decoration: none; }
.backlinks { margin-top: 32px; border-top: 1px solid var(--border); padding-top: 16px; }
.backlinks h3 { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); margin-bottom: 10px; }
.backlink-list { display: flex; flex-wrap: wrap; gap: 8px; }
.backlink-item { background: var(--accent2); padding: 6px 12px; border-radius: 6px; font-size: 12px; border: 1px solid var(--border); }
.backlink-item a { color: var(--text); text-decoration: none; }
.backlink-item a:hover { color: var(--accent); }
.backlink-item .src-cat { font-size: 10px; color: var(--text-muted); }
.page ul, .page ol { padding-left: 24px; margin: 8px 0; }
.page li { font-size: 14px; line-height: 1.7; margin: 3px 0; }
.page hr { border: none; border-top: 1px solid var(--border); margin: 20px 0; }
.page .tags { margin-top: 20px; }
.page .tag { display: inline-block; background: var(--accent2); color: var(--text-muted); font-size: 11px; padding: 2px 8px; border-radius: 10px; margin: 2px; }
.index-page h1 { font-size: 26px; color: var(--accent); margin-bottom: 8px; }
.index-page .stats { display: flex; gap: 16px; margin: 16px 0 32px; flex-wrap: wrap; }
.index-page .stat { background: var(--accent2); padding: 14px 20px; border-radius: 8px; text-align: center; min-width: 80px; }
.index-page .stat .num { font-size: 26px; color: var(--accent); font-weight: 700; }
.index-page .stat .label { font-size: 11px; color: var(--text-muted); margin-top: 4px; }
.cat-section { margin: 28px 0; }
.cat-section h2 { font-size: 15px; color: #fff; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
.cat-section h2 .count { background: var(--accent2); color: var(--text-muted); font-size: 11px; padding: 2px 8px; border-radius: 10px; }
.page-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px; }
.page-card { background: var(--accent2); border-radius: 8px; padding: 12px 14px; border: 1px solid var(--border); transition: border-color 0.15s; }
.page-card:hover { border-color: var(--accent); }
.page-card a { color: var(--text); text-decoration: none; display: block; }
.page-card .card-title { font-size: 13px; font-weight: 600; color: #fff; margin-bottom: 3px; }
.page-card .card-desc { font-size: 11px; color: var(--text-muted); line-height: 1.4; }
.back-link { display: inline-block; margin-bottom: 16px; color: var(--accent); font-size: 12px; }
.back-link:hover { text-decoration: underline; }
@media (max-width: 768px) {
  .sidebar { display: none; }
  .main { padding: 20px; }
}
"""

def href_for(page, is_index=False):
    prefix = '' if is_index else '../'
    return f'{prefix}{page["category"]}/{page["name"]}.html'


def resolve_wiki_links(body, pages, is_index=False):
    """Replace [[category/name]] or [[name]] with proper HTML links"""
    def replace_link(m):
        raw = m.group(1).strip()
        target = None
        if '/' in raw:
            # Already has category
            for slug, p in pages.items():
                if slug == raw or f"{p['category']}/{p['name']}" == raw:
                    target = slug
                    break
        else:
            # Search by name
            for slug, p in pages.items():
                if p['name'] == raw:
                    target = slug
                    break
        if target and target in pages:
            tp = pages[target]
            return f'<a href="{href_for(tp, is_index=is_index)}" class="wiki-link">{raw}</a>'
        return raw
    return re.sub(r'\[\[([^\]]+)\]\]', replace_link, body)

def build_sidebar(cats, current=None, is_index=False):
    html = '<div class="sidebar">\n'
    html += '<h2>导航</h2>\n'
    is_graph = current == 'graph.html'
    html += f'<a href="graph.html" class="{"active" if is_graph else ""}">📊 知识图谱</a>\n'
    html += '<h2>人物 <span class="cat-count">9</span></h2>\n'
    persons = [
        ('person_ShiGu.html', '矢孤'),
        ('person_Woo.html', 'Woo'),
        ('person_XuYapeng.html', '胥亚朋'),
        ('person_YunHuan.html', '沄涣'),
        ('person_YePeng.html', '叶鹏'),
        ('person_icekernel.html', 'icekernel'),
        ('person_WenBo.html', '文博'),
        ('person_Bin Ma.html', 'Bin Ma'),
        ('person_LeiLei.html', '雷雷'),
    ]
    for slug, name in persons:
        cl = 'active' if slug == current else ''
        html += f'<a href="{slug}" class="{cl}">{name}</a>\n'
    html += '<h2>概念分类</h2>\n'
    for cat, items in cats.items():
        html += f'<h2>{cat} <span class="cat-count">{len(items)}</span></h2>\n'
        for slug, p in items:
            cl = 'active' if slug == current else ''
            html += f'<a href="{href_for(p, is_index=is_index)}" class="{cl}">{p["name"]}</a>\n'
    html += '</div>\n'
    return html
def page_template(title, content, sidebar, concept_count, wiki_link_count, is_index=False):
    cls = 'index-page' if is_index else 'page'
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — P2PTalk Wiki</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>P2PTalk Wiki</h1>
  <span class="subtitle">知识图谱 · <a href="https://github.com/dapingzui/p2ptalk-wiki" target="_blank">{concept_count}概念页</a> · {wiki_link_count}条链接</span>
</header>
<div class="container">
{sidebar}
<div class="main">
<div class="{cls}">
{content}
</div></div></div></body></html>"""

# Pre-process: make wiki links clickable in body
for slug, p in pages.items():
    p['body_html'] = resolve_wiki_links(p['body'], pages, is_index=False)

# Generate each concept page
for slug, p in pages.items():
    title = p['meta'].get('subject', p['name'])
    sidebar = build_sidebar(cats, slug, is_index=False)
    content = f'<a href="../index.html" class="back-link">← 总览</a>\n'
    content += f'<h1>{title}</h1>\n'
    
    if p['meta'].get('tags'):
        tags = p['meta'].get('tags', '')
        tag_list = [t.strip() for t in tags.strip('[]').split(',')]
        content += '<div class="tags">' + ''.join(f'<span class="tag">{t}</span>' for t in tag_list) + '</div>\n'
    
    md = markdown.Markdown(extensions=['tables', 'fenced_code'])
    content += md.convert(p['body_html'])
    
    # Backlinks section
    if slug in all_wiki_links and all_wiki_links[slug]:
        content += '\n<div class="backlinks">\n'
        content += '<h3>↩ 被引用 ({n} 页)</h3>\n'.format(n=len(all_wiki_links[slug]))
        content += '<div class="backlink-list">\n'
        for src_slug in sorted(all_wiki_links[slug]):
            sp = pages[src_slug]
            content += f'<div class="backlink-item"><a href="../{sp["category"]}/{sp["name"]}.html">{sp["name"]}</a> <span class="src-cat">in {sp["category"]}</span></div>\n'
        content += '</div>\n</div>\n'

    html = page_template(title, content, sidebar, len(pages), sum(len(v) for v in all_wiki_links.values()))
    cat_dir = os.path.join(out, p['category'])
    os.makedirs(cat_dir, exist_ok=True)
    with open(os.path.join(cat_dir, f'{p["name"]}.html'), 'w') as f:
        f.write(html)

backlink_counts = {k: len(v) for k, v in all_wiki_links.items() if v}

# Generate index page
sidebar = build_sidebar(cats, None, is_index=True)
content = '<h1>P2PTalk 知识图谱</h1>\n'
content += '<p style="color:#a0a0a0;font-size:13px;margin-top:4px;margin-bottom:20px;">基于真实讨论提炼的概念知识图谱。每个概念页含：核心引述 + 讨论要点 + 相关链接。</p>\n'
content += '<div class="stats">'
content += f'<div class="stat"><div class="num">{len(pages)}</div><div class="label">概念页</div></div>'
content += f'<div class="stat"><div class="num">{sum(len(v) for v in all_wiki_links.values())}</div><div class="label">知识链接</div></div>'
content += f'<div class="stat"><div class="num">{len(backlink_counts)}</div><div class="label">被引用页面</div></div>'
content += '<div class="stat"><div class="num">9</div><div class="label">参与者</div></div>'
content += '</div>\n'

for cat, items in cats.items():
    content += f'<div class="cat-section">\n'
    content += f'<h2>{cat} <span class="count">{len(items)}</span></h2>\n'
    content += '<div class="page-list">\n'
    for slug, p in items:
        title = p['meta'].get('subject', p['name'])
        bl_count = len(all_wiki_links.get(slug, []))
        bl_tag = f'<span class="src-cat" style="margin-left:4px;">↩ {bl_count}</span>' if bl_count else ''
        content += f'<div class="page-card"><a href="{p["category"]}/{p["name"]}.html"><div class="card-title">{p["name"]}{bl_tag}</div><div class="card-desc">{title}</div></a></div>\n'
    content += '</div>\n</div>\n'

html = page_template('P2PTalk Wiki', content, sidebar, len(pages), sum(len(v) for v in all_wiki_links.values()), is_index=True)
with open(os.path.join(out, 'index.html'), 'w') as f:
    f.write(html)

print(f'Generated: {out}')
print(f'Files: {len(pages) + 1} HTML pages')
top = sorted(backlink_counts.items(), key=lambda x: -x[1])[:5]
print('Top linked pages:')
for slug, n in top:
    print(f'  {slug}: {n} backlinks')
