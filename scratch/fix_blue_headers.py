import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# I will replace the overly broad selector with a strictly scoped one.
text = text.replace(
    '[data-testid="stMarkdownContainer"] p {\n    font-family: \'Space Grotesk\', sans-serif !important;\n    font-weight: 800 !important;\n    color: #3b82f6 !important;',
    '[data-testid="stProgress"] [data-testid="stMarkdownContainer"] p {\n    font-family: \'Space Grotesk\', sans-serif !important;\n    font-weight: 800 !important;\n    color: #3b82f6 !important;'
)

# Wait, if `text="..."` on `st.progress` doesn't wrap in `stProgress`, this will break the progress bar text.
# Let's also restore the stWidgetLabel color directly to black just in case, or let the natural CSS take over.
# If I scope it to stProgress, the natural stWidgetLabel CSS (which is #475569) will take over. The user wants BLACK (#0f172a).
text = text.replace('color: #475569 !important;', 'color: #0f172a !important;') # in stWidgetLabel

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
