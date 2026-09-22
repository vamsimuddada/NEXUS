import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Add import glob and fix the button display logic
if 'import glob' not in text:
    text = text.replace('import json, time, threading, queue, sqlite3', 'import json, time, threading, queue, sqlite3, glob')

# Add session state flag for test_completed
if 'if "test_completed" not in st.session_state:' not in text:
    text = text.replace(
        'if "msg_queue" not in st.session_state: st.session_state.msg_queue = queue.Queue()',
        'if "msg_queue" not in st.session_state: st.session_state.msg_queue = queue.Queue()\nif "test_completed" not in st.session_state: st.session_state.test_completed = False'
    )

# Set test_completed = True when campaign concludes
old_done = """                if msg == "__DONE__":
                        st.session_state.running = False
                        st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")
                        st.rerun()"""
new_done = """                if msg == "__DONE__":
                        st.session_state.running = False
                        st.session_state.test_completed = True
                        st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")
                        st.rerun()"""
text = text.replace(old_done, new_done)

# Only show the TEST RESULTS button if test_completed is True!
old_button = """            st.markdown("<br>", unsafe_allow_html=True)
            if st.session_state.current_page == 'home':
                if st.button("TEST RESULTS", use_container_width=True):
                    st.session_state.current_page = 'results'
                    st.rerun()
                if st.button("ANALYTICS & EXPORTS", use_container_width=True):"""
new_button = """            st.markdown("<br>", unsafe_allow_html=True)
            if st.session_state.current_page == 'home':
                if st.session_state.test_completed:
                    if st.button("TEST RESULTS", type="primary", use_container_width=True):
                        st.session_state.current_page = 'results'
                        st.rerun()
                if st.button("ANALYTICS & EXPORTS", use_container_width=True):"""
text = text.replace(old_button, new_button)

# Also reset test_completed to False when a new campaign starts
old_start = """                if st.button("START CAMPAIGN", type="primary", use_container_width=True):
                    st.session_state.running = True
                    st.session_state.live_feed = []"""
new_start = """                if st.button("START CAMPAIGN", type="primary", use_container_width=True):
                    st.session_state.running = True
                    st.session_state.test_completed = False
                    st.session_state.live_feed = []"""
text = text.replace(old_start, new_start)


with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
