#!/usr/bin/env python3
"""Add person nodes and edges to P2PTalk knowledge graph."""
import re, json
from pathlib import Path

with open('/tmp/p2ptalk_processed.json') as f:
    data = json.load(f)

person_concepts = data['person_concepts']
all_msgs = data['all_messages']

# Build person -> {concept: msg_count} from all_messages
person_msg_concepts = {}
for m in all_msgs:
    p = m['person']
    for c in m.get('concepts', []):
        person_msg_concepts.setdefault(p, {}).setdefault(c, 0)
        person_msg_concepts[p][c] += 1

# Read graph.html
html = Path('/tmp/p2ptalk-wiki/graph.html').read_text(encoding='utf-8')

# Extract and parse DATA
m = re.search(r'const DATA = (\{.*?\})\s*;', html, re.DOTALL)
raw = m.group(1)
data_obj = json.loads(raw)
nodes = data_obj['nodes']
links = data_obj['links']

print(f'Before: {len(nodes)} nodes, {len(links)} links')

# Build concept slug -> node index map
concept_idx = {n['id']: i for i, n in enumerate(nodes)}

# Add person nodes at END
PERSON_COLOR = '#feca57'
people = ['叶鹏', '胥亚朋', '矢孤', '文博', '沄涣', 'Woo', '雷雷', 'Bin Ma']
slug_map = {
    '叶鹏': 'YePeng', '胥亚朋': 'XuYapeng', '矢孤': 'ShiGu',
    '文博': 'WenBo', '沄涣': 'YunHuan', 'Woo': 'Woo',
    '雷雷': 'LeiLei', 'Bin Ma': 'Bin_Ma'
}

new_nodes = []
new_links = []
start_idx = len(nodes)

for person in people:
    node_idx = start_idx + len(new_nodes)
    slug = slug_map.get(person, person.replace(' ', '_'))
    n_concepts = len(person_msg_concepts.get(person, {}))
    new_nodes.append({
        'id': f'person/{person}',
        'name': person,
        'category': 'people',
        'subject': f'{person} · {n_concepts}个概念',
        'url': f'person_{slug}.html',
        'color': PERSON_COLOR
    })
    for concept_slug, count in person_msg_concepts.get(person, {}).items():
        if concept_slug in concept_idx:
            new_links.append({'source': node_idx, 'target': concept_idx[concept_slug]})

all_nodes = nodes + new_nodes
all_links = links + new_links

print(f'After: {len(all_nodes)} nodes, {len(all_links)} links')
print(f'Added {len(new_nodes)} person nodes, {len(new_links)} person-concept links')

# Serialize new DATA
new_data_json = json.dumps({'nodes': all_nodes, 'links': all_links}, ensure_ascii=False)
js_data = 'const DATA = ' + new_data_json + ';'

# Replace old DATA with new DATA
html = html[:m.start()] + js_data + html[m.end():]

# Update subtitle
html = html.replace(
    '双向链接可视化 · 50概念 · 88条关系',
    f'双向链接可视化 · {len(all_nodes)}节点 · {len(all_links)}条关系'
)
html = html.replace(
    '<span id="stat-nodes">50</span> 节点 · <span id="stat-links">88</span> 关系',
    f'<span id="stat-nodes">{len(all_nodes)}</span> 节点 · <span id="stat-links">{len(all_links)}</span> 关系'
)

# Add legend item for people
legend_item = f'<div class="legend-item" onclick="filterCategory(\'people\')"><div class="legend-dot" style="background:{PERSON_COLOR}"></div><span>参与者 ({len(new_nodes)})</span></div>'
html = html.replace(
    '</div>\n</div>\n<div id="stats">',
    legend_item + '</div>\n</div>\n<div id="stats">'
)

# Add filter button
filter_btn = '<button class="filter-btn" id="btn-people" onclick="filterCategory(\'people\')">👥 参与者</button>'
html = html.replace(
    '<div id="filter-group">',
    '<div id="filter-group">' + filter_btn
)

Path('/tmp/p2ptalk-wiki/graph.html').write_text(html, encoding='utf-8')
print('Written to graph.html')
