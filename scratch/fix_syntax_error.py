import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the Python syntax error caused by mismatched string quotes!
text = text.replace(
    'st.markdown("<h3 style="color:#0f172a; font-family:\'Space Grotesk\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800; letter-spacing:-0.5px;">Live Threat Graph</h3>", unsafe_allow_html=True)',
    'st.markdown(\'<h3 style="color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800; letter-spacing:-0.5px;">Live Threat Graph</h3>\', unsafe_allow_html=True)'
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
