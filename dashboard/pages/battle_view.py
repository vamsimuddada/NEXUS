import streamlit as st
import sqlite3
import pandas as pd
from nexus.utils import NexusDB, get_logger

logger = get_logger(__name__)

def render(db: NexusDB):
    st.title("Battle View")
    st.write("Live feed and recent simulation events.")
    
    try:
        conn = sqlite3.connect(db.results)
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='events'"
        if pd.read_sql_query(query, conn).empty:
            st.info("No events data found. Run the simulation to generate results.")
            conn.close()
            return
            
        df = pd.read_sql_query("SELECT * FROM events ORDER BY timestamp DESC LIMIT 100", conn)
        conn.close()
        
        if df.empty:
            st.info("Events table is empty.")
            return
            
        st.subheader("Recent Events Timeline")
        st.dataframe(df, use_container_width=True)
        
        st.subheader("Raw Log Feed")
        for _, row in df.head(10).iterrows():
            timestamp = row.get('timestamp', 'N/A')
            event_id = row.get('id', 'N/A')
            attacker = row.get('attacker_id', 'N/A')
            detected = row.get('is_detected', False)
            details = row.get('details', '')
            st.code(f"[{timestamp}] EVENT_ID={event_id} ATTACKER={attacker} DETECTED={detected}\nDETAILS: {details}", language="json")
            
    except Exception as e:
        logger.error(f"Failed to load battle view: {e}")
        st.error("Error loading battle view data.")
