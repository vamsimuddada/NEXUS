import codecs
with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

kpi_text_css = """
.kpi-title { font-family: 'Space Grotesk', sans-serif; font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 2.5px; font-weight: 800; margin-bottom: 14px; }
.kpi-value { font-family: 'Space Grotesk', sans-serif; font-size: 2.5rem; color: #0f172a; font-weight: 800; letter-spacing: -1.5px; line-height: 1; background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; filter: drop-shadow(0 4px 6px rgba(37, 99, 235, 0.1)); }
.kpi-trend { font-size: 0.95rem; color: #10b981; font-weight: 700; margin-top: 20px; display: flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.1); padding: 8px 16px; border-radius: 24px; width: fit-content; box-shadow: inset 0 1px 0 rgba(255,255,255,0.8); white-space: nowrap; }
"""

if '.kpi-title' not in text:
    text = text.replace('</style>', kpi_text_css + '</style>')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
