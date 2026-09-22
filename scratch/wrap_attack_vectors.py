import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Remove the Adversary Intelligence block!
adversary_start = "                with st.container(border=True):\n                    st.markdown(\"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:8px; font-weight:800;'>Adversary Intelligence</h3>\", unsafe_allow_html=True)"
adversary_end = "                        st.markdown(table_html, unsafe_allow_html=True)"

# Find the exact indices to slice it out
start_idx = text.find(adversary_start)
end_idx = text.find(adversary_end) + len(adversary_end)

if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + text[end_idx:]


# 2. Refactor the Executed Attack Vectors to split across c2 and full-width!
old_c2_block = """            with c2:
                with st.container(border=True):
                    st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Executed Attack Vectors</h3>", unsafe_allow_html=True)
                    logs = report_data.get('attacker_logs', [])
                    if not logs:
                        st.info("No attacks executed during this campaign.")
                    else:
                        for idx, log in enumerate(logs):
                            attacker = log.get('attacker', 'Unknown')
                            tech = log.get('attack_technique', 'N/A')
                            target = log.get('host', 'N/A')
                            detected = log.get('detected', False)
                            
                            ip_src = log.get('ip_src', '0.0.0.0')
                            ip_dst = log.get('ip_dst', '0.0.0.0')
                            
                            # Dynamically generate mitigation explanations based on the MITRE technique
                            if not detected:
                                status = "<span style='color:#ef4444; font-weight:700;'>BYPASSED</span>"
                                mitigation_text = "<span style='color:#ef4444;'>No mitigation applied. Rule evasion successful.</span>"
                            else:
                                status = "<span style='color:#10b981; font-weight:700;'>BLOCKED</span>"
                                if tech == 'T1021':
                                    mitigation_text = f"<span style='color:#10b981;'><b>Firewall Rule Added:</b> <code>DENY TCP {ip_src} {ip_dst} EQ 3389/445</code> (Lateral Movement Blocked)</span>"
                                elif tech == 'T1071':
                                    mitigation_text = f"<span style='color:#10b981;'><b>Network Sinkhole:</b> Null-routed C2 beacon IP <code>{ip_dst}</code> at perimeter firewall</span>"
                                elif tech == 'T1486':
                                    mitigation_text = f"<span style='color:#10b981;'><b>EDR Action:</b> Quarantined host <code>{target}</code> and terminated encryption process</span>"
                                elif tech == 'T1003':
                                    mitigation_text = f"<span style='color:#10b981;'><b>EDR Action:</b> Blocked LSASS memory dump and locked user <code>{log.get('user', 'admin')}</code></span>"
                                elif tech == 'T1083':
                                    mitigation_text = f"<span style='color:#10b981;'><b>HIPS Rule:</b> Blocked anomalous automated directory discovery commands on <code>{target}</code></span>"
                                else:
                                    mitigation_text = f"<span style='color:#10b981;'><b>SIGMA Rule Triggered:</b> Dynamic payload signature blocked and IP <code>{ip_src}</code> blacklisted</span>"
                            
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
                            if idx >= 19:
                                st.markdown("*... showing first 20 attacks*")
                                break"""


new_c2_block = """
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

            logs = report_data.get('attacker_logs', [])
            
            with c2:
                with st.container(border=True):
                    st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Executed Attack Vectors</h3>", unsafe_allow_html=True)
                    if not logs:
                        st.info("No attacks executed during this campaign.")
                    else:
                        for log in logs[:4]:
                            render_attack_card(log)

            if len(logs) > 4:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.container(border=True):
                    for idx, log in enumerate(logs[4:24]):
                        render_attack_card(log)
                    if len(logs) > 24:
                        st.markdown("*... showing first 24 attacks*")"""

text = text.replace(old_c2_block, new_c2_block)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
