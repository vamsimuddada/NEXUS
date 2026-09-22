import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Aggressively fix all double-quote CSS injections inside st.markdown("...")
text = re.sub(
    r'(st\.markdown\([f]?["\'](?:<[^>]+)?style=)"(font-family:\'Inter\',[^"]+)"',
    r"\1'\2'",
    text
)

text = text.replace('st.markdown("<h3 style="font-family:\'Inter\', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;">', 'st.markdown("<h3 style=\'font-family:\\\'Inter\\\', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;\'>')
text = text.replace('st.markdown("<h3 style="font-family:\'Inter\', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-bottom:24px;">', 'st.markdown("<h3 style=\'font-family:\\\'Inter\\\', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-bottom:24px;\'>')
text = text.replace('st.markdown("<h4 style="font-family:\'Inter\', sans-serif; font-weight:800; color:#0B1121; margin-top:0; margin-bottom:16px; letter-spacing:-0.5px;">', 'st.markdown("<h4 style=\'font-family:\\\'Inter\\\', sans-serif; font-weight:800; color:#0B1121; margin-top:0; margin-bottom:16px; letter-spacing:-0.5px;\'>')
text = text.replace('st.markdown("<div style="font-family:\'Inter\', sans-serif; font-size:3.5rem; font-weight:900; color:#0B1121; letter-spacing:-2px; margin-bottom:16px;">', 'st.markdown("<div style=\'font-family:\\\'Inter\\\', sans-serif; font-size:3.5rem; font-weight:900; color:#0B1121; letter-spacing:-2px; margin-bottom:16px;\'>')
text = text.replace('st.markdown("<div style="font-family:\'Inter\', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121; letter-spacing:-0.5px;">', 'st.markdown("<div style=\'font-family:\\\'Inter\\\', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121; letter-spacing:-0.5px;\'>')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
