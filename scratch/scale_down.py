import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Add global scale-down to html, body (zoom for Chromium, font-size for rem scaling)
text = text.replace(
    "html, body { font-family: 'Inter', sans-serif !important; color: #1e293b !important; }",
    "html, body { font-family: 'Inter', sans-serif !important; color: #1e293b !important; zoom: 0.85; }\nhtml { font-size: 14px !important; }"
)

# 2. Scale down the massive custom fonts so they fit better at 100%
text = text.replace("font-size: 3.2rem;", "font-size: 2.6rem;")
text = text.replace("font-size: 2.5rem;", "font-size: 2.1rem;")
text = text.replace("margin-bottom: 30px;", "margin-bottom: 20px;")
text = text.replace("padding: 24px 32px;", "padding: 18px 24px;")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
