import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the dictionary key error
text = text.replace("STATIC_TECHNIQUES[t]['mitigation']", "STATIC_TECHNIQUES[t].get('mitigations', [''])[0] if isinstance(STATIC_TECHNIQUES[t].get('mitigations', ['']), list) else STATIC_TECHNIQUES[t].get('mitigations', '')")

# Fix the backslash HTML escaping bug globally for all double quotes that were escaped as \"
text = text.replace('style=\\"', 'style="')
text = text.replace(';\\">', ';">')
text = text.replace('\\">', '">')
text = text.replace('gap:12px;\\">', 'gap:12px;">')
text = text.replace('margin-bottom:12px;\\">', 'margin-bottom:12px;">')
text = text.replace('color:#ef4444;\\">', 'color:#ef4444;">')
text = text.replace('color:#10b981;\\">', 'color:#10b981;">')
text = text.replace('color:#8b5cf6;\\">', 'color:#8b5cf6;">')
text = text.replace('font-size:1.3rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px;\\">', 'font-size:1.3rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px;">')
text = text.replace('margin-bottom:24px;\\">', 'margin-bottom:24px;">')

# Fix Tracked Actors font
text = text.replace(
    "<h4 style='color:#0f172a; margin-top:0;'>Tracked Actors</h4>",
    "<h4 style=\"font-family:'Inter', sans-serif; font-size:1.4rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px; margin-top:0; margin-bottom:16px;\">Tracked Actors</h4>"
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
