"""
NEXUS — D3.js Kill-Chain Visualiser
Generates a standalone interactive HTML file with:
  - Force-directed graph: ThreatActor → Technique → Tactic nodes
  - Kill-chain timeline: horizontal lane diagram per attacker
  - Heat-map overlay: node colour = evasion rate (red) vs detection rate (blue)
  - Tooltips with ATT&CK metadata
  - Filters by agent name and tactic phase

Outputs a self-contained HTML file (all D3.js inlined via CDN) that opens
in any browser with no server needed.

ARM64-safe: pure Python string generation.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


# ── Colour helpers ────────────────────────────────────────────────────────────

_TACTIC_COLOURS = {
    "Initial Access":        "#ef4444",
    "Execution":             "#f97316",
    "Persistence":           "#eab308",
    "Privilege Escalation":  "#84cc16",
    "Defense Evasion":       "#22c55e",
    "Credential Access":     "#14b8a6",
    "Discovery":             "#3b82f6",
    "Lateral Movement":      "#8b5cf6",
    "Collection":            "#ec4899",
    "Command and Control":   "#06b6d4",
    "Exfiltration":          "#f59e0b",
    "Impact":                "#dc2626",
    "Unknown":               "#6b7280",
}

_AGENT_COLOURS = {
    "VIPER":  "#7c3aed",
    "KRAKEN": "#dc2626",
    "GHOST":  "#6b7280",
    "HYDRA":  "#16a34a",
    "NOVA":   "#0ea5e9",
    "CIPHER": "#f59e0b",
}


# ── Data builders ─────────────────────────────────────────────────────────────

def _build_graph_data(campaign_record, attck_client) -> dict:
    """Build node/link data for force-directed graph."""
    nodes = []
    links = []
    seen_nodes = set()

    def add_node(nid, label, ntype, color, meta=None):
        if nid not in seen_nodes:
            seen_nodes.add(nid)
            nodes.append({"id": nid, "label": label, "type": ntype,
                           "color": color, "meta": meta or {}})

    # Defender node
    add_node("DEFENDER", "DEFENDER", "defender", "#7c3aed",
             {"elo": int(next((r["elo"] for r in campaign_record.final_elo_table
                                if r["entity"] == "DEFENDER"), 1000))})

    # Agent nodes + technique nodes + links
    for row in campaign_record.final_elo_table:
        name = row["entity"]
        if name == "DEFENDER":
            continue
        add_node(name, name, "agent",
                 _AGENT_COLOURS.get(name, "#94a3b8"),
                 {"elo": int(row["elo"]), "win_rate": row["win_rate"],
                  "evasion": row["evasion_rate"]})

    for stat in campaign_record.technique_stats:
        tid  = stat["technique"]
        meta = attck_client.get_technique(tid)
        tactic_name = meta.get("tactic_name", "Unknown")
        color_r = int(255 * stat["evasion_rate"])
        color_b = int(255 * stat["detection_rate"])
        node_color = f"rgb({color_r},50,{color_b})"
        add_node(tid, f"{tid}\n{meta['name']}", "technique", node_color, {
            "tactic":      tactic_name,
            "evasion":     stat["evasion_rate"],
            "detection":   stat["detection_rate"],
            "uses":        stat["uses"],
            "url":         f"https://attack.mitre.org/techniques/{tid}/",
            "tactic_color": _TACTIC_COLOURS.get(tactic_name, "#6b7280"),
        })

        # Tactic node
        tactic_id = f"tactic_{tactic_name.replace(' ','_')}"
        add_node(tactic_id, tactic_name, "tactic",
                 _TACTIC_COLOURS.get(tactic_name, "#6b7280"),
                 {"phase": tactic_name})

        # Technique → Tactic link
        links.append({"source": tid, "target": tactic_id,
                      "type": "belongs_to", "strength": 0.3})

        # Agent → Technique links (from ELO top_technique)
        for row in campaign_record.final_elo_table:
            if row["entity"] != "DEFENDER" and row.get("top_technique") == tid:
                links.append({"source": row["entity"], "target": tid,
                               "type": "uses", "strength": 0.7,
                               "evasion": stat["evasion_rate"]})

    # Defender → all techniques (detection links)
    for stat in campaign_record.technique_stats:
        if stat["detection_rate"] > 0.3:
            links.append({"source": "DEFENDER", "target": stat["technique"],
                          "type": "detects", "strength": 0.5,
                          "detection": stat["detection_rate"]})

    return {"nodes": nodes, "links": links}


def _build_timeline_data(campaign_record, attck_client) -> list:
    """Build per-battle, per-agent timeline for the lane diagram."""
    rows = []
    agents = [r["entity"] for r in campaign_record.final_elo_table
              if r["entity"] != "DEFENDER"]
    for i, (f1, p, r) in enumerate(zip(
            campaign_record.f1_history,
            campaign_record.precision_history,
            campaign_record.recall_history)):
        battle_id = (campaign_record.battle_ids[i]
                     if i < len(campaign_record.battle_ids) else f"B{i+1}")
        for stat in campaign_record.technique_stats:
            meta = attck_client.get_technique(stat["technique"])
            rows.append({
                "battle":    i + 1,
                "battle_id": battle_id[:6],
                "technique": stat["technique"],
                "tactic":    meta.get("tactic_name", "Unknown"),
                "evasion":   stat["evasion_rate"],
                "detection": stat["detection_rate"],
                "f1":        f1,
                "winner":    campaign_record.winner_history[i]
                             if i < len(campaign_record.winner_history) else "draw",
            })
    return rows


# ── HTML builder ──────────────────────────────────────────────────────────────

def generate_killchain_html(campaign_record, attck_client,
                             output_path: str = "data/research/killchain.html") -> str:
    graph_data    = _build_graph_data(campaign_record, attck_client)
    timeline_data = _build_timeline_data(campaign_record, attck_client)
    cid           = campaign_record.campaign_id
    ts            = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    battles       = campaign_record.battles_completed
    f1_vals       = json.dumps(campaign_record.f1_history)
    sigma_vals    = json.dumps(campaign_record.sigma_rule_history)
    nova_vals     = json.dumps(campaign_record.nova_evasion_history)
    winners       = json.dumps(campaign_record.winner_history)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEXUS Kill-Chain Visualiser — Campaign {cid}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0f0f1a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }}
  header {{ padding: 16px 24px; background: #1e1e2e; border-bottom: 1px solid #334155; display:flex; justify-content:space-between; align-items:center; }}
  header h1 {{ font-size: 1.25rem; color: #a78bfa; }}
  header span {{ font-size: 0.75rem; color: #64748b; }}
  .tabs {{ display:flex; padding: 12px 24px 0; gap:4px; background:#1e1e2e; }}
  .tab {{ padding: 8px 20px; border-radius: 6px 6px 0 0; cursor:pointer; font-size:0.85rem; color:#94a3b8; border:1px solid transparent; border-bottom:none; }}
  .tab.active {{ background:#0f0f1a; color:#a78bfa; border-color:#334155; }}
  .panel {{ display:none; padding:20px 24px; }}
  .panel.active {{ display:block; }}
  svg {{ width:100%; }}
  .node circle {{ stroke-width: 2; cursor: pointer; }}
  .node text {{ font-size: 11px; fill: #e2e8f0; pointer-events:none; }}
  .link {{ stroke-opacity: 0.5; }}
  .tooltip {{ position:absolute; background:#1e293b; border:1px solid #334155; border-radius:6px; padding:10px 14px; font-size:12px; pointer-events:none; opacity:0; transition:opacity .15s; max-width:280px; z-index:100; }}
  .tooltip b {{ color:#a78bfa; }}
  .kpi {{ display:flex; gap:16px; flex-wrap:wrap; margin-bottom:20px; }}
  .kpi-card {{ background:#1e1e2e; border-radius:8px; padding:12px 18px; min-width:130px; }}
  .kpi-card .val {{ font-size:1.5rem; font-weight:700; color:#a78bfa; }}
  .kpi-card .lbl {{ font-size:0.75rem; color:#64748b; margin-top:4px; }}
  .legend {{ display:flex; flex-wrap:wrap; gap:10px; margin-bottom:16px; font-size:12px; }}
  .legend-item {{ display:flex; align-items:center; gap:6px; }}
  .legend-dot {{ width:12px; height:12px; border-radius:50%; }}
  #timeline-svg {{ overflow-x:auto; }}
  .tl-cell {{ cursor:pointer; }}
  .filter-row {{ margin-bottom:12px; display:flex; gap:8px; flex-wrap:wrap; }}
  .filter-btn {{ padding:4px 12px; border-radius:4px; border:1px solid #334155; background:transparent; color:#94a3b8; cursor:pointer; font-size:12px; }}
  .filter-btn.active {{ background:#7c3aed; color:white; border-color:#7c3aed; }}
</style>
</head>
<body>

<header>
  <h1>⚔️ NEXUS Kill-Chain Visualiser — Campaign {cid}</h1>
  <span>Generated {ts} | {battles} battles</span>
</header>

<div class="tabs">
  <div class="tab active" onclick="showTab('graph')">🕸 Force Graph</div>
  <div class="tab" onclick="showTab('timeline')">📅 Kill-Chain Timeline</div>
  <div class="tab" onclick="showTab('metrics')">📈 Campaign Metrics</div>
</div>

<div id="graph" class="panel active">
  <div class="legend" id="graph-legend"></div>
  <div class="filter-row" id="type-filters"></div>
  <div id="tooltip" class="tooltip"></div>
  <svg id="force-svg" height="560"></svg>
</div>

<div id="timeline" class="panel">
  <p style="color:#64748b;font-size:12px;margin-bottom:12px;">
    Each cell = one technique in one battle. Red = high evasion (attacker winning), Blue = high detection (defender winning).
  </p>
  <svg id="timeline-svg" height="320"></svg>
</div>

<div id="metrics" class="panel">
  <div class="kpi" id="kpi-row"></div>
  <svg id="metrics-svg" height="300"></svg>
</div>

<script>
const GRAPH_DATA    = {json.dumps(graph_data)};
const TIMELINE_DATA = {json.dumps(timeline_data)};
const F1_VALS       = {f1_vals};
const SIGMA_VALS    = {sigma_vals};
const NOVA_VALS     = {nova_vals};
const WINNERS       = {winners};

// ── Tab switching ─────────────────────────────────────────────────────────────
function showTab(id) {{
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  event.target.classList.add('active');
}}

// ── Tooltip ───────────────────────────────────────────────────────────────────
const tooltip = document.getElementById('tooltip');
function showTip(html, x, y) {{
  tooltip.innerHTML = html;
  tooltip.style.opacity = 1;
  tooltip.style.left = (x + 12) + 'px';
  tooltip.style.top  = (y - 10) + 'px';
}}
function hideTip() {{ tooltip.style.opacity = 0; }}

// ── Force-directed graph ──────────────────────────────────────────────────────
(function buildForce() {{
  const svg    = d3.select('#force-svg');
  const W      = svg.node().parentNode.clientWidth || 900;
  const H      = 560;
  svg.attr('viewBox', `0 0 ${{W}} ${{H}}`);

  const g     = svg.append('g');
  const nodes = GRAPH_DATA.nodes.map(d => Object.assign({{}}, d));
  const links = GRAPH_DATA.links.map(d => Object.assign({{}}, d));

  // Legend
  const types = ['agent','technique','tactic','defender'];
  const typeCols = {{'agent':'#3b82f6','technique':'#a78bfa','tactic':'#f59e0b','defender':'#7c3aed'}};
  const lgd = document.getElementById('graph-legend');
  types.forEach(t => {{
    lgd.innerHTML += `<div class="legend-item"><div class="legend-dot" style="background:${{typeCols[t]}}"></div>${{t}}</div>`;
  }});

  // Type filters
  let activeTypes = new Set(types);
  const frow = document.getElementById('type-filters');
  types.forEach(t => {{
    const btn = document.createElement('button');
    btn.className = 'filter-btn active';
    btn.textContent = t;
    btn.onclick = () => {{
      if (activeTypes.has(t)) {{ activeTypes.delete(t); btn.classList.remove('active'); }}
      else {{ activeTypes.add(t); btn.classList.add('active'); }}
      node.style('opacity', d => activeTypes.has(d.type) ? 1 : 0.1);
      link.style('opacity', d => {{
        const s = nodes.find(n=>n.id===d.source.id||n.id===d.source);
        const t2= nodes.find(n=>n.id===d.target.id||n.id===d.target);
        return (s&&activeTypes.has(s.type)&&t2&&activeTypes.has(t2.type)) ? 0.5 : 0.05;
      }});
    }};
    frow.appendChild(btn);
  }});

  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(d => d.type==='belongs_to' ? 80 : 120))
    .force('charge', d3.forceManyBody().strength(-220))
    .force('center', d3.forceCenter(W/2, H/2))
    .force('collision', d3.forceCollide(28));

  const link = g.append('g').selectAll('line').data(links).join('line')
    .attr('class','link')
    .attr('stroke', d => d.type==='uses' ? '#ef4444' : d.type==='detects' ? '#3b82f6' : '#475569')
    .attr('stroke-width', d => d.type==='uses' ? 2 : 1)
    .attr('stroke-dasharray', d => d.type==='detects' ? '4,3' : null);

  const node = g.append('g').selectAll('g').data(nodes).join('g')
    .attr('class','node')
    .call(d3.drag()
      .on('start', (ev,d) => {{ if(!ev.active) sim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; }})
      .on('drag',  (ev,d) => {{ d.fx=ev.x; d.fy=ev.y; }})
      .on('end',   (ev,d) => {{ if(!ev.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }}))
    .on('mouseover', (ev,d) => {{
      let html = `<b>${{d.label.replace('\\n',' ')}}</b><br>Type: ${{d.type}}`;
      if(d.meta.elo)       html += `<br>ELO: ${{d.meta.elo}}`;
      if(d.meta.evasion!==undefined) html += `<br>Evasion: ${{(d.meta.evasion*100).toFixed(1)}}%`;
      if(d.meta.tactic)    html += `<br>Tactic: ${{d.meta.tactic}}`;
      if(d.meta.uses)      html += `<br>Uses: ${{d.meta.uses}}`;
      if(d.meta.url)       html += `<br><a href="${{d.meta.url}}" target="_blank" style="color:#a78bfa">ATT&CK ↗</a>`;
      showTip(html, ev.pageX, ev.pageY);
    }})
    .on('mousemove', (ev) => {{ tooltip.style.left=(ev.pageX+12)+'px'; tooltip.style.top=(ev.pageY-10)+'px'; }})
    .on('mouseout', hideTip);

  const rMap = {{'agent':18,'technique':14,'tactic':20,'defender':22}};
  node.append('circle')
    .attr('r', d => rMap[d.type]||14)
    .attr('fill', d => d.color)
    .attr('stroke', '#0f0f1a');

  node.append('text')
    .attr('dy','0.35em')
    .attr('text-anchor','middle')
    .attr('font-size', d => d.type==='agent'||d.type==='defender' ? '11px' : '9px')
    .text(d => d.label.split('\\n')[0]);

  svg.call(d3.zoom().scaleExtent([0.3,4])
    .on('zoom', ev => g.attr('transform', ev.transform)));

  sim.on('tick', () => {{
    link.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y)
        .attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
    node.attr('transform',d=>`translate(${{d.x}},${{d.y}})`);
  }});
}})();

// ── Kill-chain timeline ───────────────────────────────────────────────────────
(function buildTimeline() {{
  const data     = TIMELINE_DATA;
  if (!data.length) return;
  const battles  = [...new Set(data.map(d=>d.battle))].sort();
  const techs    = [...new Set(data.map(d=>d.technique))];
  const cellW    = 80, cellH = 36, padL = 100, padT = 40;
  const W        = padL + battles.length * cellW + 20;
  const H        = padT + techs.length * cellH + 20;
  const svg      = d3.select('#timeline-svg')
                     .attr('viewBox', `0 0 ${{W}} ${{H}}`).attr('width', W);

  // Column headers (battle numbers)
  battles.forEach((b,i) => {{
    svg.append('text').attr('x', padL + i*cellW + cellW/2).attr('y', 24)
       .attr('text-anchor','middle').attr('fill','#94a3b8').attr('font-size',11)
       .text(`B${{b}} ${{WINNERS[b-1]?WINNERS[b-1][0].toUpperCase():'?'}}`);
  }});

  // Row labels (techniques)
  techs.forEach((t,j) => {{
    const meta = data.find(d=>d.technique===t);
    svg.append('text').attr('x', padL-6).attr('y', padT + j*cellH + cellH/2 + 4)
       .attr('text-anchor','end').attr('fill','#94a3b8').attr('font-size',10)
       .text(t + (meta ? ` (${{meta.tactic.split(' ')[0]}})` : ''));
  }});

  // Cells
  const cells = svg.append('g').selectAll('g').data(data).join('g')
    .attr('class','tl-cell')
    .attr('transform', d => {{
      const bIdx = battles.indexOf(d.battle);
      const tIdx = techs.indexOf(d.technique);
      return `translate(${{padL + bIdx*cellW}},${{padT + tIdx*cellH}})`;
    }});

  cells.append('rect')
    .attr('width', cellW-2).attr('height', cellH-2)
    .attr('rx',4)
    .attr('fill', d => {{
      const r = Math.round(d.evasion  * 200);
      const b2= Math.round(d.detection* 200);
      return `rgb(${{r}},40,${{b2}})`;
    }})
    .attr('stroke','#0f0f1a').attr('stroke-width',1);

  cells.append('text')
    .attr('x', cellW/2-1).attr('y', cellH/2+4)
    .attr('text-anchor','middle').attr('fill','#e2e8f0').attr('font-size',9)
    .text(d => `${{(d.evasion*100).toFixed(0)}}%`);

  cells
    .on('mouseover', (ev,d) => showTip(
      `<b>${{d.technique}}</b> Battle ${{d.battle}}<br>`+
      `Tactic: ${{d.tactic}}<br>`+
      `Evasion: ${{(d.evasion*100).toFixed(1)}}% | Detection: ${{(d.detection*100).toFixed(1)}}%<br>`+
      `F1: ${{d.f1.toFixed(3)}} | Winner: ${{d.winner}}`,
      ev.pageX, ev.pageY))
    .on('mousemove', ev => {{ tooltip.style.left=(ev.pageX+12)+'px'; tooltip.style.top=(ev.pageY-10)+'px'; }})
    .on('mouseout', hideTip);
}})();

// ── Metrics charts ────────────────────────────────────────────────────────────
(function buildMetrics() {{
  // KPI cards
  const kpi = document.getElementById('kpi-row');
  const last = F1_VALS.length - 1;
  [
    ['F1 Score', F1_VALS[last].toFixed(3), '#a78bfa'],
    ['SIGMA Rules', SIGMA_VALS[last], '#f59e0b'],
    ['NOVA Evasion', (NOVA_VALS[last]*100).toFixed(1)+'%', '#ef4444'],
    ['Battles', F1_VALS.length, '#3b82f6'],
    ['Winner', WINNERS[last]?.toUpperCase()||'—', '#16a34a'],
  ].forEach(([lbl,val,col]) => {{
    kpi.innerHTML += `<div class="kpi-card"><div class="val" style="color:${{col}}">${{val}}</div><div class="lbl">${{lbl}}</div></div>`;
  }});

  // Multi-line chart: F1, SIGMA (normalised), NOVA evasion
  const svg   = d3.select('#metrics-svg');
  const W     = svg.node().parentNode.clientWidth || 800;
  const H     = 280;
  const pad   = {{t:30,r:40,b:50,l:50}};
  svg.attr('viewBox',`0 0 ${{W}} ${{H}}`);

  const battles = F1_VALS.map((_,i)=>i+1);
  const xSc = d3.scaleLinear().domain([1,battles.length]).range([pad.l,W-pad.r]);
  const ySc = d3.scaleLinear().domain([0,1.05]).range([H-pad.b,pad.t]);
  const sigMax = Math.max(...SIGMA_VALS);
  const sigmaNorm = SIGMA_VALS.map(v=>v/sigMax);

  const lines = [
    {{vals: F1_VALS,     col:'#a78bfa', lbl:'F1'}},
    {{vals: sigmaNorm,   col:'#f59e0b', lbl:'SIGMA (norm)'}},
    {{vals: NOVA_VALS,   col:'#ef4444', lbl:'NOVA evasion'}},
  ];

  // Axes
  svg.append('g').attr('transform',`translate(0,${{H-pad.b}})`)
     .call(d3.axisBottom(xSc).ticks(battles.length).tickFormat(d=>`B${{d}}`))
     .selectAll('text,line,path').attr('stroke','#475569').attr('fill','#94a3b8');
  svg.append('g').attr('transform',`translate(${{pad.l}},0)`)
     .call(d3.axisLeft(ySc).ticks(5).tickFormat(d3.format('.0%')))
     .selectAll('text,line,path').attr('stroke','#475569').attr('fill','#94a3b8');

  // Grid lines
  ySc.ticks(5).forEach(v => {{
    svg.append('line')
       .attr('x1',pad.l).attr('x2',W-pad.r)
       .attr('y1',ySc(v)).attr('y2',ySc(v))
       .attr('stroke','#1e293b').attr('stroke-dasharray','3,3');
  }});

  const lineGen = d3.line().x((_,i)=>xSc(i+1)).y(v=>ySc(v)).curve(d3.curveMonotoneX);

  lines.forEach(({{vals,col,lbl}}) => {{
    svg.append('path').datum(vals)
       .attr('fill','none').attr('stroke',col).attr('stroke-width',2.5)
       .attr('d', lineGen);
    svg.selectAll(`.dot-${{lbl.replace(/ /g,'-')}}`)
       .data(vals).join('circle')
       .attr('cx',(_,i)=>xSc(i+1)).attr('cy',v=>ySc(v))
       .attr('r',4).attr('fill',col).attr('stroke','#0f0f1a').attr('stroke-width',1);
  }});

  // Legend
  lines.forEach(({{col,lbl}},i) => {{
    svg.append('circle').attr('cx',pad.l+i*110).attr('cy',H-10).attr('r',5).attr('fill',col);
    svg.append('text').attr('x',pad.l+i*110+10).attr('y',H-6)
       .attr('fill','#94a3b8').attr('font-size',11).text(lbl);
  }});
}})();
</script>
</body>
</html>"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    size = len(html)
    print(f"[D3] Kill-chain visualiser → {output_path} ({size//1024}KB)")
    return output_path
