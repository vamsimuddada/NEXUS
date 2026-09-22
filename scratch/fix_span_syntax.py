import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the JetBrains Mono span syntax error
text = text.replace(
    'tools_html = "".join([f"<span style="background:#f8fafc; color:#334155; padding:8px 16px; border-radius:8px; font-family:\'JetBrains Mono\', monospace; font-size:0.9rem; font-weight:600; border:1px solid #e2e8f0;">{mw}</span>" for mw in profile.get(\'tools\', [])])',
    'tools_html = "".join([f"<span style=\'background:#f8fafc; color:#334155; padding:8px 16px; border-radius:8px; font-family:\\\'JetBrains Mono\\\', monospace; font-size:0.9rem; font-weight:600; border:1px solid #e2e8f0;\'>{mw}</span>" for mw in profile.get(\'tools\', [])])'
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
