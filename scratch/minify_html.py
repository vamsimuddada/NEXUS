import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

start_str = '    st.markdown(\'\'\''
end_str = "    ''', unsafe_allow_html=True)"

title_idx = text.find('About the Developer')
start_idx = text.find(start_str, title_idx)
end_idx = text.find(end_str, start_idx)

if start_idx != -1 and end_idx != -1:
    end_idx += len(end_str)
    old_block = text[start_idx:end_idx]
    
    # Get just the inner HTML
    inner_html = old_block.replace("    st.markdown('''\n", "").replace("\n    ''', unsafe_allow_html=True)", "")
    # Remove ALL newlines so it's a single line
    minified_html = inner_html.replace('\n', '')
    
    new_block = f"    st.markdown('''{minified_html}''', unsafe_allow_html=True)"
    
    text = text.replace(old_block, new_block)
    
    with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
        f.write(text)
