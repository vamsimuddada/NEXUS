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
            Neural Exploitation &amp; eXplainable Unified Security
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
        st.caption(f"💾 DB: 