import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Let's replace the Executed Attack Vectors rendering loop in the results page!
old_loop = """                        for idx, log in enumerate(logs):
                            attacker = log.get('attacker', 'Unknown')
                            tech = log.get('attack_technique', 'N/A')
                            target = log.get('host', 'N/A')
                            detected = log.get('detected', False)
                            status = "<span style='color:#10b981; font-weight:700;'>BLOCKED</span>" if detected else "<span style='color:#ef4444; font-weight:700;'>BYPASSED</span>"
                            
                            st.markdown(f\"\"\"
                            <div style='background:#f8fafc; border:1px solid #e2e8f0; padding:12px 16px; border-radius:8px; margin-bottom:8px;'>
                                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>
                                    <strong style='color:#0f172a;'>{attacker} executed {tech}</strong>
                                    <div>{status}</div>
                                </div>
                                <div style='font-family:monospace; color:#64748b; font-size:0.85rem;'>Target: {target} | Src: {log.get('ip_src')} → Dst: {log.get('ip_dst')}</div>
                            </div>
                            \"\"\", unsafe_allow_html=True)
                            if idx >= 9:
                                st.markdown("*... showing first 10 attacks*")
                                break"""

new_loop = """                        for idx, log in enumerate(logs):
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
                                    <b>Vector:</b> Src: {ip_src} &rarr; Dst: {ip_dst} | <b>Target:</b> {target}
                                </div>
                                <div style='font-size:0.9rem; background:#f1f5f9; padding:8px; border-radius:4px;'>
                                    {mitigation_text}
                                </div>
                            </div>
                            \"\"\", unsafe_allow_html=True)
                            if idx >= 19:
                                st.markdown("*... showing first 20 attacks*")
                                break"""

text = text.replace(old_loop, new_loop)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
