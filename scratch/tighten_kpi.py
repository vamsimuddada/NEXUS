import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace("border-radius: 28px; padding: 32px;", "border-radius: 24px; padding: 22px;")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
