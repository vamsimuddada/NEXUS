import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Remove the st.rerun() that was halting the script in the middle of the page
old_rerun_block = """              if st.session_state.running: 
                  time.sleep(0.2)
                  st.rerun()"""
text = text.replace(old_rerun_block, "")

# Same for the queue drain break
old_drain_break = """                        if msg == "__DONE__":
                            st.session_state.running = False
                            st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")
                            st.rerun()"""
new_drain_break = """                        if msg == "__DONE__":
                            st.session_state.running = False
                            st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")
                            break"""
text = text.replace(old_drain_break, new_drain_break)

# Append the rerun loop to the VERY BOTTOM of the file so the UI actually renders!
text += """
# ══════════════════════════════════════════════════════════════════════════════
#  LIVE ANIMATION LOOP
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get('running', False):
    import time
    time.sleep(0.2)
    st.rerun()
"""

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
