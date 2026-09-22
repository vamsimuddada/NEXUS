import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Slow down the Streamlit rerun loop to prevent the browser WebSocket from dropping frames and chunking updates
old_rerun = 'time.sleep(0.05)\n                st.rerun()'
new_rerun = 'time.sleep(0.2)\n                st.rerun()'

text = text.replace(old_rerun, new_rerun)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
