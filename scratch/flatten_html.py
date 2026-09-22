import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace block 1 (Campaign overview)
old_block_1 = """            # Left floated column (Campaign Overview & Mitigations)
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
            \"\"\""""

# Wait, in the actual file, it looks like this now:
old_block_1_actual = """            html += f\"\"\"<div style="float: left; width: 38%; margin-right: 2%; margin-bottom: 24px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 24px; box-shadow: 0 4px 15px rgba(15,23,42,0.02);">
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
</div>\"\"\""""


old_block_2_actual = """                    html += f\"\"\"<div style='background:#ffffff; border:1px solid #e2e8f0; padding:16px 20px; border-radius:12px; margin-bottom:16px; box-shadow: 0 4px 15px rgba(15,23,42,0.02);'>
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
</div>\"\"\""""

new_block_1_actual = "            html += f\"<div style='float: left; width: 38%; margin-right: 2%; margin-bottom: 24px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 24px; box-shadow: 0 4px 15px rgba(15,23,42,0.02);'><h3 style='color:#0f172a; font-family:\\\"Space Grotesk\\\", sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800; letter-spacing:-0.5px;'>Campaign overview</h3><p style='margin:6px 0; font-size:0.95rem; color:#475569;'><b>Battle ID:</b> <code style='color:#0f172a; background:#f1f5f9; padding:2px 6px; border-radius:4px;'>{report_data.get('battle_id', 'N/A')}</code></p><p style='margin:6px 0; font-size:0.95rem; color:#475569;'><b>Timestamp:</b> <code style='color:#0f172a; background:#f1f5f9; padding:2px 6px; border-radius:4px;'>{report_data.get('timestamp', 'N/A')}</code></p><p style='margin:6px 0; font-size:0.95rem; color:#475569;'><b>Outcome:</b> <span style='color:{win_color}; font-weight:800; letter-spacing:0.5px;'>{winner} VICTORY</span></p><hr style='border:0; border-top:1px solid #e2e8f0; margin:24px 0;'><h3 style='color:#0f172a; font-family:\\\"Space Grotesk\\\", sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800; letter-spacing:-0.5px;'>Blue Team Mitigations</h3><p style='margin:6px 0; font-size:0.95rem; color:#475569;'><b>SIGMA Rules Deployed:</b> <code style='color:#3b82f6; background:rgba(59,130,246,0.1); padding:2px 6px; border-radius:4px;'>{metrics.get('sigma_rules', 0)}</code></p><p style='margin:6px 0; font-size:0.95rem; color:#475569;'><b>Final Accuracy (F1):</b> <code style='color:#10b981; background:rgba(16,185,129,0.1); padding:2px 6px; border-radius:4px;'>{(metrics.get('f1_score', 0)*100):.1f}%</code></p><p style='margin:6px 0; font-size:0.95rem; color:#475569;'><b>Precision:</b> <code style='color:#10b981; background:rgba(16,185,129,0.1); padding:2px 6px; border-radius:4px;'>{(metrics.get('precision', 0)*100):.1f}%</code></p><p style='margin:6px 0; font-size:0.95rem; color:#475569;'><b>Recall:</b> <code style='color:#10b981; background:rgba(16,185,129,0.1); padding:2px 6px; border-radius:4px;'>{(metrics.get('recall', 0)*100):.1f}%</code></p><p style='color:#64748b; font-size:0.85rem; margin-top:24px; line-height:1.6;'>The autonomous Blue Team agent successfully analyzed the network traffic in real-time, identifying malicious signatures and deploying new SIGMA rules to block the execution pathways.</p></div>\""

new_block_2_actual = "                    html += f\"<div style='background:#ffffff; border:1px solid #e2e8f0; padding:16px 20px; border-radius:12px; margin-bottom:16px; box-shadow: 0 4px 15px rgba(15,23,42,0.02);'><div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom: 1px solid #f1f5f9; padding-bottom: 12px;'><strong style='color:#0f172a; font-size:1.05rem; font-family:\\\"Space Grotesk\\\", sans-serif;'>{attacker} executed {tech}</strong><div>{status}</div></div><div style='font-family:monospace; color:#64748b; font-size:0.85rem; margin-bottom:12px; line-height:1.6;'><b>Network Route:</b> Src: {ip_src} &rarr; Dst: {ip_dst} | <b>Target Host:</b> {target}<br><b>Compromised Identity:</b> {log.get('user', 'SYSTEM')} ({log.get('department', 'IT')} Dept) | <b>Admin Privileges:</b> {str(log.get('is_admin', False)).upper()}<br><b>Telemetry Payload:</b> [Event ID {log.get('event_id', '???')}] {log.get('message', 'Unknown action')}</div><div style='font-size:0.85rem; background:#f8fafc; padding:10px 14px; border-radius:6px; border-left: 3px solid #10b981;'>{mitigation_text}</div></div>\""


text = text.replace(old_block_1_actual, new_block_1_actual)
text = text.replace(old_block_2_actual, new_block_2_actual)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
