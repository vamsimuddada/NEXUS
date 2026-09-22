import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

old_block = """                if msg == "__DONE__":
                        st.session_state.running = False
                        st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")
                else: """

new_block = """                if msg == "__DONE__":
                        st.session_state.running = False
                        st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")
                        st.rerun() # Force one final UI refresh so the buttons and progress bar update to the completed state!
                else: """

text = text.replace(old_block, new_block)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
