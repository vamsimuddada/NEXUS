import codecs
import re

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
    
    # Remove all empty lines inside the block
    lines = old_block.split('\n')
    new_lines = [line for line in lines if line.strip() or line == '    st.markdown(\'\'\'' or line == "    ''', unsafe_allow_html=True)"]
            
    new_block = '\n'.join(new_lines)
    
    text = text.replace(old_block, new_block)
    
    with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
        f.write(text)
