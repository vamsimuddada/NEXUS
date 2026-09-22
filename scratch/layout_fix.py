import sys

with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_block = '''    r1c1, r1c2 = st.columns([6, 4])
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
                st.warning(f"Graph engine error: {e}")'''

new_block = '''    with st.container(border=True):
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
            
    with st.container(border=True):
        st.markdown("<h3 style='color:#0f172a; margin-bottom:16px; font-weight:700;'>Live Threat Graph</h3>", unsafe_allow_html=True)
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            from integrations.network_graph import build_graph_from_db
            fig2 = build_graph_from_db()
            fig2.update_layout(NEXUS_LAYOUT)
            # Increase height for full width
            fig2.update_layout(height=600)
            st.plotly_chart(fig2, use_container_width=True, theme=None)
        except Exception as e:
            st.warning(f"Graph engine error: {e}")'''

code = code.replace(old_block, new_block)

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Layout updated.")
