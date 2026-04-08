"""
Build script for the Tech Support Category Dashboard.
Design system: Linear (DESIGN.md by Google Stitch / VoltAgent/awesome-design-md)
"""
import csv, json
from collections import defaultdict

# ─── Load aggregated ticket data ──────────────────────────────────────────────
MONTHS_ORDER = ['Sep 2025', 'Oct 2025', 'Nov 2025', 'Dec 2025', 'Jan 2026']

files = [
    ('Sep 2025', r'C:\Users\saptarshi.mukhopadhy\Desktop\cat-data\September-llm-cat - llm.csv'),
    ('Oct 2025', r'C:\Users\saptarshi.mukhopadhy\Desktop\cat-data\October-llm - main-file.csv'),
    ('Nov 2025', r'C:\Users\saptarshi.mukhopadhy\Desktop\cat-data\november-llm - llm-data.csv'),
    ('Dec 2025', r'C:\Users\saptarshi.mukhopadhy\Desktop\cat-data\December-llm - llm-data.csv'),
    ('Jan 2026', r'C:\Users\saptarshi.mukhopadhy\Desktop\cat-data\January-llm - llm-data.csv'),
]

agg = defaultdict(int)
for month, path in files:
    with open(path, encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = row.get('category', '').strip()
            sub = row.get('subCategory', '').strip()
            if not cat or ',' in cat:
                continue
            agg[(month, cat, sub)] += 1

agg_data = [
    {'month': m, 'category': c, 'subCategory': s, 'count': v}
    for (m, c, s), v in sorted(agg.items())
]

# ─── Load PM mapping ──────────────────────────────────────────────────────────
pm_map = {}   # "CAT|||SUB" -> "PM1, PM2"
pm_set = set()

with open(
    r'C:\Users\saptarshi.mukhopadhy\Downloads\[Category - PM] mapping - Mapping (1).csv',
    encoding='utf-8', errors='replace'
) as f:
    reader = csv.DictReader(f)
    for row in reader:
        cat = row['Category'].strip()
        sub = row['Sub-Category'].strip()
        pm_raw = row['PM'].strip()
        pm_map[cat + '|||' + sub] = pm_raw
        for p in pm_raw.split(','):
            p = p.strip()
            if p and p not in ('None', 'Generic', 'Tech', 'Tech_team', 'Tech team'):
                pm_set.add(p)

pms_sorted = sorted(pm_set)

# ─── Serialise for JS ─────────────────────────────────────────────────────────
RAW_DATA_JS   = json.dumps(agg_data)
PM_MAP_JS     = json.dumps(pm_map)
MONTHS_JS     = json.dumps(MONTHS_ORDER)
PMS_JS        = json.dumps(pms_sorted)

# ─── HTML ─────────────────────────────────────────────────────────────────────
html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tech Support &mdash; Category Dashboard</title>

<!-- Inter from Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;510;600&display=swap" rel="stylesheet">

<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>

<style>
/* ── Design tokens (Linear / DESIGN.md) ─────────────────────────── */
:root {
  /* surfaces */
  --bg-page:      #08090a;
  --bg-panel:     #0f1011;
  --bg-card:      #191a1b;
  --bg-elevated:  #28282c;
  /* text */
  --text-primary:   #f7f8f8;
  --text-secondary: #d0d6e0;
  --text-tertiary:  #8a8f98;
  --text-muted:     #62666d;
  /* accent */
  --accent:       #7170ff;
  --accent-bg:    #5e6ad2;
  --accent-hover: #828fff;
  /* borders */
  --border-subtle:   rgba(255,255,255,0.05);
  --border-standard: rgba(255,255,255,0.08);
  --border-solid:    #23252a;
  /* status */
  --green:  #27a644;
  --emerald:#10b981;
  --red:    #e5484d;
  --amber:  #f59e0b;
  /* radius */
  --r-sm:  6px;
  --r-md:  8px;
  --r-lg: 12px;
}

/* ── Reset & base ────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', -apple-system, system-ui, sans-serif;
  font-variant-ligatures: common-ligatures;
  font-feature-settings: "cv01","ss03";
  background: var(--bg-page);
  color: var(--text-primary);
  min-height: 100vh;
  font-size: 15px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

/* ── Header ──────────────────────────────────────────────────────── */
.header {
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border-subtle);
  padding: 18px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(12px);
}
.header-left { display: flex; align-items: center; gap: 14px; }
.header-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 10px var(--accent);
  flex-shrink: 0;
}
.header h1 {
  font-size: 15px; font-weight: 510;
  letter-spacing: -0.165px;
  color: var(--text-primary);
}
.header .tagline {
  font-size: 13px; color: var(--text-muted);
  letter-spacing: -0.13px;
  margin-top: 2px;
}
.header-right { display: flex; align-items: center; gap: 8px; }
.badge-live {
  background: rgba(39,166,68,0.15);
  color: var(--emerald);
  border: 1px solid rgba(39,166,68,0.25);
  font-size: 11px; font-weight: 510;
  padding: 2px 8px; border-radius: 9999px;
  letter-spacing: 0.2px;
}
.header-org {
  font-size: 12px; color: var(--text-muted);
  padding: 4px 10px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--r-sm);
}

/* ── Filters ─────────────────────────────────────────────────────── */
.filters {
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border-subtle);
  padding: 14px 32px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-end;
}
.filter-group { display: flex; flex-direction: column; gap: 5px; }
.filter-group label {
  font-size: 11px; font-weight: 510;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-muted);
}
.filter-group select {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-standard);
  border-radius: var(--r-sm);
  color: var(--text-secondary);
  font-family: inherit;
  font-size: 13px;
  padding: 6px 10px;
  outline: none;
  cursor: pointer;
  min-width: 148px;
  transition: border-color 0.15s;
}
.filter-group select:focus { border-color: var(--accent); }
.filter-group select[multiple] { height: 80px; }
.filter-group select option { background: var(--bg-card); color: var(--text-primary); }
.btn-reset {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border-standard);
  color: var(--text-secondary);
  font-family: inherit;
  font-size: 13px; font-weight: 510;
  padding: 6px 16px;
  border-radius: var(--r-sm);
  cursor: pointer;
  align-self: flex-end;
  transition: background 0.15s, border-color 0.15s;
}
.btn-reset:hover { background: rgba(255,255,255,0.07); border-color: rgba(255,255,255,0.14); }

/* ── Main layout ─────────────────────────────────────────────────── */
.main { padding: 24px 32px; max-width: 1600px; }

/* ── KPI row ─────────────────────────────────────────────────────── */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}
.kpi-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--r-lg);
  padding: 18px 20px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s;
}
.kpi-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
}
.kpi-card:hover { border-color: var(--border-standard); }
.kpi-label {
  font-size: 11px; font-weight: 510;
  text-transform: uppercase; letter-spacing: 0.8px;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.kpi-value {
  font-size: 28px; font-weight: 510;
  letter-spacing: -0.7px;
  color: var(--text-primary);
  line-height: 1;
}
.kpi-sub {
  font-size: 12px; color: var(--text-muted);
  margin-top: 6px; letter-spacing: -0.1px;
}
.kpi-accent-line {
  position: absolute; bottom: 0; left: 0;
  height: 2px; width: 40%;
  border-radius: 0 2px 0 0;
}
.kpi-card.accent .kpi-accent-line { background: var(--accent); }
.kpi-card.green  .kpi-accent-line { background: var(--emerald); }
.kpi-card.up     .kpi-accent-line { background: var(--amber); }
.kpi-card.down   .kpi-accent-line { background: var(--red); }
.kpi-card.purple .kpi-accent-line { background: #8b5cf6; }

/* ── Chart grid ──────────────────────────────────────────────────── */
.charts-top {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  margin-bottom: 12px;
}
.charts-bottom {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}
.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--r-lg);
  padding: 20px 24px;
  position: relative;
  overflow: hidden;
}
.chart-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
}
.chart-card h3 {
  font-size: 13px; font-weight: 510;
  color: var(--text-primary);
  letter-spacing: -0.13px;
  margin-bottom: 3px;
}
.chart-card .chart-sub {
  font-size: 12px; color: var(--text-muted);
  margin-bottom: 14px; letter-spacing: -0.1px;
}

/* ── Table card ──────────────────────────────────────────────────── */
.table-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--r-lg);
  padding: 20px 24px;
  position: relative;
  overflow: hidden;
}
.table-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
}
.table-card h3 {
  font-size: 13px; font-weight: 510;
  color: var(--text-primary);
  letter-spacing: -0.13px;
  margin-bottom: 3px;
}
.table-card .chart-sub {
  font-size: 12px; color: var(--text-muted);
  margin-bottom: 16px; letter-spacing: -0.1px;
}
.table-wrap { overflow-x: auto; }
table {
  width: 100%; border-collapse: collapse;
  font-size: 13px;
}
thead tr {
  border-bottom: 1px solid var(--border-subtle);
}
th {
  padding: 8px 12px;
  text-align: left;
  font-size: 11px; font-weight: 510;
  text-transform: uppercase; letter-spacing: 0.7px;
  color: var(--text-muted);
  white-space: nowrap;
}
td {
  padding: 9px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  color: var(--text-secondary);
  vertical-align: middle;
}
tr:hover td { background: rgba(255,255,255,0.02); }
td.cat-cell { color: var(--text-primary); font-weight: 510; letter-spacing: -0.13px; }
td.num { font-variant-numeric: tabular-nums; text-align: right; }

/* ── Badges ──────────────────────────────────────────────────────── */
.badge {
  display: inline-flex; align-items: center; gap: 3px;
  padding: 2px 7px;
  border-radius: 9999px;
  font-size: 11px; font-weight: 510;
  letter-spacing: 0.1px;
}
.badge-up     { background: rgba(16,185,129,0.12); color: var(--emerald); border: 1px solid rgba(16,185,129,0.2); }
.badge-down   { background: rgba(229,72,77,0.12);  color: var(--red);     border: 1px solid rgba(229,72,77,0.2); }
.badge-new    { background: rgba(113,112,255,0.12); color: var(--accent); border: 1px solid rgba(113,112,255,0.2); }
.badge-flat   { background: rgba(255,255,255,0.04); color: var(--text-muted); border: 1px solid var(--border-subtle); }

/* ── PM chip ─────────────────────────────────────────────────────── */
.pm-chip {
  display: inline-block;
  background: rgba(113,112,255,0.1);
  color: var(--accent);
  border: 1px solid rgba(113,112,255,0.2);
  border-radius: 4px;
  font-size: 11px; font-weight: 510;
  padding: 1px 7px;
  white-space: nowrap;
}

/* ── Footer ──────────────────────────────────────────────────────── */
footer {
  text-align: center;
  padding: 24px 32px;
  font-size: 12px; color: var(--text-muted);
  border-top: 1px solid var(--border-subtle);
  letter-spacing: -0.1px;
}
</style>
</head>
<body>

<!-- ── Header ─────────────────────────────────────────────────────── -->
<div class="header">
  <div class="header-left">
    <div class="header-dot"></div>
    <div>
      <h1>Tech Support &mdash; Category Intelligence</h1>
      <div class="tagline">AI-classified tickets &middot; Sep 2025 &ndash; Jan 2026</div>
    </div>
  </div>
  <div class="header-right">
    <span class="badge-live">Live</span>
    <span class="header-org">Incred Finance</span>
  </div>
</div>

<!-- ── Filters ─────────────────────────────────────────────────────── -->
<div class="filters">
  <div class="filter-group">
    <label>Month</label>
    <select id="filterMonth" multiple>
      <option value="Sep 2025" selected>Sep 2025</option>
      <option value="Oct 2025" selected>Oct 2025</option>
      <option value="Nov 2025" selected>Nov 2025</option>
      <option value="Dec 2025" selected>Dec 2025</option>
      <option value="Jan 2026" selected>Jan 2026</option>
    </select>
  </div>
  <div class="filter-group">
    <label>Category</label>
    <select id="filterCategory" multiple>
      <option value="ALL" selected>All Categories</option>
    </select>
  </div>
  <div class="filter-group">
    <label>Subcategory</label>
    <select id="filterSubcategory" multiple>
      <option value="ALL" selected>All Subcategories</option>
    </select>
  </div>
  <div class="filter-group">
    <label>Product Manager</label>
    <select id="filterPM">
      <option value="ALL">All PMs</option>
    </select>
  </div>
  <button class="btn-reset" onclick="resetFilters()">Reset</button>
</div>

<!-- ── Main ────────────────────────────────────────────────────────── -->
<div class="main">

  <!-- KPIs -->
  <div class="kpi-row" id="kpiRow"></div>

  <!-- Trend (full width) -->
  <div class="charts-top">
    <div class="chart-card">
      <h3>Monthly Ticket Volume &mdash; by Category</h3>
      <div class="chart-sub">Month-on-month trend for all active categories in selected filters</div>
      <div id="chartTrend"></div>
    </div>
  </div>

  <!-- Bar + Heatmap -->
  <div class="charts-bottom">
    <div class="chart-card">
      <h3>Volume by Category</h3>
      <div class="chart-sub">Total tickets in selected period, ranked</div>
      <div id="chartBar"></div>
    </div>
    <div class="chart-card">
      <h3>MoM % Change Heatmap</h3>
      <div class="chart-sub">Month-over-month growth per category &middot; green = growth</div>
      <div id="chartHeatmap"></div>
    </div>
  </div>

  <!-- Subcategory table -->
  <div class="table-card">
    <h3>Subcategory Breakdown</h3>
    <div class="chart-sub">PM ownership &middot; latest vs previous month &middot; filtered by current selection</div>
    <div class="table-wrap">
      <div id="subTable"></div>
    </div>
  </div>

</div>

<footer>
  Data refreshes daily at 5&nbsp;PM &middot; AI-categorized tickets &middot; Sep 2025&nbsp;&ndash;&nbsp;Jan 2026
  &middot; Built with Linear Design System (Google Stitch DESIGN.md)
</footer>

<!-- ── Script ──────────────────────────────────────────────────────── -->
<script>
/* ─ Data ─────────────────────────────────────────────────────────────── */
const RAW_DATA    = RAW_DATA_PLACEHOLDER;
const PM_MAP      = PM_MAP_PLACEHOLDER;   // "CAT|||SUB" -> "PM1, PM2"
const MONTHS_ORDER = MONTHS_PLACEHOLDER;
const ALL_PMS     = PMS_PLACEHOLDER;

/* ─ Plotly shared layout defaults (dark theme) ───────────────────────── */
const PLOT_LAYOUT = {
  paper_bgcolor: 'transparent',
  plot_bgcolor:  'transparent',
  font: { family: 'Inter, system-ui, sans-serif', color: '#8a8f98', size: 12 },
  margin: { t: 8, r: 16, b: 40, l: 56 },
  colorway: [
    '#7170ff','#27a644','#f59e0b','#e5484d','#06b6d4',
    '#8b5cf6','#10b981','#f97316','#ec4899','#3b82f6',
    '#a3e635','#fb923c','#e879f9','#22d3ee','#fbbf24',
    '#34d399','#f43f5e','#60a5fa','#c084fc','#a78bfa','#2dd4bf'
  ],
};
const AXIS_STYLE = {
  gridcolor: 'rgba(255,255,255,0.05)',
  zeroline: false,
  tickfont: { size: 11 },
  linecolor: 'rgba(255,255,255,0.06)',
};

/* ─ State ────────────────────────────────────────────────────────────── */
let state = {
  months: [...MONTHS_ORDER],
  categories: ['ALL'],
  subcategories: ['ALL'],
  pm: 'ALL',
};

/* ─ Init ─────────────────────────────────────────────────────────────── */
function init() {
  // categories
  const cats = [...new Set(RAW_DATA.map(d => d.category))].sort();
  const catSel = document.getElementById('filterCategory');
  cats.forEach(c => {
    const o = document.createElement('option');
    o.value = c; o.textContent = c; o.selected = true;
    catSel.appendChild(o);
  });

  // subcategories
  const subs = [...new Set(RAW_DATA.map(d => d.subCategory))].sort();
  const subSel = document.getElementById('filterSubcategory');
  subs.forEach(s => {
    const o = document.createElement('option');
    o.value = s; o.textContent = s; o.selected = true;
    subSel.appendChild(o);
  });

  // PMs
  const pmSel = document.getElementById('filterPM');
  ALL_PMS.forEach(p => {
    const o = document.createElement('option');
    o.value = p; o.textContent = p;
    pmSel.appendChild(o);
  });

  document.getElementById('filterMonth').addEventListener('change', onFilter);
  document.getElementById('filterCategory').addEventListener('change', onFilter);
  document.getElementById('filterSubcategory').addEventListener('change', onFilter);
  document.getElementById('filterPM').addEventListener('change', onFilter);

  render();
}

function getSelected(el) { return [...el.selectedOptions].map(o => o.value); }

function onFilter() {
  state.months = getSelected(document.getElementById('filterMonth'));
  state.categories = getSelected(document.getElementById('filterCategory'));
  state.subcategories = getSelected(document.getElementById('filterSubcategory'));
  state.pm = document.getElementById('filterPM').value;
  render();
}

function resetFilters() {
  ['filterMonth', 'filterCategory', 'filterSubcategory'].forEach(id => {
    [...document.getElementById(id).options].forEach(o => o.selected = true);
  });
  document.getElementById('filterPM').value = 'ALL';
  state = { months: [...MONTHS_ORDER], categories: ['ALL'], subcategories: ['ALL'], pm: 'ALL' };
  render();
}

/* ─ Filter data ──────────────────────────────────────────────────────── */
function pmForRow(d) {
  return PM_MAP[d.category + '|||' + d.subCategory] || '';
}

function filterData() {
  return RAW_DATA.filter(d => {
    if (!state.months.includes(d.month)) return false;
    if (!state.categories.includes('ALL') && !state.categories.includes(d.category)) return false;
    if (!state.subcategories.includes('ALL') && !state.subcategories.includes(d.subCategory)) return false;
    if (state.pm !== 'ALL') {
      const pmStr = pmForRow(d);
      if (!pmStr.split(',').map(p => p.trim()).includes(state.pm)) return false;
    }
    return true;
  });
}

/* ─ Render ───────────────────────────────────────────────────────────── */
function render() {
  const data = filterData();
  renderKPIs(data);
  renderTrend(data);
  renderBar(data);
  renderHeatmap(data);
  renderTable(data);
}

/* ─ KPIs ─────────────────────────────────────────────────────────────── */
function renderKPIs(data) {
  const total = data.reduce((s, d) => s + d.count, 0);
  const selMonths = MONTHS_ORDER.filter(m => state.months.includes(m));

  // top category
  const catTotals = {};
  data.forEach(d => { catTotals[d.category] = (catTotals[d.category] || 0) + d.count; });
  const topCat = Object.entries(catTotals).sort((a, b) => b[1] - a[1])[0];

  // MoM total
  let momPct = null, momLabel = '';
  if (selMonths.length >= 2) {
    const last = selMonths.at(-1), prev = selMonths.at(-2);
    const lastN = data.filter(d => d.month === last).reduce((s, d) => s + d.count, 0);
    const prevN = data.filter(d => d.month === prev).reduce((s, d) => s + d.count, 0);
    if (prevN > 0) { momPct = ((lastN - prevN) / prevN * 100).toFixed(1); momLabel = prev + ' \u2192 ' + last; }
  }

  // fastest growing subcat
  let fastSub = '', fastPct = 0;
  if (selMonths.length >= 2) {
    const last = selMonths.at(-1), prev = selMonths.at(-2);
    const mapL = {}, mapP = {};
    data.filter(d => d.month === last).forEach(d => { const k = d.category+'|'+d.subCategory; mapL[k] = (mapL[k]||0)+d.count; });
    data.filter(d => d.month === prev).forEach(d => { const k = d.category+'|'+d.subCategory; mapP[k] = (mapP[k]||0)+d.count; });
    Object.entries(mapL).forEach(([k, v]) => {
      const p = mapP[k] || 0;
      if (p > 5 && (v - p) / p * 100 > fastPct) {
        fastPct = (v - p) / p * 100; fastSub = k.split('|')[1];
      }
    });
    fastPct = fastPct.toFixed(1);
  }

  const momClass = momPct === null ? 'accent' : parseFloat(momPct) >= 0 ? 'up' : 'down';
  const momSign  = momPct !== null && parseFloat(momPct) >= 0 ? '+' : '';

  document.getElementById('kpiRow').innerHTML = `
    <div class="kpi-card accent">
      <div class="kpi-label">Total Tickets</div>
      <div class="kpi-value">${total.toLocaleString()}</div>
      <div class="kpi-sub">${selMonths.length} month${selMonths.length !== 1 ? 's' : ''} selected</div>
      <div class="kpi-accent-line"></div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-label">Top Category</div>
      <div class="kpi-value" style="font-size:18px;padding-top:2px">${topCat ? topCat[0] : '\u2014'}</div>
      <div class="kpi-sub">${topCat ? topCat[1].toLocaleString() + ' tickets' : ''}</div>
      <div class="kpi-accent-line"></div>
    </div>
    <div class="kpi-card ${momClass}">
      <div class="kpi-label">MoM Volume</div>
      <div class="kpi-value" style="font-size:24px">${momPct !== null ? momSign + momPct + '%' : '\u2014'}</div>
      <div class="kpi-sub">${momLabel}</div>
      <div class="kpi-accent-line"></div>
    </div>
    <div class="kpi-card purple">
      <div class="kpi-label">Fastest Growing</div>
      <div class="kpi-value" style="font-size:16px;padding-top:4px;font-weight:510">${fastSub || '\u2014'}</div>
      <div class="kpi-sub">${fastSub ? '+' + fastPct + '% MoM' : ''}</div>
      <div class="kpi-accent-line"></div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Active Categories</div>
      <div class="kpi-value">${new Set(data.map(d => d.category)).size}</div>
      <div class="kpi-sub">in selected period</div>
      <div class="kpi-accent-line"></div>
    </div>`;
}

/* ─ Trend chart ──────────────────────────────────────────────────────── */
function renderTrend(data) {
  const selMonths = MONTHS_ORDER.filter(m => state.months.includes(m));
  const cats = [...new Set(data.map(d => d.category))].sort();
  const colors = PLOT_LAYOUT.colorway;

  const traces = cats.map((cat, i) => ({
    x: selMonths,
    y: selMonths.map(m => data.filter(d => d.category === cat && d.month === m).reduce((s, d) => s + d.count, 0)),
    name: cat,
    type: 'scatter', mode: 'lines+markers',
    line:   { color: colors[i % colors.length], width: 2 },
    marker: { size: 5, color: colors[i % colors.length] },
    hovertemplate: '<b>%{data.name}</b><br>%{x}: %{y} tickets<extra></extra>',
  }));

  Plotly.react('chartTrend', traces, {
    ...PLOT_LAYOUT,
    height: 300,
    margin: { t: 8, r: 16, b: 48, l: 56 },
    legend: { orientation: 'h', y: -0.22, font: { size: 11 }, bgcolor: 'transparent' },
    xaxis: { ...AXIS_STYLE },
    yaxis: { ...AXIS_STYLE, title: { text: 'Tickets', font: { size: 12 } } },
    hovermode: 'x unified',
  }, { responsive: true });
}

/* ─ Category bar ─────────────────────────────────────────────────────── */
function renderBar(data) {
  const cats = [...new Set(data.map(d => d.category))];
  const sorted = cats
    .map(c => [c, data.filter(d => d.category === c).reduce((s, d) => s + d.count, 0)])
    .sort((a, b) => b[1] - a[1]);
  const colors = PLOT_LAYOUT.colorway;

  Plotly.react('chartBar', [{
    x: sorted.map(r => r[1]),
    y: sorted.map(r => r[0]),
    type: 'bar', orientation: 'h',
    marker: { color: sorted.map((_, i) => colors[i % colors.length]) },
    text: sorted.map(r => r[1].toLocaleString()),
    textposition: 'outside',
    textfont: { color: '#8a8f98', size: 11 },
    hovertemplate: '<b>%{y}</b><br>%{x} tickets<extra></extra>',
  }], {
    ...PLOT_LAYOUT,
    height: 400,
    margin: { t: 8, r: 70, b: 30, l: 170 },
    xaxis: { ...AXIS_STYLE },
    yaxis: { ...AXIS_STYLE, automargin: true },
  }, { responsive: true });
}

/* ─ Heatmap ──────────────────────────────────────────────────────────── */
function renderHeatmap(data) {
  const selMonths = MONTHS_ORDER.filter(m => state.months.includes(m));
  if (selMonths.length < 2) {
    document.getElementById('chartHeatmap').innerHTML =
      '<p style="color:var(--text-muted);padding:60px 20px;text-align:center;font-size:13px">Select at least 2 months to see MoM % change</p>';
    return;
  }
  const cats = [...new Set(data.map(d => d.category))].sort();
  const momMonths = selMonths.slice(1);
  const z = [], texts = [];

  cats.forEach(cat => {
    const row = [], rowT = [];
    momMonths.forEach((m, i) => {
      const prev = selMonths[i];
      const pv = data.filter(d => d.category === cat && d.month === prev).reduce((s, d) => s + d.count, 0);
      const cv = data.filter(d => d.category === cat && d.month === m).reduce((s, d) => s + d.count, 0);
      if (pv === 0) { row.push(null); rowT.push('—'); }
      else { const p = (cv - pv) / pv * 100; row.push(p); rowT.push((p >= 0 ? '+' : '') + p.toFixed(1) + '%'); }
    });
    z.push(row); texts.push(rowT);
  });

  const xLabels = momMonths.map((m, i) => selMonths[i].replace(' ', '\u00A0') + '\u2192' + m.replace(' ', '\u00A0'));

  Plotly.react('chartHeatmap', [{
    z, x: xLabels, y: cats,
    text: texts, texttemplate: '%{text}',
    type: 'heatmap',
    colorscale: [[0, '#7f1d1d'], [0.5, '#1a1b1e'], [1, '#052e16']],
    zmid: 0, zmin: -80, zmax: 80,
    hovertemplate: '<b>%{y}</b><br>%{x}<br>%{text}<extra></extra>',
    showscale: true,
    colorbar: {
      thickness: 12, len: 0.85,
      tickfont: { size: 10, color: '#8a8f98' },
      outlinecolor: 'rgba(255,255,255,0.05)',
      bgcolor: 'transparent',
    },
  }], {
    ...PLOT_LAYOUT,
    height: 400,
    margin: { t: 8, r: 80, b: 70, l: 160 },
    xaxis: { ...AXIS_STYLE, tickangle: -20 },
    yaxis: { ...AXIS_STYLE, automargin: true },
  }, { responsive: true });
}

/* ─ Subcategory table ────────────────────────────────────────────────── */
function renderTable(data) {
  const selMonths = MONTHS_ORDER.filter(m => state.months.includes(m));
  const last = selMonths.at(-1);
  const prev = selMonths.length >= 2 ? selMonths.at(-2) : null;

  const map = {};
  data.forEach(d => {
    const k = d.category + '|||' + d.subCategory;
    if (!map[k]) map[k] = { category: d.category, subCategory: d.subCategory, last: 0, prev: 0 };
    if (d.month === last) map[k].last += d.count;
    else if (d.month === prev) map[k].prev += d.count;
  });

  const rows = Object.values(map)
    .filter(r => r.last > 0 || r.prev > 0)
    .sort((a, b) => b.last - a.last);

  let html = '<table><thead><tr>' +
    '<th>Category</th><th>Subcategory</th><th>PM</th>' +
    (prev ? `<th style="text-align:right">${prev}</th>` : '') +
    `<th style="text-align:right">${last}</th>` +
    (prev ? '<th>MoM</th>' : '') +
    '</tr></thead><tbody>';

  rows.forEach(r => {
    const pmRaw = PM_MAP[r.category + '|||' + r.subCategory] || '';
    const pmChips = pmRaw
      ? pmRaw.split(',').map(p => p.trim()).filter(Boolean)
          .map(p => `<span class="pm-chip">${p}</span>`).join(' ')
      : '<span style="color:var(--text-muted)">—</span>';

    let badge = '';
    if (prev) {
      if (r.prev === 0 && r.last > 0)      badge = '<span class="badge badge-new">NEW</span>';
      else if (r.prev === 0)                badge = '<span class="badge badge-flat">—</span>';
      else {
        const pct = ((r.last - r.prev) / r.prev * 100).toFixed(1);
        const cls = parseFloat(pct) >= 0 ? 'badge-up' : 'badge-down';
        const sym = parseFloat(pct) >= 0 ? '▲' : '▼';
        badge = `<span class="badge ${cls}">${sym} ${Math.abs(pct)}%</span>`;
      }
    }

    html += `<tr>
      <td class="cat-cell">${r.category}</td>
      <td>${r.subCategory}</td>
      <td>${pmChips}</td>
      ${prev ? `<td class="num" style="color:var(--text-muted)">${r.prev.toLocaleString()}</td>` : ''}
      <td class="num">${r.last.toLocaleString()}</td>
      ${prev ? `<td>${badge}</td>` : ''}
    </tr>`;
  });

  html += '</tbody></table>';
  document.getElementById('subTable').innerHTML = html;
}

window.addEventListener('load', init);
</script>
</body>
</html>"""

# ── Inject data ───────────────────────────────────────────────────────────────
html = html.replace('RAW_DATA_PLACEHOLDER', RAW_DATA_JS)
html = html.replace('PM_MAP_PLACEHOLDER',   PM_MAP_JS)
html = html.replace('MONTHS_PLACEHOLDER',   MONTHS_JS)
html = html.replace('PMS_PLACEHOLDER',      PMS_JS)

out = r'C:\Users\saptarshi.mukhopadhy\Desktop\cat-dashboard\index.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Written: {out}')
print(f'Size:    {len(html):,} bytes')
