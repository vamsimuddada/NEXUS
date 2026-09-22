import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

pattern = re.compile(r"c1, c2 = st\.columns\(2\)\s*with c1:\s*with st\.container\(border=True\):\s*(.*?)\s*with c2:\s*with st\.container\(border=True\):\s*(.*?)\s*st\.markdown\(\"<br>\", unsafe_allow_html=True\)", re.DOTALL)

new_text = """with st.container(border=True):
                c1, c2 = st.columns(2)
                with c1:
                    \g<1>
                with c2:
                    \g<2>
            
            st.markdown("<br>", unsafe_allow_html=True)"""

match = pattern.search(text)
if match:
    # Use re.sub to correctly apply \g<1> and \g<2>
    text = pattern.sub(new_text, text, count=1)
    with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
        f.write(text)
    print("Replaced successfully!")
else:
    print("Failed to match regex.")
