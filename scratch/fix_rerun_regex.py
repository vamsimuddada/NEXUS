import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Delete the middle st.rerun using regex
text = re.sub(
    r'except queue\.Empty: pass\s+if st\.session_state\.running:\s+time\.sleep\(0\.2\)\s+st\.rerun\(\)',
    r'except queue.Empty: pass',
    text
)

# Also delete the __DONE__ rerun
text = re.sub(
    r'if msg == "__DONE__":\s+st\.session_state\.running = False\s+st\.session_state\.live_feed\.append\("=== CAMPAIGN CONCLUDED ==="\)\s+st\.rerun\(\)',
    r'if msg == "__DONE__":\n                        st.session_state.running = False\n                        st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")\n                        break',
    text
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
