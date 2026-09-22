import streamlit as st
import sqlite3
import pandas as pd
from nexus.utils import NexusDB, get_logger
from dashboard.components.charts import create_elo_chart

logger = get_logger(__name__)

def render(db: NexusDB):
    st.title("Attacker Profiles")
    st.write("ELO leaderboard and attacker history.")
    
    try:
        conn = sqlite3.connect(db.elo)
        
        # Leaderboard
        st.subheader("ELO Leaderboard")
        query_table = "SELECT name FROM sqlite_master WHERE type='table' AND name='leaderboard'"
        if not pd.read_sql_query(query_table, conn).empty:
            leaderboard = pd.read_sql_query("SELECT * FROM leaderboard ORDER BY elo_score DESC", conn)
            st.dataframe(leaderboard, use_container_width=True)
            
            for _, row in leaderboard.iterrows():
                attacker_id = row.get('attacker_id', 'Unknown')
                elo_score = row.get('elo_score', 0)
                with st.expander(f"Attacker: {attacker_id} (ELO: {elo_score})"):
                    st.write(f"**Wins**: {row.get('wins', 0)}")
                    st.write(f"**Losses**: {row.get('losses', 0)}")
        else:
            st.info("No leaderboard data yet.")
            
        # History
        st.subheader("ELO History")
        query_hist = "SELECT name FROM sqlite_master WHERE type='table' AND name='history'"
        if not pd.read_sql_query(query_hist, conn).empty:
            history_df = pd.read_sql_query("SELECT * FROM history ORDER BY timestamp ASC", conn)
            fig = create_elo_chart(history_df)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No ELO history yet.")
            
        conn.close()
    except Exception as e:
        logger.error(f"Failed to load attacker profiles: {e}")
        st.error("Error loading attacker profiles data.")
