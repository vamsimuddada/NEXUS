import os

code = '''"""
NEXUS War Room Dashboard — Professional Edition
================================================
Autonomous Cyber Warfare Simulation & Self-Evolving SOC Platform
"""
import sys, os, json, time, threading, queue, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import datetime, timezone
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd

st.set_page_config(page_title="NEXUS Command", page_icon="globe", layout="wide", initial_sidebar_state="expanded")

# ------------------------------------------------------------------------------
#  ABOUT PROJECT PAGE (ROUTING)
# ------------------------------------------------------------------------------
if st.query_params.get("page") == "about":
    st.markdown("""
    <style>
    /* Restore streamlits native background for this page */
    [data-testid="stAppViewContainer"] { background: #f8fafc !important; }
    .about-container { max-width: 900px; margin: 0 auto; padding: 40px; background: rgba(255,255,255,1); border-radius: 24px; box-shadow: 0 20px 40px rgba(15,23,42,0.05); border: 1px solid rgba(226,232,240,0.8); }
    .about-title { font-family: 'Google Sans', 'Plus Jakarta Sans', sans-serif; font-size: 3rem; font-weight: 800; color: #0f172a; letter-spacing: -1px; margin-bottom: 20px; }
    .about-text { font-size: 1.15rem; color: #475569; line-height: 1.8; margin-bottom: 24px; font-family: 'Plus Jakarta Sans', sans-serif; }
    .arch-box { background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 16px; padding: 24px; margin-bottom: 20px; }
    .arch-title { color: #2563eb; font-weight: 800; font-size: 1.2rem; display: flex; align-items: center; gap: 10px; margin-bottom: 12px; font-family: 'Google Sans', 'Plus Jakarta Sans', sans-serif; }
    </style>
    """, unsafe_allow_html=True)
    
    if st.button("? Back to Command Center"):
        st.query_params.clear()
        st.rerun()
        
    st.markdown("""
    <div class="about-container">
        <div class="about-title">About NEXUS</div>
        <p class="about-text">
            <b>Neural Exploitation & eXplainable Unified Security (NEXUS)</b> is an autonomous, self-evolving cyber warfare simulation platform. It is designed to act as an intelligent proving ground where autonomous Red Team agents and Blue Team defense networks wage continuous, self-improving campaigns against each other.
        </p>
        <h3 style="color:#0f172a; margin-top:40px; margin-bottom:20px; font-weight:800; font-family: 'Google Sans', sans-serif;">System Architecture</h3>
        <div class="arch-box">
            <div class="arch-title">?? Red Team (Autonomous Attackers)</div>
            <p style="margin:0; color:#475569; font-size:1rem; line-height:1.6; font-family: 'Plus Jakarta Sans', sans-serif;">Powered by intelligent agents, the Red Team dynamically scans the network, selects targets, and launches exploits based on real-time threat intelligence (TAXII/STIX). They possess a <b>Semantic Vector Memory</b> that allows them to remember which attacks worked and adapt to the Blue Team's defenses.</p>
        </div>
        <div class="arch-box">
            <div class="arch-title">??? Blue Team (SIEM & Defense)</div>
            <p style="margin:0; color:#475569; font-size:1rem; line-height:1.6; font-family: 'Plus Jakarta Sans', sans-serif;">The Blue Team monitors a simulated network (represented by the Live Threat Graph) and generates alerts based on SIEM rules. When attacks are detected, they block the originating IPs and patch vulnerabilities, forcing the Red Team to evolve their tactics.</p>
        </div>
        <div class="arch-box">
            <div class="arch-title">?? The AI Brain (Provider)</div>
            <p style="margin:0; color:#475569; font-size:1rem; line-height:1.6; font-family: 'Plus Jakarta Sans', sans-serif;">The core reasoning engine of NEXUS can be toggled between an offline <b>Mock Engine</b> (for high-speed, deterministic simulations) or a live <b>Ollama Model</b> (for true, localized AI reasoning and decision making).</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ------------------------------------------------------------------------------
#  GLOBAL THEME
# ------------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body { font-family: 'Google Sans', 'Plus Jakarta Sans', sans-serif !important; color: #1e293b !important; }
h1, h2, h3, h4, h5, h6, p, label, a, li { font-family: 'Google Sans', 'Plus Jakarta Sans', sans-serif !important; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
[data-testid="stHeader"] { background: transparent !important; pointer-events: none !important; }
[data-testid="stHeader"] button { pointer-events: auto !important; }
span[class*="material-symbols"] { font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important; }

/* -- Ultimate Fallback for Blocked Google Fonts -- */
[data-testid="collapsedControl"] span, [data-testid="stSidebarCollapsedControl"] span, [data-testid="stSidebar"] button[kind="headerNoPadding"] span { 
    opacity: 0 !important; color: transparent !important; font-size: 0px !important; line-height: 0 !important;
}

/* -- Remove Massive Native Gaps -- */
[data-testid="stAppViewBlockContainer"] { padding-top: 1rem !important; }
[data-testid="stTabs"] { margin-top: -10px !important; }

/* -- Floating Tabs Navigation -- */
[data-testid="stTabs"] > div:first-child {
    background: rgba(255, 255, 255, 0.9) !important; backdrop-filter: blur(20px) saturate(150%) !important;
    padding-top: 15px !important; padding-bottom: 5px !important; padding-left: 20px !important;
    border-bottom: 1px solid rgba(226, 232, 240, 0.8) !important;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05) !important;
    z-index: 99999 !important;
}
/* Premium Tab Button Styling */
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Plus Jakarta Sans', 'Google Sans', sans-serif !important;
    font-weight: 700 !important; font-size: 0.95rem !important; letter-spacing: 0.5px !important;
    color: #64748b !important; padding: 12px 24px !important; border-radius: 12px !important;
    transition: all 0.3s ease !important; background: transparent !important; border: none !important;
}
[data-testid="stTabs"] button[role="tab"]:hover {
    color: #0f172a !important; background: rgba(241, 245, 249, 0.8) !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #2563eb !important; background: rgba(37, 99, 235, 0.1) !important;
    box-shadow: inset 0 -3px 0 0 #2563eb !important; border-bottom-left-radius: 0px !important; border-bottom-right-radius: 0px !important;
}

/* -- Staggered Fade Up -- */
@keyframes fadeUp {
    0% { opacity: 0; transform: translateY(20px); filter: blur(10px); }
    100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
}
.stPlotlyChart, .stDataFrame, .stRadio, .stButton, .kpi-card, .status-card, .hero-header {
    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
/* Ensure tabs never receive a transform trap */
[data-testid="stTabs"], [data-testid="stTabs"] > div {
    animation: none !important;
}

/* -- Max Premium Sidebar -- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.7) 100%) !important;
    backdrop-filter: blur(40px) saturate(250%);
    border-right: 1px solid rgba(255, 255, 255, 1) !important;
    box-shadow: 20px 0 50px rgba(15, 23, 42, 0.05), inset -2px 0 10px rgba(255,255,255,0.5);
}
[data-testid="stSidebar"] * { color: #1e293b !important; }

/* Animated Logo Ring */
@keyframes spin-slow { 100% { transform: rotate(360deg); } }
.logo-ring { transform-origin: center; animation: spin-slow 10s linear infinite; stroke: url(#gradient-ring); }

/* Max Premium Nav Pills (Scoped to Sidebar only!) */
[data-testid="stSidebar"] .stRadio label {
    background: rgba(241, 245, 249, 0.5) !important;
    border: 1px solid rgba(226, 232, 240, 0.8);
    border-radius: 12px; padding: 12px 16px; margin-bottom: 8px;
    font-weight: 700; color: #475569 !important;
    box-shadow: inset 0 2px 4px rgba(255,255,255,0.5);
    transition: all 0.3s ease;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,1) !important; color: #0f172a !important;
    transform: translateX(10px); box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
    border: 1px solid rgba(255,255,255,1);
}
[data-testid="stSidebar"] .stRadio label[data-checked="true"] {
    background: linear-gradient(135deg, #2563eb, #6366f1) !important;
    color: white !important; border: none;
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.3), inset 0 2px 4px rgba(255,255,255,0.3);
}

/* -- Live Status Cards -- */
.status-card {
    background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(20px) saturate(150%);
    border: 1px solid rgba(255,255,255,1); border-radius: 20px; padding: 16px 24px;
    box-shadow: 0 4px 15px rgba(15, 23, 42, 0.05); display: flex; flex-direction: column; gap: 4px;
    transition: all 0.3s ease;
}
.status-card:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(15, 23, 42, 0.06); }
.status-card .status-title { font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.status-card .status-value { font-size: 1.1rem; color: #0f172a; font-weight: 800; display: flex; align-items: center; gap: 8px; }
.pulse-dot { width: 10px; height: 10px; border-radius: 50%; background: #10b981; box-shadow: 0 0 8px #10b981; animation: pulse-dot 2s infinite; }
@keyframes pulse-dot { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.2); } 100% { opacity: 1; transform: scale(1); } }

/* -- Hero Header -- */
.hero-header {
    font-family: 'Space Grotesk', 'Google Sans', sans-serif; font-weight: 800;
    font-size: 3.2rem; margin-bottom: 8px; background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; filter: drop-shadow(0 6px 15px rgba(37, 99, 235, 0.15));
}

/* -- Ultra Premium KPI Cards -- */
.kpi-card {
    background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(25px) saturate(150%); border-radius: 28px; padding: 32px;
    box-shadow: 0 15px 35px -10px rgba(15, 23, 42, 0.06), inset 0 2px 0 rgba(255,255,255,1);
    display: flex; flex-direction: column; border: 1px solid rgba(255, 255, 255, 1);
}
.kpi-title { font-family: 'Google Sans', 'Plus Jakarta Sans', sans-serif; font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 2.5px; font-weight: 800; margin-bottom: 14px; }
.kpi-value { font-family: 'Google Sans', 'Plus Jakarta Sans', sans-serif; font-size: 2.5rem; color: #0f172a; font-weight: 800; letter-spacing: -1.5px; line-height: 1; background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; filter: drop-shadow(0 4px 6px rgba(37, 99, 235, 0.1)); }
.kpi-trend { font-size: 0.95rem; color: #10b981; font-weight: 700; margin-top: 20px; display: flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.1); padding: 8px 16px; border-radius: 24px; width: fit-content; box-shadow: inset 0 1px 0 rgba(255,255,255,0.8); white-space: nowrap; }

/* -- Event Feed Terminal -- */
.event-feed {
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); border: 1px solid #e2e8f0;
    border-radius: 24px; padding: 24px; font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 0.85rem; line-height: 1.8; max-height: 400px; overflow-y: auto; color: #334155;
    box-shadow: inset 0 4px 10px rgba(15,23,42,0.02), 0 10px 25px rgba(15,23,42,0.03);
}

/* -- Modern Buttons -- */
.stButton > button {
    background: linear-gradient(135deg, #0f172a, #1e293b) !important; color: white !important; font-weight: 700 !important;
    border-radius: 14px !important; border: 1px solid rgba(255,255,255,0.2) !important; padding: 20px 40px !important;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.4), inset 0 2px 0 rgba(255,255,255,0.2) !important;
    transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) !important; text-transform: uppercase;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1e293b, #3b82f6) !important;
    box-shadow: 0 15px 35px -5px rgba(37, 99, 235, 0.5), inset 0 2px 0 rgba(255,255,255,0.3) !important;
    transform: translateY(-5px) scale(1.03) !important;
}

</style>
""", unsafe_allow_html=True)

NEXUS_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#475569", family="Plus Jakarta Sans"),
    xaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
    margin=dict(t=30, b=30, l=10, r=10),
)
PALETTE = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#10b981", "#34d399", "#f59e0b", "#ef4444"]

if "msg_queue" not in st.session_state: st.session_state.msg_queue = queue.Queue()
if "live_feed" not in st.session_state: st.session_state.live_feed = []
if "running" not in st.session_state: st.session_state.running = False

# ------------------------------------------------------------------------------
#  MAIN DASHBOARD HEADER
# ------------------------------------------------------------------------------
st.markdown("""
<div style='display: flex; align-items: center; gap: 20px; margin-bottom: 32px; margin-top: -55px;'>
    <div style='width:60px; height:60px; border-radius:50%; background:linear-gradient(135deg, #e0e7ff, #ffffff); display:flex; align-items:center; justify-content:center; box-shadow: 0 10px 25px rgba(37, 99, 235, 0.15); border: 1px solid rgba(255,255,255,1);'>
        <svg width='32' height='32' viewBox='0 0 24 24' fill='none' stroke='#3b82f6' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>
            <path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'></path>
        </svg>
    </div>
    <div style="display: flex; align-items: baseline; gap: 16px;">
        <div style="font-family:'Google Sans', 'Plus Jakarta Sans', sans-serif; font-size:3.2rem; font-weight:800; color:#0f172a; line-height:1; letter-spacing:-2px;">NEXUS</div>
        <div style="font-family:'Google Sans', 'Plus Jakarta Sans', sans-serif; font-size:1.1rem; font-weight:600; color:#64748b; letter-spacing:0px;">Neural Exploitation & eXplainable Unified Security</div>
        <a href="?page=about" target="_self" style="color:#3b82f6; margin-left:4px; margin-top:4px; opacity:0.6; transition:all 0.2s;" onmouseover="this.style.opacity=1; this.style.transform='scale(1.1)';" onmouseout="this.style.opacity=0.6; this.style.transform='scale(1)';" title="About Project">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# TABS
tab1, tab2, tab3 = st.tabs(["Command Center", "Threat Intelligence", "Analytics & Export"])

def kpi_card(title, value, trend, color, icon_svg):
    return f"""
    <div class="kpi-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
            </div>
            <div style="color: {color}; background: {color}15; padding: 12px; border-radius: 16px;">{icon_svg}</div>
        </div>
        <div class="kpi-trend">{trend}</div>
    </div>
    """

ICON_F1 = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline><polyline points="16 7 22 7 22 13"></polyline></svg>'
ICON_SHIELD = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
ICON_DB = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>'
ICON_WARN = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'

with tab1:
    st.markdown("<div class='hero-header' style='margin-top:-15px; font-size: 2.8rem; letter-spacing: -1px;'>Security Command Center</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; margin-bottom:32px; font-size:1.1rem; font-weight:500;'>Unified threat intelligence and autonomous agent telemetry.</p>", unsafe_allow_html=True)
    
    total_battles = 0
    defender_wins = 0
    avg_f1 = 0.0
    
    try:
        with sqlite3.connect("data/simulation_results.db") as conn:
            df_perf = pd.read_sql("SELECT data FROM simulation_results WHERE event_type='performance'", conn)
            if not df_perf.empty:
                f1_scores = df_perf["data"].apply(lambda x: json.loads(x).get("f1_score", 0))
                avg_f1 = f1_scores.mean()
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM simulation_results WHERE event_type='battle_result'")
            total_battles = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM simulation_results WHERE event_type='battle_result' AND data LIKE '%defender%'")
            defender_wins = c.fetchone()[0]
    except Exception as e: pass

    c1, c2, c3, c4 = st.columns(4)
    win_rate = (defender_wins/total_battles*100) if total_battles else 0
    c1.markdown(kpi_card("Mean F1 Score", f"{avg_f1:.3f}", "+0.02 vs last week", "#2563eb", ICON_F1), unsafe_allow_html=True)
    c2.markdown(kpi_card("Defend Win Rate", f"{win_rate:.1f}%", f"{defender_wins} total blocks", "#10b981", ICON_SHIELD), unsafe_allow_html=True)
    c3.markdown(kpi_card("Battles Logged", str(total_battles), "Simulation database", "#f59e0b", ICON_DB), unsafe_allow_html=True)
    c4.markdown(kpi_card("Active Threats", "6", "Persistent APT Actors", "#ef4444", ICON_WARN), unsafe_allow_html=True)
    
    st.markdown("<h3 style='color:#0f172a; font-family:\"Google Sans\", \"Plus Jakarta Sans\", sans-serif; font-weight:800; letter-spacing:-1px; margin-top:32px; margin-bottom:16px;'>Active Operation</h3>", unsafe_allow_html=True)
    op_c1, op_c2 = st.columns([3, 7])
    with op_c1:
        with st.container(border=True):
            provider = st.selectbox("AI Brain", ["Mock (offline)", "Ollama (local)"])
            turns = st.slider("Campaign Turns", 1, 10, 3)
            st.markdown("---")
            hosts = st.slider("Target Hosts", 2, 20, 4)
            users = st.slider("Simulated Users", 5, 50, 8)
            if st.button("INITIATE WARGAMES", use_container_width=True):
                st.session_state.running = True
                st.session_state.live_feed.append(f"Initializing campaign with {turns} turns...")
                msg_q = st.session_state.msg_queue
                def run_sim(q):
                    import subprocess
                    prov = "mock" if "Mock" in provider else "ollama"
                    cmd = [sys.executable, "scripts/run_simulation.py", "--provider", prov, "--turns", str(turns)]
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
                    for line in iter(process.stdout.readline, ""):
                        if line.strip(): q.put(line.strip())
                    process.stdout.close()
                    q.put("__DONE__")
                threading.Thread(target=run_sim, args=(msg_q,), daemon=True).start()
                st.rerun()
            
    with op_c2:
        if st.session_state.running:
            try:
                while True:
                    msg = st.session_state.msg_queue.get_nowait()
                    if msg == "__DONE__":
                        st.session_state.running = False
                        st.rerun()
                    else: st.session_state.live_feed.append(msg)
            except queue.Empty: pass
            if st.session_state.running: time.sleep(0.5); st.rerun()
            
        feed_html = "<div class='event-feed' style='height: 420px;'><div style='color:#0f172a;'>"
        if st.session_state.live_feed:
            for line in st.session_state.live_feed:
                if "Battle" in line or "WINNER" in line: feed_html += f"<div style='color:#f59e0b; font-weight:700;'>{line}</div>"
                elif "ATTACK" in line: feed_html += f"<div style='color:#ef4444;'>{line}</div>"
                elif "DETECT" in line or "SIGMA" in line: feed_html += f"<div style='color:#10b981;'>{line}</div>"
                else: feed_html += f"<div>{line}</div>"
        else: feed_html += "System standing by. No active campaigns."
        feed_html += "</div></div>"
        st.markdown(feed_html, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<h3 style='color:#0f172a; font-family:\"Google Sans\", \"Plus Jakarta Sans\", sans-serif; margin-bottom:16px; font-weight:700;'>Top Alerts by Severity</h3>", unsafe_allow_html=True)
        try:
            with sqlite3.connect("data/simulation_results.db") as conn:
                df_alerts = pd.read_sql("SELECT agent_id, data FROM simulation_results WHERE event_type='alert'", conn)
                if not df_alerts.empty:
                    df_alerts["severity"] = df_alerts["data"].apply(lambda x: json.loads(x).get("severity", "medium"))
                    sev_counts = df_alerts["severity"].value_counts().reset_index()
                    sev_counts.columns = ["Severity", "Count"]
                    fig = px.bar(sev_counts, x="Severity", y="Count", color="Severity", color_discrete_sequence=PALETTE)
                    fig.update_layout(NEXUS_LAYOUT)
                    st.plotly_chart(fig, use_container_width=True, theme=None)
                else: st.info("No alerts recorded yet.")
        except: st.info("Database not initialized.")
            
    with st.container(border=True):
        st.markdown("<h3 style='color:#0f172a; font-family:\"Google Sans\", \"Plus Jakarta Sans\", sans-serif; margin-bottom:16px; font-weight:700;'>Live Threat Graph</h3>", unsafe_allow_html=True)
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            from integrations.network_graph import build_graph_from_db
            fig2 = build_graph_from_db()
            fig2.update_layout(NEXUS_LAYOUT)
            fig2.update_layout(height=600)
            st.plotly_chart(fig2, use_container_width=True, theme=None)
        except Exception as e:
            st.warning(f"Graph engine error: {e}")
            
    st.markdown("<h3 style='color:#0f172a; font-family:\"Google Sans\", \"Plus Jakarta Sans\", sans-serif; margin-top:32px; margin-bottom:16px; font-weight:700;'>Recent Security Events</h3>", unsafe_allow_html=True)
    with st.container(border=True):
        try:
            with sqlite3.connect("data/simulation_results.db") as conn:
                df_events = pd.read_sql("SELECT timestamp, agent_id, event_type, data FROM simulation_results ORDER BY timestamp DESC LIMIT 5", conn)
                if not df_events.empty:
                    st.dataframe(df_events, use_container_width=True, hide_index=True)
                else: st.info("No recent events.")
        except: st.info("Database not initialized.")

with tab2:
    st.markdown("<h2 style='color:#0f172a; font-family:\"Google Sans\", \"Plus Jakarta Sans\", sans-serif; font-weight:800; letter-spacing:-1px; margin-bottom:24px;'>Live TAXII Intel</h2>", unsafe_allow_html=True)
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from integrations.taxii_client import get_taxii
        client = get_taxii(use_live=False)
        groups = client.get_all_apt_groups()

        r1, r2 = st.columns([1, 2])
        with r1:
            with st.container(border=True):
                selected_apt = st.radio("Tracked Threat Actors", groups)
            
        with r2:
            profile = client.get_apt_profile(selected_apt)
            with st.container(border=True):
                st.markdown(f"<h3 style='color:#ef4444; margin-top:0;'>{selected_apt}</h3>", unsafe_allow_html=True)
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("Origin", profile.get('origin', 'Unknown'))
                c_b.metric("Motivation", profile.get('motivation', 'Unknown'))
                c_c.metric("Primary Target", profile.get('targets', ['Unknown'])[0])
                st.markdown("**Known Tools & Malware:**")
                for mw in profile.get('tools', []): st.markdown(f"- {mw}")
    except Exception as e:
        st.error(f"Failed to load Threat Intel: {e}")

with tab3:
    st.markdown("<h2 style='color:#0f172a; font-family:\"Google Sans\", \"Plus Jakarta Sans\", sans-serif; font-weight:800; letter-spacing:-1px; margin-bottom:24px;'>Reporting & SIEM Integration</h2>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### Export Artifacts")
        def dl_btn(title, path, mime):
            p = Path(path)
            if p.exists(): st.download_button(f"Download {title}", data=p.read_bytes(), file_name=p.name, mime=mime)
            else: st.button(f"Missing {title}", disabled=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: dl_btn("SIEM Logs (NDJSON)", "data/siem/nexus_events.ndjson", "application/x-ndjson")
        with c2: dl_btn("Vector Memory (SQLite)", "data/nexus_memory.db", "application/x-sqlite3")
        with c3: dl_btn("Simulation Results (DB)", "data/simulation_results.db", "application/x-sqlite3")
        with c4: dl_btn("Attack Graph (JSON)", "data/attack_graph.json", "application/json")
        
    try:
        from integrations.vector_memory import get_memory
        with st.container(border=True):
            st.markdown("### Semantic Vector Memory Store")
            st.info("The agents use a pure-Python TF-IDF vector database to remember past engagements.")
            with sqlite3.connect("data/nexus_memory.db") as conn:
                df = pd.read_sql("SELECT agent_id, category, content FROM memories LIMIT 10", conn)
                st.dataframe(df, use_container_width=True)
    except: pass
'''

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Dashboard fully restored and updated safely.")
