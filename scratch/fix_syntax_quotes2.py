import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the broken Python strings that got messed up by the global replace
text = text.replace('st.markdown("<h3 style="font-family:\\\'Inter\\\', sans-serif;', 'st.markdown("<h3 style=\'font-family:\\\'Inter\\\', sans-serif;')
text = text.replace('st.markdown("<h4 style="font-family:\\\'Inter\\\', sans-serif;', 'st.markdown("<h4 style=\'font-family:\\\'Inter\\\', sans-serif;')
text = text.replace('st.markdown("<div style="font-family:\\\'Inter\\\', sans-serif;', 'st.markdown("<div style=\'font-family:\\\'Inter\\\', sans-serif;')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
