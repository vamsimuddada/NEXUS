import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

old_block_start = "          latest_report = report_files[0]\n          try:"
old_block_end = "        except Exception as e:\n              st.error(f\"Error parsing report: {e}\")"

# Wait, let me find the exact text using python
idx1 = text.find("          latest_report = report_files[0]\n          try:\n              with open(latest_report, \"r\") as f:")
idx2 = text.find("        except Exception as e:\n            st.error(f\"Error parsing report: {e}\")") + len("        except Exception as e:\n            st.error(f\"Error parsing report: {e}\")")

if idx1 == -1 or idx2 == -1:
    # Alternative search
    idx1 = text.find("latest_report = report_files[0]")
    idx2 = text.find("st.error(f\"Error parsing report: {e}\")") + len("st.error(f\"Error parsing report: {e}\")")

if idx1 != -1 and idx2 != -1:
    old_text = text[idx1:idx2]
    
    new_text = """latest_report = report_files[0]
        try:
            with open(latest_report, "r") as f:
                report_data = json.load(f)
            
            winner = report_data.get('winner', 'unknown').upper()
            win_color = "#10b981" if winner == "DEFENDER" else "#ef4444"
            metrics = report_data.get('metrics', {})
            
            html = "<div>"
            
            # Left floated column (Campaign Overview & Mitigations)
            html += f\"\"\"
            <div style="float: left; width: 38%; margin-right: 2%; margin-bottom: 24px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 24px; box-shadow: 0 4px 15px rgba(15,23,42,0.02);">
                <h3 style="color:#0f172a; font-family:'Space Grotesk', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800; letter-spacing:-0.5px;">Campaign overview</h3>
                <p style="margin:6px 0; font-size:0.95rem; color:#475569;"><b>Battle ID:</b> <code style="color:#0f172a; background:#f1f5f9; padding:2px 6px; border-radius:4px;">{report_data.get('battle_id', 'N/A')}</code></p>
                <p style="margin:6px 0; font-size:0.95rem; color:#475569;"><b>Timestamp:</b> <code style="color:#0f172a; background:#f1f5f9; padding:2px 6px; border-radius:4px;">{report_data.get('timestamp', 'N/A')}</code></p>
                <p style="margin:6px 0; font-size:0.95rem; color:#475569;"><b>Outcome:</b> <span style="color:{win_color}; font-weight:800; letter-spacing:0.5px;">{winner} VICTORY</span></p>
                
                <hr style="border:0; border-top:1px solid #e2e8f0; margin:24px 0;">
                
                <h3 style="color:#0f172a; font-family:'Space Grotesk', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800; letter-spacing:-0.5px;">Blue Team Mitigations</h3>
                <p style="margin:6px 0; font-size:0.95rem; color:#475569;"><b>SIGMA Rules Deployed:</b> <code style="color:#3b82f6; background:rgba(59,130,246,0.1); padding:2px 6px; border-radius:4px;">{metrics.get('sigma_rules', 0)}</code></p>
                <p style="margin:6px 0; font-size:0.95rem; color:#475569;"><b>Final Accuracy (F1):</b> <code style="color:#10b981; background:rgba(16,185,129,0.1); padding:2px 6px; border-radius:4px;">{(metrics.get('f1_score', 0)*100):.1f}%</code></p>
                <p style="margin:6px 0; font-size:0.95rem; color:#475569;"><b>Precision:</b> <code style="color:#10b981; background:rgba(16,185,129,0.1); padding:2px 6px; border-radius:4px;">{(metrics.get('precision', 0)*100):.1f}%</code></p>
                <p style="margin:6px 0; font-size:0.95rem; color:#475569;"><b>Recall:</b> <code style="color:#10b981; background:rgba(16,185,129,0.1); padding:2px 6px; border-radius:4px;">{(metrics.get('recall', 0)*100):.1f}%</code></p>
                
                <p style="color:#64748b; font-size:0.85rem; margin-top:24px; line-height:1.6;">The autonomous Blue Team agent successfully analyzed the network traffic in real-time, identifying malicious signatures and deploying new SIGMA rules to block the execution pathways.</p>
            </div>
            \"\"\"
            
            # Right/Flowing content (Attack Vectors)
            html += f\"\"\"<h3 style="color:#0f172a; font-family:'Space Grotesk', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800; letter-spacing:-0.5px;">Executed Attack Vectors</h3>\"\"\"
            
            logs = report_data.get('attacker_logs', [])
            if not logs:
                html += "<p style='color:#64748b;'>No attacks executed during this campaign.</p>"
            else:
                for idx, log in enumerate(logs[:24]):
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
                    
                    html += f\"\"\"
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
                    \"\"\"
            
            if len(logs) > 24:
                html += "<p style='color:#64748b; font-size:0.9rem;'><i>... showing first 24 attacks</i></p>"
                
            html += "<div style='clear: both;'></div></div>"
            st.markdown(html, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error parsing report: {e}")"""
    
    text = text.replace(old_text, new_text)
    
    with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
        f.write(text)
else:
    print("Could not find the block to replace.")
