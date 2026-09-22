import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Drain the msg_queue completely on every rerun so the dashboard perfectly mirrors the true state of the subprocess
old_queue = """                try:
                    # Read one line at a time for realtime cinematic effect
                    msg = st.session_state.msg_queue.get_nowait()
                    if msg == "__DONE__":
                        st.session_state.running = False
                        st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")
                        st.rerun()
                    else: 
                        st.session_state.live_feed.append(msg)
                except queue.Empty: pass"""

new_queue = """                try:
                    # Drain all currently available messages from the subprocess
                    while True:
                        msg = st.session_state.msg_queue.get_nowait()
                        if msg == "__DONE__":
                            st.session_state.running = False
                            st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")
                            break
                        else: 
                            st.session_state.live_feed.append(msg)
                except queue.Empty: pass"""

text = text.replace(old_queue, new_queue)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
