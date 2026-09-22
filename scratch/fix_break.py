import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the SyntaxError: 'break' outside loop
old_break = """                        st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")
                        break"""

new_break = """                        st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")"""

text = text.replace(old_break, new_break)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
