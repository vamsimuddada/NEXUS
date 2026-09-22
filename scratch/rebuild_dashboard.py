import re
import codecs

# 1. Read the original dashboard
with codecs.open('scratch/original.txt', 'r', 'utf-8') as f:
    text = f.read()
    
# Extract the code block from the prompt
match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
if match:
    original_code = match.group(1)
else:
    original_code = text

# 2. We need to implement the Stacked Layout for the Results page!
# In original_code, find the Results block:

pattern = re.compile(r"html \+= f\"\"\"\s*<div style=\"float: left.*?except Exception as e:\s*st\.error\(f\"Error parsing report: \{e\}\"\)", re.DOTALL)

new_results_block = """
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
                      if len(logs) > 24:
                          st.markdown("<p style='color:#64748b; font-size:0.9rem;'><i>... showing first 24 attacks</i></p>", unsafe_allow_html=True)
          except Exception as e:
              st.error(f"Error parsing report: {e}")
"""

# Let's fix the empty space issue right inside this new block!
# Wrap c1 and c2 inside ONE single bordered container!
new_results_block_fixed = """
              with st.container(border=True):
                  c1, c2 = st.columns(2)
                  
                  with c1:
                      st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Campaign overview</h3>", unsafe_allow_html=True)
                      st.write(f"**Battle ID:** `{report_data.get('battle_id', 'N/A')}`")
                      st.write(f"**Timestamp:** `{report_data.get('timestamp', 'N/A')}`")
                      st.markdown(f"**Outcome:** <span style='color:{win_color}; font-weight:800;'>{winner} VICTORY</span>", unsafe_allow_html=True)
                  
                  with c2:
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
                      if len(logs) > 24:
                          st.markdown("<p style='color:#64748b; font-size:0.9rem;'><i>... showing first 24 attacks</i></p>", unsafe_allow_html=True)
          except Exception as e:
              st.error(f"Error parsing report: {e}")
"""

final_code = pattern.sub(new_results_block_fixed, original_code)

# We also need to fix the glob issue that I fixed earlier (adding `import glob` at the top of the file)
if "import glob" not in final_code:
    final_code = final_code.replace("import sys, os, json, time, threading, queue, sqlite3", "import sys, os, json, time, threading, queue, sqlite3, glob")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(final_code)
    print("Rebuilt dashboard.py perfectly!")
