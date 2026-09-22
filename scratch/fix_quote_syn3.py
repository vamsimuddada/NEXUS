import codecs
with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace('font-family: "Space Grotesk"', "font-family: 'Space Grotesk'")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
