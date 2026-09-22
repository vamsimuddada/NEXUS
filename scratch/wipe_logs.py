import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Find the INITIATE WARGAMES button block
old_btn = 'if st.button("🚀 INITIATE WARGAMES", use_container_width=True):'
new_btn = """if st.button("🚀 INITIATE WARGAMES", use_container_width=True):
                # Wipe the old logs so the dashboard only shows the current test
                try:
                    open("data/siem/nexus_events.ndjson", "w").close()
                    import sqlite3
                    with sqlite3.connect("data/simulation_results.db") as conn:
                        conn.execute("DELETE FROM simulation_results")
                except: pass"""

text = text.replace(old_btn, new_btn)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
