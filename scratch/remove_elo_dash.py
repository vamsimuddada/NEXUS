import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

import re

# Remove ELO Leaderboard section from the dashboard
old_dash = r"""        st.markdown("<div class='section-header'>GLOBAL THREAT LEADERBOARD</div>", unsafe_allow_html=True)
        # We enforce strict formatting for the dashboard too to prevent string overflow
        df_elo = pd.DataFrame(elo_table)
        df_elo["win_rate"] = (df_elo["win_rate"] * 100).round(1).astype(str) + "%"
        df_elo["evasion_rate"] = (df_elo["evasion_rate"] * 100).round(1).astype(str) + "%"
        df_elo["elo"] = df_elo["elo"].astype(int)
        df_elo["peak_elo"] = df_elo["peak_elo"].astype(int)
        elo_table = df_elo[["rank", "entity", "elo", "peak_elo", "battles", "win_rate", "evasion_rate"]]
        st.dataframe(elo_table, use_container_width=True, hide_index=True)"""

text = text.replace(old_dash, "")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
