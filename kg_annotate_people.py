#!/usr/bin/env python3
"""Add person annotations to concept nodes (not separate nodes)."""
import re, json
from pathlib import Path

with open('/tmp/p2ptalk_processed.json') as f:
    data = json.load(f)

all_msgs = data['all_messages']

# Build concept_slug -> [person1, person2, ...] mapping
concept_people = {}
for m in all_msgs:
    for c in m.get('concepts', []):
        concept_people.setdefault(c, set()).add(m['person'])

# Fresh clone
import subprocess
subprocess.run(['rm', '-rf', '/tmp/p2ptalk-wiki2'], check=True)
subprocess.run(['git', 'clone', 'https://github.com/dapingzui/p2ptalk-wiki.git', '/tmp/p2ptalk-wiki2'], check=True)

html = Path('/tmp/p2ptalk-wiki2/graph.html').read_text(encoding='utf-8')

# Extract DATA
m = re.search(r'const DATA = (\{.*?\})\s*;', html, re.DOTALL)
raw = m.group(1)
data_obj = json.loads(raw)
nodes = data_obj['nodes']
links = data_obj['links']

print(f'Original: {len(nodes)} nodes, {len(links)} links')

# Remove person nodes (category=='people') - they are at the end
person_indices = {i for i, n in enumerate(nodes) if n['category'] == 'people'}
concept_nodes = [n for i, n in enumerate(nodes) if n['category'] != 'people']
print(f'After removing {len(person_indices)} person nodes: {len(concept_nodes)} concept nodes')

# Build index maps
old_id_to_new_idx = {nodes[i]['id']: i for i, n in enumerate(nodes) if i not in person_indices}
# new_idx: old_position -> new_position
old_pos_to_new_idx = {}
new_pos = 0
for i, n in enumerate(nodes):
    if i not in person_indices:
        old_pos_to_new_idx[i] = new_pos
        new_pos += 1

# Filter and re-index concept-concept links
new_links = []
for l in links:
    s = l['source'] if isinstance(l['source'], int) else l['source'].get('id', l['source'])
    t = l['target'] if isinstance(l['target'], int) else l['target'].get('id', l['target'])
    if s not in person_indices and t not in person_indices:
        new_links.append({'source': old_pos_to_new_idx[s], 'target': old_pos_to_new_idx[t]})

print(f'Concept-concept links: {len(new_links)}')

# Add people field to each concept node
for n in concept_nodes:
    people_list = sorted(concept_people.get(n['id'], []))
    n['people'] = people_list

# Show some samples
for n in concept_nodes[:5]:
    print(f'  {n["id"]}: {n["people"]}')

# Re-serialize
new_data = json.dumps({'nodes': concept_nodes, 'links': new_links}, ensure_ascii=False)
js_data = 'const DATA = ' + new_data + ';'
html = html[:m.start()] + js_data + html[m.end():]

# Update subtitle and stats
html = html.replace('双向链接可视化 · 58节点 · 170条关系', f'双向链接可视化 · {len(concept_nodes)}概念 · {len(new_links)}条关系')
html = html.replace('<span id="stat-nodes">58</span> 节点 · <span id="stat-links">170</span> 关系',
                    f'<span id="stat-nodes">{len(concept_nodes)}</span> 概念 · <span id="stat-links">{len(new_links)}</span> 关系')

# Remove the 👥 filter button and person legend item added in previous commit
html = html.replace('<button class="filter-btn" id="btn-people" onclick="filterCategory(\'people\')">👥 参与者</button>', '')
html = html.replace('<div class="legend-item" onclick="filterCategory(\'people\')"><div class="legend-dot" style="background:#feca57"></div><span>参与者 (8)</span></div>', '')

Path('/tmp/p2ptalk-wiki2/graph.html').write_text(html, encoding='utf-8')

# Copy back
import shutil
shutil.copy('/tmp/p2ptalk-wiki2/graph.html', '/tmp/p2ptalk-wiki/graph.html')
print('Done - copied to p2ptalk-wiki')
