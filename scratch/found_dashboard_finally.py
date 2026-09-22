"""
NEXUS War Room Dashboard — Professional Edition
================================================
Autonomous Cyber Warfare Simulation & Self-Evolving SOC Platform

Launch:
    .venv\\Scripts\\python.exe -m streamlit run scripts/dashboard.py
"""

import sys, os, json, time, threading, queue, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timezone
from pathlib import Path

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NEXUS War Room",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL THEME — injected CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Base ─────────────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #070b14 !important;
    color: #e2e8f0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
[data-testid="stSidebar"] {
    background-color: #0d1117 !important;
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* ── Metric cards ─────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0f172a, #111827);
    border: 1px solid #1e293b;
    border-left: 3px solid #00d2ff;
    border-radius: 8px;
    padding: 14px 18px !important;
    box-shadow: 0 4px 20px rgba(0,210,255,0.06);
    transition: box-shadow 0.3s;
}
[data-testid="metric-container"]:hover {
    box-shadow: 0 4px 24px rgba(0,210,255,0.18);
}
[data-testid="metric-container"] label {
    color: #94a3b8 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #00d2ff !important;
    font-size: 1.9rem !important;
    font-weight: 700;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.82rem !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid #1e293b;
    gap: 4px;
}
[data-testid="stTabs"] button[role="tab"] {
    color: #64748b !important;
    border-radius: 6px 6px 0 0;
    font-size: 0.88rem;
    font-weight: 500;
    padding: 8px 16px;
    border: 1px solid transparent !important;
    background: transparent !important;
    transition: all 0.2s;
}
[data-testid="stTabs"] button[role="tab"]:hover {
    color: #cbd5e1 !important;
    background: rgba(255,255,255,0.04) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #00d2ff !important;
    border-bottom: 2px solid #00d2ff !important;
    background: rgba(0,210,255,0.05) !important;
}

/* ── Buttons ──────────────────────────────────────────────────────────── */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
    border: none !important;
    color: white !important;
    font-weight: 600;
    letter-spacing: 0.03em;
    border-radius: 6px;
    box-shadow: 0 4px 15px rgba(14,165,233,0.3);
    transition: all 0.25s;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(14,165,233,0.5);
    transform: translateY(-1px);
}
.stDownloadButton > button {
    background: rgba(0,210,255,0.08) !important;
    border: 1px solid #00d2ff !important;
    color: #00d2ff !important;
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.2s;
}
.stDownloadButton > button:hover {
    background: rgba(0,210,255,0.18) !important;
}

/* ── Expanders ────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 6px;
    margin-bottom: 6px;
}

/* ── Dataframe ────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border: 1px solid #1e293b; border-radius: 6px; }

/* ── Info / warning boxes ─────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 6px; }

/* ── Divider ──────────────────────────────────────────────────────────── */
hr { border-color: #1e293b !important; }

/* ── Feed box ─────────────────────────────────────────────────────────── */
.feed-box {
    background: #0d1117;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 16px 20px;
    font-family: 'Courier New', monospace;
    font-size: 0.83rem;
    line-height: 1.7;
    max-height: 480px;
    overflow-y: auto;
    color: #94a3b8;
}
.feed-box .battle-line  { color: #f59e0b; font-weight: 600; }
.feed-box .attack-line  { color: #e2e8f0; }
.feed-box .detect-line  { color: #10b981; }

/* ── Header gradient ──────────────────────────────────────────────────── */
.nexus-header {
    background: linear-gradient(90deg, rgba(0,210,255,0.12), rgba(99,102,241,0.06));
    border: 1px solid rgba(0,210,255,0.15);
    border-radius: 10px;
    padding: 18px 24px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.nexus-header h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00d2ff, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.nexus-header p { margin: 0; color: #64748b; font-size: 0.9rem; }

/* ── Section header ───────────────────────────────────────────────────── */
.section-header {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #00d2ff;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(0,210,255,0.2);
}

/* ── Status badge ─────────────────────────────────────────────────────── */
.badge-running {
    display: inline-block;
    background: rgba(245,158,11,0.15);
    color: #f59e0b;
    border: 1px solid #f59e0b;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    animation: pulse 2s infinite;
}
.badge-done {
    display: inline-block;
    background: rgba(16,185,129,0.15);
    color: #10b981;
    border: 1px solid #10b981;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78rem;
    font-weight: 600;
}
@keyframes pulse {
    0%   { opacity: 1; }
    50%  { opacity: 0.5; }
    100% { opacity: 1; }
}

/* ── SOAR action chips ────────────────────────────────────────────────── */
.soar-chip {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 3px;
}

/* ── Block container ──────────────────────────────────────────────────── */
.block-container { padding-top: 1.2rem !important; padding-bottom: 1rem !important; }

/* ── Slider ───────────────────────────────────────────────────────────── */
[data-testid="stSlider"] > div > div > div > div { background: #00d2ff !important; }

/* ── Selectbox ────────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: #0f172a !important;
    border-color: #334155 !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PLOTLY DARK TEMPLATE
# ══════════════════════════════════════════════════════════════════════════════
NEXUS_LAYOUT = dict(
    plot_bgcolor  = "#070b14",
    paper_bgcolor = "#0d1117",
    font          = dict(color="#94a3b8", family="Segoe UI"),
    xaxis         = dict(showgrid=True, gridcolor="#1e293b", zeroline=False,
                         linecolor="#1e293b"),
    yaxis         = dict(showgrid=True, gridcolor="#1e293b", zeroline=False,
                         linecolor="#1e293b"),
    legend        = dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e293b",
                         borderwidth=1, orientation="h",
                         yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin        = dict(t=30, b=30, l=10, r=10),
    hoverlabel    = dict(bgcolor="#111827", bordercolor="#1e293b",
                         font_size=13),
)
PALETTE = ["#00d2ff","#6366f1","#f59e0b","#10b981","#ef4444","#8b5cf6",
           "#ec4899","#06b6d4","#84cc16"]

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 5px'>
        <div style='font-size:2.2rem'>⚔️</div>
        <div style='font-size:1.5rem; font-weight:800; color:#00d2ff; letter-spacing:0.05em'>NEXUS</div>
        <div style='font-size:0.72rem; color:#475569; margin-top:-4px'>
            Neural Exploitation & eXplainable Unified Security
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown('<div class="section-header">⚙ Campaign Config</div>', unsafe_allow_html=True)
    n_battles        = st.slider("Battles",            2, 8,   3)
    turns_per_battle = st.slider("Turns / battle",     2, 12,  5)
    num_users        = st.slider("AD users",           10, 80, 25)
    num_hosts        = st.slider("Hosts",              4,  20,  8)
    normal_per_turn  = st.slider("Normal logs / turn", 5,  40, 15)
    gnn_pretrain     = st.slider("GNN pretrain logs",  50, 400, 150)

    st.divider()
    st.markdown('<div class="section-header">🤖 AI Provider</div>', unsafe_allow_html=True)
    provider = st.selectbox(
        "LLM backend",
        ["mock", "ollama", "gemini", "anthropic", "openai"],
        format_func=lambda x: {
            "mock":      "🎲 Mock (offline)",
            "ollama":    "🦙 Ollama (local)",
            "gemini":    "♊ Gemini (Google)",
            "anthropic": "🟠 Claude (Anthropic)",
            "openai":    "🟢 GPT-4 (OpenAI)",
        }[x]
    )
    seed = st.number_input("Random seed", value=42, step=1)

    st.divider()
    run_btn = st.button("▶ Launch Campaign", type="primary", use_container_width=True)

    st.divider()
    st.markdown('<div class="section-header">📊 System</div>', unsafe_allow_html=True)
    db_path = Path("data/simulation_results.db")
    if db_path.exists():
        size_mb = db_path.stat().st_size / 1_048_576
        st.caption(f"💾 DB: `{size_mb:.1f} MB`")
    st.caption(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
    st.caption("🖥 ARM64-safe · no GPU required")

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for key, default in [
    ("record", None), ("live_feed", []), ("battle_metrics", []),
    ("running", False), ("turn_queue", None), ("campaign_start", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
record   = st.session_state.record
bmetrics = st.session_state.battle_metrics
running  = st.session_state.running

if running:
    status_html = '<span class="badge-running">● LIVE</span>'
elif record:
    status_html = '<span class="badge-done">✓ COMPLETE</span>'
else:
    status_html = '<span style="color:#475569;font-size:0.8rem">● IDLE</span>'

elapsed = ""
if st.session_state.campaign_start:
    secs = int(time.time() - st.session_state.campaign_start)
    elapsed = f"&nbsp;&nbsp;⏱ {secs//60:02d}:{secs%60:02d}"

st.markdown(f"""
<div class="nexus-header">
    <div style="font-size:2.4rem">⚔️</div>
    <div>
        <h1>NEXUS War Room</h1>
        <p>Autonomous Cyber Warfare Simulation — Co-evolution Dashboard</p>
    </div>
    <div style="margin-left:auto; text-align:right">
        {status_html}{elapsed}
        <div style="color:#475569; font-size:0.75rem; margin-top:4px">
            {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CAMPAIGN RUNNER (background thread)
# ══════════════════════════════════════════════════════════════════════════════
def _run_campaign_streamed(cfg: dict, q: queue.Queue):
    try:
        from core.campaign import CampaignRunner
        runner = CampaignRunner(**cfg)
        original_run_single = runner._run_single_battle

        def patched(battle_num, seed, defender):
            report = original_run_single(battle_num, seed, defender)
            q.put({
                "type":        "battle_done",
                "battle_num":  battle_num,
                "metrics":     report.metrics,
                "winner":      report.winner,
                "sigma":       len(defender.sigma.rules),
                "attack_logs": report.attacker_logs[-6:],
                "missed":      report.missed_techniques,
                "evolution":   report.evolution_result,
            })
            return report

        runner._run_single_battle = patched
        record = runner.run()
        q.put({"type": "done", "record": record})
    except Exception as e:
        q.put({"type": "error", "msg": str(e)})

if run_btn and not running:
    st.session_state.running        = True
    st.session_state.live_feed      = []
    st.session_state.battle_metrics = []
    st.session_state.record         = None
    st.session_state.campaign_start = time.time()
    q = queue.Queue()
    st.session_state.turn_queue = q
    cfg = dict(
        n_battles=n_battles, turns_per_battle=turns_per_battle,
        num_users=num_users, num_hosts=num_hosts, llm_provider=provider,
        normal_logs_per_turn=normal_per_turn, gnn_pretrain_logs=gnn_pretrain,
        seed=int(seed), verbose=False, save_reports=True,
    )
    threading.Thread(target=_run_campaign_streamed, args=(cfg, q), daemon=True).start()

# Drain queue
if running and st.session_state.turn_queue:
    q = st.session_state.turn_queue
    while not q.empty():
        ev = q.get_nowait()
        if ev["type"] == "battle_done":
            st.session_state.battle_metrics.append(ev)
            evo = ev.get("evolution", {})
            new_rules = len(evo.get("new_sigma_rules", []))
            st.session_state.live_feed.append(
                f"⚔️ **Battle {ev['battle_num']}** · "
                f"Winner: `{ev['winner'].upper()}` · "
                f"F1={ev['metrics']['f1_score']:.3f} · "
                f"SIGMA={ev['sigma']} ({new_rules:+d} new)"
            )
            for log in ev.get("attack_logs", []):
                agent   = log.get("attacker", "?")
                tech    = log.get("attack_technique", "?")
                host    = log.get("host", "?")
                stealth = log.get("stealth_level", "?")
                st.session_state.live_feed.append(
                    f"  └ `[{agent:<7s}]` {tech} → {host} · stealth={stealth}"
                )
        elif ev["type"] == "done":
            st.session_state.record  = ev["record"]
            st.session_state.running = False
        elif ev["type"] == "error":
            st.error(f"❌ Campaign error: {ev['msg']}")
            st.session_state.running = False
    if st.session_state.running:
        time.sleep(0.5)
        st.rerun()

# Refresh state after drain
record   = st.session_state.record
bmetrics = st.session_state.battle_metrics
battles  = list(range(1, len(bmetrics) + 1))
running  = st.session_state.running

def _val(key, default=0.0):
    if not bmetrics:
        return default
    return bmetrics[-1]["metrics"].get(key, default)

# ══════════════════════════════════════════════════════════════════════════════
#  KPI STRIP
# ══════════════════════════════════════════════════════════════════════════════
k = st.columns(6)
with k[0]: st.metric("F1 Score",   f"{_val('f1_score'):.3f}",
                      delta=f"{_val('f1_score') - _val('f1_score', 0):.3f}" if len(bmetrics) > 1 else None)
with k[1]: st.metric("Precision",  f"{_val('precision'):.3f}")
with k[2]: st.metric("Recall",     f"{_val('recall'):.3f}")
with k[3]:
    sigma_now   = bmetrics[-1]["sigma"] if bmetrics else 0
    sigma_delta = (sigma_now - bmetrics[0]["sigma"]) if len(bmetrics) > 1 else None
    st.metric("SIGMA Rules", sigma_now, delta=sigma_delta)
with k[4]:
    nova_rate = 0.0
    if record and record.nova_evasion_history:
        nova_rate = max(record.nova_evasion_history)
    st.metric("NOVA Peak Evasion", f"{nova_rate:.1%}")
with k[5]:
    if record:
        d  = sum(1 for w in record.winner_history if w == "defender")
        a  = sum(1 for w in record.winner_history if w == "attacker")
        dr = sum(1 for w in record.winner_history if w == "draw")
        st.metric("Record D/A/=", f"{d} / {a} / {dr}")
    else:
        st.metric("Battles Done", f"{len(bmetrics)} / {n_battles}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📈 Live Metrics", "🏆 ELO Leaderboard", "🔬 Techniques",
    "📋 Event Feed",   "🛡 SOAR Actions",    "🗺 ATT&CK",     "📤 Export"
])
tab_metrics, tab_elo, tab_tech, tab_feed, tab_soar, tab_attck, tab_export = tabs

# ─── Tab 1: Live Metrics ──────────────────────────────────────────────────────
with tab_metrics:
    if running:
        prog = len(bmetrics) / n_battles if n_battles else 0
        st.progress(prog, text=f"⏳ Battle {len(bmetrics)} / {n_battles} running…")

    if bmetrics:
        f1s    = [b["metrics"]["f1_score"]  for b in bmetrics]
        precs  = [b["metrics"]["precision"] for b in bmetrics]
        recs   = [b["metrics"]["recall"]    for b in bmetrics]
        sigmas = [b["sigma"]                for b in bmetrics]
        winners= [b["winner"]               for b in bmetrics]

        col_l, col_r = st.columns([3, 2])

        with col_l:
            st.markdown('<div class="section-header">Defender Performance Over Battles</div>',
                        unsafe_allow_html=True)
            fig = go.Figure()
            for y, name, color, dash in [
                (f1s,   "F1 Score",  "#00d2ff", "solid"),
                (precs, "Precision", "#6366f1", "dot"),
                (recs,  "Recall",    "#10b981", "dash"),
            ]:
                fig.add_trace(go.Scatter(
                    x=battles, y=y, mode="lines+markers", name=name,
                    line=dict(color=color, width=2.5, dash=dash),
                    marker=dict(size=7, symbol="circle"),
                    hovertemplate=f"<b>{name}</b>: %{{y:.3f}}<extra></extra>"
                ))
            fig.add_hrect(y0=0.7, y1=1.05, fillcolor="#10b981", opacity=0.05,
                          line_width=0, annotation_text="🛡 Safe Zone",
                          annotation_font_color="#10b981")
            fig.add_hrect(y0=0.0, y1=0.30, fillcolor="#ef4444", opacity=0.05,
                          line_width=0, annotation_text="⚠ Danger Zone",
                          annotation_font_color="#ef4444")
            fig.update_layout(height=320, yaxis=dict(range=[0, 1.08]),
                              xaxis_title="Battle #", **NEXUS_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-header">SIGMA Rule Evolution</div>',
                        unsafe_allow_html=True)
            baseline = sigmas[0] if sigmas else 10
            auto = [s - baseline for s in sigmas]
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=battles, y=[baseline]*len(battles),
                                  name="Baseline", marker_color="#334155",
                                  hovertemplate="Baseline: %{y}<extra></extra>"))
            fig2.add_trace(go.Bar(x=battles, y=auto,
                                  name="Auto-generated", marker_color="#f59e0b",
                                  base=[baseline]*len(battles),
                                  hovertemplate="New rules: %{y}<extra></extra>"))
            fig2.update_layout(height=320, barmode="stack",
                               xaxis_title="Battle #", yaxis_title="Rules",
                               **NEXUS_LAYOUT)
            st.plotly_chart(fig2, use_container_width=True)

        # ── Winner history timeline ──────────────────────────────────────────
        st.markdown('<div class="section-header">Battle Outcomes</div>',
                    unsafe_allow_html=True)
        win_colors = {"defender": "#10b981", "attacker": "#ef4444", "draw": "#f59e0b"}
        outcome_fig = go.Figure()
        for b_num, winner in zip(battles, winners):
            outcome_fig.add_trace(go.Scatter(
                x=[b_num], y=[1],
                mode="markers+text",
                marker=dict(size=40, color=win_colors.get(winner, "#64748b"),
                            symbol="square", opacity=0.85,
                            line=dict(width=2, color="white")),
                text=[winner[:1].upper()],
                textfont=dict(color="white", size=14, family="monospace"),
                textposition="middle center",
                name=winner,
                hovertemplate=f"<b>Battle {b_num}</b>: {winner}<extra></extra>",
                showlegend=b_num == 1
            ))
        outcome_fig.update_layout(
            height=110, showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, tickvals=battles,
                       title="Battle #"),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       range=[0.6, 1.4]),
            plot_bgcolor="#070b14", paper_bgcolor="#0d1117",
            margin=dict(t=10, b=30, l=10, r=10)
        )
        st.plotly_chart(outcome_fig, use_container_width=True)

        # ── Confusion matrix ─────────────────────────────────────────────────
        st.markdown('<div class="section-header">Confusion Matrix — Last Battle</div>',
                    unsafe_allow_html=True)
        last = bmetrics[-1]["metrics"]
        tp = last.get("true_positives",  0)
        fp = last.get("false_positives", 0)
        fn = last.get("false_negatives", 0)
        tn = last.get("true_negatives",  0)
        cm_fig = go.Figure(go.Heatmap(
            z=[[tp, fn], [fp, tn]],
            x=["Predicted Malicious", "Predicted Benign"],
            y=["Actual Malicious", "Actual Benign"],
            colorscale=[[0, "#0d1117"], [1, "#00d2ff"]],
            text=[[f"<b>TP</b><br>{tp}", f"<b>FN</b><br>{fn}"],
                  [f"<b>FP</b><br>{fp}", f"<b>TN</b><br>{tn}"]],
            texttemplate="%{text}", showscale=False,
            hovertemplate="<b>%{y} / %{x}</b><br>Count: %{z}<extra></extra>",
        ))
        cm_fig.update_layout(height=260, paper_bgcolor="#0d1117",
                             plot_bgcolor="#070b14",
                             font=dict(color="#e2e8f0"),
                             margin=dict(t=10, b=30, l=10, r=10))
        st.plotly_chart(cm_fig, use_container_width=True)

    else:
        st.markdown("""
        <div style='text-align:center; padding:60px 0; color:#334155'>
            <div style='font-size:3rem'>⚔️</div>
            <div style='font-size:1.1rem; margin-top:12px'>
                Configure your campaign in the sidebar and click <b>Launch Campaign</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── Tab 2: ELO ───────────────────────────────────────────────────────────────
with tab_elo:
    if record and record.final_elo_table:
        lb     = record.final_elo_table
        names  = [r["entity"] for r in lb]
        elos   = [r["elo"]    for r in lb]

        st.markdown('<div class="section-header">ELO Leaderboard</div>',
                    unsafe_allow_html=True)

        bar_colors = []
        for n in names:
            if n == "DEFENDER":  bar_colors.append("#10b981")
            elif n == "NOVA":    bar_colors.append("#ef4444")
            else:                bar_colors.append("#6366f1")

        fig3 = go.Figure(go.Bar(
            x=names, y=elos,
            marker=dict(color=bar_colors,
                        line=dict(color="rgba(255,255,255,0.1)", width=1)),
            text=[f"{e:.0f}" for e in elos], textposition="outside",
            textfont=dict(color="#e2e8f0"),
            hovertemplate="<b>%{x}</b><br>ELO: %{y:.0f}<extra></extra>",
        ))
        fig3.update_layout(
            height=320,
            yaxis=dict(range=[min(elos) - 80, max(elos) + 100]),
            xaxis_title="", yaxis_title="ELO Rating",
            **NEXUS_LAYOUT
        )
        st.plotly_chart(fig3, use_container_width=True)

        import pandas as pd
        df = pd.DataFrame([{
            "🏅 Rank": r["rank"], "Entity": r["entity"],
            "ELO": int(r["elo"]), "Peak ELO": int(r["peak_elo"]),
            "W": r["wins"], "L": r["losses"],
            "Win %": f"{r['win_rate']*100:.1f}%",
            "Evasion %": f"{r['evasion_rate']*100:.1f}%",
            "Top TTP": r["top_technique"],
        } for r in lb])
        st.dataframe(df, hide_index=True, use_container_width=True)

        if record.elo_history:
            st.markdown('<div class="section-header" style="margin-top:20px">ELO Trend Per Battle</div>',
                        unsafe_allow_html=True)
            fig4 = go.Figure()
            for i, name in enumerate(record.elo_history[0].keys()):
                ys = [b.get(name, 1000) for b in record.elo_history]
                color = "#10b981" if name == "DEFENDER" else PALETTE[i % len(PALETTE)]
                fig4.add_trace(go.Scatter(
                    x=list(range(1, len(ys) + 1)), y=ys,
                    mode="lines+markers", name=name,
                    line=dict(color=color, width=2),
                    marker=dict(size=6),
                    hovertemplate=f"<b>{name}</b> Battle %{{x}}: %{{y:.0f}}<extra></extra>"
                ))
            fig4.update_layout(height=300, xaxis_title="Battle #",
                               yaxis_title="ELO", **NEXUS_LAYOUT)
            st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("🏆 Complete a campaign to see ELO rankings and trends.")

# ─── Tab 3: Techniques ────────────────────────────────────────────────────────
with tab_tech:
    if record and record.technique_stats:
        import pandas as pd
        try:
            from research.attck_client import get_client
            attck = get_client(use_live=False)
            stats = record.technique_stats
            for s in stats:
                meta = attck.get_technique(s["technique"])
                s["name"]   = meta["name"]
                s["tactic"] = meta["tactic_name"]
        except Exception:
            stats = record.technique_stats
            for s in stats:
                s.setdefault("name",   "Unknown")
                s.setdefault("tactic", "Unknown")

        st.markdown('<div class="section-header">Detection vs Evasion by Technique</div>',
                    unsafe_allow_html=True)
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(
            name="Detected", marker_color="#10b981",
            x=[s["technique"] for s in stats],
            y=[s["detection_rate"] for s in stats],
            hovertemplate="<b>%{x}</b><br>Detection: %{y:.1%}<extra></extra>",
        ))
        fig5.add_trace(go.Bar(
            name="Evaded", marker_color="#ef4444",
            x=[s["technique"] for s in stats],
            y=[s["evasion_rate"] for s in stats],
            hovertemplate="<b>%{x}</b><br>Evasion: %{y:.1%}<extra></extra>",
        ))
        fig5.update_layout(barmode="group", height=320, yaxis_title="Rate",
                           **NEXUS_LAYOUT)
        st.plotly_chart(fig5, use_container_width=True)

        df2 = pd.DataFrame([{
            "TTP": s["technique"], "Name": s["name"], "Tactic": s["tactic"],
            "Uses": s["uses"], "Evaded": s["evaded"], "Detected": s["detected"],
            "Evasion %": f"{s['evasion_rate']:.1%}",
            "Detection %": f"{s['detection_rate']:.1%}",
        } for s in stats])
        st.dataframe(df2, hide_index=True, use_container_width=True)
    else:
        st.info("🔬 Complete a campaign to see technique-level breakdown.")

# ─── Tab 4: Event Feed ────────────────────────────────────────────────────────
with tab_feed:
    st.markdown('<div class="section-header">Live Attack Event Feed</div>',
                unsafe_allow_html=True)
    feed = st.session_state.live_feed
    if running:
        st.progress(len(bmetrics) / n_battles if n_battles else 0,
                    text=f"Battle {len(bmetrics)} / {n_battles} in progress…")

    if feed:
        lines_html = ""
        for line in reversed(feed[-80:]):
            if line.startswith("⚔️"):
                lines_html += f'<div class="battle-line">{line}</div>'
            elif "detect" in line.lower() or "✓" in line:
                lines_html += f'<div class="detect-line">{line}</div>'
            else:
                lines_html += f'<div class="attack-line">{line}</div>'
        st.markdown(f'<div class="feed-box">{lines_html}</div>',
                    unsafe_allow_html=True)
        st.caption(f"Showing latest {min(80, len(feed))} of {len(feed)} events")
    else:
        st.markdown("""
        <div class="feed-box" style="text-align:center; color:#334155; padding:40px">
            Feed will populate as battles run…
        </div>
        """, unsafe_allow_html=True)

# ─── Tab 5: SOAR ─────────────────────────────────────────────────────────────
with tab_soar:
    st.markdown('<div class="section-header">Autonomous SOAR Counterstrike Actions</div>',
                unsafe_allow_html=True)

    soar_totals = {"honeypot": 0, "lockout": 0, "isolate": 0,
                   "deception": 0, "hunt": 0}
    if bmetrics:
        for bm in bmetrics:
            evo = bm.get("evolution", {})
            for k2, v in evo.get("soar_stats", {}).get("actions_by_type", {}).items():
                soar_totals[k2] = soar_totals.get(k2, 0) + v

    total_actions = sum(soar_totals.values())

    col1, col2 = st.columns([3, 1])
    with col1:
        soar_colors = {
            "honeypot": "#f59e0b", "lockout": "#ef4444",
            "isolate":  "#8b5cf6", "deception": "#06b6d4",
            "hunt":     "#10b981",
        }
        soar_emojis = {
            "honeypot": "🍯", "lockout": "🔒",
            "isolate": "🚫", "deception": "🎭", "hunt": "🔍",
        }
        fig6 = go.Figure()
        for action, count in soar_totals.items():
            fig6.add_trace(go.Bar(
                x=[action],
                y=[count],
                name=action.title(),
                marker_color=soar_colors.get(action, "#64748b"),
                text=[f"{soar_emojis.get(action,'')} {count}"],
                textposition="outside",
                textfont=dict(color="#e2e8f0"),
                hovertemplate=f"<b>{action.title()}</b>: %{{y}} actions<extra></extra>",
            ))
        fig6.update_layout(height=320, yaxis_title="Total Actions",
                           showlegend=False, **NEXUS_LAYOUT)
        st.plotly_chart(fig6, use_container_width=True)

    with col2:
        st.metric("Total Actions", total_actions)
        st.divider()
        for action, count in soar_totals.items():
            pct = f"{count/total_actions*100:.0f}%" if total_actions else "0%"
            st.markdown(
                f'{soar_emojis.get(action,"⚡")} **{action.title()}** &nbsp;'
                f'<span style="color:#64748b">{count} ({pct})</span>',
                unsafe_allow_html=True
            )

    # Per-battle SOAR timeline
    if len(bmetrics) > 1:
        st.markdown('<div class="section-header" style="margin-top:20px">SOAR Actions Per Battle</div>',
                    unsafe_allow_html=True)
        fig7 = go.Figure()
        for action, color in soar_colors.items():
            per_battle = []
            for bm in bmetrics:
                evo = bm.get("evolution", {})
                per_battle.append(
                    evo.get("soar_stats", {}).get("actions_by_type", {}).get(action, 0)
                )
            fig7.add_trace(go.Scatter(
                x=battles, y=per_battle, mode="lines+markers",
                name=action.title(), line=dict(color=color, width=2),
                stackgroup="one", groupnorm="",
                hovertemplate=f"<b>{action.title()}</b> Battle %{{x}}: %{{y}}<extra></extra>"
            ))
        fig7.update_layout(height=260, xaxis_title="Battle #",
                           yaxis_title="Actions", **NEXUS_LAYOUT)
        st.plotly_chart(fig7, use_container_width=True)

# ─── Tab 6: ATT&CK ───────────────────────────────────────────────────────────
with tab_attck:
    st.markdown('<div class="section-header">MITRE ATT&CK Context & Kill-Chain</div>',
                unsafe_allow_html=True)
    try:
        from research.attck_client import get_client
        attck = get_client(use_live=False)
        attck_ok = True
    except Exception:
        attck_ok = False

    if record and record.technique_stats and attck_ok:
        for s in record.technique_stats:
            meta = attck.get_technique(s["technique"])
            s["name"]       = meta["name"]
            s["tactic"]     = meta["tactic_name"]
            s["detection"]  = meta["detection"]
            s["platforms"]  = ", ".join(meta["platforms"][:3])

        all_techs = [s["technique"] for s in record.technique_stats]
        chain     = attck.validate_tactic_chain(all_techs)

        col_a, col_b = st.columns([1, 1])

        with col_a:
            st.markdown("**Kill-Chain Coverage**")
            completeness = chain["completeness"]
            st.progress(completeness, text=f"{completeness:.0%} of MITRE tactics covered")
            phases = " → ".join(chain["covered_phases"])
            st.markdown(f"<span style='color:#94a3b8; font-size:0.85rem'>{phases}</span>",
                        unsafe_allow_html=True)
            if chain["violations"]:
                st.warning(f"⚠ {len(chain['violations'])} out-of-order transitions")
                for v in chain["violations"]:
                    st.caption(f"  {v['from']} → {v['to']}: {v['note']}")
            else:
                st.success("✅ Kill-chain sequence is plausible")

            # Tactic coverage donut
            covered = len(chain["covered_phases"])
            total_tactics = 14  # MITRE ATT&CK tactical phases
            tactic_fig = go.Figure(go.Pie(
                labels=["Covered", "Not Seen"],
                values=[covered, max(0, total_tactics - covered)],
                marker=dict(colors=["#00d2ff", "#1e293b"]),
                hole=0.65,
                textinfo="none",
                hovertemplate="<b>%{label}</b>: %{value}<extra></extra>",
            ))
            tactic_fig.add_annotation(text=f"{covered}/{total_tactics}",
                                      showarrow=False,
                                      font=dict(size=22, color="#00d2ff", family="Segoe UI"))
            tactic_fig.update_layout(height=220, showlegend=True,
                                     paper_bgcolor="#0d1117",
                                     font=dict(color="#94a3b8"),
                                     margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(tactic_fig, use_container_width=True)

        with col_b:
            st.markdown("**Technique Details**")
            for s in record.technique_stats:
                evasion_color = "#ef4444" if s["evasion_rate"] > 0.4 else "#10b981"
                with st.expander(f"`{s['technique']}` — {s['name']}"):
                    cols_t = st.columns(2)
                    cols_t[0].caption(f"**Tactic:** {s['tactic']}")
                    cols_t[1].caption(f"**Platforms:** {s['platforms']}")
                    st.caption(f"**Detection guidance:** {s['detection'][:200]}…")
                    st.markdown(
                        f"Evasion rate: "
                        f"<span style='color:{evasion_color};font-weight:600'>"
                        f"{s['evasion_rate']:.1%}</span>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"[🔗 View on ATT&CK ↗](https://attack.mitre.org/techniques/{s['technique']}/)"
                    )

        # Navigator download
        nav_files = sorted(Path("data/research").glob("navigator_*.json")) \
                    if Path("data/research").exists() else []
        if nav_files:
            st.divider()
            col_nav1, col_nav2 = st.columns([3, 1])
            with col_nav1:
                st.markdown("**📥 ATT&CK Navigator Layer**")
                st.caption("Import at: https://mitre-attack.github.io/attack-navigator/")
            with col_nav2:
                nav_content = nav_files[-1].read_text(encoding="utf-8", errors="replace")
                st.download_button("⬇ Download JSON", data=nav_content,
                                   file_name=nav_files[-1].name,
                                   mime="application/json",
                                   use_container_width=True)
    else:
        st.info("🗺 Complete a campaign to see ATT&CK context and kill-chain analysis.")

# ─── Tab 7: Export ────────────────────────────────────────────────────────────
with tab_export:
    st.markdown('<div class="section-header">Research Output Export</div>',
                unsafe_allow_html=True)

    BINARY_EXTS = {'.pdf', '.png', '.jpg', '.jpeg', '.gif', '.zip'}

    def _dl_btn(col, title, icon, glob_pattern, base_dir, mime, label):
        with col:
            st.markdown(
                f"<div style='text-align:center; padding:10px; background:#0f172a; "
                f"border:1px solid #1e293b; border-radius:8px; margin-bottom:8px'>"
                f"<div style='font-size:1.6rem'>{icon}</div>"
                f"<div style='font-size:0.8rem; color:#94a3b8; margin-top:4px'>{title}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            files = sorted(Path(base_dir).glob(glob_pattern)) \
                    if Path(base_dir).exists() else []
            if files:
                f = files[-1]
                content = f.read_bytes() if f.suffix.lower() in BINARY_EXTS \
                          else f.read_text(encoding='utf-8', errors='replace')
                st.download_button(
                    label, data=content, file_name=f.name, mime=mime,
                    use_container_width=True
                )
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                st.caption(f"`{f.name}` · {mtime}")
            else:
                st.caption("Run a campaign first.")

    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    _dl_btn(col_e1, "STIX 2.1 Bundle",   "📦", "campaign_*.json",
            "data/stix",     "application/json", "⬇ STIX Bundle")
    _dl_btn(col_e2, "Training Dataset",  "📊", "nexus_logs.csv",
            "data/datasets", "text/csv",          "⬇ CSV Dataset")
    _dl_btn(col_e3, "Paper Draft (MD)",  "📝", "paper_*.md",
            "data/research", "text/markdown",     "⬇ Paper Draft")
    _dl_btn(col_e4, "Navigator Layer",   "🗺", "navigator_*.json",
            "data/research", "application/json",  "⬇ Navigator JSON")

    st.markdown("<br>", unsafe_allow_html=True)
    col_e5, col_e6, col_e7 = st.columns(3)
    _dl_btn(col_e5, "D3 Kill-Chain HTML", "🕸", "killchain_*.html",
            "data/research", "text/html",        "⬇ Kill-Chain HTML")
    _dl_btn(col_e6, "PDF Paper",          "📄", "paper_*.pdf",
            "data/research", "application/pdf",  "⬇ PDF Paper")
    _dl_btn(col_e7, "LaTeX Source",       "📐", "paper_*.tex",
            "data/research", "text/plain",       "⬇ LaTeX .tex")

    # ── Bulk run statistics ──────────────────────────────────────────────────
    bulk_path = Path("data/bulk/bulk_summary.json")
    if bulk_path.exists():
        st.divider()
        st.markdown('<div class="section-header">📈 Bulk Run Statistics</div>',
                    unsafe_allow_html=True)
        bs = json.loads(bulk_path.read_text(encoding="utf-8", errors="replace"))
        bcols = st.columns(4)
        with bcols[0]: st.metric("Mean F1",        f"{bs['f1']['mean']:.3f}",
                                  delta=f"σ={bs['f1']['stdev']:.3f}")
        with bcols[1]: st.metric("Mean Precision",  f"{bs['precision']['mean']:.3f}")
        with bcols[2]: st.metric("Defender Wins",
                                  f"{bs['winners']['defender']}/{bs['n_simulations']}",
                                  delta=f"{bs['winner_rates']['defender']:.0%}")
        with bcols[3]: st.metric("Rule Gen Rate",   f"{bs['rule_generation_rate']:.0%}")

        pie_col, _ = st.columns([1, 2])
        with pie_col:
            winner_fig = go.Figure(go.Pie(
                labels=["Defender", "Draw", "Attacker"],
                values=[bs["winners"]["defender"],
                        bs["winners"]["draw"],
                        bs["winners"]["attacker"]],
                marker=dict(colors=["#10b981", "#f59e0b", "#ef4444"]),
                hole=0.5, textinfo="label+percent",
                hovertemplate="<b>%{label}</b>: %{value} (%{percent})<extra></extra>",
            ))
            winner_fig.add_annotation(text="Outcomes", showarrow=False,
                                      font=dict(size=13, color="#94a3b8"))
            winner_fig.update_layout(height=260, showlegend=False,
                                     paper_bgcolor="#0d1117",
                                     font=dict(color="#e2e8f0"),
                                     margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(winner_fig, use_container_width=True)
    else:
        st.info("Run `python scripts/run_simulation.py --bulk --bulk-n 100` to generate bulk statistics.")
