import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace("margin-top: -30px;", "margin-top: 5px;")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
