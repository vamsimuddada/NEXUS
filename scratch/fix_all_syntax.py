import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix all instances where st.markdown("<TAG style="font-family:\'Inter\', was broken
text = re.sub(
    r'(st\.markdown\([f]?["\'](?:<[^>]+)?style=)"(font-family:\\?\'[^\']+\\?\',[^"]+)\'',
    r"\1'\2'",
    text
)

# And fix any that I missed that use 'st.markdown("<p style="font-family...'
text = re.sub(
    r'(st\.markdown\([f]?["\'](?:<[^>]+)?style=)"(font-family:[^>]+)\'',
    r"\1'\2'",
    text
)

# Actually, the simplest brute force is just replacing the exact strings.
text = text.replace('st.markdown("<p style="font-family:\\\'Inter\\\',', 'st.markdown("<p style=\'font-family:\\\'Inter\\\',')
text = text.replace('st.markdown("<h2 style="font-family:\\\'Inter\\\',', 'st.markdown("<h2 style=\'font-family:\\\'Inter\\\',')
text = text.replace('st.markdown("<h3 style="font-family:\\\'Inter\\\',', 'st.markdown("<h3 style=\'font-family:\\\'Inter\\\',')
text = text.replace('st.markdown("<h4 style="font-family:\\\'Inter\\\',', 'st.markdown("<h4 style=\'font-family:\\\'Inter\\\',')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
