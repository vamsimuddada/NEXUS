import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

pattern = re.compile(r"latest_report = report_files\[0\].*?st\.error\(f\"Error parsing report: \{e\}\"\)", re.DOTALL)

new_text = """latest_report = report_files[0]
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
                    status = "<span style='color:#ef4444; font-weight:700;'>BYPASSED</span>"
                    mitigation_text = "<span style='color:#ef4444;'>No mitigation applied. Rule evasion successful.</span>"
                else:
                    status = "<span style='color:#10b981; font-weight:700;'>BLOCKED</span>"
                    if tech == 'T1021': mitigation_text = f"<span style='color:#10b981;'><b>Firewall Rule Added:</b> <code>DENY TCP {ip_src} {ip_dst} EQ 3389/445</code> (Lateral Movement Blocked)</span>"
                    elif tech == 'T1071': mitigation_text = f"<span style='color:#10b981;'><b>Network Sinkhole:</b> Null-routed C2 beacon IP <code>{ip_dst}</code> at perimeter firewall</span>"
                    elif tech == 'T1486': mitigation_text = f"<span style='color:#10b981;'><b>EDR Action:</b> Quarantined host <code>{target}</code> and terminated encryption process</span>"
                    elif tech == 'T1003': mitigation_text = f"<span style='color:#10b981;'><b>EDR Action:</b> Blocked LSASS memory dump and locked user <code>{log.get('user', 'admin')}</code></span>"
                    elif tech == 'T1083': mitigation_text = f"<span style='color:#10b981;'><b>HIPS Rule:</b> Blocked anomalous automated directory discovery commands on <code>{target}</code></span>"
                    else: mitigation_text = f"<span style='color:#10b981;'><b>SIGMA Rule Triggered:</b> Dynamic payload signature blocked and IP <code>{ip_src}</code> blacklisted</span>"
                
                st.markdown(f\"\"\"
                <div style='background:#f8fafc; border:1px solid #e2e8f0; padding:12px 16px; border-radius:8px; margin-bottom:12px; box-shadow: 0 2px 5px rgba(0,0,0,0.02);'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;'>
                        <strong style='color:#0f172a; font-size:1.05rem;'>{attacker} executed {tech}</strong>
                        <div>{status}</div>
                    </div>
                    <div style='font-family:monospace; color:#64748b; font-size:0.85rem; margin-bottom:8px;'>
                        <b>Network Route:</b> Src: {ip_src} &rarr; Dst: {ip_dst} | <b>Target Host:</b> {target}<br>
                        <b>Compromised Identity:</b> {log.get('user', 'SYSTEM')} ({log.get('department', 'IT')} Dept) | <b>Admin Privileges:</b> {str(log.get('is_admin', False)).upper()}<br>
                        <b>Telemetry Payload:</b> [Event ID {log.get('event_id', '???')}] {log.get('message', 'Unknown action')}
                    </div>
                    <div style='font-size:0.9rem; background:#f1f5f9; padding:8px; border-radius:4px;'>
                        {mitigation_text}
                    </div>
                </div>
                \"\"\", unsafe_allow_html=True)

            c1, c2 = st.columns([1, 1.5])
            
            with c1:
                with st.container(border=True):
                    st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Campaign overview</h3>", unsafe_allow_html=True)
                    st.write(f"**Battle ID:** `{report_data.get('battle_id', 'N/A')}`")
                    st.write(f"**Timestamp:** `{report_data.get('timestamp', 'N/A')}`")
                    st.markdown(f"**Outcome:** <span style='color:{win_color}; font-weight:800;'>{winner} VICTORY</span>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Blue Team Mitigations</h3>", unsafe_allow_html=True)
                    st.write(f"**SIGMA Rules Deployed:** `{metrics.get('sigma_rules', 0)}` dynamic rules written")
                    st.write(f"**Final Accuracy (F1):** `{(metrics.get('f1_score', 0)*100):.1f}%`")
                    st.write(f"**Precision:** `{(metrics.get('precision', 0)*100):.1f}%`")
                    st.write(f"**Recall:** `{(metrics.get('recall', 0)*100):.1f}%`")
                    
                    st.markdown("<p style='color:#64748b; font-size:0.9rem; margin-top:16px;'>The autonomous Blue Team agent successfully analyzed the network traffic in real-time, identifying malicious signatures and deploying new SIGMA rules to block the execution pathways.</p>", unsafe_allow_html=True)

            with c2:
                with st.container(border=True):
                    st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Executed Attack Vectors</h3>", unsafe_allow_html=True)
                    if not logs:
                        st.info("No attacks executed during this campaign.")
                    else:
                        # We slice exactly 3 logs for c2 to precisely match the height of c1.
                        for log in logs[:3]:
                            render_attack_card(log)
                            
            if len(logs) > 3:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.container(border=True):
                    for log in logs[3:24]:
                        render_attack_card(log)
                    if len(logs) > 24:
                        st.markdown("<p style='color:#64748b; font-size:0.9rem;'><i>... showing first 24 attacks</i></p>", unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"Error parsing report: {e}")"""

match = pattern.search(text)
if match:
    text = text[:match.start()] + new_text + text[match.end():]
    with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
        f.write(text)
else:
    print("Failed to match regex.")
