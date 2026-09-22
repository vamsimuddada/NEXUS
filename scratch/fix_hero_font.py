import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the CSS for hero-header and kpi-value
text = text.replace(".hero-header {\n    font-family: 'Space Grotesk', sans-serif;", ".hero-header {\n    font-family: 'Space Grotesk', sans-serif !important;")
text = text.replace(".kpi-value { font-family: 'Space Grotesk', sans-serif;", ".kpi-value { font-family: 'Space Grotesk', sans-serif !important;")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
