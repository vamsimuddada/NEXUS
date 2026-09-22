import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the indentation of the injected block
text = text.replace('st.markdown("<hr style=\'border: none;', '    st.markdown("<hr style=\'border: none;')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
