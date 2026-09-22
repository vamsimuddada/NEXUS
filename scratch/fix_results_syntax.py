import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

bad_line = 'st.markdown("<p style="font-family:\'Space Grotesk\', sans-serif; color:#64748b; margin-bottom:32px; font-size:1.1rem; font-weight:500;">Detailed breakdown of the most recent campaign, including executed attacks, blue team mitigations, and dynamic rule generation.</p>", unsafe_allow_html=True)'

fixed_line = 'st.markdown(\'<p style="font-family:\\\'Space Grotesk\\\', sans-serif; color:#64748b; margin-bottom:32px; font-size:1.1rem; font-weight:500;">Detailed breakdown of the most recent campaign, including executed attacks, blue team mitigations, and dynamic rule generation.</p>\', unsafe_allow_html=True)'

text = text.replace(bad_line, fixed_line)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
