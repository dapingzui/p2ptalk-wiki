#!/usr/bin/env python3
"""Add person chip rendering to concept nodes in graph.html."""
import re
from pathlib import Path

html = Path('/tmp/p2ptalk-wiki/graph.html').read_text(encoding='utf-8')

# Find the section where label.text(d => d.name) is set and add a renderLabel helper
# Find the simulation definition area and add helper before it

# Add a renderLabel function that shows name + person chips
render_label_js = '''
// Render label: concept name + participant chips
function renderLabel(el, d) {
  el.selectAll('*').remove();
  el.append('tspan').text(d.name).attr('x', 0).attr('dy', 0).attr('text-anchor', 'middle');
  if (d.people && d.people.length > 0) {
    const names = d.people.slice(0, 5).join('·');
    el.append('tspan').text(names).attr('x', 0).attr('dy', '1.1em')
      .attr('text-anchor', 'middle').attr('fill', '#feca57').attr('font-size', '8px').attr('opacity', 0.85);
  }
}

'''

# Insert before simulation definition
sim_idx = html.find('simulation = d3.forceSimulation')
if sim_idx < 0:
    print('WARNING: simulation not found')
else:
    html = html[:sim_idx] + render_label_js + html[sim_idx:]

# Replace all label.text(d => d.name) with label.each(renderLabel)
# But we need to be careful about the different contexts

# Main render: label.text(d => d.name)
html = html.replace(
    'label.text(d => d.name);',
    'label.each(function(d) { renderLabel(d3.select(this), d); });'
)

# In btn-all: label.text(d => d.name).style('opacity', 1)
html = html.replace(
    "label.text(d => d.name).style('opacity', 1);",
    "label.each(function(d) { renderLabel(d3.select(this), d); d3.select(this).style('opacity', 1); });"
)

# In search input handler - need to handle empty vs match cases
old_search = '''label.text(d => {
    const match = d.name.toLowerCase().includes(q) || (d.subject && d.subject.toLowerCase().includes(q));
    return match ? d.name : '';
  });'''

new_search = '''label.each(function(d) {
    const match = d.name.toLowerCase().includes(q) || (d.subject && d.subject.toLowerCase().includes(q));
    if (match) { renderLabel(d3.select(this), d); d3.select(this).style('opacity', 1); }
    else { d3.select(this).selectAll('*').remove(); }
  });'''

html = html.replace(old_search, new_search)

# In filterCategory: label.text(d => d.category === cat ? d.name : '')
# and label.text(d => connectedIds.has(d.id) ? d.name : '')
html = html.replace(
    "label.text(d => d.category === cat ? d.name : '');",
    "label.each(function(d) { if (d.category === cat) { renderLabel(d3.select(this), d); } else { d3.select(this).selectAll('*').remove(); } });"
)
html = html.replace(
    "label.text(d => connectedIds.has(d.id) ? d.name : '');",
    "label.each(function(d) { if (connectedIds.has(d.id)) { renderLabel(d3.select(this), d); } else { d3.select(this).selectAll('*').remove(); } });"
)

Path('/tmp/p2ptalk-wiki/graph.html').write_text(html, encoding='utf-8')
print('Done - renderLabel added')
