import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Remove the broken CSS block
pattern = re.compile(r'/\*\s*Progress Bar Integration\s*\*/.*?(?=\*/|</style>)', re.DOTALL)

# Add a much safer, non-destructive CSS block
new_css = """/*  Progress Bar Integration  */
[data-testid="stProgress"] p {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 800 !important;
    color: #3b82f6 !important;
    letter-spacing: 0.5px !important;
    font-size: 1rem !important;
}
[role="progressbar"] {
    background: linear-gradient(90deg, #0ea5e9, #3b82f6) !important;
}
"""

text = pattern.sub(new_css, text)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
