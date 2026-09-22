import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Add st.session_state.live_feed = [] when starting a new campaign
old_btn = """                if st.button("START CAMPAIGN", use_container_width=True):
                    # Wipe the old logs so the dashboard only shows the current test
                    try:"""

new_btn = """                if st.button("START CAMPAIGN", use_container_width=True):
                    st.session_state.live_feed = []  # Clear the terminal UI
                    # Wipe the old logs so the dashboard only shows the current test
                    try:"""

text = text.replace(old_btn, new_btn)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
