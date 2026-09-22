import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

badge_html = '<div style="background: #0f172a; color: #ffffff; font-family: \'JetBrains Mono\', monospace; font-size: 0.7rem; padding: 4px 10px; border-radius: 4px; font-weight: 700; letter-spacing: 0.5px;">ACTION REQUIRED</div>\n'

text = text.replace(badge_html, '')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
