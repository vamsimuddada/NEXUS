import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the broken st.markdown(" left over from regex
text = text.replace(
    'st.markdown("\n\n    \n    st.markdown("<h3 style=\\"font-family:\'Inter\', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;\\">Simulation Lifecycle</h3>"',
    'st.markdown("<h3 style=\\"font-family:\'Inter\', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;\\">Simulation Lifecycle</h3>"'
)
# Just brute force delete the lonely st.markdown("
text = re.sub(r'st\.markdown\("\s*st\.markdown\("<h3', r'st.markdown("<h3', text, flags=re.DOTALL)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
