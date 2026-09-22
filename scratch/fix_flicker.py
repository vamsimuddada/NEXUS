import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Hide the top-right flickering running widget
css_inject = """<style>
/* Hide the flickering Streamlit 'Running...' indicator in top right */
[data-testid="stStatusWidget"] { visibility: hidden !important; display: none !important; }
"""
text = text.replace('<style>', css_inject)

# 2. Add Stop button and progress bar
old_feed_block = """        if st.session_state.running:
            try:
                while True:
                    msg = st.session_state.msg_queue.get_nowait()
                    if msg == "__DONE__":
                        st.session_state.running = False
                        st.rerun()
                    else: st.session_state.live_feed.append(msg)
            except queue.Empty: pass
            if st.session_state.running: time.sleep(0.5); st.rerun()"""

new_feed_block = """        if st.session_state.running:
            c1, c2 = st.columns([3, 1])
            with c2:
                if st.button("🛑 HALT WARGAMES", use_container_width=True):
                    st.session_state.running = False
                    st.session_state.live_feed.append("=== SIMULATION ABORTED BY USER ===")
                    st.rerun()
            with c1:
                # Mock a progress bar based on feed length
                prog = min(len(st.session_state.live_feed) * 2, 95)
                st.progress(prog, text="🧠 AI Simulation in Progress...")

            try:
                while True:
                    msg = st.session_state.msg_queue.get_nowait()
                    if msg == "__DONE__":
                        st.session_state.running = False
                        st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")
                        st.rerun()
                    else: st.session_state.live_feed.append(msg)
            except queue.Empty: pass
            if st.session_state.running: time.sleep(0.3); st.rerun()
        else:
            if st.session_state.live_feed:
                st.progress(100, text="✅ Simulation Complete")
"""

text = text.replace(old_feed_block, new_feed_block)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
