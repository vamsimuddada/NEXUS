import codecs
text = codecs.open('scripts/dashboard.py', 'r', 'utf-8').read()
idx = text.find('if st.query_params.get("page") == "about":')
idx_end = text.find('st.stop()', idx)
print(text[idx:idx_end+15].encode('ascii', 'ignore').decode())
