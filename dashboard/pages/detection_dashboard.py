import streamlit as st
import sqlite3
import pandas as pd
from nexus.utils import NexusDB, get_logger
from dashboard.components.charts import create_detection_rate_chart, create_confusion_matrix

logger = get_logger(__name__)

def render(db: NexusDB):
    st.title("Detection Dashboard")
    st.write("Overview of detection rates and gaps in defense.")
    
    # Results DB for Detection Rates
    try:
        conn = sqlite3.connect(db.results)
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='events'"
        if not pd.read_sql_query(query, conn).empty:
            st.subheader("Detection Rates")
            df = pd.read_sql_query("SELECT * FROM events", conn)
            if not df.empty:
                total = len(df)
                if 'is_detected' in df.columns:
                    detected = len(df[df['is_detected'] == 1])
                    rate = (detected / total) * 100 if total > 0 else 0
                    st.metric("Overall Detection Rate", f"{rate:.2f}%")
                    
                    if 'timestamp' in df.columns:
                        # Dummy time_window to create a trend chart
                        try:
                            df['timestamp'] = pd.to_datetime(df['timestamp'])
                            df['time_window'] = df['timestamp'].dt.floor('h')
                            stats = df.groupby('time_window')['is_detected'].mean().reset_index()
                            stats.rename(columns={'is_detected': 'detection_rate'}, inplace=True)
                            
                            fig = create_detection_rate_chart(stats)
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            logger.error(f"Error parsing timestamps for detection chart: {e}")
                else:
                    st.info("No 'is_detected' column found in events.")
            else:
                st.info("Events table is empty.")
        else:
            st.info("No events data available.")
        conn.close()
    except Exception as e:
        logger.error(f"Error loading detection rates: {e}")
        st.error("Error loading detection rates.")
        
    # Gaps DB for Confusion Matrix
    try:
        conn_gaps = sqlite3.connect(db.gaps)
        query_gaps = "SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'"
        if not pd.read_sql_query(query_gaps, conn_gaps).empty:
            metrics_df = pd.read_sql_query("SELECT * FROM metrics ORDER BY id DESC LIMIT 1", conn_gaps)
            if not metrics_df.empty:
                st.subheader("Confusion Matrix")
                row = metrics_df.iloc[0]
                tp = int(row.get('tp', 0))
                fp = int(row.get('fp', 0))
                fn = int(row.get('fn', 0))
                tn = int(row.get('tn', 0))
                
                fig2 = create_confusion_matrix(tp, fp, fn, tn)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No gap metrics data available for confusion matrix.")
        else:
            st.info("No gap metrics data available.")
        conn_gaps.close()
    except Exception as e:
        logger.error(f"Error loading gap metrics: {e}")
        st.error("Error loading gaps data.")
        
    st.subheader("Tri-Brain Logic Summary")
    st.write("NEXUS employs a layered detection mechanism combining deterministic rules, heuristic anomaly detection, and AI-driven behavioral analysis.")
