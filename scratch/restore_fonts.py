import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace global CSS header fonts
text = text.replace("h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif !important; }", 
                    "h1, h2, h3, h4, h5, h6 { font-family: 'Space Grotesk', sans-serif !important; }")

# Replace hardcoded fonts in injected HTML
text = text.replace("font-family:'Inter'", "font-family:'Space Grotesk'")
text = text.replace("font-family:\\'Inter\\'", "font-family:\\'Space Grotesk\\'")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
