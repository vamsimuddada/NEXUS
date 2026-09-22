import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Find the end of tab1 (right before tab2)
idx = text.find('with tab2:')

new_elo_ui = """
    # "?"? THREAT INTELLIGENCE LEADERBOARD "?"?
    st.markdown("<h3 style='color:#0f172a; font-family: \\'Space Grotesk\\', sans-serif !important; font-weight:800; letter-spacing:-1px; margin-top:32px; margin-bottom:16px;'>Threat Intelligence Leaderboard</h3>", unsafe_allow_html=True)
    with st.container(border=True):
        try:
            import glob, json
            reports = glob.glob("data/reports/battle_*.json")
            if reports:
                latest = max(reports, key=os.path.getctime)
                with codecs.open(latest, 'r', 'utf-8') as rf:
                    rep_data = json.load(rf)
                elo_table = rep_data.get("final_elo_table", [])
                if elo_table:
                    import pandas as pd
                    df_elo = pd.DataFrame(elo_table)
                    df_elo = df_elo[["rank", "entity", "elo", "peak_elo", "win_rate", "evasion_rate"]]
                    df_elo.columns = ["Rank", "Agent Entity", "Current ELO", "Peak ELO", "Win Rate", "Evasion Rate"]
                    # Format percentages
                    df_elo["Win Rate"] = df_elo["Win Rate"].apply(lambda x: f"{x:.1%}")
                    df_elo["Evasion Rate"] = df_elo["Evasion Rate"].apply(lambda x: f"{x:.1%}")
                    
                    st.dataframe(df_elo, use_container_width=True, hide_index=True)
                else:
                    st.info("No ELO data found in the latest campaign record.")
            else:
                st.info("No campaign reports generated yet.")
        except Exception as e:
            st.error(f"Failed to load ELO Leaderboard: {e}")

"""

text = text[:idx] + new_elo_ui + "\n\n" + text[idx:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
