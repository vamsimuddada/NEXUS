import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace the broken span HTML with correct double quotes for the style attribute
old_span = "tech_html += f\"<span style='background:#f1f5f9; border: 1px solid #e2e8f0; color:#334155; padding:6px 12px; border-radius:6px; font-family:\\'JetBrains Mono\\', monospace; font-weight:600; font-size:0.85rem; margin-right:10px; margin-bottom:10px; display:inline-block;'>{t_name}</span>\""
new_span = "tech_html += f'<span style=\"background:#f1f5f9; border: 1px solid #e2e8f0; color:#334155; padding:6px 12px; border-radius:6px; font-family:\\'JetBrains Mono\\', monospace; font-weight:600; font-size:0.85rem; margin-right:10px; margin-bottom:10px; display:inline-block;\">{t_name}</span>'"

text = text.replace(old_span, new_span)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
