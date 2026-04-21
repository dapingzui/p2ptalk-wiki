import os, re, json
from collections import defaultdict

src = '/Users/ice/.openclaw/workspace/inbox/p2ptalk/KnowledgeGraph'
out = '/Users/ice/Downloads/P2PTalk_KG_HTML'

# Load pages
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
        }

# Build link graph
nodes = []
slug_to_idx = {}
node_map = {}

# Category colors
cat_colors = {
    'atom': '#e94560',
    'consensus': '#0f9b8e',
    'broadcast': '#9b59b6',
    'market': '#f39c12',
    'ai': '#3498db',
    'security': '#e67e22',
    'math': '#1abc9c',
    'meeting': '#95a5a6',
}

for slug, p in pages.items():
    idx = len(nodes)
    slug_to_idx[slug] = idx
    nodes.append({
        'id': slug,
        'name': p['name'],
        'category': p['category'],
        'subject': p['meta'].get('subject', ''),
        'url': f'{p["category"]}/{p["name"]}.html',
        'color': cat_colors.get(p['category'], '#888'),
    })

links = []
link_set = set()
for src_slug, p in pages.items():
    for m in re.finditer(r'\[\[([^\]]+)\]\]', p['body']):
        raw = m.group(1).strip()
        target = None
        if '/' in raw:
            for slug in pages:
                if slug == raw or slug.endswith(f'/{raw}'):
                    target = slug
                    break
        else:
            for slug, pp in pages.items():
                if pp['name'] == raw:
                    target = slug
                    break
        if target and target in slug_to_idx and target != src_slug:
            key = (slug_to_idx[src_slug], slug_to_idx[target])
            if key not in link_set:
                link_set.add(key)
                links.append({'source': slug_to_idx[src_slug], 'target': slug_to_idx[target]})

# Category stats
from collections import Counter
cat_counts = Counter(p['category'] for p in pages.values())
cat_list = sorted(cat_counts.items())

# Category order for legend
cat_order = ['atom', 'consensus', 'broadcast', 'meeting', 'market', 'ai', 'security', 'math']

graph_data = {'nodes': nodes, 'links': links}

HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>P2PTalk 知识图谱 — 动态关系图</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 100%; height: 100%; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0d1117; color: #e6edf3; }
#toolbar { position: fixed; top: 0; left: 0; right: 0; height: 52px; background: rgba(13,17,23,0.95); border-bottom: 1px solid #30363d; display: flex; align-items: center; padding: 0 20px; gap: 24px; z-index: 100; backdrop-filter: blur(8px); }
#toolbar h1 { font-size: 15px; color: #e94560; font-weight: 600; }
#toolbar .subtitle { font-size: 12px; color: #8b949e; }
#toolbar .actions { margin-left: auto; display: flex; gap: 8px; }
.btn { background: #21262d; border: 1px solid #30363d; color: #c9d1d9; font-size: 12px; padding: 5px 12px; border-radius: 6px; cursor: pointer; }
.btn:hover { background: #30363d; border-color: #8b949e; }
#graph-container { width: 100%; height: 100%; }
svg { width: 100%; height: 100%; }
circle { cursor: pointer; stroke: rgba(255,255,255,0.2); stroke-width: 1.5px; transition: r 0.15s; }
circle:hover { stroke: rgba(255,255,255,0.6); stroke-width: 2px; }
line { stroke: rgba(255,255,255,0.08); stroke-width: 1px; pointer-events: none; }
text { pointer-events: none; font-size: 10px; fill: #8b949e; }
#panel { position: fixed; top: 52px; right: 0; bottom: 0; width: 320px; background: rgba(13,17,23,0.97); border-left: 1px solid #30363d; overflow-y: auto; display: none; z-index: 99; backdrop-filter: blur(8px); }
#panel.active { display: block; }
#panel-header { padding: 16px; border-bottom: 1px solid #30363d; }
#panel-header h2 { font-size: 15px; color: #e94560; margin-bottom: 4px; }
#panel-header .cat-tag { font-size: 11px; background: #21262d; padding: 2px 8px; border-radius: 10px; color: #8b949e; }
#panel-header .subject { font-size: 12px; color: #8b949e; margin-top: 8px; line-height: 1.5; }
#panel-close { float: right; background: none; border: none; color: #8b949e; font-size: 18px; cursor: pointer; padding: 0 4px; }
#panel-close:hover { color: #fff; }
#panel-body { padding: 16px; }
#panel-body h3 { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #8b949e; margin: 16px 0 8px; }
#panel-body .link-list { display: flex; flex-direction: column; gap: 6px; }
#panel-body .link-item { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 8px 10px; font-size: 12px; cursor: pointer; transition: border-color 0.15s; }
#panel-body .link-item:hover { border-color: #e94560; }
#panel-body .link-item a { color: #c9d1d9; text-decoration: none; display: flex; align-items: center; gap: 6px; }
#panel-body .link-item .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
#panel-body .link-item.empty { color: #8b949e; font-style: italic; }
#legend { position: fixed; bottom: 20px; left: 20px; background: rgba(13,17,23,0.92); border: 1px solid #30363d; border-radius: 8px; padding: 12px 14px; z-index: 50; backdrop-filter: blur(8px); }
#legend h4 { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #8b949e; margin-bottom: 8px; }
.legend-item { display: flex; align-items: center; gap: 7px; font-size: 12px; margin: 4px 0; cursor: pointer; }
.legend-item:hover { color: #fff; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
#stats { position: fixed; bottom: 20px; right: 20px; background: rgba(13,17,23,0.92); border: 1px solid #30363d; border-radius: 8px; padding: 10px 14px; z-index: 50; font-size: 11px; color: #8b949e; backdrop-filter: blur(8px); }
#stats span { color: #e94560; font-weight: 600; }
#search { background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; font-size: 13px; padding: 6px 12px; border-radius: 6px; width: 200px; outline: none; }
#search:focus { border-color: #e94560; }
#search::placeholder { color: #484f58; }
#filter-group { display: flex; align-items: center; gap: 6px; }
.filter-btn { background: none; border: 1px solid #30363d; color: #8b949e; font-size: 11px; padding: 4px 8px; border-radius: 4px; cursor: pointer; }
.filter-btn:hover { border-color: #8b949e; color: #c9d1d9; }
.filter-btn.active { border-color: #e94560; color: #e94560; }
</style>
</head>
<body>
<div id="toolbar">
  <h1>P2PTalk 知识图谱</h1>
  <span class="subtitle">双向链接可视化 · 50概念 · 88条关系</span>
  <div id="filter-group">
    <input type="text" id="search" placeholder="搜索概念...">
  </div>
  <div class="actions">
    <button class="btn" id="btn-reset">重置视图</button>
    <button class="btn" id="btn-all">显示全部</button>
  </div>
</div>

<div id="graph-container"></div>

<div id="panel">
  <div id="panel-header">
    <button id="panel-close">×</button>
    <h2 id="panel-title">—</h2>
    <span class="cat-tag" id="panel-cat">—</span>
    <p class="subject" id="panel-subject">—</p>
  </div>
  <div id="panel-body">
    <h3>引用此页 ↩</h3>
    <div class="link-list" id="panel-backlinks"></div>
    <h3>此页引用 →</h3>
    <div class="link-list" id="panel-links"></div>
  </div>
</div>

<div id="legend">
  <h4>分类</h4>
  <div id="legend-items"></div>
</div>

<div id="stats">
  <span id="stat-nodes">50</span> 节点 · <span id="stat-links">88</span> 关系
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script>
const DATA = ''' + json.dumps(graph_data, ensure_ascii=False) + ''';

const catColors = ''' + json.dumps(cat_colors, ensure_ascii=False) + ''';
const catOrder = ''' + json.dumps(cat_order, ensure_ascii=False) + ''';

// Build adjacency
const outLinks = {};
const inLinks = {};
DATA.nodes.forEach(n => { outLinks[n.id] = []; inLinks[n.id] = []; });
DATA.links.forEach(l => {
  const s = DATA.nodes[l.source].id || l.source;
  const t = DATA.nodes[l.target].id || l.target;
  if (typeof l.source === 'object') l.source = l.source.id;
  if (typeof l.target === 'object') l.target = l.target.id;
  outLinks[s] = outLinks[s] || [];
  inLinks[t] = inLinks[t] || [];
  outLinks[s].push(t);
  inLinks[t].push(s);
});

const container = document.getElementById('graph-container');
const width = container.clientWidth;
const height = container.clientHeight;

// Simulation
const simulation = d3.forceSimulation(DATA.nodes)
  .force('link', d3.forceLink(DATA.links).id(d => d.id).distance(90).strength(0.4))
  .force('charge', d3.forceManyBody().strength(-280))
  .force('center', d3.forceCenter(width / 2, height / 2))
  .force('collision', d3.forceCollide(18))
  .alphaDecay(0.028);

const svg = d3.select('#graph-container').append('svg')
  .attr('width', width)
  .attr('height', height);

const g = svg.append('g');

// Zoom
const zoom = d3.zoom()
  .scaleExtent([0.2, 4])
  .on('zoom', e => g.attr('transform', e.transform));
svg.call(zoom);
svg.on('dblclick.zoom', null);

// Links
const link = g.append('g').selectAll('line')
  .data(DATA.links)
  .join('line')
  .attr('class', 'link')
  .attr('stroke', 'rgba(255,255,255,0.1)');

// Node groups
const node = g.append('g').selectAll('g')
  .data(DATA.nodes)
  .join('g')
  .attr('class', 'node-group')
  .call(d3.drag()
    .on('start', (e, d) => {
      if (!e.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x; d.fy = d.y;
    })
    .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
    .on('end', (e, d) => {
      if (!e.active) simulation.alphaTarget(0);
      d.fx = null; d.fy = null;
    }));

// Circles
const circle = node.append('circle')
  .attr('r', d => {
    const conn = (outLinks[d.id]?.length || 0) + (inLinks[d.id]?.length || 0);
    return 8 + Math.min(conn * 1.5, 14);
  })
  .attr('fill', d => d.color)
  .attr('opacity', 0.85);

// Labels (only show for high-degree nodes by default)
const label = node.append('text')
  .text(d => d.name)
  .attr('text-anchor', 'middle')
  .attr('dy', d => {
    const conn = (outLinks[d.id]?.length || 0) + (inLinks[d.id]?.length || 0);
    return 8 + Math.min(conn * 1.5, 14) + 12;
  })
  .style('font-size', '10px')
  .style('fill', '#8b949e')
  .style('pointer-events', 'none');

// Click to open panel
node.on('click', (e, d) => {
  e.stopPropagation();
  openPanel(d);
});

// Click background to close
svg.on('click', () => closePanel());

// Tick
simulation.on('tick', () => {
  link
    .attr('x1', d => d.source.x)
    .attr('y1', d => d.source.y)
    .attr('x2', d => d.target.x)
    .attr('y2', d => d.target.y);
  node.attr('transform', d => `translate(${d.x},${d.y})`);
});

// Panel
function openPanel(d) {
  document.getElementById('panel').classList.add('active');
  document.getElementById('panel-title').textContent = d.name;
  document.getElementById('panel-cat').textContent = d.category;
  document.getElementById('panel-cat').style.background = d.color + '33';
  document.getElementById('panel-cat').style.color = d.color;
  document.getElementById('panel-subject').textContent = d.subject || '—';

  const bl = document.getElementById('panel-backlinks');
  const ol = document.getElementById('panel-links');
  bl.innerHTML = '';
  ol.innerHTML = '';

  const inL = inLinks[d.id] || [];
  const outL = outLinks[d.id] || [];

  if (inL.length === 0) bl.innerHTML = '<div class="link-item empty">暂无反向引用</div>';
  inL.forEach(tid => {
    const n = DATA.nodes.find(x => x.id === tid);
    if (!n) return;
    bl.innerHTML += `<div class="link-item" onclick="jumpTo('${n.id}')"><span class="dot" style="background:${n.color}"></span><a href="${n.url}">${n.name}</a><span style="color:#8b949e;font-size:10px;margin-left:auto">in ${n.category}</span></div>`;
  });

  if (outL.length === 0) ol.innerHTML = '<div class="link-item empty">暂无引用</div>';
  outL.forEach(tid => {
    const n = DATA.nodes.find(x => x.id === tid);
    if (!n) return;
    ol.innerHTML += `<div class="link-item" onclick="jumpTo('${n.id}')"><span class="dot" style="background:${n.color}"></span><a href="${n.url}">${n.name}</a><span style="color:#8b949e;font-size:10px;margin-left:auto">in ${n.category}</span></div>`;
  });

  // Highlight
  circle.attr('opacity', d => {
    if (d.id === d.id || inL.includes(d.id) || outL.includes(d.id)) return 1;
    return 0.2;
  });
  link.attr('stroke', l => {
    const s = l.source.id || l.source;
    const t = l.target.id || l.target;
    if (s === d.id || t === d.id) return 'rgba(233,69,96,0.5)';
    return 'rgba(255,255,255,0.04)';
  }).attr('stroke-width', l => {
    const s = l.source.id || l.source;
    const t = l.target.id || l.target;
    return (s === d.id || t === d.id) ? 2 : 1;
  });
}

function closePanel() {
  document.getElementById('panel').classList.remove('active');
  circle.attr('opacity', 0.85);
  link.attr('stroke', 'rgba(255,255,255,0.1)').attr('stroke-width', 1);
}

window.jumpTo = function(id) {
  const n = DATA.nodes.find(x => x.id === id);
  if (n) {
    openPanel(n);
    // Center view on node
    svg.transition().duration(500).call(
      zoom.transform,
      d3.zoomIdentity.translate(width/2 - n.x, height/2 - n.y)
    );
  }
};

// Reset button
document.getElementById('btn-reset').onclick = () => {
  simulation.alpha(0.8).restart();
  svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
  closePanel();
};

// Show all
document.getElementById('btn-all').onclick = () => {
  closePanel();
  circle.attr('opacity', 0.85);
  label.text(d => d.name);
};

// Search
const searchInput = document.getElementById('search');
searchInput.oninput = () => {
  const q = searchInput.value.trim().toLowerCase();
  if (!q) {
    circle.attr('opacity', 0.85);
    label.text(d => d.name).style('opacity', 1);
    return;
  }
  circle.attr('opacity', d => {
    const match = d.name.toLowerCase().includes(q) || (d.subject && d.subject.toLowerCase().includes(q));
    return match ? 1 : 0.08;
  });
  label.text(d => {
    const match = d.name.toLowerCase().includes(q) || (d.subject && d.subject.toLowerCase().includes(q));
    return match ? d.name : '';
  });
};

// Legend
const legendEl = document.getElementById('legend-items');
catOrder.forEach(cat => {
  const count = DATA.nodes.filter(n => n.category === cat).length;
  if (count === 0) return;
  const color = catColors[cat];
  const item = document.createElement('div');
  item.className = 'legend-item';
  item.innerHTML = `<span class="legend-dot" style="background:${color}"></span>${cat} (${count})`;
  item.onclick = () => {
    const others = DATA.nodes.filter(n => n.category !== cat);
    circle.attr('opacity', d => d.category === cat ? 1 : 0.08);
    label.text(d => d.category === cat ? d.name : '');
  };
  legendEl.appendChild(item);
});

// Stats
document.getElementById('stat-nodes').textContent = DATA.nodes.length;
document.getElementById('stat-links').textContent = DATA.links.length;

// Center initially
svg.call(zoom.transform, d3.zoomIdentity.translate(width*0.05, height*0.05).scale(0.85));
</script>
</body>
</html>'''

with open(os.path.join(out, 'graph.html'), 'w') as f:
    f.write(HTML)

print(f'Graph page written to {out}/graph.html')
print(f'Nodes: {len(nodes)}, Links: {len(links)}')
