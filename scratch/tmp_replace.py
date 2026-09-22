import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# I need to find the block I injected earlier:
bad_block = """    # ── MITRE Heatmap & Firewall Feed ──
    st.markdown("<h3 style='color:#0f172a; font-family: 'Google Sans', sans-serif; font-weight:800; letter-spacing:-1px; margin-top:32px; margin-bottom:16px;'>Tactics & Perimeter Defense</h3>", unsafe_allow_html=True)"""
# Wait, I reverted fonts, so the fonts are Space Grotesk now?
# Let's write a python script to dynamically find and replace the whole block.
