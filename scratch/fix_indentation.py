import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the massive indentation caused by the string replace concatenation!
text = re.sub(r' +st\.plotly_chart\(fig2, use_container_width=True, theme=None\)', '            st.plotly_chart(fig2, use_container_width=True, theme=None)', text)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
