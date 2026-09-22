import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

idx = text.find('st.markdown(f"""\n<div style=\'background: #ffffff;')
if idx != -1:
    end_idx = text.find('""", unsafe_allow_html=True)', idx)
    old_block = text[idx:end_idx+len('""", unsafe_allow_html=True)')]
    
    # Strip ALL leading whitespace from every line in the block
    lines = old_block.split('\n')
    new_lines = [line.lstrip() for line in lines]
            
    new_block = '\n'.join(new_lines)
    text = text.replace(old_block, new_block)
    
with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
