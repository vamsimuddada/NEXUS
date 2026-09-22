import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from nexus.utils import NexusDB, get_logger

logger = get_logger(__name__)

def render(db: NexusDB):
    st.title("Evolution Log")
    st.write("GNN training curves and newly generated defense rules.")
    
    try:
        conn = sqlite3.connect(db.training)
        
        # Loss curve
        query_loss = "SELECT name FROM sqlite_master WHERE type='table' AND name='loss_history'"
        if not pd.read_sql_query(query_loss, conn).empty:
            loss_df = pd.read_sql_query("SELECT * FROM loss_history ORDER BY epoch ASC", conn)
            if not loss_df.empty:
                st.subheader("GNN Loss Curve")
                if 'epoch' in loss_df.columns and 'loss' in loss_df.columns:
                    fig = px.line(loss_df, x='epoch', y='loss', title="Training Loss over Epochs", markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(loss_df, use_container_width=True)
            else:
                st.info("Loss history table is empty.")
        else:
            st.info("No training loss data yet.")
            
        # Rules generated
        query_rules = "SELECT name FROM sqlite_master WHERE type='table' AND name='rules'"
        if not pd.read_sql_query(query_rules, conn).empty:
            rules_df = pd.read_sql_query("SELECT * FROM rules ORDER BY created_at DESC LIMIT 50", conn)
            st.subheader("Recent Generated Rules")
            if not rules_df.empty:
                for _, row in rules_df.iterrows():
                    rule_id = row.get('rule_id', 'Unknown')
                    name = row.get('name', 'N/A')
                    with st.expander(f"Rule: {rule_id} - {name}"):
                        st.code(row.get('rule_content', ''), language='yaml')
            else:
                st.info("No rules generated yet.")
        else:
            st.info("No rules data yet.")
            
        conn.close()
    except Exception as e:
        logger.error(f"Failed to load evolution log: {e}")
        st.error("Error loading evolution log data.")
