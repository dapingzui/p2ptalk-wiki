const stateMap = {
  trend_continuation: '趋势延续',
  short_squeeze_risk: '逼空风险',
  long_liquidation_risk: '多头清算风险',
  overheated: '过热拥挤',
  chop_no_trade: '震荡/不交易',
};

const actionMap = {
  trend_continuation: '顺势看，等回踩确认，不追极端拉升。',
  short_squeeze_risk: '向上加速风险高，别逆势空。',
  long_liquidation_risk: '小心下破连锁清算，不急着抄底。',
  overheated: '拥挤过热，减仓/不追高优先。',
  chop_no_trade: '没有明显 edge，少动或者不交易。',
};

function fmtNum(v, digits = 2) {
  if (v === null || v === undefined || Number.isNaN(v)) return '-';
  return Number(v).toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

function setBadge(risk) {
  const el = document.getElementById('statusBadge');
  el.textContent = risk || 'UNKNOWN';
  el.className = 'badge ' + (risk === 'LOW' ? 'good' : risk === 'MEDIUM' ? 'warn' : risk === 'HIGH' ? 'bad' : 'neutral');
}

async function load() {
  const res = await fetch('/api/snapshot');
  if (!res.ok) throw new Error('load failed');
  const data = await res.json();
  const s = data.snapshot;
  const v = data.verdict;

  document.getElementById('stateName').textContent = stateMap[v.state] || v.state;
  document.getElementById('actionBias').textContent = actionMap[v.state] || '-';
  document.getElementById('riskLevel').textContent = v.risk;
  document.getElementById('confidence').textContent = v.confidence;
  document.getElementById('timestamp').textContent = new Date(s.ts * 1000).toLocaleString();
  document.getElementById('price').textContent = '$' + fmtNum(s.price, 2);
  document.getElementById('oi').textContent = fmtNum(s.oi, 0);
  document.getElementById('funding').textContent = fmtNum(s.funding, 4) + '%';
  document.getElementById('longLiq').textContent = '$' + fmtNum(s.long_liq_24h, 0);
  document.getElementById('shortLiq').textContent = '$' + fmtNum(s.short_liq_24h, 0);
  document.getElementById('sources').textContent = `liq:${data.liquidation_source} | oi:${data.oi_source} | funding:${data.funding_source}`;

  const sm = document.getElementById('structureMetrics');
  sm.innerHTML = '';
  Object.entries(v.metrics).forEach(([k, val]) => {
    const div = document.createElement('div');
    div.className = 'metric';
    const cls = typeof val === 'number' && val < 0 ? 'down' : 'up';
    div.innerHTML = `<span>${k}</span><strong class="${cls}">${val}</strong>`;
    sm.appendChild(div);
  });

  const tags = document.getElementById('tags');
  tags.innerHTML = '';
  (v.tags || []).forEach(tag => {
    const span = document.createElement('span');
    span.className = 'tag';
    span.textContent = tag;
    tags.appendChild(span);
  });
  if (!v.tags || !v.tags.length) {
    const span = document.createElement('span');
    span.className = 'tag';
    span.textContent = 'none';
    tags.appendChild(span);
  }

  const reportRes = await fetch('/api/report');
  document.getElementById('rawReport').textContent = await reportRes.text();
  setBadge(v.risk);
}

document.getElementById('refreshBtn').addEventListener('click', async () => {
  document.getElementById('statusBadge').textContent = '刷新中';
  await fetch('/api/refresh', { method: 'POST' });
  await load();
});

load().catch(err => {
  document.getElementById('statusBadge').textContent = '加载失败';
  document.getElementById('rawReport').textContent = String(err);
});
