import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the CSS escaping issue!
text = text.replace(
    "<h3 style='color:#0f172a; font-family:\\'Space Grotesk\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800; letter-spacing:-0.5px;'>Live Threat Graph</h3>",
    '<h3 style="color:#0f172a; font-family:\'Space Grotesk\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800; letter-spacing:-0.5px;">Live Threat Graph</h3>'
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
