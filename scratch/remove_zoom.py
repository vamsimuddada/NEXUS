import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Remove the broken zoom property
text = text.replace("zoom: 0.85;", "")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
