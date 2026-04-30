#!/usr/bin/env python3
"""Fix graph.html: add filterCategory function and fix person node interactions."""
import re
from pathlib import Path

html = Path('/tmp/p2ptalk-wiki/graph.html').read_text(encoding='utf-8')

# 1. Add filterCategory function before buildTimeFilter
filter_category_js = '''
// Filter by category
function filterCategory(cat) {
  if (cat === 'people') {
    // Show person nodes + their connected concept nodes
    const personIds = DATA.nodes.filter(n => n.category === 'people').map(n => n.id);
    const connectedIds = new Set();
    personIds.forEach(pid => connectedIds.add(pid));
    DATA.links.forEach(l => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      if (personIds.includes(s)) connectedIds.add(t);
      if (personIds.includes(t)) connectedIds.add(s);
    });
    circle.attr('opacity', d => connectedIds.has(d.id) ? 1 : 0.08);
    label.text(d => connectedIds.has(d.id) ? d.name : '');
  } else {
    circle.attr('opacity', d => d.category === cat ? 1 : 0.08);
    label.text(d => d.category === cat ? d.name : '');
  }
}

'''

# Find position before buildTimeFilter
idx = html.find('// Time filter\nfunction buildTimeFilter()')
if idx < 0:
    print('WARNING: buildTimeFilter not found')
else:
    html = html[:idx] + filter_category_js + html[idx:]

# 2. Fix person node click: if it's a person node, open their page directly
# The current openPanel handles concept nodes. For person nodes, redirect to person page.
old_node_click = '''node.on('click', (e, d) => {
  e.stopPropagation();
  openPanel(d);
});'''

new_node_click = '''node.on('click', (e, d) => {
  e.stopPropagation();
  if (d.category === 'people') {
    window.open(d.url, '_blank');
  } else {
    openPanel(d);
  }
});'''

html = html.replace(old_node_click, new_node_click)

# 3. Add person color to catColors if not present
if "'people':" not in html:
    html = html.replace(
        "const catColors = {",
        "const catColors = {\n  'people': '#feca57',"
    )

Path('/tmp/p2ptalk-wiki/graph.html').write_text(html, encoding='utf-8')
print('Done: filterCategory added, person nodes open person page')
