import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

pattern = re.compile(r'\.stButton > button:hover\s*\{.*?\transform:\s*translateY\(-5px\)\s*scale\(1\.03\)\s*!important;\s*\}', re.DOTALL)

new_hover = """.stButton > button:hover {
    background: linear-gradient(135deg, #1e293b, #2563eb) !important;
    box-shadow: 0 2px 10px rgba(37, 99, 235, 0.3), inset 0 4px 10px rgba(0, 0, 0, 0.6) !important;
    transform: translateY(3px) scale(0.98) !important;
    border: 1px solid #60a5fa !important;
}"""

text = pattern.sub(new_hover, text)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
