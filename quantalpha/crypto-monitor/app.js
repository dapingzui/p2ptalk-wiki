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
let mainChart, candleSeries, oiChart, oiSeries, fundingChart, fundingSeries;
let tradeSocket;

function fmtNum(v, digits = 2) {
  if (v === null || v === undefined || Number.isNaN(v)) return '-';
  return Number(v).toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
}
function setBadge(risk) {
  const el = document.getElementById('statusBadge');
  el.textContent = risk || 'UNKNOWN';
  el.className = 'badge ' + (risk === 'LOW' ? 'good' : risk === 'MEDIUM' ? 'warn' : risk === 'HIGH' ? 'bad' : 'neutral');
}
function initCharts() {
  const common = { layout:{background:{color:'#0f162a'},textColor:'#dbe7ff'}, grid:{vertLines:{color:'#18223d'},horzLines:{color:'#18223d'}}, rightPriceScale:{borderColor:'#243255'}, timeScale:{borderColor:'#243255'} };
  mainChart = LightweightCharts.createChart(document.getElementById('chart'), { ...common, height: 410 });
  candleSeries = mainChart.addCandlestickSeries({ upColor:'#22c55e', downColor:'#ef4444', borderVisible:false, wickUpColor:'#22c55e', wickDownColor:'#ef4444' });
  oiChart = LightweightCharts.createChart(document.getElementById('oiChart'), { ...common, height: 280 });
  oiSeries = oiChart.addLineSeries({ color:'#60a5fa', lineWidth:2 });
  fundingChart = LightweightCharts.createChart(document.getElementById('fundingChart'), { ...common, height: 280 });
  fundingSeries = fundingChart.addHistogramSeries({ color:'#f59e0b' });
}
async function loadCandles() {
  const interval = document.getElementById('intervalSelect').value;
  const res = await fetch('/api/candles?interval=' + encodeURIComponent(interval));
  const data = await res.json();
  candleSeries.setData(data.candles || []);
  document.getElementById('priceLine').textContent = `interval: ${interval} | candles: ${(data.candles || []).length}`;
}
function pushTradeRow(price, qty, side, ts) {
  const tape = document.getElementById('tradeTape');
  const row = document.createElement('div');
  row.className = 'trade-row';
  row.innerHTML = `<span>${new Date(ts).toLocaleTimeString()}</span><span class="${side}">${price}</span><span class="${side}">${qty}</span>`;
  tape.prepend(row);
  while (tape.children.length > 80) tape.removeChild(tape.lastChild);
}
function connectTrades() {
  if (tradeSocket) tradeSocket.close();
  tradeSocket = new WebSocket('wss://stream.binance.com:9443/ws/btcusdt@trade');
  let buyVol = 0, sellVol = 0;
  tradeSocket.onmessage = (ev) => {
    const d = JSON.parse(ev.data);
    const price = Number(d.p).toFixed(2);
    const qty = Number(d.q).toFixed(4);
    const side = d.m ? 'sell' : 'buy';
    if (side === 'buy') buyVol += Number(d.q); else sellVol += Number(d.q);
    pushTradeRow(price, qty, side, d.T);
    document.getElementById('tapeStats').textContent = `buyVol: ${buyVol.toFixed(2)} | sellVol: ${sellVol.toFixed(2)} | imbalance: ${(buyVol - sellVol).toFixed(2)}`;
  };
}
async function loadState() {
  const [snapRes, reportRes] = await Promise.all([fetch('/api/snapshot'), fetch('/api/report')]);
  const data = await snapRes.json();
  const report = await reportRes.text();
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
  const sm = document.getElementById('structureMetrics'); sm.innerHTML = '';
  Object.entries(v.metrics).forEach(([k, val]) => {
    const div = document.createElement('div'); div.className = 'metric';
    const cls = typeof val === 'number' && val < 0 ? 'down' : 'up';
    div.innerHTML = `<span>${k}</span><strong class="${cls}">${val}</strong>`; sm.appendChild(div);
  });
  const tags = document.getElementById('tags'); tags.innerHTML = '';
  (v.tags || []).forEach(tag => { const span = document.createElement('span'); span.className='tag'; span.textContent=tag; tags.appendChild(span); });
  if (!v.tags || !v.tags.length) { const span = document.createElement('span'); span.className='tag'; span.textContent='none'; tags.appendChild(span); }
  document.getElementById('rawReport').textContent = report;
  setBadge(v.risk);
  document.getElementById('curveStats').textContent = `funding: ${fmtNum(s.funding, 4)}% | oi: ${fmtNum(s.oi, 0)}`;
  oiSeries.setData((s.history_oi || []).map((x, i) => ({ time: i + 1, value: x })));
  fundingSeries.setData((s.history_funding || []).map((x, i) => ({ time: i + 1, value: x, color: x >= 0 ? '#22c55e' : '#ef4444' })));
}
async function refreshAll() {
  await fetch('/api/refresh', { method: 'POST' });
  await Promise.all([loadState(), loadCandles()]);
}
document.getElementById('refreshBtn').addEventListener('click', refreshAll);
document.getElementById('intervalSelect').addEventListener('change', loadCandles);
initCharts();
Promise.all([loadState(), loadCandles()]).then(connectTrades).catch(err => { document.getElementById('rawReport').textContent = String(err); setBadge('ERROR'); });
