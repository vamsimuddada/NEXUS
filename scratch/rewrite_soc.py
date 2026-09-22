import sys

with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update Fonts in CSS
code = code.replace("family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700;800&display=swap", "family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap")
code = code.replace("'Inter', sans-serif", "'Google Sans', 'Plus Jakarta Sans', sans-serif")
code = code.replace("'Space Grotesk', sans-serif", "'Google Sans', 'Plus Jakarta Sans', sans-serif")

# 2. Rewrite SOC Overview
# Find the bounds of tab1
start_idx = code.find('with tab1:')
end_idx = code.find('with tab2:')

new_tab1 = '''with tab1:
    st.markdown("<div class='hero-header' style='margin-top:-10px; font-size: 2.8rem; letter-spacing: -1px;'>Security Command Center</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; margin-bottom:32px; font-size:1.1rem; font-weight:500;'>Unified threat intelligence and autonomous agent telemetry.</p>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    win_rate = (defender_wins/total_battles*100) if total_battles else 0
    c1.markdown(kpi_card("Mean F1 Score", f"{avg_f1:.3f}", "+0.02 vs last week", "#2563eb", ICON_F1), unsafe_allow_html=True)
    c2.markdown(kpi_card("Defend Win Rate", f"{win_rate:.1f}%", f"{defender_wins} total blocks", "#10b981", ICON_SHIELD), unsafe_allow_html=True)
    c3.markdown(kpi_card("Battles Logged", str(total_battles), "Simulation database", "#f59e0b", ICON_DB), unsafe_allow_html=True)
    c4.markdown(kpi_card("Active Threats", "6", "Persistent APT Actors", "#ef4444", ICON_WARN), unsafe_allow_html=True)
    
    r1c1, r1c2 = st.columns([6, 4])
    with r1c1:
        with st.container(border=True):
            st.markdown("<h3 style='color:#0f172a; margin-bottom:16px; font-weight:700;'>Top Alerts by Severity</h3>", unsafe_allow_html=True)
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
            
    with r1c2:
        with st.container(border=True):
            st.markdown("<h3 style='color:#0f172a; margin-bottom:16px; font-weight:700;'>Live Threat Graph</h3>", unsafe_allow_html=True)
            try:
                sys.path.insert(0, os.path.dirname(__file__))
                from integrations.network_graph import build_graph_from_db
                fig2 = build_graph_from_db()
                fig2.update_layout(NEXUS_LAYOUT)
                st.plotly_chart(fig2, use_container_width=True, theme=None)
            except Exception as e:
                st.warning(f"Graph engine error: {e}")
                
    st.markdown("<h3 style='color:#0f172a; margin-top:32px; margin-bottom:16px; font-weight:700;'>Recent Security Events</h3>", unsafe_allow_html=True)
    with st.container(border=True):
        try:
            with sqlite3.connect("data/simulation_results.db") as conn:
                df_events = pd.read_sql("SELECT timestamp, agent_id, event_type, data FROM simulation_results ORDER BY timestamp DESC LIMIT 5", conn)
                if not df_events.empty:
                    st.dataframe(df_events, use_container_width=True, hide_index=True)
                else: st.info("No recent events.")
        except: st.info("Database not initialized.")

'''

code = code[:start_idx] + new_tab1 + code[end_idx:]

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Rewrote SOC tab successfully.")
