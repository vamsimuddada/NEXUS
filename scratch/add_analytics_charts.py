import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Find the end of tab2
idx = text.find('if __name__ == "__main__":')

new_charts = """

    # --- ADVANCED ANALYTICS ---
    st.markdown("<h3 style='color:#0f172a; font-family: \\'Space Grotesk\\', sans-serif !important; font-weight:800; letter-spacing:-1px; margin-top:32px; margin-bottom:16px;'>Global Evolution Analytics</h3>", unsafe_allow_html=True)
    
    try:
        import glob, json
        import pandas as pd
        import plotly.express as px
        
        campaigns = glob.glob("data/campaigns/campaign_*.json")
        if campaigns:
            latest_camp = max(campaigns, key=os.path.getctime)
            with open(latest_camp, 'r', encoding='utf-8') as f:
                camp_data = json.load(f)
                
            # ELO History Chart
            elo_hist = camp_data.get("elo_history", [])
            if elo_hist:
                df_elo_hist = pd.DataFrame(elo_hist)
                df_elo_hist.index.name = "Battle/Turn"
                df_elo_hist = df_elo_hist.reset_index()
                df_elo_hist = df_elo_hist.melt(id_vars=["Battle/Turn"], var_name="Agent", value_name="ELO")
                
                fig_elo = px.line(df_elo_hist, x="Battle/Turn", y="ELO", color="Agent", title="Agent Intelligence (ELO) Co-Evolution Trajectory")
                fig_elo.update_layout(
                    font_family="Space Grotesk",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis_title="Simulation Time",
                    yaxis_title="ELO Rating",
                    legend_title="Entities"
                )
                
            # F1 History Chart
            f1_hist = camp_data.get("f1_history", [])
            if f1_hist:
                df_f1 = pd.DataFrame({"Battle": range(len(f1_hist)), "F1 Score": f1_hist})
                fig_f1 = px.area(df_f1, x="Battle", y="F1 Score", title="Defender Detection Accuracy (F1 Score) Trend")
                fig_f1.update_traces(line_color="#10b981", fillcolor="rgba(16,185,129,0.2)")
                fig_f1.update_layout(
                    font_family="Space Grotesk",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)"
                )
                
            c_chart1, c_chart2 = st.columns(2)
            with c_chart1:
                with st.container(border=True):
                    if elo_hist: st.plotly_chart(fig_elo, use_container_width=True)
            with c_chart2:
                with st.container(border=True):
                    if f1_hist: st.plotly_chart(fig_f1, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to render advanced analytics: {e}")

"""

text = text[:idx] + new_charts + "\n\n" + text[idx:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
