import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace the widget configuration with better defaults
old_widgets = """            provider = st.selectbox("AI Brain", ["Mock (offline)", "Ollama (local)"])
            turns = st.slider("Campaign Turns", 1, 10, 3)
            st.markdown("---")
            hosts = st.slider("Target Hosts", 2, 20, 4)
            users = st.slider("Simulated Users", 5, 50, 8)"""

new_widgets = """            provider = st.selectbox("AI Brain", ["Mock (Instant/Offline)", "Ollama (Live AI)"], index=0)
            turns = st.slider("Campaign Turns", 1, 10, 5)
            st.markdown("---")
            hosts = st.slider("Target Hosts", 2, 20, 8)
            users = st.slider("Simulated Users", 5, 50, 24)"""

text = text.replace(old_widgets, new_widgets)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
