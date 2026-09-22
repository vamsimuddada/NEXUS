import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace(
    """st.markdown("<h4 style='color:#0f172a; margin-top:0;'>Tracked Actors</h4>", unsafe_allow_html=True)""",
    """st.markdown('<h4 style="font-family:\\'Inter\\', sans-serif; font-size:1.4rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px; margin-top:0; margin-bottom:16px;">Tracked Actors</h4>', unsafe_allow_html=True)"""
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
