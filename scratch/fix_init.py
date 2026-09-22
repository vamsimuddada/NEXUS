import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

target = 'if "msg_queue" not in st.session_state:'
insertion = "if 'current_page' not in st.session_state: st.session_state.current_page = 'home'\nif \"msg_queue\" not in st.session_state:"

text = text.replace(target, insertion)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
