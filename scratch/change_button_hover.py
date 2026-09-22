import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

old_hover = """.stButton > button:hover {
    background: linear-gradient(135deg, #1e293b, #3b82f6) !important;
    box-shadow: 0 15px 35px -5px rgba(37, 99, 235, 0.5), inset 0 2px 0 rgba(255,255,255,0.3) !important;
    transform: translateY(-5px) scale(1.03) !important;
}"""

new_hover = """.stButton > button:hover {
    background: linear-gradient(135deg, #1e293b, #2563eb) !important;
    box-shadow: 0 2px 10px rgba(37, 99, 235, 0.3), inset 0 4px 10px rgba(0, 0, 0, 0.6) !important;
    transform: translateY(3px) scale(0.98) !important;
    border: 1px solid #60a5fa !important;
}"""

text = text.replace(old_hover, new_hover)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
