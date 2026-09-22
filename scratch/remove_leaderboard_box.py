import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Use re.sub to carefully strip it
# The emoji is "\U0001f3c6"
pattern = r"    # . THREAT INTELLIGENCE LEADERBOARD ..*?elif st\.session_state\.current_page == 'analytics':"
replacement = "elif st.session_state.current_page == 'analytics':"
text = re.sub(pattern, replacement, text, flags=re.DOTALL)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
