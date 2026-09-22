import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Fix terminal feed height contradiction
text = text.replace(
    "max-height: 400px; overflow-y: auto; color: #334155; height: 420px;'",
    "max-height: 450px; overflow-y: auto; color: #334155; height: 450px;'"
)

# 2. Remove the graph squishing (450px is too tight for the graph)
text = text.replace("fig2.update_layout(height=450)\n", "")

# 3. Tighten the Live Threat Graph title margins to align perfectly within its container
text = text.replace(
    "<h3 style='color:#0f172a; font-family:\\'Space Grotesk\\', sans-serif; margin-bottom:16px; font-weight:700;'>Live Threat Graph</h3>",
    "<h3 style='color:#0f172a; font-family:\\'Space Grotesk\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800; letter-spacing:-0.5px;'>Live Threat Graph</h3>"
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
