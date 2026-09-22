import streamlit as st
import sqlite3
from nexus.utils import NexusDB, get_logger

# Configure logger
logger = get_logger(__name__)

# Import pages
from dashboard.pages import battle_view, attacker_profiles, detection_dashboard, evolution_log

def main():
    st.set_page_config(page_title="NEXUS Dashboard", layout="wide")
    
    db = NexusDB('data')
    
    st.sidebar.title("NEXUS Navigation")
    
    # Sidebar navigation
    page = st.sidebar.radio(
        "Go to",
        ['Battle View', 'Attacker Profiles', 'Detection Dashboard', 'Evolution Log']
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Global Stats")
    try:
        conn = sqlite3.connect(db.results)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
        if c.fetchone():
            c.execute("SELECT COUNT(*) FROM events")
            total = c.fetchone()[0]
            st.sidebar.metric("Total Events", total)
            
            # Additional metric if is_detected exists
            try:
                c.execute("SELECT COUNT(*) FROM events WHERE is_detected=1")
                detected = c.fetchone()[0]
                st.sidebar.metric("Detected Events", detected)
            except sqlite3.OperationalError:
                pass
        else:
            st.sidebar.info("No events data yet.")
        conn.close()
    except Exception as e:
        logger.error(f"Error loading global stats: {e}")
        st.sidebar.error("Stats unavailable.")
    
    if page == 'Battle View':
        battle_view.render(db)
    elif page == 'Attacker Profiles':
        attacker_profiles.render(db)
    elif page == 'Detection Dashboard':
        detection_dashboard.render(db)
    elif page == 'Evolution Log':
        evolution_log.render(db)

if __name__ == "__main__":
    main()
