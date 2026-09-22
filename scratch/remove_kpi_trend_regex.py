import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Completely strip out the <div class="kpi-trend"> line regardless of indentation
text = re.sub(r'^[ \t]*<div class="kpi-trend">\{trend\}</div>\r?\n', '', text, flags=re.MULTILINE)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
