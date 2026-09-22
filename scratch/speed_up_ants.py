import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace('animation: dash-march 3s linear infinite !important;', 'animation: dash-march 1.5s linear infinite !important;')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
