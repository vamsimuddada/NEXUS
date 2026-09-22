import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

bad_css = "h1, h2, h3, h4, h5, h6, p, label, a, li { font-family: 'Inter', sans-serif !important; }"
good_css = """h1, h2, h3, h4, h5, h6 { font-family: 'Space Grotesk', sans-serif !important; }
p, label, a, li { font-family: 'Inter', sans-serif !important; }"""

text = text.replace(bad_css, good_css)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
