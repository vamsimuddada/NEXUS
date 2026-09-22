import codecs

# 1. Read CSS from current_dash.py
with codecs.open('scratch/current_dash.py', 'r', encoding='utf-16') as f:
    lines = f.readlines()

css_lines = []
in_css = False
for line in lines:
    if '<style>' in line:
        in_css = True
    if in_css:
        css_lines.append(line)
    if '</style>' in line:
        break

css_block = "".join(css_lines)

# 2. Re-create the dashboard logic
final_code = f'''"""
NEXUS War Room Dashboard - Professional Edition
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

st.set_page_config(page_title="NEXUS Command", page_icon="globe", layout="wide", initial_sidebar_state="collapsed")

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL THEME
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
{css_block}
<div class="ambient-orb orb-1"></div>
<div class="ambient-orb orb-2"></div>
<div class="ambient-orb orb-3"></div>
""", unsafe_allow_html=True)

NEXUS_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#475569", family="Inter"),
    xaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
    margin=dict(t=30, b=30, l=10, r=10),
)
PALETTE = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#10b981", "#34d399", "#f59e0b", "#ef4444"]

ICON_SWORDS = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="14.5 17.5 3 6 3 3 6 3 17.5 14.5"></polyline><line x1="13" y1="19" x2="19" y2="13"></line><line x1="16" y1="16" x2="20" y2="20"></line><line x1="19" y1="21" x2="21" y2="19"></line><polyline points="14.5 6.5 18 3 21 3 21 6 17.5 9.5"></polyline><line x1="5" y1="14" x2="9" y2="18"></line><line x1="7" y1="17" x2="4" y2="20"></line><line x1="3" y1="19" x2="5" y2="21"></line></svg>'
ICON_SHIELD = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
ICON_BRAIN = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"></path></svg>'
ICON_F1 = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>'
ICON_SHIELD2 = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>'
ICON_DB = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>'
ICON_WARN = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>'

# ══════════════════════════════════════════════════════════════════════════════
#  ABOUT PROJECT PAGE (ROUTING)
# ══════════════════════════════════════════════════════════════════════════════
if st.query_params.get("page") == "about":
    st.markdown("<div style='margin-bottom:24px;'>", unsafe_allow_html=True)
    if st.button("← Back to Command Center"):
        st.query_params.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='font-family:\"Space Grotesk\", sans-serif; font-size:3rem; font-weight:800; color:#0f172a; margin-bottom:16px;'>About NEXUS</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.15rem; color:#475569; line-height:1.8; margin-bottom:40px;'><b>Neural Exploitation & eXplainable Unified Security (NEXUS)</b> is an autonomous, self-evolving cyber warfare simulation platform. It acts as an intelligent proving ground where autonomous Red Team agents and Blue Team defense networks wage continuous, self-improving campaigns against each other.</p>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='font-family:\"Space Grotesk\", sans-serif; font-weight:800; color:#0f172a; margin-bottom:24px;'>System Architecture</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown(f"<div style='display:flex; align-items:center; gap:12px; margin-bottom:12px;'><div style='color:#ef4444;'>{{ICON_SWORDS}}</div><div style='font-family:\"Space Grotesk\", sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a;'>Red Team (Autonomous Attackers)</div></div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#475569; line-height:1.6;'>Powered by intelligent agents, the Red Team dynamically scans the network, selects targets, and launches exploits based on real-time threat intelligence (TAXII/STIX). They possess a <b>Semantic Vector Memory</b> that allows them to remember which attacks worked and adapt to the Blue Team's defenses.</p>", unsafe_allow_html=True)
        
    with st.container(border=True):
        st.markdown(f"<div style='display:flex; align-items:center; gap:12px; margin-bottom:12px;'><div style='color:#10b981;'>{{ICON_SHIELD}}</div><div style='font-family:\"Space Grotesk\", sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a;'>Blue Team (SIEM & Defense)</div></div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#475569; line-height:1.6;'>The Blue Team monitors a simulated network (represented by the Live Threat Graph) and generates alerts based on SIEM rules. When attacks are detected, they block the originating IPs and patch vulnerabilities, forcing the Red Team to evolve their tactics.</p>", unsafe_allow_html=True)
        
    with st.container(border=True):
        st.markdown(f"<div style='display:flex; align-items:center; gap:12px; margin-bottom:12px;'><div style='color:#8b5cf6;'>{{ICON_BRAIN}}</div><div style='font-family:\"Space Grotesk\", sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a;'>The AI Brain (Provider)</div></div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#475569; line-height:1.6;'>The core reasoning engine of NEXUS can be toggled between an offline <b>Mock Engine</b> (for high-speed, deterministic simulations) or a live <b>Ollama Model</b> (for true, localized AI reasoning and decision making).</p>", unsafe_allow_html=True)
        
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if "msg_queue" not in st.session_state: st.session_state.msg_queue = queue.Queue()
if "live_feed" not in st.session_state: st.session_state.live_feed = []
if "running" not in st.session_state: st.session_state.running = False

st.markdown("""
<div style='display: flex; align-items: center; gap: 20px; margin-bottom: 24px; margin-top: -30px;'>
    <div style='width:60px; height:60px; border-radius:50%; background:linear-gradient(135deg, #e0e7ff, #ffffff); display:flex; align-items:center; justify-content:center; box-shadow: 0 10px 25px rgba(37, 99, 235, 0.15); border: 1px solid rgba(255,255,255,1);'>
        <svg width='32' height='32' viewBox='0 0 24 24' fill='none' stroke='#3b82f6' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>
            <path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'></path>
        </svg>
    </div>
    <div style="display: flex; align-items: baseline; gap: 12px;">
        <div style="font-family:'Space Grotesk', sans-serif; font-size:3.2rem; font-weight:800; color:#0f172a; line-height:1; letter-spacing:-2px;">NEXUS</div>
        <div style="font-family:'Inter', sans-serif; font-size:0.95rem; font-weight:600; color:#64748b; letter-spacing:0px;">- Neural Exploitation & eXplainable Unified Security</div>
        <a href="?page=about" target="_self" style="color:#3b82f6; margin-left:4px; margin-top:4px; opacity:0.6; transition:all 0.2s;" onmouseover="this.style.opacity=1; this.style.transform='scale(1.1)';" onmouseout="this.style.opacity=0.6; this.style.transform='scale(1)';" title="About Project">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# TABS
tab1, tab2, tab3 = st.tabs(["SOC Overview", "Threat Intelligence", "Analytics & Export"])

def kpi_card(title, value, trend, color, icon_svg):
    return f"""
    <div class="kpi-card" style="border-top-color: {color};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <div class="kpi-title">{title}</div>
            <div style="color: {color}; opacity: 0.8; width: 24px; height: 24px;">{icon_svg}</div>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-trend" style="font-size: 0.85rem; font-weight: 700; color: #10b981; margin-top: 12px; background: rgba(16, 185, 129, 0.15); padding: 4px 12px; border-radius: 20px; display: inline-block;">{trend}</div>
    </div>
    """

with tab1:
    st.markdown("<div class='hero-header' style='font-size: 2.8rem; letter-spacing: -1px; margin-top: 16px;'>Security Command Center</div>", unsafe_allow_html=True)
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
    c2.markdown(kpi_card("Defend Win Rate", f"{win_rate:.1f}%", f"{defender_wins} total blocks", "#10b981", ICON_SHIELD2), unsafe_allow_html=True)
    c3.markdown(kpi_card("Battles Logged", str(total_battles), "Simulation database", "#f59e0b", ICON_DB), unsafe_allow_html=True)
    c4.markdown(kpi_card("Active Threats", "6", "Persistent APT Actors", "#ef4444", ICON_WARN), unsafe_allow_html=True)
    
    st.markdown("<h3 style='color:#0f172a; font-family:\"Space Grotesk\", sans-serif; font-weight:800; letter-spacing:-1px; margin-top:32px; margin-bottom:16px;'>Active Operation</h3>", unsafe_allow_html=True)
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
            
        feed_html = "<div class='terminal-feed' style='background: white; border: 1px solid #e2e8f0; border-radius: 24px; padding: 24px; font-family: monospace; font-size: 0.85rem; line-height: 1.8; max-height: 400px; overflow-y: auto; color: #334155; height: 420px;'><div style='color:#0f172a;'>"
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
        st.markdown("<h3 style='color:#0f172a; font-family:\"Space Grotesk\", sans-serif; margin-bottom:16px; font-weight:700;'>Top Alerts by Severity</h3>", unsafe_allow_html=True)
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

with tab2:
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

with tab3:
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
'''

with codecs.open("scripts/dashboard.py", "w", encoding="utf-8") as f:
    f.write(final_code)
