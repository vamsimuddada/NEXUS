import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Fix the 0 values by pulling from the 'metrics' dictionary instead of 'stats'
old_stats = """                    stats = report_data.get('stats', {})
                    st.write(f"**SIGMA Rules Deployed:** `{stats.get('total_sigma_rules', 0)}` dynamic rules written")
                    st.write(f"**Final Accuracy:** `{(stats.get('accuracy', 0)*100):.1f}%`")
                    st.write(f"**Precision:** `{(stats.get('precision', 0)*100):.1f}%`")
                    st.write(f"**Recall:** `{(stats.get('recall', 0)*100):.1f}%`")"""

new_stats = """                    metrics = report_data.get('metrics', {})
                    st.write(f"**SIGMA Rules Deployed:** `{metrics.get('sigma_rules', 0)}` dynamic rules written")
                    st.write(f"**Final Accuracy (F1):** `{(metrics.get('f1_score', 0)*100):.1f}%`")
                    st.write(f"**Precision:** `{(metrics.get('precision', 0)*100):.1f}%`")
                    st.write(f"**Recall:** `{(metrics.get('recall', 0)*100):.1f}%`")"""

text = text.replace(old_stats, new_stats)


# 2. Add much more context to the vectors!
old_vector = """                                <div style='font-family:monospace; color:#64748b; font-size:0.85rem; margin-bottom:8px;'>
                                    <b>Vector:</b> Src: {ip_src} &rarr; Dst: {ip_dst} | <b>Target:</b> {target}
                                </div>"""

new_vector = """                                <div style='font-family:monospace; color:#64748b; font-size:0.85rem; margin-bottom:8px;'>
                                    <b>Network Route:</b> Src: {ip_src} &rarr; Dst: {ip_dst} | <b>Target Host:</b> {target}<br>
                                    <b>Compromised Identity:</b> {log.get('user', 'SYSTEM')} ({log.get('department', 'IT')} Dept) | <b>Admin Privileges:</b> {str(log.get('is_admin', False)).upper()}<br>
                                    <b>Telemetry Payload:</b> [Event ID {log.get('event_id', '???')}] {log.get('message', 'Unknown action')}
                                </div>"""

text = text.replace(old_vector, new_vector)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
