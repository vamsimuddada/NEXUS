import sys
with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(r'''"""
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700;800&display=swap');

html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; color: #1e293b !important; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
[data-testid="stHeader"] { background: transparent !important; }

.ambient-orb {
    position: fixed; border-radius: 50%; filter: blur(80px); z-index: -1;
    animation: float 20s infinite ease-in-out alternate; opacity: 0.3;
}
.orb-1 { top: -10%; left: -10%; width: 500px; height: 500px; background: rgba(37, 99, 235, 0.4); animation-delay: 0s; }
.orb-2 { bottom: -20%; right: -10%; width: 600px; height: 600px; background: rgba(139, 92, 246, 0.3); animation-delay: -5s; }
.orb-3 { top: 40%; left: 60%; width: 400px; height: 400px; background: rgba(16, 185, 129, 0.2); animation-delay: -10s; }

@keyframes float {
    0% { transform: translate(0, 0) scale(1); }
    33% { transform: translate(50px, -50px) scale(1.1); }
    66% { transform: translate(-30px, 40px) scale(0.9); }
    100% { transform: translate(0, 0) scale(1); }
}

[data-testid="stAppViewContainer"] {
    background-color: #f1f5f9 !important;
    background-image: 
        linear-gradient(rgba(37, 99, 235, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(37, 99, 235, 0.03) 1px, transparent 1px) !important;
    background-size: 30px 30px !important;
    background-position: center center !important;
    animation: grid-move 30s linear infinite; position: relative; z-index: 1;
}
@keyframes grid-move { 100% { background-position: 30px 30px; } }

@keyframes fadeUp {
    0% { opacity: 0; transform: translateY(30px) scale(0.95); filter: blur(10px); }
    100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
}
.stMarkdown, .stPlotlyChart, .stDataFrame, .stRadio, .stButton {
    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.65) !important;
    backdrop-filter: blur(40px) saturate(150%);
    border-right: 1px solid rgba(255,255,255,0.8) !important;
    box-shadow: 10px 0 30px rgba(15, 23, 42, 0.03);
}
[data-testid="stSidebar"] * { color: #475569 !important; font-family: 'Inter', sans-serif !important; }

.nexus-brand {
    font-size: 2.2rem; font-weight: 800; letter-spacing: -1px;
    background: linear-gradient(300deg, #2563eb, #8b5cf6, #3b82f6);
    background-size: 200% 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: gradient-shift 6s ease infinite; font-family: 'Space Grotesk', sans-serif;
    filter: drop-shadow(0 4px 10px rgba(37, 99, 235, 0.2));
}
@keyframes gradient-shift { 50% { background-position: 100% 50%; } }

.stRadio > div { gap: 12px; }
.stRadio label {
    color: #64748b !important; padding: 12px 20px; border-radius: 12px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer; font-weight: 600;
    border: 1px solid transparent; background: transparent;
}
.stRadio label:hover {
    background: rgba(255,255,255,0.9) !important; color: #0f172a !important;
    transform: translateX(6px); box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    border: 1px solid rgba(255,255,255,1);
}
div[role="radiogroup"] label > div:first-child { display: none; }
div[role="radiogroup"] label[data-selected="true"] {
    background: #ffffff !important; color: #2563eb !important; font-weight: 700;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.12); border-left: 4px solid #2563eb;
    border-radius: 4px 12px 12px 4px;
}

h1, h2, h3, h4, h5, h6, .stMarkdown p { color: #0f172a !important; }

.hero-header {
    font-family: 'Space Grotesk', sans-serif; font-weight: 800; letter-spacing: -1.5px;
    font-size: 2.8rem; margin-bottom: 4px; background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; filter: drop-shadow(0 4px 10px rgba(37, 99, 235, 0.15));
}

.kpi-card {
    background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(20px); border-radius: 24px; padding: 28px;
    box-shadow: 0 10px 30px -10px rgba(15, 23, 42, 0.05), inset 0 1px 0 rgba(255,255,255,1);
    display: flex; flex-direction: column; border: 1px solid rgba(255, 255, 255, 0.9);
    transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); margin-bottom: 20px; position: relative; overflow: hidden;
    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.kpi-card::before {
    content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: conic-gradient(from 0deg, transparent 0%, rgba(56, 189, 248, 0.4) 25%, transparent 50%);
    animation: spin 4s linear infinite; z-index: -1; opacity: 0; transition: opacity 0.5s ease;
}
.kpi-card:hover::before { opacity: 1; }
@keyframes spin { 100% { transform: rotate(360deg); } }
.kpi-card:hover {
    transform: translateY(-8px) scale(1.03); box-shadow: 0 30px 50px -15px rgba(37, 99, 235, 0.15), inset 0 1px 0 rgba(255,255,255,1);
    border-color: rgba(37, 99, 235, 0.2);
}
.kpi-title { font-family: 'Space Grotesk', sans-serif; font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; margin-bottom: 12px; }
.kpi-value { font-family: 'Space Grotesk', sans-serif; font-size: 3rem; color: #0f172a; font-weight: 800; letter-spacing: -1.5px; line-height: 1; background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; filter: drop-shadow(0 4px 6px rgba(37, 99, 235, 0.1)); }
.kpi-trend { font-size: 0.9rem; color: #10b981; font-weight: 700; margin-top: 16px; display: flex; align-items: center; gap: 6px; background: rgba(16, 185, 129, 0.12); padding: 6px 12px; border-radius: 20px; width: fit-content; box-shadow: inset 0 1px 0 rgba(255,255,255,0.5); }

.stButton > button {
    border-radius: 14px !important; font-weight: 700 !important; letter-spacing: 0.5px !important;
    background: linear-gradient(135deg, #0f172a, #1e293b) !important; color: white !important;
    border: 1px solid rgba(255,255,255,0.1) !important; padding: 16px 32px !important;
    box-shadow: 0 8px 16px -4px rgba(15, 23, 42, 0.3), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important; text-transform: uppercase;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1e293b, #3b82f6) !important;
    box-shadow: 0 12px 24px -6px rgba(37, 99, 235, 0.4), inset 0 1px 0 rgba(255,255,255,0.2) !important;
    transform: translateY(-3px) scale(1.02) !important;
}

.event-feed {
    font-family: 'JetBrains Mono', 'Roboto Mono', monospace; font-size: 0.85rem; line-height: 1.9; height: 450px; overflow-y: auto;
    background: rgba(255, 255, 255, 0.5); padding: 24px; border-radius: 20px; border: 1px solid rgba(226, 232, 240, 0.5);
    box-shadow: inset 0 2px 8px rgba(15, 23, 42, 0.03); color: #1e293b;
}
.event-feed::-webkit-scrollbar { width: 6px; }
.event-feed::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }

.status-dot {
    height: 8px; width: 8px; background-color: #10b981; border-radius: 50%; display: inline-block; position: relative; box-shadow: 0 0 12px rgba(16,185,129,0.6);
}
.status-dot::after {
    content: ''; position: absolute; top: -5px; left: -5px; right: -5px; bottom: -5px;
    border: 2px solid #10b981; border-radius: 50%; animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pulse { 100% { transform: scale(2.2); opacity: 0; } }
</style>
<div class="ambient-orb orb-1"></div>
<div class="ambient-orb orb-2"></div>
<div class="ambient-orb orb-3"></div>
""", unsafe_allow_html=True)

NEXUS_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#475569", family="Inter"),
    xaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False), margin=dict(t=10, b=10, l=10, r=10)
)
PALETTE = ["#1a73e8", "#ea4335", "#fbbc04", "#34a853", "#9334e6", "#12b5cb"]

if "live_feed" not in st.session_state: st.session_state.live_feed = []
if "running" not in st.session_state: st.session_state.running = False
if "msg_queue" not in st.session_state: st.session_state.msg_queue = queue.Queue()

total_battles = 0; avg_f1 = 0.0; defender_wins = 0
try:
    with sqlite3.connect("data/simulation_results.db") as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT data FROM simulation_results WHERE event_type='battle_done'").fetchall()
        total_battles = len(rows)
        if total_battles > 0:
            f1_sum = 0
            for r in rows:
                d = json.loads(r["data"])
                f1_sum += d.get("metrics", {}).get("f1_score", 0)
                if d.get("winner") == "defender": defender_wins += 1
            avg_f1 = f1_sum / total_battles
except: pass

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding-bottom: 32px;'>
        <div style='margin-bottom:12px; color:#2563eb;'>
            <svg xmlns="http://www.w3.org/2000/svg" width="54" height="54" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="display:inline-block; filter: drop-shadow(0 4px 6px rgba(37, 99, 235, 0.2));">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
        </div>
        <div class="nexus-brand">NEXUS</div>
        <div style='font-size:0.8rem; color:#64748b; font-weight:700; letter-spacing:2px; margin-top:4px;'>COMMAND CENTER</div>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.radio("NAVIGATION", ["SOC Overview", "Mission Control", "Threat Intelligence", "Analytics & Export"], label_visibility="collapsed")
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.caption("SYSTEM STATUS")
    try:
        from integrations.vector_memory import get_memory
        st.markdown("<div style='display:flex; align-items:center; gap:8px;'><span class='status-dot'></span> <span style='font-size:0.85rem; color:#5f6368; font-weight:600;'>Vector Engine</span></div>", unsafe_allow_html=True)
    except:
        st.markdown("<div style='display:flex; align-items:center; gap:8px;'><span class='status-dot' style='background:#ea4335;'></span> <span style='font-size:0.85rem; color:#5f6368; font-weight:600;'>Vector Engine</span></div>", unsafe_allow_html=True)
    try:
        from integrations.siem_forwarder import get_forwarder
        st.markdown("<div style='display:flex; align-items:center; gap:8px;'><span class='status-dot'></span> <span style='font-size:0.85rem; color:#5f6368; font-weight:600;'>SIEM Forwarder</span></div>", unsafe_allow_html=True)
    except: pass

def kpi_card(title, value, trend, color, icon_svg):
    return f"""
    <div class="kpi-card" style="border-top-color: {color};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <div class="kpi-title">{title}</div>
            <div style="color: {color}; opacity: 0.8; width: 20px; height: 20px;">{icon_svg}</div>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-trend">{trend}</div>
    </div>
    """

ICON_F1 = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>'
ICON_SHIELD = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>'
ICON_DB = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>'
ICON_WARN = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>'

if page == "SOC Overview":
    st.markdown("<div class='hero-header'>Global SOC Overview</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; margin-bottom:32px; font-size:1.15rem; font-weight:500;'>Real-time unified threat simulation metrics</p>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    win_rate = (defender_wins/total_battles*100) if total_battles else 0
    c1.markdown(kpi_card("Mean F1 Score", f"{avg_f1:.3f}", "+0.02 vs last week", "#2563eb", ICON_F1), unsafe_allow_html=True)
    c2.markdown(kpi_card("Defend Win Rate", f"{win_rate:.1f}%", f"{defender_wins} total blocks", "#10b981", ICON_SHIELD), unsafe_allow_html=True)
    c3.markdown(kpi_card("Battles Logged", str(total_battles), "Simulation database", "#f59e0b", ICON_DB), unsafe_allow_html=True)
    c4.markdown(kpi_card("Active Threats", "6", "Persistent APT Actors", "#ef4444", ICON_WARN), unsafe_allow_html=True)
    
    r1c1, r1c2 = st.columns([6, 4])
    with r1c1:
        with st.container(border=True):
            st.markdown("<h3 style='color:#0f172a; font-family:\"Space Grotesk\", sans-serif; margin-bottom:16px;'>Top Alerts by Severity</h3>", unsafe_allow_html=True)
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
            
    with r1c2:
        with st.container(border=True):
            st.markdown("<h3 style='color:#0f172a; font-family:\"Space Grotesk\", sans-serif; margin-bottom:16px;'>Live Threat Graph</h3>", unsafe_allow_html=True)
            try:
                sys.path.insert(0, os.path.dirname(__file__))
                from integrations.network_graph import generate_attack_graph
                fig2 = generate_attack_graph(n_nodes=20)
                st.plotly_chart(fig2, use_container_width=True, theme=None)
            except Exception as e:
                st.warning(f"Graph engine error: {e}")

elif page == "Mission Control":
    st.markdown("<h2 style='color:#0f172a; font-family:\"Space Grotesk\", sans-serif; font-weight:800; letter-spacing:-1px; margin-bottom:24px;'>Launch Campaign</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 7])
    with c1:
        with st.container(border=True):
            provider = st.selectbox("AI Brain", ["Mock (offline)", "Ollama (local)"])
            turns = st.slider("Campaign Turns", 1, 10, 3)
            st.markdown("---")
            hosts = st.slider("Target Hosts", 2, 20, 4)
            users = st.slider("Simulated Users", 5, 50, 8)
            if st.button("INITIATE WARGAMES", use_container_width=True):
                st.session_state.running = True
                st.session_state.live_feed.append(f"Initializing campaign with {turns} turns...")
                def run_sim():
                    import subprocess
                    prov = "mock" if "Mock" in provider else "ollama"
                    cmd = [sys.executable, "scripts/run_simulation.py", "--provider", prov, "--turns", str(turns)]
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
                    for line in iter(process.stdout.readline, ""):
                        if line.strip(): st.session_state.msg_queue.put(line.strip())
                    process.stdout.close()
                    st.session_state.msg_queue.put("__DONE__")
                threading.Thread(target=run_sim, daemon=True).start()
                st.rerun()
            
    with c2:
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
            
        feed_html = "<div class='event-feed'><div style='color:#0f172a;'>"
        if st.session_state.live_feed:
            for line in st.session_state.live_feed:
                if "Battle" in line or "WINNER" in line: feed_html += f"<div style='color:#f59e0b; font-weight:700;'>{line}</div>"
                elif "ATTACK" in line: feed_html += f"<div style='color:#ef4444;'>{line}</div>"
                elif "DETECT" in line or "SIGMA" in line: feed_html += f"<div style='color:#10b981;'>{line}</div>"
                else: feed_html += f"<div>{line}</div>"
        else: feed_html += "System standing by. No active campaigns."
        feed_html += "</div></div>"
        st.markdown(feed_html, unsafe_allow_html=True)

elif page == "Threat Intelligence":
    st.markdown("<h2 style='color:#0f172a; font-family:\"Space Grotesk\", sans-serif; font-weight:800; letter-spacing:-1px; margin-bottom:24px;'>Live TAXII Intel</h2>", unsafe_allow_html=True)
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
                for mw in profile.get('tools', []): st.markdown(f"- `{mw}`")
    except Exception as e:
        st.error(f"Failed to load Threat Intel: {e}")

elif page == "Analytics & Export":
    st.markdown("<h2 style='color:#0f172a; font-family:\"Space Grotesk\", sans-serif; font-weight:800; letter-spacing:-1px; margin-bottom:24px;'>Reporting & SIEM Integration</h2>", unsafe_allow_html=True)
    
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
)
