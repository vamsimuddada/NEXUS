import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# --- 1. Fix Active Threats KPI ---
# I'll just find c4.markdown(kpi_card("Active Threats", "6"...
# And replace "6" with a dynamic variable
kpi_replacement = """
    # Dynamically count active threats from SIEM logs
    active_threats_count = 0
    try:
        import os, json
        if os.path.exists("data/siem/nexus_events.ndjson"):
            attackers = set()
            with codecs.open("data/siem/nexus_events.ndjson", "r", "utf-8") as sf:
                for line in sf:
                    if line.strip():
                        try: attackers.add(json.loads(line).get("labels", {}).get("nexus_attacker"))
                        except: pass
            attackers.discard(None)
            active_threats_count = len(attackers)
    except: pass
    
    c4.markdown(kpi_card("Active Threats", str(active_threats_count), "Persistent APT Actors", "#ef4444", ICON_WARN), unsafe_allow_html=True)
"""
text = re.sub(r'c4\.markdown\(kpi_card\("Active Threats", "6",.*?unsafe_allow_html=True\)', kpi_replacement.strip(), text)

# --- 2. Fix Top Alerts Chart ---
old_alerts = """            try:
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
            except: st.info("Database not initialized.")"""

new_alerts = """            try:
                import os, json, pandas as pd
                if os.path.exists("data/siem/nexus_events.ndjson"):
                    severities = []
                    with codecs.open("data/siem/nexus_events.ndjson", "r", "utf-8") as sf:
                        for line in sf:
                            if line.strip():
                                try:
                                    log = json.loads(line)
                                    sev_val = log.get("event", {}).get("severity", 50)
                                    if sev_val >= 80: sev = "Critical"
                                    elif sev_val >= 60: sev = "High"
                                    elif sev_val >= 40: sev = "Medium"
                                    else: sev = "Low"
                                    severities.append(sev)
                                except: pass
                    
                    if severities:
                        df_alerts = pd.DataFrame({"Severity": severities})
                        sev_counts = df_alerts["Severity"].value_counts().reset_index()
                        sev_counts.columns = ["Severity", "Count"]
                        fig = px.bar(sev_counts, x="Severity", y="Count", color="Severity", color_discrete_sequence=PALETTE)
                        fig.update_layout(NEXUS_LAYOUT)
                        st.plotly_chart(fig, use_container_width=True, theme=None)
                    else: st.info("No alerts recorded yet.")
                else: st.info("SIEM feed not found.")
            except Exception as e: st.warning(f"Error loading alerts: {e}")"""

text = text.replace(old_alerts, new_alerts)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
