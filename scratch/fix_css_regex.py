import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix hero-header
text = re.sub(r"(\.hero-header\s*\{[\s\r\n]*font-family:\s*'Space Grotesk',\s*sans-serif);", r"\1 !important;", text)

# Fix kpi-value
text = re.sub(r"(\.kpi-value\s*\{[\s\r\n]*font-family:\s*'Space Grotesk',\s*sans-serif);", r"\1 !important;", text)

# Remove the bad slider rule
bad_slider_pattern = r"\[data-testid=\"stSlider\"\] > div > div > div > div\s*\{[\s\r\n]*background:\s*#3b82f6 !important;[\s\r\n]*\}"
text = re.sub(bad_slider_pattern, "", text)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
