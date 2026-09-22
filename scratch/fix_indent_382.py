import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the indent error
text = text.replace(
    'if st.query_params.get("page") == "about":\n    st.markdown("<div style="font-family:\'Inter\',',
    'if st.query_params.get("page") == "about":\n        st.markdown("<div style="font-family:\'Inter\','
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
