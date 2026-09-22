import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace broken single-quote HTML escaping with proper double-quoted style attributes.
# Example: <div style='font-family:\'Inter\', sans-serif;'> -> <div style="font-family:'Inter', sans-serif;">
text = text.replace("style='font-family:\\'Inter\\',", 'style="font-family:\\\'Inter\\\',')
text = text.replace("style='font-family:\\'JetBrains Mono\\',", 'style="font-family:\\\'JetBrains Mono\\\',')

# Actually, a much safer way is to replace the exact strings used in tab2 since I wrote them.
text = text.replace("<div style='font-family:\\'Inter\\', sans-serif; font-size: 2rem; font-weight: 900; color: #ef4444; letter-spacing: -1px;'>", "<div style=\"font-family:'Inter', sans-serif; font-size: 2rem; font-weight: 900; color: #ef4444; letter-spacing: -1px;\">")
text = text.replace("<div style='font-family:\\'Inter\\', sans-serif; font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>", "<div style=\"font-family:'Inter', sans-serif; font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;\">")
text = text.replace("<div style='font-family:\\'Inter\\', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a;'>", "<div style=\"font-family:'Inter', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a;\">")
text = text.replace("<div style='font-family:\\'Inter\\', sans-serif; font-size: 0.85rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px;'>", "<div style=\"font-family:'Inter', sans-serif; font-size: 0.85rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px;\">")

# And for the span (JetBrains Mono)
text = text.replace("<span style='background:#f8fafc; color:#334155; padding:8px 16px; border-radius:8px; font-family:\\'JetBrains Mono\\', monospace; font-size:0.9rem; font-weight:600; border:1px solid #e2e8f0;'>", "<span style=\"background:#f8fafc; color:#334155; padding:8px 16px; border-radius:8px; font-family:'JetBrains Mono', monospace; font-size:0.9rem; font-weight:600; border:1px solid #e2e8f0;\">")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
