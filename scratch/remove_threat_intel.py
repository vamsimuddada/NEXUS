import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

idx1 = text.find('Threat Intelligence</div>')
if idx1 != -1:
    idx_start = text.rfind('st.markdown', 0, idx1)
    
    # We want to remove the indentation before st.markdown as well
    # Find the newline before idx_start
    idx_start = text.rfind('\n', 0, idx_start)
    
    idx_end = text.find('with tab2:', idx_start)
    
    # Slice it out
    if idx_start != -1 and idx_end != -1:
        text = text[:idx_start] + '\n\n' + text[idx_end:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
