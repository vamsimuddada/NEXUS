import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Add a third chart for MITRE ATT&CK Effectiveness
old_charts = """            c_chart1, c_chart2 = st.columns(2)
            with c_chart1:
                with st.container(border=True):
                    if elo_hist: st.plotly_chart(fig_elo, use_container_width=True)
            with c_chart2:
                with st.container(border=True):
                    if f1_hist: st.plotly_chart(fig_f1, use_container_width=True)"""

new_charts = """            # MITRE Technique Chart
            tech_stats = camp_data.get("technique_stats", [])
            fig_tech = None
            if tech_stats:
                df_tech = pd.DataFrame(tech_stats)
                # Filter out techniques with negligible uses for a cleaner chart
                df_tech = df_tech[df_tech['uses'] > 10].sort_values("uses", ascending=False)
                fig_tech = px.bar(df_tech, x="technique", y=["detected", "evaded"], title="MITRE ATT&CK Technique Effectiveness (Detected vs Evaded)", barmode="stack", color_discrete_sequence=["#3b82f6", "#ef4444"])
                fig_tech.update_layout(
                    font_family="Space Grotesk",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis_title="ATT&CK Technique",
                    yaxis_title="Total Usages",
                    legend_title="Outcome"
                )

            c_chart1, c_chart2 = st.columns(2)
            with c_chart1:
                with st.container(border=True):
                    if elo_hist: st.plotly_chart(fig_elo, use_container_width=True)
            with c_chart2:
                with st.container(border=True):
                    if f1_hist: st.plotly_chart(fig_f1, use_container_width=True)
            
            if fig_tech:
                with st.container(border=True):
                    st.plotly_chart(fig_tech, use_container_width=True)"""

text = text.replace(old_charts, new_charts)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
