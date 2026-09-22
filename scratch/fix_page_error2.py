import codecs
with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

bad_block = """if page == "SOC Overview":
    st.markdown("<div class='hero-header'>Global SOC Overview</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; margin-bottom:32px; font-size:1.15rem; font-weight:500;'>Real-time unified threat simulation metrics</p>", unsafe_allow_html=True)"""

bad_block2 = bad_block.replace('\n', '\r\n')

text = text.replace(bad_block, "")
text = text.replace(bad_block2, "")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
