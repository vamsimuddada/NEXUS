import codecs
import re

with codecs.open('scratch/write_dash.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Update imports
if "import glob" not in text:
    text = text.replace("import sys, os, json, time, threading, queue, sqlite3", 
                        "import sys, os, json, time, threading, queue, sqlite3, glob, codecs")

# 2. Update navigation
text = text.replace('["SOC Overview", "Mission Control", "Threat Intelligence", "Analytics & Export"]', 
                    '["SOC Overview", "Mission Control", "Test Results", "Analytics & Export"]')

# 3. Update toggle logic
text = text.replace(
'''        if st.button("▶  START CAMPAIGN", type="primary", use_container_width=True):
            st.session_state.running = True
            st.session_state.start_time = time.time()''',
'''        if st.button("▶  START CAMPAIGN", type="primary", use_container_width=True):
            st.session_state.running = True
            st.session_state.start_time = time.time()
            st.session_state.test_completed = False'''
)

# 4. Replace Threat Intel with Test Results

threat_intel_code = """elif page == "Threat Intelligence":
    st.markdown("<h2 style='color:#0f172a; font-family:\\"Space Grotesk\\", sans-serif; font-weight:800; letter-spacing:-1px; margin-bottom:24px;'>Live TAXII Intel</h2>", unsafe_allow_html=True)
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
        st.error(f"Failed to load Threat Intel: {e}")"""

test_results_code = """elif page == "Test Results":
    st.markdown('<div class="section-header">Operation After-Action Report</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:\\\'Space Grotesk\\\', sans-serif; color:#475569; margin-bottom:24px; font-weight:500;">Detailed breakdown of the most recent campaign, including executed attacks, blue team mitigations, and dynamic rule generation.</p>', unsafe_allow_html=True)
    
    report_files = sorted(Path("data/reports").glob("campaign_*.json"), reverse=True)
    if not report_files:
        st.warning("No campaign reports found. Run a simulation first.")
    else:
        latest_report = report_files[0]
        try:
            with open(latest_report, "r") as f:
                report_data = json.load(f)
            
            winner = report_data.get('winner', 'unknown').upper()
            win_color = "#10b981" if winner == "DEFENDER" else "#ef4444"
            metrics = report_data.get('metrics', {})
            logs = report_data.get('attacker_logs', [])
            
            def render_attack_card(log):
                attacker = log.get('attacker', 'Unknown')
                tech = log.get('attack_technique', 'N/A')
                target = log.get('host', 'N/A')
                detected = log.get('detected', False)
                ip_src = log.get('ip_src', '0.0.0.0')
                ip_dst = log.get('ip_dst', '0.0.0.0')
                
                if not detected:
                    status = "<span style='color:#ef4444; font-weight:800; font-size:0.8rem; letter-spacing:1px;'>BYPASSED</span>"
                    mitigation_text = "<span style='color:#ef4444;'>No mitigation applied. Rule evasion successful.</span>"
                else:
                    status = "<span style='color:#10b981; font-weight:800; font-size:0.8rem; letter-spacing:1px;'>BLOCKED</span>"
                    if tech == 'T1021': mitigation_text = f"<span style='color:#10b981;'><b>Firewall Rule Added:</b> <code style='color:#10b981; background:rgba(16,185,129,0.1); border:none;'>DENY TCP {ip_src} {ip_dst} EQ 3389/445</code> (Lateral Movement Blocked)</span>"
                    elif tech == 'T1071': mitigation_text = f"<span style='color:#10b981;'><b>Network Sinkhole:</b> Null-routed C2 beacon IP <code style='color:#10b981; background:rgba(16,185,129,0.1); border:none;'>{ip_dst}</code> at perimeter firewall</span>"
                    elif tech == 'T1486': mitigation_text = f"<span style='color:#10b981;'><b>EDR Action:</b> Quarantined host <code>{target}</code> and terminated encryption process</span>"
                    elif tech == 'T1003': mitigation_text = f"<span style='color:#10b981;'><b>EDR Action:</b> Blocked LSASS memory dump and locked user <code>{log.get('user', 'admin')}</code></span>"
                    elif tech == 'T1083': mitigation_text = f"<span style='color:#10b981;'><b>HIPS Rule:</b> Blocked anomalous automated directory discovery commands on <code>{target}</code></span>"
                    else: mitigation_text = f"<span style='color:#10b981;'><b>SIGMA Rule Triggered:</b> Dynamic payload signature blocked and IP <code>{ip_src}</code> blacklisted</span>"
                
                st.markdown(f\"\"\"
                <div style='background:#ffffff; border:1px solid #e2e8f0; padding:16px 20px; border-radius:12px; margin-bottom:16px; box-shadow: 0 4px 15px rgba(15,23,42,0.02);'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom: 1px solid #f1f5f9; padding-bottom: 12px;'>
                        <strong style='color:#0f172a; font-size:1.05rem; font-family:"Space Grotesk", sans-serif;'>{attacker} executed {tech}</strong>
                        <div>{status}</div>
                    </div>
                    <div style='font-family:monospace; color:#64748b; font-size:0.85rem; margin-bottom:12px; line-height:1.6;'>
                        <b>Network Route:</b> Src: {ip_src} &rarr; Dst: {ip_dst} | <b>Target Host:</b> {target}<br>
                        <b>Compromised Identity:</b> {log.get('user', 'SYSTEM')} ({log.get('department', 'IT')} Dept) | <b>Admin Privileges:</b> {str(log.get('is_admin', False)).upper()}<br>
                        <b>Telemetry Payload:</b> [Event ID {log.get('event_id', '???')}] {log.get('message', 'Unknown action')}
                    </div>
                    <div style='font-size:0.85rem; background:#f8fafc; padding:10px 14px; border-radius:6px; border-left: 3px solid #10b981;'>
                        {mitigation_text}
                    </div>
                </div>
                \"\"\", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            
            with c1:
                with st.container(border=True):
                    st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Campaign overview</h3>", unsafe_allow_html=True)
                    st.write(f"**Battle ID:** `{report_data.get('battle_id', 'N/A')}`")
                    st.write(f"**Timestamp:** `{report_data.get('timestamp', 'N/A')}`")
                    st.markdown(f"**Outcome:** <span style='color:{win_color}; font-weight:800;'>{winner} VICTORY</span>", unsafe_allow_html=True)
            
            with c2:
                with st.container(border=True):
                    st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Blue Team Mitigations</h3>", unsafe_allow_html=True)
                    st.write(f"**SIGMA Rules Deployed:** `{metrics.get('sigma_rules', 0)}` dynamic rules written")
                    st.write(f"**Final Accuracy (F1):** `{(metrics.get('f1_score', 0)*100):.1f}%`")
                    st.write(f"**Precision:** `{(metrics.get('precision', 0)*100):.1f}%`")
                    st.write(f"**Recall:** `{(metrics.get('recall', 0)*100):.1f}%`")
                    st.markdown("<p style='color:#64748b; font-size:0.9rem; margin-top:16px;'>The autonomous Blue Team agent successfully analyzed the network traffic in real-time, identifying malicious signatures and deploying new SIGMA rules to block the execution pathways.</p>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Executed Attack Vectors</h3>", unsafe_allow_html=True)
                if not logs:
                    st.info("No attacks executed during this campaign.")
                else:
                    for log in logs[:24]:
                        render_attack_card(log)
                    if len(logs) > 24:
                        st.markdown("<p style='color:#64748b; font-size:0.9rem;'><i>... showing first 24 attacks</i></p>", unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"Error parsing report: {e}")"""

if threat_intel_code in text:
    text = text.replace(threat_intel_code, test_results_code)
else:
    print("WARNING: Threat intel code block not found exactly!")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)

print("RESTORED DASHBOARD WITH STACKED LAYOUT!")
